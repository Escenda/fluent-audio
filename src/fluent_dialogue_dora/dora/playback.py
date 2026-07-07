"""DORA protobuf helpers for playback contracts."""

from __future__ import annotations

from typing import TypeAlias

from fluent_dialogue_dora.contracts import (
    PlaybackClear,
    PlaybackControlFlush,
    PlaybackDone,
    PlaybackPause,
    PlaybackResume,
    PlaybackState,
    PlaybackStop,
)
from fluent_dialogue_dora.dora.protobuf import (
    DoraMetadataMapping,
    DoraProtobufEncodedPayload,
    DoraProtobufMetadata,
    DoraProtobufPayloadInput,
    decode_proto_message_from_dora,
    encode_proto_message_for_dora,
    validate_dora_protobuf_metadata,
)
from fluent_dialogue_dora_contracts.fluent_dialogue_dora.v1.playback_pb2 import (
    PLAYBACK_COMMAND_KIND_CLEAR,
    PLAYBACK_COMMAND_KIND_PAUSE,
    PLAYBACK_COMMAND_KIND_RESUME,
    PLAYBACK_COMMAND_KIND_STOP,
    PLAYBACK_CONTROL_KIND_FLUSH,
    PLAYBACK_DONE_STATUS_CANCELLED,
    PLAYBACK_DONE_STATUS_COMPLETED,
    PLAYBACK_DONE_STATUS_FAILED,
    PLAYBACK_DONE_STATUS_STOPPED,
    PLAYBACK_STATE_KIND_CANCELLED,
    PLAYBACK_STATE_KIND_COMPLETED,
    PLAYBACK_STATE_KIND_FAILED,
    PLAYBACK_STATE_KIND_PAUSED,
    PLAYBACK_STATE_KIND_PLAYING,
    PLAYBACK_STATE_KIND_QUEUED,
    PLAYBACK_STATE_KIND_STOPPED,
    PlaybackCommand,
    PlaybackControlCommand as PbPlaybackControlCommand,
    PlaybackDone as PbPlaybackDone,
    PlaybackState as PbPlaybackState,
)

PlaybackCommandEvent: TypeAlias = PlaybackStop | PlaybackPause | PlaybackResume | PlaybackClear
DoraPlaybackPayloadInput: TypeAlias = DoraProtobufPayloadInput
DoraPlaybackEncodedPayload: TypeAlias = DoraProtobufEncodedPayload
DoraPlaybackCommandMetadata: TypeAlias = DoraProtobufMetadata
DoraPlaybackControlMetadata: TypeAlias = DoraProtobufMetadata
DoraPlaybackStateMetadata: TypeAlias = DoraProtobufMetadata
DoraPlaybackDoneMetadata: TypeAlias = DoraProtobufMetadata


class DoraPlaybackMetadataError(ValueError):
    """Raised when DORA playback protobuf payloads cannot validate."""


def encode_playback_command_for_dora(
    command: PlaybackCommandEvent,
) -> tuple[DoraPlaybackEncodedPayload, DoraPlaybackCommandMetadata]:
    return encode_proto_message_for_dora(
        PlaybackCommand(
            command=_playback_command_to_proto(command.command),
            request_id=command.request_id,
            stream_id=command.stream_id,
            seq=command.seq,
        )
    )


def decode_playback_command_from_dora(
    payload: DoraPlaybackPayloadInput,
    metadata: DoraMetadataMapping | DoraPlaybackCommandMetadata | None,
) -> PlaybackCommandEvent:
    command_metadata = validate_dora_playback_command_metadata(metadata)
    try:
        command = decode_proto_message_from_dora(payload, command_metadata, PlaybackCommand)
        command_name = _playback_command_from_proto(command.command)
        if command_name == "stop":
            return PlaybackStop(
                command="stop",
                request_id=command.request_id,
                stream_id=command.stream_id,
                seq=command.seq,
            )
        if command_name == "pause":
            return PlaybackPause(
                command="pause",
                request_id=command.request_id,
                stream_id=command.stream_id,
                seq=command.seq,
            )
        if command_name == "resume":
            return PlaybackResume(
                command="resume",
                request_id=command.request_id,
                stream_id=command.stream_id,
                seq=command.seq,
            )
        return PlaybackClear(
            command="clear",
            request_id=command.request_id,
            stream_id=command.stream_id,
            seq=command.seq,
        )
    except ValueError as exc:
        raise DoraPlaybackMetadataError(
            "DORA playback command protobuf did not validate as PlaybackCommand"
        ) from exc


def validate_dora_playback_command_metadata(
    metadata: DoraMetadataMapping | DoraPlaybackCommandMetadata | None,
) -> DoraPlaybackCommandMetadata:
    return _validate_playback_metadata(metadata, PlaybackCommand.DESCRIPTOR.full_name)


def encode_playback_control_command_for_dora(
    control: PlaybackControlFlush,
) -> tuple[DoraPlaybackEncodedPayload, DoraPlaybackControlMetadata]:
    return encode_proto_message_for_dora(
        PbPlaybackControlCommand(
            kind=_playback_control_to_proto(control.kind),
            stream_id=control.stream_id,
            seq=control.seq,
            fade_out_ms=control.fade_out_ms,
        )
    )


def decode_playback_control_command_from_dora(
    payload: DoraPlaybackPayloadInput,
    metadata: DoraMetadataMapping | DoraPlaybackControlMetadata | None,
) -> PlaybackControlFlush:
    control_metadata = validate_dora_playback_control_metadata(metadata)
    try:
        control = decode_proto_message_from_dora(
            payload, control_metadata, PbPlaybackControlCommand
        )
        return PlaybackControlFlush(
            kind=_playback_control_from_proto(control.kind),
            stream_id=control.stream_id,
            seq=control.seq,
            fade_out_ms=control.fade_out_ms,
        )
    except ValueError as exc:
        raise DoraPlaybackMetadataError(
            "DORA playback control protobuf did not validate as PlaybackControlCommand"
        ) from exc


def validate_dora_playback_control_metadata(
    metadata: DoraMetadataMapping | DoraPlaybackControlMetadata | None,
) -> DoraPlaybackControlMetadata:
    return _validate_playback_metadata(metadata, PbPlaybackControlCommand.DESCRIPTOR.full_name)


def encode_playback_state_for_dora(
    state: PlaybackState,
) -> tuple[DoraPlaybackEncodedPayload, DoraPlaybackStateMetadata]:
    proto_state = PbPlaybackState(
        request_id=state.request_id,
        session_id=state.session_id,
        user_turn_id=state.user_turn_id,
        stream_id=state.stream_id,
        state=_playback_state_to_proto(state.state),
        seq=state.seq,
        played_frames=state.played_frames,
    )
    if state.reason is not None:
        proto_state.reason = state.reason
    return encode_proto_message_for_dora(proto_state)


def decode_playback_state_from_dora(
    payload: DoraPlaybackPayloadInput,
    metadata: DoraMetadataMapping | DoraPlaybackStateMetadata | None,
) -> PlaybackState:
    state_metadata = validate_dora_playback_state_metadata(metadata)
    try:
        state = decode_proto_message_from_dora(payload, state_metadata, PbPlaybackState)
        return PlaybackState(
            request_id=state.request_id,
            session_id=state.session_id,
            user_turn_id=state.user_turn_id,
            stream_id=state.stream_id,
            state=_playback_state_from_proto(state.state),
            seq=state.seq,
            played_frames=state.played_frames,
            reason=state.reason if state.HasField("reason") else None,
        )
    except ValueError as exc:
        raise DoraPlaybackMetadataError(
            "DORA playback state protobuf did not validate as PlaybackState"
        ) from exc


def validate_dora_playback_state_metadata(
    metadata: DoraMetadataMapping | DoraPlaybackStateMetadata | None,
) -> DoraPlaybackStateMetadata:
    return _validate_playback_metadata(metadata, PbPlaybackState.DESCRIPTOR.full_name)


def encode_playback_done_for_dora(
    done: PlaybackDone,
) -> tuple[DoraPlaybackEncodedPayload, DoraPlaybackDoneMetadata]:
    proto_done = PbPlaybackDone(
        request_id=done.request_id,
        session_id=done.session_id,
        user_turn_id=done.user_turn_id,
        stream_id=done.stream_id,
        status=_playback_done_status_to_proto(done.status),
    )
    if done.final_sequence is not None:
        proto_done.final_sequence = done.final_sequence
    if done.total_frames is not None:
        proto_done.total_frames = done.total_frames
    if done.reason is not None:
        proto_done.reason = done.reason
    return encode_proto_message_for_dora(proto_done)


def decode_playback_done_from_dora(
    payload: DoraPlaybackPayloadInput,
    metadata: DoraMetadataMapping | DoraPlaybackDoneMetadata | None,
) -> PlaybackDone:
    done_metadata = validate_dora_playback_done_metadata(metadata)
    try:
        done = decode_proto_message_from_dora(payload, done_metadata, PbPlaybackDone)
        return PlaybackDone(
            request_id=done.request_id,
            session_id=done.session_id,
            user_turn_id=done.user_turn_id,
            stream_id=done.stream_id,
            status=_playback_done_status_from_proto(done.status),
            final_sequence=done.final_sequence if done.HasField("final_sequence") else None,
            total_frames=done.total_frames if done.HasField("total_frames") else None,
            reason=done.reason if done.HasField("reason") else None,
        )
    except ValueError as exc:
        raise DoraPlaybackMetadataError(
            "DORA playback done protobuf did not validate as PlaybackDone"
        ) from exc


def validate_dora_playback_done_metadata(
    metadata: DoraMetadataMapping | DoraPlaybackDoneMetadata | None,
) -> DoraPlaybackDoneMetadata:
    return _validate_playback_metadata(metadata, PbPlaybackDone.DESCRIPTOR.full_name)


def _validate_playback_metadata(
    metadata: DoraMetadataMapping | DoraProtobufMetadata | None,
    message_type: str,
) -> DoraProtobufMetadata:
    try:
        protobuf_metadata = validate_dora_protobuf_metadata(metadata)
    except ValueError as exc:
        raise DoraPlaybackMetadataError("DORA playback metadata is invalid") from exc
    if protobuf_metadata.message_type != message_type:
        raise DoraPlaybackMetadataError(
            "DORA playback metadata message type is invalid: "
            f"expected {message_type!r}, got {protobuf_metadata.message_type!r}"
        )
    return protobuf_metadata


def _playback_command_to_proto(command: str) -> int:
    mapping = {
        "stop": PLAYBACK_COMMAND_KIND_STOP,
        "pause": PLAYBACK_COMMAND_KIND_PAUSE,
        "resume": PLAYBACK_COMMAND_KIND_RESUME,
        "clear": PLAYBACK_COMMAND_KIND_CLEAR,
    }
    if command not in mapping:
        raise DoraPlaybackMetadataError(f"Unsupported playback command: {command!r}")
    return mapping[command]


def _playback_command_from_proto(command: int) -> str:
    mapping = {
        PLAYBACK_COMMAND_KIND_STOP: "stop",
        PLAYBACK_COMMAND_KIND_PAUSE: "pause",
        PLAYBACK_COMMAND_KIND_RESUME: "resume",
        PLAYBACK_COMMAND_KIND_CLEAR: "clear",
    }
    if command not in mapping:
        raise DoraPlaybackMetadataError(f"Unsupported protobuf playback command: {command}")
    return mapping[command]


def _playback_control_to_proto(kind: str) -> int:
    if kind != "flush":
        raise DoraPlaybackMetadataError(f"Unsupported playback control kind: {kind!r}")
    return PLAYBACK_CONTROL_KIND_FLUSH


def _playback_control_from_proto(kind: int) -> str:
    if kind != PLAYBACK_CONTROL_KIND_FLUSH:
        raise DoraPlaybackMetadataError(f"Unsupported protobuf playback control kind: {kind}")
    return "flush"


def _playback_state_to_proto(state: str) -> int:
    mapping = {
        "queued": PLAYBACK_STATE_KIND_QUEUED,
        "playing": PLAYBACK_STATE_KIND_PLAYING,
        "paused": PLAYBACK_STATE_KIND_PAUSED,
        "stopped": PLAYBACK_STATE_KIND_STOPPED,
        "completed": PLAYBACK_STATE_KIND_COMPLETED,
        "cancelled": PLAYBACK_STATE_KIND_CANCELLED,
        "failed": PLAYBACK_STATE_KIND_FAILED,
    }
    if state not in mapping:
        raise DoraPlaybackMetadataError(f"Unsupported playback state: {state!r}")
    return mapping[state]


def _playback_state_from_proto(state: int) -> str:
    mapping = {
        PLAYBACK_STATE_KIND_QUEUED: "queued",
        PLAYBACK_STATE_KIND_PLAYING: "playing",
        PLAYBACK_STATE_KIND_PAUSED: "paused",
        PLAYBACK_STATE_KIND_STOPPED: "stopped",
        PLAYBACK_STATE_KIND_COMPLETED: "completed",
        PLAYBACK_STATE_KIND_CANCELLED: "cancelled",
        PLAYBACK_STATE_KIND_FAILED: "failed",
    }
    if state not in mapping:
        raise DoraPlaybackMetadataError(f"Unsupported protobuf playback state: {state}")
    return mapping[state]


def _playback_done_status_to_proto(status: str) -> int:
    mapping = {
        "completed": PLAYBACK_DONE_STATUS_COMPLETED,
        "stopped": PLAYBACK_DONE_STATUS_STOPPED,
        "cancelled": PLAYBACK_DONE_STATUS_CANCELLED,
        "failed": PLAYBACK_DONE_STATUS_FAILED,
    }
    if status not in mapping:
        raise DoraPlaybackMetadataError(f"Unsupported playback done status: {status!r}")
    return mapping[status]


def _playback_done_status_from_proto(status: int) -> str:
    mapping = {
        PLAYBACK_DONE_STATUS_COMPLETED: "completed",
        PLAYBACK_DONE_STATUS_STOPPED: "stopped",
        PLAYBACK_DONE_STATUS_CANCELLED: "cancelled",
        PLAYBACK_DONE_STATUS_FAILED: "failed",
    }
    if status not in mapping:
        raise DoraPlaybackMetadataError(
            f"Unsupported protobuf playback done status: {status}"
        )
    return mapping[status]
