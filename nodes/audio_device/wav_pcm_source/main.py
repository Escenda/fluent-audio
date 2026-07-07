"""DORA source node for paced PCM WAV replay."""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Callable, Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from fluent_dialogue_dora.contracts import AudioChunk
from fluent_dialogue_dora.dora import encode_audio_chunk_for_dora, encode_audio_final_marker_for_dora
from fluent_dialogue_dora.offline import (
    WavPcmReadConfig,
    capture_time_ns_for_frame_offset,
    iter_wav_pcm_chunks,
)

DORA_FINAL_MARKER_DRAIN_SECONDS = 0.1
SleepFn = Callable[[float], None]


class WavPcmReplayPacingConfig(BaseModel):
    """Explicit replay pacing for treating a WAV file as a live audio source."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    replay_speed: float = Field(gt=0.0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read PCM WAV and emit timed AudioChunk events.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--chunk-frames", required=True, type=int)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--stream-id", required=True)
    parser.add_argument("--start-seq", type=int, default=0)
    parser.add_argument("--start-sample-index", type=int, default=0)
    parser.add_argument("--start-capture-time-ns", required=True, type=int)
    parser.add_argument("--expected-sample-rate-hz", type=int)
    parser.add_argument("--expected-channels", type=int)
    parser.add_argument("--dora", action="store_true")
    parser.add_argument(
        "--replay-speed",
        type=float,
        help="When set with --dora, sleep after each chunk at real-time / replay_speed.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = WavPcmReadConfig(
        path=args.input,
        chunk_frames=args.chunk_frames,
        source_id=args.source_id,
        stream_id=args.stream_id,
        start_seq=args.start_seq,
        start_sample_index=args.start_sample_index,
        start_capture_time_ns=args.start_capture_time_ns,
        expected_sample_rate_hz=args.expected_sample_rate_hz,
        expected_channels=args.expected_channels,
    )

    if args.dora:
        from dora import Node

        send_wav_pcm_source_dora(
            Node(),
            config,
            pacing_config=_pacing_config_from_args(args),
        )
        return 0

    for chunk in iter_wav_pcm_chunks(config):
        sys.stdout.write(_metadata_json_line(chunk))
        sys.stdout.write("\n")
    return 0


def send_wav_pcm_source_dora(
    node,
    config: WavPcmReadConfig,
    *,
    pacing_config: WavPcmReplayPacingConfig | None = None,
    sleep: SleepFn = time.sleep,
) -> int:
    """Send WAV chunks through DORA as bytes payloads."""

    chunks_sent = 0
    next_seq = config.start_seq
    next_sample_index = config.start_sample_index
    final_capture_time_ns = config.start_capture_time_ns
    last_format = None

    for chunk in iter_wav_pcm_chunks(config):
        payload, metadata = encode_audio_chunk_for_dora(chunk)
        node.send_output("audio", payload, metadata=metadata.to_dora_metadata())
        chunks_sent += 1
        next_seq = chunk.next_seq
        next_sample_index = chunk.next_sample_index
        last_format = chunk.format
        final_capture_time_ns = capture_time_ns_for_frame_offset(
            config.start_capture_time_ns,
            next_sample_index - config.start_sample_index,
            chunk.format.sample_rate_hz,
        )
        if pacing_config is not None:
            sleep(_chunk_replay_sleep_seconds(chunk, pacing_config))

    if last_format is None:
        raise ValueError("WAV source produced no chunks")
    final_payload, final_metadata = encode_audio_final_marker_for_dora(
        source_id=config.source_id,
        stream_id=config.stream_id,
        seq=next_seq,
        sample_index=next_sample_index,
        capture_time_ns=final_capture_time_ns,
        audio_format=last_format,
    )
    node.send_output("audio", final_payload, metadata=final_metadata.to_dora_metadata())
    _drain_dora_final_marker_send()
    return chunks_sent


def _pacing_config_from_args(args: argparse.Namespace) -> WavPcmReplayPacingConfig | None:
    if args.replay_speed is None:
        return None
    return WavPcmReplayPacingConfig(replay_speed=args.replay_speed)


def _chunk_replay_sleep_seconds(
    chunk: AudioChunk,
    pacing_config: WavPcmReplayPacingConfig,
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
