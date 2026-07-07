from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PlaybackCommandKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PLAYBACK_COMMAND_KIND_UNSPECIFIED: _ClassVar[PlaybackCommandKind]
    PLAYBACK_COMMAND_KIND_STOP: _ClassVar[PlaybackCommandKind]
    PLAYBACK_COMMAND_KIND_PAUSE: _ClassVar[PlaybackCommandKind]
    PLAYBACK_COMMAND_KIND_RESUME: _ClassVar[PlaybackCommandKind]
    PLAYBACK_COMMAND_KIND_CLEAR: _ClassVar[PlaybackCommandKind]

class PlaybackStateKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PLAYBACK_STATE_KIND_UNSPECIFIED: _ClassVar[PlaybackStateKind]
    PLAYBACK_STATE_KIND_QUEUED: _ClassVar[PlaybackStateKind]
    PLAYBACK_STATE_KIND_PLAYING: _ClassVar[PlaybackStateKind]
    PLAYBACK_STATE_KIND_PAUSED: _ClassVar[PlaybackStateKind]
    PLAYBACK_STATE_KIND_STOPPED: _ClassVar[PlaybackStateKind]
    PLAYBACK_STATE_KIND_COMPLETED: _ClassVar[PlaybackStateKind]
    PLAYBACK_STATE_KIND_CANCELLED: _ClassVar[PlaybackStateKind]
    PLAYBACK_STATE_KIND_FAILED: _ClassVar[PlaybackStateKind]

class PlaybackDoneStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PLAYBACK_DONE_STATUS_UNSPECIFIED: _ClassVar[PlaybackDoneStatus]
    PLAYBACK_DONE_STATUS_COMPLETED: _ClassVar[PlaybackDoneStatus]
    PLAYBACK_DONE_STATUS_STOPPED: _ClassVar[PlaybackDoneStatus]
    PLAYBACK_DONE_STATUS_CANCELLED: _ClassVar[PlaybackDoneStatus]
    PLAYBACK_DONE_STATUS_FAILED: _ClassVar[PlaybackDoneStatus]

class PlaybackControlKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PLAYBACK_CONTROL_KIND_UNSPECIFIED: _ClassVar[PlaybackControlKind]
    PLAYBACK_CONTROL_KIND_FLUSH: _ClassVar[PlaybackControlKind]
PLAYBACK_COMMAND_KIND_UNSPECIFIED: PlaybackCommandKind
PLAYBACK_COMMAND_KIND_STOP: PlaybackCommandKind
PLAYBACK_COMMAND_KIND_PAUSE: PlaybackCommandKind
PLAYBACK_COMMAND_KIND_RESUME: PlaybackCommandKind
PLAYBACK_COMMAND_KIND_CLEAR: PlaybackCommandKind
PLAYBACK_STATE_KIND_UNSPECIFIED: PlaybackStateKind
PLAYBACK_STATE_KIND_QUEUED: PlaybackStateKind
PLAYBACK_STATE_KIND_PLAYING: PlaybackStateKind
PLAYBACK_STATE_KIND_PAUSED: PlaybackStateKind
PLAYBACK_STATE_KIND_STOPPED: PlaybackStateKind
PLAYBACK_STATE_KIND_COMPLETED: PlaybackStateKind
PLAYBACK_STATE_KIND_CANCELLED: PlaybackStateKind
PLAYBACK_STATE_KIND_FAILED: PlaybackStateKind
PLAYBACK_DONE_STATUS_UNSPECIFIED: PlaybackDoneStatus
PLAYBACK_DONE_STATUS_COMPLETED: PlaybackDoneStatus
PLAYBACK_DONE_STATUS_STOPPED: PlaybackDoneStatus
PLAYBACK_DONE_STATUS_CANCELLED: PlaybackDoneStatus
PLAYBACK_DONE_STATUS_FAILED: PlaybackDoneStatus
PLAYBACK_CONTROL_KIND_UNSPECIFIED: PlaybackControlKind
PLAYBACK_CONTROL_KIND_FLUSH: PlaybackControlKind

class PlaybackCommand(_message.Message):
    __slots__ = ("command", "request_id", "stream_id", "seq")
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    command: PlaybackCommandKind
    request_id: str
    stream_id: str
    seq: int
    def __init__(self, command: _Optional[_Union[PlaybackCommandKind, str]] = ..., request_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., seq: _Optional[int] = ...) -> None: ...

class PlaybackControlCommand(_message.Message):
    __slots__ = ("kind", "stream_id", "seq", "fade_out_ms")
    KIND_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    FADE_OUT_MS_FIELD_NUMBER: _ClassVar[int]
    kind: PlaybackControlKind
    stream_id: str
    seq: int
    fade_out_ms: int
    def __init__(self, kind: _Optional[_Union[PlaybackControlKind, str]] = ..., stream_id: _Optional[str] = ..., seq: _Optional[int] = ..., fade_out_ms: _Optional[int] = ...) -> None: ...

class PlaybackState(_message.Message):
    __slots__ = ("request_id", "session_id", "user_turn_id", "stream_id", "state", "seq", "played_frames", "reason")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    PLAYED_FRAMES_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    session_id: str
    user_turn_id: str
    stream_id: str
    state: PlaybackStateKind
    seq: int
    played_frames: int
    reason: str
    def __init__(self, request_id: _Optional[str] = ..., session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., state: _Optional[_Union[PlaybackStateKind, str]] = ..., seq: _Optional[int] = ..., played_frames: _Optional[int] = ..., reason: _Optional[str] = ...) -> None: ...

class PlaybackDone(_message.Message):
    __slots__ = ("request_id", "session_id", "user_turn_id", "stream_id", "status", "final_sequence", "total_frames", "reason")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    FINAL_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FRAMES_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    session_id: str
    user_turn_id: str
    stream_id: str
    status: PlaybackDoneStatus
    final_sequence: int
    total_frames: int
    reason: str
    def __init__(self, request_id: _Optional[str] = ..., session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., status: _Optional[_Union[PlaybackDoneStatus, str]] = ..., final_sequence: _Optional[int] = ..., total_frames: _Optional[int] = ..., reason: _Optional[str] = ...) -> None: ...
