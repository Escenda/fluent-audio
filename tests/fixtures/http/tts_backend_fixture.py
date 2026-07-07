"""One-shot HTTP fixture for tts_backend DORA integration smokes."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import base64
import sys
from collections.abc import Sequence
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fluent_dialogue_dora.contracts import AudioFormat
from nodes.tts.tts_backend.main import (
    TtsBackendAudioChunkEvent,
    TtsBackendAudioDoneEvent,
    TtsBackendPostRequest,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a one-shot TTS HTTP fixture.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--audio-file", required=True, type=Path)
    parser.add_argument("--sample-rate-hz", required=True, type=int)
    parser.add_argument("--channels", required=True, type=int)
    parser.add_argument("--sample-format", required=True, choices=("s16le", "f32le"))
    parser.add_argument("--channel-layout", required=True, choices=("interleaved",))
    parser.add_argument("--audio-source-id", required=True)
    parser.add_argument("--audio-stream-id", required=True)
    parser.add_argument("--expected-requests", type=int, default=1)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    audio_format = AudioFormat(
        sample_rate_hz=args.sample_rate_hz,
        channels=args.channels,
        sample_format=args.sample_format,
        channel_layout=args.channel_layout,
    )
    payload = args.audio_file.read_bytes()
    frame_count = _frame_count(payload, audio_format)
    server = _build_server(
        args.host,
        args.port,
        payload=payload,
        frame_count=frame_count,
        audio_format=audio_format,
        audio_source_id=args.audio_source_id,
        audio_stream_id=args.audio_stream_id,
    )
    while getattr(server, "served_post_requests") < args.expected_requests:
        server.handle_request()
    return 0


def _build_server(
    host: str,
    port: int,
    *,
    payload: bytes,
    frame_count: int,
    audio_format: AudioFormat,
    audio_source_id: str,
    audio_stream_id: str,
) -> HTTPServer:
    class CountingHTTPServer(HTTPServer):
        allow_reuse_address = True
        served_post_requests = 0

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path != "/health":
                self.send_error(404, "Not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"ok")

        def do_POST(self) -> None:
            content_length = self.headers.get("Content-Length")
            if content_length is None:
                self.send_error(411, "Content-Length is required")
                return
            request_body = self.rfile.read(int(content_length))
            try:
                request = TtsBackendPostRequest.model_validate_json(request_body)
            except ValueError:
                self.send_error(400, "Invalid TTS request")
                return

            chunk = request.chunk
            payload_b64 = base64.b64encode(payload).decode("ascii")
            audio_event = TtsBackendAudioChunkEvent(
                event="audio_chunk",
                request_id=chunk.request_id,
                session_id=chunk.session_id,
                assistant_turn_id=chunk.assistant_turn_id,
                seq=0,
                audio_source_id=audio_source_id,
                audio_stream_id=audio_stream_id,
                audio_seq=0,
                audio_sample_index=0,
                audio_capture_time_ns=0,
                audio_frame_count=frame_count,
                audio_format=audio_format,
                payload_b64=payload_b64,
            )
            done_event = TtsBackendAudioDoneEvent(
                event="audio_done",
                request_id=chunk.request_id,
                session_id=chunk.session_id,
                assistant_turn_id=chunk.assistant_turn_id,
                seq=1,
                audio_source_id=audio_source_id,
                audio_stream_id=audio_stream_id,
                audio_seq=1,
                audio_sample_index=frame_count,
                audio_capture_time_ns=(frame_count * 1_000_000_000)
                // audio_format.sample_rate_hz,
                audio_format=audio_format,
            )
            body = f"{audio_event.model_dump_json()}\n{done_event.model_dump_json()}\n"
            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson")
            self.send_header("Content-Length", str(len(body.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))
            self.server.served_post_requests += 1

        def log_message(self, format: str, *args) -> None:
            return

    return CountingHTTPServer((host, port), Handler)


def _frame_count(payload: bytes, audio_format: AudioFormat) -> int:
    if len(payload) == 0:
        raise ValueError("audio fixture must not be empty")
    if len(payload) % audio_format.frame_size_bytes != 0:
        raise ValueError("audio fixture bytes must align to complete frames")
    return len(payload) // audio_format.frame_size_bytes


if __name__ == "__main__":
    raise SystemExit(main())
