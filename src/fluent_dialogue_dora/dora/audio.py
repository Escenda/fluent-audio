"""DORA protobuf helpers for raw PCM audio messages."""

from __future__ import annotations

from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field

from fluent_dialogue_dora.contracts import AudioChunk, AudioFormat, ChannelLayout, SampleFormat
from fluent_dialogue_dora.dora.protobuf import (
    DoraMetadataMapping,
    DoraProtobufEncodedPayload,
    DoraProtobufMetadata,
    DoraProtobufPayloadInput,
    encode_proto_message_for_dora,
    decode_proto_message_from_dora,
    validate_dora_protobuf_metadata,
)
from fluent_dialogue_dora_contracts.fluent_dialogue_dora.v1.audio_pb2 import (
    CHANNEL_LAYOUT_INTERLEAVED,
    SAMPLE_FORMAT_F32LE,
    SAMPLE_FORMAT_S16LE,
    AudioFormat as PbAudioFormat,
    AudioFrame,
    AudioStreamFinal,
)

DoraAudioPayloadInput: TypeAlias = DoraProtobufPayloadInput
DoraAudioEncodedPayload: TypeAlias = DoraProtobufEncodedPayload
DoraAudioMetadata: TypeAlias = DoraProtobufMetadata


class DoraAudioMetadataError(ValueError):
    """Raised when DORA audio protobuf payloads cannot validate."""


class DoraAudioFinalMarkerError(DoraAudioMetadataError):
    """Raised when a DORA final marker is decoded as an audio chunk."""


class DoraAudioFinalMarker(BaseModel):
    """Validated audio stream completion decoded from protobuf transport."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    source_id: str = Field(min_length=1)
    stream_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    sample_index: int = Field(ge=0)
    capture_time_ns: int = Field(ge=0)
    sample_rate_hz: int = Field(gt=0)
    channels: int = Field(gt=0)
    sample_format: SampleFormat
    channel_layout: ChannelLayout

    def to_audio_format(self) -> AudioFormat:
        return AudioFormat(
            sample_rate_hz=self.sample_rate_hz,
            channels=self.channels,
            sample_format=self.sample_format,
            channel_layout=self.channel_layout,
        )


def encode_audio_chunk_for_dora(
    chunk: AudioChunk,
) -> tuple[DoraAudioEncodedPayload, DoraAudioMetadata]:
    frame = AudioFrame(
        source_id=chunk.source_id,
        stream_id=chunk.stream_id,
        seq=chunk.seq,
        sample_index=chunk.sample_index,
        capture_time_ns=chunk.capture_time_ns,
        frame_count=chunk.frame_count,
        format=_audio_format_to_proto(chunk.format),
        payload=chunk.payload,
    )
    return encode_proto_message_for_dora(frame)


def encode_audio_final_marker_for_dora(
    *,
    source_id: str,
    stream_id: str,
    seq: int,
    sample_index: int,
    capture_time_ns: int,
    audio_format: AudioFormat,
) -> tuple[DoraAudioEncodedPayload, DoraAudioMetadata]:
    final = AudioStreamFinal(
        source_id=source_id,
        stream_id=stream_id,
        seq=seq,
        sample_index=sample_index,
        capture_time_ns=capture_time_ns,
        format=_audio_format_to_proto(audio_format),
    )
    return encode_proto_message_for_dora(final)


def validate_dora_audio_metadata(
    metadata: DoraMetadataMapping | DoraAudioMetadata | None,
) -> DoraAudioMetadata:
    try:
        protobuf_metadata = validate_dora_protobuf_metadata(metadata)
    except ValueError as exc:
        raise DoraAudioMetadataError("DORA audio metadata is invalid") from exc
    if protobuf_metadata.message_type not in (
        AudioFrame.DESCRIPTOR.full_name,
        AudioStreamFinal.DESCRIPTOR.full_name,
    ):
        raise DoraAudioMetadataError(
            "DORA audio metadata message type is invalid: "
            f"{protobuf_metadata.message_type!r}"
        )
    return protobuf_metadata


def decode_audio_chunk_from_dora(
    payload: DoraAudioPayloadInput,
    metadata: DoraMetadataMapping | DoraAudioMetadata | None,
) -> AudioChunk:
    audio_metadata = validate_dora_audio_metadata(metadata)
    if audio_metadata.message_type == AudioStreamFinal.DESCRIPTOR.full_name:
        raise DoraAudioFinalMarkerError("DORA final audio marker is not an AudioChunk")
    try:
        frame = decode_proto_message_from_dora(payload, audio_metadata, AudioFrame)
        return AudioChunk(
            source_id=frame.source_id,
            stream_id=frame.stream_id,
            seq=frame.seq,
            sample_index=frame.sample_index,
            capture_time_ns=frame.capture_time_ns,
            frame_count=frame.frame_count,
            format=_audio_format_from_proto(frame.format),
            payload=frame.payload,
        )
    except ValueError as exc:
        raise DoraAudioMetadataError(
            "DORA audio protobuf did not validate as AudioChunk"
        ) from exc


def validate_dora_audio_final_marker(
    payload: DoraAudioPayloadInput,
    metadata: DoraMetadataMapping | DoraAudioMetadata | None,
) -> DoraAudioFinalMarker:
    audio_metadata = validate_dora_audio_metadata(metadata)
    if audio_metadata.message_type != AudioStreamFinal.DESCRIPTOR.full_name:
        raise DoraAudioMetadataError("DORA audio metadata is not a final marker")
    try:
        final = decode_proto_message_from_dora(payload, audio_metadata, AudioStreamFinal)
        return DoraAudioFinalMarker(
            source_id=final.source_id,
            stream_id=final.stream_id,
            seq=final.seq,
            sample_index=final.sample_index,
            capture_time_ns=final.capture_time_ns,
            sample_rate_hz=final.format.sample_rate_hz,
            channels=final.format.channels,
            sample_format=_sample_format_from_proto(final.format.sample_format),
            channel_layout=_channel_layout_from_proto(final.format.channel_layout),
        )
    except ValueError as exc:
        raise DoraAudioMetadataError(
            "DORA audio protobuf did not validate as AudioStreamFinal"
        ) from exc


def _audio_format_to_proto(audio_format: AudioFormat) -> PbAudioFormat:
    return PbAudioFormat(
        sample_rate_hz=audio_format.sample_rate_hz,
        channels=audio_format.channels,
        sample_format=_sample_format_to_proto(audio_format.sample_format),
        channel_layout=_channel_layout_to_proto(audio_format.channel_layout),
    )


def _audio_format_from_proto(audio_format: PbAudioFormat) -> AudioFormat:
    return AudioFormat(
        sample_rate_hz=audio_format.sample_rate_hz,
        channels=audio_format.channels,
        sample_format=_sample_format_from_proto(audio_format.sample_format),
        channel_layout=_channel_layout_from_proto(audio_format.channel_layout),
    )


def _sample_format_to_proto(sample_format: SampleFormat) -> int:
    if sample_format == "s16le":
        return SAMPLE_FORMAT_S16LE
    if sample_format == "f32le":
        return SAMPLE_FORMAT_F32LE
    raise DoraAudioMetadataError(f"Unsupported sample format: {sample_format!r}")


def _sample_format_from_proto(sample_format: int) -> SampleFormat:
    if sample_format == SAMPLE_FORMAT_S16LE:
        return "s16le"
    if sample_format == SAMPLE_FORMAT_F32LE:
        return "f32le"
    raise DoraAudioMetadataError(f"Unsupported protobuf sample format: {sample_format}")


def _channel_layout_to_proto(channel_layout: ChannelLayout) -> int:
    if channel_layout == "interleaved":
        return CHANNEL_LAYOUT_INTERLEAVED
    raise DoraAudioMetadataError(f"Unsupported channel layout: {channel_layout!r}")


def _channel_layout_from_proto(channel_layout: int) -> ChannelLayout:
    if channel_layout == CHANNEL_LAYOUT_INTERLEAVED:
        return "interleaved"
    raise DoraAudioMetadataError(f"Unsupported protobuf channel layout: {channel_layout}")
