"""DORA node for deterministic turn detection from voice activity events."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Sequence
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pydantic import BaseModel, ConfigDict, Field

from fluent_dialogue_dora.contracts import TurnEvent, VoiceActivityEvent
from fluent_dialogue_dora.dora import (
    DoraVoiceActivityMetadata,
    decode_voice_activity_event_from_dora,
    encode_turn_event_for_dora,
    encode_turn_final_marker_for_dora,
    validate_dora_voice_activity_final_marker,
    validate_dora_voice_activity_metadata,
)
from nodes.vad.turn_detector.logic import (
    TurnDetectorConfig,
    TurnDetectorState,
)

DORA_FINAL_MARKER_DRAIN_SECONDS = 0.1


class TurnDetectorNodeError(ValueError):
    """Raised when the turn detector DORA node receives invalid input."""


class TurnDetectorNodeConfig(BaseModel):
    """Runtime configuration for one turn detector DORA node."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    input_source_id: str = Field(min_length=1)
    input_stream_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    output_stream_id: str = Field(min_length=1)
    end_silence_frames: int = Field(default=1024, gt=0)
    user_turn_id_prefix: str = Field(default="user-turn", min_length=1)

    def to_logic_config(self) -> TurnDetectorConfig:
        return TurnDetectorConfig(
            session_id=self.session_id,
            output_stream_id=self.output_stream_id,
            end_silence_frames=self.end_silence_frames,
            user_turn_id_prefix=self.user_turn_id_prefix,
        )


class TurnDetectorNodeSummary(BaseModel):
    """Validated processing summary for one activity stream."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    activity_events: int = Field(ge=0)
    turn_events: int = Field(ge=0)
    started_events: int = Field(ge=0)
    ended_events: int = Field(ge=0)
    final_sample_index: int = Field(ge=0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run turn detection over DORA activity input.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--input-source-id", required=True)
    parser.add_argument("--input-stream-id", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--output-stream-id", required=True)
    parser.add_argument("--end-silence-frames", type=int, default=1024)
    parser.add_argument("--user-turn-id-prefix", default="user-turn")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("turn_detector requires --dora")

    from dora import Node

    config = TurnDetectorNodeConfig(
        input_source_id=args.input_source_id,
        input_stream_id=args.input_stream_id,
        session_id=args.session_id,
        output_stream_id=args.output_stream_id,
        end_silence_frames=args.end_silence_frames,
        user_turn_id_prefix=args.user_turn_id_prefix,
    )
    summary = run_turn_detector_events(Node(), config)
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def run_turn_detector_events(
    node,
    config: TurnDetectorNodeConfig,
) -> TurnDetectorNodeSummary:
    detector = TurnDetectorState(config.to_logic_config())
    activity_events = 0
    turn_events = 0
    started_events = 0
    ended_events = 0
    previous_activity: VoiceActivityEvent | None = None

    for event in node:
        if event is None:
            raise TurnDetectorNodeError("DORA event stream ended before activity completion")

        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            raise TurnDetectorNodeError("DORA STOP arrived before activity completion")
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id != "activity":
                raise TurnDetectorNodeError(f"Unexpected DORA input id: {input_id!r}")
            if previous_activity is None:
                raise TurnDetectorNodeError("DORA activity input closed before activity events")
            final_sample_index = previous_activity.sample_index + previous_activity.frame_count
            emitted = detector.finish(final_sample_index)
            turn_events, started_events, ended_events = _send_turn_events(
                node,
                emitted,
                turn_events=turn_events,
                started_events=started_events,
                ended_events=ended_events,
            )
            _send_turn_final(node, config, turn_events, final_sample_index)
            return TurnDetectorNodeSummary(
                activity_events=activity_events,
                turn_events=turn_events,
                started_events=started_events,
                ended_events=ended_events,
                final_sample_index=final_sample_index,
            )
        if event_type != "INPUT":
            continue

        input_id = _required_event_text(event, "id")
        if input_id != "activity":
            raise TurnDetectorNodeError(f"Unexpected DORA input id: {input_id!r}")

        payload = event.get("value")
        metadata = validate_dora_voice_activity_metadata(event.get("metadata"))
        if metadata.final:
            final_marker = validate_dora_voice_activity_final_marker(payload, metadata)
            _validate_activity_final_marker(final_marker, previous_activity, config)
            emitted = detector.finish(final_marker.sample_index)
            turn_events, started_events, ended_events = _send_turn_events(
                node,
                emitted,
                turn_events=turn_events,
                started_events=started_events,
                ended_events=ended_events,
            )
            _send_turn_final(node, config, turn_events, final_marker.sample_index)
            return TurnDetectorNodeSummary(
                activity_events=activity_events,
                turn_events=turn_events,
                started_events=started_events,
                ended_events=ended_events,
                final_sample_index=final_marker.sample_index,
            )

        activity_event = decode_voice_activity_event_from_dora(payload, metadata)
        _validate_activity_event(activity_event, config)
        emitted = detector.push(activity_event)
        turn_events, started_events, ended_events = _send_turn_events(
            node,
            emitted,
            turn_events=turn_events,
            started_events=started_events,
            ended_events=ended_events,
        )
        previous_activity = activity_event
        activity_events += 1

    raise TurnDetectorNodeError("DORA activity stream ended without completion")


def _send_turn_events(
    node,
    events: list[TurnEvent],
    *,
    turn_events: int,
    started_events: int,
    ended_events: int,
) -> tuple[int, int, int]:
    sent_turn_events = turn_events
    sent_started_events = started_events
    sent_ended_events = ended_events
    for event in events:
        payload, metadata = encode_turn_event_for_dora(event)
        node.send_output("turn", payload, metadata=metadata.to_dora_metadata())
        sent_turn_events += 1
        if event.state == "started":
            sent_started_events += 1
        if event.state == "ended":
            sent_ended_events += 1
    return sent_turn_events, sent_started_events, sent_ended_events


def _send_turn_final(
    node,
    config: TurnDetectorNodeConfig,
    seq: int,
    sample_index: int,
) -> None:
    payload, metadata = encode_turn_final_marker_for_dora(
        config.session_id,
        config.output_stream_id,
        seq,
        sample_index,
    )
    node.send_output("turn", payload, metadata=metadata.to_dora_metadata())
    _drain_dora_final_marker_send()


def _validate_activity_event(
    event: VoiceActivityEvent,
    config: TurnDetectorNodeConfig,
) -> None:
    if event.source_id != config.input_source_id:
        raise TurnDetectorNodeError(
            "Turn detector activity source mismatch: "
            f"expected {config.input_source_id!r}, got {event.source_id!r}"
        )
    if event.stream_id != config.input_stream_id:
        raise TurnDetectorNodeError(
            "Turn detector activity stream mismatch: "
            f"expected {config.input_stream_id!r}, got {event.stream_id!r}"
        )


def _validate_activity_final_marker(
    final_marker: DoraVoiceActivityMetadata,
    previous_activity: VoiceActivityEvent | None,
    config: TurnDetectorNodeConfig,
) -> None:
    if final_marker.source_id != config.input_source_id:
        raise TurnDetectorNodeError(
            "Turn detector final source mismatch: "
            f"expected {config.input_source_id!r}, got {final_marker.source_id!r}"
        )
    if final_marker.stream_id != config.input_stream_id:
        raise TurnDetectorNodeError(
            "Turn detector final stream mismatch: "
            f"expected {config.input_stream_id!r}, got {final_marker.stream_id!r}"
        )
    if previous_activity is None:
        raise TurnDetectorNodeError("Turn detector received final marker before activity events")
    expected_seq = previous_activity.seq + 1
    expected_min_sample_index = previous_activity.sample_index
    expected_max_sample_index = previous_activity.sample_index + previous_activity.frame_count
    if final_marker.seq != expected_seq:
        raise TurnDetectorNodeError(
            f"Turn detector final seq discontinuity: expected {expected_seq}, "
            f"got {final_marker.seq}"
        )
    if not expected_min_sample_index < final_marker.sample_index <= expected_max_sample_index:
        raise TurnDetectorNodeError(
            "Turn detector final sample_index discontinuity: "
            f"expected > {expected_min_sample_index} and <= {expected_max_sample_index}, "
            f"got {final_marker.sample_index}"
        )


def _drain_dora_final_marker_send() -> None:
    # The DORA Python API exposes no output flush/ack. Keep the node alive briefly
    # after sending the explicit final marker so process teardown cannot race daemon
    # ingestion; turn probes still fail closed if that marker is not observed.
    time.sleep(DORA_FINAL_MARKER_DRAIN_SECONDS)


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise TurnDetectorNodeError(f"DORA event field {key!r} must be a string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
