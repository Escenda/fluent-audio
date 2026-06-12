from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

import pytest

from fluent_audio.contracts import (
    AgentApprovalRequest,
    AgentTextDelta,
    AgentToolEvent,
    AgentTurnDone,
    AsrStart,
    AudioChunk,
    AudioFormat,
    DialogueEvent,
    PlaybackDone,
    PlaybackState,
    PlaybackStop,
    TranscriptDelta,
    TranscriptFinal,
    TranscriptPartial,
    TurnEvent,
    TurnIds,
    VoiceActivityEvent,
    VoiceSessionEvent,
)
from fluent_audio.dora import (
    DoraMetadataMapping,
    encode_agent_approval_request_for_dora,
    encode_agent_text_delta_for_dora,
    encode_agent_tool_event_for_dora,
    encode_agent_turn_done_for_dora,
    encode_asr_control_final_marker_for_dora,
    encode_asr_control_for_dora,
    encode_audio_chunk_for_dora,
    encode_audio_final_marker_for_dora,
    encode_dialogue_event_for_dora,
    encode_playback_command_for_dora,
    encode_playback_done_for_dora,
    encode_playback_state_for_dora,
    encode_transcript_delta_for_dora,
    encode_transcript_final_for_dora,
    encode_transcript_partial_for_dora,
    encode_transcript_stream_final_marker_for_dora,
    encode_turn_event_for_dora,
    encode_turn_final_marker_for_dora,
    encode_voice_activity_event_for_dora,
    encode_voice_activity_final_marker_for_dora,
    encode_voice_session_event_for_dora,
)
from bridges.ros2_bridge.main import (
    Ros2BridgePayloadInput,
    JsonlRos2BridgeProjectionPublisher,
    Ros2BridgeProjectionConfig,
    Ros2BridgeProjectionError,
    Ros2BridgeJsonlRecord,
    Ros2BridgeProjectionSummary,
    Ros2BridgeRawEvent,
    run_ros2_bridge_projection_events,
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
)

PublishedRos2Message = (
    Ros2AudioFrame
    | Ros2VoiceActivity
    | Ros2TurnEvent
    | Ros2AsrControl
    | Ros2Transcript
    | Ros2VoiceSessionEvent
    | Ros2DialogueEvent
    | Ros2AgentTextDelta
    | Ros2AgentTurnDone
    | Ros2AgentApprovalRequest
    | Ros2AgentToolEvent
    | Ros2PlaybackCommand
    | Ros2PlaybackState
    | Ros2PlaybackDone
)


class DoraMetadataEncoder(Protocol):
    def to_dora_metadata(self) -> DoraMetadataMapping: ...


class FakeDoraNode:
    def __init__(self, events: tuple[Ros2BridgeRawEvent, ...]) -> None:
        self._events = events

    def __iter__(self) -> Iterator[Ros2BridgeRawEvent]:
        return iter(self._events)


class FixedClock:
    def __init__(self) -> None:
        self._time_ns = 1_000

    def time_ns(self) -> int:
        self._time_ns += 1
        return self._time_ns


class CapturingRos2Publisher:
    def __init__(self) -> None:
        self.messages: list[PublishedRos2Message] = []

    def publish_audio_frame(self, message: Ros2AudioFrame) -> None:
        self.messages.append(message)

    def publish_voice_activity(self, message: Ros2VoiceActivity) -> None:
        self.messages.append(message)

    def publish_turn_event(self, message: Ros2TurnEvent) -> None:
        self.messages.append(message)

    def publish_asr_control(self, message: Ros2AsrControl) -> None:
        self.messages.append(message)

    def publish_transcript(self, message: Ros2Transcript) -> None:
        self.messages.append(message)

    def publish_voice_session_event(self, message: Ros2VoiceSessionEvent) -> None:
        self.messages.append(message)

    def publish_dialogue_event(self, message: Ros2DialogueEvent) -> None:
        self.messages.append(message)

    def publish_agent_text_delta(self, message: Ros2AgentTextDelta) -> None:
        self.messages.append(message)

    def publish_agent_turn_done(self, message: Ros2AgentTurnDone) -> None:
        self.messages.append(message)

    def publish_agent_approval_request(self, message: Ros2AgentApprovalRequest) -> None:
        self.messages.append(message)

    def publish_agent_tool_event(self, message: Ros2AgentToolEvent) -> None:
        self.messages.append(message)

    def publish_playback_command(self, message: Ros2PlaybackCommand) -> None:
        self.messages.append(message)

    def publish_playback_state(self, message: Ros2PlaybackState) -> None:
        self.messages.append(message)

    def publish_playback_done(self, message: Ros2PlaybackDone) -> None:
        self.messages.append(message)


def _input_event(
    input_id: str,
    payload: Ros2BridgePayloadInput,
    metadata: DoraMetadataMapping,
) -> Ros2BridgeRawEvent:
    return {
        "type": "INPUT",
        "id": input_id,
        "value": payload,
        "metadata": metadata,
    }


def _input_closed(input_id: str) -> Ros2BridgeRawEvent:
    return {
        "type": "INPUT_CLOSED",
        "id": input_id,
    }


def _encoded_input(
    input_id: str,
    encoded: tuple[Ros2BridgePayloadInput, DoraMetadataEncoder],
) -> Ros2BridgeRawEvent:
    payload, metadata = encoded
    return _input_event(input_id, payload, metadata.to_dora_metadata())


def _audio_format() -> AudioFormat:
    return AudioFormat(sample_rate_hz=16_000, channels=1, sample_format="s16le")


def test_ros2_bridge_projects_dora_contracts_to_typed_ros2_messages() -> None:
    publisher = CapturingRos2Publisher()
    audio_format = _audio_format()

    summary = run_ros2_bridge_projection_events(
        FakeDoraNode(
            (
                _encoded_input(
                    "audio",
                    encode_audio_chunk_for_dora(
                        AudioChunk(
                            source_id="mic",
                            stream_id="audio/main",
                            seq=0,
                            sample_index=0,
                            capture_time_ns=100,
                            frame_count=2,
                            format=audio_format,
                            payload=b"\x01\x00\x02\x00",
                        )
                    ),
                ),
                _encoded_input(
                    "activity",
                    encode_voice_activity_event_for_dora(
                        VoiceActivityEvent(
                            source_id="vad",
                            stream_id="activity/main",
                            seq=0,
                            sample_index=0,
                            frame_count=2,
                            state="speech",
                            speech_probability=0.8,
                        )
                    ),
                ),
                _encoded_input(
                    "turn",
                    encode_turn_event_for_dora(
                        TurnEvent(
                            session_id="session-1",
                            user_turn_id="turn-1",
                            stream_id="turn/main",
                            seq=0,
                            sample_index=0,
                            state="started",
                            confidence=0.9,
                        )
                    ),
                ),
                _encoded_input(
                    "asr_control",
                    encode_asr_control_for_dora(
                        AsrStart(
                            action="start",
                            session_id="session-1",
                            user_turn_id="turn-1",
                            stream_id="audio/main",
                            seq=0,
                            start_sample_index=0,
                        )
                    ),
                ),
                _encoded_input(
                    "transcript",
                    encode_transcript_delta_for_dora(
                        TranscriptDelta(
                            session_id="session-1",
                            user_turn_id="turn-1",
                            stream_id="transcript/main",
                            seq=0,
                            text="hello",
                        )
                    ),
                ),
                _encoded_input(
                    "transcript",
                    encode_transcript_final_for_dora(
                        TranscriptFinal(
                            session_id="session-1",
                            user_turn_id="turn-1",
                            stream_id="transcript/main",
                            seq=1,
                            text="hello world",
                            start_sample_index=0,
                            end_sample_index=3200,
                        )
                    ),
                ),
                _encoded_input(
                    "transcript",
                    encode_transcript_partial_for_dora(
                        TranscriptPartial(
                            session_id="session-1",
                            user_turn_id="turn-1",
                            stream_id="transcript/main",
                            seq=2,
                            text="hello wor",
                        )
                    ),
                ),
                _encoded_input(
                    "session",
                    encode_voice_session_event_for_dora(
                        VoiceSessionEvent(
                            event="state_changed",
                            state="thinking",
                            seq=0,
                            turn_ids=TurnIds(
                                session_id="session-1",
                                user_turn_id="turn-1",
                                assistant_turn_id="assistant-turn-1",
                            ),
                        )
                    ),
                ),
                _encoded_input(
                    "dialogue",
                    encode_dialogue_event_for_dora(
                        DialogueEvent(
                            event="tts_text",
                            session_id="session-1",
                            user_turn_id="turn-1",
                            seq=0,
                            text="speak",
                        )
                    ),
                ),
                _encoded_input(
                    "agent_text",
                    encode_agent_text_delta_for_dora(
                        AgentTextDelta(
                            session_id="session-1",
                            user_turn_id="turn-1",
                            agent_turn_id="agent-turn-1",
                            seq=0,
                            text="answer",
                        )
                    ),
                ),
                _encoded_input(
                    "agent_done",
                    encode_agent_turn_done_for_dora(
                        AgentTurnDone(
                            session_id="session-1",
                            user_turn_id="turn-1",
                            agent_turn_id="agent-turn-1",
                            seq=0,
                            status="completed",
                        )
                    ),
                ),
                _encoded_input(
                    "agent_approval",
                    encode_agent_approval_request_for_dora(
                        AgentApprovalRequest(
                            session_id="session-1",
                            user_turn_id="turn-1",
                            approval_id="approval-1",
                            seq=0,
                            prompt="Proceed?",
                            action_label="robot_action",
                        )
                    ),
                ),
                _encoded_input(
                    "agent_tool",
                    encode_agent_tool_event_for_dora(
                        AgentToolEvent(
                            session_id="session-1",
                            user_turn_id="turn-1",
                            tool_call_id="tool-1",
                            tool_name="robot.inspect",
                            event="completed",
                            seq=0,
                            summary="done",
                        )
                    ),
                ),
                _encoded_input(
                    "playback_command",
                    encode_playback_command_for_dora(
                        PlaybackStop(
                            command="stop",
                            request_id="tts-1",
                            stream_id="audio/playback",
                            seq=0,
                        )
                    ),
                ),
                _encoded_input(
                    "playback_state",
                    encode_playback_state_for_dora(
                        PlaybackState(
                            request_id="tts-1",
                            session_id="session-1",
                            user_turn_id="user-turn-1",
                            stream_id="audio/playback",
                            state="playing",
                            seq=1,
                            played_frames=512,
                        )
                    ),
                ),
                _encoded_input(
                    "playback_done",
                    encode_playback_done_for_dora(
                        PlaybackDone(
                            request_id="tts-1",
                            session_id="session-1",
                            user_turn_id="user-turn-1",
                            stream_id="audio/playback",
                            status="completed",
                            total_frames=1024,
                        )
                    ),
                ),
                _encoded_input(
                    "audio",
                    encode_audio_final_marker_for_dora(
                        source_id="mic",
                        stream_id="audio/main",
                        seq=1,
                        sample_index=2,
                        capture_time_ns=200,
                        audio_format=audio_format,
                    ),
                ),
                _encoded_input(
                    "activity",
                    encode_voice_activity_final_marker_for_dora(
                        source_id="vad",
                        stream_id="activity/main",
                        seq=1,
                        sample_index=2,
                    ),
                ),
                _encoded_input(
                    "turn",
                    encode_turn_final_marker_for_dora(
                        "session-1",
                        "turn/main",
                        1,
                        2,
                    ),
                ),
                _encoded_input(
                    "asr_control",
                    encode_asr_control_final_marker_for_dora(
                        session_id="session-1",
                        stream_id="audio/main",
                        seq=1,
                    ),
                ),
                _encoded_input(
                    "transcript",
                    encode_transcript_stream_final_marker_for_dora(
                        session_id="session-1",
                        stream_id="transcript/main",
                        seq=3,
                        sample_index=3200,
                    ),
                ),
            )
        ),
        Ros2BridgeProjectionConfig(
            required_final_inputs=("audio", "activity", "turn", "asr_control", "transcript")
        ),
        publisher,
        FixedClock(),
    )

    assert summary == Ros2BridgeProjectionSummary(
        processed_inputs=21,
        published_messages=20,
        final_inputs=5,
        audio_frames=1,
        audio_final_markers=1,
        activity_events=1,
        activity_final_markers=1,
        turn_events=1,
        turn_final_markers=1,
        asr_controls=1,
        asr_control_final_markers=1,
        transcript_deltas=1,
        transcript_partials=1,
        transcript_finals=1,
        transcript_stream_finals=1,
        session_events=1,
        dialogue_events=1,
        agent_text_deltas=1,
        agent_turn_done=1,
        agent_approval_requests=1,
        agent_tool_events=1,
        playback_commands=1,
        playback_states=1,
        playback_done=1,
    )
    assert len(publisher.messages) == 20
    assert isinstance(publisher.messages[0], Ros2AudioFrame)
    assert isinstance(publisher.messages[3], Ros2AsrControl)
    assert isinstance(publisher.messages[-1], Ros2Transcript)
    assert publisher.messages[-1].kind == "stream_final"


def test_ros2_bridge_rejects_transport_close_before_required_final_marker() -> None:
    with pytest.raises(Ros2BridgeProjectionError, match="closed before required final marker"):
        run_ros2_bridge_projection_events(
            FakeDoraNode((_input_closed("audio"),)),
            Ros2BridgeProjectionConfig(required_final_inputs=("audio",)),
            CapturingRos2Publisher(),
            FixedClock(),
        )


def test_ros2_bridge_rejects_missing_required_final_marker_at_stream_end() -> None:
    audio_format = _audio_format()

    with pytest.raises(Ros2BridgeProjectionError, match="ended before required final markers"):
        run_ros2_bridge_projection_events(
            FakeDoraNode(
                (
                    _encoded_input(
                        "audio",
                        encode_audio_chunk_for_dora(
                            AudioChunk(
                                source_id="mic",
                                stream_id="audio/main",
                                seq=0,
                                sample_index=0,
                                capture_time_ns=100,
                                frame_count=2,
                                format=audio_format,
                                payload=b"\x01\x00\x02\x00",
                            )
                        ),
                    ),
                )
            ),
            Ros2BridgeProjectionConfig(required_final_inputs=("audio",)),
            CapturingRos2Publisher(),
            FixedClock(),
        )


def test_ros2_bridge_jsonl_publisher_supports_dora_stop(tmp_path: Path) -> None:
    output_path = tmp_path / "ros2_projection.jsonl"
    publisher = JsonlRos2BridgeProjectionPublisher(output_path)
    audio_format = _audio_format()
    try:
        summary = run_ros2_bridge_projection_events(
            FakeDoraNode(
                (
                    _encoded_input(
                        "audio",
                        encode_audio_chunk_for_dora(
                            AudioChunk(
                                source_id="mic",
                                stream_id="audio/main",
                                seq=0,
                                sample_index=0,
                                capture_time_ns=100,
                                frame_count=2,
                                format=audio_format,
                                payload=b"\x01\x00\x02\x00",
                            )
                        ),
                    ),
                    _encoded_input(
                        "audio",
                        encode_audio_final_marker_for_dora(
                            source_id="mic",
                            stream_id="audio/main",
                            seq=1,
                            sample_index=2,
                            capture_time_ns=200,
                            audio_format=audio_format,
                        ),
                    ),
                    {"type": "STOP"},
                )
            ),
            Ros2BridgeProjectionConfig(required_final_inputs=("audio",)),
            publisher,
            FixedClock(),
        )
    finally:
        publisher.close()

    records = [
        Ros2BridgeJsonlRecord.model_validate_json(line)
        for line in output_path.read_text(encoding="utf-8").splitlines()
    ]
    assert summary.audio_frames == 1
    assert summary.audio_final_markers == 1
    assert summary.final_inputs == 1
    assert [record.topic for record in records] == ["audio", "audio"]
    assert [record.message_type for record in records] == ["Ros2AudioFrame", "Ros2AudioFrame"]
