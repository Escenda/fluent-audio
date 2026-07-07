import pytest

from fluent_dialogue_dora.contracts import AsrCancel, AsrStart, AsrStop, AudioChunk, AudioFormat
from nodes.asr.nemotron_streaming.logic import (
    AsrBackendFinalResult,
    AsrBackendPushResult,
    NemotronStreamingConfig,
    NemotronStreamingError,
    NemotronStreamingRuntime,
    StreamingAsrBackend,
    slice_audio_chunk,
)


class CollectingBackend(StreamingAsrBackend):
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
        return AsrBackendPushResult(partial_texts=(f"frames={pushed_frames}",))

    def stop(self, control: AsrStop) -> AsrBackendFinalResult:
        self.stopped.append(control)
        pushed_frames = sum(item.frame_count for item in self.pushed)
        return AsrBackendFinalResult(text=f"final frames={pushed_frames}")

    def cancel(self, control: AsrCancel) -> None:
        self.cancelled.append(control)


class EmptyFinalBackend(CollectingBackend):
    def push_audio(self, chunk: AudioChunk) -> AsrBackendPushResult:
        self.pushed.append(chunk)
        return AsrBackendPushResult()

    def stop(self, control: AsrStop) -> AsrBackendFinalResult:
        self.stopped.append(control)
        return AsrBackendFinalResult(text="")


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


def _config(
    *,
    prebuffer_frames: int = 2048,
    control_holdback_frames: int = 0,
    late_stop_tolerance_frames: int = 16000,
) -> NemotronStreamingConfig:
    return NemotronStreamingConfig(
        input_audio_source_id="media_graph",
        input_audio_stream_id="audio/asr/input",
        output_stream_id="transcript/main",
        expected_audio_format=_audio_format(),
        prebuffer_frames=prebuffer_frames,
        control_holdback_frames=control_holdback_frames,
        late_stop_tolerance_frames=late_stop_tolerance_frames,
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


def _start(
    *,
    seq: int = 0,
    start_sample_index: int = 0,
    user_turn_id: str = "user-turn-1",
) -> AsrStart:
    return AsrStart(
        action="start",
        session_id="session-1",
        user_turn_id=user_turn_id,
        stream_id="audio/asr/input",
        seq=seq,
        start_sample_index=start_sample_index,
    )


def _stop(
    *,
    seq: int = 1,
    stop_sample_index: int = 0,
    user_turn_id: str = "user-turn-1",
) -> AsrStop:
    return AsrStop(
        action="stop",
        session_id="session-1",
        user_turn_id=user_turn_id,
        stream_id="audio/asr/input",
        seq=seq,
        stop_sample_index=stop_sample_index,
    )


def _cancel(*, seq: int = 1) -> AsrCancel:
    return AsrCancel(
        action="cancel",
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="audio/asr/input",
        seq=seq,
        reason="barge-in",
    )


def test_slice_audio_chunk_preserves_requested_sample_span() -> None:
    chunk = _chunk(seq=3, sample_index=100, frame_count=10)

    sliced = slice_audio_chunk(chunk, start_sample_index=103, end_sample_index=108)

    assert sliced.seq == 3
    assert sliced.sample_index == 103
    assert sliced.frame_count == 5
    assert sliced.next_sample_index == 108
    assert sliced.payload == bytes([3]) * (5 * _audio_format().frame_size_bytes)
    assert sliced.capture_time_ns == chunk.capture_time_ns + (3 * 1_000_000_000) // 16_000


def test_start_replays_retained_prebuffer_and_stop_emits_final() -> None:
    backend = CollectingBackend()
    runtime = NemotronStreamingRuntime(_config(), backend)
    runtime.push_audio(_chunk(seq=0, sample_index=0))
    runtime.push_audio(_chunk(seq=1, sample_index=512))

    start_events = runtime.push_control(_start(start_sample_index=256))
    live_events = runtime.push_audio(_chunk(seq=2, sample_index=1024))
    final_events = runtime.push_control(_stop(stop_sample_index=1536))

    assert [event.text for event in start_events] == ["frames=256", "frames=768"]
    assert [event.text for event in live_events] == ["frames=1280"]
    assert len(final_events) == 1
    assert final_events[0].text == "final frames=1280"
    assert final_events[0].start_sample_index == 256
    assert final_events[0].end_sample_index == 1536
    assert [chunk.sample_index for chunk in backend.pushed] == [256, 512, 1024]
    assert [chunk.frame_count for chunk in backend.pushed] == [256, 512, 512]


def test_stop_can_wait_for_future_audio_before_finalizing() -> None:
    backend = CollectingBackend()
    runtime = NemotronStreamingRuntime(_config(), backend)

    assert runtime.push_control(_start(start_sample_index=0)) == []
    assert runtime.push_audio(_chunk(seq=0, sample_index=0))[-1].text == "frames=512"
    assert runtime.push_control(_stop(stop_sample_index=1024)) == []

    events = runtime.push_audio(_chunk(seq=1, sample_index=512))

    assert [event.text for event in events] == ["frames=1024", "final frames=1024"]
    assert runtime.active_turn is None


def test_next_turn_start_waits_while_previous_stop_waits_for_audio() -> None:
    backend = CollectingBackend()
    runtime = NemotronStreamingRuntime(_config(), backend)

    assert runtime.push_control(_start(seq=0, start_sample_index=0)) == []
    assert runtime.push_control(_stop(seq=1, stop_sample_index=1024)) == []
    assert (
        runtime.push_control(
            _start(seq=2, start_sample_index=1024, user_turn_id="user-turn-2")
        )
        == []
    )

    events = runtime.push_audio(_chunk(seq=0, sample_index=0, frame_count=2048))

    assert [event.text for event in events] == [
        "frames=1024",
        "final frames=1024",
        "frames=2048",
    ]
    assert [control.user_turn_id for control, _audio_format in backend.started] == [
        "user-turn-1",
        "user-turn-2",
    ]
    assert [control.user_turn_id for control in backend.stopped] == ["user-turn-1"]
    assert runtime.active_turn is not None
    assert runtime.active_turn.user_turn_id == "user-turn-2"


def test_pending_stop_slices_audio_chunk_at_stop_sample() -> None:
    backend = CollectingBackend()
    runtime = NemotronStreamingRuntime(_config(), backend)
    runtime.push_control(_start(start_sample_index=0))
    runtime.push_control(_stop(stop_sample_index=256))

    events = runtime.push_audio(_chunk(seq=0, sample_index=0))

    assert [event.text for event in events] == ["frames=256", "final frames=256"]
    assert [chunk.frame_count for chunk in backend.pushed] == [256]
    assert runtime.active_turn is None


def test_empty_backend_final_consumes_turn_without_transcript_final() -> None:
    backend = EmptyFinalBackend()
    runtime = NemotronStreamingRuntime(_config(), backend)

    runtime.push_control(_start(start_sample_index=0))
    assert runtime.push_audio(_chunk(seq=0, sample_index=0)) == []
    final_events = runtime.push_control(_stop(stop_sample_index=512))

    assert final_events == []
    assert runtime.active_turn is None
    assert len(backend.stopped) == 1


def test_start_fails_when_required_prebuffer_was_pruned() -> None:
    backend = CollectingBackend()
    runtime = NemotronStreamingRuntime(_config(prebuffer_frames=512), backend)
    runtime.push_audio(_chunk(seq=0, sample_index=0))
    runtime.push_audio(_chunk(seq=1, sample_index=512))
    runtime.push_audio(_chunk(seq=2, sample_index=1024))

    with pytest.raises(NemotronStreamingError, match="older than retained prebuffer"):
        runtime.push_control(_start(start_sample_index=0))


def test_stop_fails_when_audio_already_pushed_beyond_stop() -> None:
    backend = CollectingBackend()
    runtime = NemotronStreamingRuntime(_config(late_stop_tolerance_frames=0), backend)
    runtime.push_control(_start(start_sample_index=0))
    runtime.push_audio(_chunk(seq=0, sample_index=0))

    with pytest.raises(NemotronStreamingError, match="behind audio already pushed"):
        runtime.push_control(_stop(stop_sample_index=256))


def test_late_stop_within_tolerance_finalizes_at_pushed_audio_boundary() -> None:
    backend = CollectingBackend()
    runtime = NemotronStreamingRuntime(_config(late_stop_tolerance_frames=512), backend)
    runtime.push_control(_start(start_sample_index=0))
    runtime.push_audio(_chunk(seq=0, sample_index=0))

    final_events = runtime.push_control(_stop(stop_sample_index=256))

    assert len(final_events) == 1
    assert final_events[0].text == "final frames=512"
    assert final_events[0].start_sample_index == 0
    assert final_events[0].end_sample_index == 512
    assert backend.stopped[0].stop_sample_index == 512
    assert runtime.active_turn is None


def test_control_holdback_prevents_late_stop_from_overshooting_backend() -> None:
    backend = CollectingBackend()
    runtime = NemotronStreamingRuntime(
        _config(prebuffer_frames=4096, control_holdback_frames=1024),
        backend,
    )

    runtime.push_control(_start(start_sample_index=0))
    assert runtime.push_audio(_chunk(seq=0, sample_index=0)) == []
    assert runtime.push_audio(_chunk(seq=1, sample_index=512)) == []
    assert [event.text for event in runtime.push_audio(_chunk(seq=2, sample_index=1024))] == [
        "frames=512"
    ]
    assert [event.text for event in runtime.push_audio(_chunk(seq=3, sample_index=1536))] == [
        "frames=1024"
    ]

    final_events = runtime.push_control(_stop(stop_sample_index=1536))

    assert [event.text for event in final_events] == ["frames=1536", "final frames=1536"]
    assert [chunk.sample_index for chunk in backend.pushed] == [0, 512, 1024]
    assert [chunk.frame_count for chunk in backend.pushed] == [512, 512, 512]
    assert runtime.active_turn is None


def test_cancel_drops_active_turn_without_final_transcript() -> None:
    backend = CollectingBackend()
    runtime = NemotronStreamingRuntime(_config(), backend)
    runtime.push_control(_start(start_sample_index=0))

    assert runtime.push_control(_cancel()) == []
    assert runtime.active_turn is None
    assert len(backend.cancelled) == 1


def test_rejects_audio_format_source_stream_and_sequence_mismatch() -> None:
    wrong_source_runtime = NemotronStreamingRuntime(_config(), CollectingBackend())
    with pytest.raises(NemotronStreamingError, match="source mismatch"):
        wrong_source_runtime.push_audio(_chunk(seq=0, sample_index=0, source_id="other"))

    wrong_stream_runtime = NemotronStreamingRuntime(_config(), CollectingBackend())
    with pytest.raises(NemotronStreamingError, match="stream mismatch"):
        wrong_stream_runtime.push_audio(_chunk(seq=0, sample_index=0, stream_id="other"))

    wrong_format_runtime = NemotronStreamingRuntime(_config(), CollectingBackend())
    with pytest.raises(NemotronStreamingError, match="format mismatch"):
        wrong_format_runtime.push_audio(
            _chunk(seq=0, sample_index=0, audio_format=_audio_format(sample_rate_hz=48_000))
        )

    idle_discontinuity_runtime = NemotronStreamingRuntime(_config(), CollectingBackend())
    idle_discontinuity_runtime.push_audio(_chunk(seq=0, sample_index=0))
    assert idle_discontinuity_runtime.push_audio(_chunk(seq=2, sample_index=1024)) == []
    assert idle_discontinuity_runtime.latest_audio_sample_index == 1536

    active_discontinuity_runtime = NemotronStreamingRuntime(_config(), CollectingBackend())
    active_discontinuity_runtime.push_audio(_chunk(seq=0, sample_index=0))
    active_discontinuity_runtime.push_control(_start(start_sample_index=0))
    with pytest.raises(NemotronStreamingError, match="discontinuity"):
        active_discontinuity_runtime.push_audio(_chunk(seq=2, sample_index=512))


def test_rejects_control_stream_and_sequence_mismatch() -> None:
    wrong_stream = AsrStart(
        action="start",
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="other",
        seq=0,
        start_sample_index=0,
    )
    runtime = NemotronStreamingRuntime(_config(), CollectingBackend())
    with pytest.raises(NemotronStreamingError, match="control stream mismatch"):
        runtime.push_control(wrong_stream)

    runtime = NemotronStreamingRuntime(_config(), CollectingBackend())
    with pytest.raises(NemotronStreamingError, match="control seq discontinuity"):
        runtime.push_control(_start(seq=2))


def test_finish_audio_rejects_active_turn() -> None:
    runtime = NemotronStreamingRuntime(_config(), CollectingBackend())
    runtime.push_audio(_chunk(seq=0, sample_index=0))
    runtime.push_control(_start(start_sample_index=0))

    with pytest.raises(NemotronStreamingError, match="still active"):
        runtime.finish_audio(512)
