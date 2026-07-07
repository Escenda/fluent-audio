import pytest

from fluent_dialogue_dora.contracts import (
    AgentApprovalRequest,
    AgentTextDelta,
    AgentToolEvent,
    AgentTurnDone,
)
from fluent_dialogue_dora.dora import (
    encode_agent_approval_request_for_dora,
    encode_agent_text_delta_for_dora,
    encode_agent_tool_event_for_dora,
    encode_agent_turn_done_for_dora,
)
from nodes.dialogue_engine.agent_output_probe import (
    AgentOutputProbeError,
    AgentOutputProbeSummary,
    run_agent_output_probe_dora,
    validate_summary,
)


class FakeDoraNode:
    def __init__(self, events) -> None:
        self._events = events

    def __iter__(self):
        return iter(self._events)


def _input_event(input_id: str, encoded):
    payload, metadata = encoded
    return {
        "type": "INPUT",
        "id": input_id,
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def test_agent_output_probe_validates_text_tool_approval_and_done() -> None:
    summary = run_agent_output_probe_dora(
        FakeDoraNode(
            (
                _input_event(
                    "agent_text",
                    encode_agent_text_delta_for_dora(
                        AgentTextDelta(
                            session_id="session-1",
                            user_turn_id="user-turn-1",
                            agent_turn_id="assistant-turn-1",
                            seq=0,
                            text="hello",
                        )
                    ),
                ),
                _input_event(
                    "agent_approval",
                    encode_agent_approval_request_for_dora(
                        AgentApprovalRequest(
                            session_id="session-1",
                            user_turn_id="user-turn-1",
                            approval_id="approval-1",
                            seq=1,
                            prompt="Proceed?",
                            action_label="robot.move",
                        )
                    ),
                ),
                _input_event(
                    "agent_tool",
                    encode_agent_tool_event_for_dora(
                        AgentToolEvent(
                            session_id="session-1",
                            user_turn_id="user-turn-1",
                            tool_call_id="tool-1",
                            tool_name="robot.inspect",
                            event="completed",
                            seq=2,
                            summary="done",
                        )
                    ),
                ),
                _input_event(
                    "agent_done",
                    encode_agent_turn_done_for_dora(
                        AgentTurnDone(
                            session_id="session-1",
                            user_turn_id="user-turn-1",
                            agent_turn_id="assistant-turn-1",
                            seq=3,
                            status="completed",
                        )
                    ),
                ),
            )
        ),
        session_id="session-1",
        user_turn_id="user-turn-1",
        agent_turn_id="assistant-turn-1",
    )

    assert summary == AgentOutputProbeSummary(
        text_deltas=1,
        turn_done=1,
        approval_requests=1,
        tool_events=1,
        done_status="completed",
        text="hello",
    )
    validate_summary(
        summary,
        expected_min_text_deltas=1,
        expected_approval_requests=1,
        expected_tool_events=1,
        expected_done_status="completed",
        expected_text_contains="ell",
    )


def test_agent_output_probe_accepts_split_stream_done_arriving_before_text() -> None:
    summary = run_agent_output_probe_dora(
        FakeDoraNode(
            (
                _input_event(
                    "agent_done",
                    encode_agent_turn_done_for_dora(
                        AgentTurnDone(
                            session_id="session-1",
                            user_turn_id="user-turn-1",
                            agent_turn_id="assistant-turn-1",
                            seq=2,
                            status="completed",
                        )
                    ),
                ),
                _input_event(
                    "agent_text",
                    encode_agent_text_delta_for_dora(
                        AgentTextDelta(
                            session_id="session-1",
                            user_turn_id="user-turn-1",
                            agent_turn_id="assistant-turn-1",
                            seq=1,
                            text="hello",
                        )
                    ),
                ),
            )
        ),
        session_id="session-1",
        user_turn_id="user-turn-1",
        agent_turn_id="assistant-turn-1",
    )

    assert summary == AgentOutputProbeSummary(
        text_deltas=1,
        turn_done=1,
        approval_requests=0,
        tool_events=0,
        done_status="completed",
        text="hello",
    )


def test_agent_output_probe_rejects_non_increasing_seq() -> None:
    with pytest.raises(AgentOutputProbeError, match="duplicate seq"):
        run_agent_output_probe_dora(
            FakeDoraNode(
                (
                    _input_event(
                        "agent_text",
                        encode_agent_text_delta_for_dora(
                            AgentTextDelta(
                                session_id="session-1",
                                user_turn_id="user-turn-1",
                                agent_turn_id="assistant-turn-1",
                                seq=1,
                                text="hello",
                            )
                        ),
                    ),
                    _input_event(
                        "agent_done",
                        encode_agent_turn_done_for_dora(
                            AgentTurnDone(
                                session_id="session-1",
                                user_turn_id="user-turn-1",
                                agent_turn_id="assistant-turn-1",
                                seq=1,
                                status="completed",
                            )
                        ),
                    ),
                )
            ),
            session_id="session-1",
            user_turn_id="user-turn-1",
            agent_turn_id="assistant-turn-1",
        )


def test_agent_output_probe_summary_rejects_unexpected_approval() -> None:
    with pytest.raises(AgentOutputProbeError, match="approval count mismatch"):
        validate_summary(
            AgentOutputProbeSummary(
                text_deltas=0,
                turn_done=1,
                approval_requests=1,
                tool_events=0,
                done_status="completed",
                text="",
            ),
            expected_min_text_deltas=0,
            expected_approval_requests=0,
            expected_tool_events=0,
            expected_done_status="completed",
            expected_text_contains="",
        )
