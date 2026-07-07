"""DORA source node for PipeWire PCM capture through pw-record."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import BinaryIO

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pydantic import BaseModel, ConfigDict, Field

from fluent_dialogue_dora.contracts import AudioChunk, AudioFormat
from fluent_dialogue_dora.dora import encode_audio_chunk_for_dora, encode_audio_final_marker_for_dora

DORA_FINAL_MARKER_DRAIN_SECONDS = 0.1
PW_RECORD_BINARY = "pw-record"


class PipeWirePcmCaptureError(ValueError):
    """Raised when PipeWire PCM capture cannot produce valid audio chunks."""


class PipeWirePcmCaptureConfig(BaseModel):
    """Validated configuration for one PipeWire PCM capture stream."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    target: str = Field(min_length=1)
    latency: str = Field(min_length=1)
    audio_format: AudioFormat
    chunk_frames: int = Field(gt=0)
    source_id: str = Field(min_length=1)
    stream_id: str = Field(min_length=1)
    start_seq: int = Field(ge=0)
    start_sample_index: int = Field(ge=0)
    start_capture_time_ns: int = Field(ge=0)
    max_chunks: int | None = Field(default=None, gt=0)
    output_drain_seconds: float = Field(default=DORA_FINAL_MARKER_DRAIN_SECONDS, ge=0.0)

    @property
    def chunk_size_bytes(self) -> int:
        return self.chunk_frames * self.audio_format.frame_size_bytes


class PipeWirePcmCaptureSummary(BaseModel):
    """Counters emitted by one bounded PipeWire PCM capture run."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    chunks: int = Field(ge=0)
    frames: int = Field(ge=0)
    bytes: int = Field(ge=0)
    final_sample_index: int = Field(ge=0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture PipeWire PCM and emit DORA audio chunks.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--target", required=True)
    parser.add_argument("--latency", default="20ms")
    parser.add_argument("--sample-rate-hz", required=True, type=int)
    parser.add_argument("--channels", required=True, type=int)
    parser.add_argument("--sample-format", required=True, choices=("s16le",))
    parser.add_argument("--channel-layout", required=True, choices=("interleaved",))
    parser.add_argument("--chunk-frames", required=True, type=int)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--stream-id", required=True)
    parser.add_argument("--start-seq", type=int, default=0)
    parser.add_argument("--start-sample-index", type=int, default=0)
    parser.add_argument("--start-capture-time-ns", required=True, type=int)
    parser.add_argument("--max-chunks", type=int)
    parser.add_argument(
        "--output-drain-seconds",
        type=float,
        default=DORA_FINAL_MARKER_DRAIN_SECONDS,
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.dora:
        raise SystemExit("pipewire_pcm_capture requires --dora")

    from dora import Node

    config = PipeWirePcmCaptureConfig(
        target=args.target,
        latency=args.latency,
        audio_format=AudioFormat(
            sample_rate_hz=args.sample_rate_hz,
            channels=args.channels,
            sample_format=args.sample_format,
            channel_layout=args.channel_layout,
        ),
        chunk_frames=args.chunk_frames,
        source_id=args.source_id,
        stream_id=args.stream_id,
        start_seq=args.start_seq,
        start_sample_index=args.start_sample_index,
        start_capture_time_ns=args.start_capture_time_ns,
        max_chunks=args.max_chunks,
        output_drain_seconds=args.output_drain_seconds,
    )
    summary = run_pipewire_pcm_capture_dora(Node(), config)
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def run_pipewire_pcm_capture_dora(
    node,
    config: PipeWirePcmCaptureConfig,
) -> PipeWirePcmCaptureSummary:
    """Capture PipeWire PCM bytes and send typed DORA audio frames."""

    command = build_pw_record_command(config)
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.stdout is None:
        process.kill()
        raise PipeWirePcmCaptureError("pw-record stdout pipe was not created")

    chunks = 0
    frames = 0
    bytes_sent = 0
    seq = config.start_seq
    sample_index = config.start_sample_index
    try:
        for raw_chunk in iter_exact_chunks(process.stdout, config.chunk_size_bytes):
            frame_count = len(raw_chunk) // config.audio_format.frame_size_bytes
            if frame_count <= 0:
                raise PipeWirePcmCaptureError("pw-record produced an empty PCM chunk")
            chunk = AudioChunk(
                source_id=config.source_id,
                stream_id=config.stream_id,
                seq=seq,
                sample_index=sample_index,
                capture_time_ns=_capture_time_ns_for_sample_index(config, sample_index),
                frame_count=frame_count,
                format=config.audio_format,
                payload=raw_chunk,
            )
            payload, metadata = encode_audio_chunk_for_dora(chunk)
            node.send_output("audio", payload, metadata=metadata.to_dora_metadata())
            chunks += 1
            frames += frame_count
            bytes_sent += len(raw_chunk)
            seq = chunk.next_seq
            sample_index = chunk.next_sample_index
            if config.max_chunks is not None and chunks >= config.max_chunks:
                break
    finally:
        _terminate_process(process)

    return_code = process.poll()
    if return_code not in (0, None) and config.max_chunks is None:
        stderr = _read_process_stderr(process)
        raise PipeWirePcmCaptureError(f"pw-record exited with {return_code}: {stderr}")

    final_payload, final_metadata = encode_audio_final_marker_for_dora(
        source_id=config.source_id,
        stream_id=config.stream_id,
        seq=seq,
        sample_index=sample_index,
        capture_time_ns=_capture_time_ns_for_sample_index(config, sample_index),
        audio_format=config.audio_format,
    )
    node.send_output("audio", final_payload, metadata=final_metadata.to_dora_metadata())
    time.sleep(config.output_drain_seconds)
    return PipeWirePcmCaptureSummary(
        chunks=chunks,
        frames=frames,
        bytes=bytes_sent,
        final_sample_index=sample_index,
    )


def build_pw_record_command(config: PipeWirePcmCaptureConfig) -> tuple[str, ...]:
    if shutil.which(PW_RECORD_BINARY) is None:
        raise PipeWirePcmCaptureError("required command not found: pw-record")
    if config.audio_format.sample_format != "s16le":
        raise PipeWirePcmCaptureError("pipewire_pcm_capture currently supports only s16le")
    if config.audio_format.channel_layout != "interleaved":
        raise PipeWirePcmCaptureError(
            "pipewire_pcm_capture currently supports only interleaved PCM"
        )
    return (
        PW_RECORD_BINARY,
        "--target",
        config.target,
        "--latency",
        config.latency,
        "--format",
        "s16",
        "--rate",
        str(config.audio_format.sample_rate_hz),
        "--channels",
        str(config.audio_format.channels),
        "-",
    )


def iter_exact_chunks(stream: BinaryIO, chunk_size_bytes: int) -> Iterator[bytes]:
    if chunk_size_bytes <= 0:
        raise PipeWirePcmCaptureError("chunk_size_bytes must be positive")
    pending = bytearray()
    while True:
        data = stream.read(chunk_size_bytes - len(pending))
        if not data:
            if pending:
                yield bytes(pending)
            return
        pending.extend(data)
        if len(pending) == chunk_size_bytes:
            yield bytes(pending)
            pending.clear()


def _capture_time_ns_for_sample_index(
    config: PipeWirePcmCaptureConfig,
    sample_index: int,
) -> int:
    frame_offset = sample_index - config.start_sample_index
    return config.start_capture_time_ns + (
        frame_offset * 1_000_000_000
    ) // config.audio_format.sample_rate_hz


def _terminate_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=2.0)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=2.0)


def _read_process_stderr(process: subprocess.Popen[bytes]) -> str:
    if process.stderr is None:
        return ""
    return process.stderr.read().decode("utf-8", errors="replace").strip()


if __name__ == "__main__":
    raise SystemExit(main())
