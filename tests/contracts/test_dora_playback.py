import pyarrow as pa
import pytest

from fluent_audio.contracts import (
    PlaybackClear,
    PlaybackDone,
    PlaybackPause,
    PlaybackResume,
    PlaybackState,
    PlaybackStop,
)
from fluent_audio.dora import (
    DoraPlaybackMetadataError,
    decode_playback_command_from_dora,
    decode_playback_done_from_dora,
    decode_playback_state_from_dora,
    encode_playback_command_for_dora,
    encode_playback_done_for_dora,
    encode_playback_state_for_dora,
)


def test_playback_commands_roundtrip_through_dora() -> None:
    commands = [
        PlaybackStop(command="stop", request_id="tts-1", stream_id="audio/playback", seq=0),
        PlaybackPause(command="pause", request_id="tts-1", stream_id="audio/playback", seq=1),
        PlaybackResume(command="resume", request_id="tts-1", stream_id="audio/playback", seq=2),
        PlaybackClear(command="clear", request_id="tts-1", stream_id="audio/playback", seq=3),
    ]

    for command in commands:
        payload, metadata = encode_playback_command_for_dora(command)
        decoded = decode_playback_command_from_dora(payload, metadata.to_dora_metadata())
        assert decoded == command


def test_playback_command_rejects_invalid_payload() -> None:
    command = PlaybackStop(command="stop", request_id="tts-1", stream_id="audio/playback", seq=0)
    _, metadata = encode_playback_command_for_dora(command)

    with pytest.raises(DoraPlaybackMetadataError, match="protobuf did not validate"):
        decode_playback_command_from_dora(pa.array([1], type=pa.uint8()), metadata)


def test_playback_state_roundtrips_through_dora() -> None:
    state = PlaybackState(
        request_id="tts-1",
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="audio/playback",
        state="playing",
        seq=4,
        played_frames=4096,
    )

    payload, metadata = encode_playback_state_for_dora(state)
    decoded = decode_playback_state_from_dora(payload, metadata.to_dora_metadata())

    assert decoded == state


def test_playback_state_rejects_failed_without_reason() -> None:
    metadata = {
        "request_id": "tts-1",
        "session_id": "session-1",
        "user_turn_id": "user-turn-1",
        "stream_id": "audio/playback",
        "state": "failed",
        "seq": 4,
        "played_frames": 0,
        "reason": "",
    }

    with pytest.raises(DoraPlaybackMetadataError, match="invalid"):
        decode_playback_state_from_dora(b"", metadata)


def test_playback_done_roundtrips_through_dora() -> None:
    done = PlaybackDone(
        request_id="tts-1",
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="audio/playback",
        status="completed",
        total_frames=8192,
    )

    payload, metadata = encode_playback_done_for_dora(done)
    decoded = decode_playback_done_from_dora(payload, metadata.to_dora_metadata())

    assert decoded == done


def test_playback_done_preserves_failed_reason() -> None:
    done = PlaybackDone(
        request_id="tts-1",
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="audio/playback",
        status="failed",
        final_sequence=8,
        reason="device_error",
    )

    payload, metadata = encode_playback_done_for_dora(done)
    decoded = decode_playback_done_from_dora(payload, metadata.to_dora_metadata())

    assert decoded == done


def test_playback_done_rejects_missing_position() -> None:
    metadata = {
        "request_id": "tts-1",
        "session_id": "session-1",
        "user_turn_id": "user-turn-1",
        "stream_id": "audio/playback",
        "status": "completed",
        "final_sequence_present": False,
        "final_sequence": 0,
        "total_frames_present": False,
        "total_frames": 0,
        "reason": "",
    }

    with pytest.raises(DoraPlaybackMetadataError, match="invalid"):
        decode_playback_done_from_dora(b"", metadata)
