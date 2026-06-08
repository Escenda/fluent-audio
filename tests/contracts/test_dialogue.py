import pytest
from pydantic import ValidationError

from fluent_audio.contracts import (
    AgentApprovalRequest,
    AgentCancelRequest,
    AgentTextDelta,
    AgentToolEvent,
    DialogueEvent,
    DialogueInput,
)


def test_dialogue_input_validates_transcript_and_playback_variants() -> None:
    transcript = DialogueInput(
        input_type="transcript_final",
        session_id="session-1",
        user_turn_id="user-turn-1",
        seq=0,
        text="turn text",
    )
    playback = DialogueInput(
        input_type="playback_done",
        session_id="session-1",
        user_turn_id="user-turn-1",
        seq=1,
        request_id="playback-1",
    )

    assert transcript.text == "turn text"
    assert playback.request_id == "playback-1"


def test_dialogue_input_rejects_missing_variant_payload() -> None:
    with pytest.raises(ValidationError, match="requires text"):
        DialogueInput(
            input_type="transcript_final",
            session_id="session-1",
            user_turn_id="user-turn-1",
            seq=0,
        )


def test_dialogue_event_validates_text_and_error_payloads() -> None:
    text_event = DialogueEvent(
        event="tts_text",
        session_id="session-1",
        user_turn_id="user-turn-1",
        seq=2,
        text="hello",
    )
    error_event = DialogueEvent(
        event="error",
        session_id="session-1",
        user_turn_id="user-turn-1",
        seq=3,
        message="agent unavailable",
    )

    assert text_event.text == "hello"
    assert error_event.message == "agent unavailable"


def test_agent_event_models_validate_required_fields() -> None:
    delta = AgentTextDelta(
        session_id="session-1",
        user_turn_id="user-turn-1",
        agent_turn_id="agent-turn-1",
        seq=4,
        text="agent says",
    )
    approval = AgentApprovalRequest(
        session_id="session-1",
        user_turn_id="user-turn-1",
        approval_id="approval-1",
        seq=5,
        prompt="Allow robot motion?",
        action_label="move_arm",
    )
    cancel = AgentCancelRequest(
        session_id="session-1",
        user_turn_id="user-turn-1",
        seq=6,
    )

    assert delta.text == "agent says"
    assert approval.action_label == "move_arm"
    assert cancel.reason is None


def test_agent_tool_failed_event_requires_error_message() -> None:
    with pytest.raises(ValidationError, match="requires error_message"):
        AgentToolEvent(
            session_id="session-1",
            user_turn_id="user-turn-1",
            tool_call_id="tool-1",
            tool_name="robot.move",
            event="failed",
            seq=7,
        )

    event = AgentToolEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        tool_call_id="tool-1",
        tool_name="robot.move",
        event="completed",
        seq=8,
        summary="done",
    )
    assert event.summary == "done"
