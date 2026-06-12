"""DORA transcript probe sink for ASR smoke verification."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pydantic import BaseModel, ConfigDict, Field

from fluent_audio.contracts import TranscriptDelta, TranscriptFinal
from fluent_audio.dora import (
    decode_transcript_delta_from_dora,
    decode_transcript_final_from_dora,
    validate_dora_transcript_metadata,
    validate_dora_transcript_stream_final_marker,
)


class TranscriptProbeError(ValueError):
    """Raised when DORA transcript probe validation fails."""


class TranscriptProbeSummary(BaseModel):
    """Validated smoke summary for a DORA transcript stream."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    deltas: int = Field(ge=0)
    finals: int = Field(ge=0)
    final_seen: bool
    final_sample_index: int = Field(ge=0)
    last_text: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and discard DORA transcript events.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--stream-id", required=True)
    parser.add_argument("--expected-min-deltas", required=True, type=int)
    parser.add_argument("--expected-finals", required=True, type=int)
    parser.add_argument("--expected-final-sample-index", required=True, type=int)
    parser.add_argument("--expected-last-text", default="")
    parser.add_argument("--expected-last-text-compact", default="")
    parser.add_argument("--expected-min-last-text-length", default=0, type=int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("transcript_probe requires --dora")

    from dora import Node

    summary = run_transcript_probe_dora(
        Node(),
        session_id=args.session_id,
        stream_id=args.stream_id,
    )
    validate_summary(
        summary,
        expected_min_deltas=args.expected_min_deltas,
        expected_finals=args.expected_finals,
        expected_final_sample_index=args.expected_final_sample_index,
        expected_last_text=args.expected_last_text,
        expected_last_text_compact=args.expected_last_text_compact,
        expected_min_last_text_length=args.expected_min_last_text_length,
    )
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def run_transcript_probe_dora(
    node,
    *,
    session_id: str,
    stream_id: str,
) -> TranscriptProbeSummary:
    deltas = 0
    finals = 0
    previous_seq: int | None = None
    last_text = ""

    for event in node:
        if event is None:
            raise TranscriptProbeError("DORA event stream ended before transcript final marker")

        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            raise TranscriptProbeError("DORA STOP arrived before transcript final marker")
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id != "transcript":
                raise TranscriptProbeError(f"Unexpected DORA input id: {input_id!r}")
            raise TranscriptProbeError("DORA input closed before transcript final marker")
        if event_type != "INPUT":
            raise TranscriptProbeError(f"Unexpected DORA event type: {event_type!r}")

        input_id = _required_event_text(event, "id")
        if input_id != "transcript":
            raise TranscriptProbeError(f"Unexpected DORA input id: {input_id!r}")

        payload = event.get("value")
        metadata = validate_dora_transcript_metadata(event.get("metadata"))
        if metadata.kind == "stream_final":
            final_marker = validate_dora_transcript_stream_final_marker(payload, metadata)
            if final_marker.session_id != session_id:
                raise TranscriptProbeError(
                    "Transcript final session mismatch: "
                    f"expected {session_id!r}, got {final_marker.session_id!r}"
                )
            if final_marker.stream_id != stream_id:
                raise TranscriptProbeError(
                    "Transcript final stream mismatch: "
                    f"expected {stream_id!r}, got {final_marker.stream_id!r}"
                )
            return TranscriptProbeSummary(
                deltas=deltas,
                finals=finals,
                final_seen=True,
                final_sample_index=final_marker.start_sample_index,
                last_text=last_text,
            )

        if metadata.kind == "delta":
            transcript = decode_transcript_delta_from_dora(payload, metadata)
            _validate_transcript_event(
                transcript,
                session_id=session_id,
                stream_id=stream_id,
                previous_seq=previous_seq,
            )
            previous_seq = transcript.seq
            deltas += 1
            last_text += transcript.text
            continue

        transcript = decode_transcript_final_from_dora(payload, metadata)
        _validate_transcript_event(
            transcript,
            session_id=session_id,
            stream_id=stream_id,
            previous_seq=previous_seq,
        )
        previous_seq = transcript.seq
        finals += 1
        last_text = transcript.text

    raise TranscriptProbeError("DORA transcript stream ended without final marker")


def validate_summary(
    summary: TranscriptProbeSummary,
    *,
    expected_min_deltas: int,
    expected_finals: int,
    expected_final_sample_index: int,
    expected_last_text: str = "",
    expected_last_text_compact: str = "",
    expected_min_last_text_length: int = 0,
) -> None:
    if summary.deltas < expected_min_deltas:
        raise TranscriptProbeError(
            "Transcript delta count below expectation: "
            f"expected at least {expected_min_deltas}, got {summary.deltas}"
        )
    if summary.finals != expected_finals:
        raise TranscriptProbeError(
            f"Transcript final count mismatch: expected {expected_finals}, got {summary.finals}"
        )
    if summary.final_sample_index != expected_final_sample_index:
        raise TranscriptProbeError(
            "Transcript final sample_index mismatch: "
            f"expected {expected_final_sample_index}, got {summary.final_sample_index}"
        )
    if not summary.final_seen:
        raise TranscriptProbeError("Transcript probe did not receive final marker")
    if expected_last_text and summary.last_text != expected_last_text:
        raise TranscriptProbeError(
            "Transcript final text mismatch: "
            f"expected {expected_last_text!r}, got {summary.last_text!r}"
        )
    compact_last_text = "".join(summary.last_text.split())
    if expected_last_text_compact and compact_last_text != expected_last_text_compact:
        raise TranscriptProbeError(
            "Transcript compact final text mismatch: "
            f"expected {expected_last_text_compact!r}, got {compact_last_text!r}"
        )
    if len(summary.last_text) < expected_min_last_text_length:
        raise TranscriptProbeError(
            "Transcript final text length below expectation: "
            f"expected at least {expected_min_last_text_length}, got {len(summary.last_text)}"
        )


def _validate_transcript_event(
    event: TranscriptDelta | TranscriptFinal,
    *,
    session_id: str,
    stream_id: str,
    previous_seq: int | None,
) -> None:
    if event.session_id != session_id:
        raise TranscriptProbeError(
            f"Transcript session mismatch: expected {session_id!r}, got {event.session_id!r}"
        )
    if event.stream_id != stream_id:
        raise TranscriptProbeError(
            f"Transcript stream mismatch: expected {stream_id!r}, got {event.stream_id!r}"
        )
    if previous_seq is not None and event.seq != previous_seq + 1:
        raise TranscriptProbeError(
            f"Transcript seq discontinuity: expected {previous_seq + 1}, got {event.seq}"
        )


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise TranscriptProbeError(f"DORA event field {key!r} must be a string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
