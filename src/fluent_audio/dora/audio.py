"""Typed DORA metadata helpers for raw PCM audio payloads."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from typing import Self, TypeAlias

import pyarrow as pa
from pydantic import BaseModel, ConfigDict, Field, model_validator

from fluent_audio.contracts import AudioChunk, AudioFormat, ChannelLayout, SampleFormat

DoraMetadataPrimitive: TypeAlias = bool | int | float | str
DoraMetadataValue: TypeAlias = DoraMetadataPrimitive | list[DoraMetadataPrimitive]
DoraMetadataMapping: TypeAlias = Mapping[str, DoraMetadataValue]
DoraMetadataMutableMapping: TypeAlias = MutableMapping[str, DoraMetadataValue]
DoraAudioPayloadInput: TypeAlias = bytes | pa.UInt8Array
DoraAudioEncodedPayload: TypeAlias = pa.UInt8Array

DORA_AUDIO_METADATA_FIELDS: tuple[str, ...] = (
    "source_id",
    "stream_id",
    "seq",
    "sample_index",
    "capture_time_ns",
    "frame_count",
    "sample_rate_hz",
    "channels",
    "sample_format",
    "channel_layout",
    "final",
)


class DoraAudioMetadataError(ValueError):
    """Raised when DORA audio metadata cannot validate an audio payload."""


class DoraAudioFinalMarkerError(DoraAudioMetadataError):
    """Raised when a DORA final marker is decoded as an audio chunk."""


class DoraAudioMetadata(BaseModel):
    """Flat DORA metadata needed to reconstruct an ``AudioChunk``."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    source_id: str = Field(min_length=1)
    stream_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    sample_index: int = Field(ge=0)
    capture_time_ns: int = Field(ge=0)
    frame_count: int = Field(ge=0)
    sample_rate_hz: int = Field(gt=0)
    channels: int = Field(gt=0)
    sample_format: SampleFormat
    channel_layout: ChannelLayout
    final: bool

    @model_validator(mode="after")
    def validate_frame_count(self) -> Self:
        if self.final:
            if self.frame_count != 0:
                raise ValueError("DORA final audio marker must have frame_count=0")
        elif self.frame_count == 0:
            raise ValueError("DORA audio chunk metadata must have frame_count > 0")
        return self

    def to_audio_format(self) -> AudioFormat:
        return AudioFormat(
            sample_rate_hz=self.sample_rate_hz,
            channels=self.channels,
            sample_format=self.sample_format,
            channel_layout=self.channel_layout,
        )

    def to_dora_metadata(self) -> DoraMetadataMutableMapping:
        return {
            "source_id": self.source_id,
            "stream_id": self.stream_id,
            "seq": self.seq,
            "sample_index": self.sample_index,
            "capture_time_ns": self.capture_time_ns,
            "frame_count": self.frame_count,
            "sample_rate_hz": self.sample_rate_hz,
            "channels": self.channels,
            "sample_format": self.sample_format,
            "channel_layout": self.channel_layout,
            "final": self.final,
        }


DoraAudioMetadataInput: TypeAlias = DoraMetadataMapping | DoraAudioMetadata | None


def encode_audio_chunk_for_dora(
    chunk: AudioChunk,
) -> tuple[DoraAudioEncodedPayload, DoraAudioMetadata]:
    """Encode an ``AudioChunk`` as a DORA payload plus flat DORA metadata."""

    return (
        _encode_dora_audio_payload(chunk.payload),
        DoraAudioMetadata(
            source_id=chunk.source_id,
            stream_id=chunk.stream_id,
            seq=chunk.seq,
            sample_index=chunk.sample_index,
            capture_time_ns=chunk.capture_time_ns,
            frame_count=chunk.frame_count,
            sample_rate_hz=chunk.format.sample_rate_hz,
            channels=chunk.format.channels,
            sample_format=chunk.format.sample_format,
            channel_layout=chunk.format.channel_layout,
            final=False,
        ),
    )


def encode_audio_final_marker_for_dora(
    *,
    source_id: str,
    stream_id: str,
    seq: int,
    sample_index: int,
    capture_time_ns: int,
    audio_format: AudioFormat,
) -> tuple[DoraAudioEncodedPayload, DoraAudioMetadata]:
    """Encode explicit source completion for the DORA audio boundary."""

    return (
        _encode_dora_audio_payload(b""),
        DoraAudioMetadata(
            source_id=source_id,
            stream_id=stream_id,
            seq=seq,
            sample_index=sample_index,
            capture_time_ns=capture_time_ns,
            frame_count=0,
            sample_rate_hz=audio_format.sample_rate_hz,
            channels=audio_format.channels,
            sample_format=audio_format.sample_format,
            channel_layout=audio_format.channel_layout,
            final=True,
        ),
    )


def validate_dora_audio_metadata(metadata: DoraAudioMetadataInput) -> DoraAudioMetadata:
    """Validate DORA audio metadata at the boundary."""

    if metadata is None:
        raise DoraAudioMetadataError("DORA audio metadata is required")
    if isinstance(metadata, DoraAudioMetadata):
        return metadata
    if not isinstance(metadata, Mapping):
        raise DoraAudioMetadataError("DORA audio metadata is invalid")

    extracted_metadata = _extract_dora_audio_metadata(metadata)
    try:
        return DoraAudioMetadata.model_validate(extracted_metadata)
    except ValueError as exc:
        raise DoraAudioMetadataError("DORA audio metadata is invalid") from exc


def decode_audio_chunk_from_dora(
    payload: DoraAudioPayloadInput, metadata: DoraAudioMetadataInput
) -> AudioChunk:
    """Decode DORA bytes payload and metadata into a validated ``AudioChunk``."""

    payload_bytes = _decode_dora_audio_payload(payload)
    audio_metadata = validate_dora_audio_metadata(metadata)
    if audio_metadata.final:
        raise DoraAudioFinalMarkerError("DORA final audio marker is not an AudioChunk")
    try:
        return AudioChunk(
            source_id=audio_metadata.source_id,
            stream_id=audio_metadata.stream_id,
            seq=audio_metadata.seq,
            sample_index=audio_metadata.sample_index,
            capture_time_ns=audio_metadata.capture_time_ns,
            frame_count=audio_metadata.frame_count,
            format=audio_metadata.to_audio_format(),
            payload=payload_bytes,
        )
    except ValueError as exc:
        raise DoraAudioMetadataError(
            "DORA audio payload and metadata did not validate as AudioChunk"
        ) from exc


def validate_dora_audio_final_marker(
    payload: DoraAudioPayloadInput, metadata: DoraAudioMetadataInput
) -> DoraAudioMetadata:
    """Validate an explicit DORA audio final marker."""

    payload_bytes = _decode_dora_audio_payload(payload)
    audio_metadata = validate_dora_audio_metadata(metadata)
    if not audio_metadata.final:
        raise DoraAudioMetadataError("DORA audio metadata is not a final marker")
    if payload_bytes != b"":
        raise DoraAudioMetadataError("DORA final audio marker payload must be empty")
    return audio_metadata


def _decode_dora_audio_payload(payload: DoraAudioPayloadInput) -> bytes:
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, pa.UInt8Array):
        if payload.null_count != 0:
            raise DoraAudioMetadataError("DORA audio payload must not contain null samples")
        return bytes(payload.to_pylist())
    payload_type = type(payload)
    raise DoraAudioMetadataError(
        f"DORA audio payload must be bytes or uint8 Arrow array, got "
        f"{payload_type.__module__}.{payload_type.__name__}"
    )


def _encode_dora_audio_payload(payload: bytes) -> DoraAudioEncodedPayload:
    return pa.array(payload, type=pa.uint8())


def _extract_dora_audio_metadata(metadata: DoraMetadataMapping) -> DoraMetadataMutableMapping:
    missing_fields = [field for field in DORA_AUDIO_METADATA_FIELDS if field not in metadata]
    if missing_fields:
        missing = ", ".join(missing_fields)
        raise DoraAudioMetadataError(
            f"DORA audio metadata is invalid: missing required keys: {missing}"
        )
    return {field: metadata[field] for field in DORA_AUDIO_METADATA_FIELDS}
