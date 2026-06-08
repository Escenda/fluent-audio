"""Typed DORA metadata helpers for ASR control events."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal, Self, TypeAlias

import pyarrow as pa
from pydantic import BaseModel, ConfigDict, Field, model_validator

from fluent_audio.contracts import AsrCancel, AsrStart, AsrStop
from fluent_audio.dora.audio import DoraMetadataMapping, DoraMetadataMutableMapping

AsrControlEvent: TypeAlias = AsrStart | AsrStop | AsrCancel
DoraAsrControlPayloadInput: TypeAlias = bytes | pa.UInt8Array
DoraAsrControlEncodedPayload: TypeAlias = pa.UInt8Array
DoraAsrControlAction: TypeAlias = Literal["start", "stop", "cancel"]

DORA_ASR_CONTROL_METADATA_FIELDS: tuple[str, ...] = (
    "action",
    "session_id",
    "user_turn_id",
    "stream_id",
    "seq",
    "start_sample_index",
    "stop_sample_index",
    "reason",
)


class DoraAsrControlMetadataError(ValueError):
    """Raised when DORA ASR control metadata cannot validate an event."""


class DoraAsrControlMetadata(BaseModel):
    """Flat DORA metadata needed to reconstruct one ASR control command."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    action: DoraAsrControlAction
    session_id: str = Field(min_length=1)
    user_turn_id: str = Field(min_length=1)
    stream_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    start_sample_index: int = Field(ge=0)
    stop_sample_index: int = Field(ge=0)
    reason: str

    @model_validator(mode="after")
    def validate_variant_fields(self) -> Self:
        if self.action == "start":
            if self.stop_sample_index != 0:
                raise ValueError("DORA ASR start metadata must have stop_sample_index=0")
            if self.reason != "":
                raise ValueError("DORA ASR start metadata must have empty reason")
        elif self.action == "stop":
            if self.start_sample_index != 0:
                raise ValueError("DORA ASR stop metadata must have start_sample_index=0")
            if self.reason != "":
                raise ValueError("DORA ASR stop metadata must have empty reason")
        elif self.action == "cancel":
            if self.start_sample_index != 0:
                raise ValueError("DORA ASR cancel metadata must have start_sample_index=0")
            if self.stop_sample_index != 0:
                raise ValueError("DORA ASR cancel metadata must have stop_sample_index=0")
            if self.reason == "":
                raise ValueError("DORA ASR cancel metadata must have non-empty reason")
        return self

    def to_dora_metadata(self) -> DoraMetadataMutableMapping:
        return {
            "action": self.action,
            "session_id": self.session_id,
            "user_turn_id": self.user_turn_id,
            "stream_id": self.stream_id,
            "seq": self.seq,
            "start_sample_index": self.start_sample_index,
            "stop_sample_index": self.stop_sample_index,
            "reason": self.reason,
        }


DoraAsrControlMetadataInput: TypeAlias = (
    DoraMetadataMapping | DoraAsrControlMetadata | None
)


def encode_asr_control_for_dora(
    control: AsrControlEvent,
) -> tuple[DoraAsrControlEncodedPayload, DoraAsrControlMetadata]:
    """Encode an ASR control command as an empty DORA payload plus metadata."""

    if isinstance(control, AsrStart):
        return (
            _encode_empty_dora_asr_control_payload(),
            DoraAsrControlMetadata(
                action="start",
                session_id=control.session_id,
                user_turn_id=control.user_turn_id,
                stream_id=control.stream_id,
                seq=control.seq,
                start_sample_index=control.start_sample_index,
                stop_sample_index=0,
                reason="",
            ),
        )
    if isinstance(control, AsrStop):
        return (
            _encode_empty_dora_asr_control_payload(),
            DoraAsrControlMetadata(
                action="stop",
                session_id=control.session_id,
                user_turn_id=control.user_turn_id,
                stream_id=control.stream_id,
                seq=control.seq,
                start_sample_index=0,
                stop_sample_index=control.stop_sample_index,
                reason="",
            ),
        )
    if isinstance(control, AsrCancel):
        return (
            _encode_empty_dora_asr_control_payload(),
            DoraAsrControlMetadata(
                action="cancel",
                session_id=control.session_id,
                user_turn_id=control.user_turn_id,
                stream_id=control.stream_id,
                seq=control.seq,
                start_sample_index=0,
                stop_sample_index=0,
                reason=control.reason,
            ),
        )
    control_type = type(control)
    raise DoraAsrControlMetadataError(
        "ASR control must be AsrStart, AsrStop, or AsrCancel, got "
        f"{control_type.__module__}.{control_type.__name__}"
    )


def validate_dora_asr_control_metadata(
    metadata: DoraAsrControlMetadataInput,
) -> DoraAsrControlMetadata:
    """Validate DORA ASR control metadata at the boundary."""

    if metadata is None:
        raise DoraAsrControlMetadataError("DORA ASR control metadata is required")
    if isinstance(metadata, DoraAsrControlMetadata):
        return metadata
    if not isinstance(metadata, Mapping):
        raise DoraAsrControlMetadataError("DORA ASR control metadata is invalid")

    extracted_metadata = _extract_dora_asr_control_metadata(metadata)
    try:
        return DoraAsrControlMetadata.model_validate(extracted_metadata)
    except ValueError as exc:
        raise DoraAsrControlMetadataError(
            "DORA ASR control metadata is invalid"
        ) from exc


def decode_asr_control_from_dora(
    payload: DoraAsrControlPayloadInput,
    metadata: DoraAsrControlMetadataInput,
) -> AsrControlEvent:
    """Decode DORA payload and metadata into a validated ASR control command."""

    _validate_empty_dora_asr_control_payload(payload)
    asr_metadata = validate_dora_asr_control_metadata(metadata)
    try:
        if asr_metadata.action == "start":
            return AsrStart(
                action="start",
                session_id=asr_metadata.session_id,
                user_turn_id=asr_metadata.user_turn_id,
                stream_id=asr_metadata.stream_id,
                seq=asr_metadata.seq,
                start_sample_index=asr_metadata.start_sample_index,
            )
        if asr_metadata.action == "stop":
            return AsrStop(
                action="stop",
                session_id=asr_metadata.session_id,
                user_turn_id=asr_metadata.user_turn_id,
                stream_id=asr_metadata.stream_id,
                seq=asr_metadata.seq,
                stop_sample_index=asr_metadata.stop_sample_index,
            )
        return AsrCancel(
            action="cancel",
            session_id=asr_metadata.session_id,
            user_turn_id=asr_metadata.user_turn_id,
            stream_id=asr_metadata.stream_id,
            seq=asr_metadata.seq,
            reason=asr_metadata.reason,
        )
    except ValueError as exc:
        raise DoraAsrControlMetadataError(
            "DORA ASR control metadata did not validate as an ASR control command"
        ) from exc


def _validate_empty_dora_asr_control_payload(
    payload: DoraAsrControlPayloadInput,
) -> None:
    if isinstance(payload, bytes):
        if payload != b"":
            raise DoraAsrControlMetadataError("DORA ASR control payload must be empty")
        return
    if isinstance(payload, pa.UInt8Array):
        if payload.null_count != 0:
            raise DoraAsrControlMetadataError(
                "DORA ASR control payload must not contain null values"
            )
        if len(payload) != 0:
            raise DoraAsrControlMetadataError("DORA ASR control payload must be empty")
        return
    payload_type = type(payload)
    raise DoraAsrControlMetadataError(
        f"DORA ASR control payload must be bytes or uint8 Arrow array, got "
        f"{payload_type.__module__}.{payload_type.__name__}"
    )


def _encode_empty_dora_asr_control_payload() -> DoraAsrControlEncodedPayload:
    return pa.array([], type=pa.uint8())


def _extract_dora_asr_control_metadata(
    metadata: DoraMetadataMapping,
) -> DoraMetadataMutableMapping:
    missing_fields = [
        field for field in DORA_ASR_CONTROL_METADATA_FIELDS if field not in metadata
    ]
    if missing_fields:
        missing = ", ".join(missing_fields)
        raise DoraAsrControlMetadataError(
            "DORA ASR control metadata is invalid: "
            f"missing required keys: {missing}"
        )
    return {field: metadata[field] for field in DORA_ASR_CONTROL_METADATA_FIELDS}
