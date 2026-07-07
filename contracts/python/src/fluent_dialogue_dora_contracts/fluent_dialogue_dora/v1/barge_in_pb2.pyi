from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class BargeInEvent(_message.Message):
    __slots__ = ("session_id", "source_id", "stream_id", "seq", "playback_request_id", "playback_stream_id", "played_frames", "detected_sample_index", "speech_probability")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    PLAYBACK_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYBACK_STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYED_FRAMES_FIELD_NUMBER: _ClassVar[int]
    DETECTED_SAMPLE_INDEX_FIELD_NUMBER: _ClassVar[int]
    SPEECH_PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    source_id: str
    stream_id: str
    seq: int
    playback_request_id: str
    playback_stream_id: str
    played_frames: int
    detected_sample_index: int
    speech_probability: float
    def __init__(self, session_id: _Optional[str] = ..., source_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., seq: _Optional[int] = ..., playback_request_id: _Optional[str] = ..., playback_stream_id: _Optional[str] = ..., played_frames: _Optional[int] = ..., detected_sample_index: _Optional[int] = ..., speech_probability: _Optional[float] = ...) -> None: ...

class BargeInStreamFinal(_message.Message):
    __slots__ = ("session_id", "source_id", "stream_id", "seq")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    source_id: str
    stream_id: str
    seq: int
    def __init__(self, session_id: _Optional[str] = ..., source_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., seq: _Optional[int] = ...) -> None: ...
