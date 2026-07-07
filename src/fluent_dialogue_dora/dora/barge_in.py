"""DORA protobuf helpers for barge-in signal events."""

from __future__ import annotations

from typing import TypeAlias

from fluent_dialogue_dora.contracts import BargeInEvent, BargeInStreamFinal
from fluent_dialogue_dora.dora.protobuf import (
    DoraMetadataMapping,
    DoraProtobufEncodedPayload,
    DoraProtobufMetadata,
    DoraProtobufPayloadInput,
    decode_proto_message_from_dora,
    encode_proto_message_for_dora,
    validate_dora_protobuf_metadata,
)
from fluent_dialogue_dora_contracts.fluent_dialogue_dora.v1.barge_in_pb2 import (
    BargeInEvent as PbBargeInEvent,
    BargeInStreamFinal as PbBargeInStreamFinal,
)

DoraBargeInPayloadInput: TypeAlias = DoraProtobufPayloadInput
DoraBargeInEncodedPayload: TypeAlias = DoraProtobufEncodedPayload
DoraBargeInMetadata: TypeAlias = DoraProtobufMetadata


class DoraBargeInMetadataError(ValueError):
    """Raised when DORA barge-in protobuf payloads cannot validate."""


class DoraBargeInFinalMarkerError(DoraBargeInMetadataError):
    """Raised when a DORA final marker is decoded as a barge-in event."""


def encode_barge_in_event_for_dora(
    event: BargeInEvent,
) -> tuple[DoraBargeInEncodedPayload, DoraBargeInMetadata]:
    return encode_proto_message_for_dora(
        PbBargeInEvent(
            session_id=event.session_id,
            source_id=event.source_id,
            stream_id=event.stream_id,
            seq=event.seq,
            playback_request_id=event.playback_request_id,
            playback_stream_id=event.playback_stream_id,
            played_frames=event.played_frames,
            detected_sample_index=event.detected_sample_index,
            speech_probability=event.speech_probability,
        )
    )


def encode_barge_in_stream_final_for_dora(
    event: BargeInStreamFinal,
) -> tuple[DoraBargeInEncodedPayload, DoraBargeInMetadata]:
    return encode_proto_message_for_dora(
        PbBargeInStreamFinal(
            session_id=event.session_id,
            source_id=event.source_id,
            stream_id=event.stream_id,
            seq=event.seq,
        )
    )


def validate_dora_barge_in_metadata(
    metadata: DoraMetadataMapping | DoraBargeInMetadata | None,
) -> DoraBargeInMetadata:
    try:
        protobuf_metadata = validate_dora_protobuf_metadata(metadata)
    except ValueError as exc:
        raise DoraBargeInMetadataError("DORA barge-in metadata is invalid") from exc
    if protobuf_metadata.message_type not in (
        PbBargeInEvent.DESCRIPTOR.full_name,
        PbBargeInStreamFinal.DESCRIPTOR.full_name,
    ):
        raise DoraBargeInMetadataError(
            "DORA barge-in metadata message type is invalid: "
            f"{protobuf_metadata.message_type!r}"
        )
    return protobuf_metadata


def decode_barge_in_event_from_dora(
    payload: DoraBargeInPayloadInput,
    metadata: DoraMetadataMapping | DoraBargeInMetadata | None,
) -> BargeInEvent:
    barge_in_metadata = validate_dora_barge_in_metadata(metadata)
    if barge_in_metadata.message_type == PbBargeInStreamFinal.DESCRIPTOR.full_name:
        raise DoraBargeInFinalMarkerError("DORA barge-in final marker is not a BargeInEvent")
    try:
        event = decode_proto_message_from_dora(payload, barge_in_metadata, PbBargeInEvent)
        return BargeInEvent(
            session_id=event.session_id,
            source_id=event.source_id,
            stream_id=event.stream_id,
            seq=event.seq,
            playback_request_id=event.playback_request_id,
            playback_stream_id=event.playback_stream_id,
            played_frames=event.played_frames,
            detected_sample_index=event.detected_sample_index,
            speech_probability=event.speech_probability,
        )
    except ValueError as exc:
        raise DoraBargeInMetadataError(
            "DORA barge-in protobuf did not validate as BargeInEvent"
        ) from exc


def validate_dora_barge_in_final_marker(
    payload: DoraBargeInPayloadInput,
    metadata: DoraMetadataMapping | DoraBargeInMetadata | None,
) -> BargeInStreamFinal:
    barge_in_metadata = validate_dora_barge_in_metadata(metadata)
    if barge_in_metadata.message_type != PbBargeInStreamFinal.DESCRIPTOR.full_name:
        raise DoraBargeInMetadataError("DORA barge-in metadata is not a final marker")
    try:
        final = decode_proto_message_from_dora(payload, barge_in_metadata, PbBargeInStreamFinal)
        return BargeInStreamFinal(
            session_id=final.session_id,
            source_id=final.source_id,
            stream_id=final.stream_id,
            seq=final.seq,
        )
    except ValueError as exc:
        raise DoraBargeInMetadataError(
            "DORA barge-in protobuf did not validate as BargeInStreamFinal"
        ) from exc
