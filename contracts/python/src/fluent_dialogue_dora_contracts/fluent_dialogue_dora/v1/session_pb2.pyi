from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VoiceSessionState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VOICE_SESSION_STATE_UNSPECIFIED: _ClassVar[VoiceSessionState]
    VOICE_SESSION_STATE_IDLE: _ClassVar[VoiceSessionState]
    VOICE_SESSION_STATE_LISTENING: _ClassVar[VoiceSessionState]
    VOICE_SESSION_STATE_USER_SPEAKING: _ClassVar[VoiceSessionState]
    VOICE_SESSION_STATE_TRANSCRIBING: _ClassVar[VoiceSessionState]
    VOICE_SESSION_STATE_THINKING: _ClassVar[VoiceSessionState]
    VOICE_SESSION_STATE_SPEAKING: _ClassVar[VoiceSessionState]
    VOICE_SESSION_STATE_INTERRUPTED: _ClassVar[VoiceSessionState]
    VOICE_SESSION_STATE_CLOSED: _ClassVar[VoiceSessionState]
    VOICE_SESSION_STATE_ERROR: _ClassVar[VoiceSessionState]

class VoiceSessionEventKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VOICE_SESSION_EVENT_KIND_UNSPECIFIED: _ClassVar[VoiceSessionEventKind]
    VOICE_SESSION_EVENT_KIND_SESSION_STARTED: _ClassVar[VoiceSessionEventKind]
    VOICE_SESSION_EVENT_KIND_STATE_CHANGED: _ClassVar[VoiceSessionEventKind]
    VOICE_SESSION_EVENT_KIND_USER_TURN_STARTED: _ClassVar[VoiceSessionEventKind]
    VOICE_SESSION_EVENT_KIND_USER_TURN_FINALIZED: _ClassVar[VoiceSessionEventKind]
    VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_STARTED: _ClassVar[VoiceSessionEventKind]
    VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_COMPLETED: _ClassVar[VoiceSessionEventKind]
    VOICE_SESSION_EVENT_KIND_SESSION_CLOSED: _ClassVar[VoiceSessionEventKind]
    VOICE_SESSION_EVENT_KIND_ERROR: _ClassVar[VoiceSessionEventKind]
VOICE_SESSION_STATE_UNSPECIFIED: VoiceSessionState
VOICE_SESSION_STATE_IDLE: VoiceSessionState
VOICE_SESSION_STATE_LISTENING: VoiceSessionState
VOICE_SESSION_STATE_USER_SPEAKING: VoiceSessionState
VOICE_SESSION_STATE_TRANSCRIBING: VoiceSessionState
VOICE_SESSION_STATE_THINKING: VoiceSessionState
VOICE_SESSION_STATE_SPEAKING: VoiceSessionState
VOICE_SESSION_STATE_INTERRUPTED: VoiceSessionState
VOICE_SESSION_STATE_CLOSED: VoiceSessionState
VOICE_SESSION_STATE_ERROR: VoiceSessionState
VOICE_SESSION_EVENT_KIND_UNSPECIFIED: VoiceSessionEventKind
VOICE_SESSION_EVENT_KIND_SESSION_STARTED: VoiceSessionEventKind
VOICE_SESSION_EVENT_KIND_STATE_CHANGED: VoiceSessionEventKind
VOICE_SESSION_EVENT_KIND_USER_TURN_STARTED: VoiceSessionEventKind
VOICE_SESSION_EVENT_KIND_USER_TURN_FINALIZED: VoiceSessionEventKind
VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_STARTED: VoiceSessionEventKind
VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_COMPLETED: VoiceSessionEventKind
VOICE_SESSION_EVENT_KIND_SESSION_CLOSED: VoiceSessionEventKind
VOICE_SESSION_EVENT_KIND_ERROR: VoiceSessionEventKind

class TurnIds(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "assistant_turn_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANT_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    assistant_turn_id: str
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., assistant_turn_id: _Optional[str] = ...) -> None: ...

class VoiceSessionEvent(_message.Message):
    __slots__ = ("event", "state", "seq", "turn_ids", "message")
    EVENT_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    TURN_IDS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    event: VoiceSessionEventKind
    state: VoiceSessionState
    seq: int
    turn_ids: TurnIds
    message: str
    def __init__(self, event: _Optional[_Union[VoiceSessionEventKind, str]] = ..., state: _Optional[_Union[VoiceSessionState, str]] = ..., seq: _Optional[int] = ..., turn_ids: _Optional[_Union[TurnIds, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...
