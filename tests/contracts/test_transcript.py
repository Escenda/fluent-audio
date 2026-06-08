import pytest
from pydantic import ValidationError

from fluent_audio.contracts import TranscriptDelta, TranscriptFinal


def test_transcript_models_preserve_turn_ids_and_text() -> None:
    delta = TranscriptDelta(
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="mic/main",
        seq=2,
        text="hello",
    )
    final = TranscriptFinal(
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="mic/main",
        seq=3,
        text="hello world",
        start_sample_index=320,
        end_sample_index=3200,
    )

    assert delta.user_turn_id == "user-turn-1"
    assert delta.text == "hello"
    assert final.text == "hello world"


def test_transcript_delta_rejects_empty_text() -> None:
    with pytest.raises(ValidationError):
        TranscriptDelta(
            session_id="session-1",
            user_turn_id="user-turn-1",
            stream_id="mic/main",
            seq=2,
            text="",
        )


def test_transcript_final_rejects_empty_sample_range() -> None:
    with pytest.raises(ValidationError, match="end_sample_index"):
        TranscriptFinal(
            session_id="session-1",
            user_turn_id="user-turn-1",
            stream_id="mic/main",
            seq=3,
            text="hello world",
            start_sample_index=3200,
            end_sample_index=3200,
        )
