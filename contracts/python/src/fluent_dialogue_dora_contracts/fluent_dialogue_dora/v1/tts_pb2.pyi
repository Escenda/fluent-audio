from fluent_dialogue_dora_contracts.fluent_dialogue_dora.v1 import audio_pb2 as _audio_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TtsTextChunk(_message.Message):
    __slots__ = ("request_id", "session_id", "user_turn_id", "assistant_turn_id", "seq", "text", "is_final")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANT_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    IS_FINAL_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    session_id: str
    user_turn_id: str
    assistant_turn_id: str
    seq: int
    text: str
    is_final: bool
    def __init__(self, request_id: _Optional[str] = ..., session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., assistant_turn_id: _Optional[str] = ..., seq: _Optional[int] = ..., text: _Optional[str] = ..., is_final: _Optional[bool] = ...) -> None: ...

class TtsTextStreamFinal(_message.Message):
    __slots__ = ("session_id", "user_turn_id", "assistant_turn_id", "seq")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANT_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_turn_id: str
    assistant_turn_id: str
    seq: int
    def __init__(self, session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., assistant_turn_id: _Optional[str] = ..., seq: _Optional[int] = ...) -> None: ...

class SynthesizedAudioChunk(_message.Message):
    __slots__ = ("request_id", "session_id", "user_turn_id", "assistant_turn_id", "seq", "audio")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANT_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    AUDIO_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    session_id: str
    user_turn_id: str
    assistant_turn_id: str
    seq: int
    audio: _audio_pb2.AudioFrame
    def __init__(self, request_id: _Optional[str] = ..., session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., assistant_turn_id: _Optional[str] = ..., seq: _Optional[int] = ..., audio: _Optional[_Union[_audio_pb2.AudioFrame, _Mapping]] = ...) -> None: ...

class SynthesizedAudioStreamFinal(_message.Message):
    __slots__ = ("request_id", "session_id", "user_turn_id", "assistant_turn_id", "seq", "audio_source_id", "audio_stream_id", "audio_seq", "audio_sample_index", "audio_capture_time_ns", "audio_format")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    ASSISTANT_TURN_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    AUDIO_SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    AUDIO_STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    AUDIO_SEQ_FIELD_NUMBER: _ClassVar[int]
    AUDIO_SAMPLE_INDEX_FIELD_NUMBER: _ClassVar[int]
    AUDIO_CAPTURE_TIME_NS_FIELD_NUMBER: _ClassVar[int]
    AUDIO_FORMAT_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    session_id: str
    user_turn_id: str
    assistant_turn_id: str
    seq: int
    audio_source_id: str
    audio_stream_id: str
    audio_seq: int
    audio_sample_index: int
    audio_capture_time_ns: int
    audio_format: _audio_pb2.AudioFormat
    def __init__(self, request_id: _Optional[str] = ..., session_id: _Optional[str] = ..., user_turn_id: _Optional[str] = ..., assistant_turn_id: _Optional[str] = ..., seq: _Optional[int] = ..., audio_source_id: _Optional[str] = ..., audio_stream_id: _Optional[str] = ..., audio_seq: _Optional[int] = ..., audio_sample_index: _Optional[int] = ..., audio_capture_time_ns: _Optional[int] = ..., audio_format: _Optional[_Union[_audio_pb2.AudioFormat, _Mapping]] = ...) -> None: ...
