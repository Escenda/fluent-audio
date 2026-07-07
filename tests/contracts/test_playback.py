import pytest
from pydantic import TypeAdapter, ValidationError

from fluent_dialogue_dora.contracts import (
    PlaybackCommand,
    PlaybackDone,
    PlaybackPause,
    PlaybackState,
    PlaybackStop,
)


def test_playback_command_validates_discriminated_variants() -> None:
    adapter = TypeAdapter(PlaybackCommand)

    stop = adapter.validate_python(
        {
            "command": "stop",
            "request_id": "req-1",
            "stream_id": "speaker/main",
            "seq": 3,
        }
    )
    pause = adapter.validate_python(
        {
            "command": "pause",
            "request_id": "req-2",
            "stream_id": "speaker/main",
            "seq": 4,
        }
    )

    assert isinstance(stop, PlaybackStop)
    assert isinstance(pause, PlaybackPause)


def test_playback_command_rejects_unknown_variant() -> None:
    adapter = TypeAdapter(PlaybackCommand)

    with pytest.raises(ValidationError):
        adapter.validate_python(
            {
                "command": "seek",
                "request_id": "req-1",
                "stream_id": "speaker/main",
                "seq": 3,
            }
        )


def test_playback_done_requires_completion_position() -> None:
    with pytest.raises(ValidationError, match="requires final_sequence or total_frames"):
        PlaybackDone(
            request_id="req-1",
            session_id="session-1",
            user_turn_id="user-turn-1",
            stream_id="speaker/main",
            status="completed",
        )


def test_playback_done_validates_failure_reason() -> None:
    with pytest.raises(ValidationError, match="requires reason"):
        PlaybackDone(
            request_id="req-1",
            session_id="session-1",
            user_turn_id="user-turn-1",
            stream_id="speaker/main",
            status="failed",
            final_sequence=9,
        )

    done = PlaybackDone(
        request_id="req-1",
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="speaker/main",
        status="completed",
        final_sequence=9,
    )
    assert done.final_sequence == 9


def test_playback_state_validates_correlation_ids() -> None:
    state = PlaybackState(
        request_id="req-1",
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="speaker/main",
        state="playing",
        seq=3,
        played_frames=640,
    )

    assert state.request_id == "req-1"
    assert state.played_frames == 640


def test_playback_state_failed_requires_reason() -> None:
    with pytest.raises(ValidationError, match="requires reason"):
        PlaybackState(
            request_id="req-1",
            session_id="session-1",
            user_turn_id="user-turn-1",
            stream_id="speaker/main",
            state="failed",
            seq=3,
            played_frames=640,
        )
