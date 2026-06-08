"""Typed DORA metadata helpers for streaming transcript events."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal, Self, TypeAlias

import pyarrow as pa
from pydantic import BaseModel, ConfigDict, Field, model_validator

from fluent_audio.contracts import TranscriptDelta, TranscriptFinal
from fluent_audio.dora.audio import DoraMetadataMapping, DoraMetadataMutableMapping

TranscriptEvent: TypeAlias = TranscriptDelta | TranscriptFinal
DoraTranscriptKind: TypeAlias = Literal["delta", "final", "stream_final"]
DoraTranscriptPayloadInput: TypeAlias = bytes | pa.UInt8Array
DoraTranscriptEncodedPayload: TypeAlias = pa.UInt8Array

DORA_TRANSCRIPT_METADATA_FIELDS: tuple[str, ...] = (
    "kind",
    "session_id",
    "user_turn_id",
    "stream_id",
    "seq",
    "start_sample_index",
    "end_sample_index",
)


class DoraTranscriptMetadataError(ValueError):
    """Raised when DORA transcript metadata cannot validate an event."""


class DoraTranscriptStreamFinalMarkerError(DoraTranscriptMetadataError):
    """Raised when a DORA transcript stream marker is decoded as a transcript."""


class DoraTranscriptMetadata(BaseModel):
    """Flat DORA metadata needed to reconstruct one transcript event."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    kind: DoraTranscriptKind
    session_id: str = Field(min_length=1)
    user_turn_id: str
    stream_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    start_sample_index: int = Field(ge=0)
    end_sample_index: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_kind_fields(self) -> Self:
        if self.kind == "delta":
            if self.user_turn_id == "":
                raise ValueError("DORA transcript delta requires non-empty user_turn_id")
            if self.start_sample_index != 0:
                raise ValueError(
                    "DORA transcript delta metadata must have start_sample_index=0"
                )
            if self.end_sample_index != 0:
                raise ValueError(
                    "DORA transcript delta metadata must have end_sample_index=0"
                )
        elif self.kind == "final":
            if self.user_turn_id == "":
                raise ValueError("DORA transcript final requires non-empty user_turn_id")
            if self.end_sample_index <= self.start_sample_index:
                raise ValueError(
                    "DORA transcript final requires end_sample_index > "
                    "start_sample_index"
                )
        elif self.kind == "stream_final":
            if self.user_turn_id != "":
                raise ValueError(
                    "DORA transcript stream final marker must have empty user_turn_id"
                )
            if self.end_sample_index != self.start_sample_index:
                raise ValueError(
                    "DORA transcript stream final marker requires "
                    "end_sample_index == start_sample_index"
                )
        return self

    def to_dora_metadata(self) -> DoraMetadataMutableMapping:
        return {
            "kind": self.kind,
            "session_id": self.session_id,
            "user_turn_id": self.user_turn_id,
            "stream_id": self.stream_id,
            "seq": self.seq,
            "start_sample_index": self.start_sample_index,
            "end_sample_index": self.end_sample_index,
        }


DoraTranscriptMetadataInput: TypeAlias = (
    DoraMetadataMapping | DoraTranscriptMetadata | None
)


def encode_transcript_delta_for_dora(
    event: TranscriptDelta,
) -> tuple[DoraTranscriptEncodedPayload, DoraTranscriptMetadata]:
    """Encode a transcript delta as UTF-8 DORA payload plus metadata."""

    return (
        _encode_dora_transcript_payload(event.text),
        DoraTranscriptMetadata(
            kind="delta",
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            stream_id=event.stream_id,
            seq=event.seq,
            start_sample_index=0,
            end_sample_index=0,
        ),
    )


def encode_transcript_final_for_dora(
    event: TranscriptFinal,
) -> tuple[DoraTranscriptEncodedPayload, DoraTranscriptMetadata]:
    """Encode a final transcript as UTF-8 DORA payload plus metadata."""

    return (
        _encode_dora_transcript_payload(event.text),
        DoraTranscriptMetadata(
            kind="final",
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            stream_id=event.stream_id,
            seq=event.seq,
            start_sample_index=event.start_sample_index,
            end_sample_index=event.end_sample_index,
        ),
    )


def encode_transcript_stream_final_marker_for_dora(
    *,
    session_id: str,
    stream_id: str,
    seq: int,
    sample_index: int,
) -> tuple[DoraTranscriptEncodedPayload, DoraTranscriptMetadata]:
    """Encode explicit DORA transcript stream completion."""

    return (
        _encode_empty_dora_transcript_payload(),
        DoraTranscriptMetadata(
            kind="stream_final",
            session_id=session_id,
            user_turn_id="",
            stream_id=stream_id,
            seq=seq,
            start_sample_index=sample_index,
            end_sample_index=sample_index,
        ),
    )


def validate_dora_transcript_metadata(
    metadata: DoraTranscriptMetadataInput,
) -> DoraTranscriptMetadata:
    """Validate DORA transcript metadata at the boundary."""

    if metadata is None:
        raise DoraTranscriptMetadataError("DORA transcript metadata is required")
    if isinstance(metadata, DoraTranscriptMetadata):
        return metadata
    if not isinstance(metadata, Mapping):
        raise DoraTranscriptMetadataError("DORA transcript metadata is invalid")

    extracted_metadata = _extract_dora_transcript_metadata(metadata)
    try:
        return DoraTranscriptMetadata.model_validate(extracted_metadata)
    except ValueError as exc:
        raise DoraTranscriptMetadataError(
            "DORA transcript metadata is invalid"
        ) from exc


def decode_transcript_delta_from_dora(
    payload: DoraTranscriptPayloadInput,
    metadata: DoraTranscriptMetadataInput,
) -> TranscriptDelta:
    """Decode DORA payload and metadata into a validated transcript delta."""

    transcript_metadata = validate_dora_transcript_metadata(metadata)
    if transcript_metadata.kind == "stream_final":
        raise DoraTranscriptStreamFinalMarkerError(
            "DORA transcript stream final marker is not a TranscriptDelta"
        )
    if transcript_metadata.kind != "delta":
        raise DoraTranscriptMetadataError(
            "DORA transcript metadata is not a transcript delta"
        )
    text = _decode_dora_transcript_payload(payload, require_text=True)
    try:
        return TranscriptDelta(
            session_id=transcript_metadata.session_id,
            user_turn_id=transcript_metadata.user_turn_id,
            stream_id=transcript_metadata.stream_id,
            seq=transcript_metadata.seq,
            text=text,
        )
    except ValueError as exc:
        raise DoraTranscriptMetadataError(
            "DORA transcript metadata did not validate as TranscriptDelta"
        ) from exc


def decode_transcript_final_from_dora(
    payload: DoraTranscriptPayloadInput,
    metadata: DoraTranscriptMetadataInput,
) -> TranscriptFinal:
    """Decode DORA payload and metadata into a validated final transcript."""

    transcript_metadata = validate_dora_transcript_metadata(metadata)
    if transcript_metadata.kind == "stream_final":
        raise DoraTranscriptStreamFinalMarkerError(
            "DORA transcript stream final marker is not a TranscriptFinal"
        )
    if transcript_metadata.kind != "final":
        raise DoraTranscriptMetadataError(
            "DORA transcript metadata is not a transcript final"
        )
    text = _decode_dora_transcript_payload(payload, require_text=True)
    try:
        return TranscriptFinal(
            session_id=transcript_metadata.session_id,
            user_turn_id=transcript_metadata.user_turn_id,
            stream_id=transcript_metadata.stream_id,
            seq=transcript_metadata.seq,
            text=text,
            start_sample_index=transcript_metadata.start_sample_index,
            end_sample_index=transcript_metadata.end_sample_index,
        )
    except ValueError as exc:
        raise DoraTranscriptMetadataError(
            "DORA transcript metadata did not validate as TranscriptFinal"
        ) from exc


def validate_dora_transcript_stream_final_marker(
    payload: DoraTranscriptPayloadInput,
    metadata: DoraTranscriptMetadataInput,
) -> DoraTranscriptMetadata:
    """Validate an explicit DORA transcript stream final marker."""

    transcript_metadata = validate_dora_transcript_metadata(metadata)
    if transcript_metadata.kind != "stream_final":
        raise DoraTranscriptMetadataError(
            "DORA transcript metadata is not a stream final marker"
        )
    _decode_dora_transcript_payload(payload, require_text=False)
    return transcript_metadata


def _decode_dora_transcript_payload(
    payload: DoraTranscriptPayloadInput,
    *,
    require_text: bool,
) -> str:
    payload_bytes = _decode_dora_transcript_payload_bytes(payload)
    if not payload_bytes:
        if require_text:
            raise DoraTranscriptMetadataError("DORA transcript payload must not be empty")
        return ""
    try:
        text = payload_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DoraTranscriptMetadataError(
            "DORA transcript payload must be valid UTF-8"
        ) from exc
    return text


def _decode_dora_transcript_payload_bytes(
    payload: DoraTranscriptPayloadInput,
) -> bytes:
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, pa.UInt8Array):
        if payload.null_count != 0:
            raise DoraTranscriptMetadataError(
                "DORA transcript payload must not contain null values"
            )
        return bytes(payload.to_pylist())
    payload_type = type(payload)
    raise DoraTranscriptMetadataError(
        f"DORA transcript payload must be bytes or uint8 Arrow array, got "
        f"{payload_type.__module__}.{payload_type.__name__}"
    )


def _encode_dora_transcript_payload(text: str) -> DoraTranscriptEncodedPayload:
    return pa.array(text.encode("utf-8"), type=pa.uint8())


def _encode_empty_dora_transcript_payload() -> DoraTranscriptEncodedPayload:
    return pa.array([], type=pa.uint8())


def _extract_dora_transcript_metadata(
    metadata: DoraMetadataMapping,
) -> DoraMetadataMutableMapping:
    missing_fields = [
        field for field in DORA_TRANSCRIPT_METADATA_FIELDS if field not in metadata
    ]
    if missing_fields:
        missing = ", ".join(missing_fields)
        raise DoraTranscriptMetadataError(
            "DORA transcript metadata is invalid: "
            f"missing required keys: {missing}"
        )
    return {field: metadata[field] for field in DORA_TRANSCRIPT_METADATA_FIELDS}
