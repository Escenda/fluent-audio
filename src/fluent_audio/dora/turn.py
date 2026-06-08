"""Typed DORA metadata helpers for turn boundary events."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Self, TypeAlias

import pyarrow as pa
from pydantic import BaseModel, ConfigDict, Field, model_validator

from fluent_audio.contracts import TurnEvent, TurnState
from fluent_audio.dora.audio import DoraMetadataMapping, DoraMetadataMutableMapping

DoraTurnPayloadInput: TypeAlias = bytes | pa.UInt8Array
DoraTurnEncodedPayload: TypeAlias = pa.UInt8Array

DORA_TURN_METADATA_FIELDS: tuple[str, ...] = (
    "session_id",
    "user_turn_id",
    "stream_id",
    "seq",
    "sample_index",
    "state",
    "confidence_present",
    "confidence",
    "final",
)


class DoraTurnMetadataError(ValueError):
    """Raised when DORA turn metadata cannot validate an event."""


class DoraTurnFinalMarkerError(DoraTurnMetadataError):
    """Raised when a DORA final marker is decoded as a turn event."""


class DoraTurnMetadata(BaseModel):
    """Flat DORA metadata needed to reconstruct a ``TurnEvent``."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: str = Field(min_length=1)
    user_turn_id: str
    stream_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    sample_index: int = Field(ge=0)
    state: TurnState
    confidence_present: bool
    confidence: float = Field(ge=0.0, le=1.0)
    final: bool

    @model_validator(mode="after")
    def validate_final_marker(self) -> Self:
        if self.final:
            if self.user_turn_id != "":
                raise ValueError("DORA turn final marker must have empty user_turn_id")
            if self.state != "idle":
                raise ValueError("DORA turn final marker must have state='idle'")
            if self.confidence_present:
                raise ValueError(
                    "DORA turn final marker must have confidence_present=false"
                )
            if self.confidence != 0.0:
                raise ValueError("DORA turn final marker must have confidence=0.0")
        elif self.user_turn_id == "":
            raise ValueError("DORA turn event metadata must have non-empty user_turn_id")

        if not self.confidence_present and self.confidence != 0.0:
            raise ValueError(
                "DORA turn metadata must have confidence=0.0 when "
                "confidence_present=false"
            )
        return self

    def to_dora_metadata(self) -> DoraMetadataMutableMapping:
        return {
            "session_id": self.session_id,
            "user_turn_id": self.user_turn_id,
            "stream_id": self.stream_id,
            "seq": self.seq,
            "sample_index": self.sample_index,
            "state": self.state,
            "confidence_present": self.confidence_present,
            "confidence": self.confidence,
            "final": self.final,
        }


DoraTurnMetadataInput: TypeAlias = DoraMetadataMapping | DoraTurnMetadata | None


def encode_turn_event_for_dora(
    event: TurnEvent,
) -> tuple[DoraTurnEncodedPayload, DoraTurnMetadata]:
    """Encode a ``TurnEvent`` as an empty DORA payload plus flat metadata."""

    confidence_present = event.confidence is not None
    return (
        _encode_empty_dora_turn_payload(),
        DoraTurnMetadata(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            stream_id=event.stream_id,
            seq=event.seq,
            sample_index=event.sample_index,
            state=event.state,
            confidence_present=confidence_present,
            confidence=event.confidence if confidence_present else 0.0,
            final=False,
        ),
    )


def encode_turn_final_marker_for_dora(
    session_id: str,
    stream_id: str,
    seq: int,
    sample_index: int,
) -> tuple[DoraTurnEncodedPayload, DoraTurnMetadata]:
    """Encode explicit source completion for the DORA turn boundary."""

    return (
        _encode_empty_dora_turn_payload(),
        DoraTurnMetadata(
            session_id=session_id,
            user_turn_id="",
            stream_id=stream_id,
            seq=seq,
            sample_index=sample_index,
            state="idle",
            confidence_present=False,
            confidence=0.0,
            final=True,
        ),
    )


def validate_dora_turn_metadata(metadata: DoraTurnMetadataInput) -> DoraTurnMetadata:
    """Validate DORA turn metadata at the boundary."""

    if metadata is None:
        raise DoraTurnMetadataError("DORA turn metadata is required")
    if isinstance(metadata, DoraTurnMetadata):
        return metadata
    if not isinstance(metadata, Mapping):
        raise DoraTurnMetadataError("DORA turn metadata is invalid")

    extracted_metadata = _extract_dora_turn_metadata(metadata)
    try:
        return DoraTurnMetadata.model_validate(extracted_metadata)
    except ValueError as exc:
        raise DoraTurnMetadataError("DORA turn metadata is invalid") from exc


def decode_turn_event_from_dora(
    payload: DoraTurnPayloadInput,
    metadata: DoraTurnMetadataInput,
) -> TurnEvent:
    """Decode DORA payload and metadata into a validated ``TurnEvent``."""

    _validate_empty_dora_turn_payload(payload)
    turn_metadata = validate_dora_turn_metadata(metadata)
    if turn_metadata.final:
        raise DoraTurnFinalMarkerError("DORA turn final marker is not a TurnEvent")
    try:
        return TurnEvent(
            session_id=turn_metadata.session_id,
            user_turn_id=turn_metadata.user_turn_id,
            stream_id=turn_metadata.stream_id,
            seq=turn_metadata.seq,
            sample_index=turn_metadata.sample_index,
            state=turn_metadata.state,
            confidence=turn_metadata.confidence
            if turn_metadata.confidence_present
            else None,
        )
    except ValueError as exc:
        raise DoraTurnMetadataError(
            "DORA turn metadata did not validate as TurnEvent"
        ) from exc


def validate_dora_turn_final_marker(
    payload: DoraTurnPayloadInput,
    metadata: DoraTurnMetadataInput,
) -> DoraTurnMetadata:
    """Validate an explicit DORA turn final marker."""

    _validate_empty_dora_turn_payload(payload)
    turn_metadata = validate_dora_turn_metadata(metadata)
    if not turn_metadata.final:
        raise DoraTurnMetadataError("DORA turn metadata is not a final marker")
    return turn_metadata


def _validate_empty_dora_turn_payload(payload: DoraTurnPayloadInput) -> None:
    if isinstance(payload, bytes):
        if payload != b"":
            raise DoraTurnMetadataError("DORA turn payload must be empty")
        return
    if isinstance(payload, pa.UInt8Array):
        if payload.null_count != 0:
            raise DoraTurnMetadataError("DORA turn payload must not contain null values")
        if len(payload) != 0:
            raise DoraTurnMetadataError("DORA turn payload must be empty")
        return
    payload_type = type(payload)
    raise DoraTurnMetadataError(
        f"DORA turn payload must be bytes or uint8 Arrow array, got "
        f"{payload_type.__module__}.{payload_type.__name__}"
    )


def _encode_empty_dora_turn_payload() -> DoraTurnEncodedPayload:
    return pa.array([], type=pa.uint8())


def _extract_dora_turn_metadata(
    metadata: DoraMetadataMapping,
) -> DoraMetadataMutableMapping:
    missing_fields = [field for field in DORA_TURN_METADATA_FIELDS if field not in metadata]
    if missing_fields:
        missing = ", ".join(missing_fields)
        raise DoraTurnMetadataError(
            f"DORA turn metadata is invalid: missing required keys: {missing}"
        )
    return {field: metadata[field] for field in DORA_TURN_METADATA_FIELDS}
