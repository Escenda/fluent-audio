"""DORA protobuf helpers for streaming transcript events."""

from __future__ import annotations

from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field

from fluent_audio.contracts import TranscriptDelta, TranscriptFinal, TranscriptPartial
from fluent_audio.dora.protobuf import (
    DoraMetadataMapping,
    DoraProtobufEncodedPayload,
    DoraProtobufMetadata,
    DoraProtobufPayloadInput,
    decode_proto_message_from_dora,
    encode_proto_message_for_dora,
    validate_dora_protobuf_metadata,
)
from fluent_audio_contracts.fluent_audio.v1.asr_pb2 import (
    TranscriptDelta as PbTranscriptDelta,
    TranscriptFinal as PbTranscriptFinal,
    TranscriptPartial as PbTranscriptPartial,
    TranscriptStreamFinal,
)

TranscriptEvent: TypeAlias = TranscriptDelta | TranscriptFinal | TranscriptPartial
DoraTranscriptPayloadInput: TypeAlias = DoraProtobufPayloadInput
DoraTranscriptEncodedPayload: TypeAlias = DoraProtobufEncodedPayload
DoraTranscriptMetadata: TypeAlias = DoraProtobufMetadata


class DoraTranscriptMetadataError(ValueError):
    """Raised when DORA transcript protobuf payloads cannot validate."""


class DoraTranscriptStreamFinalMarkerError(DoraTranscriptMetadataError):
    """Raised when a DORA transcript stream marker is decoded as a transcript."""


class DoraTranscriptStreamFinalMarker(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: str = Field(min_length=1)
    stream_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    start_sample_index: int = Field(ge=0)
    end_sample_index: int = Field(ge=0)


def encode_transcript_delta_for_dora(
    event: TranscriptDelta,
) -> tuple[DoraTranscriptEncodedPayload, DoraTranscriptMetadata]:
    return encode_proto_message_for_dora(
        PbTranscriptDelta(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            stream_id=event.stream_id,
            seq=event.seq,
            text=event.text,
        )
    )


def encode_transcript_partial_for_dora(
    event: TranscriptPartial,
) -> tuple[DoraTranscriptEncodedPayload, DoraTranscriptMetadata]:
    return encode_proto_message_for_dora(
        PbTranscriptPartial(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            stream_id=event.stream_id,
            seq=event.seq,
            text=event.text,
        )
    )


def encode_transcript_final_for_dora(
    event: TranscriptFinal,
) -> tuple[DoraTranscriptEncodedPayload, DoraTranscriptMetadata]:
    return encode_proto_message_for_dora(
        PbTranscriptFinal(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            stream_id=event.stream_id,
            seq=event.seq,
            text=event.text,
            start_sample_index=event.start_sample_index,
            end_sample_index=event.end_sample_index,
        )
    )


def encode_transcript_stream_final_marker_for_dora(
    *,
    session_id: str,
    stream_id: str,
    seq: int,
    sample_index: int,
) -> tuple[DoraTranscriptEncodedPayload, DoraTranscriptMetadata]:
    return encode_proto_message_for_dora(
        TranscriptStreamFinal(
            session_id=session_id,
            stream_id=stream_id,
            seq=seq,
            sample_index=sample_index,
        )
    )


def validate_dora_transcript_metadata(
    metadata: DoraMetadataMapping | DoraTranscriptMetadata | None,
) -> DoraTranscriptMetadata:
    try:
        protobuf_metadata = validate_dora_protobuf_metadata(metadata)
    except ValueError as exc:
        raise DoraTranscriptMetadataError("DORA transcript metadata is invalid") from exc
    if protobuf_metadata.message_type not in (
        PbTranscriptDelta.DESCRIPTOR.full_name,
        PbTranscriptPartial.DESCRIPTOR.full_name,
        PbTranscriptFinal.DESCRIPTOR.full_name,
        TranscriptStreamFinal.DESCRIPTOR.full_name,
    ):
        raise DoraTranscriptMetadataError(
            f"DORA transcript metadata message type is invalid: {protobuf_metadata.message_type!r}"
        )
    return protobuf_metadata


def decode_transcript_delta_from_dora(
    payload: DoraTranscriptPayloadInput,
    metadata: DoraMetadataMapping | DoraTranscriptMetadata | None,
) -> TranscriptDelta:
    transcript_metadata = validate_dora_transcript_metadata(metadata)
    if transcript_metadata.message_type == TranscriptStreamFinal.DESCRIPTOR.full_name:
        raise DoraTranscriptStreamFinalMarkerError(
            "DORA transcript stream final marker is not a TranscriptDelta"
        )
    if transcript_metadata.message_type != PbTranscriptDelta.DESCRIPTOR.full_name:
        raise DoraTranscriptMetadataError("DORA transcript metadata is not a transcript delta")
    try:
        delta = decode_proto_message_from_dora(payload, transcript_metadata, PbTranscriptDelta)
        return TranscriptDelta(
            session_id=delta.session_id,
            user_turn_id=delta.user_turn_id,
            stream_id=delta.stream_id,
            seq=delta.seq,
            text=delta.text,
        )
    except ValueError as exc:
        raise DoraTranscriptMetadataError(
            "DORA transcript protobuf did not validate as TranscriptDelta"
        ) from exc


def decode_transcript_final_from_dora(
    payload: DoraTranscriptPayloadInput,
    metadata: DoraMetadataMapping | DoraTranscriptMetadata | None,
) -> TranscriptFinal:
    transcript_metadata = validate_dora_transcript_metadata(metadata)
    if transcript_metadata.message_type == TranscriptStreamFinal.DESCRIPTOR.full_name:
        raise DoraTranscriptStreamFinalMarkerError(
            "DORA transcript stream final marker is not a TranscriptFinal"
        )
    if transcript_metadata.message_type != PbTranscriptFinal.DESCRIPTOR.full_name:
        raise DoraTranscriptMetadataError("DORA transcript metadata is not a transcript final")
    try:
        final = decode_proto_message_from_dora(payload, transcript_metadata, PbTranscriptFinal)
        return TranscriptFinal(
            session_id=final.session_id,
            user_turn_id=final.user_turn_id,
            stream_id=final.stream_id,
            seq=final.seq,
            text=final.text,
            start_sample_index=final.start_sample_index,
            end_sample_index=final.end_sample_index,
        )
    except ValueError as exc:
        raise DoraTranscriptMetadataError(
            "DORA transcript protobuf did not validate as TranscriptFinal"
        ) from exc


def decode_transcript_partial_from_dora(
    payload: DoraTranscriptPayloadInput,
    metadata: DoraMetadataMapping | DoraTranscriptMetadata | None,
) -> TranscriptPartial:
    transcript_metadata = validate_dora_transcript_metadata(metadata)
    if transcript_metadata.message_type == TranscriptStreamFinal.DESCRIPTOR.full_name:
        raise DoraTranscriptStreamFinalMarkerError(
            "DORA transcript stream final marker is not a TranscriptPartial"
        )
    if transcript_metadata.message_type != PbTranscriptPartial.DESCRIPTOR.full_name:
        raise DoraTranscriptMetadataError("DORA transcript metadata is not a transcript partial")
    try:
        partial = decode_proto_message_from_dora(
            payload,
            transcript_metadata,
            PbTranscriptPartial,
        )
        return TranscriptPartial(
            session_id=partial.session_id,
            user_turn_id=partial.user_turn_id,
            stream_id=partial.stream_id,
            seq=partial.seq,
            text=partial.text,
        )
    except ValueError as exc:
        raise DoraTranscriptMetadataError(
            "DORA transcript protobuf did not validate as TranscriptPartial"
        ) from exc


def validate_dora_transcript_stream_final_marker(
    payload: DoraTranscriptPayloadInput,
    metadata: DoraMetadataMapping | DoraTranscriptMetadata | None,
) -> DoraTranscriptStreamFinalMarker:
    transcript_metadata = validate_dora_transcript_metadata(metadata)
    if transcript_metadata.message_type != TranscriptStreamFinal.DESCRIPTOR.full_name:
        raise DoraTranscriptMetadataError("DORA transcript metadata is not a stream final marker")
    try:
        final = decode_proto_message_from_dora(payload, transcript_metadata, TranscriptStreamFinal)
        return DoraTranscriptStreamFinalMarker(
            session_id=final.session_id,
            stream_id=final.stream_id,
            seq=final.seq,
            start_sample_index=final.sample_index,
            end_sample_index=final.sample_index,
        )
    except ValueError as exc:
        raise DoraTranscriptMetadataError(
            "DORA transcript protobuf did not validate as TranscriptStreamFinal"
        ) from exc
