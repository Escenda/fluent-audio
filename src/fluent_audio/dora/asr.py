"""DORA protobuf helpers for ASR control events."""

from __future__ import annotations

from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field

from fluent_audio.contracts import AsrCancel, AsrStart, AsrStop
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
    AsrCancel as PbAsrCancel,
    AsrControl,
    AsrControlStreamFinal,
    AsrStart as PbAsrStart,
    AsrStop as PbAsrStop,
)

AsrControlEvent: TypeAlias = AsrStart | AsrStop | AsrCancel
DoraAsrControlPayloadInput: TypeAlias = DoraProtobufPayloadInput
DoraAsrControlEncodedPayload: TypeAlias = DoraProtobufEncodedPayload
DoraAsrControlMetadata: TypeAlias = DoraProtobufMetadata


class DoraAsrControlMetadataError(ValueError):
    """Raised when DORA ASR control protobuf payloads cannot validate."""


class DoraAsrControlFinalMarkerError(ValueError):
    """Raised when a DORA ASR control final marker is decoded as a control."""


class DoraAsrControlFinalMarker(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: str = Field(min_length=1)
    stream_id: str = Field(min_length=1)
    seq: int = Field(ge=0)


def encode_asr_control_for_dora(
    control: AsrControlEvent,
) -> tuple[DoraAsrControlEncodedPayload, DoraAsrControlMetadata]:
    if isinstance(control, AsrStart):
        return encode_proto_message_for_dora(
            AsrControl(
                start=PbAsrStart(
                    session_id=control.session_id,
                    user_turn_id=control.user_turn_id,
                    stream_id=control.stream_id,
                    seq=control.seq,
                    start_sample_index=control.start_sample_index,
                )
            )
        )
    if isinstance(control, AsrStop):
        return encode_proto_message_for_dora(
            AsrControl(
                stop=PbAsrStop(
                    session_id=control.session_id,
                    user_turn_id=control.user_turn_id,
                    stream_id=control.stream_id,
                    seq=control.seq,
                    stop_sample_index=control.stop_sample_index,
                )
            )
        )
    if isinstance(control, AsrCancel):
        return encode_proto_message_for_dora(
            AsrControl(
                cancel=PbAsrCancel(
                    session_id=control.session_id,
                    user_turn_id=control.user_turn_id,
                    stream_id=control.stream_id,
                    seq=control.seq,
                    reason=control.reason,
                )
            )
        )
    control_type = type(control)
    raise DoraAsrControlMetadataError(
        "ASR control must be AsrStart, AsrStop, or AsrCancel, got "
        f"{control_type.__module__}.{control_type.__name__}"
    )


def encode_asr_control_final_marker_for_dora(
    *,
    session_id: str,
    stream_id: str,
    seq: int,
) -> tuple[DoraAsrControlEncodedPayload, DoraAsrControlMetadata]:
    return encode_proto_message_for_dora(
        AsrControlStreamFinal(session_id=session_id, stream_id=stream_id, seq=seq)
    )


def validate_dora_asr_control_metadata(
    metadata: DoraMetadataMapping | DoraAsrControlMetadata | None,
) -> DoraAsrControlMetadata:
    try:
        protobuf_metadata = validate_dora_protobuf_metadata(metadata)
    except ValueError as exc:
        raise DoraAsrControlMetadataError("DORA ASR control metadata is invalid") from exc
    if protobuf_metadata.message_type not in (
        AsrControl.DESCRIPTOR.full_name,
        AsrControlStreamFinal.DESCRIPTOR.full_name,
    ):
        raise DoraAsrControlMetadataError(
            "DORA ASR control metadata message type is invalid: "
            f"{protobuf_metadata.message_type!r}"
        )
    return protobuf_metadata


def decode_asr_control_from_dora(
    payload: DoraAsrControlPayloadInput,
    metadata: DoraMetadataMapping | DoraAsrControlMetadata | None,
) -> AsrControlEvent:
    asr_metadata = validate_dora_asr_control_metadata(metadata)
    if asr_metadata.message_type == AsrControlStreamFinal.DESCRIPTOR.full_name:
        raise DoraAsrControlFinalMarkerError(
            "DORA ASR control final marker is not an ASR control command"
        )
    try:
        control = decode_proto_message_from_dora(payload, asr_metadata, AsrControl)
        control_variant = control.WhichOneof("control")
        if control_variant == "start":
            start = control.start
            return AsrStart(
                action="start",
                session_id=start.session_id,
                user_turn_id=start.user_turn_id,
                stream_id=start.stream_id,
                seq=start.seq,
                start_sample_index=start.start_sample_index,
            )
        if control_variant == "stop":
            stop = control.stop
            return AsrStop(
                action="stop",
                session_id=stop.session_id,
                user_turn_id=stop.user_turn_id,
                stream_id=stop.stream_id,
                seq=stop.seq,
                stop_sample_index=stop.stop_sample_index,
            )
        if control_variant == "cancel":
            cancel = control.cancel
            return AsrCancel(
                action="cancel",
                session_id=cancel.session_id,
                user_turn_id=cancel.user_turn_id,
                stream_id=cancel.stream_id,
                seq=cancel.seq,
                reason=cancel.reason,
            )
    except ValueError as exc:
        raise DoraAsrControlMetadataError(
            "DORA ASR control protobuf did not validate as an ASR control command"
        ) from exc
    raise DoraAsrControlMetadataError("DORA ASR control protobuf is missing oneof control")


def validate_dora_asr_control_final_marker(
    payload: DoraAsrControlPayloadInput,
    metadata: DoraMetadataMapping | DoraAsrControlMetadata | None,
) -> DoraAsrControlFinalMarker:
    asr_metadata = validate_dora_asr_control_metadata(metadata)
    if asr_metadata.message_type != AsrControlStreamFinal.DESCRIPTOR.full_name:
        raise DoraAsrControlMetadataError("DORA ASR control metadata is not a final marker")
    try:
        final = decode_proto_message_from_dora(payload, asr_metadata, AsrControlStreamFinal)
        return DoraAsrControlFinalMarker(
            session_id=final.session_id,
            stream_id=final.stream_id,
            seq=final.seq,
        )
    except ValueError as exc:
        raise DoraAsrControlMetadataError(
            "DORA ASR control protobuf did not validate as AsrControlStreamFinal"
        ) from exc
