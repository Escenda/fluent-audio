import pytest
from pydantic import TypeAdapter, ValidationError

from fluent_audio.contracts import AsrControl, AsrStart, AsrStop


def test_asr_control_validates_discriminated_variants() -> None:
    adapter = TypeAdapter(AsrControl)

    start = adapter.validate_python(
        {
            "action": "start",
            "session_id": "session-1",
            "user_turn_id": "user-turn-1",
            "stream_id": "mic/main",
            "seq": 0,
            "start_sample_index": 320,
        }
    )
    stop = adapter.validate_python(
        {
            "action": "stop",
            "session_id": "session-1",
            "user_turn_id": "user-turn-1",
            "stream_id": "mic/main",
            "seq": 1,
            "stop_sample_index": 3200,
        }
    )

    assert isinstance(start, AsrStart)
    assert isinstance(stop, AsrStop)


def test_asr_control_rejects_unknown_variant() -> None:
    adapter = TypeAdapter(AsrControl)

    with pytest.raises(ValidationError):
        adapter.validate_python(
            {
                "action": "flush",
                "session_id": "session-1",
                "user_turn_id": "user-turn-1",
                "stream_id": "mic/main",
                "seq": 1,
            }
        )
