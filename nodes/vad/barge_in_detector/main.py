"""DORA node detecting user barge-in during agent playback.

Subscribes to voice activity (from the VAD) and playback state (from the
playback queue). While the agent is playing, sustained user speech emits a
single BargeInEvent. This node only signals; the dialogue engine acts on it.
"""
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

from fluent_dialogue_dora.contracts import BargeInEvent, BargeInStreamFinal
from fluent_dialogue_dora.dora import (
    decode_playback_state_from_dora,
    decode_voice_activity_event_from_dora,
    encode_barge_in_event_for_dora,
    encode_barge_in_stream_final_for_dora,
    validate_dora_playback_state_metadata,
    validate_dora_voice_activity_metadata,
)
from nodes.vad.barge_in_detector.logic import (
    BargeInDetectorConfig,
    BargeInDetectorState,
)

DORA_FINAL_MARKER_DRAIN_SECONDS = 0.1
ACTIVITY_INPUT_ID = "activity"
PLAYBACK_STATE_INPUT_ID = "playback_state"
BARGE_IN_OUTPUT_ID = "barge_in"


class BargeInDetectorNodeError(ValueError):
    """Raised when the barge-in detector DORA node receives invalid input."""


class BargeInDetectorNodeConfig(BaseModel):
    """Runtime configuration for one barge-in detector DORA node."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    output_stream_id: str = Field(min_length=1)
    barge_in_speech_frames: int = Field(default=4800, gt=0)
    silence_reset_frames: int = Field(default=2048, gt=0)
    min_speech_probability: float = Field(default=0.5, ge=0.0, le=1.0)

    def to_logic_config(self) -> BargeInDetectorConfig:
        return BargeInDetectorConfig(
            session_id=self.session_id,
            source_id=self.source_id,
            output_stream_id=self.output_stream_id,
            barge_in_speech_frames=self.barge_in_speech_frames,
            silence_reset_frames=self.silence_reset_frames,
            min_speech_probability=self.min_speech_probability,
        )


class BargeInDetectorNodeSummary(BaseModel):
    """Validated processing summary for one barge-in detector run."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    activity_events: int = Field(ge=0)
    playback_states: int = Field(ge=0)
    barge_in_events: int = Field(ge=0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detect user barge-in during agent playback.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--source-id", default="barge_in_detector")
    parser.add_argument("--output-stream-id", required=True)
    parser.add_argument("--barge-in-speech-frames", type=int, default=4800)
    parser.add_argument("--silence-reset-frames", type=int, default=2048)
    parser.add_argument("--min-speech-probability", type=float, default=0.5)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("barge_in_detector requires --dora")

    from dora import Node

    config = BargeInDetectorNodeConfig(
        session_id=args.session_id,
        source_id=args.source_id,
        output_stream_id=args.output_stream_id,
        barge_in_speech_frames=args.barge_in_speech_frames,
        silence_reset_frames=args.silence_reset_frames,
        min_speech_probability=args.min_speech_probability,
    )
    summary = run_barge_in_detector_events(Node(), config)
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def run_barge_in_detector_events(
    node,
    config: BargeInDetectorNodeConfig,
) -> BargeInDetectorNodeSummary:
    detector = BargeInDetectorState(config.to_logic_config())
    activity_events = 0
    playback_states = 0
    barge_in_events = 0
    open_inputs = {ACTIVITY_INPUT_ID, PLAYBACK_STATE_INPUT_ID}

    for event in node:
        if event is None:
            break

        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            break
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            open_inputs.discard(input_id)
            if not open_inputs:
                break
            continue
        if event_type != "INPUT":
            continue

        input_id = _required_event_text(event, "id")
        payload = event.get("value")
        if input_id == PLAYBACK_STATE_INPUT_ID:
            metadata = validate_dora_playback_state_metadata(event.get("metadata"))
            state = decode_playback_state_from_dora(payload, metadata)
            detector.on_playback_state(state)
            playback_states += 1
            continue
        if input_id == ACTIVITY_INPUT_ID:
            metadata = validate_dora_voice_activity_metadata(event.get("metadata"))
            if metadata.final:
                # The VAD stream ended; no more user audio to consider.
                continue
            activity_event = decode_voice_activity_event_from_dora(payload, metadata)
            for barge_in in detector.on_activity(activity_event):
                _send_barge_in(node, barge_in)
                barge_in_events += 1
            activity_events += 1
            continue
        raise BargeInDetectorNodeError(f"Unexpected DORA input id: {input_id!r}")

    _send_barge_in_final(node, config, detector.next_output_seq)
    return BargeInDetectorNodeSummary(
        activity_events=activity_events,
        playback_states=playback_states,
        barge_in_events=barge_in_events,
    )


def _send_barge_in(node, barge_in: BargeInEvent) -> None:
    payload, metadata = encode_barge_in_event_for_dora(barge_in)
    node.send_output(BARGE_IN_OUTPUT_ID, payload, metadata=metadata.to_dora_metadata())


def _send_barge_in_final(node, config: BargeInDetectorNodeConfig, seq: int) -> None:
    payload, metadata = encode_barge_in_stream_final_for_dora(
        BargeInStreamFinal(
            session_id=config.session_id,
            source_id=config.source_id,
            stream_id=config.output_stream_id,
            seq=seq,
        )
    )
    node.send_output(BARGE_IN_OUTPUT_ID, payload, metadata=metadata.to_dora_metadata())
    _drain_dora_final_marker_send()


def _drain_dora_final_marker_send() -> None:
    # The DORA Python API exposes no output flush/ack; keep the node alive briefly
    # so process teardown cannot race daemon ingestion of the final marker.
    time.sleep(DORA_FINAL_MARKER_DRAIN_SECONDS)


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise BargeInDetectorNodeError(f"DORA event field {key!r} must be a string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
