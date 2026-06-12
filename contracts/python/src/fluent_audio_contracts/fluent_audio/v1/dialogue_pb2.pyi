from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DialogueInputKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DIALOGUE_INPUT_KIND_UNSPECIFIED: _ClassVar[DialogueInputKind]
    DIALOGUE_INPUT_KIND_TRANSCRIPT_FINAL: _ClassVar[DialogueInputKind]
    DIALOGUE_INPUT_KIND_CANCEL: _ClassVar[DialogueInputKind]
    DIALOGUE_INPUT_KIND_PLAYBACK_DONE: _ClassVar[DialogueInputKind]

class DialogueEventKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DIALOGUE_EVENT_KIND_UNSPECIFIED: _ClassVar[DialogueEventKind]
    DIALOGUE_EVENT_KIND_AGENT_TEXT: _ClassVar[DialogueEventKind]
    DIALOGUE_EVENT_KIND_TTS_TEXT: _ClassVar[DialogueEventKind]
    DIALOGUE_EVENT_KIND_APPROVAL_REQUESTED: _ClassVar[DialogueEventKind]
    DIALOGUE_EVENT_KIND_USER_INPUT_REQUESTED: _ClassVar[DialogueEventKind]
    DIALOGUE_EVENT_KIND_MCP_ELICITATION_REQUESTED: _ClassVar[DialogueEventKind]
    DIALOGUE_EVENT_KIND_TOOL_EVENT: _ClassVar[DialogueEventKind]
    DIALOGUE_EVENT_KIND_CANCELLED: _ClassVar[DialogueEventKind]
    DIALOGUE_EVENT_KIND_ERROR: _ClassVar[DialogueEventKind]

class AgentApprovalDecision(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AGENT_APPROVAL_DECISION_UNSPECIFIED: _ClassVar[AgentApprovalDecision]
    AGENT_APPROVAL_DECISION_ACCEPT: _ClassVar[AgentApprovalDecision]
    AGENT_APPROVAL_DECISION_DECLINE: _ClassVar[AgentApprovalDecision]
    AGENT_APPROVAL_DECISION_CANCEL: _ClassVar[AgentApprovalDecision]

class AgentApprovalScope(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AGENT_APPROVAL_SCOPE_UNSPECIFIED: _ClassVar[AgentApprovalScope]
    AGENT_APPROVAL_SCOPE_TURN: _ClassVar[AgentApprovalScope]
    AGENT_APPROVAL_SCOPE_SESSION: _ClassVar[AgentApprovalScope]

class AgentToolEventKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AGENT_TOOL_EVENT_KIND_UNSPECIFIED: _ClassVar[AgentToolEventKind]
    AGENT_TOOL_EVENT_KIND_STARTED: _ClassVar[AgentToolEventKind]
    AGENT_TOOL_EVENT_KIND_COMPLETED: _ClassVar[AgentToolEventKind]
    AGENT_TOOL_EVENT_KIND_FAILED: _ClassVar[AgentToolEventKind]

class AgentTurnDoneStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AGENT_TURN_DONE_STATUS_UNSPECIFIED: _ClassVar[AgentTurnDoneStatus]
    AGENT_TURN_DONE_STATUS_COMPLETED: _ClassVar[AgentTurnDoneStatus]
    AGENT_TURN_DONE_STATUS_CANCELLED: _ClassVar[AgentTurnDoneStatus]
    AGENT_TURN_DONE_STATUS_FAILED: _ClassVar[AgentTurnDoneStatus]

class AgentMcpElicitationMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AGENT_MCP_ELICITATION_MODE_UNSPECIFIED: _ClassVar[AgentMcpElicitationMode]
    AGENT_MCP_ELICITATION_MODE_FORM: _ClassVar[AgentMcpElicitationMode]
    AGENT_MCP_ELICITATION_MODE_URL: _ClassVar[AgentMcpElicitationMode]

class AgentMcpElicitationAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AGENT_MCP_ELICITATION_ACTION_UNSPECIFIED: _ClassVar[AgentMcpElicitationAction]
    AGENT_MCP_ELICITATION_ACTION_ACCEPT: _ClassVar[AgentMcpElicitationAction]
    AGENT_MCP_ELICITATION_ACTION_DECLINE: _ClassVar[AgentMcpElicitationAction]
    AGENT_MCP_ELICITATION_ACTION_CANCEL: _ClassVar[AgentMcpElicitationAction]
DIALOGUE_INPUT_KIND_UNSPECIFIED: DialogueInputKind
DIALOGUE_INPUT_KIND_TRANSCRIPT_FINAL: DialogueInputKind
DIALOGUE_INPUT_KIND_CANCEL: DialogueInputKind
DIALOGUE_INPUT_KIND_PLAYBACK_DONE: DialogueInputKind
DIALOGUE_EVENT_KIND_UNSPECIFIED: DialogueEventKind
DIALOGUE_EVENT_KIND_AGENT_TEXT: DialogueEventKind
DIALOGUE_EVENT_KIND_TTS_TEXT: DialogueEventKind
DIALOGUE_EVENT_KIND_APPROVAL_REQUESTED: DialogueEventKind
DIALOGUE_EVENT_KIND_USER_INPUT_REQUESTED: DialogueEventKind
DIALOGUE_EVENT_KIND_MCP_ELICITATION_REQUESTED: DialogueEventKind
DIALOGUE_EVENT_KIND_TOOL_EVENT: DialogueEventKind
DIALOGUE_EVENT_KIND_CANCELLED: DialogueEventKind
DIALOGUE_EVENT_KIND_ERROR: DialogueEventKind
AGENT_APPROVAL_DECISION_UNSPECIFIED: AgentApprovalDecision
AGENT_APPROVAL_DECISION_ACCEPT: AgentApprovalDecision
AGENT_APPROVAL_DECISION_DECLINE: AgentApprovalDecision
AGENT_APPROVAL_DECISION_CANCEL: AgentApprovalDecision
AGENT_APPROVAL_SCOPE_UNSPECIFIED: AgentApprovalScope
AGENT_APPROVAL_SCOPE_TURN: AgentApprovalScope
AGENT_APPROVAL_SCOPE_SESSION: AgentApprovalScope
AGENT_TOOL_EVENT_KIND_UNSPECIFIED: AgentToolEventKind
AGENT_TOOL_EVENT_KIND_STARTED: AgentToolEventKind
AGENT_TOOL_EVENT_KIND_COMPLETED: AgentToolEventKind
AGENT_TOOL_EVENT_KIND_FAILED: AgentToolEventKind
AGENT_TURN_DONE_STATUS_UNSPECIFIED: AgentTurnDoneStatus
AGENT_TURN_DONE_STATUS_COMPLETED: AgentTurnDoneStatus
AGENT_TURN_DONE_STATUS_CANCELLED: AgentTurnDoneStatus
AGENT_TURN_DONE_STATUS_FAILED: AgentTurnDoneStatus
AGENT_MCP_ELICITATION_MODE_UNSPECIFIED: AgentMcpElicitationMode
AGENT_MCP_ELICITATION_MODE_FORM: AgentMcpElicitationMode
AGENT_MCP_ELICITATION_MODE_URL: AgentMcpElicitationMode
AGENT_MCP_ELICITATION_ACTION_UNSPECIFIED: AgentMcpElicitationAction
AGENT_MCP_ELICITATION_ACTION_ACCEPT: AgentMcpElicitationAction
AGENT_MCP_ELICITATION_ACTION_DECLINE: AgentMcpElicitationAction
AGENT_MCP_ELICITATION_ACTION_CANCEL: AgentMcpElicitationAction

class DialogueInput(_message.Message):
    __slots__ = ("input_type", "session_id", "user_turn_id", "seq", "text", "request_id")
    INPUT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    input_type: DialogueInputKind
    session_id: str
    user_turn_id: str
    seq: int
    text: str
    request_id: str
    def __init__(self, input_type: _Optional[_Union[DialogueInputKind, str]] = ..., session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., seq: _Optional[int] = ..., text: _Optional[str] = ..., request_id: _Optional[str] = ...) -> None: ...

class DialogueEvent(_message.Message):
    __slots__ = ("event", "session_id", "user_turn_id", "seq", "text", "request_id", "message")
    EVENT_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    event: DialogueEventKind
    session_id: str
    user_turn_id: str
    seq: int
    text: str
    request_id: str
    message: str
    def __init__(self, event: _Optional[_Union[DialogueEventKind, str]] = ..., session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., seq: _Optional[int] = ..., text: _Optional[str] = ..., request_id: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class AgentTurnRequest(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "assistant_turn_id", "seq", "text")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANT_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    assistant_turn_id: str
    seq: int
    text: str
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., assistant_turn_id: _Optional[str] = ..., seq: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...

class AgentTextDelta(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "agent_turn_id", "seq", "text")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    agent_turn_id: str
    seq: int
    text: str
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., agent_turn_id: _Optional[str] = ..., seq: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...

class AgentTurnDone(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "agent_turn_id", "seq", "status", "reason")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    agent_turn_id: str
    seq: int
    status: AgentTurnDoneStatus
    reason: str
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., agent_turn_id: _Optional[str] = ..., seq: _Optional[int] = ..., status: _Optional[_Union[AgentTurnDoneStatus, str]] = ..., reason: _Optional[str] = ...) -> None: ...

class AgentApprovalRequest(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "approval_id", "seq", "prompt", "action_label")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    ACTION_LABEL_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    approval_id: str
    seq: int
    prompt: str
    action_label: str
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., approval_id: _Optional[str] = ..., seq: _Optional[int] = ..., prompt: _Optional[str] = ..., action_label: _Optional[str] = ...) -> None: ...

class AgentApprovalResponse(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "approval_id", "seq", "decision", "scope", "reason")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    DECISION_FIELD_NUMBER: _ClassVar[int]
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    approval_id: str
    seq: int
    decision: AgentApprovalDecision
    scope: AgentApprovalScope
    reason: str
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., approval_id: _Optional[str] = ..., seq: _Optional[int] = ..., decision: _Optional[_Union[AgentApprovalDecision, str]] = ..., scope: _Optional[_Union[AgentApprovalScope, str]] = ..., reason: _Optional[str] = ...) -> None: ...

class AgentToolEvent(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "tool_call_id", "seq", "event", "name", "summary", "error_message")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALL_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    tool_call_id: str
    seq: int
    event: AgentToolEventKind
    name: str
    summary: str
    error_message: str
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., tool_call_id: _Optional[str] = ..., seq: _Optional[int] = ..., event: _Optional[_Union[AgentToolEventKind, str]] = ..., name: _Optional[str] = ..., summary: _Optional[str] = ..., error_message: _Optional[str] = ...) -> None: ...

class AgentCancelRequest(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "seq", "reason")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    seq: int
    reason: str
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., seq: _Optional[int] = ..., reason: _Optional[str] = ...) -> None: ...

class AgentUserInputOption(_message.Message):
    __slots__ = ("label", "description")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    label: str
    description: str
    def __init__(self, label: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class AgentUserInputQuestion(_message.Message):
    __slots__ = ("id", "header", "question", "is_other", "is_secret", "options")
    ID_FIELD_NUMBER: _ClassVar[int]
    HEADER_FIELD_NUMBER: _ClassVar[int]
    QUESTION_FIELD_NUMBER: _ClassVar[int]
    IS_OTHER_FIELD_NUMBER: _ClassVar[int]
    IS_SECRET_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    id: str
    header: str
    question: str
    is_other: bool
    is_secret: bool
    options: _containers.RepeatedCompositeFieldContainer[AgentUserInputOption]
    def __init__(self, id: _Optional[str] = ..., header: _Optional[str] = ..., question: _Optional[str] = ..., is_other: _Optional[bool] = ..., is_secret: _Optional[bool] = ..., options: _Optional[_Iterable[_Union[AgentUserInputOption, _Mapping]]] = ...) -> None: ...

class AgentUserInputRequest(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "request_id", "seq", "questions")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    QUESTIONS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    request_id: str
    seq: int
    questions: _containers.RepeatedCompositeFieldContainer[AgentUserInputQuestion]
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., request_id: _Optional[str] = ..., seq: _Optional[int] = ..., questions: _Optional[_Iterable[_Union[AgentUserInputQuestion, _Mapping]]] = ...) -> None: ...

class AgentUserInputAnswer(_message.Message):
    __slots__ = ("question_id", "answers")
    QUESTION_ID_FIELD_NUMBER: _ClassVar[int]
    ANSWERS_FIELD_NUMBER: _ClassVar[int]
    question_id: str
    answers: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, question_id: _Optional[str] = ..., answers: _Optional[_Iterable[str]] = ...) -> None: ...

class AgentUserInputResponse(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "request_id", "seq", "answers")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    ANSWERS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    request_id: str
    seq: int
    answers: _containers.RepeatedCompositeFieldContainer[AgentUserInputAnswer]
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., request_id: _Optional[str] = ..., seq: _Optional[int] = ..., answers: _Optional[_Iterable[_Union[AgentUserInputAnswer, _Mapping]]] = ...) -> None: ...

class AgentMcpElicitationRequest(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "request_id", "seq", "server_name", "mode", "message", "url", "elicitation_id", "requested_schema", "meta")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    SERVER_NAME_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    ELICITATION_ID_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    request_id: str
    seq: int
    server_name: str
    mode: AgentMcpElicitationMode
    message: str
    url: str
    elicitation_id: str
    requested_schema: _struct_pb2.Value
    meta: _struct_pb2.Value
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., request_id: _Optional[str] = ..., seq: _Optional[int] = ..., server_name: _Optional[str] = ..., mode: _Optional[_Union[AgentMcpElicitationMode, str]] = ..., message: _Optional[str] = ..., url: _Optional[str] = ..., elicitation_id: _Optional[str] = ..., requested_schema: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ..., meta: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ...) -> None: ...

class AgentMcpElicitationResponse(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "request_id", "seq", "action", "content", "meta")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    request_id: str
    seq: int
    action: AgentMcpElicitationAction
    content: _struct_pb2.Value
    meta: _struct_pb2.Value
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., request_id: _Optional[str] = ..., seq: _Optional[int] = ..., action: _Optional[_Union[AgentMcpElicitationAction, str]] = ..., content: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ..., meta: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ...) -> None: ...
