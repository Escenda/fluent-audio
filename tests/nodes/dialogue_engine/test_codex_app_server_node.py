from pathlib import Path
import threading
import time

import pytest

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
    AgentUserInputOption,
    AgentUserInputQuestion,
    AgentUserInputRequest,
    AgentUserInputResponse,
)
from fluent_audio.dora import (
    decode_agent_approval_request_from_dora,
    decode_agent_mcp_elicitation_request_from_dora,
    decode_agent_runtime_event_from_dora,
    decode_agent_text_delta_from_dora,
    decode_agent_tool_event_from_dora,
    decode_agent_turn_done_from_dora,
    decode_agent_user_input_request_from_dora,
    encode_agent_cancel_request_for_dora,
    encode_agent_mcp_elicitation_response_for_dora,
    encode_agent_turn_request_for_dora,
    encode_agent_user_input_response_for_dora,
    validate_dora_agent_approval_metadata,
    validate_dora_agent_mcp_elicitation_request_metadata,
    validate_dora_agent_runtime_event_metadata,
    validate_dora_agent_text_metadata,
    validate_dora_agent_tool_metadata,
    validate_dora_agent_turn_done_metadata,
    validate_dora_agent_user_input_request_metadata,
)
from nodes.dialogue_engine.codex_app_server.main import (
    CodexActiveTurn,
    CodexApprovalResponseSubmission,
    CodexAppServerConfig,
    CodexAppServerNodeError,
    CodexControlQueue,
    CodexCommandApprovalRequestEnvelope,
    CodexFileChangeApprovalRequestEnvelope,
    CodexItemStartedEnvelope,
    CodexMcpElicitationJsonRpcResponse,
    CodexMcpElicitationRequestEnvelope,
    CodexAdditionalFileSystemPermissions,
    CodexAdditionalNetworkPermissions,
    CodexPermissionProfile,
    CodexPermissionsApprovalJsonRpcResponse,
    CodexPermissionsApprovalRequestEnvelope,
    CodexServerMessage,
    CodexToolUserInputJsonRpcResponse,
    CodexToolUserInputRequestEnvelope,
    PendingCodexApproval,
    PendingCodexMcpElicitationRequest,
    PendingCodexUserInputRequest,
    ProjectedApprovalRequestEvent,
    ProjectedAppServerEvent,
    ProjectedMcpElicitationRequestEvent,
    ProjectedTextDeltaEvent,
    ProjectedToolEvent,
    ProjectedTurnDoneEvent,
    ProjectedUserInputRequestEvent,
    parse_codex_server_message_line,
    parse_codex_ignorable_notification_line,
    project_codex_server_message,
    _build_codex_approval_response,
    _build_codex_mcp_elicitation_response,
    _build_codex_user_input_response,
    resolve_app_server_command,
    resolve_instruction_text,
    run_codex_app_server_events,
)


class FakeDoraNode:
    def __init__(self, events) -> None:
        self._events = events
        self._index = 0
        self.sent = []

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._events):
            raise StopIteration
        event = self._events[self._index]
        self._index += 1
        return event

    def next(self, timeout=None):
        return self.__next__()

    def send_output(self, output_id, data, metadata=None) -> None:
        self.sent.append((output_id, data, metadata))


class FakeCodexAppServerTransport:
    def __init__(self, *, turn_events: tuple[ProjectedAppServerEvent, ...] = ()) -> None:
        self._turn_events = turn_events
        self.turn_requests: list[AgentTurnRequest] = []
        self.approval_responses: list[AgentApprovalResponse] = []
        self.user_input_responses: list[AgentUserInputResponse] = []
        self.mcp_elicitation_responses: list[AgentMcpElicitationResponse] = []
        self.cancel_requests: list[AgentCancelRequest] = []

    def stream_turn(self, request: AgentTurnRequest) -> tuple[ProjectedAppServerEvent, ...]:
        self.turn_requests.append(request)
        return self._turn_events

    def respond_approval(self, response: AgentApprovalResponse) -> None:
        self.approval_responses.append(response)

    def respond_user_input(self, response: AgentUserInputResponse) -> None:
        self.user_input_responses.append(response)

    def respond_mcp_elicitation(self, response: AgentMcpElicitationResponse) -> None:
        self.mcp_elicitation_responses.append(response)

    def interrupt_turn(self, request: AgentCancelRequest) -> None:
        self.cancel_requests.append(request)


def _input(input_id: str, encoded):
    payload, metadata = encoded
    return {
        "type": "INPUT",
        "id": input_id,
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _turn_request() -> AgentTurnRequest:
    return AgentTurnRequest(
        session_id="session-1",
        user_turn_id="user-turn-1",
        assistant_turn_id="assistant-turn-1",
        seq=0,
        text="hello",
    )


def _active_turn() -> CodexActiveTurn:
    return CodexActiveTurn(
        session_id="session-1",
        thread_id="thread-1",
        turn_id="codex-turn-1",
    )


def _turn_event(turn: AgentTurnRequest):
    return _input("agent_turn", encode_agent_turn_request_for_dora(turn))


def _cancel_request() -> AgentCancelRequest:
    return AgentCancelRequest(
        session_id="session-1",
        user_turn_id="user-turn-1",
        seq=1,
        reason="voice_cancel",
    )


def _cancel_event(cancel: AgentCancelRequest):
    return _input("agent_cancel", encode_agent_cancel_request_for_dora(cancel))


def _approval_response_submission_thread(
    control_queue: CodexControlQueue,
    response: AgentApprovalResponse,
) -> threading.Thread:
    def submit_response() -> None:
        submission = CodexApprovalResponseSubmission(
            decision=response.decision,
            scope=response.scope,
            reason=response.reason,
        )
        deadline = time.monotonic() + 2.0
        while True:
            try:
                control_queue.submit_approval_response(
                    (response.session_id, response.user_turn_id, response.approval_id),
                    submission,
                )
                return
            except CodexAppServerNodeError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.01)

    thread = threading.Thread(target=submit_response, daemon=True)
    thread.start()
    return thread


def _user_input_response() -> AgentUserInputResponse:
    return AgentUserInputResponse(
        session_id="session-1",
        user_turn_id="user-turn-1",
        request_id="user-input-1",
        seq=0,
        answers=(
            AgentUserInputAnswer(question_id="q1", answers=("yes",)),
        ),
    )


def _user_input_response_event(response: AgentUserInputResponse | None = None):
    if response is None:
        response = _user_input_response()
    return _input("agent_user_input_response", encode_agent_user_input_response_for_dora(response))


def _mcp_elicitation_response() -> AgentMcpElicitationResponse:
    return AgentMcpElicitationResponse(
        session_id="session-1",
        user_turn_id="user-turn-1",
        request_id="mcp-elicitation-1",
        seq=0,
        action="accept",
        content={"approved": True},
    )


def _mcp_elicitation_response_event(
    response: AgentMcpElicitationResponse | None = None,
):
    if response is None:
        response = _mcp_elicitation_response()
    return _input(
        "agent_mcp_elicitation_response",
        encode_agent_mcp_elicitation_response_for_dora(response),
    )


def _text_delta(text: str = "Hello") -> ProjectedTextDeltaEvent:
    return ProjectedTextDeltaEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        agent_turn_id="assistant-turn-1",
        seq=0,
        text=text,
    )


def _turn_done(*, status: str = "completed") -> ProjectedTurnDoneEvent:
    return ProjectedTurnDoneEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        agent_turn_id="assistant-turn-1",
        seq=3,
        status=status,
        message="interrupted" if status == "cancelled" else None,
    )


def _approval() -> ProjectedApprovalRequestEvent:
    return ProjectedApprovalRequestEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        approval_id="approval-1",
        seq=1,
        prompt="Move arm?",
        action_label="robot.move",
    )


def _user_input_request() -> ProjectedUserInputRequestEvent:
    return ProjectedUserInputRequestEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        request_id="user-input-1",
        seq=2,
        questions=(
            AgentUserInputQuestion(
                id="q1",
                header="Confirm",
                question="Continue?",
                options=(
                    AgentUserInputOption(label="Yes", description="Continue the operation"),
                    AgentUserInputOption(label="No", description="Cancel the operation"),
                ),
            ),
        ),
    )


def _mcp_elicitation_request() -> ProjectedMcpElicitationRequestEvent:
    return ProjectedMcpElicitationRequestEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        request_id="mcp-elicitation-1",
        seq=3,
        server_name="robot",
        mode="form",
        message="Approve robot operation?",
        requested_schema={
            "type": "object",
            "properties": {"approved": {"type": "boolean"}},
            "required": ["approved"],
        },
    )


def _tool_event() -> ProjectedToolEvent:
    return ProjectedToolEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        tool_call_id="tool-1",
        tool_name="robot.move",
        tool_event="started",
        seq=2,
        summary="planning",
    )


def _decode_outputs(fake_node: FakeDoraNode):
    agent_events: list[
        AgentTextDelta
        | AgentTurnDone
        | AgentApprovalRequest
        | AgentUserInputRequest
        | AgentMcpElicitationRequest
        | AgentToolEvent
    ] = []
    text_deltas: list[AgentTextDelta] = []
    turn_done: list[AgentTurnDone] = []
    approvals: list[AgentApprovalRequest] = []
    user_inputs: list[AgentUserInputRequest] = []
    mcp_elicitations: list[AgentMcpElicitationRequest] = []
    tools: list[AgentToolEvent] = []
    for output_id, payload, metadata in fake_node.sent:
        assert metadata is not None
        if output_id == "agent_event":
            event_metadata = validate_dora_agent_runtime_event_metadata(metadata)
            agent_events.append(decode_agent_runtime_event_from_dora(payload, event_metadata))
        elif output_id == "agent_text":
            text_metadata = validate_dora_agent_text_metadata(metadata)
            text_deltas.append(decode_agent_text_delta_from_dora(payload, text_metadata))
        elif output_id == "agent_done":
            done_metadata = validate_dora_agent_turn_done_metadata(metadata)
            turn_done.append(decode_agent_turn_done_from_dora(payload, done_metadata))
        elif output_id == "agent_approval":
            approval_metadata = validate_dora_agent_approval_metadata(metadata)
            approvals.append(decode_agent_approval_request_from_dora(payload, approval_metadata))
        elif output_id == "agent_user_input":
            request_metadata = validate_dora_agent_user_input_request_metadata(metadata)
            user_inputs.append(
                decode_agent_user_input_request_from_dora(payload, request_metadata)
            )
        elif output_id == "agent_mcp_elicitation":
            request_metadata = validate_dora_agent_mcp_elicitation_request_metadata(metadata)
            mcp_elicitations.append(
                decode_agent_mcp_elicitation_request_from_dora(payload, request_metadata)
            )
        elif output_id == "agent_tool":
            tool_metadata = validate_dora_agent_tool_metadata(metadata)
            tools.append(decode_agent_tool_event_from_dora(payload, tool_metadata))
        else:
            raise AssertionError(f"unexpected output id: {output_id}")
    return agent_events, text_deltas, turn_done, approvals, user_inputs, mcp_elicitations, tools


def _parse_message(line: str) -> CodexServerMessage:
    message = parse_codex_server_message_line(line)
    assert message is not None
    return message


def test_codex_app_server_turn_stream_projects_validated_events_to_dora() -> None:
    turn = _turn_request()
    transport = FakeCodexAppServerTransport(
        turn_events=(
            _text_delta("Hello."),
            _approval(),
            _tool_event(),
            _turn_done(),
        ),
    )
    response = AgentApprovalResponse(
        session_id="session-1",
        user_turn_id="user-turn-1",
        approval_id="approval-1",
        seq=0,
        decision="accept",
    )
    fake_node = FakeDoraNode([_turn_event(turn), {"type": "STOP"}])
    control_queue = CodexControlQueue()
    response_thread = _approval_response_submission_thread(control_queue, response)

    summary = run_codex_app_server_events(fake_node, transport, control_queue=control_queue)
    response_thread.join(timeout=2.0)
    assert not response_thread.is_alive()
    (
        agent_events,
        text_deltas,
        turn_done,
        approvals,
        user_inputs,
        mcp_elicitations,
        tools,
    ) = _decode_outputs(fake_node)

    assert transport.turn_requests == [turn]
    assert transport.approval_responses == [response]
    assert summary.turn_requests == 1
    assert summary.text_deltas == 1
    assert summary.approval_requests == 1
    assert summary.approval_responses == 1
    assert summary.tool_events == 1
    assert summary.turn_done == 1
    assert [event.seq for event in agent_events] == [0, 1, 2, 3]
    assert [event.__class__ for event in agent_events] == [
        AgentTextDelta,
        AgentApprovalRequest,
        AgentToolEvent,
        AgentTurnDone,
    ]
    assert text_deltas == [
        AgentTextDelta(
            session_id="session-1",
            user_turn_id="user-turn-1",
            agent_turn_id="assistant-turn-1",
            seq=0,
            text="Hello.",
        )
    ]
    assert turn_done == [
        AgentTurnDone(
            session_id="session-1",
            user_turn_id="user-turn-1",
            agent_turn_id="assistant-turn-1",
            seq=3,
            status="completed",
        )
    ]
    assert approvals == [
        AgentApprovalRequest(
            session_id="session-1",
            user_turn_id="user-turn-1",
            approval_id="approval-1",
            seq=1,
            prompt="Move arm?",
            action_label="robot.move",
        )
    ]
    assert user_inputs == []
    assert mcp_elicitations == []
    assert tools == [
        AgentToolEvent(
            session_id="session-1",
            user_turn_id="user-turn-1",
            tool_call_id="tool-1",
            tool_name="robot.move",
            event="started",
            seq=2,
            summary="planning",
        )
    ]
    assert agent_events == [
        text_deltas[0],
        approvals[0],
        tools[0],
        turn_done[0],
    ]


def test_codex_app_server_resolves_user_input_and_mcp_elicitation_requests() -> None:
    user_input_response = _user_input_response()
    mcp_response = _mcp_elicitation_response()
    transport = FakeCodexAppServerTransport(
        turn_events=(
            _user_input_request(),
            _mcp_elicitation_request(),
            _turn_done(),
        ),
    )
    fake_node = FakeDoraNode(
        [
            _turn_event(_turn_request()),
            _user_input_response_event(user_input_response),
            _mcp_elicitation_response_event(mcp_response),
            {"type": "STOP"},
        ]
    )

    summary = run_codex_app_server_events(fake_node, transport)
    (
        agent_events,
        _text_deltas,
        _turn_done_events,
        _approvals,
        user_inputs,
        mcp_elicitations,
        _tools,
    ) = _decode_outputs(fake_node)

    assert transport.user_input_responses == [user_input_response]
    assert transport.mcp_elicitation_responses == [mcp_response]
    assert summary.user_input_requests == 1
    assert summary.user_input_responses == 1
    assert summary.mcp_elicitation_requests == 1
    assert summary.mcp_elicitation_responses == 1
    assert [event.__class__ for event in agent_events] == [
        AgentUserInputRequest,
        AgentMcpElicitationRequest,
        AgentTurnDone,
    ]
    assert user_inputs == [_user_input_request().to_contract()]
    assert mcp_elicitations == [_mcp_elicitation_request().to_contract()]


def test_codex_app_server_rejects_unmatched_user_input_and_mcp_responses() -> None:
    user_input_node = FakeDoraNode([_user_input_response_event(), {"type": "STOP"}])
    with pytest.raises(CodexAppServerNodeError, match="without a pending user-input"):
        run_codex_app_server_events(user_input_node, FakeCodexAppServerTransport())

    mcp_node = FakeDoraNode([_mcp_elicitation_response_event(), {"type": "STOP"}])
    with pytest.raises(CodexAppServerNodeError, match="without a pending MCP elicitation"):
        run_codex_app_server_events(mcp_node, FakeCodexAppServerTransport())


def test_codex_app_server_posts_cancel_request_to_active_transport() -> None:
    cancel = _cancel_request()
    transport = FakeCodexAppServerTransport()
    fake_node = FakeDoraNode([_cancel_event(cancel), {"type": "STOP"}])

    summary = run_codex_app_server_events(fake_node, transport)

    assert transport.cancel_requests == [cancel]
    assert summary.cancel_requests == 1
    assert summary.turn_requests == 0
    assert fake_node.sent == []


def test_codex_app_server_rejects_dora_approval_response_input() -> None:
    transport = FakeCodexAppServerTransport()
    fake_node = FakeDoraNode(
        [
            {
                "type": "INPUT",
                "id": "agent_approval_response",
                "value": b"",
                "metadata": {},
            },
            {"type": "STOP"},
        ]
    )

    with pytest.raises(CodexAppServerNodeError, match="Unexpected DORA input id"):
        run_codex_app_server_events(fake_node, transport)


def test_codex_control_queue_rejects_response_without_pending_approval() -> None:
    control_queue = CodexControlQueue()
    submission = CodexApprovalResponseSubmission(decision="accept")

    with pytest.raises(CodexAppServerNodeError, match="pending Codex request"):
        control_queue.submit_approval_response(
            ("session-1", "user-turn-1", "other-approval"),
            submission,
        )


def test_codex_app_server_accepts_cancel_while_waiting_for_approval_response() -> None:
    cancel = _cancel_request()
    transport = FakeCodexAppServerTransport(
        turn_events=(
            _approval(),
            _turn_done(status="cancelled"),
        ),
    )
    fake_node = FakeDoraNode([_turn_event(_turn_request()), _cancel_event(cancel), {"type": "STOP"}])

    summary = run_codex_app_server_events(
        fake_node,
        transport,
        poll_dora_control_during_approval=True,
    )

    assert transport.cancel_requests == [cancel]
    assert transport.approval_responses == []
    assert summary.approval_requests == 1
    assert summary.approval_responses == 0
    assert summary.cancel_requests == 1


def test_codex_app_server_requires_turn_done_for_each_turn_stream() -> None:
    transport = FakeCodexAppServerTransport(turn_events=(_text_delta(),))
    fake_node = FakeDoraNode([_turn_event(_turn_request()), {"type": "STOP"}])

    with pytest.raises(CodexAppServerNodeError, match="without exactly one turn_done"):
        run_codex_app_server_events(fake_node, transport)


def test_codex_app_server_rejects_event_after_turn_done() -> None:
    transport = FakeCodexAppServerTransport(turn_events=(_turn_done(), _text_delta()))
    fake_node = FakeDoraNode([_turn_event(_turn_request()), {"type": "STOP"}])

    with pytest.raises(CodexAppServerNodeError, match="after turn_done"):
        run_codex_app_server_events(fake_node, transport)


def test_codex_jsonrpc_message_projection_maps_delta_and_done() -> None:
    turn = _turn_request()
    active = _active_turn()
    delta = _parse_message(
        '{"method":"item/agentMessage/delta","params":{'
        '"threadId":"thread-1","turnId":"codex-turn-1","itemId":"item-1","delta":"Hi"}}'
    )
    done = _parse_message(
        '{"method":"turn/completed","params":{'
        '"threadId":"thread-1","turn":{"id":"codex-turn-1","items":[],"status":"interrupted"}}}'
    )

    projected_delta = project_codex_server_message(turn, active, delta, seq=0)
    projected_done = project_codex_server_message(turn, active, done, seq=1)

    assert projected_delta == ProjectedTextDeltaEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        agent_turn_id="assistant-turn-1",
        seq=0,
        text="Hi",
    )
    assert projected_done == ProjectedTurnDoneEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        agent_turn_id="assistant-turn-1",
        seq=1,
        status="cancelled",
    )


def test_codex_jsonrpc_message_projection_maps_tool_lifecycle() -> None:
    turn = _turn_request()
    active = _active_turn()
    message = _parse_message(
        '{"method":"item/started","params":{'
        '"threadId":"thread-1","turnId":"codex-turn-1","startedAtMs":1,'
        '"item":{"type":"mcpToolCall","id":"tool-1","server":"robot",'
        '"tool":"move","status":"inProgress","arguments":{}}}}'
    )

    projected = project_codex_server_message(turn, active, message, seq=2)

    assert isinstance(message, CodexItemStartedEnvelope)
    assert projected == ProjectedToolEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        tool_call_id="tool-1",
        tool_name="robot.move",
        tool_event="started",
        seq=2,
        summary="inProgress",
    )


def test_codex_jsonrpc_message_projection_ignores_command_lifecycle_and_resolved() -> None:
    turn = _turn_request()
    active = _active_turn()
    command_completed = _parse_message(
        '{"method":"item/completed","params":{'
        '"threadId":"thread-1","turnId":"codex-turn-1",'
        '"item":{"type":"commandExecution","id":"cmd-1","status":"completed"}}}'
    )
    user_message_started = _parse_message(
        '{"method":"item/started","params":{'
        '"threadId":"thread-1","turnId":"codex-turn-1",'
        '"item":{"type":"userMessage","id":"user-message-1",'
        '"message":{"text_elements":[]}}}}'
    )
    reasoning_started = _parse_message(
        '{"method":"item/started","params":{'
        '"threadId":"thread-1","turnId":"codex-turn-1",'
        '"item":{"type":"reasoning","id":"reasoning-1",'
        '"summary":[],"content":[]}}}'
    )
    reasoning_delta = _parse_message(
        '{"method":"item/reasoning/textDelta","params":{'
        '"threadId":"thread-1","turnId":"codex-turn-1",'
        '"itemId":"reasoning-1","delta":"thinking","contentIndex":0}}'
    )
    resolved = _parse_message(
        '{"method":"serverRequest/resolved","params":{'
        '"threadId":"thread-1","requestId":"approval-1"}}'
    )

    assert project_codex_server_message(turn, active, command_completed, seq=3) is None
    assert project_codex_server_message(turn, active, user_message_started, seq=4) is None
    assert project_codex_server_message(turn, active, reasoning_started, seq=5) is None
    assert project_codex_server_message(turn, active, reasoning_delta, seq=6) is None
    assert project_codex_server_message(turn, active, resolved, seq=7) is None


def test_codex_jsonrpc_message_projection_maps_command_and_file_approvals() -> None:
    turn = _turn_request()
    active = _active_turn()
    command = _parse_message(
        '{"id":"approval-1","method":"item/commandExecution/requestApproval","params":{'
        '"threadId":"thread-1","turnId":"codex-turn-1","itemId":"item-1",'
        '"startedAtMs":1,"command":"robot move","reason":"Move the robot?"}}'
    )
    file_change = _parse_message(
        '{"id":"approval-2","method":"item/fileChange/requestApproval","params":{'
        '"threadId":"thread-1","turnId":"codex-turn-1","itemId":"item-2",'
        '"startedAtMs":2,"grantRoot":"/tmp/robot","reason":"Write robot state?"}}'
    )

    projected_command = project_codex_server_message(turn, active, command, seq=3)
    projected_file_change = project_codex_server_message(turn, active, file_change, seq=4)

    assert isinstance(command, CodexCommandApprovalRequestEnvelope)
    assert isinstance(file_change, CodexFileChangeApprovalRequestEnvelope)
    assert projected_command == ProjectedApprovalRequestEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        approval_id="approval-1",
        seq=3,
        prompt="Move the robot?",
        action_label="robot move",
    )
    assert projected_file_change == ProjectedApprovalRequestEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        approval_id="approval-2",
        seq=4,
        prompt="Write robot state?",
        action_label="/tmp/robot",
    )


def test_codex_jsonrpc_numeric_approval_request_id_is_preserved_for_response() -> None:
    turn = _turn_request()
    active = _active_turn()
    command = _parse_message(
        '{"id":0,"method":"item/commandExecution/requestApproval","params":{'
        '"threadId":"thread-1","turnId":"codex-turn-1","itemId":"item-1",'
        '"command":"printf ok","reason":"Run command?"}}'
    )

    projected = project_codex_server_message(turn, active, command, seq=8)

    assert isinstance(command, CodexCommandApprovalRequestEnvelope)
    assert projected == ProjectedApprovalRequestEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        approval_id="0",
        seq=8,
        prompt="Run command?",
        action_label="printf ok",
    )

    response = _build_codex_approval_response(
        PendingCodexApproval(
            session_id="session-1",
            user_turn_id="user-turn-1",
            approval_id="0",
            request_id=0,
            kind="command",
        ),
        AgentApprovalResponse(
            session_id="session-1",
            user_turn_id="user-turn-1",
            approval_id="0",
            seq=9,
            decision="accept",
        ),
    )

    assert response.model_dump(by_alias=True, exclude_none=True) == {
        "id": 0,
        "result": {"decision": "accept"},
    }


def test_codex_jsonrpc_permissions_approval_projects_to_typed_approval_request() -> None:
    turn = _turn_request()
    active = _active_turn()
    permissions = _parse_message(
        '{"id":"approval-3","method":"item/permissions/requestApproval","params":{'
        '"threadId":"thread-1","turnId":"codex-turn-1","itemId":"item-3",'
        '"cwd":"/tmp/project","startedAtMs":10,'
        '"permissions":{"fileSystem":{"write":["/tmp/project","/tmp/shared"]},'
        '"network":{"enabled":true}},'
        '"reason":"Need additional workspace access"}}'
    )

    projected = project_codex_server_message(turn, active, permissions, seq=5)

    assert isinstance(permissions, CodexPermissionsApprovalRequestEnvelope)
    assert projected == ProjectedApprovalRequestEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        approval_id="approval-3",
        seq=5,
        prompt="Need additional workspace access",
        action_label="filesystem write:2, network:true",
    )


def test_codex_jsonrpc_permissions_approval_response_grants_or_denies_requested_subset() -> None:
    requested = CodexPermissionProfile(
        file_system=CodexAdditionalFileSystemPermissions(write=("/tmp/project",)),
        network=CodexAdditionalNetworkPermissions(enabled=True),
    )
    pending = PendingCodexApproval(
        session_id="session-1",
        user_turn_id="user-turn-1",
        approval_id="approval-3",
        request_id="jsonrpc-approval-3",
        kind="permissions",
        requested_permissions=requested,
    )

    accepted = _build_codex_approval_response(
        pending,
        AgentApprovalResponse(
            session_id="session-1",
            user_turn_id="user-turn-1",
            approval_id="approval-3",
            seq=0,
            decision="accept",
            scope="session",
        ),
    )
    declined = _build_codex_approval_response(
        pending,
        AgentApprovalResponse(
            session_id="session-1",
            user_turn_id="user-turn-1",
            approval_id="approval-3",
            seq=1,
            decision="decline",
        ),
    )

    assert isinstance(accepted, CodexPermissionsApprovalJsonRpcResponse)
    assert accepted.model_dump(by_alias=True, exclude_none=True) == {
        "id": "jsonrpc-approval-3",
        "result": {
            "permissions": {
                "fileSystem": {"write": ("/tmp/project",)},
                "network": {"enabled": True},
            },
            "scope": "session",
        },
    }
    assert isinstance(declined, CodexPermissionsApprovalJsonRpcResponse)
    assert declined.model_dump(by_alias=True, exclude_none=True) == {
        "id": "jsonrpc-approval-3",
        "result": {"permissions": {}, "scope": "turn"},
    }


def test_codex_jsonrpc_user_input_projects_and_builds_typed_response() -> None:
    turn = _turn_request()
    active = _active_turn()
    tool_input = _parse_message(
        '{"id":"tool-input-1","method":"item/tool/requestUserInput","params":{'
        '"threadId":"thread-1","turnId":"codex-turn-1","itemId":"item-1",'
        '"questions":[{"id":"q1","header":"Confirm","question":"Continue?",'
        '"isOther":false,"isSecret":false,'
        '"options":[{"label":"Yes","description":"Continue"},'
        '{"label":"No","description":"Cancel"}]}]}}'
    )

    projected = project_codex_server_message(turn, active, tool_input, seq=5)

    assert isinstance(tool_input, CodexToolUserInputRequestEnvelope)
    assert projected == ProjectedUserInputRequestEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        request_id="tool-input-1",
        seq=5,
        questions=(
            AgentUserInputQuestion(
                id="q1",
                header="Confirm",
                question="Continue?",
                options=(
                    AgentUserInputOption(label="Yes", description="Continue"),
                    AgentUserInputOption(label="No", description="Cancel"),
                ),
            ),
        ),
    )

    response = _build_codex_user_input_response(
        PendingCodexUserInputRequest(
            session_id="session-1",
            user_turn_id="user-turn-1",
            request_id="tool-input-1",
            codex_request_id="tool-input-1",
            question_ids=("q1",),
        ),
        AgentUserInputResponse(
            session_id="session-1",
            user_turn_id="user-turn-1",
            request_id="tool-input-1",
            seq=6,
            answers=(
                AgentUserInputAnswer(question_id="q1", answers=("yes",)),
            ),
        ),
    )

    assert isinstance(response, CodexToolUserInputJsonRpcResponse)
    assert response.model_dump(by_alias=True, exclude_none=True) == {
        "id": "tool-input-1",
        "result": {"answers": {"q1": {"answers": ("yes",)}}},
    }


def test_codex_jsonrpc_mcp_elicitation_projects_url_and_form_modes() -> None:
    turn = _turn_request()
    active = _active_turn()
    url_elicitation = _parse_message(
        '{"id":"mcp-elicitation-1","method":"mcpServer/elicitation/request","params":{'
        '"threadId":"thread-1","turnId":"codex-turn-1","serverName":"robot",'
        '"mode":"url","elicitationId":"elicit-1","url":"https://example.invalid",'
        '"message":"Open robot console?","_meta":{"source":"mcp"}}}'
    )
    form_elicitation = _parse_message(
        '{"id":"mcp-elicitation-2","method":"mcpServer/elicitation/request","params":{'
        '"threadId":"thread-1","turnId":"codex-turn-1","serverName":"robot",'
        '"mode":"form","message":"Approve robot operation?",'
        '"requestedSchema":{"type":"object","properties":{"approved":{"type":"boolean"}},'
        '"required":["approved"]}}}'
    )

    projected_url = project_codex_server_message(turn, active, url_elicitation, seq=6)
    projected_form = project_codex_server_message(turn, active, form_elicitation, seq=7)

    assert isinstance(url_elicitation, CodexMcpElicitationRequestEnvelope)
    assert isinstance(form_elicitation, CodexMcpElicitationRequestEnvelope)
    assert projected_url == ProjectedMcpElicitationRequestEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        request_id="mcp-elicitation-1",
        seq=6,
        server_name="robot",
        mode="url",
        message="Open robot console?",
        url="https://example.invalid",
        elicitation_id="elicit-1",
        meta={"source": "mcp"},
    )
    assert projected_form == ProjectedMcpElicitationRequestEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        request_id="mcp-elicitation-2",
        seq=7,
        server_name="robot",
        mode="form",
        message="Approve robot operation?",
        requested_schema={
            "type": "object",
            "properties": {"approved": {"type": "boolean"}},
            "required": ["approved"],
        },
    )

    response = _build_codex_mcp_elicitation_response(
        PendingCodexMcpElicitationRequest(
            session_id="session-1",
            user_turn_id="user-turn-1",
            request_id="mcp-elicitation-2",
            codex_request_id="mcp-elicitation-2",
            mode="form",
        ),
        AgentMcpElicitationResponse(
            session_id="session-1",
            user_turn_id="user-turn-1",
            request_id="mcp-elicitation-2",
            seq=8,
            action="accept",
            content={"approved": True},
        ),
    )

    assert isinstance(response, CodexMcpElicitationJsonRpcResponse)
    assert response.model_dump(by_alias=True, exclude_none=False) == {
        "id": "mcp-elicitation-2",
        "result": {
            "action": "accept",
            "content": {"approved": True},
            "_meta": None,
        },
    }


def test_codex_jsonrpc_parser_rejects_unknown_server_messages() -> None:
    assert parse_codex_server_message_line("") is None
    assert parse_codex_server_message_line("  \n") is None

    with pytest.raises(CodexAppServerNodeError, match="invalid"):
        parse_codex_server_message_line('{"method":"turn/completed","params":{}}')

    with pytest.raises(CodexAppServerNodeError, match="invalid"):
        parse_codex_server_message_line('{"method":"unknown","params":{}}')


def test_codex_jsonrpc_parser_accepts_live_non_turn_notifications() -> None:
    config_warning = parse_codex_ignorable_notification_line(
        '{"method":"configWarning","params":{"summary":"sandbox warning","details":null}}'
    )
    generic_warning = parse_codex_ignorable_notification_line(
        '{"method":"warning","params":{"message":"model warning"}}'
    )
    deprecation_notice = parse_codex_ignorable_notification_line(
        '{"method":"deprecationNotice","params":{'
        '"deprecation":{"key":"web_search_request",'
        '"message":"web search is enabled by default"}}}'
    )
    remote_status = parse_codex_ignorable_notification_line(
        '{"method":"remoteControl/status/changed","params":{'
        '"status":"disabled","serverName":"host","installationId":"install-1",'
        '"environmentId":null}}'
    )
    mcp_startup_status = parse_codex_ignorable_notification_line(
        '{"method":"mcpServer/startupStatus/updated","params":{'
        '"serverName":"filesystem","status":{"state":"starting","error":null}}}'
    )
    thread_status = parse_codex_ignorable_notification_line(
        '{"method":"thread/status/changed","params":{'
        '"threadId":"thread-1","status":{"state":"active","activeFlags":[]}}}'
    )
    token_usage = parse_codex_ignorable_notification_line(
        '{"method":"thread/tokenUsage/updated","params":{'
        '"threadId":"thread-1","usage":{"inputTokens":1,'
        '"outputTokens":2,"contextWindow":258400}}}'
    )
    rate_limits = parse_codex_ignorable_notification_line(
        '{"method":"account/rateLimits/updated","params":{'
        '"rateLimits":{"primary":{"usedPercent":0,'
        '"windowMinutes":300,"resetsInSeconds":1,'
        '"limitReachedType":null}}}}'
    )

    assert config_warning is not None
    assert generic_warning is not None
    assert deprecation_notice is not None
    assert remote_status is not None
    assert mcp_startup_status is not None
    assert thread_status is not None
    assert token_usage is not None
    assert rate_limits is not None
    assert parse_codex_ignorable_notification_line('{"method":"unknown","params":{}}') is None


def test_codex_config_rejects_empty_command() -> None:
    with pytest.raises(ValueError, match="command must not be empty"):
        CodexAppServerConfig(command=())


def test_resolve_app_server_command_reads_one_argument_per_line_file(tmp_path: Path) -> None:
    command_file = tmp_path / "codex-fixture.command"
    command_file.write_text(
        "# comment\n"
        "  # indented comment\n"
        "uv\n"
        "run\n"
        "fixture.py\n",
        encoding="utf-8",
    )

    command = resolve_app_server_command(
        command_remainder=(),
        command_json=None,
        command_file=command_file,
    )

    assert command == ("uv", "run", "fixture.py")


def test_resolve_app_server_command_parses_json_array() -> None:
    command = resolve_app_server_command(
        command_remainder=(),
        command_json='["uv","run","fixture.py"]',
        command_file=None,
    )

    assert command == ("uv", "run", "fixture.py")


def test_resolve_app_server_command_rejects_multiple_sources(tmp_path: Path) -> None:
    command_file = tmp_path / "codex-fixture.command"
    command_file.write_text("uv\n", encoding="utf-8")

    with pytest.raises(CodexAppServerNodeError, match="Specify only one"):
        resolve_app_server_command(
            command_remainder=("codex",),
            command_json=None,
            command_file=command_file,
        )


def test_resolve_instruction_text_reads_file(tmp_path: Path) -> None:
    instruction_file = tmp_path / "instructions.txt"
    instruction_file.write_text("Use local vLLM only.\nNever use external model calls.", encoding="utf-8")

    resolved = resolve_instruction_text(
        inline_text=None,
        text_file=instruction_file,
        label="base-instructions",
    )

    assert resolved == "Use local vLLM only.\nNever use external model calls."


def test_resolve_instruction_text_rejects_multiple_sources(tmp_path: Path) -> None:
    instruction_file = tmp_path / "instructions.txt"
    instruction_file.write_text("from file", encoding="utf-8")

    with pytest.raises(CodexAppServerNodeError, match="Specify only one"):
        resolve_instruction_text(
            inline_text="inline",
            text_file=instruction_file,
            label="developer-instructions",
        )
