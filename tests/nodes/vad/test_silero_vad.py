from pathlib import Path

import numpy as np
import pytest
from pydantic import ValidationError

from nodes.vad.silero.silero import (
    DEFAULT_MODEL_PATH,
    EXPECTED_MODEL_SHA256,
    SileroVadConfig,
    SileroVadError,
    SileroVadSession,
    pad_final_window,
    s16le_mono_16k_to_float32_waveform,
    sha256_file,
)

FIXTURE_DIR = Path(__file__).parents[2] / "fixtures" / "vad"
SPEECH_FIXTURE = FIXTURE_DIR / "harvard_16k_mono_32768f.s16le"
SILENCE_FIXTURE = FIXTURE_DIR / "silence_16k_mono_1024f.s16le"


def _fixture_waveform(path: Path) -> np.ndarray:
    return s16le_mono_16k_to_float32_waveform(path.read_bytes())


def _probabilities(path: Path) -> list[float]:
    session = SileroVadSession(SileroVadConfig())
    results = session.push(_fixture_waveform(path))
    results.extend(session.flush())
    return [result.probability for result in results]


def test_model_hash_matches_pinned_onnx_file() -> None:
    assert sha256_file(DEFAULT_MODEL_PATH) == EXPECTED_MODEL_SHA256
    assert SileroVadConfig().model_path == DEFAULT_MODEL_PATH


def test_config_rejects_model_hash_mismatch(tmp_path: Path) -> None:
    model_path = tmp_path / "silero_vad_16k_op15.onnx"
    model_path.write_bytes(b"not the pinned model")

    with pytest.raises(ValidationError, match="Silero ONNX model sha256 mismatch"):
        SileroVadConfig(model_path=model_path)


def test_s16le_mono_16k_to_float32_waveform_validates_format() -> None:
    waveform = s16le_mono_16k_to_float32_waveform(b"\x00\x00\x00\x40\x00\x80")

    assert waveform.dtype == np.float32
    assert waveform.tolist() == [0.0, 0.5, -1.0]

    with pytest.raises(SileroVadError, match="16000 Hz"):
        s16le_mono_16k_to_float32_waveform(b"\x00\x00", sample_rate_hz=8_000)
    with pytest.raises(SileroVadError, match="byte length must be even"):
        s16le_mono_16k_to_float32_waveform(b"\x00")


def test_push_buffers_partial_window_and_flush_zero_pads() -> None:
    session = SileroVadSession(SileroVadConfig())
    partial = np.zeros((128,), dtype=np.float32)

    assert session.push(partial) == []
    assert session.buffered_frames == 128

    flushed = session.flush()

    assert len(flushed) == 1
    assert flushed[0].window_start_frame == 0
    assert flushed[0].padded_frames == 384
    assert session.buffered_frames == 0


def test_pad_final_window_is_explicit_and_shape_checked() -> None:
    partial = np.ones((4,), dtype=np.float32)
    padded = pad_final_window(partial, window_frames=8)

    assert padded.dtype == np.float32
    assert padded.tolist() == [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0]

    with pytest.raises(SileroVadError, match="cannot exceed"):
        pad_final_window(np.zeros((9,), dtype=np.float32), window_frames=8)
    with pytest.raises(SileroVadError, match="float32 waveform"):
        pad_final_window(np.zeros((4,), dtype=np.float64), window_frames=8)


def test_speech_fixture_crosses_threshold_with_contextual_session_inference() -> None:
    probabilities = _probabilities(SPEECH_FIXTURE)

    assert len(probabilities) == 64
    assert max(probabilities) > 0.5


def test_silence_fixture_stays_below_threshold() -> None:
    probabilities = _probabilities(SILENCE_FIXTURE)

    assert len(probabilities) == 2
    assert max(probabilities) < 0.5


def test_push_requires_float32_mono_waveform() -> None:
    session = SileroVadSession(SileroVadConfig())

    with pytest.raises(SileroVadError, match="float32 waveform"):
        session.push(np.zeros((512,), dtype=np.float64))
    with pytest.raises(SileroVadError, match="mono waveform"):
        session.push(np.zeros((1, 512), dtype=np.float32))
