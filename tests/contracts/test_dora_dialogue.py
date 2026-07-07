import pyarrow as pa
import pytest

from fluent_dialogue_dora.contracts import (
    AgentApprovalRequest,
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
from fluent_dialogue_dora.dora import (
    DoraDialogueMetadataError,
    decode_agent_approval_request_from_dora,
    decode_agent_cancel_request_from_dora,
    decode_agent_mcp_elicitation_request_from_dora,
    decode_agent_mcp_elicitation_response_from_dora,
    decode_agent_runtime_event_from_dora,
    decode_agent_text_delta_from_dora,
    decode_agent_tool_event_from_dora,
    decode_agent_turn_done_from_dora,
    decode_agent_turn_request_from_dora,
    decode_agent_user_input_request_from_dora,
    decode_agent_user_input_response_from_dora,
    decode_dialogue_event_from_dora,
    decode_dialogue_input_from_dora,
    encode_agent_approval_request_for_dora,
    encode_agent_cancel_request_for_dora,
    encode_agent_mcp_elicitation_request_for_dora,
    encode_agent_mcp_elicitation_response_for_dora,
    encode_agent_runtime_event_for_dora,
    encode_agent_text_delta_for_dora,
    encode_agent_tool_event_for_dora,
    encode_agent_turn_done_for_dora,
    encode_agent_turn_request_for_dora,
    encode_agent_user_input_request_for_dora,
    encode_agent_user_input_response_for_dora,
    encode_dialogue_event_for_dora,
    encode_dialogue_input_for_dora,
)


def test_dialogue_input_roundtrips_transcript_final() -> None:
    event = DialogueInput(
        input_type="transcript_final",
        session_id="session-1",
        user_turn_id="user-turn-000001",
        seq=0,
        text="hello",
    )

    payload, metadata = encode_dialogue_input_for_dora(event)
    decoded = decode_dialogue_input_from_dora(payload, metadata.to_dora_metadata())

    assert decoded == event


def test_dialogue_input_roundtrips_playback_done() -> None:
    event = DialogueInput(
        input_type="playback_done",
        session_id="session-1",
        user_turn_id="user-turn-000001",
        seq=1,
        request_id="tts-1",
    )

    payload, metadata = encode_dialogue_input_for_dora(event)
    decoded = decode_dialogue_input_from_dora(payload, metadata.to_dora_metadata())

    assert decoded == event


def test_dialogue_input_rejects_invalid_payload() -> None:
    event = DialogueInput(
        input_type="playback_done",
        session_id="session-1",
        user_turn_id="user-turn-000001",
        seq=1,
        request_id="tts-1",
    )
    _, metadata = encode_dialogue_input_for_dora(event)

    with pytest.raises(DoraDialogueMetadataError, match="protobuf did not validate"):
        decode_dialogue_input_from_dora(
            pa.array(list(b"unexpected"), type=pa.uint8()),
            metadata.to_dora_metadata(),
        )


def test_dialogue_event_roundtrips_text_and_message_payloads() -> None:
    tts_event = DialogueEvent(
        event="tts_text",
        session_id="session-1",
        user_turn_id="user-turn-000001",
        seq=2,
        text="どうぞ",
        request_id="tts-1",
    )
    error_event = DialogueEvent(
        event="error",
        session_id="session-1",
        user_turn_id="user-turn-000001",
        seq=3,
        message="agent failed",
    )

    tts_payload, tts_metadata = encode_dialogue_event_for_dora(tts_event)
    error_payload, error_metadata = encode_dialogue_event_for_dora(error_event)

    assert decode_dialogue_event_from_dora(tts_payload, tts_metadata.to_dora_metadata()) == tts_event
    assert (
        decode_dialogue_event_from_dora(error_payload, error_metadata.to_dora_metadata())
        == error_event
    )


def test_dialogue_event_rejects_invalid_payload() -> None:
    event = DialogueEvent(
        event="cancelled",
        session_id="session-1",
        user_turn_id="user-turn-000001",
        seq=3,
    )
    _, metadata = encode_dialogue_event_for_dora(event)

    with pytest.raises(DoraDialogueMetadataError, match="protobuf did not validate"):
        decode_dialogue_event_from_dora(
            pa.array(list(b"unexpected"), type=pa.uint8()),
            metadata.to_dora_metadata(),
        )


def test_agent_text_and_approval_roundtrip_through_dora() -> None:
    text_delta = AgentTextDelta(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        agent_turn_id="agent-turn-000001",
        seq=4,
        text="answer",
    )
    approval = AgentApprovalRequest(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        approval_id="approval-1",
        seq=5,
        prompt="Move arm?",
        action_label="move_arm",
    )

    text_payload, text_metadata = encode_agent_text_delta_for_dora(text_delta)
    approval_payload, approval_metadata = encode_agent_approval_request_for_dora(approval)

    assert (
        decode_agent_text_delta_from_dora(text_payload, text_metadata.to_dora_metadata())
        == text_delta
    )
    assert (
        decode_agent_approval_request_from_dora(
            approval_payload,
            approval_metadata.to_dora_metadata(),
        )
        == approval
    )


def test_agent_runtime_event_roundtrips_ordered_agent_variants() -> None:
    events = (
        AgentTextDelta(
            session_id="session-1",
            user_turn_id="user-turn-000001",
            agent_turn_id="agent-turn-000001",
            seq=0,
            text="answer",
        ),
        AgentApprovalRequest(
            session_id="session-1",
            user_turn_id="user-turn-000001",
            approval_id="approval-1",
            seq=1,
            prompt="Move arm?",
            action_label="move_arm",
        ),
        AgentUserInputRequest(
            session_id="session-1",
            user_turn_id="user-turn-000001",
            request_id="input-1",
            seq=2,
            questions=(AgentUserInputQuestion(id="q1", header="Confirm", question="Continue?"),),
        ),
        AgentMcpElicitationRequest(
            session_id="session-1",
            user_turn_id="user-turn-000001",
            request_id="mcp-1",
            seq=3,
            server_name="robot",
            mode="url",
            message="Open console?",
            url="https://example.invalid",
            elicitation_id="elicit-1",
        ),
        AgentToolEvent(
            session_id="session-1",
            user_turn_id="user-turn-000001",
            tool_call_id="tool-1",
            tool_name="robot.move",
            event="started",
            seq=4,
        ),
        AgentTurnDone(
            session_id="session-1",
            user_turn_id="user-turn-000001",
            agent_turn_id="agent-turn-000001",
            seq=5,
            status="completed",
        ),
    )

    for event in events:
        payload, metadata = encode_agent_runtime_event_for_dora(event)
        assert decode_agent_runtime_event_from_dora(payload, metadata.to_dora_metadata()) == event


def test_agent_user_input_and_mcp_elicitation_split_roundtrip_through_dora() -> None:
    user_input_request = AgentUserInputRequest(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        request_id="input-1",
        seq=6,
        questions=(AgentUserInputQuestion(id="q1", header="Confirm", question="Continue?"),),
    )
    user_input_response = AgentUserInputResponse(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        request_id="input-1",
        seq=7,
        answers=(AgentUserInputAnswer(question_id="q1", answers=("yes",)),),
    )
    mcp_request = AgentMcpElicitationRequest(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        request_id="mcp-1",
        seq=8,
        server_name="robot",
        mode="form",
        message="Approve?",
        requested_schema={"type": "object"},
    )
    mcp_response = AgentMcpElicitationResponse(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        request_id="mcp-1",
        seq=9,
        action="accept",
        content={"approved": True},
    )

    input_request_payload, input_request_metadata = encode_agent_user_input_request_for_dora(
        user_input_request
    )
    input_response_payload, input_response_metadata = encode_agent_user_input_response_for_dora(
        user_input_response
    )
    mcp_request_payload, mcp_request_metadata = encode_agent_mcp_elicitation_request_for_dora(
        mcp_request
    )
    mcp_response_payload, mcp_response_metadata = encode_agent_mcp_elicitation_response_for_dora(
        mcp_response
    )

    assert (
        decode_agent_user_input_request_from_dora(
            input_request_payload,
            input_request_metadata.to_dora_metadata(),
        )
        == user_input_request
    )
    assert (
        decode_agent_user_input_response_from_dora(
            input_response_payload,
            input_response_metadata.to_dora_metadata(),
        )
        == user_input_response
    )
    assert (
        decode_agent_mcp_elicitation_request_from_dora(
            mcp_request_payload,
            mcp_request_metadata.to_dora_metadata(),
        )
        == mcp_request
    )
    assert (
        decode_agent_mcp_elicitation_response_from_dora(
            mcp_response_payload,
            mcp_response_metadata.to_dora_metadata(),
        )
        == mcp_response
    )


def test_agent_turn_request_and_done_roundtrip_through_dora() -> None:
    request = AgentTurnRequest(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        assistant_turn_id="assistant-turn-000001",
        seq=0,
        text="hello",
    )
    done = AgentTurnDone(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        agent_turn_id="assistant-turn-000001",
        seq=1,
        status="failed",
        message="model unavailable",
    )

    request_payload, request_metadata = encode_agent_turn_request_for_dora(request)
    done_payload, done_metadata = encode_agent_turn_done_for_dora(done)

    assert (
        decode_agent_turn_request_from_dora(
            request_payload,
            request_metadata.to_dora_metadata(),
        )
        == request
    )
    assert (
        decode_agent_turn_done_from_dora(
            done_payload,
            done_metadata.to_dora_metadata(),
        )
        == done
    )


def test_agent_turn_done_rejects_invalid_payload() -> None:
    event = AgentTurnDone(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        agent_turn_id="assistant-turn-000001",
        seq=1,
        status="completed",
    )
    _, metadata = encode_agent_turn_done_for_dora(event)

    with pytest.raises(DoraDialogueMetadataError, match="protobuf did not validate"):
        decode_agent_turn_done_from_dora(
            pa.array(list(b"unexpected"), type=pa.uint8()),
            metadata.to_dora_metadata(),
        )


def test_agent_tool_event_roundtrips_optional_fields() -> None:
    completed = AgentToolEvent(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        tool_call_id="tool-1",
        tool_name="robot.move",
        event="completed",
        seq=6,
        summary="done",
    )
    failed = AgentToolEvent(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        tool_call_id="tool-2",
        tool_name="robot.move",
        event="failed",
        seq=7,
        summary="attempted",
        error_message="blocked",
    )

    completed_payload, completed_metadata = encode_agent_tool_event_for_dora(completed)
    failed_payload, failed_metadata = encode_agent_tool_event_for_dora(failed)

    assert (
        decode_agent_tool_event_from_dora(completed_payload, completed_metadata.to_dora_metadata())
        == completed
    )
    assert (
        decode_agent_tool_event_from_dora(failed_payload, failed_metadata.to_dora_metadata())
        == failed
    )


def test_agent_tool_event_rejects_invalid_payload() -> None:
    event = AgentToolEvent(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        tool_call_id="tool-1",
        tool_name="robot.move",
        event="completed",
        seq=6,
        summary="done",
    )
    _, metadata = encode_agent_tool_event_for_dora(event)

    with pytest.raises(DoraDialogueMetadataError, match="protobuf did not validate"):
        decode_agent_tool_event_from_dora(
            pa.array(list(b"unexpected"), type=pa.uint8()),
            metadata.to_dora_metadata(),
        )


def test_agent_cancel_roundtrips_optional_reason() -> None:
    cancel = AgentCancelRequest(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        seq=8,
        reason="barge_in",
    )

    payload, metadata = encode_agent_cancel_request_for_dora(cancel)
    decoded = decode_agent_cancel_request_from_dora(payload, metadata.to_dora_metadata())

    assert decoded == cancel


def test_dialogue_rejects_invalid_payload() -> None:
    event = AgentTextDelta(
        session_id="session-1",
        user_turn_id="user-turn-000001",
        agent_turn_id="agent-turn-000001",
        seq=4,
        text="answer",
    )
    _, metadata = encode_agent_text_delta_for_dora(event)

    with pytest.raises(DoraDialogueMetadataError, match="protobuf did not validate"):
        decode_agent_text_delta_from_dora(pa.array([255], type=pa.uint8()), metadata)
