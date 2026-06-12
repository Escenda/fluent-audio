from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SampleFormat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SAMPLE_FORMAT_UNSPECIFIED: _ClassVar[SampleFormat]
    SAMPLE_FORMAT_S16LE: _ClassVar[SampleFormat]
    SAMPLE_FORMAT_F32LE: _ClassVar[SampleFormat]

class ChannelLayout(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHANNEL_LAYOUT_UNSPECIFIED: _ClassVar[ChannelLayout]
    CHANNEL_LAYOUT_INTERLEAVED: _ClassVar[ChannelLayout]
SAMPLE_FORMAT_UNSPECIFIED: SampleFormat
SAMPLE_FORMAT_S16LE: SampleFormat
SAMPLE_FORMAT_F32LE: SampleFormat
CHANNEL_LAYOUT_UNSPECIFIED: ChannelLayout
CHANNEL_LAYOUT_INTERLEAVED: ChannelLayout

class AudioFormat(_message.Message):
    __slots__ = ("sample_rate_hz", "channels", "sample_format", "channel_layout")
    SAMPLE_RATE_HZ_FIELD_NUMBER: _ClassVar[int]
    CHANNELS_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_FORMAT_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_LAYOUT_FIELD_NUMBER: _ClassVar[int]
    sample_rate_hz: int
    channels: int
    sample_format: SampleFormat
    channel_layout: ChannelLayout
    def __init__(self, sample_rate_hz: _Optional[int] = ..., channels: _Optional[int] = ..., sample_format: _Optional[_Union[SampleFormat, str]] = ..., channel_layout: _Optional[_Union[ChannelLayout, str]] = ...) -> None: ...

class AudioFrame(_message.Message):
    __slots__ = ("source_id", "stream_id", "seq", "sample_index", "capture_time_ns", "frame_count", "format", "payload")
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_INDEX_FIELD_NUMBER: _ClassVar[int]
    CAPTURE_TIME_NS_FIELD_NUMBER: _ClassVar[int]
    FRAME_COUNT_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    source_id: str
    stream_id: str
    seq: int
    sample_index: int
    capture_time_ns: int
    frame_count: int
    format: AudioFormat
    payload: bytes
    def __init__(self, source_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., seq: _Optional[int] = ..., sample_index: _Optional[int] = ..., capture_time_ns: _Optional[int] = ..., frame_count: _Optional[int] = ..., format: _Optional[_Union[AudioFormat, _Mapping]] = ..., payload: _Optional[bytes] = ...) -> None: ...

class AudioStreamFinal(_message.Message):
    __slots__ = ("source_id", "stream_id", "seq", "sample_index", "capture_time_ns", "format")
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_INDEX_FIELD_NUMBER: _ClassVar[int]
    CAPTURE_TIME_NS_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    source_id: str
    stream_id: str
    seq: int
    sample_index: int
    capture_time_ns: int
    format: AudioFormat
    def __init__(self, source_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., seq: _Optional[int] = ..., sample_index: _Optional[int] = ..., capture_time_ns: _Optional[int] = ..., format: _Optional[_Union[AudioFormat, _Mapping]] = ...) -> None: ...
