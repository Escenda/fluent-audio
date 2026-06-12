"""DORA node converting turn events into ASR control commands."""
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

from fluent_audio.contracts import AsrCancel, AsrStart, AsrStop, TurnEvent
from fluent_audio.dora import (
    decode_turn_event_from_dora,
    encode_asr_control_for_dora,
    encode_asr_control_final_marker_for_dora,
    validate_dora_turn_final_marker,
    validate_dora_turn_metadata,
)

DEFAULT_DORA_OUTPUT_DRAIN_SECONDS = 0.5


class AsrControlFromTurnError(ValueError):
    """Raised when turn-to-ASR-control conversion receives invalid input."""


class AsrControlFromTurnConfig(BaseModel):
    """Runtime configuration for one turn-to-ASR-control DORA node."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    input_session_id: str = Field(min_length=1)
    input_turn_stream_id: str = Field(min_length=1)
    output_audio_stream_id: str = Field(min_length=1)
    asr_prebuffer_frames: int = Field(default=0, ge=0)
    output_drain_seconds: float = Field(default=DEFAULT_DORA_OUTPUT_DRAIN_SECONDS, ge=0.0)


class AsrControlFromTurnSummary(BaseModel):
    """Validated processing summary for one turn stream."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    turn_events: int = Field(ge=0)
    start_controls: int = Field(ge=0)
    stop_controls: int = Field(ge=0)
    cancel_controls: int = Field(ge=0)
    final_sample_index: int = Field(ge=0)
    first_start_sample_index: int | None = Field(default=None, ge=0)
    last_stop_sample_index: int | None = Field(default=None, ge=0)


class AsrControlFromTurnState:
    """State machine mapping one validated turn stream to ASR controls."""

    def __init__(self, config: AsrControlFromTurnConfig) -> None:
        self._config = config
        self._active_user_turn_id: str | None = None
        self._next_control_seq = 0
        self._previous_turn_seq: int | None = None

    @property
    def next_control_seq(self) -> int:
        return self._next_control_seq

    def push(self, turn: TurnEvent) -> AsrStart | AsrStop | AsrCancel | None:
        self._validate_turn(turn)
        self._previous_turn_seq = turn.seq
        if turn.state == "started":
            if self._active_user_turn_id is not None:
                raise AsrControlFromTurnError("ASR control start received while a turn is active")
            self._active_user_turn_id = turn.user_turn_id
            start_sample_index = max(0, turn.sample_index - self._config.asr_prebuffer_frames)
            return self._next_start(turn, start_sample_index)
        if turn.state == "active":
            self._require_active_turn(turn)
            return None
        if turn.state == "ended":
            self._require_active_turn(turn)
            self._active_user_turn_id = None
            return self._next_stop(turn)
        if turn.state == "cancelled":
            self._require_active_turn(turn)
            self._active_user_turn_id = None
            return self._next_cancel(turn)
        return None

    def finish(self, final_sample_index: int) -> None:
        if self._active_user_turn_id is not None:
            raise AsrControlFromTurnError("Turn stream ended while an ASR turn is active")
        if final_sample_index < 0:
            raise AsrControlFromTurnError("Turn final sample_index must be non-negative")

    def _next_start(self, turn: TurnEvent, start_sample_index: int) -> AsrStart:
        control = AsrStart(
            action="start",
            session_id=turn.session_id,
            user_turn_id=turn.user_turn_id,
            stream_id=self._config.output_audio_stream_id,
            seq=self._next_control_seq,
            start_sample_index=start_sample_index,
        )
        self._next_control_seq += 1
        return control

    def _next_stop(self, turn: TurnEvent) -> AsrStop:
        control = AsrStop(
            action="stop",
            session_id=turn.session_id,
            user_turn_id=turn.user_turn_id,
            stream_id=self._config.output_audio_stream_id,
            seq=self._next_control_seq,
            stop_sample_index=turn.sample_index,
        )
        self._next_control_seq += 1
        return control

    def _next_cancel(self, turn: TurnEvent) -> AsrCancel:
        control = AsrCancel(
            action="cancel",
            session_id=turn.session_id,
            user_turn_id=turn.user_turn_id,
            stream_id=self._config.output_audio_stream_id,
            seq=self._next_control_seq,
            reason="turn_cancelled",
        )
        self._next_control_seq += 1
        return control

    def _validate_turn(self, turn: TurnEvent) -> None:
        if turn.session_id != self._config.input_session_id:
            raise AsrControlFromTurnError(
                "Turn session mismatch: "
                f"expected {self._config.input_session_id!r}, got {turn.session_id!r}"
            )
        if turn.stream_id != self._config.input_turn_stream_id:
            raise AsrControlFromTurnError(
                "Turn stream mismatch: "
                f"expected {self._config.input_turn_stream_id!r}, got {turn.stream_id!r}"
            )
        if self._previous_turn_seq is not None and turn.seq != self._previous_turn_seq + 1:
            raise AsrControlFromTurnError(
                "Turn seq discontinuity: "
                f"expected {self._previous_turn_seq + 1}, got {turn.seq}"
            )

    def _require_active_turn(self, turn: TurnEvent) -> None:
        if self._active_user_turn_id is None:
            raise AsrControlFromTurnError("Turn event requires an active ASR turn")
        if turn.user_turn_id != self._active_user_turn_id:
            raise AsrControlFromTurnError(
                "Turn user_turn_id mismatch: "
                f"expected {self._active_user_turn_id!r}, got {turn.user_turn_id!r}"
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert turn events into ASR control.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--input-session-id", required=True)
    parser.add_argument("--input-turn-stream-id", required=True)
    parser.add_argument("--output-audio-stream-id", required=True)
    parser.add_argument("--asr-prebuffer-frames", type=int, default=0)
    parser.add_argument(
        "--output-drain-seconds",
        type=float,
        default=DEFAULT_DORA_OUTPUT_DRAIN_SECONDS,
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("asr_control_from_turn requires --dora")

    from dora import Node

    config = AsrControlFromTurnConfig(
        input_session_id=args.input_session_id,
        input_turn_stream_id=args.input_turn_stream_id,
        output_audio_stream_id=args.output_audio_stream_id,
        asr_prebuffer_frames=args.asr_prebuffer_frames,
        output_drain_seconds=args.output_drain_seconds,
    )
    summary = run_asr_control_from_turn_events(Node(), config)
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def run_asr_control_from_turn_events(
    node,
    config: AsrControlFromTurnConfig,
) -> AsrControlFromTurnSummary:
    state = AsrControlFromTurnState(config)
    turn_events = 0
    start_controls = 0
    stop_controls = 0
    cancel_controls = 0
    first_start_sample_index: int | None = None
    last_stop_sample_index: int | None = None

    for event in node:
        if event is None:
            raise AsrControlFromTurnError("DORA event stream ended before turn final marker")

        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            raise AsrControlFromTurnError("DORA STOP arrived before turn final marker")
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id != "turn":
                raise AsrControlFromTurnError(f"Unexpected DORA input id: {input_id!r}")
            raise AsrControlFromTurnError("DORA input closed before turn final marker")
        if event_type != "INPUT":
            raise AsrControlFromTurnError(f"Unexpected DORA event type: {event_type!r}")

        input_id = _required_event_text(event, "id")
        if input_id != "turn":
            raise AsrControlFromTurnError(f"Unexpected DORA input id: {input_id!r}")

        payload = event.get("value")
        metadata = validate_dora_turn_metadata(event.get("metadata"))
        if metadata.final:
            final_marker = validate_dora_turn_final_marker(payload, metadata)
            if final_marker.session_id != config.input_session_id:
                raise AsrControlFromTurnError(
                    "Turn final session mismatch: "
                    f"expected {config.input_session_id!r}, got {final_marker.session_id!r}"
                )
            if final_marker.stream_id != config.input_turn_stream_id:
                raise AsrControlFromTurnError(
                    "Turn final stream mismatch: "
                    f"expected {config.input_turn_stream_id!r}, got {final_marker.stream_id!r}"
            )
            state.finish(final_marker.sample_index)
            _send_asr_control_final_marker(node, config, state.next_control_seq)
            _drain_dora_output_send(config.output_drain_seconds)
            return AsrControlFromTurnSummary(
                turn_events=turn_events,
                start_controls=start_controls,
                stop_controls=stop_controls,
                cancel_controls=cancel_controls,
                final_sample_index=final_marker.sample_index,
                first_start_sample_index=first_start_sample_index,
                last_stop_sample_index=last_stop_sample_index,
            )

        turn_event = decode_turn_event_from_dora(payload, metadata)
        control = state.push(turn_event)
        turn_events += 1
        if control is None:
            continue
        _send_asr_control(node, control)
        if isinstance(control, AsrStart):
            start_controls += 1
            if first_start_sample_index is None:
                first_start_sample_index = control.start_sample_index
        elif isinstance(control, AsrStop):
            stop_controls += 1
            last_stop_sample_index = control.stop_sample_index
        else:
            cancel_controls += 1

    raise AsrControlFromTurnError("DORA turn stream ended without final marker")


def _send_asr_control(
    node,
    control: AsrStart | AsrStop | AsrCancel,
) -> None:
    payload, metadata = encode_asr_control_for_dora(control)
    node.send_output("asr_control", payload, metadata=metadata.to_dora_metadata())


def _send_asr_control_final_marker(
    node,
    config: AsrControlFromTurnConfig,
    seq: int,
) -> None:
    payload, metadata = encode_asr_control_final_marker_for_dora(
        session_id=config.input_session_id,
        stream_id=config.output_audio_stream_id,
        seq=seq,
    )
    node.send_output("asr_control", payload, metadata=metadata.to_dora_metadata())


def _drain_dora_output_send(output_drain_seconds: float) -> None:
    # The DORA Python API exposes no output flush/ack. Keep this translator alive
    # briefly after the upstream turn stream closes so final ASR controls are not
    # lost to process teardown before the daemon ingests them.
    time.sleep(output_drain_seconds)


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise AsrControlFromTurnError(f"DORA event field {key!r} must be a string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
