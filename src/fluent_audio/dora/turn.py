"""DORA protobuf helpers for turn boundary events."""

from __future__ import annotations

from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field

from fluent_audio.contracts import TurnEvent, TurnState
from fluent_audio.dora.protobuf import (
    DoraMetadataMapping,
    DoraProtobufEncodedPayload,
    DoraProtobufMetadata,
    DoraProtobufPayloadInput,
    decode_proto_message_from_dora,
    encode_proto_message_for_dora,
    validate_dora_protobuf_metadata,
)
from fluent_audio_contracts.fluent_audio.v1.vad_pb2 import (
    TURN_STATE_ACTIVE,
    TURN_STATE_CANCELLED,
    TURN_STATE_ENDED,
    TURN_STATE_IDLE,
    TURN_STATE_STARTED,
    TurnEvent as PbTurnEvent,
    TurnStreamFinal,
)

DoraTurnPayloadInput: TypeAlias = DoraProtobufPayloadInput
DoraTurnEncodedPayload: TypeAlias = DoraProtobufEncodedPayload
DoraTurnMetadata: TypeAlias = DoraProtobufMetadata


class DoraTurnMetadataError(ValueError):
    """Raised when DORA turn protobuf payloads cannot validate."""


class DoraTurnFinalMarkerError(DoraTurnMetadataError):
    """Raised when a DORA final marker is decoded as a turn event."""


class DoraTurnFinalMarker(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: str = Field(min_length=1)
    stream_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    sample_index: int = Field(ge=0)


def encode_turn_event_for_dora(
    event: TurnEvent,
) -> tuple[DoraTurnEncodedPayload, DoraTurnMetadata]:
    proto_event = PbTurnEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        stream_id=event.stream_id,
        seq=event.seq,
        sample_index=event.sample_index,
        state=_turn_state_to_proto(event.state),
    )
    if event.confidence is not None:
        proto_event.confidence = event.confidence
    return encode_proto_message_for_dora(proto_event)


def encode_turn_final_marker_for_dora(
    session_id: str,
    stream_id: str,
    seq: int,
    sample_index: int,
) -> tuple[DoraTurnEncodedPayload, DoraTurnMetadata]:
    return encode_proto_message_for_dora(
        TurnStreamFinal(
            session_id=session_id,
            stream_id=stream_id,
            seq=seq,
            sample_index=sample_index,
        )
    )


def validate_dora_turn_metadata(
    metadata: DoraMetadataMapping | DoraTurnMetadata | None,
) -> DoraTurnMetadata:
    try:
        protobuf_metadata = validate_dora_protobuf_metadata(metadata)
    except ValueError as exc:
        raise DoraTurnMetadataError("DORA turn metadata is invalid") from exc
    if protobuf_metadata.message_type not in (
        PbTurnEvent.DESCRIPTOR.full_name,
        TurnStreamFinal.DESCRIPTOR.full_name,
    ):
        raise DoraTurnMetadataError(
            "DORA turn metadata message type is invalid: "
            f"{protobuf_metadata.message_type!r}"
        )
    return protobuf_metadata


def decode_turn_event_from_dora(
    payload: DoraTurnPayloadInput,
    metadata: DoraMetadataMapping | DoraTurnMetadata | None,
) -> TurnEvent:
    turn_metadata = validate_dora_turn_metadata(metadata)
    if turn_metadata.message_type == TurnStreamFinal.DESCRIPTOR.full_name:
        raise DoraTurnFinalMarkerError("DORA turn final marker is not a TurnEvent")
    try:
        event = decode_proto_message_from_dora(payload, turn_metadata, PbTurnEvent)
        confidence = event.confidence if event.HasField("confidence") else None
        return TurnEvent(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            stream_id=event.stream_id,
            seq=event.seq,
            sample_index=event.sample_index,
            state=_turn_state_from_proto(event.state),
            confidence=confidence,
        )
    except ValueError as exc:
        raise DoraTurnMetadataError(
            "DORA turn protobuf did not validate as TurnEvent"
        ) from exc


def validate_dora_turn_final_marker(
    payload: DoraTurnPayloadInput,
    metadata: DoraMetadataMapping | DoraTurnMetadata | None,
) -> DoraTurnFinalMarker:
    turn_metadata = validate_dora_turn_metadata(metadata)
    if turn_metadata.message_type != TurnStreamFinal.DESCRIPTOR.full_name:
        raise DoraTurnMetadataError("DORA turn metadata is not a final marker")
    try:
        final = decode_proto_message_from_dora(payload, turn_metadata, TurnStreamFinal)
        return DoraTurnFinalMarker(
            session_id=final.session_id,
            stream_id=final.stream_id,
            seq=final.seq,
            sample_index=final.sample_index,
        )
    except ValueError as exc:
        raise DoraTurnMetadataError(
            "DORA turn protobuf did not validate as TurnStreamFinal"
        ) from exc


def _turn_state_to_proto(state: TurnState) -> int:
    if state == "idle":
        return TURN_STATE_IDLE
    if state == "started":
        return TURN_STATE_STARTED
    if state == "active":
        return TURN_STATE_ACTIVE
    if state == "ended":
        return TURN_STATE_ENDED
    if state == "cancelled":
        return TURN_STATE_CANCELLED
    raise DoraTurnMetadataError(f"Unsupported turn state: {state!r}")


def _turn_state_from_proto(state: int) -> TurnState:
    if state == TURN_STATE_IDLE:
        return "idle"
    if state == TURN_STATE_STARTED:
        return "started"
    if state == TURN_STATE_ACTIVE:
        return "active"
    if state == TURN_STATE_ENDED:
        return "ended"
    if state == TURN_STATE_CANCELLED:
        return "cancelled"
    raise DoraTurnMetadataError(f"Unsupported protobuf turn state: {state}")
