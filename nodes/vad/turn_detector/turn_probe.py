"""DORA turn probe sink for turn detector smoke verification."""
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

from fluent_dialogue_dora.contracts import TurnEvent
from fluent_dialogue_dora.dora import (
    decode_turn_event_from_dora,
    validate_dora_turn_final_marker,
    validate_dora_turn_metadata,
)

class TurnProbeError(ValueError):
    """Raised when DORA turn probe validation fails."""


class TurnProbeSummary(BaseModel):
    """Validated smoke summary for a DORA turn stream."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    events: int = Field(ge=0)
    started_events: int = Field(ge=0)
    ended_events: int = Field(ge=0)
    final_seen: bool
    final_sample_index: int = Field(ge=0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and discard DORA turn events.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--stream-id", required=True)
    parser.add_argument("--expected-min-total-events", required=True, type=int)
    parser.add_argument("--expected-min-started-events", required=True, type=int)
    parser.add_argument("--expected-min-ended-events", required=True, type=int)
    parser.add_argument("--expected-final-sample-index", required=True, type=int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("turn_probe requires --dora")

    from dora import Node

    summary = run_turn_probe_dora(
        Node(),
        session_id=args.session_id,
        stream_id=args.stream_id,
    )
    validate_summary(
        summary,
        expected_min_total_events=args.expected_min_total_events,
        expected_min_started_events=args.expected_min_started_events,
        expected_min_ended_events=args.expected_min_ended_events,
        expected_final_sample_index=args.expected_final_sample_index,
    )
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def run_turn_probe_dora(
    node,
    *,
    session_id: str,
    stream_id: str,
) -> TurnProbeSummary:
    events = 0
    started_events = 0
    ended_events = 0
    previous_event: TurnEvent | None = None

    for event in node:
        if event is None:
            raise TurnProbeError("DORA event stream ended before turn final marker")

        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            raise TurnProbeError("DORA STOP arrived before turn final marker")
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id != "turn":
                raise TurnProbeError(f"Unexpected DORA input id: {input_id!r}")
            if previous_event is None:
                raise TurnProbeError("DORA turn input closed before turn events")
            return TurnProbeSummary(
                events=events,
                started_events=started_events,
                ended_events=ended_events,
                final_seen=True,
                final_sample_index=previous_event.sample_index,
            )
        if event_type != "INPUT":
            raise TurnProbeError(f"Unexpected DORA event type: {event_type!r}")

        input_id = _required_event_text(event, "id")
        if input_id != "turn":
            raise TurnProbeError(f"Unexpected DORA input id: {input_id!r}")

        payload = event.get("value")
        metadata = validate_dora_turn_metadata(event.get("metadata"))
        if metadata.final:
            final_marker = validate_dora_turn_final_marker(payload, metadata)
            if final_marker.session_id != session_id:
                raise TurnProbeError(
                    "Turn probe final session mismatch: "
                    f"expected {session_id!r}, got {final_marker.session_id!r}"
                )
            if final_marker.stream_id != stream_id:
                raise TurnProbeError(
                    "Turn probe final stream mismatch: "
                    f"expected {stream_id!r}, got {final_marker.stream_id!r}"
                )
            if final_marker.seq != events:
                raise TurnProbeError(
                    f"Turn probe final seq mismatch: expected {events}, got {final_marker.seq}"
                )
            return TurnProbeSummary(
                events=events,
                started_events=started_events,
                ended_events=ended_events,
                final_seen=True,
                final_sample_index=final_marker.sample_index,
            )

        turn_event = decode_turn_event_from_dora(payload, metadata)
        if turn_event.session_id != session_id:
            raise TurnProbeError(
                f"Turn probe session mismatch: expected {session_id!r}, got "
                f"{turn_event.session_id!r}"
            )
        if turn_event.stream_id != stream_id:
            raise TurnProbeError(
                f"Turn probe stream mismatch: expected {stream_id!r}, got "
                f"{turn_event.stream_id!r}"
            )
        if previous_event is not None and turn_event.seq != previous_event.seq + 1:
            raise TurnProbeError(
                f"TurnEvent seq discontinuity: expected {previous_event.seq + 1}, "
                f"got {turn_event.seq}"
            )
        events += 1
        if turn_event.state == "started":
            started_events += 1
        if turn_event.state == "ended":
            ended_events += 1
        previous_event = turn_event

    raise TurnProbeError("DORA turn stream ended without final marker")


def validate_summary(
    summary: TurnProbeSummary,
    *,
    expected_min_total_events: int,
    expected_min_started_events: int,
    expected_min_ended_events: int,
    expected_final_sample_index: int,
) -> None:
    if summary.events < expected_min_total_events:
        raise TurnProbeError(
            f"Turn event count below expectation: expected at least "
            f"{expected_min_total_events}, got {summary.events}"
        )
    if summary.started_events < expected_min_started_events:
        raise TurnProbeError(
            "Turn started event count below expectation: "
            f"expected at least {expected_min_started_events}, got {summary.started_events}"
        )
    if summary.ended_events < expected_min_ended_events:
        raise TurnProbeError(
            "Turn ended event count below expectation: "
            f"expected at least {expected_min_ended_events}, got {summary.ended_events}"
        )
    if summary.final_sample_index != expected_final_sample_index:
        raise TurnProbeError(
            "Turn final sample_index mismatch: "
            f"expected {expected_final_sample_index}, got {summary.final_sample_index}"
        )
    if not summary.final_seen:
        raise TurnProbeError("Turn probe did not receive final marker")


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise TurnProbeError(f"DORA event field {key!r} must be a string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
