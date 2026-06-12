from __future__ import annotations

import json
import tempfile
import threading
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import pytest

from fluent_audio.contracts import TtsTextChunk
from nodes.tts.tts_backend.main import (
    TtsBackendAudioChunkEvent,
    TtsBackendAudioDoneEvent,
    TtsBackendPostRequest,
    parse_tts_backend_event_line,
)
from nodes.tts.tts_pyopenjtalk_server.main import (
    PyOpenJTalkBackend,
    PyOpenJTalkServerConfig,
    TtsPyOpenJTalkServerError,
    build_server,
    synthesize_ndjson_lines,
)


class FakePyOpenJTalkRuntime:
    def __init__(self, waveform: np.ndarray, sample_rate_hz: int = 24000) -> None:
        self._waveform = waveform
        self._sample_rate_hz = sample_rate_hz
        self.calls: list[tuple[str, tuple[tuple[str, str], ...]]] = []

    def tts(self, text: str, **options: str) -> tuple[np.ndarray, int]:
        self.calls.append((text, tuple(sorted(options.items()))))
        return self._waveform, self._sample_rate_hz


def _config(dictionary_dir: Path, *, chunk_frames: int = 2) -> PyOpenJTalkServerConfig:
    return PyOpenJTalkServerConfig(
        openjtalk_dict_dir=dictionary_dir,
        audio_source_id="tts_test",
        audio_stream_id="tts/test",
        default_voice_id="",
        chunk_frames=chunk_frames,
    )


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


def test_pyopenjtalk_server_emits_ndjson_audio_chunks_and_done() -> None:
    with tempfile.TemporaryDirectory() as directory:
        runtime = FakePyOpenJTalkRuntime(np.array([0.0, 0.25, -0.5], dtype=np.float32))
        config = _config(Path(directory), chunk_frames=2)
        backend = PyOpenJTalkBackend(config=config, runtime=runtime)

        lines = synthesize_ndjson_lines(config, backend, _request(voice_id="voice-1"))
        events = tuple(parse_tts_backend_event_line(line) for line in lines)

        assert runtime.calls == [("こんにちは", (("voice", "voice-1"),))]
        assert len(events) == 3
        assert isinstance(events[0], TtsBackendAudioChunkEvent)
        assert isinstance(events[1], TtsBackendAudioChunkEvent)
        assert isinstance(events[2], TtsBackendAudioDoneEvent)
        assert events[0].audio_frame_count == 2
        assert events[1].audio_sample_index == 2
        assert events[1].audio_frame_count == 1
        assert events[2].audio_seq == 2
        assert events[2].audio_sample_index == 3
        assert events[0].audio_format.sample_format == "f32le"
        assert events[0].audio_format.channels == 1


@pytest.mark.parametrize(
    ("waveform", "message"),
    [
        (np.array([[0.0]], dtype=np.float32), "mono"),
        (np.array([], dtype=np.float32), "must not be empty"),
        (np.array([np.nan], dtype=np.float32), "non-finite"),
    ],
)
def test_pyopenjtalk_backend_rejects_invalid_waveforms(
    waveform: np.ndarray,
    message: str,
) -> None:
    with tempfile.TemporaryDirectory() as directory:
        config = _config(Path(directory))
        backend = PyOpenJTalkBackend(
            config=config,
            runtime=FakePyOpenJTalkRuntime(waveform),
        )

        with pytest.raises(TtsPyOpenJTalkServerError, match=message):
            backend.synthesize(_request())


def test_pyopenjtalk_backend_requires_existing_dictionary_dir() -> None:
    runtime = FakePyOpenJTalkRuntime(np.array([0.0], dtype=np.float32))

    with pytest.raises(TtsPyOpenJTalkServerError, match="not a directory"):
        PyOpenJTalkBackend(
            config=_config(Path("/tmp/fluent-audio-missing-openjtalk-dict")),
            runtime=runtime,
        )


def test_pyopenjtalk_backend_normalizes_int16_scale_waveform() -> None:
    with tempfile.TemporaryDirectory() as directory:
        config = _config(Path(directory))
        backend = PyOpenJTalkBackend(
            config=config,
            runtime=FakePyOpenJTalkRuntime(np.array([0.0, 16384.0, -32768.0])),
        )

        synthesized = backend.synthesize(_request())
        waveform = np.frombuffer(synthesized.audio_bytes, dtype=np.float32)

        assert waveform.tolist() == [0.0, 0.5, -1.0]


def test_pyopenjtalk_backend_peak_normalizes_large_finite_waveform() -> None:
    with tempfile.TemporaryDirectory() as directory:
        config = _config(Path(directory))
        backend = PyOpenJTalkBackend(
            config=config,
            runtime=FakePyOpenJTalkRuntime(np.array([0.0, 40000.0, -20000.0])),
        )

        synthesized = backend.synthesize(_request())
        waveform = np.frombuffer(synthesized.audio_bytes, dtype=np.float32)

        assert waveform.tolist() == [0.0, 1.0, -0.5]


def test_pyopenjtalk_http_server_accepts_tts_backend_contract() -> None:
    with tempfile.TemporaryDirectory() as directory:
        config = _config(Path(directory), chunk_frames=8)
        backend = PyOpenJTalkBackend(
            config=config,
            runtime=FakePyOpenJTalkRuntime(np.array([0.0, 0.1], dtype=np.float32)),
        )
        server = build_server("127.0.0.1", 0, config, backend)
        try:
            _handle_one_request(server)
            response_text = _post(
                server.server_port,
                "/synthesize",
                _request().model_dump_json().encode("utf-8"),
            )
            lines = response_text.strip().splitlines()
            first_event = json.loads(lines[0])
            done_event = json.loads(lines[1])
            assert first_event["event"] == "audio_chunk"
            assert done_event["event"] == "audio_done"
        finally:
            server.server_close()


def test_pyopenjtalk_http_server_rejects_backend_contract_violation() -> None:
    with tempfile.TemporaryDirectory() as directory:
        config = _config(Path(directory))
        backend = PyOpenJTalkBackend(
            config=config,
            runtime=FakePyOpenJTalkRuntime(np.array([np.nan], dtype=np.float32)),
        )
        server = build_server("127.0.0.1", 0, config, backend)
        try:
            _handle_one_request(server)
            with pytest.raises(urllib.error.HTTPError) as error:
                _post(
                    server.server_port,
                    "/synthesize",
                    _request().model_dump_json().encode("utf-8"),
                )
            assert error.value.code == 422
        finally:
            server.server_close()


def _handle_one_request(server) -> None:
    thread = threading.Thread(target=server.handle_request)
    thread.start()
    thread.join(timeout=0.01)


def _post(port: int, path: str, payload: bytes) -> str:
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=2.0) as response:
        return response.read().decode("utf-8")
