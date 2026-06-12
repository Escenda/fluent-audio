"""DORA synthesized-audio probe sink for TTS smoke verification."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fluent_audio.contracts import SynthesizedAudioChunk
from fluent_audio.dora import (
    decode_synthesized_audio_chunk_from_dora,
    validate_dora_synthesized_audio_final_marker,
    validate_dora_synthesized_audio_metadata,
)


class SynthAudioProbeError(ValueError):
    """Raised when DORA synthesized audio validation fails."""


class SynthAudioProbeSummary(BaseModel):
    """Validated smoke summary for a DORA synthesized audio stream."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    chunks: int = Field(ge=0)
    frames: int = Field(ge=0)
    final_seen: bool
    final_sample_index: int = Field(ge=0)
    sample_rate_hz: int = Field(gt=0)
    sample_format: str = Field(min_length=1)
    channels: int = Field(gt=0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and discard DORA synthesized audio.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--user-turn-id", required=True)
    parser.add_argument("--assistant-turn-id", required=True)
    parser.add_argument("--audio-source-id", required=True)
    parser.add_argument("--audio-stream-id", required=True)
    parser.add_argument("--expected-min-chunks", required=True, type=int)
    parser.add_argument("--expected-min-frames", required=True, type=int)
    parser.add_argument("--expected-sample-format", required=True)
    parser.add_argument("--expected-channels", required=True, type=int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("synth_audio_probe requires --dora")

    from dora import Node

    summary = run_synth_audio_probe_dora(
        Node(),
        request_id=args.request_id,
        session_id=args.session_id,
        user_turn_id=args.user_turn_id,
        assistant_turn_id=args.assistant_turn_id,
        audio_source_id=args.audio_source_id,
        audio_stream_id=args.audio_stream_id,
    )
    validate_summary(
        summary,
        expected_min_chunks=args.expected_min_chunks,
        expected_min_frames=args.expected_min_frames,
        expected_sample_format=args.expected_sample_format,
        expected_channels=args.expected_channels,
    )
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def run_synth_audio_probe_dora(
    node,
    *,
    request_id: str,
    session_id: str,
    user_turn_id: str,
    assistant_turn_id: str,
    audio_source_id: str,
    audio_stream_id: str,
) -> SynthAudioProbeSummary:
    chunks = 0
    frames = 0
    previous_chunk: SynthesizedAudioChunk | None = None

    for event in node:
        if event is None:
            raise SynthAudioProbeError("DORA event stream ended before synthesized audio final")
        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            raise SynthAudioProbeError("DORA STOP arrived before synthesized audio final")
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id != "synth_audio":
                raise SynthAudioProbeError(f"Unexpected DORA input id: {input_id!r}")
            raise SynthAudioProbeError("DORA input closed before synthesized audio final")
        if event_type != "INPUT":
            raise SynthAudioProbeError(f"Unexpected DORA event type: {event_type!r}")

        input_id = _required_event_text(event, "id")
        if input_id != "synth_audio":
            raise SynthAudioProbeError(f"Unexpected DORA input id: {input_id!r}")

        payload = event.get("value")
        metadata = validate_dora_synthesized_audio_metadata(event.get("metadata"))
        if metadata.final:
            final = validate_dora_synthesized_audio_final_marker(payload, metadata)
            _validate_final_marker(
                final,
                request_id=request_id,
                session_id=session_id,
                user_turn_id=user_turn_id,
                assistant_turn_id=assistant_turn_id,
                audio_source_id=audio_source_id,
                audio_stream_id=audio_stream_id,
                expected_seq=chunks,
                expected_sample_index=frames,
            )
            return SynthAudioProbeSummary(
                chunks=chunks,
                frames=frames,
                final_seen=True,
                final_sample_index=final.audio_sample_index,
                sample_rate_hz=final.audio_format.sample_rate_hz,
                sample_format=final.audio_format.sample_format,
                channels=final.audio_format.channels,
            )

        chunk = decode_synthesized_audio_chunk_from_dora(payload, metadata)
        _validate_chunk(
            chunk,
            request_id=request_id,
            session_id=session_id,
            user_turn_id=user_turn_id,
            assistant_turn_id=assistant_turn_id,
            audio_source_id=audio_source_id,
            audio_stream_id=audio_stream_id,
            previous_chunk=previous_chunk,
        )
        chunks += 1
        frames += chunk.audio.frame_count
        previous_chunk = chunk

    raise SynthAudioProbeError("DORA synthesized audio stream ended without final marker")


def validate_summary(
    summary: SynthAudioProbeSummary,
    *,
    expected_min_chunks: int,
    expected_min_frames: int,
    expected_sample_format: str,
    expected_channels: int,
) -> None:
    if summary.chunks < expected_min_chunks:
        raise SynthAudioProbeError(
            f"Expected at least {expected_min_chunks} chunks, got {summary.chunks}"
        )
    if summary.frames < expected_min_frames:
        raise SynthAudioProbeError(
            f"Expected at least {expected_min_frames} frames, got {summary.frames}"
        )
    if summary.sample_format != expected_sample_format:
        raise SynthAudioProbeError(
            "Sample format mismatch: "
            f"expected {expected_sample_format!r}, got {summary.sample_format!r}"
        )
    if summary.channels != expected_channels:
        raise SynthAudioProbeError(
            f"Channel count mismatch: expected {expected_channels}, got {summary.channels}"
        )


def _validate_chunk(
    chunk: SynthesizedAudioChunk,
    *,
    request_id: str,
    session_id: str,
    user_turn_id: str,
    assistant_turn_id: str,
    audio_source_id: str,
    audio_stream_id: str,
    previous_chunk: SynthesizedAudioChunk | None,
) -> None:
    if chunk.request_id != request_id:
        raise SynthAudioProbeError("Synthesized audio request_id mismatch")
    if chunk.session_id != session_id:
        raise SynthAudioProbeError("Synthesized audio session_id mismatch")
    if chunk.user_turn_id != user_turn_id:
        raise SynthAudioProbeError("Synthesized audio user_turn_id mismatch")
    if chunk.assistant_turn_id != assistant_turn_id:
        raise SynthAudioProbeError("Synthesized audio assistant_turn_id mismatch")
    if chunk.audio.source_id != audio_source_id:
        raise SynthAudioProbeError("Synthesized audio source_id mismatch")
    if chunk.audio.stream_id != audio_stream_id:
        raise SynthAudioProbeError("Synthesized audio stream_id mismatch")
    if previous_chunk is None:
        if chunk.seq != 0 or chunk.audio.seq != 0 or chunk.audio.sample_index != 0:
            raise SynthAudioProbeError("First synthesized audio chunk must start at zero")
        return
    if chunk.seq != previous_chunk.seq + 1:
        raise SynthAudioProbeError("Synthesized audio chunk seq discontinuity")
    if chunk.audio.seq != previous_chunk.audio.seq + 1:
        raise SynthAudioProbeError("Synthesized audio audio.seq discontinuity")
    if chunk.audio.sample_index != previous_chunk.audio.next_sample_index:
        raise SynthAudioProbeError("Synthesized audio sample_index discontinuity")
    if chunk.audio.format != previous_chunk.audio.format:
        raise SynthAudioProbeError("Synthesized audio format changed")


def _validate_final_marker(
    final,
    *,
    request_id: str,
    session_id: str,
    user_turn_id: str,
    assistant_turn_id: str,
    audio_source_id: str,
    audio_stream_id: str,
    expected_seq: int,
    expected_sample_index: int,
) -> None:
    if final.request_id != request_id:
        raise SynthAudioProbeError("Synthesized audio final request_id mismatch")
    if final.session_id != session_id:
        raise SynthAudioProbeError("Synthesized audio final session_id mismatch")
    if final.user_turn_id != user_turn_id:
        raise SynthAudioProbeError("Synthesized audio final user_turn_id mismatch")
    if final.assistant_turn_id != assistant_turn_id:
        raise SynthAudioProbeError("Synthesized audio final assistant_turn_id mismatch")
    if final.audio_source_id != audio_source_id:
        raise SynthAudioProbeError("Synthesized audio final source_id mismatch")
    if final.audio_stream_id != audio_stream_id:
        raise SynthAudioProbeError("Synthesized audio final stream_id mismatch")
    if final.seq != expected_seq or final.audio_seq != expected_seq:
        raise SynthAudioProbeError("Synthesized audio final seq mismatch")
    if final.audio_sample_index != expected_sample_index:
        raise SynthAudioProbeError("Synthesized audio final sample_index mismatch")


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise SynthAudioProbeError(f"DORA event field {key!r} must be a string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
