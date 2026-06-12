import pyarrow as pa
import pytest

from fluent_audio.contracts import TurnIds, VoiceSessionEvent
from fluent_audio.dora import (
    DoraSessionMetadataError,
    decode_voice_session_event_from_dora,
    encode_voice_session_event_for_dora,
)


def test_voice_session_event_roundtrips_through_dora() -> None:
    event = VoiceSessionEvent(
        event="assistant_turn_started",
        state="speaking",
        seq=4,
        turn_ids=TurnIds(
            session_id="session-1",
            user_turn_id="user-turn-000001",
            assistant_turn_id="assistant-turn-000001",
        ),
        message="started",
    )

    payload, metadata = encode_voice_session_event_for_dora(event)
    decoded = decode_voice_session_event_from_dora(payload, metadata.to_dora_metadata())

    assert decoded == event


def test_voice_session_event_preserves_absent_optional_fields() -> None:
    event = VoiceSessionEvent(
        event="user_turn_started",
        state="user_speaking",
        seq=1,
        turn_ids=TurnIds(
            session_id="session-1",
            user_turn_id="user-turn-000001",
        ),
    )

    payload, metadata = encode_voice_session_event_for_dora(event)
    decoded = decode_voice_session_event_from_dora(payload, metadata.to_dora_metadata())

    assert decoded == event
    assert decoded.turn_ids.assistant_turn_id is None
    assert decoded.message is None


def test_voice_session_rejects_invalid_payload() -> None:
    event = VoiceSessionEvent(
        event="user_turn_started",
        state="user_speaking",
        seq=1,
        turn_ids=TurnIds(session_id="session-1", user_turn_id="user-turn-000001"),
    )
    _, metadata = encode_voice_session_event_for_dora(event)

    with pytest.raises(DoraSessionMetadataError, match="protobuf did not validate"):
        decode_voice_session_event_from_dora(pa.array([1], type=pa.uint8()), metadata)
