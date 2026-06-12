"""DORA protobuf helpers for voice session events."""

from __future__ import annotations

from typing import TypeAlias

from fluent_audio.contracts import TurnIds, VoiceSessionEvent
from fluent_audio.dora.protobuf import (
    DoraMetadataMapping,
    DoraProtobufEncodedPayload,
    DoraProtobufMetadata,
    DoraProtobufPayloadInput,
    decode_proto_message_from_dora,
    encode_proto_message_for_dora,
    validate_dora_protobuf_metadata,
)
from fluent_audio_contracts.fluent_audio.v1.session_pb2 import (
    VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_COMPLETED,
    VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_STARTED,
    VOICE_SESSION_EVENT_KIND_ERROR,
    VOICE_SESSION_EVENT_KIND_SESSION_CLOSED,
    VOICE_SESSION_EVENT_KIND_SESSION_STARTED,
    VOICE_SESSION_EVENT_KIND_STATE_CHANGED,
    VOICE_SESSION_EVENT_KIND_USER_TURN_FINALIZED,
    VOICE_SESSION_EVENT_KIND_USER_TURN_STARTED,
    VOICE_SESSION_STATE_CLOSED,
    VOICE_SESSION_STATE_ERROR,
    VOICE_SESSION_STATE_IDLE,
    VOICE_SESSION_STATE_INTERRUPTED,
    VOICE_SESSION_STATE_LISTENING,
    VOICE_SESSION_STATE_SPEAKING,
    VOICE_SESSION_STATE_THINKING,
    VOICE_SESSION_STATE_TRANSCRIBING,
    VOICE_SESSION_STATE_USER_SPEAKING,
    TurnIds as PbTurnIds,
    VoiceSessionEvent as PbVoiceSessionEvent,
)

DoraSessionPayloadInput: TypeAlias = DoraProtobufPayloadInput
DoraSessionEncodedPayload: TypeAlias = DoraProtobufEncodedPayload
DoraVoiceSessionMetadata: TypeAlias = DoraProtobufMetadata


class DoraSessionMetadataError(ValueError):
    """Raised when DORA session protobuf payloads cannot validate."""


def encode_voice_session_event_for_dora(
    event: VoiceSessionEvent,
) -> tuple[DoraSessionEncodedPayload, DoraVoiceSessionMetadata]:
    turn_ids = PbTurnIds(
        session_id=event.turn_ids.session_id,
        user_turn_id=event.turn_ids.user_turn_id,
    )
    if event.turn_ids.assistant_turn_id is not None:
        turn_ids.assistant_turn_id = event.turn_ids.assistant_turn_id
    proto_event = PbVoiceSessionEvent(
        event=_session_event_to_proto(event.event),
        state=_session_state_to_proto(event.state),
        seq=event.seq,
        turn_ids=turn_ids,
    )
    if event.message is not None:
        proto_event.message = event.message
    return encode_proto_message_for_dora(proto_event)


def decode_voice_session_event_from_dora(
    payload: DoraSessionPayloadInput,
    metadata: DoraMetadataMapping | DoraVoiceSessionMetadata | None,
) -> VoiceSessionEvent:
    session_metadata = validate_dora_voice_session_metadata(metadata)
    try:
        event = decode_proto_message_from_dora(payload, session_metadata, PbVoiceSessionEvent)
        return VoiceSessionEvent(
            event=_session_event_from_proto(event.event),
            state=_session_state_from_proto(event.state),
            seq=event.seq,
            turn_ids=TurnIds(
                session_id=event.turn_ids.session_id,
                user_turn_id=event.turn_ids.user_turn_id,
                assistant_turn_id=event.turn_ids.assistant_turn_id
                if event.turn_ids.HasField("assistant_turn_id")
                else None,
            ),
            message=event.message if event.HasField("message") else None,
        )
    except ValueError as exc:
        raise DoraSessionMetadataError(
            "DORA session protobuf did not validate as VoiceSessionEvent"
        ) from exc


def validate_dora_voice_session_metadata(
    metadata: DoraMetadataMapping | DoraVoiceSessionMetadata | None,
) -> DoraVoiceSessionMetadata:
    try:
        protobuf_metadata = validate_dora_protobuf_metadata(metadata)
    except ValueError as exc:
        raise DoraSessionMetadataError("DORA session metadata is invalid") from exc
    if protobuf_metadata.message_type != PbVoiceSessionEvent.DESCRIPTOR.full_name:
        raise DoraSessionMetadataError(
            "DORA session metadata message type is invalid: "
            f"{protobuf_metadata.message_type!r}"
        )
    return protobuf_metadata


def _session_event_to_proto(event: str) -> int:
    mapping = {
        "session_started": VOICE_SESSION_EVENT_KIND_SESSION_STARTED,
        "state_changed": VOICE_SESSION_EVENT_KIND_STATE_CHANGED,
        "user_turn_started": VOICE_SESSION_EVENT_KIND_USER_TURN_STARTED,
        "user_turn_finalized": VOICE_SESSION_EVENT_KIND_USER_TURN_FINALIZED,
        "assistant_turn_started": VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_STARTED,
        "assistant_turn_completed": VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_COMPLETED,
        "session_closed": VOICE_SESSION_EVENT_KIND_SESSION_CLOSED,
        "error": VOICE_SESSION_EVENT_KIND_ERROR,
    }
    if event not in mapping:
        raise DoraSessionMetadataError(f"Unsupported voice session event: {event!r}")
    return mapping[event]


def _session_event_from_proto(event: int) -> str:
    mapping = {
        VOICE_SESSION_EVENT_KIND_SESSION_STARTED: "session_started",
        VOICE_SESSION_EVENT_KIND_STATE_CHANGED: "state_changed",
        VOICE_SESSION_EVENT_KIND_USER_TURN_STARTED: "user_turn_started",
        VOICE_SESSION_EVENT_KIND_USER_TURN_FINALIZED: "user_turn_finalized",
        VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_STARTED: "assistant_turn_started",
        VOICE_SESSION_EVENT_KIND_ASSISTANT_TURN_COMPLETED: "assistant_turn_completed",
        VOICE_SESSION_EVENT_KIND_SESSION_CLOSED: "session_closed",
        VOICE_SESSION_EVENT_KIND_ERROR: "error",
    }
    if event not in mapping:
        raise DoraSessionMetadataError(f"Unsupported protobuf voice session event: {event}")
    return mapping[event]


def _session_state_to_proto(state: str) -> int:
    mapping = {
        "idle": VOICE_SESSION_STATE_IDLE,
        "listening": VOICE_SESSION_STATE_LISTENING,
        "user_speaking": VOICE_SESSION_STATE_USER_SPEAKING,
        "transcribing": VOICE_SESSION_STATE_TRANSCRIBING,
        "thinking": VOICE_SESSION_STATE_THINKING,
        "speaking": VOICE_SESSION_STATE_SPEAKING,
        "interrupted": VOICE_SESSION_STATE_INTERRUPTED,
        "closed": VOICE_SESSION_STATE_CLOSED,
        "error": VOICE_SESSION_STATE_ERROR,
    }
    if state not in mapping:
        raise DoraSessionMetadataError(f"Unsupported voice session state: {state!r}")
    return mapping[state]


def _session_state_from_proto(state: int) -> str:
    mapping = {
        VOICE_SESSION_STATE_IDLE: "idle",
        VOICE_SESSION_STATE_LISTENING: "listening",
        VOICE_SESSION_STATE_USER_SPEAKING: "user_speaking",
        VOICE_SESSION_STATE_TRANSCRIBING: "transcribing",
        VOICE_SESSION_STATE_THINKING: "thinking",
        VOICE_SESSION_STATE_SPEAKING: "speaking",
        VOICE_SESSION_STATE_INTERRUPTED: "interrupted",
        VOICE_SESSION_STATE_CLOSED: "closed",
        VOICE_SESSION_STATE_ERROR: "error",
    }
    if state not in mapping:
        raise DoraSessionMetadataError(f"Unsupported protobuf voice session state: {state}")
    return mapping[state]
