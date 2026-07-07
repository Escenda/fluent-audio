from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VoiceActivityState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VOICE_ACTIVITY_STATE_UNSPECIFIED: _ClassVar[VoiceActivityState]
    VOICE_ACTIVITY_STATE_SILENCE: _ClassVar[VoiceActivityState]
    VOICE_ACTIVITY_STATE_SPEECH: _ClassVar[VoiceActivityState]

class TurnState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TURN_STATE_UNSPECIFIED: _ClassVar[TurnState]
    TURN_STATE_IDLE: _ClassVar[TurnState]
    TURN_STATE_STARTED: _ClassVar[TurnState]
    TURN_STATE_ACTIVE: _ClassVar[TurnState]
    TURN_STATE_ENDED: _ClassVar[TurnState]
    TURN_STATE_CANCELLED: _ClassVar[TurnState]
VOICE_ACTIVITY_STATE_UNSPECIFIED: VoiceActivityState
VOICE_ACTIVITY_STATE_SILENCE: VoiceActivityState
VOICE_ACTIVITY_STATE_SPEECH: VoiceActivityState
TURN_STATE_UNSPECIFIED: TurnState
TURN_STATE_IDLE: TurnState
TURN_STATE_STARTED: TurnState
TURN_STATE_ACTIVE: TurnState
TURN_STATE_ENDED: TurnState
TURN_STATE_CANCELLED: TurnState

class VoiceActivityEvent(_message.Message):
    __slots__ = ("source_id", "stream_id", "seq", "sample_index", "frame_count", "state", "speech_probability")
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_INDEX_FIELD_NUMBER: _ClassVar[int]
    FRAME_COUNT_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    SPEECH_PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    source_id: str
    stream_id: str
    seq: int
    sample_index: int
    frame_count: int
    state: VoiceActivityState
    speech_probability: float
    def __init__(self, source_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., seq: _Optional[int] = ..., sample_index: _Optional[int] = ..., frame_count: _Optional[int] = ..., state: _Optional[_Union[VoiceActivityState, str]] = ..., speech_probability: _Optional[float] = ...) -> None: ...

class AudioLevelEvent(_message.Message):
    __slots__ = ("source_id", "stream_id", "seq", "sample_index", "frame_count", "rms_dbfs", "peak_dbfs", "speech_probability")
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_INDEX_FIELD_NUMBER: _ClassVar[int]
    FRAME_COUNT_FIELD_NUMBER: _ClassVar[int]
    RMS_DBFS_FIELD_NUMBER: _ClassVar[int]
    PEAK_DBFS_FIELD_NUMBER: _ClassVar[int]
    SPEECH_PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    source_id: str
    stream_id: str
    seq: int
    sample_index: int
    frame_count: int
    rms_dbfs: float
    peak_dbfs: float
    speech_probability: float
    def __init__(self, source_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., seq: _Optional[int] = ..., sample_index: _Optional[int] = ..., frame_count: _Optional[int] = ..., rms_dbfs: _Optional[float] = ..., peak_dbfs: _Optional[float] = ..., speech_probability: _Optional[float] = ...) -> None: ...

class VoiceActivityStreamFinal(_message.Message):
    __slots__ = ("source_id", "stream_id", "seq", "sample_index")
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_INDEX_FIELD_NUMBER: _ClassVar[int]
    source_id: str
    stream_id: str
    seq: int
    sample_index: int
    def __init__(self, source_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., seq: _Optional[int] = ..., sample_index: _Optional[int] = ...) -> None: ...

class TurnEvent(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "stream_id", "seq", "sample_index", "state", "confidence")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_INDEX_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    stream_id: str
    seq: int
    sample_index: int
    state: TurnState
    confidence: float
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., seq: _Optional[int] = ..., sample_index: _Optional[int] = ..., state: _Optional[_Union[TurnState, str]] = ..., confidence: _Optional[float] = ...) -> None: ...

class TurnStreamFinal(_message.Message):
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
