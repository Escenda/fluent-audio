import pytest
from pydantic import ValidationError

from fluent_audio.contracts import (
    AgentApprovalRequest,
    AgentApprovalResponse,
    AgentCancelRequest,
    AgentMcpElicitationRequest,
    AgentMcpElicitationResponse,
    AgentTextDelta,
    AgentToolEvent,
    AgentTurnDone,
    AgentTurnRequest,
    AgentUserInputAnswer,
    AgentUserInputQuestion,
    AgentUserInputRequest,
    AgentUserInputResponse,
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


def test_agent_approval_response_validates_decision_scope() -> None:
    response = AgentApprovalResponse(
        session_id="session-1",
        user_turn_id="user-turn-1",
        approval_id="approval-1",
        seq=6,
        decision="accept",
        scope="session",
        reason="trusted for this run",
    )

    assert response.scope == "session"

    with pytest.raises(ValidationError, match="scope=session is only valid for accept"):
        AgentApprovalResponse(
            session_id="session-1",
            user_turn_id="user-turn-1",
            approval_id="approval-1",
            seq=7,
            decision="decline",
            scope="session",
        )


def test_agent_user_input_models_validate_unique_questions_and_answers() -> None:
    request = AgentUserInputRequest(
        session_id="session-1",
        user_turn_id="user-turn-1",
        request_id="input-1",
        seq=7,
        questions=(
            AgentUserInputQuestion(
                id="q1",
                header="Confirm",
                question="Continue?",
            ),
        ),
    )
    response = AgentUserInputResponse(
        session_id="session-1",
        user_turn_id="user-turn-1",
        request_id="input-1",
        seq=8,
        answers=(AgentUserInputAnswer(question_id="q1", answers=("yes",)),),
    )

    assert request.questions[0].question == "Continue?"
    assert response.answers[0].answers == ("yes",)

    with pytest.raises(ValidationError, match="question ids must be unique"):
        AgentUserInputRequest(
            session_id="session-1",
            user_turn_id="user-turn-1",
            request_id="input-1",
            seq=9,
            questions=(
                AgentUserInputQuestion(id="q1", header="One", question="One?"),
                AgentUserInputQuestion(id="q1", header="Two", question="Two?"),
            ),
        )

    with pytest.raises(ValidationError, match="answer question ids must be unique"):
        AgentUserInputResponse(
            session_id="session-1",
            user_turn_id="user-turn-1",
            request_id="input-1",
            seq=10,
            answers=(
                AgentUserInputAnswer(question_id="q1", answers=("yes",)),
                AgentUserInputAnswer(question_id="q1", answers=("no",)),
            ),
        )


def test_agent_mcp_elicitation_models_validate_mode_payloads() -> None:
    url_request = AgentMcpElicitationRequest(
        session_id="session-1",
        user_turn_id="user-turn-1",
        request_id="mcp-1",
        seq=9,
        server_name="robot",
        mode="url",
        message="Open console?",
        url="https://example.invalid",
        elicitation_id="elicit-1",
    )
    form_request = AgentMcpElicitationRequest(
        session_id="session-1",
        user_turn_id="user-turn-1",
        request_id="mcp-2",
        seq=10,
        server_name="robot",
        mode="form",
        message="Approve?",
        requested_schema={"type": "object"},
    )
    decline_response = AgentMcpElicitationResponse(
        session_id="session-1",
        user_turn_id="user-turn-1",
        request_id="mcp-2",
        seq=11,
        action="decline",
    )

    assert url_request.url == "https://example.invalid"
    assert form_request.requested_schema == {"type": "object"}
    assert decline_response.content is None

    with pytest.raises(ValidationError, match="form mode requires requested_schema"):
        AgentMcpElicitationRequest(
            session_id="session-1",
            user_turn_id="user-turn-1",
            request_id="mcp-3",
            seq=12,
            server_name="robot",
            mode="form",
            message="Approve?",
        )

    with pytest.raises(ValidationError, match="decline/cancel responses must not carry content"):
        AgentMcpElicitationResponse(
            session_id="session-1",
            user_turn_id="user-turn-1",
            request_id="mcp-2",
            seq=13,
            action="cancel",
            content={"approved": False},
        )


def test_agent_turn_request_and_done_validate_terminal_variants() -> None:
    request = AgentTurnRequest(
        session_id="session-1",
        user_turn_id="user-turn-1",
        assistant_turn_id="assistant-turn-1",
        seq=0,
        text="hello",
    )
    completed = AgentTurnDone(
        session_id="session-1",
        user_turn_id="user-turn-1",
        agent_turn_id="assistant-turn-1",
        seq=1,
        status="completed",
    )
    cancelled = AgentTurnDone(
        session_id="session-1",
        user_turn_id="user-turn-1",
        agent_turn_id="assistant-turn-1",
        seq=2,
        status="cancelled",
        message="barge_in",
    )

    assert request.text == "hello"
    assert completed.message is None
    assert cancelled.message == "barge_in"


def test_agent_turn_done_failed_requires_message() -> None:
    with pytest.raises(ValidationError, match="failed requires message"):
        AgentTurnDone(
            session_id="session-1",
            user_turn_id="user-turn-1",
            agent_turn_id="assistant-turn-1",
            seq=0,
            status="failed",
        )


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
