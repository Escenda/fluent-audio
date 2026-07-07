from pathlib import Path

import pyarrow as pa
import pytest

from fluent_dialogue_dora.contracts import AudioChunk, AudioFormat
from fluent_dialogue_dora.dora import (
    decode_audio_level_event_from_dora,
    decode_voice_activity_event_from_dora,
    encode_audio_chunk_for_dora,
    encode_audio_final_marker_for_dora,
    validate_dora_audio_level_metadata,
    validate_dora_voice_activity_final_marker,
    validate_dora_voice_activity_metadata,
)
from nodes.vad.silero.main import VadNodeConfig, VadNodeError, run_vad_events

FIXTURE_DIR = Path(__file__).parents[2] / "fixtures" / "vad"
SPEECH_FIXTURE = FIXTURE_DIR / "harvard_16k_mono_32768f.s16le"
SILENCE_FIXTURE = FIXTURE_DIR / "silence_16k_mono_1024f.s16le"


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


def _vad_config() -> VadNodeConfig:
    return VadNodeConfig(
        input_source_id="fixture",
        input_stream_id="audio/vad/input",
        output_source_id="silero_vad",
        output_stream_id="activity/vad",
        threshold=0.5,
    )


def _chunk(
    *,
    seq: int,
    sample_index: int,
    payload: bytes,
    audio_format: AudioFormat | None = None,
) -> AudioChunk:
    resolved_format = audio_format or _audio_format()
    frame_count = len(payload) // resolved_format.frame_size_bytes
    return AudioChunk(
        source_id="fixture",
        stream_id="audio/vad/input",
        seq=seq,
        sample_index=sample_index,
        capture_time_ns=(sample_index * 1_000_000_000) // resolved_format.sample_rate_hz,
        frame_count=frame_count,
        format=resolved_format,
        payload=payload,
    )


def _dora_input_event(chunk: AudioChunk):
    payload, metadata = encode_audio_chunk_for_dora(chunk)
    return {
        "type": "INPUT",
        "id": "audio",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _dora_final_event(
    *,
    seq: int,
    sample_index: int,
    audio_format: AudioFormat | None = None,
):
    resolved_format = audio_format or _audio_format()
    payload, metadata = encode_audio_final_marker_for_dora(
        source_id="fixture",
        stream_id="audio/vad/input",
        seq=seq,
        sample_index=sample_index,
        capture_time_ns=(sample_index * 1_000_000_000) // resolved_format.sample_rate_hz,
        audio_format=resolved_format,
    )
    return {
        "type": "INPUT",
        "id": "audio",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _fixture_events(path: Path, *, chunk_frames: int = 512):
    payload = path.read_bytes()
    bytes_per_chunk = chunk_frames * _audio_format().frame_size_bytes
    events = []
    seq = 0
    sample_index = 0
    for offset in range(0, len(payload), bytes_per_chunk):
        chunk_payload = payload[offset : offset + bytes_per_chunk]
        chunk = _chunk(seq=seq, sample_index=sample_index, payload=chunk_payload)
        events.append(_dora_input_event(chunk))
        seq = chunk.next_seq
        sample_index = chunk.next_sample_index
    events.append(_dora_final_event(seq=seq, sample_index=sample_index))
    return events


class FakeDoraNode:
    def __init__(self, events) -> None:
        self._events = events
        self.sent = []

    def __iter__(self):
        return iter(self._events)

    def send_output(self, output_id, data, metadata=None) -> None:
        self.sent.append((output_id, data, metadata))


def _decode_activity_outputs(fake_node: FakeDoraNode):
    activity_events = []
    level_events = []
    final_marker = None
    for output_id, payload, metadata in fake_node.sent:
        assert isinstance(payload, pa.UInt8Array)
        assert metadata is not None
        if output_id == "meter":
            level_events.append(
                decode_audio_level_event_from_dora(
                    payload,
                    validate_dora_audio_level_metadata(metadata),
                )
            )
            continue
        assert output_id == "activity"
        activity_metadata = validate_dora_voice_activity_metadata(metadata)
        if activity_metadata.final:
            final_marker = validate_dora_voice_activity_final_marker(payload, activity_metadata)
        else:
            activity_events.append(decode_voice_activity_event_from_dora(payload, activity_metadata))
    assert final_marker is not None
    return activity_events, final_marker, level_events


def test_vad_dora_node_emits_speech_events_and_final_marker() -> None:
    fake_node = FakeDoraNode(_fixture_events(SPEECH_FIXTURE))

    summary = run_vad_events(fake_node, _vad_config())
    activity_events, final_marker, level_events = _decode_activity_outputs(fake_node)

    assert summary.input_chunks == 64
    assert summary.input_frames == 32_768
    assert summary.activity_events == 64
    assert summary.level_events == 8
    assert summary.speech_events >= 1
    assert summary.final_sample_index == 32_768
    assert len(activity_events) == 64
    assert sum(1 for event in activity_events if event.state == "speech") >= 1
    assert [event.seq for event in activity_events] == list(range(64))
    assert [event.sample_index for event in activity_events[:3]] == [0, 512, 1024]
    assert {event.frame_count for event in activity_events} == {512}
    assert final_marker.seq == 64
    assert final_marker.sample_index == 32_768
    assert [event.seq for event in level_events] == list(range(8))
    assert [event.sample_index for event in level_events[:3]] == [0, 4096, 8192]
    assert all(event.stream_id == "activity/vad/level" for event in level_events)
    assert all(event.peak_dbfs <= 0.0 for event in level_events)


def test_vad_dora_node_keeps_silence_below_threshold() -> None:
    fake_node = FakeDoraNode(_fixture_events(SILENCE_FIXTURE))

    summary = run_vad_events(fake_node, _vad_config())
    activity_events, final_marker, level_events = _decode_activity_outputs(fake_node)

    assert summary.activity_events == 2
    assert summary.level_events == 1
    assert summary.speech_events == 0
    assert all(event.state == "silence" for event in activity_events)
    assert final_marker.sample_index == 1024
    assert level_events[0].peak_dbfs == -120.0


def test_vad_dora_node_reports_final_partial_window_as_audio_span() -> None:
    payload = b"\x00\x00" * 768
    first = _chunk(seq=0, sample_index=0, payload=payload[: 512 * 2])
    second = _chunk(seq=1, sample_index=512, payload=payload[512 * 2 :])
    fake_node = FakeDoraNode(
        [
            _dora_input_event(first),
            _dora_input_event(second),
            _dora_final_event(seq=2, sample_index=768),
        ]
    )

    summary = run_vad_events(fake_node, _vad_config())
    activity_events, final_marker, level_events = _decode_activity_outputs(fake_node)

    assert summary.activity_events == 2
    assert summary.level_events == 1
    assert [event.sample_index for event in activity_events] == [0, 512]
    assert [event.frame_count for event in activity_events] == [512, 256]
    assert final_marker.sample_index == 768
    assert level_events[0].sample_index == 0


def test_vad_dora_node_final_partial_window_preserves_real_end_sample() -> None:
    payload = SPEECH_FIXTURE.read_bytes()[: 640 * _audio_format().frame_size_bytes]
    first = _chunk(seq=0, sample_index=10, payload=payload)
    fake_node = FakeDoraNode(
        [
            _dora_input_event(first),
            _dora_final_event(seq=1, sample_index=650),
        ]
    )

    run_vad_events(fake_node, _vad_config())
    activity_events, final_marker, level_events = _decode_activity_outputs(fake_node)

    assert [event.sample_index for event in activity_events] == [10, 522]
    assert [event.frame_count for event in activity_events] == [512, 128]
    assert final_marker.sample_index == 650
    assert level_events[0].sample_index == 10


def test_vad_dora_node_rejects_format_mismatch() -> None:
    wrong_format = _audio_format(sample_rate_hz=48_000)
    chunk = _chunk(seq=0, sample_index=0, payload=b"\x00\x00" * 512, audio_format=wrong_format)
    fake_node = FakeDoraNode(
        [
            _dora_input_event(chunk),
            _dora_final_event(seq=1, sample_index=512, audio_format=wrong_format),
        ]
    )

    with pytest.raises(VadNodeError, match="format mismatch"):
        run_vad_events(fake_node, _vad_config())


def test_vad_dora_node_rejects_sequence_discontinuity() -> None:
    first = _chunk(seq=0, sample_index=0, payload=b"\x00\x00" * 512)
    second = _chunk(seq=2, sample_index=512, payload=b"\x00\x00" * 512)
    fake_node = FakeDoraNode(
        [
            _dora_input_event(first),
            _dora_input_event(second),
            _dora_final_event(seq=3, sample_index=1024),
        ]
    )

    with pytest.raises(VadNodeError, match="sequence discontinuity"):
        run_vad_events(fake_node, _vad_config())


def test_vad_dora_node_rejects_missing_final_marker() -> None:
    fake_node = FakeDoraNode(
        [_dora_input_event(_chunk(seq=0, sample_index=0, payload=b"\x00\x00" * 512))]
    )

    with pytest.raises(VadNodeError, match="without final marker"):
        run_vad_events(fake_node, _vad_config())


def test_vad_dora_node_rejects_stop_and_input_closed_before_final_marker() -> None:
    first = _dora_input_event(_chunk(seq=0, sample_index=0, payload=b"\x00\x00" * 512))

    with pytest.raises(VadNodeError, match="STOP arrived before audio final marker"):
        run_vad_events(FakeDoraNode([first, {"type": "STOP"}]), _vad_config())

    with pytest.raises(VadNodeError, match="input closed before audio final marker"):
        run_vad_events(
            FakeDoraNode([first, {"type": "INPUT_CLOSED", "id": "audio"}]),
            _vad_config(),
        )

    with pytest.raises(VadNodeError, match="input closed before audio final marker"):
        run_vad_events(
            FakeDoraNode([{"type": "INPUT_CLOSED", "id": "audio"}]),
            _vad_config(),
        )


def test_vad_dora_node_rejects_final_marker_before_audio_chunks() -> None:
    fake_node = FakeDoraNode([_dora_final_event(seq=0, sample_index=0)])

    with pytest.raises(VadNodeError, match="final marker before audio chunks"):
        run_vad_events(fake_node, _vad_config())
