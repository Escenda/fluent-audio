import pytest

from fluent_audio.contracts import AudioChunk, AudioFormat
from fluent_audio.dora import encode_audio_chunk_for_dora, encode_audio_final_marker_for_dora
from nodes.audio_device.audio_probe.main import (
    AudioProbeError,
    amplitude_to_dbfs,
    run_probe_dora,
    validate_summary,
)


def _audio_format() -> AudioFormat:
    return AudioFormat(
        sample_rate_hz=48_000,
        channels=1,
        sample_format="s16le",
        channel_layout="interleaved",
    )


def _chunk(*, seq: int, sample_index: int, payload: bytes) -> AudioChunk:
    frame_count = len(payload) // _audio_format().frame_size_bytes
    return AudioChunk(
        source_id="cpal_capture",
        stream_id="audio/cpal_capture/smoke",
        seq=seq,
        sample_index=sample_index,
        capture_time_ns=(sample_index * 1_000_000_000) // 48_000,
        frame_count=frame_count,
        format=_audio_format(),
        payload=payload,
    )


def _input_event(chunk: AudioChunk):
    payload, metadata = encode_audio_chunk_for_dora(chunk)
    return {
        "type": "INPUT",
        "id": "audio",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _final_event(*, seq: int, sample_index: int):
    payload, metadata = encode_audio_final_marker_for_dora(
        source_id="cpal_capture",
        stream_id="audio/cpal_capture/smoke",
        seq=seq,
        sample_index=sample_index,
        capture_time_ns=(sample_index * 1_000_000_000) // 48_000,
        audio_format=_audio_format(),
    )
    return {
        "type": "INPUT",
        "id": "audio",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def test_audio_probe_reports_amplitude_metrics_for_nonzero_s16le_payload() -> None:
    first = _chunk(
        seq=0,
        sample_index=0,
        payload=(
            (0).to_bytes(2, "little", signed=True)
            + (16_384).to_bytes(2, "little", signed=True)
        ),
    )
    second = _chunk(
        seq=1,
        sample_index=2,
        payload=(
            (-32_768).to_bytes(2, "little", signed=True)
            + (0).to_bytes(2, "little", signed=True)
        ),
    )

    summary = run_probe_dora(
        [_input_event(first), _input_event(second), _final_event(seq=2, sample_index=4)],
        expected_format=_audio_format(),
        source_id="cpal_capture",
        stream_id="audio/cpal_capture/smoke",
    )

    assert summary.chunks == 2
    assert summary.frames == 4
    assert summary.bytes == 8
    assert summary.nonzero_samples == 2
    assert summary.peak_dbfs == 0.0
    assert summary.rms_dbfs > -10.0


def test_audio_probe_validates_minimum_nonzero_samples_and_peak() -> None:
    summary = run_probe_dora(
        [
            _input_event(_chunk(seq=0, sample_index=0, payload=b"\x00\x00\x00\x00")),
            _final_event(seq=1, sample_index=2),
        ],
        expected_format=_audio_format(),
        source_id="cpal_capture",
        stream_id="audio/cpal_capture/smoke",
    )

    with pytest.raises(AudioProbeError, match="nonzero sample count below expectation"):
        validate_summary(
            summary,
            expected_chunks=1,
            expected_frames=2,
            expected_bytes=4,
            expected_min_nonzero_samples=1,
        )

    with pytest.raises(AudioProbeError, match="peak dBFS below expectation"):
        validate_summary(
            summary,
            expected_chunks=1,
            expected_frames=2,
            expected_bytes=4,
            expected_min_peak_dbfs=-60.0,
        )


def test_amplitude_to_dbfs_floors_silence_for_stable_diagnostics() -> None:
    assert amplitude_to_dbfs(0.0) == -120.0
