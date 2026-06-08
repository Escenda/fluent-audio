import pytest
from pydantic import ValidationError

from fluent_audio.contracts import TurnEvent, VoiceActivityEvent


def test_voice_activity_event_accepts_probability_bounds() -> None:
    silent = VoiceActivityEvent(
        source_id="fixture",
        stream_id="mic/main",
        seq=0,
        sample_index=0,
        frame_count=160,
        state="silence",
        speech_probability=0.0,
    )
    speech = VoiceActivityEvent(
        source_id="fixture",
        stream_id="mic/main",
        seq=1,
        sample_index=160,
        frame_count=160,
        state="speech",
        speech_probability=1.0,
    )

    assert silent.state == "silence"
    assert speech.state == "speech"


def test_voice_activity_event_rejects_probability_outside_unit_interval() -> None:
    with pytest.raises(ValidationError):
        VoiceActivityEvent(
            source_id="fixture",
            stream_id="mic/main",
            seq=0,
            sample_index=0,
            frame_count=160,
            state="speech",
            speech_probability=1.01,
        )


def test_turn_event_preserves_turn_correlation() -> None:
    event = TurnEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="mic/main",
        seq=7,
        sample_index=320,
        state="started",
        confidence=0.75,
    )

    assert event.session_id == "session-1"
    assert event.user_turn_id == "user-turn-1"


def test_turn_event_rejects_confidence_outside_unit_interval() -> None:
    with pytest.raises(ValidationError):
        TurnEvent(
            session_id="session-1",
            user_turn_id="user-turn-1",
            stream_id="mic/main",
            seq=7,
            sample_index=320,
            state="started",
            confidence=-0.1,
        )
