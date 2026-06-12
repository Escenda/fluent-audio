import pytest

from fluent_audio.contracts import TranscriptDelta, TranscriptFinal
from fluent_audio.dora import (
    encode_transcript_delta_for_dora,
    encode_transcript_final_for_dora,
    encode_transcript_stream_final_marker_for_dora,
)
from nodes.asr.nemotron_streaming.transcript_probe import (
    TranscriptProbeError,
    run_transcript_probe_dora,
    validate_summary,
)


class FakeDoraNode:
    def __init__(self, events) -> None:
        self._events = events

    def __iter__(self):
        return iter(self._events)


def _dora_delta(delta: TranscriptDelta):
    payload, metadata = encode_transcript_delta_for_dora(delta)
    return {
        "type": "INPUT",
        "id": "transcript",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _dora_final(final: TranscriptFinal):
    payload, metadata = encode_transcript_final_for_dora(final)
    return {
        "type": "INPUT",
        "id": "transcript",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _dora_stream_final(*, seq: int, sample_index: int):
    payload, metadata = encode_transcript_stream_final_marker_for_dora(
        session_id="session-1",
        stream_id="transcript/main",
        seq=seq,
        sample_index=sample_index,
    )
    return {
        "type": "INPUT",
        "id": "transcript",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def test_transcript_probe_accepts_delta_final_and_stream_final() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_delta(
                TranscriptDelta(
                    session_id="session-1",
                    user_turn_id="turn-1",
                    stream_id="transcript/main",
                    seq=0,
                    text="hello",
                )
            ),
            _dora_final(
                TranscriptFinal(
                    session_id="session-1",
                    user_turn_id="turn-1",
                    stream_id="transcript/main",
                    seq=1,
                    text="hello world",
                    start_sample_index=0,
                    end_sample_index=16000,
                )
            ),
            _dora_stream_final(seq=2, sample_index=16000),
        ]
    )

    summary = run_transcript_probe_dora(
        fake_node,
        session_id="session-1",
        stream_id="transcript/main",
    )
    validate_summary(
        summary,
        expected_min_deltas=1,
        expected_finals=1,
        expected_final_sample_index=16000,
        expected_last_text_compact="helloworld",
    )

    assert summary.deltas == 1
    assert summary.finals == 1
    assert summary.last_text == "hello world"


def test_transcript_probe_rejects_expected_last_text_mismatch() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_final(
                TranscriptFinal(
                    session_id="session-1",
                    user_turn_id="turn-1",
                    stream_id="transcript/main",
                    seq=0,
                    text="hello",
                    start_sample_index=0,
                    end_sample_index=16000,
                )
            ),
            _dora_stream_final(seq=1, sample_index=16000),
        ]
    )

    summary = run_transcript_probe_dora(
        fake_node,
        session_id="session-1",
        stream_id="transcript/main",
    )
    with pytest.raises(TranscriptProbeError, match="final text mismatch"):
        validate_summary(
            summary,
            expected_min_deltas=0,
            expected_finals=1,
            expected_final_sample_index=16000,
            expected_last_text="different",
        )


def test_transcript_probe_rejects_short_last_text() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_final(
                TranscriptFinal(
                    session_id="session-1",
                    user_turn_id="turn-1",
                    stream_id="transcript/main",
                    seq=0,
                    text="hi",
                    start_sample_index=0,
                    end_sample_index=16000,
                )
            ),
            _dora_stream_final(seq=1, sample_index=16000),
        ]
    )

    summary = run_transcript_probe_dora(
        fake_node,
        session_id="session-1",
        stream_id="transcript/main",
    )
    with pytest.raises(TranscriptProbeError, match="text length"):
        validate_summary(
            summary,
            expected_min_deltas=0,
            expected_finals=1,
            expected_final_sample_index=16000,
            expected_min_last_text_length=3,
        )


def test_transcript_probe_rejects_seq_gap() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_delta(
                TranscriptDelta(
                    session_id="session-1",
                    user_turn_id="turn-1",
                    stream_id="transcript/main",
                    seq=0,
                    text="hello",
                )
            ),
            _dora_final(
                TranscriptFinal(
                    session_id="session-1",
                    user_turn_id="turn-1",
                    stream_id="transcript/main",
                    seq=2,
                    text="hello world",
                    start_sample_index=0,
                    end_sample_index=16000,
                )
            ),
        ]
    )

    with pytest.raises(TranscriptProbeError, match="seq discontinuity"):
        run_transcript_probe_dora(
            fake_node,
            session_id="session-1",
            stream_id="transcript/main",
        )


def test_transcript_probe_rejects_missing_stream_final() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_final(
                TranscriptFinal(
                    session_id="session-1",
                    user_turn_id="turn-1",
                    stream_id="transcript/main",
                    seq=0,
                    text="hello",
                    start_sample_index=0,
                    end_sample_index=16000,
                )
            )
        ]
    )

    with pytest.raises(TranscriptProbeError, match="without final marker"):
        run_transcript_probe_dora(
            fake_node,
            session_id="session-1",
            stream_id="transcript/main",
        )
