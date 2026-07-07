"""Pure DORA-to-ROS2 projection runner for the ROS2 bridge.

This module intentionally does not import rclpy. It validates DORA payloads at
the bridge boundary, projects them to typed ROS-facing models, and hands those
models to a publisher interface. A future ROS2 sidecar can implement that
publisher with generated message classes.
"""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol, TypeAlias

import pyarrow as pa
from pydantic import BaseModel, ConfigDict, Field, model_validator

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fluent_dialogue_dora.dora import (
    DoraMetadataMapping,
    decode_agent_approval_request_from_dora,
    decode_agent_text_delta_from_dora,
    decode_agent_tool_event_from_dora,
    decode_agent_turn_done_from_dora,
    decode_asr_control_from_dora,
    decode_audio_chunk_from_dora,
    decode_dialogue_event_from_dora,
    decode_playback_command_from_dora,
    decode_playback_done_from_dora,
    decode_playback_state_from_dora,
    decode_transcript_delta_from_dora,
    decode_transcript_final_from_dora,
    decode_transcript_partial_from_dora,
    decode_turn_event_from_dora,
    decode_voice_activity_event_from_dora,
    decode_voice_session_event_from_dora,
    validate_dora_asr_control_final_marker,
    validate_dora_asr_control_metadata,
    validate_dora_audio_final_marker,
    validate_dora_audio_metadata,
    validate_dora_transcript_metadata,
    validate_dora_transcript_stream_final_marker,
    validate_dora_turn_final_marker,
    validate_dora_turn_metadata,
    validate_dora_voice_activity_final_marker,
    validate_dora_voice_activity_metadata,
)
from bridges.ros2_bridge.messages import (
    Ros2AgentApprovalRequest,
    Ros2AgentTextDelta,
    Ros2AgentToolEvent,
    Ros2AgentTurnDone,
    Ros2AsrControl,
    Ros2AudioFrame,
    Ros2DialogueEvent,
    Ros2PlaybackCommand,
    Ros2PlaybackDone,
    Ros2PlaybackState,
    Ros2Transcript,
    Ros2TurnEvent,
    Ros2VoiceActivity,
    Ros2VoiceSessionEvent,
    agent_approval_request_to_ros2,
    agent_text_delta_to_ros2,
    agent_tool_event_to_ros2,
    agent_turn_done_to_ros2,
    asr_control_to_ros2,
    audio_chunk_to_ros2,
    audio_final_marker_to_ros2,
    dialogue_event_to_ros2,
    playback_command_to_ros2,
    playback_done_to_ros2,
    playback_state_to_ros2,
    transcript_delta_to_ros2,
    transcript_final_to_ros2,
    transcript_partial_to_ros2,
    transcript_stream_final_to_ros2,
    turn_event_to_ros2,
    turn_final_marker_to_ros2,
    voice_activity_final_marker_to_ros2,
    voice_activity_to_ros2,
    voice_session_event_to_ros2,
)

Ros2BridgeEventType: TypeAlias = Literal["INPUT", "INPUT_CLOSED", "STOP"]
Ros2BridgeInputId: TypeAlias = Literal[
    "audio",
    "activity",
    "turn",
    "asr_control",
    "transcript",
    "session",
    "dialogue",
    "agent_text",
    "agent_done",
    "agent_approval",
    "agent_tool",
    "playback_command",
    "playback_state",
    "playback_done",
]
Ros2BridgeFiniteInputId: TypeAlias = Literal[
    "audio",
    "activity",
    "turn",
    "asr_control",
    "transcript",
]
Ros2BridgePayloadInput: TypeAlias = bytes | pa.UInt8Array
Ros2BridgeRawEventValue: TypeAlias = str | Ros2BridgePayloadInput | DoraMetadataMapping
Ros2BridgeRawEvent: TypeAlias = Mapping[str, Ros2BridgeRawEventValue]

ROS2_BRIDGE_INPUT_IDS: tuple[Ros2BridgeInputId, ...] = (
    "audio",
    "activity",
    "turn",
    "asr_control",
    "transcript",
    "session",
    "dialogue",
    "agent_text",
    "agent_done",
    "agent_approval",
    "agent_tool",
    "playback_command",
    "playback_state",
    "playback_done",
)

ROS2_BRIDGE_FINITE_INPUT_IDS: tuple[Ros2BridgeFiniteInputId, ...] = (
    "audio",
    "activity",
    "turn",
    "asr_control",
    "transcript",
)


class Ros2BridgeProjectionError(ValueError):
    """Raised when the bridge cannot project a DORA event to ROS2."""


class Ros2BridgeProjectionConfig(BaseModel):
    """Pure projection configuration for the ROS2 bridge."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    required_final_inputs: tuple[Ros2BridgeFiniteInputId, ...] = Field(default=())

    @model_validator(mode="after")
    def validate_required_inputs(self) -> "Ros2BridgeProjectionConfig":
        if len(set(self.required_final_inputs)) != len(self.required_final_inputs):
            raise ValueError("required_final_inputs must not contain duplicates")
        return self


class Ros2BridgeJsonlRecord(BaseModel):
    """Serialized projection record for rclpy-free DORA smokes."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    topic: str = Field(min_length=1)
    message_type: str = Field(min_length=1)
    payload_json: str = Field(min_length=1)


@dataclass
class Ros2BridgeProjectionSummary:
    """Counters for one pure projection run."""

    processed_inputs: int = 0
    published_messages: int = 0
    final_inputs: int = 0
    audio_frames: int = 0
    audio_final_markers: int = 0
    activity_events: int = 0
    activity_final_markers: int = 0
    turn_events: int = 0
    turn_final_markers: int = 0
    asr_controls: int = 0
    asr_control_final_markers: int = 0
    transcript_deltas: int = 0
    transcript_partials: int = 0
    transcript_finals: int = 0
    transcript_stream_finals: int = 0
    session_events: int = 0
    dialogue_events: int = 0
    agent_text_deltas: int = 0
    agent_turn_done: int = 0
    agent_approval_requests: int = 0
    agent_tool_events: int = 0
    playback_commands: int = 0
    playback_states: int = 0
    playback_done: int = 0


class Ros2BridgeProjectionClock(Protocol):
    def time_ns(self) -> int: ...


class SystemRos2BridgeClock:
    def time_ns(self) -> int:
        return time.time_ns()


SYSTEM_ROS2_BRIDGE_CLOCK = SystemRos2BridgeClock()


class Ros2BridgeProjectionPublisher(Protocol):
    def publish_audio_frame(self, message: Ros2AudioFrame) -> None: ...

    def publish_voice_activity(self, message: Ros2VoiceActivity) -> None: ...

    def publish_turn_event(self, message: Ros2TurnEvent) -> None: ...

    def publish_asr_control(self, message: Ros2AsrControl) -> None: ...

    def publish_transcript(self, message: Ros2Transcript) -> None: ...

    def publish_voice_session_event(self, message: Ros2VoiceSessionEvent) -> None: ...

    def publish_dialogue_event(self, message: Ros2DialogueEvent) -> None: ...

    def publish_agent_text_delta(self, message: Ros2AgentTextDelta) -> None: ...

    def publish_agent_turn_done(self, message: Ros2AgentTurnDone) -> None: ...

    def publish_agent_approval_request(self, message: Ros2AgentApprovalRequest) -> None: ...

    def publish_agent_tool_event(self, message: Ros2AgentToolEvent) -> None: ...

    def publish_playback_command(self, message: Ros2PlaybackCommand) -> None: ...

    def publish_playback_state(self, message: Ros2PlaybackState) -> None: ...

    def publish_playback_done(self, message: Ros2PlaybackDone) -> None: ...


class JsonlRos2BridgeProjectionPublisher:
    """Write projected ROS-facing messages as JSONL without importing ROS2."""

    def __init__(self, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._output_file = output_path.open("w", encoding="utf-8")

    def close(self) -> None:
        self._output_file.close()

    def publish_audio_frame(self, message: Ros2AudioFrame) -> None:
        self._write("audio", message)

    def publish_voice_activity(self, message: Ros2VoiceActivity) -> None:
        self._write("activity", message)

    def publish_turn_event(self, message: Ros2TurnEvent) -> None:
        self._write("turn", message)

    def publish_asr_control(self, message: Ros2AsrControl) -> None:
        self._write("asr_control", message)

    def publish_transcript(self, message: Ros2Transcript) -> None:
        self._write("transcript", message)

    def publish_voice_session_event(self, message: Ros2VoiceSessionEvent) -> None:
        self._write("session", message)

    def publish_dialogue_event(self, message: Ros2DialogueEvent) -> None:
        self._write("dialogue", message)

    def publish_agent_text_delta(self, message: Ros2AgentTextDelta) -> None:
        self._write("agent_text", message)

    def publish_agent_turn_done(self, message: Ros2AgentTurnDone) -> None:
        self._write("agent_done", message)

    def publish_agent_approval_request(self, message: Ros2AgentApprovalRequest) -> None:
        self._write("agent_approval", message)

    def publish_agent_tool_event(self, message: Ros2AgentToolEvent) -> None:
        self._write("agent_tool", message)

    def publish_playback_command(self, message: Ros2PlaybackCommand) -> None:
        self._write("playback_command", message)

    def publish_playback_state(self, message: Ros2PlaybackState) -> None:
        self._write("playback_state", message)

    def publish_playback_done(self, message: Ros2PlaybackDone) -> None:
        self._write("playback_done", message)

    def _write(self, topic: str, message: BaseModel) -> None:
        record = Ros2BridgeJsonlRecord(
            topic=topic,
            message_type=message.__class__.__name__,
            payload_json=message.model_dump_json(),
        )
        self._output_file.write(record.model_dump_json())
        self._output_file.write("\n")
        self._output_file.flush()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the fluent-dialogue-dora ROS2 projection bridge.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--jsonl-output", required=True, type=Path)
    parser.add_argument(
        "--required-final-input",
        action="append",
        choices=list(ROS2_BRIDGE_FINITE_INPUT_IDS),
        dest="required_final_inputs",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("ros2_bridge requires --dora")

    from dora import Node

    publisher = JsonlRos2BridgeProjectionPublisher(args.jsonl_output)
    try:
        summary = run_ros2_bridge_projection_events(
            Node(),
            Ros2BridgeProjectionConfig(
                required_final_inputs=tuple(args.required_final_inputs or ()),
            ),
            publisher,
        )
    finally:
        publisher.close()
    sys.stdout.write(_summary_json(summary))
    sys.stdout.write("\n")
    return 0


def run_ros2_bridge_projection_events(
    events: Iterable[Ros2BridgeRawEvent],
    config: Ros2BridgeProjectionConfig,
    publisher: Ros2BridgeProjectionPublisher,
    clock: Ros2BridgeProjectionClock = SYSTEM_ROS2_BRIDGE_CLOCK,
) -> Ros2BridgeProjectionSummary:
    """Project validated DORA input events to ROS-facing typed messages."""

    summary = Ros2BridgeProjectionSummary()
    completed_inputs: set[Ros2BridgeFiniteInputId] = set()

    for raw_event in events:
        event_type = _event_type(raw_event)
        if event_type == "STOP":
            break
        input_id = _event_id(raw_event)
        if event_type == "INPUT_CLOSED":
            _validate_transport_close(input_id, config, completed_inputs)
            continue
        payload = _event_payload(raw_event)
        metadata = _event_metadata(raw_event)
        summary.processed_inputs += 1
        timestamp_ns = clock.time_ns()
        final_input = _project_input_event(
            input_id, payload, metadata, timestamp_ns, publisher, summary
        )
        if final_input:
            finite_input_id = _finite_input_id(input_id)
            completed_inputs.add(finite_input_id)
            summary.final_inputs += 1

    missing_inputs = [
        input_id for input_id in config.required_final_inputs if input_id not in completed_inputs
    ]
    if missing_inputs:
        missing = ", ".join(missing_inputs)
        raise Ros2BridgeProjectionError(
            f"ROS2 bridge event stream ended before required final markers: {missing}"
        )
    return summary


def _project_input_event(
    input_id: Ros2BridgeInputId,
    payload: Ros2BridgePayloadInput,
    metadata: DoraMetadataMapping,
    timestamp_ns: int,
    publisher: Ros2BridgeProjectionPublisher,
    summary: Ros2BridgeProjectionSummary,
) -> bool:
    if input_id == "audio":
        return _project_audio(payload, metadata, publisher, summary)
    if input_id == "activity":
        return _project_activity(payload, metadata, timestamp_ns, publisher, summary)
    if input_id == "turn":
        return _project_turn(payload, metadata, timestamp_ns, publisher, summary)
    if input_id == "asr_control":
        return _project_asr_control(payload, metadata, timestamp_ns, publisher, summary)
    if input_id == "transcript":
        return _project_transcript(payload, metadata, timestamp_ns, publisher, summary)
    if input_id == "session":
        session = decode_voice_session_event_from_dora(payload, metadata)
        publisher.publish_voice_session_event(
            voice_session_event_to_ros2(session, timestamp_ns=timestamp_ns)
        )
        summary.session_events += 1
    elif input_id == "dialogue":
        dialogue = decode_dialogue_event_from_dora(payload, metadata)
        publisher.publish_dialogue_event(
            dialogue_event_to_ros2(dialogue, timestamp_ns=timestamp_ns)
        )
        summary.dialogue_events += 1
    elif input_id == "agent_text":
        text_delta = decode_agent_text_delta_from_dora(payload, metadata)
        publisher.publish_agent_text_delta(
            agent_text_delta_to_ros2(text_delta, timestamp_ns=timestamp_ns)
        )
        summary.agent_text_deltas += 1
    elif input_id == "agent_done":
        turn_done = decode_agent_turn_done_from_dora(payload, metadata)
        publisher.publish_agent_turn_done(
            agent_turn_done_to_ros2(turn_done, timestamp_ns=timestamp_ns)
        )
        summary.agent_turn_done += 1
    elif input_id == "agent_approval":
        approval = decode_agent_approval_request_from_dora(payload, metadata)
        publisher.publish_agent_approval_request(
            agent_approval_request_to_ros2(approval, timestamp_ns=timestamp_ns)
        )
        summary.agent_approval_requests += 1
    elif input_id == "agent_tool":
        tool = decode_agent_tool_event_from_dora(payload, metadata)
        publisher.publish_agent_tool_event(
            agent_tool_event_to_ros2(tool, timestamp_ns=timestamp_ns)
        )
        summary.agent_tool_events += 1
    elif input_id == "playback_command":
        command = decode_playback_command_from_dora(payload, metadata)
        publisher.publish_playback_command(
            playback_command_to_ros2(command, timestamp_ns=timestamp_ns)
        )
        summary.playback_commands += 1
    elif input_id == "playback_state":
        playback_state = decode_playback_state_from_dora(payload, metadata)
        publisher.publish_playback_state(
            playback_state_to_ros2(playback_state, timestamp_ns=timestamp_ns)
        )
        summary.playback_states += 1
    elif input_id == "playback_done":
        playback_done = decode_playback_done_from_dora(payload, metadata)
        publisher.publish_playback_done(
            playback_done_to_ros2(playback_done, timestamp_ns=timestamp_ns)
        )
        summary.playback_done += 1
    summary.published_messages += 1
    return False


def _project_audio(
    payload: Ros2BridgePayloadInput,
    metadata: DoraMetadataMapping,
    publisher: Ros2BridgeProjectionPublisher,
    summary: Ros2BridgeProjectionSummary,
) -> bool:
    audio_metadata = validate_dora_audio_metadata(metadata)
    if audio_metadata.final:
        final_marker = validate_dora_audio_final_marker(payload, audio_metadata)
        publisher.publish_audio_frame(
            audio_final_marker_to_ros2(
                source_id=final_marker.source_id,
                stream_id=final_marker.stream_id,
                seq=final_marker.seq,
                sample_index=final_marker.sample_index,
                capture_time_ns=final_marker.capture_time_ns,
                audio_format=final_marker.to_audio_format(),
            )
        )
        summary.audio_final_markers += 1
        summary.published_messages += 1
        return True
    chunk = decode_audio_chunk_from_dora(payload, audio_metadata)
    publisher.publish_audio_frame(audio_chunk_to_ros2(chunk))
    summary.audio_frames += 1
    summary.published_messages += 1
    return False


def _project_activity(
    payload: Ros2BridgePayloadInput,
    metadata: DoraMetadataMapping,
    timestamp_ns: int,
    publisher: Ros2BridgeProjectionPublisher,
    summary: Ros2BridgeProjectionSummary,
) -> bool:
    activity_metadata = validate_dora_voice_activity_metadata(metadata)
    if activity_metadata.final:
        final_marker = validate_dora_voice_activity_final_marker(payload, activity_metadata)
        publisher.publish_voice_activity(
            voice_activity_final_marker_to_ros2(
                source_id=final_marker.source_id,
                stream_id=final_marker.stream_id,
                seq=final_marker.seq,
                sample_index=final_marker.sample_index,
                timestamp_ns=timestamp_ns,
            )
        )
        summary.activity_final_markers += 1
        summary.published_messages += 1
        return True
    activity = decode_voice_activity_event_from_dora(payload, activity_metadata)
    publisher.publish_voice_activity(voice_activity_to_ros2(activity, timestamp_ns=timestamp_ns))
    summary.activity_events += 1
    summary.published_messages += 1
    return False


def _project_turn(
    payload: Ros2BridgePayloadInput,
    metadata: DoraMetadataMapping,
    timestamp_ns: int,
    publisher: Ros2BridgeProjectionPublisher,
    summary: Ros2BridgeProjectionSummary,
) -> bool:
    turn_metadata = validate_dora_turn_metadata(metadata)
    if turn_metadata.final:
        final_marker = validate_dora_turn_final_marker(payload, turn_metadata)
        publisher.publish_turn_event(
            turn_final_marker_to_ros2(
                session_id=final_marker.session_id,
                stream_id=final_marker.stream_id,
                seq=final_marker.seq,
                sample_index=final_marker.sample_index,
                timestamp_ns=timestamp_ns,
            )
        )
        summary.turn_final_markers += 1
        summary.published_messages += 1
        return True
    turn = decode_turn_event_from_dora(payload, turn_metadata)
    publisher.publish_turn_event(turn_event_to_ros2(turn, timestamp_ns=timestamp_ns))
    summary.turn_events += 1
    summary.published_messages += 1
    return False


def _project_asr_control(
    payload: Ros2BridgePayloadInput,
    metadata: DoraMetadataMapping,
    timestamp_ns: int,
    publisher: Ros2BridgeProjectionPublisher,
    summary: Ros2BridgeProjectionSummary,
) -> bool:
    control_metadata = validate_dora_asr_control_metadata(metadata)
    if control_metadata.final:
        validate_dora_asr_control_final_marker(payload, control_metadata)
        summary.asr_control_final_markers += 1
        return True
    control = decode_asr_control_from_dora(payload, control_metadata)
    publisher.publish_asr_control(asr_control_to_ros2(control, timestamp_ns=timestamp_ns))
    summary.asr_controls += 1
    summary.published_messages += 1
    return False


def _project_transcript(
    payload: Ros2BridgePayloadInput,
    metadata: DoraMetadataMapping,
    timestamp_ns: int,
    publisher: Ros2BridgeProjectionPublisher,
    summary: Ros2BridgeProjectionSummary,
) -> bool:
    transcript_metadata = validate_dora_transcript_metadata(metadata)
    if transcript_metadata.kind == "stream_final":
        final_marker = validate_dora_transcript_stream_final_marker(
            payload,
            transcript_metadata,
        )
        publisher.publish_transcript(
            transcript_stream_final_to_ros2(
                session_id=final_marker.session_id,
                stream_id=final_marker.stream_id,
                seq=final_marker.seq,
                sample_index=final_marker.start_sample_index,
                timestamp_ns=timestamp_ns,
            )
        )
        summary.transcript_stream_finals += 1
        summary.published_messages += 1
        return True
    if transcript_metadata.kind == "delta":
        delta = decode_transcript_delta_from_dora(payload, transcript_metadata)
        publisher.publish_transcript(transcript_delta_to_ros2(delta, timestamp_ns=timestamp_ns))
        summary.transcript_deltas += 1
    elif transcript_metadata.kind == "partial":
        partial = decode_transcript_partial_from_dora(payload, transcript_metadata)
        publisher.publish_transcript(transcript_partial_to_ros2(partial, timestamp_ns=timestamp_ns))
        summary.transcript_partials += 1
    else:
        final = decode_transcript_final_from_dora(payload, transcript_metadata)
        publisher.publish_transcript(transcript_final_to_ros2(final, timestamp_ns=timestamp_ns))
        summary.transcript_finals += 1
    summary.published_messages += 1
    return False


def _event_type(event: Ros2BridgeRawEvent) -> Ros2BridgeEventType:
    if "type" not in event:
        raise Ros2BridgeProjectionError("DORA event is missing type")
    event_type = event["type"]
    if event_type == "INPUT":
        return "INPUT"
    if event_type == "INPUT_CLOSED":
        return "INPUT_CLOSED"
    if event_type == "STOP":
        return "STOP"
    raise Ros2BridgeProjectionError(
        f"ROS2 bridge received unsupported DORA event type: {event_type}"
    )


def _event_id(event: Ros2BridgeRawEvent) -> Ros2BridgeInputId:
    if "id" not in event:
        raise Ros2BridgeProjectionError("DORA event is missing id")
    input_id = event["id"]
    if not isinstance(input_id, str):
        raise Ros2BridgeProjectionError("DORA event id must be a string")
    if input_id in ROS2_BRIDGE_INPUT_IDS:
        return input_id
    raise Ros2BridgeProjectionError(f"ROS2 bridge received unsupported input id: {input_id}")


def _event_payload(event: Ros2BridgeRawEvent) -> Ros2BridgePayloadInput:
    if "value" not in event:
        raise Ros2BridgeProjectionError("DORA INPUT event is missing value")
    payload = event["value"]
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, pa.UInt8Array):
        return payload
    raise Ros2BridgeProjectionError("DORA INPUT value must be bytes or uint8 Arrow array")


def _event_metadata(event: Ros2BridgeRawEvent) -> DoraMetadataMapping:
    if "metadata" not in event:
        raise Ros2BridgeProjectionError("DORA INPUT event is missing metadata")
    metadata = event["metadata"]
    if not isinstance(metadata, Mapping):
        raise Ros2BridgeProjectionError("DORA INPUT metadata must be a mapping")
    return metadata


def _finite_input_id(input_id: Ros2BridgeInputId) -> Ros2BridgeFiniteInputId:
    if input_id in ROS2_BRIDGE_FINITE_INPUT_IDS:
        return input_id
    raise Ros2BridgeProjectionError(f"Input id does not have a final marker contract: {input_id}")


def _validate_transport_close(
    input_id: Ros2BridgeInputId,
    config: Ros2BridgeProjectionConfig,
    completed_inputs: set[Ros2BridgeFiniteInputId],
) -> None:
    if input_id in config.required_final_inputs and input_id not in completed_inputs:
        raise Ros2BridgeProjectionError(
            f"DORA input closed before required final marker: {input_id}"
        )


def _summary_json(summary: Ros2BridgeProjectionSummary) -> str:
    return (
        "{"
        f'"processed_inputs":{summary.processed_inputs},'
        f'"published_messages":{summary.published_messages},'
        f'"final_inputs":{summary.final_inputs},'
        f'"audio_frames":{summary.audio_frames},'
        f'"audio_final_markers":{summary.audio_final_markers},'
        f'"activity_events":{summary.activity_events},'
        f'"activity_final_markers":{summary.activity_final_markers},'
        f'"turn_events":{summary.turn_events},'
        f'"turn_final_markers":{summary.turn_final_markers},'
        f'"asr_controls":{summary.asr_controls},'
        f'"asr_control_final_markers":{summary.asr_control_final_markers},'
        f'"transcript_deltas":{summary.transcript_deltas},'
        f'"transcript_partials":{summary.transcript_partials},'
        f'"transcript_finals":{summary.transcript_finals},'
        f'"transcript_stream_finals":{summary.transcript_stream_finals},'
        f'"session_events":{summary.session_events},'
        f'"dialogue_events":{summary.dialogue_events},'
        f'"agent_text_deltas":{summary.agent_text_deltas},'
        f'"agent_turn_done":{summary.agent_turn_done},'
        f'"agent_approval_requests":{summary.agent_approval_requests},'
        f'"agent_tool_events":{summary.agent_tool_events},'
        f'"playback_commands":{summary.playback_commands},'
        f'"playback_states":{summary.playback_states},'
        f'"playback_done":{summary.playback_done}'
        "}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
