import pytest

from fluent_dialogue_dora.contracts import (
    AgentApprovalRequest,
    AgentCancelRequest,
    AgentTextDelta,
    AgentToolEvent,
    AgentTurnDone,
    AsrCancel,
    AsrStart,
    AsrStop,
    AudioChunk,
    AudioFormat,
    DialogueEvent,
    PlaybackStop,
    PlaybackDone,
    PlaybackState,
    TranscriptDelta,
    TranscriptFinal,
    TranscriptPartial,
    TurnEvent,
    TurnIds,
    VoiceActivityEvent,
    VoiceSessionEvent,
)
from bridges.ros2_bridge.messages import (
    Ros2AgentCancelRequest,
    Ros2AudioFrame,
    Ros2BridgeMessageError,
    Ros2Transcript,
    agent_approval_request_to_ros2,
    agent_cancel_request_to_ros2,
    agent_text_delta_to_ros2,
    agent_tool_event_to_ros2,
    agent_turn_done_to_ros2,
    asr_control_to_ros2,
    audio_chunk_to_ros2,
    audio_final_marker_to_ros2,
    dialogue_event_to_ros2,
    playback_done_to_ros2,
    playback_command_to_ros2,
    playback_state_to_ros2,
    ros2_agent_cancel_request_to_contract,
    ros2_asr_control_to_contract,
    ros2_audio_to_chunk,
    ros2_playback_command_to_contract,
    ros2_transcript_to_contract,
    ros2_turn_to_event,
    ros2_voice_activity_to_event,
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


def test_audio_chunk_roundtrips_through_ros2_projection() -> None:
    chunk = AudioChunk(
        source_id="mic",
        stream_id="audio/asr/input",
        seq=7,
        sample_index=1600,
        capture_time_ns=123_456_789_000,
        frame_count=4,
        format=AudioFormat(sample_rate_hz=16_000, channels=1, sample_format="s16le"),
        payload=b"\x01\x00\x02\x00\x03\x00\x04\x00",
    )

    projected = audio_chunk_to_ros2(chunk)
    restored = ros2_audio_to_chunk(projected)

    assert projected.header.stamp.to_unix_ns() == chunk.capture_time_ns
    assert projected.encoding == "PCM16LE"
    assert projected.bit_depth == 16
    assert projected.final is False
    assert restored == chunk


def test_audio_final_marker_is_not_decoded_as_audio_chunk() -> None:
    final = audio_final_marker_to_ros2(
        source_id="mic",
        stream_id="audio/asr/input",
        seq=8,
        sample_index=2048,
        capture_time_ns=128_000_000,
        audio_format=AudioFormat(sample_rate_hz=16_000, channels=1, sample_format="s16le"),
    )

    assert final.final is True
    assert final.data == b""
    with pytest.raises(Ros2BridgeMessageError, match="final marker"):
        ros2_audio_to_chunk(final)


def test_audio_projection_rejects_size_mismatch() -> None:
    with pytest.raises(ValueError, match="data size mismatch"):
        Ros2AudioFrame(
            header=audio_final_marker_to_ros2(
                source_id="mic",
                stream_id="audio/main",
                seq=0,
                sample_index=0,
                capture_time_ns=0,
                audio_format=AudioFormat(sample_rate_hz=16_000, channels=1),
            ).header,
            source_id="mic",
            stream_id="audio/main",
            seq=0,
            sample_index=0,
            capture_time_ns=0,
            frame_count=2,
            encoding="PCM16LE",
            sample_rate_hz=16_000,
            channels=1,
            bit_depth=16,
            layout="interleaved",
            data=b"\x00\x00",
            final=False,
        )


def test_voice_activity_roundtrips_through_ros2_projection() -> None:
    event = VoiceActivityEvent(
        source_id="vad",
        stream_id="activity/main",
        seq=3,
        sample_index=1024,
        frame_count=512,
        state="speech",
        speech_probability=0.75,
    )

    projected = voice_activity_to_ros2(event, timestamp_ns=10)

    assert projected.state == "speech"
    assert ros2_voice_activity_to_event(projected) == event


def test_voice_activity_final_marker_is_not_decoded_as_activity_event() -> None:
    projected = voice_activity_final_marker_to_ros2(
        source_id="vad",
        stream_id="activity/main",
        seq=4,
        sample_index=1536,
        timestamp_ns=11,
    )

    assert projected.final is True
    assert projected.frame_count == 0
    with pytest.raises(Ros2BridgeMessageError, match="final marker"):
        ros2_voice_activity_to_event(projected)


def test_turn_event_roundtrips_with_string_user_turn_id() -> None:
    event = TurnEvent(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        stream_id="turn/main",
        seq=4,
        sample_index=8192,
        state="ended",
        confidence=0.9,
    )

    projected = turn_event_to_ros2(event, timestamp_ns=20)

    assert projected.user_turn_id == "user-turn-000001"
    assert projected.confidence_present is True
    assert ros2_turn_to_event(projected) == event


def test_turn_final_marker_is_not_decoded_as_turn_event() -> None:
    projected = turn_final_marker_to_ros2(
        session_id="session-1",
        stream_id="turn/main",
        seq=5,
        sample_index=8192,
        timestamp_ns=21,
    )

    assert projected.final is True
    assert projected.user_turn_id == ""
    with pytest.raises(Ros2BridgeMessageError, match="final marker"):
        ros2_turn_to_event(projected)


def test_asr_control_roundtrips_all_variants() -> None:
    controls = [
        AsrStart(
            action="start",
            session_id="session-1",
            user_turn_id="user-turn-000001",
            stream_id="audio/asr/input",
            seq=0,
            start_sample_index=512,
        ),
        AsrStop(
            action="stop",
            session_id="session-1",
            user_turn_id="user-turn-000001",
            stream_id="audio/asr/input",
            seq=1,
            stop_sample_index=8192,
        ),
        AsrCancel(
            action="cancel",
            session_id="session-1",
            user_turn_id="user-turn-000001",
            stream_id="audio/asr/input",
            seq=2,
            reason="barge_in",
        ),
    ]

    for control in controls:
        projected = asr_control_to_ros2(control, timestamp_ns=30)
        restored = ros2_asr_control_to_contract(projected)
        assert restored == control


def test_transcript_projection_preserves_delta_final_and_stream_final() -> None:
    delta = TranscriptDelta(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        stream_id="transcript/main",
        seq=0,
        text="hello",
    )
    final = TranscriptFinal(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        stream_id="transcript/main",
        seq=1,
        text="hello world",
        start_sample_index=512,
        end_sample_index=8192,
    )
    partial = TranscriptPartial(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        stream_id="transcript/main",
        seq=2,
        text="hello wor",
    )

    projected_delta = transcript_delta_to_ros2(delta, timestamp_ns=40)
    projected_final = transcript_final_to_ros2(final, timestamp_ns=41)
    projected_partial = transcript_partial_to_ros2(partial, timestamp_ns=42)
    projected_stream_final = transcript_stream_final_to_ros2(
        session_id="session-1",
        stream_id="transcript/main",
        seq=3,
        sample_index=8192,
        timestamp_ns=43,
    )

    assert ros2_transcript_to_contract(projected_delta) == delta
    assert ros2_transcript_to_contract(projected_partial) == partial
    assert ros2_transcript_to_contract(projected_final) == final
    assert projected_stream_final.kind == "stream_final"
    with pytest.raises(Ros2BridgeMessageError, match="stream_final"):
        ros2_transcript_to_contract(projected_stream_final)


def test_transcript_projection_rejects_final_with_empty_text() -> None:
    with pytest.raises(ValueError, match="requires text"):
        Ros2Transcript(
            header=transcript_stream_final_to_ros2(
                session_id="session-1",
                stream_id="transcript/main",
                seq=2,
                sample_index=8192,
                timestamp_ns=42,
            ).header,
            kind="final",
            session_id="session-1",
            user_turn_id="user-turn-000001",
            stream_id="transcript/main",
            seq=0,
            text="",
            start_sample_index=0,
            end_sample_index=8192,
        )


def test_session_dialogue_agent_and_playback_projections() -> None:
    timestamp_ns = 50
    session = VoiceSessionEvent(
        event="state_changed",
        state="thinking",
        seq=3,
        turn_ids=TurnIds(
            session_id="session-1",
            user_turn_id="user-turn-000001",
            assistant_turn_id="assistant-turn-000001",
        ),
    )
    dialogue = DialogueEvent(
        event="tts_text",
        session_id="session-1",
        user_turn_id="user-turn-000001",
        seq=4,
        text="どうぞ",
    )
    text_delta = AgentTextDelta(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        agent_turn_id="agent-turn-000001",
        seq=5,
        text="result",
    )
    turn_done = AgentTurnDone(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        agent_turn_id="agent-turn-000001",
        seq=6,
        status="completed",
    )
    approval = AgentApprovalRequest(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        approval_id="approval-1",
        seq=7,
        prompt="Move arm?",
        action_label="move_arm",
    )
    tool = AgentToolEvent(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        tool_call_id="tool-1",
        tool_name="robot.move",
        event="completed",
        seq=8,
        summary="done",
    )
    playback_state = PlaybackState(
        request_id="tts-1",
        session_id="session-1",
        user_turn_id="user-turn-000001",
        stream_id="audio/playback",
        state="playing",
        seq=9,
        played_frames=1024,
    )
    playback_command = PlaybackStop(
        command="stop",
        request_id="tts-1",
        stream_id="audio/playback",
        seq=10,
    )
    playback_done = PlaybackDone(
        request_id="tts-1",
        session_id="session-1",
        user_turn_id="user-turn-000001",
        stream_id="audio/playback",
        status="completed",
        total_frames=2048,
    )

    assert voice_session_event_to_ros2(session, timestamp_ns=timestamp_ns).assistant_turn_id
    assert dialogue_event_to_ros2(dialogue, timestamp_ns=timestamp_ns).text == "どうぞ"
    assert agent_text_delta_to_ros2(text_delta, timestamp_ns=timestamp_ns).text == "result"
    assert agent_turn_done_to_ros2(turn_done, timestamp_ns=timestamp_ns).status == "completed"
    assert (
        agent_approval_request_to_ros2(approval, timestamp_ns=timestamp_ns).action_label
        == "move_arm"
    )
    assert agent_tool_event_to_ros2(tool, timestamp_ns=timestamp_ns).summary == "done"
    assert playback_state_to_ros2(playback_state, timestamp_ns=timestamp_ns).state == "playing"
    projected_command = playback_command_to_ros2(playback_command, timestamp_ns=timestamp_ns)
    assert ros2_playback_command_to_contract(projected_command) == playback_command
    projected_done = playback_done_to_ros2(playback_done, timestamp_ns=timestamp_ns)
    assert projected_done.total_frames_present is True
    assert projected_done.total_frames == 2048


def test_agent_cancel_request_roundtrips_through_ros2_projection() -> None:
    cancel = AgentCancelRequest(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        seq=12,
        reason="voice_cancel",
    )

    projected = agent_cancel_request_to_ros2(cancel, timestamp_ns=61)

    assert projected.reason_present is True
    assert ros2_agent_cancel_request_to_contract(projected) == cancel


def test_agent_cancel_request_rejects_reason_presence_mismatch() -> None:
    cancel = AgentCancelRequest(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        seq=12,
    )
    projected = agent_cancel_request_to_ros2(cancel, timestamp_ns=61)

    payload = projected.model_dump()
    with pytest.raises(ValueError, match="reason is required"):
        Ros2AgentCancelRequest.model_validate(payload | {"reason_present": True})
    with pytest.raises(ValueError, match="reason must be empty"):
        Ros2AgentCancelRequest.model_validate(payload | {"reason": "voice_cancel"})
