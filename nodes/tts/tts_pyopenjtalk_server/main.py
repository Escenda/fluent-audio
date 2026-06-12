"""Fixed-voice PyOpenJTalk HTTP server for the fluent-audio TTS boundary."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import base64
import os
import sys
import time
from collections.abc import Sequence
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Protocol

import numpy as np
import pyopenjtalk
from pydantic import BaseModel, ConfigDict, Field

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fluent_audio.contracts import AudioFormat
from nodes.tts.tts_backend.main import (
    TtsBackendAudioChunkEvent,
    TtsBackendAudioDoneEvent,
    TtsBackendPostRequest,
)

F32LE_BYTES_PER_SAMPLE = 4


class TtsPyOpenJTalkServerError(ValueError):
    """Raised when the PyOpenJTalk HTTP boundary cannot synthesize safely."""


class PyOpenJTalkServerConfig(BaseModel):
    """Runtime configuration for a fixed-voice PyOpenJTalk HTTP server."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    openjtalk_dict_dir: Path
    audio_source_id: str = Field(default="tts_pyopenjtalk", min_length=1)
    audio_stream_id: str = Field(default="tts/pyopenjtalk", min_length=1)
    default_voice_id: str = ""
    chunk_frames: int = Field(default=24000, gt=0)


class PyOpenJTalkSynthesizedAudio(BaseModel):
    """Validated mono f32le audio produced by PyOpenJTalk."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    audio_bytes: bytes = Field(min_length=1)
    sample_rate_hz: int = Field(gt=0)
    frame_count: int = Field(gt=0)


class PyOpenJTalkRuntime(Protocol):
    """Runtime shape used from the pyopenjtalk module or a test fake."""

    def tts(self, text: str, **options: str) -> tuple[np.ndarray, int]:
        """Synthesize a waveform and sample rate."""


class PyOpenJTalkBackend:
    """Small fixed-voice wrapper around pyopenjtalk.tts."""

    def __init__(self, *, config: PyOpenJTalkServerConfig, runtime: PyOpenJTalkRuntime) -> None:
        dictionary_dir = config.openjtalk_dict_dir.expanduser()
        if not dictionary_dir.is_dir():
            raise TtsPyOpenJTalkServerError(
                f"openjtalk_dict_dir is not a directory: {dictionary_dir}"
            )
        os.environ["OPEN_JTALK_DICT_DIR"] = str(dictionary_dir)
        os.environ["TQDM_DISABLE"] = "1"
        self._config = config
        self._runtime = runtime

    def synthesize(self, request: TtsBackendPostRequest) -> PyOpenJTalkSynthesizedAudio:
        voice_id = request.voice_id if request.voice_id != "" else self._config.default_voice_id
        options: dict[str, str] = {}
        if voice_id != "":
            options["voice"] = voice_id
        waveform_raw, sample_rate_hz = self._runtime.tts(request.chunk.text, **options)
        waveform = np.asarray(waveform_raw, dtype=np.float32)
        if waveform.ndim != 1:
            raise TtsPyOpenJTalkServerError("pyopenjtalk waveform must be mono")
        if waveform.size == 0:
            raise TtsPyOpenJTalkServerError("pyopenjtalk waveform must not be empty")
        if not np.all(np.isfinite(waveform)):
            raise TtsPyOpenJTalkServerError("pyopenjtalk waveform contains non-finite samples")
        sample_rate = int(sample_rate_hz)
        if sample_rate <= 0:
            raise TtsPyOpenJTalkServerError("pyopenjtalk sample rate must be positive")
        mono = _normalize_pyopenjtalk_waveform(waveform)
        return PyOpenJTalkSynthesizedAudio(
            audio_bytes=mono.tobytes(),
            sample_rate_hz=sample_rate,
            frame_count=int(mono.shape[0]),
        )


def _normalize_pyopenjtalk_waveform(waveform: np.ndarray) -> np.ndarray:
    """Normalize PyOpenJTalk's known float domains to fluent-audio f32le."""

    peak = float(np.max(np.abs(waveform)))
    if peak <= 1.0:
        return np.ascontiguousarray(waveform, dtype=np.float32)
    if peak <= 32768.0:
        return np.ascontiguousarray(waveform / 32768.0, dtype=np.float32)
    # PyOpenJTalk can return finite float-domain samples whose peak exceeds the
    # int16 scale on some text/backend combinations. The HTTP boundary contract
    # is mono f32le in [-1.0, 1.0], so keep the waveform shape and normalize by
    # its actual peak after empty/non-finite cases have already failed closed.
    return np.ascontiguousarray(waveform / peak, dtype=np.float32)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a PyOpenJTalk TTS HTTP server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--openjtalk-dict-dir", type=Path, required=True)
    parser.add_argument("--audio-source-id", default="tts_pyopenjtalk")
    parser.add_argument("--audio-stream-id", default="tts/pyopenjtalk")
    parser.add_argument("--default-voice-id", default="")
    parser.add_argument("--chunk-frames", type=int, default=24000)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = PyOpenJTalkServerConfig(
        openjtalk_dict_dir=args.openjtalk_dict_dir,
        audio_source_id=args.audio_source_id,
        audio_stream_id=args.audio_stream_id,
        default_voice_id=args.default_voice_id,
        chunk_frames=args.chunk_frames,
    )
    backend = PyOpenJTalkBackend(config=config, runtime=pyopenjtalk)
    server = build_server(args.host, args.port, config, backend)
    server.serve_forever()
    return 0


def build_server(
    host: str,
    port: int,
    config: PyOpenJTalkServerConfig,
    backend: PyOpenJTalkBackend,
) -> ThreadingHTTPServer:
    class ReusableHTTPServer(ThreadingHTTPServer):
        allow_reuse_address = True

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path == "/health":
                _send_bytes(self, 200, b"ok", content_type="text/plain")
                return
            _send_error(self, 404, "Not found")

        def do_POST(self) -> None:
            if self.path != "/synthesize":
                _send_error(self, 404, "Not found")
                return
            content_length = self.headers.get("Content-Length")
            if content_length is None:
                _send_error(self, 411, "Content-Length is required")
                return
            request_body = self.rfile.read(int(content_length))
            try:
                request = TtsBackendPostRequest.model_validate_json(request_body)
                lines = tuple(synthesize_ndjson_lines(config, backend, request))
            except TtsPyOpenJTalkServerError as exc:
                _send_error(self, 422, str(exc))
                return
            except ValueError:
                _send_error(self, 400, "Invalid TTS backend request")
                return
            _send_bytes(
                self,
                200,
                "".join(lines).encode("utf-8"),
                content_type="application/x-ndjson",
            )

        def log_message(self, format: str, *args: str) -> None:
            return

    return ReusableHTTPServer((host, port), Handler)


def synthesize_ndjson_lines(
    config: PyOpenJTalkServerConfig,
    backend: PyOpenJTalkBackend,
    request: TtsBackendPostRequest,
) -> tuple[str, ...]:
    synthesized = backend.synthesize(request)
    audio_format = AudioFormat(
        sample_rate_hz=synthesized.sample_rate_hz,
        channels=1,
        sample_format="f32le",
        channel_layout="interleaved",
    )
    lines: list[str] = []
    seq = 0
    audio_seq = 0
    sample_index = 0
    capture_time_ns = time.time_ns()
    while sample_index < synthesized.frame_count:
        frame_count = min(config.chunk_frames, synthesized.frame_count - sample_index)
        start_byte = sample_index * F32LE_BYTES_PER_SAMPLE
        end_byte = start_byte + frame_count * F32LE_BYTES_PER_SAMPLE
        payload = synthesized.audio_bytes[start_byte:end_byte]
        lines.append(
            TtsBackendAudioChunkEvent(
                event="audio_chunk",
                request_id=request.chunk.request_id,
                session_id=request.chunk.session_id,
                assistant_turn_id=request.chunk.assistant_turn_id,
                seq=seq,
                audio_source_id=config.audio_source_id,
                audio_stream_id=config.audio_stream_id,
                audio_seq=audio_seq,
                audio_sample_index=sample_index,
                audio_capture_time_ns=capture_time_ns,
                audio_frame_count=frame_count,
                audio_format=audio_format,
                payload_b64=base64.b64encode(payload).decode("ascii"),
            ).model_dump_json()
            + "\n"
        )
        seq += 1
        audio_seq += 1
        sample_index += frame_count
    lines.append(
        TtsBackendAudioDoneEvent(
            event="audio_done",
            request_id=request.chunk.request_id,
            session_id=request.chunk.session_id,
            assistant_turn_id=request.chunk.assistant_turn_id,
            seq=seq,
            audio_source_id=config.audio_source_id,
            audio_stream_id=config.audio_stream_id,
            audio_seq=audio_seq,
            audio_sample_index=sample_index,
            audio_capture_time_ns=capture_time_ns,
            audio_format=audio_format,
        ).model_dump_json()
        + "\n"
    )
    return tuple(lines)


def _send_error(handler: BaseHTTPRequestHandler, status: int, message: str) -> None:
    _send_bytes(handler, status, f"{message}\n".encode("utf-8"), content_type="text/plain")


def _send_bytes(
    handler: BaseHTTPRequestHandler,
    status: int,
    body: bytes,
    *,
    content_type: str,
) -> None:
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


if __name__ == "__main__":
    raise SystemExit(main())
