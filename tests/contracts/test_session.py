import pytest
from pydantic import ValidationError

from fluent_dialogue_dora.contracts import TurnIds, VoiceSessionEvent


def test_voice_session_event_validates_expected_variant() -> None:
    event = VoiceSessionEvent(
        event="state_changed",
        state="listening",
        seq=5,
        turn_ids=TurnIds(session_id="session-1", user_turn_id="user-turn-1"),
    )

    assert event.state == "listening"
    assert event.turn_ids.assistant_turn_id is None


def test_voice_session_event_rejects_unknown_event() -> None:
    with pytest.raises(ValidationError):
        VoiceSessionEvent(
            event="heartbeat",
            state="listening",
            seq=5,
            turn_ids=TurnIds(session_id="session-1", user_turn_id="user-turn-1"),
        )


def test_voice_session_event_rejects_unknown_state() -> None:
    with pytest.raises(ValidationError):
        VoiceSessionEvent(
            event="state_changed",
            state="sleeping",
            seq=5,
            turn_ids=TurnIds(session_id="session-1", user_turn_id="user-turn-1"),
        )
