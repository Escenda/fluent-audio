"""CLI wrapper for the raw PCM offline source node logic."""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Callable
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from fluent_audio.contracts import AudioChunk, AudioFormat
from fluent_audio.dora import encode_audio_chunk_for_dora, encode_audio_final_marker_for_dora
from fluent_audio.offline import (
    RawPcmReadConfig,
    capture_time_ns_for_frame_offset,
    iter_raw_pcm_chunks,
    write_raw_pcm_chunk_jsonl,
)

DORA_FINAL_MARKER_DRAIN_SECONDS = 0.1
SleepFn = Callable[[float], None]


class RawPcmReplayPacingConfig(BaseModel):
    """Explicit DORA replay pacing for treating offline PCM as a stream."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    replay_speed: float = Field(gt=0.0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read headerless PCM and emit AudioChunk JSONL.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--sample-rate-hz", required=True, type=int)
    parser.add_argument("--channels", required=True, type=int)
    parser.add_argument("--sample-format", required=True, choices=("s16le", "f32le"))
    parser.add_argument("--channel-layout", required=True, choices=("interleaved",))
    parser.add_argument("--chunk-frames", required=True, type=int)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--stream-id", required=True)
    parser.add_argument("--start-seq", type=int, default=0)
    parser.add_argument("--start-sample-index", type=int, default=0)
    parser.add_argument("--start-capture-time-ns", required=True, type=int)
    parser.add_argument("--dora", action="store_true")
    parser.add_argument(
        "--replay-speed",
        type=float,
        help="When set with --dora, sleep after each chunk at real-time / replay_speed.",
    )
    parser.add_argument("--chunks-jsonl", type=Path)
    parser.add_argument("--overwrite-jsonl", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = RawPcmReadConfig(
        path=args.input,
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
    )

    if args.dora:
        from dora import Node

        send_raw_pcm_source_dora(
            Node(),
            config,
            pacing_config=_pacing_config_from_args(args),
        )
        return 0

    chunks = iter_raw_pcm_chunks(config)

    if args.chunks_jsonl is not None:
        write_raw_pcm_chunk_jsonl(
            args.chunks_jsonl,
            chunks,
            overwrite=args.overwrite_jsonl,
        )
        return 0

    for chunk in chunks:
        sys.stdout.write(_metadata_json_line(chunk))
        sys.stdout.write("\n")
    return 0


def send_raw_pcm_source_dora(
    node,
    config: RawPcmReadConfig,
    *,
    pacing_config: RawPcmReplayPacingConfig | None = None,
    sleep: SleepFn = time.sleep,
) -> int:
    """Send raw PCM chunks through DORA as bytes payloads."""

    chunks_sent = 0
    next_seq = config.start_seq
    next_sample_index = config.start_sample_index
    final_capture_time_ns = config.start_capture_time_ns

    for chunk in iter_raw_pcm_chunks(config):
        payload, metadata = encode_audio_chunk_for_dora(chunk)
        node.send_output("audio", payload, metadata=metadata.to_dora_metadata())
        chunks_sent += 1
        next_seq = chunk.next_seq
        next_sample_index = chunk.next_sample_index
        final_capture_time_ns = capture_time_ns_for_frame_offset(
            config.start_capture_time_ns,
            next_sample_index - config.start_sample_index,
            config.audio_format.sample_rate_hz,
        )
        if pacing_config is not None:
            sleep(_chunk_replay_sleep_seconds(chunk, pacing_config))

    final_payload, final_metadata = encode_audio_final_marker_for_dora(
        source_id=config.source_id,
        stream_id=config.stream_id,
        seq=next_seq,
        sample_index=next_sample_index,
        capture_time_ns=final_capture_time_ns,
        audio_format=config.audio_format,
    )
    node.send_output("audio", final_payload, metadata=final_metadata.to_dora_metadata())
    _drain_dora_final_marker_send()
    return chunks_sent


def _pacing_config_from_args(args: argparse.Namespace) -> RawPcmReplayPacingConfig | None:
    if args.replay_speed is None:
        return None
    return RawPcmReplayPacingConfig(replay_speed=args.replay_speed)


def _chunk_replay_sleep_seconds(
    chunk: AudioChunk,
    pacing_config: RawPcmReplayPacingConfig,
) -> float:
    return chunk.frame_count / (chunk.format.sample_rate_hz * pacing_config.replay_speed)


def _drain_dora_final_marker_send() -> None:
    # The DORA Python API exposes no output flush/ack. Keep the source alive briefly
    # after sending the explicit final marker so process teardown cannot race daemon
    # ingestion; downstream nodes still fail closed if that marker is not observed.
    time.sleep(DORA_FINAL_MARKER_DRAIN_SECONDS)


def _metadata_json_line(chunk: AudioChunk) -> str:
    return json.dumps(
        {
            "source_id": chunk.source_id,
            "stream_id": chunk.stream_id,
            "seq": chunk.seq,
            "sample_index": chunk.sample_index,
            "capture_time_ns": chunk.capture_time_ns,
            "frame_count": chunk.frame_count,
            "format": chunk.format.model_dump(mode="json"),
            "payload_size_bytes": chunk.payload_size_bytes,
        },
        sort_keys=True,
    )


if __name__ == "__main__":
    raise SystemExit(main())
