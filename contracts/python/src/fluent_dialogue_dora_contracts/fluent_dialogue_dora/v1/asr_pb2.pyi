from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AsrStart(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "stream_id", "seq", "start_sample_index")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    START_SAMPLE_INDEX_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    stream_id: str
    seq: int
    start_sample_index: int
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., seq: _Optional[int] = ..., start_sample_index: _Optional[int] = ...) -> None: ...

class AsrStop(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "stream_id", "seq", "stop_sample_index")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    STOP_SAMPLE_INDEX_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    stream_id: str
    seq: int
    stop_sample_index: int
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., seq: _Optional[int] = ..., stop_sample_index: _Optional[int] = ...) -> None: ...

class AsrCancel(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "stream_id", "seq", "reason")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    stream_id: str
    seq: int
    reason: str
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., seq: _Optional[int] = ..., reason: _Optional[str] = ...) -> None: ...

class AsrControl(_message.Message):
    __slots__ = ("start", "stop", "cancel")
    START_FIELD_NUMBER: _ClassVar[int]
    STOP_FIELD_NUMBER: _ClassVar[int]
    CANCEL_FIELD_NUMBER: _ClassVar[int]
    start: AsrStart
    stop: AsrStop
    cancel: AsrCancel
    def __init__(self, start: _Optional[_Union[AsrStart, _Mapping]] = ..., stop: _Optional[_Union[AsrStop, _Mapping]] = ..., cancel: _Optional[_Union[AsrCancel, _Mapping]] = ...) -> None: ...

class AsrControlStreamFinal(_message.Message):
    __slots__ = ("session_id", "stream_id", "seq")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    stream_id: str
    seq: int
    def __init__(self, session_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., seq: _Optional[int] = ...) -> None: ...

class TranscriptDelta(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "stream_id", "seq", "text")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    stream_id: str
    seq: int
    text: str
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., seq: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...

class TranscriptPartial(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "stream_id", "seq", "text")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    stream_id: str
    seq: int
    text: str
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., seq: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...

class TranscriptFinal(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "stream_id", "seq", "text", "start_sample_index", "end_sample_index")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    START_SAMPLE_INDEX_FIELD_NUMBER: _ClassVar[int]
    END_SAMPLE_INDEX_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    stream_id: str
    seq: int
    text: str
    start_sample_index: int
    end_sample_index: int
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., seq: _Optional[int] = ..., text: _Optional[str] = ..., start_sample_index: _Optional[int] = ..., end_sample_index: _Optional[int] = ...) -> None: ...

class TranscriptEvent(_message.Message):
    __slots__ = ("delta", "final", "partial")
    DELTA_FIELD_NUMBER: _ClassVar[int]
    FINAL_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_FIELD_NUMBER: _ClassVar[int]
    delta: TranscriptDelta
    final: TranscriptFinal
    partial: TranscriptPartial
    def __init__(self, delta: _Optional[_Union[TranscriptDelta, _Mapping]] = ..., final: _Optional[_Union[TranscriptFinal, _Mapping]] = ..., partial: _Optional[_Union[TranscriptPartial, _Mapping]] = ...) -> None: ...

class TranscriptStreamFinal(_message.Message):
    __slots__ = ("session_id", "stream_id", "seq", "sample_index")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_INDEX_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    stream_id: str
    seq: int
    sample_index: int
    def __init__(self, session_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., seq: _Optional[int] = ..., sample_index: _Optional[int] = ...) -> None: ...
