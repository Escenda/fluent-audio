"""Typed DORA metadata helpers for voice activity events."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Self, TypeAlias

import pyarrow as pa
from pydantic import BaseModel, ConfigDict, Field, model_validator

from fluent_audio.contracts import VoiceActivityEvent, VoiceActivityState
from fluent_audio.dora.audio import DoraMetadataMapping, DoraMetadataMutableMapping

DoraVoiceActivityPayloadInput: TypeAlias = bytes | pa.UInt8Array
DoraVoiceActivityEncodedPayload: TypeAlias = pa.UInt8Array

DORA_VOICE_ACTIVITY_METADATA_FIELDS: tuple[str, ...] = (
    "source_id",
    "stream_id",
    "seq",
    "sample_index",
    "frame_count",
    "state",
    "speech_probability",
    "final",
)


class DoraVoiceActivityMetadataError(ValueError):
    """Raised when DORA voice activity metadata cannot validate an event."""


class DoraVoiceActivityFinalMarkerError(DoraVoiceActivityMetadataError):
    """Raised when a DORA final marker is decoded as a voice activity event."""


class DoraVoiceActivityMetadata(BaseModel):
    """Flat DORA metadata needed to reconstruct a ``VoiceActivityEvent``."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    source_id: str = Field(min_length=1)
    stream_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    sample_index: int = Field(ge=0)
    frame_count: int = Field(ge=0)
    state: VoiceActivityState
    speech_probability: float = Field(ge=0.0, le=1.0)
    final: bool

    @model_validator(mode="after")
    def validate_final_marker(self) -> Self:
        if self.final:
            if self.frame_count != 0:
                raise ValueError("DORA voice activity final marker must have frame_count=0")
            if self.state != "silence":
                raise ValueError("DORA voice activity final marker must have state='silence'")
            if self.speech_probability != 0.0:
                raise ValueError(
                    "DORA voice activity final marker must have speech_probability=0.0"
                )
        elif self.frame_count == 0:
            raise ValueError("DORA voice activity event metadata must have frame_count > 0")
        return self

    def to_dora_metadata(self) -> DoraMetadataMutableMapping:
        return {
            "source_id": self.source_id,
            "stream_id": self.stream_id,
            "seq": self.seq,
            "sample_index": self.sample_index,
            "frame_count": self.frame_count,
            "state": self.state,
            "speech_probability": self.speech_probability,
            "final": self.final,
        }


DoraVoiceActivityMetadataInput: TypeAlias = (
    DoraMetadataMapping | DoraVoiceActivityMetadata | None
)


def encode_voice_activity_event_for_dora(
    event: VoiceActivityEvent,
) -> tuple[DoraVoiceActivityEncodedPayload, DoraVoiceActivityMetadata]:
    """Encode a ``VoiceActivityEvent`` as an empty DORA payload plus flat metadata."""

    return (
        _encode_empty_dora_voice_activity_payload(),
        DoraVoiceActivityMetadata(
            source_id=event.source_id,
            stream_id=event.stream_id,
            seq=event.seq,
            sample_index=event.sample_index,
            frame_count=event.frame_count,
            state=event.state,
            speech_probability=event.speech_probability,
            final=False,
        ),
    )


def encode_voice_activity_final_marker_for_dora(
    *,
    source_id: str,
    stream_id: str,
    seq: int,
    sample_index: int,
) -> tuple[DoraVoiceActivityEncodedPayload, DoraVoiceActivityMetadata]:
    """Encode explicit source completion for the DORA voice activity boundary."""

    return (
        _encode_empty_dora_voice_activity_payload(),
        DoraVoiceActivityMetadata(
            source_id=source_id,
            stream_id=stream_id,
            seq=seq,
            sample_index=sample_index,
            frame_count=0,
            state="silence",
            speech_probability=0.0,
            final=True,
        ),
    )


def validate_dora_voice_activity_metadata(
    metadata: DoraVoiceActivityMetadataInput,
) -> DoraVoiceActivityMetadata:
    """Validate DORA voice activity metadata at the boundary."""

    if metadata is None:
        raise DoraVoiceActivityMetadataError("DORA voice activity metadata is required")
    if isinstance(metadata, DoraVoiceActivityMetadata):
        return metadata
    if not isinstance(metadata, Mapping):
        raise DoraVoiceActivityMetadataError("DORA voice activity metadata is invalid")

    extracted_metadata = _extract_dora_voice_activity_metadata(metadata)
    try:
        return DoraVoiceActivityMetadata.model_validate(extracted_metadata)
    except ValueError as exc:
        raise DoraVoiceActivityMetadataError(
            "DORA voice activity metadata is invalid"
        ) from exc


def decode_voice_activity_event_from_dora(
    payload: DoraVoiceActivityPayloadInput,
    metadata: DoraVoiceActivityMetadataInput,
) -> VoiceActivityEvent:
    """Decode DORA payload and metadata into a validated ``VoiceActivityEvent``."""

    _validate_empty_dora_voice_activity_payload(payload)
    activity_metadata = validate_dora_voice_activity_metadata(metadata)
    if activity_metadata.final:
        raise DoraVoiceActivityFinalMarkerError(
            "DORA voice activity final marker is not a VoiceActivityEvent"
        )
    try:
        return VoiceActivityEvent(
            source_id=activity_metadata.source_id,
            stream_id=activity_metadata.stream_id,
            seq=activity_metadata.seq,
            sample_index=activity_metadata.sample_index,
            frame_count=activity_metadata.frame_count,
            state=activity_metadata.state,
            speech_probability=activity_metadata.speech_probability,
        )
    except ValueError as exc:
        raise DoraVoiceActivityMetadataError(
            "DORA voice activity metadata did not validate as VoiceActivityEvent"
        ) from exc


def validate_dora_voice_activity_final_marker(
    payload: DoraVoiceActivityPayloadInput,
    metadata: DoraVoiceActivityMetadataInput,
) -> DoraVoiceActivityMetadata:
    """Validate an explicit DORA voice activity final marker."""

    _validate_empty_dora_voice_activity_payload(payload)
    activity_metadata = validate_dora_voice_activity_metadata(metadata)
    if not activity_metadata.final:
        raise DoraVoiceActivityMetadataError(
            "DORA voice activity metadata is not a final marker"
        )
    return activity_metadata


def _validate_empty_dora_voice_activity_payload(
    payload: DoraVoiceActivityPayloadInput,
) -> None:
    if isinstance(payload, bytes):
        if payload != b"":
            raise DoraVoiceActivityMetadataError(
                "DORA voice activity payload must be empty"
            )
        return
    if isinstance(payload, pa.UInt8Array):
        if payload.null_count != 0:
            raise DoraVoiceActivityMetadataError(
                "DORA voice activity payload must not contain null values"
            )
        if len(payload) != 0:
            raise DoraVoiceActivityMetadataError(
                "DORA voice activity payload must be empty"
            )
        return
    payload_type = type(payload)
    raise DoraVoiceActivityMetadataError(
        f"DORA voice activity payload must be bytes or uint8 Arrow array, got "
        f"{payload_type.__module__}.{payload_type.__name__}"
    )


def _encode_empty_dora_voice_activity_payload() -> DoraVoiceActivityEncodedPayload:
    return pa.array([], type=pa.uint8())


def _extract_dora_voice_activity_metadata(
    metadata: DoraMetadataMapping,
) -> DoraMetadataMutableMapping:
    missing_fields = [
        field for field in DORA_VOICE_ACTIVITY_METADATA_FIELDS if field not in metadata
    ]
    if missing_fields:
        missing = ", ".join(missing_fields)
        raise DoraVoiceActivityMetadataError(
            "DORA voice activity metadata is invalid: "
            f"missing required keys: {missing}"
        )
    return {field: metadata[field] for field in DORA_VOICE_ACTIVITY_METADATA_FIELDS}
