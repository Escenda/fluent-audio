from fluent_dialogue_dora.contracts import AudioChunk, AudioFormat
from fluent_dialogue_dora.dora import (
    decode_audio_chunk_from_dora,
    encode_audio_chunk_for_dora,
    encode_audio_final_marker_for_dora,
    validate_dora_audio_final_marker,
)
from nodes.playback.speaker_stream_adapter.main import (
    SpeakerStreamAdapterConfig,
    SpeakerStreamAdapterError,
    run_speaker_stream_adapter_events,
)


class FakeDoraNode:
    def __init__(self, events) -> None:
        self._events = events
        self.sent = []

    def __iter__(self):
        return iter(self._events)

    def send_output(self, output_id, payload, *, metadata) -> None:
        self.sent.append((output_id, payload, metadata))


def _format() -> AudioFormat:
    return AudioFormat(sample_rate_hz=48_000, channels=1, sample_format="f32le")


def _chunk(seq: int) -> AudioChunk:
    frame_count = 2
    sample_index = seq * frame_count
    return AudioChunk(
        source_id="playback_queue",
        stream_id="speaker/main",
        seq=seq,
        sample_index=sample_index,
        capture_time_ns=sample_index * 1_000,
        frame_count=frame_count,
        format=_format(),
        payload=bytes((0, 0, 0, 0, 0, 0, 0, 0)),
    )


def _input(encoded):
    payload, metadata = encoded
    return {
        "type": "INPUT",
        "id": "audio",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _final(seq: int, sample_index: int):
    return _input(
        encode_audio_final_marker_for_dora(
            source_id="playback_queue",
            stream_id="speaker/main",
            seq=seq,
            sample_index=sample_index,
            capture_time_ns=sample_index * 1_000,
            audio_format=_format(),
        )
    )


def _input_closed():
    return {"type": "INPUT_CLOSED", "id": "audio"}


def _config() -> SpeakerStreamAdapterConfig:
    return SpeakerStreamAdapterConfig(
        input_source_id="playback_queue",
        input_stream_id="speaker/main",
        output_source_id="speaker_stream",
        output_stream_id="speaker/continuous",
        output_drain_seconds=0.0,
    )


def test_speaker_stream_adapter_suppresses_request_finals_until_input_closes() -> None:
    node = FakeDoraNode(
        [
            _input(encode_audio_chunk_for_dora(_chunk(0))),
            _final(seq=1, sample_index=2),
            _input(encode_audio_chunk_for_dora(_chunk(1))),
            _final(seq=2, sample_index=4),
            _input_closed(),
        ]
    )

    summary = run_speaker_stream_adapter_events(node, _config())

    assert summary.input_chunks == 2
    assert summary.input_request_finals == 2
    assert summary.output_chunks == 2
    assert summary.output_final_sent is True
    assert summary.final_sample_index == 4
    assert [output_id for output_id, _, _ in node.sent] == ["audio", "audio", "audio"]

    first = decode_audio_chunk_from_dora(node.sent[0][1], node.sent[0][2])
    second = decode_audio_chunk_from_dora(node.sent[1][1], node.sent[1][2])
    final = validate_dora_audio_final_marker(node.sent[2][1], node.sent[2][2])

    assert first.source_id == "speaker_stream"
    assert first.stream_id == "speaker/continuous"
    assert first.seq == 0
    assert first.sample_index == 0
    assert second.seq == 1
    assert second.sample_index == 2
    assert final.source_id == "speaker_stream"
    assert final.stream_id == "speaker/continuous"
    assert final.seq == 2
    assert final.sample_index == 4


def test_speaker_stream_adapter_rejects_input_final_with_bad_position() -> None:
    node = FakeDoraNode(
        [
            _input(encode_audio_chunk_for_dora(_chunk(0))),
            _final(seq=9, sample_index=2),
        ]
    )

    try:
        run_speaker_stream_adapter_events(node, _config())
    except SpeakerStreamAdapterError as exc:
        assert "seq discontinuity" in str(exc)
    else:
        raise AssertionError("speaker stream adapter accepted a discontinuous request final")


def test_speaker_stream_adapter_rejects_input_close_before_audio() -> None:
    node = FakeDoraNode([_input_closed()])

    try:
        run_speaker_stream_adapter_events(node, _config())
    except SpeakerStreamAdapterError as exc:
        assert "before any audio chunk" in str(exc)
    else:
        raise AssertionError("speaker stream adapter accepted an empty stream")
