"""DORA protobuf helpers for voice activity events."""

from __future__ import annotations

from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field

from fluent_audio.contracts import AudioLevelEvent, VoiceActivityEvent, VoiceActivityState
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
    AudioLevelEvent as PbAudioLevelEvent,
    VOICE_ACTIVITY_STATE_SILENCE,
    VOICE_ACTIVITY_STATE_SPEECH,
    VoiceActivityEvent as PbVoiceActivityEvent,
    VoiceActivityStreamFinal,
)

DoraVoiceActivityPayloadInput: TypeAlias = DoraProtobufPayloadInput
DoraVoiceActivityEncodedPayload: TypeAlias = DoraProtobufEncodedPayload
DoraVoiceActivityMetadata: TypeAlias = DoraProtobufMetadata


class DoraVoiceActivityMetadataError(ValueError):
    """Raised when DORA voice activity protobuf payloads cannot validate."""


class DoraVoiceActivityFinalMarkerError(DoraVoiceActivityMetadataError):
    """Raised when a DORA final marker is decoded as a voice activity event."""


class DoraVoiceActivityFinalMarker(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    source_id: str = Field(min_length=1)
    stream_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    sample_index: int = Field(ge=0)


class DoraAudioLevelMetadataError(ValueError):
    """Raised when DORA audio level protobuf payloads cannot validate."""


def encode_voice_activity_event_for_dora(
    event: VoiceActivityEvent,
) -> tuple[DoraVoiceActivityEncodedPayload, DoraVoiceActivityMetadata]:
    return encode_proto_message_for_dora(
        PbVoiceActivityEvent(
            source_id=event.source_id,
            stream_id=event.stream_id,
            seq=event.seq,
            sample_index=event.sample_index,
            frame_count=event.frame_count,
            state=_voice_activity_state_to_proto(event.state),
            speech_probability=event.speech_probability,
        )
    )


def encode_audio_level_event_for_dora(
    event: AudioLevelEvent,
) -> tuple[DoraVoiceActivityEncodedPayload, DoraVoiceActivityMetadata]:
    return encode_proto_message_for_dora(
        PbAudioLevelEvent(
            source_id=event.source_id,
            stream_id=event.stream_id,
            seq=event.seq,
            sample_index=event.sample_index,
            frame_count=event.frame_count,
            rms_dbfs=event.rms_dbfs,
            peak_dbfs=event.peak_dbfs,
            speech_probability=event.speech_probability,
        )
    )


def encode_voice_activity_final_marker_for_dora(
    *,
    source_id: str,
    stream_id: str,
    seq: int,
    sample_index: int,
) -> tuple[DoraVoiceActivityEncodedPayload, DoraVoiceActivityMetadata]:
    return encode_proto_message_for_dora(
        VoiceActivityStreamFinal(
            source_id=source_id,
            stream_id=stream_id,
            seq=seq,
            sample_index=sample_index,
        )
    )


def validate_dora_voice_activity_metadata(
    metadata: DoraMetadataMapping | DoraVoiceActivityMetadata | None,
) -> DoraVoiceActivityMetadata:
    try:
        protobuf_metadata = validate_dora_protobuf_metadata(metadata)
    except ValueError as exc:
        raise DoraVoiceActivityMetadataError(
            "DORA voice activity metadata is invalid"
        ) from exc
    if protobuf_metadata.message_type not in (
        PbVoiceActivityEvent.DESCRIPTOR.full_name,
        VoiceActivityStreamFinal.DESCRIPTOR.full_name,
    ):
        raise DoraVoiceActivityMetadataError(
            "DORA voice activity metadata message type is invalid: "
            f"{protobuf_metadata.message_type!r}"
        )
    return protobuf_metadata


def validate_dora_audio_level_metadata(
    metadata: DoraMetadataMapping | DoraVoiceActivityMetadata | None,
) -> DoraVoiceActivityMetadata:
    try:
        protobuf_metadata = validate_dora_protobuf_metadata(metadata)
    except ValueError as exc:
        raise DoraAudioLevelMetadataError("DORA audio level metadata is invalid") from exc
    if protobuf_metadata.message_type != PbAudioLevelEvent.DESCRIPTOR.full_name:
        raise DoraAudioLevelMetadataError(
            "DORA audio level metadata message type is invalid: "
            f"{protobuf_metadata.message_type!r}"
        )
    return protobuf_metadata


def decode_voice_activity_event_from_dora(
    payload: DoraVoiceActivityPayloadInput,
    metadata: DoraMetadataMapping | DoraVoiceActivityMetadata | None,
) -> VoiceActivityEvent:
    activity_metadata = validate_dora_voice_activity_metadata(metadata)
    if activity_metadata.message_type == VoiceActivityStreamFinal.DESCRIPTOR.full_name:
        raise DoraVoiceActivityFinalMarkerError(
            "DORA voice activity final marker is not a VoiceActivityEvent"
        )
    try:
        event = decode_proto_message_from_dora(payload, activity_metadata, PbVoiceActivityEvent)
        return VoiceActivityEvent(
            source_id=event.source_id,
            stream_id=event.stream_id,
            seq=event.seq,
            sample_index=event.sample_index,
            frame_count=event.frame_count,
            state=_voice_activity_state_from_proto(event.state),
            speech_probability=event.speech_probability,
        )
    except ValueError as exc:
        raise DoraVoiceActivityMetadataError(
            "DORA voice activity protobuf did not validate as VoiceActivityEvent"
        ) from exc


def decode_audio_level_event_from_dora(
    payload: DoraVoiceActivityPayloadInput,
    metadata: DoraMetadataMapping | DoraVoiceActivityMetadata | None,
) -> AudioLevelEvent:
    level_metadata = validate_dora_audio_level_metadata(metadata)
    try:
        event = decode_proto_message_from_dora(payload, level_metadata, PbAudioLevelEvent)
        return AudioLevelEvent(
            source_id=event.source_id,
            stream_id=event.stream_id,
            seq=event.seq,
            sample_index=event.sample_index,
            frame_count=event.frame_count,
            rms_dbfs=event.rms_dbfs,
            peak_dbfs=event.peak_dbfs,
            speech_probability=event.speech_probability,
        )
    except ValueError as exc:
        raise DoraAudioLevelMetadataError(
            "DORA audio level protobuf did not validate as AudioLevelEvent"
        ) from exc


def validate_dora_voice_activity_final_marker(
    payload: DoraVoiceActivityPayloadInput,
    metadata: DoraMetadataMapping | DoraVoiceActivityMetadata | None,
) -> DoraVoiceActivityFinalMarker:
    activity_metadata = validate_dora_voice_activity_metadata(metadata)
    if activity_metadata.message_type != VoiceActivityStreamFinal.DESCRIPTOR.full_name:
        raise DoraVoiceActivityMetadataError(
            "DORA voice activity metadata is not a final marker"
        )
    try:
        final = decode_proto_message_from_dora(payload, activity_metadata, VoiceActivityStreamFinal)
        return DoraVoiceActivityFinalMarker(
            source_id=final.source_id,
            stream_id=final.stream_id,
            seq=final.seq,
            sample_index=final.sample_index,
        )
    except ValueError as exc:
        raise DoraVoiceActivityMetadataError(
            "DORA voice activity protobuf did not validate as VoiceActivityStreamFinal"
        ) from exc


def _voice_activity_state_to_proto(state: VoiceActivityState) -> int:
    if state == "silence":
        return VOICE_ACTIVITY_STATE_SILENCE
    if state == "speech":
        return VOICE_ACTIVITY_STATE_SPEECH
    raise DoraVoiceActivityMetadataError(f"Unsupported voice activity state: {state!r}")


def _voice_activity_state_from_proto(state: int) -> VoiceActivityState:
    if state == VOICE_ACTIVITY_STATE_SILENCE:
        return "silence"
    if state == VOICE_ACTIVITY_STATE_SPEECH:
        return "speech"
    raise DoraVoiceActivityMetadataError(
        f"Unsupported protobuf voice activity state: {state}"
    )
