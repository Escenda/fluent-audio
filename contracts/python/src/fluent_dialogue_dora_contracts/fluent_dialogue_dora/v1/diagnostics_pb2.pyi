from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DiagnosticSeverity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DIAGNOSTIC_SEVERITY_UNSPECIFIED: _ClassVar[DiagnosticSeverity]
    DIAGNOSTIC_SEVERITY_OK: _ClassVar[DiagnosticSeverity]
    DIAGNOSTIC_SEVERITY_WARN: _ClassVar[DiagnosticSeverity]
    DIAGNOSTIC_SEVERITY_ERROR: _ClassVar[DiagnosticSeverity]
    DIAGNOSTIC_SEVERITY_FATAL: _ClassVar[DiagnosticSeverity]

class NodeState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NODE_STATE_UNSPECIFIED: _ClassVar[NodeState]
    NODE_STATE_STARTING: _ClassVar[NodeState]
    NODE_STATE_READY: _ClassVar[NodeState]
    NODE_STATE_RUNNING: _ClassVar[NodeState]
    NODE_STATE_DEGRADED: _ClassVar[NodeState]
    NODE_STATE_STOPPING: _ClassVar[NodeState]
    NODE_STATE_STOPPED: _ClassVar[NodeState]
    NODE_STATE_FAILED: _ClassVar[NodeState]
DIAGNOSTIC_SEVERITY_UNSPECIFIED: DiagnosticSeverity
DIAGNOSTIC_SEVERITY_OK: DiagnosticSeverity
DIAGNOSTIC_SEVERITY_WARN: DiagnosticSeverity
DIAGNOSTIC_SEVERITY_ERROR: DiagnosticSeverity
DIAGNOSTIC_SEVERITY_FATAL: DiagnosticSeverity
NODE_STATE_UNSPECIFIED: NodeState
NODE_STATE_STARTING: NodeState
NODE_STATE_READY: NodeState
NODE_STATE_RUNNING: NodeState
NODE_STATE_DEGRADED: NodeState
NODE_STATE_STOPPING: NodeState
NODE_STATE_STOPPED: NodeState
NODE_STATE_FAILED: NodeState

class NodeStatus(_message.Message):
    __slots__ = ("node_id", "state", "seq", "observed_time_ns", "message")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    OBSERVED_TIME_NS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    state: NodeState
    seq: int
    observed_time_ns: int
    message: str
    def __init__(self, node_id: _Optional[str] = ..., state: _Optional[_Union[NodeState, str]] = ..., seq: _Optional[int] = ..., observed_time_ns: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class DiagnosticEvent(_message.Message):
    __slots__ = ("node_id", "severity", "seq", "observed_time_ns", "code", "message")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    OBSERVED_TIME_NS_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    node_id: str
    severity: DiagnosticSeverity
    seq: int
    observed_time_ns: int
    code: str
    message: str
    def __init__(self, node_id: _Optional[str] = ..., severity: _Optional[_Union[DiagnosticSeverity, str]] = ..., seq: _Optional[int] = ..., observed_time_ns: _Optional[int] = ..., code: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...
