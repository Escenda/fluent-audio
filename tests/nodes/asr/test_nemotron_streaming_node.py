import pytest

from fluent_audio.contracts import AsrCancel, AsrStart, AsrStop, AudioChunk, AudioFormat
from fluent_audio.dora import (
    decode_transcript_delta_from_dora,
    decode_transcript_final_from_dora,
    decode_transcript_partial_from_dora,
    encode_asr_control_for_dora,
    encode_asr_control_final_marker_for_dora,
    encode_audio_chunk_for_dora,
    encode_audio_final_marker_for_dora,
    validate_dora_transcript_metadata,
    validate_dora_transcript_stream_final_marker,
)
from nodes.asr.nemotron_streaming.logic import (
    AsrBackendFinalResult,
    AsrBackendPushResult,
    StreamingAsrBackend,
)
from nodes.asr.nemotron_streaming.main import (
    NemotronStreamingNodeConfig,
    NemotronStreamingNodeError,
    run_nemotron_streaming_events,
    warmup_streaming_backend,
)


class CountingBackend(StreamingAsrBackend):
    def __init__(self) -> None:
        self.started = []
        self.pushed = []
        self.stopped = []
        self.cancelled = []

    def start(self, control: AsrStart, audio_format: AudioFormat) -> None:
        self.started.append((control, audio_format))

    def push_audio(self, chunk: AudioChunk) -> AsrBackendPushResult:
        self.pushed.append(chunk)
        pushed_frames = sum(item.frame_count for item in self.pushed)
        return AsrBackendPushResult(delta_texts=(f"frames={pushed_frames}",))

    def stop(self, control: AsrStop) -> AsrBackendFinalResult:
        self.stopped.append(control)
        pushed_frames = sum(item.frame_count for item in self.pushed)
        return AsrBackendFinalResult(text=f"final frames={pushed_frames}")

    def cancel(self, control: AsrCancel) -> None:
        self.cancelled.append(control)


class EmptyFinalBackend(CountingBackend):
    def push_audio(self, chunk: AudioChunk) -> AsrBackendPushResult:
        self.pushed.append(chunk)
        return AsrBackendPushResult()

    def stop(self, control: AsrStop) -> AsrBackendFinalResult:
        self.stopped.append(control)
        return AsrBackendFinalResult(text="")


class PartialBackend(CountingBackend):
    def push_audio(self, chunk: AudioChunk) -> AsrBackendPushResult:
        self.pushed.append(chunk)
        pushed_frames = sum(item.frame_count for item in self.pushed)
        return AsrBackendPushResult(
            partial_texts=(f"partial frames={pushed_frames}",),
            delta_texts=(f"frames={pushed_frames}",),
        )


class FakeDoraNode:
    def __init__(self, events) -> None:
        self._events = events
        self.sent = []

    def __iter__(self):
        return iter(self._events)

    def send_output(self, output_id, data, metadata=None) -> None:
        self.sent.append((output_id, data, metadata))


def _audio_format(
    *,
    sample_rate_hz: int = 16_000,
    channels: int = 1,
    sample_format: str = "s16le",
) -> AudioFormat:
    return AudioFormat(
        sample_rate_hz=sample_rate_hz,
        channels=channels,
        sample_format=sample_format,
        channel_layout="interleaved",
    )


def _config(*, prebuffer_frames: int = 2048) -> NemotronStreamingNodeConfig:
    return NemotronStreamingNodeConfig(
        input_audio_source_id="media_graph",
        input_audio_stream_id="audio/asr/input",
        session_id="session-1",
        output_stream_id="transcript/main",
        prebuffer_frames=prebuffer_frames,
        control_holdback_frames=0,
    )


def _chunk(
    *,
    seq: int,
    sample_index: int,
    frame_count: int = 512,
    audio_format: AudioFormat | None = None,
    source_id: str = "media_graph",
    stream_id: str = "audio/asr/input",
) -> AudioChunk:
    resolved_format = audio_format or _audio_format()
    payload = bytes([seq % 256]) * (frame_count * resolved_format.frame_size_bytes)
    return AudioChunk(
        source_id=source_id,
        stream_id=stream_id,
        seq=seq,
        sample_index=sample_index,
        capture_time_ns=(sample_index * 1_000_000_000) // resolved_format.sample_rate_hz,
        frame_count=frame_count,
        format=resolved_format,
        payload=payload,
    )


def _start(*, seq: int = 0, start_sample_index: int = 0) -> AsrStart:
    return AsrStart(
        action="start",
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="audio/asr/input",
        seq=seq,
        start_sample_index=start_sample_index,
    )


def _stop(*, seq: int = 1, stop_sample_index: int = 0) -> AsrStop:
    return AsrStop(
        action="stop",
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="audio/asr/input",
        seq=seq,
        stop_sample_index=stop_sample_index,
    )


def test_warmup_streaming_backend_runs_silent_turn_before_dora_start() -> None:
    backend = CountingBackend()
    config = _config()

    warmup_streaming_backend(backend, config)

    assert len(backend.started) == 1
    assert backend.started[0][0].user_turn_id == "nemotron-warmup-turn"
    assert backend.pushed[0].sample_index == 0
    assert backend.pushed[0].frame_count == 16000
    assert backend.pushed[0].payload == bytes(16000 * _audio_format().frame_size_bytes)
    assert backend.stopped[0].stop_sample_index == 16000


def test_warmup_streaming_backend_can_be_disabled() -> None:
    backend = CountingBackend()
    config = _config().model_copy(update={"warmup_frames": 0})

    warmup_streaming_backend(backend, config)

    assert backend.started == []
    assert backend.pushed == []
    assert backend.stopped == []


def _dora_audio_event(chunk: AudioChunk):
    payload, metadata = encode_audio_chunk_for_dora(chunk)
    return {
        "type": "INPUT",
        "id": "audio",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _dora_audio_final_event(*, seq: int, sample_index: int):
    payload, metadata = encode_audio_final_marker_for_dora(
        source_id="media_graph",
        stream_id="audio/asr/input",
        seq=seq,
        sample_index=sample_index,
        capture_time_ns=(sample_index * 1_000_000_000) // 16_000,
        audio_format=_audio_format(),
    )
    return {
        "type": "INPUT",
        "id": "audio",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _dora_control_event(control: AsrStart | AsrStop):
    payload, metadata = encode_asr_control_for_dora(control)
    return {
        "type": "INPUT",
        "id": "asr_control",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _dora_control_final_event(*, seq: int):
    payload, metadata = encode_asr_control_final_marker_for_dora(
        session_id="session-1",
        stream_id="audio/asr/input",
        seq=seq,
    )
    return {
        "type": "INPUT",
        "id": "asr_control",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _decode_transcript_outputs(fake_node: FakeDoraNode):
    deltas = []
    partials = []
    finals = []
    stream_final = None
    for output_id, payload, metadata in fake_node.sent:
        assert output_id == "transcript"
        assert metadata is not None
        transcript_metadata = validate_dora_transcript_metadata(metadata)
        if transcript_metadata.kind == "delta":
            deltas.append(decode_transcript_delta_from_dora(payload, transcript_metadata))
        elif transcript_metadata.kind == "partial":
            partials.append(decode_transcript_partial_from_dora(payload, transcript_metadata))
        elif transcript_metadata.kind == "final":
            finals.append(decode_transcript_final_from_dora(payload, transcript_metadata))
        else:
            stream_final = validate_dora_transcript_stream_final_marker(
                payload,
                transcript_metadata,
            )
    assert stream_final is not None
    return deltas, partials, finals, stream_final


def test_nemotron_streaming_node_emits_transcripts_and_stream_final_marker() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_audio_event(_chunk(seq=0, sample_index=0)),
            _dora_audio_event(_chunk(seq=1, sample_index=512)),
            _dora_control_event(_start(start_sample_index=256)),
            _dora_audio_event(_chunk(seq=2, sample_index=1024)),
            _dora_control_event(_stop(stop_sample_index=1536)),
            _dora_audio_final_event(seq=3, sample_index=1536),
            _dora_control_final_event(seq=2),
        ]
    )

    summary = run_nemotron_streaming_events(fake_node, _config(), CountingBackend())
    deltas, partials, finals, stream_final = _decode_transcript_outputs(fake_node)

    assert summary.input_chunks == 3
    assert summary.input_frames == 1536
    assert summary.control_events == 2
    assert summary.transcript_deltas == 3
    assert summary.transcript_partials == 0
    assert summary.transcript_finals == 1
    assert summary.final_sample_index == 1536
    assert [delta.text for delta in deltas] == ["frames=256", "frames=768", "frames=1280"]
    assert [delta.seq for delta in deltas] == [0, 1, 2]
    assert partials == []
    assert finals[0].seq == 3
    assert finals[0].text == "final frames=1280"
    assert finals[0].start_sample_index == 256
    assert finals[0].end_sample_index == 1536
    assert stream_final.seq == 4
    assert stream_final.start_sample_index == 1536


def test_nemotron_streaming_node_emits_partial_hypotheses() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_control_event(_start(start_sample_index=0)),
            _dora_audio_event(_chunk(seq=0, sample_index=0)),
            _dora_control_event(_stop(stop_sample_index=512)),
            _dora_audio_final_event(seq=1, sample_index=512),
            _dora_control_final_event(seq=2),
        ]
    )

    summary = run_nemotron_streaming_events(fake_node, _config(), PartialBackend())
    deltas, partials, finals, stream_final = _decode_transcript_outputs(fake_node)

    assert summary.transcript_partials == 1
    assert summary.transcript_deltas == 1
    assert [partial.text for partial in partials] == ["partial frames=512"]
    assert [partial.seq for partial in partials] == [0]
    assert [delta.text for delta in deltas] == ["frames=512"]
    assert [delta.seq for delta in deltas] == [1]
    assert finals[0].seq == 2
    assert stream_final.seq == 3


def test_nemotron_streaming_node_waits_for_pending_stop() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_control_event(_start(start_sample_index=0)),
            _dora_audio_event(_chunk(seq=0, sample_index=0)),
            _dora_control_event(_stop(stop_sample_index=1024)),
            _dora_audio_event(_chunk(seq=1, sample_index=512)),
            _dora_audio_final_event(seq=2, sample_index=1024),
            _dora_control_final_event(seq=2),
        ]
    )

    summary = run_nemotron_streaming_events(fake_node, _config(), CountingBackend())
    deltas, _partials, finals, stream_final = _decode_transcript_outputs(fake_node)

    assert summary.transcript_deltas == 2
    assert summary.transcript_finals == 1
    assert [delta.text for delta in deltas] == ["frames=512", "frames=1024"]
    assert finals[0].end_sample_index == 1024
    assert stream_final.start_sample_index == 1024


def test_nemotron_streaming_node_consumes_empty_final_without_transcript_final() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_control_event(_start(start_sample_index=0)),
            _dora_audio_event(_chunk(seq=0, sample_index=0)),
            _dora_control_event(_stop(stop_sample_index=512)),
            _dora_audio_final_event(seq=1, sample_index=512),
            _dora_control_final_event(seq=2),
        ]
    )

    summary = run_nemotron_streaming_events(fake_node, _config(), EmptyFinalBackend())
    deltas, partials, finals, stream_final = _decode_transcript_outputs(fake_node)

    assert summary.transcript_deltas == 0
    assert summary.transcript_finals == 0
    assert deltas == []
    assert partials == []
    assert finals == []
    assert stream_final.start_sample_index == 512


def test_nemotron_streaming_node_accepts_audio_final_after_transport_close() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_control_event(_start(start_sample_index=0)),
            _dora_audio_event(_chunk(seq=0, sample_index=0)),
            _dora_audio_event(_chunk(seq=1, sample_index=512)),
            _dora_control_event(_stop(stop_sample_index=1024)),
            {"type": "INPUT_CLOSED", "id": "audio"},
            _dora_audio_final_event(seq=2, sample_index=1024),
            _dora_control_final_event(seq=2),
        ]
    )

    summary = run_nemotron_streaming_events(fake_node, _config(), CountingBackend())
    _deltas, _partials, finals, stream_final = _decode_transcript_outputs(fake_node)

    assert summary.input_chunks == 2
    assert summary.input_frames == 1024
    assert summary.transcript_finals == 1
    assert summary.final_sample_index == 1024
    assert finals[0].end_sample_index == 1024
    assert stream_final.start_sample_index == 1024


def test_nemotron_streaming_node_waits_for_stop_after_audio_input_closed() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_control_event(_start(start_sample_index=0)),
            _dora_audio_event(_chunk(seq=0, sample_index=0)),
            _dora_audio_event(_chunk(seq=1, sample_index=512)),
            {"type": "INPUT_CLOSED", "id": "audio"},
            _dora_control_event(_stop(stop_sample_index=1024)),
            _dora_audio_final_event(seq=2, sample_index=1024),
            _dora_control_final_event(seq=2),
        ]
    )

    summary = run_nemotron_streaming_events(fake_node, _config(), CountingBackend())
    _deltas, _partials, finals, stream_final = _decode_transcript_outputs(fake_node)

    assert summary.control_events == 2
    assert summary.transcript_finals == 1
    assert finals[0].end_sample_index == 1024
    assert stream_final.start_sample_index == 1024


def test_nemotron_streaming_node_accepts_queued_control_after_input_closed() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_control_event(_start(start_sample_index=0)),
            _dora_audio_event(_chunk(seq=0, sample_index=0)),
            _dora_audio_event(_chunk(seq=1, sample_index=512)),
            {"type": "INPUT_CLOSED", "id": "asr_control"},
            _dora_control_event(_stop(stop_sample_index=1024)),
            _dora_audio_final_event(seq=2, sample_index=1024),
            _dora_control_final_event(seq=2),
        ]
    )

    summary = run_nemotron_streaming_events(fake_node, _config(), CountingBackend())
    _deltas, _partials, finals, stream_final = _decode_transcript_outputs(fake_node)

    assert summary.control_events == 2
    assert summary.transcript_finals == 1
    assert finals[0].end_sample_index == 1024
    assert stream_final.start_sample_index == 1024


def test_nemotron_streaming_node_rejects_audio_final_while_turn_is_active() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_control_event(_start(start_sample_index=0)),
            _dora_audio_event(_chunk(seq=0, sample_index=0)),
            _dora_audio_final_event(seq=1, sample_index=512),
            _dora_control_final_event(seq=1),
        ]
    )

    with pytest.raises(NemotronStreamingNodeError, match="still active"):
        run_nemotron_streaming_events(fake_node, _config(), CountingBackend())


def test_nemotron_streaming_node_rejects_audio_input_closed_without_final_marker() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_control_event(_start(start_sample_index=0)),
            _dora_audio_event(_chunk(seq=0, sample_index=0)),
            _dora_control_event(_stop(stop_sample_index=512)),
            {"type": "INPUT_CLOSED", "id": "audio"},
            _dora_control_final_event(seq=2),
        ]
    )

    with pytest.raises(NemotronStreamingNodeError, match="before audio final marker"):
        run_nemotron_streaming_events(fake_node, _config(), CountingBackend())


def test_nemotron_streaming_node_rejects_missing_prebuffer() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_audio_event(_chunk(seq=0, sample_index=0)),
            _dora_audio_event(_chunk(seq=1, sample_index=512)),
            _dora_audio_event(_chunk(seq=2, sample_index=1024)),
            _dora_control_event(_start(start_sample_index=0)),
        ]
    )

    with pytest.raises(NemotronStreamingNodeError, match="audio error|control error"):
        run_nemotron_streaming_events(
            fake_node,
            _config(prebuffer_frames=512),
            CountingBackend(),
        )


def test_nemotron_streaming_node_accepts_audio_input_closed_without_started_turn() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_audio_event(_chunk(seq=0, sample_index=0)),
            {"type": "INPUT_CLOSED", "id": "audio"},
            _dora_audio_final_event(seq=1, sample_index=512),
            _dora_control_final_event(seq=0),
        ]
    )

    summary = run_nemotron_streaming_events(fake_node, _config(), CountingBackend())
    deltas, partials, finals, stream_final = _decode_transcript_outputs(fake_node)

    assert summary.transcript_deltas == 0
    assert summary.transcript_partials == 0
    assert summary.transcript_finals == 0
    assert summary.final_sample_index == 512
    assert deltas == []
    assert partials == []
    assert finals == []
    assert stream_final.start_sample_index == 512


def test_nemotron_streaming_node_rejects_control_after_control_final_marker() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_control_final_event(seq=0),
            _dora_control_event(_start(start_sample_index=0)),
        ]
    )

    with pytest.raises(NemotronStreamingNodeError, match="after ASR control final marker"):
        run_nemotron_streaming_events(fake_node, _config(), CountingBackend())


def test_nemotron_streaming_node_rejects_control_input_close_while_turn_is_active() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_control_event(_start(start_sample_index=0)),
            {"type": "INPUT_CLOSED", "id": "asr_control"},
        ]
    )

    with pytest.raises(NemotronStreamingNodeError, match="still active"):
        run_nemotron_streaming_events(fake_node, _config(), CountingBackend())
