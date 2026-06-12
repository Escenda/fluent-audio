import pytest
from pydantic import ValidationError

from fluent_audio.contracts import (
    AudioChunk,
    AudioFormat,
    SynthesizedAudioChunk,
    TtsTextChunk,
    TtsTextStreamFinal,
)


def test_tts_text_chunk_validates_correlation_ids() -> None:
    chunk = TtsTextChunk(
        request_id="tts-1",
        session_id="session-1",
        user_turn_id="user-turn-1",
        assistant_turn_id="assistant-turn-1",
        seq=0,
        text="hello",
        is_final=False,
    )

    assert chunk.request_id == "tts-1"
    assert chunk.text == "hello"


def test_tts_text_stream_final_validates_turn_correlation() -> None:
    marker = TtsTextStreamFinal(
        session_id="session-1",
        user_turn_id="user-turn-1",
        assistant_turn_id="assistant-turn-1",
        seq=1,
    )

    assert marker.session_id == "session-1"
    assert marker.assistant_turn_id == "assistant-turn-1"


def test_synthesized_audio_chunk_reuses_audio_chunk_validation() -> None:
    audio = AudioChunk(
        source_id="tts",
        stream_id="speaker/main",
        seq=0,
        sample_index=0,
        capture_time_ns=1_000,
        frame_count=2,
        format=AudioFormat(sample_rate_hz=16_000, channels=1),
        payload=b"\x00\x00\x00\x00",
    )
    chunk = SynthesizedAudioChunk(
        request_id="tts-1",
        session_id="session-1",
        user_turn_id="user-turn-1",
        assistant_turn_id="assistant-turn-1",
        seq=0,
        audio=audio,
    )

    assert chunk.audio.payload_size_bytes == 4


def test_synthesized_audio_chunk_rejects_invalid_nested_audio() -> None:
    with pytest.raises(ValidationError, match="payload size mismatch"):
        SynthesizedAudioChunk.model_validate(
            {
                "request_id": "tts-1",
                "session_id": "session-1",
                "user_turn_id": "user-turn-1",
                "assistant_turn_id": "assistant-turn-1",
                "seq": 0,
                "audio": {
                    "source_id": "tts",
                    "stream_id": "speaker/main",
                    "seq": 0,
                    "sample_index": 0,
                    "capture_time_ns": 1_000,
                    "frame_count": 2,
                    "format": {
                        "sample_rate_hz": 16_000,
                        "channels": 1,
                        "sample_format": "s16le",
                        "channel_layout": "interleaved",
                    },
                    "payload": b"\x00",
                },
            }
        )
