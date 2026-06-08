"""DORA audio probe sink for hardware smoke verification."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict, Field

from fluent_audio.contracts import AudioChunk, AudioFormat, require_contiguous_audio_chunks
from fluent_audio.dora import (
    decode_audio_chunk_from_dora,
    validate_dora_audio_final_marker,
    validate_dora_audio_metadata,
)


class AudioProbeError(ValueError):
    """Raised when DORA audio probe validation fails."""


class AudioProbeSummary(BaseModel):
    """Validated smoke summary for a DORA audio input stream."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    chunks: int = Field(ge=0)
    frames: int = Field(ge=0)
    bytes: int = Field(ge=0)
    final_seen: bool


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and discard DORA audio chunks.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--sample-rate-hz", required=True, type=int)
    parser.add_argument("--channels", required=True, type=int)
    parser.add_argument("--sample-format", required=True, choices=("s16le", "f32le"))
    parser.add_argument("--channel-layout", required=True, choices=("interleaved",))
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--stream-id", required=True)
    parser.add_argument("--expected-chunks", required=True, type=int)
    parser.add_argument("--expected-frames", required=True, type=int)
    parser.add_argument("--expected-bytes", required=True, type=int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("audio_probe requires --dora")

    from dora import Node

    expected_format = AudioFormat(
        sample_rate_hz=args.sample_rate_hz,
        channels=args.channels,
        sample_format=args.sample_format,
        channel_layout=args.channel_layout,
    )
    summary = run_probe_dora(
        Node(),
        expected_format=expected_format,
        source_id=args.source_id,
        stream_id=args.stream_id,
    )
    validate_summary(
        summary,
        expected_chunks=args.expected_chunks,
        expected_frames=args.expected_frames,
        expected_bytes=args.expected_bytes,
    )
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def run_probe_dora(
    node,
    *,
    expected_format: AudioFormat,
    source_id: str,
    stream_id: str,
) -> AudioProbeSummary:
    chunks = 0
    frames = 0
    bytes_seen = 0
    previous_chunk: AudioChunk | None = None

    for chunk in iter_dora_probe_audio_chunks(node):
        if chunk.source_id != source_id:
            raise AudioProbeError(
                f"Audio probe source mismatch: expected {source_id!r}, got {chunk.source_id!r}"
            )
        if chunk.stream_id != stream_id:
            raise AudioProbeError(
                f"Audio probe stream mismatch: expected {stream_id!r}, got {chunk.stream_id!r}"
            )
        if chunk.format != expected_format:
            raise AudioProbeError("Audio probe format mismatch")
        if previous_chunk is not None:
            require_contiguous_audio_chunks(previous_chunk, chunk)
        chunks += 1
        frames += chunk.frame_count
        bytes_seen += chunk.payload_size_bytes
        previous_chunk = chunk

    return AudioProbeSummary(
        chunks=chunks,
        frames=frames,
        bytes=bytes_seen,
        final_seen=True,
    )


def iter_dora_probe_audio_chunks(events):
    for event in events:
        if event is None:
            raise AudioProbeError("DORA event stream ended before audio final marker")

        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            raise AudioProbeError("DORA STOP arrived before audio final marker")
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id != "audio":
                raise AudioProbeError(f"Unexpected DORA input id: {input_id!r}")
            raise AudioProbeError("DORA input closed before audio final marker")
        if event_type != "INPUT":
            raise AudioProbeError(f"Unexpected DORA event type: {event_type!r}")

        input_id = _required_event_text(event, "id")
        if input_id != "audio":
            raise AudioProbeError(f"Unexpected DORA input id: {input_id!r}")

        payload = event.get("value")
        metadata = validate_dora_audio_metadata(event.get("metadata"))
        if metadata.final:
            validate_dora_audio_final_marker(payload, metadata)
            return

        yield decode_audio_chunk_from_dora(payload, metadata)

    raise AudioProbeError("DORA audio stream ended without final marker")


def validate_summary(
    summary: AudioProbeSummary,
    *,
    expected_chunks: int,
    expected_frames: int,
    expected_bytes: int,
) -> None:
    if summary.chunks != expected_chunks:
        raise AudioProbeError(
            f"Audio probe chunk count mismatch: expected {expected_chunks}, got {summary.chunks}"
        )
    if summary.frames != expected_frames:
        raise AudioProbeError(
            f"Audio probe frame count mismatch: expected {expected_frames}, got {summary.frames}"
        )
    if summary.bytes != expected_bytes:
        raise AudioProbeError(
            f"Audio probe byte count mismatch: expected {expected_bytes}, got {summary.bytes}"
        )
    if not summary.final_seen:
        raise AudioProbeError("Audio probe did not receive final marker")


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise AudioProbeError(f"DORA event field {key!r} must be a string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
