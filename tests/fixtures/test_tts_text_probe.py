import pytest

from fluent_dialogue_dora.contracts import TtsTextChunk, TtsTextStreamFinal
from fluent_dialogue_dora.dora import (
    encode_tts_text_chunk_for_dora,
    encode_tts_text_stream_final_marker_for_dora,
)
from tests.fixtures.dora.tts_text_probe import (
    TtsTextProbeConfig,
    TtsTextProbeError,
    run_tts_text_probe_dora,
)


class FakeDoraNode:
    def __init__(self, events) -> None:
        self._events = events

    def __iter__(self):
        return iter(self._events)


def _input(encoded):
    payload, metadata = encoded
    return {
        "type": "INPUT",
        "id": "tts_text",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _chunk(text: str, seq: int = 0):
    return _input(
        encode_tts_text_chunk_for_dora(
            TtsTextChunk(
                request_id=f"tts-{seq:06d}",
                session_id="session-1",
                user_turn_id="user-turn-1",
                assistant_turn_id="assistant-turn-000000",
                seq=seq,
                text=text,
                is_final=True,
            )
        )
    )


def _final(seq: int = 1):
    return _input(
        encode_tts_text_stream_final_marker_for_dora(
            TtsTextStreamFinal(
                session_id="session-1",
                user_turn_id="user-turn-1",
                assistant_turn_id="assistant-turn-000000",
                seq=seq,
            )
        )
    )


def _config() -> TtsTextProbeConfig:
    return TtsTextProbeConfig(
        session_id="session-1",
        user_turn_id="user-turn-1",
        assistant_turn_id="assistant-turn-000000",
        expected_min_chunks=1,
        expected_text_contains=("こんにちは。",),
        forbidden_text_contains=("<think>", "</think>"),
    )


def test_tts_text_probe_accepts_filtered_tts_text() -> None:
    summary = run_tts_text_probe_dora(
        FakeDoraNode([_chunk("こんにちは。"), _final()]),
        _config(),
    )

    assert summary.chunks == 1
    assert summary.final_seen is True
    assert summary.text == "こんにちは。"


def test_tts_text_probe_rejects_forbidden_think_text() -> None:
    with pytest.raises(TtsTextProbeError, match="forbidden"):
        run_tts_text_probe_dora(
            FakeDoraNode([_chunk("<think>secret</think>こんにちは。"), _final()]),
            _config(),
        )
