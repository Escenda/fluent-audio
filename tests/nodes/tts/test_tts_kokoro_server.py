from __future__ import annotations

import numpy as np
import pytest

from fluent_dialogue_dora.contracts import TtsTextChunk
from nodes.tts.tts_backend.main import (
    TtsBackendAudioChunkEvent,
    TtsBackendAudioDoneEvent,
    TtsBackendPostRequest,
    parse_tts_backend_event_line,
)
from nodes.tts.tts_kokoro_server.main import (
    KokoroBackend,
    KokoroServerConfig,
    TtsKokoroServerError,
    synthesize_ndjson_lines,
)


class FakeKokoroRuntime:
    def __init__(self, waveform: np.ndarray, sample_rate_hz: int = 24_000) -> None:
        self._waveform = waveform
        self._sample_rate_hz = sample_rate_hz
        self.calls: list[tuple[str, str]] = []

    def synthesize(self, text: str, voice: str) -> tuple[np.ndarray, int]:
        self.calls.append((text, voice))
        return self._waveform, self._sample_rate_hz


def _config(**overrides) -> KokoroServerConfig:
    values = {
        "audio_source_id": "tts_test",
        "audio_stream_id": "tts/test",
        "default_voice_id": "jf_alpha",
        "chunk_frames": 4,
        "output_sample_rate_hz": 48_000,
    }
    values.update(overrides)
    return KokoroServerConfig(**values)


def _request(*, voice_id: str = "") -> TtsBackendPostRequest:
    return TtsBackendPostRequest(
        chunk=TtsTextChunk(
            request_id="tts-1",
            session_id="session-1",
            user_turn_id="turn-1",
            assistant_turn_id="assistant-1",
            seq=0,
            text="こんにちは",
            is_final=True,
        ),
        voice_id=voice_id,
    )


def test_kokoro_server_emits_ndjson_chunks_resampled_to_output_rate() -> None:
    runtime = FakeKokoroRuntime(np.zeros(24, dtype=np.float32), sample_rate_hz=24_000)
    config = _config(chunk_frames=32)
    backend = KokoroBackend(config=config, runtime=runtime)

    lines = synthesize_ndjson_lines(config, backend, _request())
    events = tuple(parse_tts_backend_event_line(line) for line in lines)

    # 24 frames at 24 kHz become 48 frames at 48 kHz: 32 + 16 chunks + done.
    assert runtime.calls == [("こんにちは", "jf_alpha")]
    assert [type(event) for event in events] == [
        TtsBackendAudioChunkEvent,
        TtsBackendAudioChunkEvent,
        TtsBackendAudioDoneEvent,
    ]
    assert events[0].audio_format.sample_rate_hz == 48_000
    assert events[0].audio_frame_count == 32
    assert events[1].audio_frame_count == 16
    assert events[2].audio_sample_index == 48


def test_kokoro_backend_uses_request_voice_and_normalizes_peak() -> None:
    runtime = FakeKokoroRuntime(np.array([0.0, 2.0, -4.0], dtype=np.float32), 48_000)
    backend = KokoroBackend(config=_config(), runtime=runtime)

    synthesized = backend.synthesize(_request(voice_id="jm_kumo"))

    assert runtime.calls == [("こんにちは", "jm_kumo")]
    samples = np.frombuffer(synthesized.audio_bytes, dtype="<f4")
    assert synthesized.sample_rate_hz == 48_000
    assert float(np.max(np.abs(samples))) <= 1.0


def test_kokoro_backend_rejects_non_finite_waveform() -> None:
    runtime = FakeKokoroRuntime(np.array([0.0, np.nan], dtype=np.float32))
    backend = KokoroBackend(config=_config(), runtime=runtime)

    with pytest.raises(TtsKokoroServerError, match="non-finite"):
        backend.synthesize(_request())
