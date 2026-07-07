"""Fixed-voice Kokoro-82M HTTP server for the fluent-dialogue-dora TTS boundary."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import base64
import math
import sys
import time
from collections.abc import Sequence
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Protocol

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

_REPO_ROOT = Path(__file__).resolve().parents[3]
for _path in (_REPO_ROOT, _REPO_ROOT / "src", _REPO_ROOT / "contracts/python/src"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from fluent_dialogue_dora.contracts import AudioFormat
from nodes.tts.tts_backend.main import (
    TtsBackendAudioChunkEvent,
    TtsBackendAudioDoneEvent,
    TtsBackendPostRequest,
)

F32LE_BYTES_PER_SAMPLE = 4
DEFAULT_KOKORO_REPO_ID = str(_REPO_ROOT / "data/models/fluent_dialogue_dora/Kokoro-82M")
KOKORO_NATIVE_SAMPLE_RATE_HZ = 24_000


class TtsKokoroServerError(ValueError):
    """Raised when the Kokoro HTTP boundary cannot synthesize safely."""


class KokoroServerConfig(BaseModel):
    """Runtime configuration for a fixed-voice Kokoro HTTP server."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    audio_source_id: str = Field(default="tts_kokoro", min_length=1)
    audio_stream_id: str = Field(default="tts/kokoro", min_length=1)
    default_voice_id: str = Field(default="jf_alpha", min_length=1)
    chunk_frames: int = Field(default=2400, gt=0)
    output_sample_rate_hz: int = Field(default=48_000, gt=0)


class KokoroSynthesizedAudio(BaseModel):
    """Validated mono f32le audio produced by Kokoro."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    audio_bytes: bytes = Field(min_length=1)
    sample_rate_hz: int = Field(gt=0)
    frame_count: int = Field(gt=0)


class KokoroRuntime(Protocol):
    """Runtime shape used from the Kokoro pipeline or a test fake."""

    def synthesize(self, text: str, voice: str) -> tuple[np.ndarray, int]:
        """Synthesize a mono waveform and its sample rate."""


class KokoroPipelineRuntime:
    """Real Kokoro-82M pipeline runtime (Japanese G2P)."""

    def __init__(self, *, repo_id: str = DEFAULT_KOKORO_REPO_ID) -> None:
        repo_path = Path(repo_id).expanduser()
        if repo_path.is_absolute() and not repo_path.exists():
            raise TtsKokoroServerError(
                f"missing Kokoro model directory: {repo_path}; "
                "run scripts/bootstrap_dev_env.sh --models or pass --repo-id"
            )
        from kokoro import KPipeline

        self._pipeline = KPipeline(lang_code="j", repo_id=repo_id)

    def synthesize(self, text: str, voice: str) -> tuple[np.ndarray, int]:
        parts = [result.audio for result in self._pipeline(text, voice=voice)]
        if not parts:
            raise TtsKokoroServerError("Kokoro pipeline produced no audio segments")
        waveform = np.concatenate([np.asarray(part, dtype=np.float32) for part in parts])
        return waveform, KOKORO_NATIVE_SAMPLE_RATE_HZ


class KokoroBackend:
    """Fixed-voice wrapper that validates and resamples Kokoro output."""

    def __init__(self, *, config: KokoroServerConfig, runtime: KokoroRuntime) -> None:
        self._config = config
        self._runtime = runtime

    def synthesize(self, request: TtsBackendPostRequest) -> KokoroSynthesizedAudio:
        voice_id = request.voice_id if request.voice_id != "" else self._config.default_voice_id
        waveform_raw, sample_rate_hz = self._runtime.synthesize(request.chunk.text, voice_id)
        waveform = np.asarray(waveform_raw, dtype=np.float32)
        if waveform.ndim != 1:
            raise TtsKokoroServerError("Kokoro waveform must be mono")
        if waveform.size == 0:
            raise TtsKokoroServerError("Kokoro waveform must not be empty")
        if not np.all(np.isfinite(waveform)):
            raise TtsKokoroServerError("Kokoro waveform contains non-finite samples")
        sample_rate = int(sample_rate_hz)
        if sample_rate <= 0:
            raise TtsKokoroServerError("Kokoro sample rate must be positive")
        peak = float(np.max(np.abs(waveform)))
        if peak > 1.0:
            waveform = waveform / peak
        resampled = _resample_to_output_rate(
            waveform,
            input_rate_hz=sample_rate,
            output_rate_hz=self._config.output_sample_rate_hz,
        )
        if resampled.size == 0:
            raise TtsKokoroServerError("Kokoro waveform is empty after resampling")
        mono = np.ascontiguousarray(resampled, dtype=np.float32)
        return KokoroSynthesizedAudio(
            audio_bytes=mono.tobytes(),
            sample_rate_hz=self._config.output_sample_rate_hz,
            frame_count=int(mono.shape[0]),
        )


def _resample_to_output_rate(
    waveform: np.ndarray,
    *,
    input_rate_hz: int,
    output_rate_hz: int,
) -> np.ndarray:
    if input_rate_hz == output_rate_hz:
        return waveform
    from scipy.signal import resample_poly

    divisor = math.gcd(input_rate_hz, output_rate_hz)
    return resample_poly(
        waveform,
        output_rate_hz // divisor,
        input_rate_hz // divisor,
    ).astype(np.float32)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a Kokoro-82M TTS HTTP server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--repo-id", default=DEFAULT_KOKORO_REPO_ID)
    parser.add_argument("--audio-source-id", default="tts_kokoro")
    parser.add_argument("--audio-stream-id", default="tts/kokoro")
    parser.add_argument("--default-voice-id", default="jf_alpha")
    parser.add_argument("--chunk-frames", type=int, default=2400)
    parser.add_argument("--output-sample-rate-hz", type=int, default=48_000)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = KokoroServerConfig(
        audio_source_id=args.audio_source_id,
        audio_stream_id=args.audio_stream_id,
        default_voice_id=args.default_voice_id,
        chunk_frames=args.chunk_frames,
        output_sample_rate_hz=args.output_sample_rate_hz,
    )
    backend = KokoroBackend(
        config=config,
        runtime=KokoroPipelineRuntime(repo_id=args.repo_id),
    )
    warmup_backend(backend)
    server = build_server(args.host, args.port, config, backend)
    server.serve_forever()
    return 0


def warmup_backend(backend: KokoroBackend) -> None:
    """Load model weights and exercise one synthesis before the port opens."""

    from fluent_dialogue_dora.contracts import TtsTextChunk

    backend.synthesize(
        TtsBackendPostRequest(
            chunk=TtsTextChunk(
                request_id="kokoro-warmup",
                session_id="kokoro-warmup",
                user_turn_id="kokoro-warmup",
                assistant_turn_id="kokoro-warmup",
                seq=0,
                text="ウォームアップです。",
                is_final=True,
            ),
            voice_id="",
        )
    )


def build_server(
    host: str,
    port: int,
    config: KokoroServerConfig,
    backend: KokoroBackend,
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
                lines = synthesize_ndjson_lines(config, backend, request)
            except TtsKokoroServerError as exc:
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
    config: KokoroServerConfig,
    backend: KokoroBackend,
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
