"""DORA activity probe sink for VAD smoke verification."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict, Field

from fluent_audio.contracts import VoiceActivityEvent
from fluent_audio.dora import (
    decode_voice_activity_event_from_dora,
    validate_dora_voice_activity_final_marker,
    validate_dora_voice_activity_metadata,
)


class ActivityProbeError(ValueError):
    """Raised when DORA activity probe validation fails."""


class ActivityProbeSummary(BaseModel):
    """Validated smoke summary for a DORA activity stream."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    events: int = Field(ge=0)
    speech_events: int = Field(ge=0)
    final_seen: bool
    final_sample_index: int = Field(ge=0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and discard DORA activity events.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--stream-id", required=True)
    parser.add_argument("--expected-total-events", required=True, type=int)
    parser.add_argument("--expected-min-speech-events", required=True, type=int)
    parser.add_argument("--expected-final-sample-index", required=True, type=int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("activity_probe requires --dora")

    from dora import Node

    summary = run_activity_probe_dora(
        Node(),
        source_id=args.source_id,
        stream_id=args.stream_id,
    )
    validate_summary(
        summary,
        expected_total_events=args.expected_total_events,
        expected_min_speech_events=args.expected_min_speech_events,
        expected_final_sample_index=args.expected_final_sample_index,
    )
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def run_activity_probe_dora(
    node,
    *,
    source_id: str,
    stream_id: str,
) -> ActivityProbeSummary:
    events = 0
    speech_events = 0
    previous_event: VoiceActivityEvent | None = None

    for event in node:
        if event is None:
            raise ActivityProbeError("DORA event stream ended before activity final marker")

        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            raise ActivityProbeError("DORA STOP arrived before activity final marker")
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id != "activity":
                raise ActivityProbeError(f"Unexpected DORA input id: {input_id!r}")
            raise ActivityProbeError("DORA input closed before activity final marker")
        if event_type != "INPUT":
            raise ActivityProbeError(f"Unexpected DORA event type: {event_type!r}")

        input_id = _required_event_text(event, "id")
        if input_id != "activity":
            raise ActivityProbeError(f"Unexpected DORA input id: {input_id!r}")

        payload = event.get("value")
        metadata = validate_dora_voice_activity_metadata(event.get("metadata"))
        if metadata.final:
            final_marker = validate_dora_voice_activity_final_marker(payload, metadata)
            if final_marker.source_id != source_id:
                raise ActivityProbeError(
                    "Activity probe final marker source mismatch: "
                    f"expected {source_id!r}, got {final_marker.source_id!r}"
                )
            if final_marker.stream_id != stream_id:
                raise ActivityProbeError(
                    "Activity probe final marker stream mismatch: "
                    f"expected {stream_id!r}, got {final_marker.stream_id!r}"
                )
            if final_marker.seq != events:
                raise ActivityProbeError(
                    f"Activity probe final marker seq mismatch: expected {events}, "
                    f"got {final_marker.seq}"
                )
            return ActivityProbeSummary(
                events=events,
                speech_events=speech_events,
                final_seen=True,
                final_sample_index=final_marker.sample_index,
            )

        activity_event = decode_voice_activity_event_from_dora(payload, metadata)
        if activity_event.source_id != source_id:
            raise ActivityProbeError(
                "Activity probe source mismatch: "
                f"expected {source_id!r}, got {activity_event.source_id!r}"
            )
        if activity_event.stream_id != stream_id:
            raise ActivityProbeError(
                "Activity probe stream mismatch: "
                f"expected {stream_id!r}, got {activity_event.stream_id!r}"
            )
        if previous_event is not None:
            _require_contiguous_activity_events(previous_event, activity_event)
        events += 1
        if activity_event.state == "speech":
            speech_events += 1
        previous_event = activity_event

    raise ActivityProbeError("DORA activity stream ended without final marker")


def validate_summary(
    summary: ActivityProbeSummary,
    *,
    expected_total_events: int,
    expected_min_speech_events: int,
    expected_final_sample_index: int,
) -> None:
    if summary.events != expected_total_events:
        raise ActivityProbeError(
            "Activity probe event count mismatch: "
            f"expected {expected_total_events}, got {summary.events}"
        )
    if summary.speech_events < expected_min_speech_events:
        raise ActivityProbeError(
            "Activity probe speech event count below minimum: "
            f"expected at least {expected_min_speech_events}, got {summary.speech_events}"
        )
    if summary.final_sample_index != expected_final_sample_index:
        raise ActivityProbeError(
            "Activity probe final sample_index mismatch: "
            f"expected {expected_final_sample_index}, got {summary.final_sample_index}"
        )
    if not summary.final_seen:
        raise ActivityProbeError("Activity probe did not receive final marker")


def _require_contiguous_activity_events(
    previous: VoiceActivityEvent,
    current: VoiceActivityEvent,
) -> None:
    if current.seq != previous.seq + 1:
        raise ActivityProbeError(
            f"VoiceActivityEvent seq discontinuity: expected {previous.seq + 1}, "
            f"got {current.seq}"
        )
    expected_sample_index = previous.sample_index + previous.frame_count
    if current.sample_index != expected_sample_index:
        raise ActivityProbeError(
            "VoiceActivityEvent sample_index discontinuity: "
            f"expected {expected_sample_index}, got {current.sample_index}"
        )


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise ActivityProbeError(f"DORA event field {key!r} must be a string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
