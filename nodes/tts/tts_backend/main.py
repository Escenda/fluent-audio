"""DORA boundary for an external typed TTS runtime.

This node does not select, host, or wrap a TTS model. It validates TTS-ready
text chunks from DORA, posts each chunk to a configured HTTP boundary, validates
returned NDJSON/SSE audio events, and projects synthesized audio back to DORA.
"""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import base64
import binascii
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path
from typing import Annotated, Literal, Protocol, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fluent_dialogue_dora.contracts import (
    AudioChunk,
    AudioFormat,
    SynthesizedAudioChunk,
    TtsTextChunk,
)
from fluent_dialogue_dora.dora import (
    decode_tts_text_chunk_from_dora,
    encode_synthesized_audio_chunk_for_dora,
    encode_synthesized_audio_final_marker_for_dora,
    validate_dora_tts_text_metadata,
    validate_dora_tts_text_stream_final_marker,
)


class TtsBackendNodeError(ValueError):
    """Raised when the external TTS boundary cannot be validated."""


class TtsBackendConfig(BaseModel):
    """Runtime configuration for the TTS DORA boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    endpoint_url: str = Field(min_length=1)
    auth_token: str | None = None
    timeout_seconds: float = Field(default=30.0, gt=0.0)
    default_voice_id: str = ""
    output_drain_seconds: float = Field(default=0.2, ge=0.0)


class TtsBackendPostRequest(BaseModel):
    """HTTP request body sent for one TTS-ready text chunk."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    request_type: Literal["tts_text"] = "tts_text"
    chunk: TtsTextChunk
    voice_id: str


class TtsBackendAudioChunkEvent(BaseModel):
    """One audio payload event emitted by the external TTS runtime."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event: Literal["audio_chunk"]
    request_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    assistant_turn_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    audio_source_id: str = Field(min_length=1)
    audio_stream_id: str = Field(min_length=1)
    audio_seq: int = Field(ge=0)
    audio_sample_index: int = Field(ge=0)
    audio_capture_time_ns: int = Field(ge=0)
    audio_frame_count: int = Field(gt=0)
    audio_format: AudioFormat
    payload_b64: str = Field(min_length=1)

    def to_contract(self, *, user_turn_id: str) -> SynthesizedAudioChunk:
        try:
            payload = base64.b64decode(self.payload_b64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise TtsBackendNodeError("TTS audio_chunk payload_b64 is invalid") from exc
        try:
            audio = AudioChunk(
                source_id=self.audio_source_id,
                stream_id=self.audio_stream_id,
                seq=self.audio_seq,
                sample_index=self.audio_sample_index,
                capture_time_ns=self.audio_capture_time_ns,
                frame_count=self.audio_frame_count,
                format=self.audio_format,
                payload=payload,
            )
            return SynthesizedAudioChunk(
                request_id=self.request_id,
                session_id=self.session_id,
                user_turn_id=user_turn_id,
                assistant_turn_id=self.assistant_turn_id,
                seq=self.seq,
                audio=audio,
            )
        except ValueError as exc:
            raise TtsBackendNodeError("TTS audio_chunk did not validate") from exc


class TtsBackendAudioDoneEvent(BaseModel):
    """Terminal audio marker emitted by the external TTS runtime."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event: Literal["audio_done"]
    request_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    assistant_turn_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    audio_source_id: str = Field(min_length=1)
    audio_stream_id: str = Field(min_length=1)
    audio_seq: int = Field(ge=0)
    audio_sample_index: int = Field(ge=0)
    audio_capture_time_ns: int = Field(ge=0)
    audio_format: AudioFormat


TtsBackendEvent: TypeAlias = TtsBackendAudioChunkEvent | TtsBackendAudioDoneEvent
TtsBackendEventEnvelope: TypeAlias = Annotated[
    TtsBackendEvent,
    Field(discriminator="event"),
]

TTS_BACKEND_EVENT_ADAPTER = TypeAdapter(TtsBackendEventEnvelope)


class TtsBackendRequestSummary(BaseModel):
    """Counters for one TTS backend response stream."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    audio_chunks: int = Field(ge=0)
    audio_done: int = Field(ge=0)


class TtsBackendSummary(BaseModel):
    """Validated counters for one DORA node run."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    tts_text_chunks: int = Field(ge=0)
    tts_text_stream_finals: int = Field(ge=0)
    synthesized_audio_chunks: int = Field(ge=0)
    synthesized_audio_finals: int = Field(ge=0)


class TtsBackendTransport(Protocol):
    """HTTP boundary used by the node runtime and fake tests."""

    def post_tts_text(self, request: TtsBackendPostRequest) -> Iterable[str]:
        """Post one TTS text chunk and return NDJSON or SSE-style event lines."""


class HttpTtsBackendTransport:
    """urllib based transport for the external TTS runtime boundary."""

    def __init__(self, config: TtsBackendConfig) -> None:
        endpoint_url = config.endpoint_url.strip()
        if endpoint_url == "":
            raise TtsBackendNodeError("endpoint_url must not be empty")
        self._endpoint_url = endpoint_url
        self._auth_token = config.auth_token
        self._timeout_seconds = config.timeout_seconds

    def post_tts_text(self, request: TtsBackendPostRequest) -> Iterable[str]:
        return self._post_stream(request.model_dump_json())

    def _post_stream(self, body: str) -> Iterator[str]:
        request = self._build_request(body)
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                status = response.getcode()
                if status < 200 or status >= 300:
                    raise TtsBackendNodeError(
                        f"TTS backend returned unexpected HTTP status {status}"
                    )
                for raw_line in response:
                    yield raw_line.decode("utf-8")
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise TtsBackendNodeError(
                f"TTS backend request failed with HTTP {exc.code}: {error_body}"
            ) from exc
        except urllib.error.URLError as exc:
            raise TtsBackendNodeError(f"TTS backend request failed: {exc}") from exc
        except UnicodeDecodeError as exc:
            raise TtsBackendNodeError("TTS backend stream line must be UTF-8") from exc

    def _build_request(self, body: str) -> urllib.request.Request:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/x-ndjson, text/event-stream",
        }
        if self._auth_token is not None:
            headers["Authorization"] = f"Bearer {self._auth_token}"
        return urllib.request.Request(
            self._endpoint_url,
            data=body.encode("utf-8"),
            headers=headers,
            method="POST",
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the TTS backend DORA boundary.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--endpoint-url", required=True)
    parser.add_argument("--auth-token")
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--default-voice-id", default="")
    parser.add_argument("--output-drain-seconds", type=float, default=0.2)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("tts_backend requires --dora")

    from dora import Node

    config = TtsBackendConfig(
        endpoint_url=args.endpoint_url,
        auth_token=args.auth_token,
        timeout_seconds=args.timeout_seconds,
        default_voice_id=args.default_voice_id,
        output_drain_seconds=args.output_drain_seconds,
    )
    summary = run_tts_backend_events(Node(), config, HttpTtsBackendTransport(config))
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def run_tts_backend_events(
    node,
    config: TtsBackendConfig,
    transport: TtsBackendTransport,
) -> TtsBackendSummary:
    _validate_config_endpoint(config)
    tts_text_chunks = 0
    tts_text_stream_finals = 0
    synthesized_audio_chunks = 0
    synthesized_audio_finals = 0

    for event in node:
        if event is None:
            raise TtsBackendNodeError("DORA event stream ended before STOP")
        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            _drain_dora_output_send(config.output_drain_seconds)
            return TtsBackendSummary(
                tts_text_chunks=tts_text_chunks,
                tts_text_stream_finals=tts_text_stream_finals,
                synthesized_audio_chunks=synthesized_audio_chunks,
                synthesized_audio_finals=synthesized_audio_finals,
            )
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id != "tts_text":
                raise TtsBackendNodeError(f"Unexpected DORA input id: {input_id!r}")
            _drain_dora_output_send(config.output_drain_seconds)
            return TtsBackendSummary(
                tts_text_chunks=tts_text_chunks,
                tts_text_stream_finals=tts_text_stream_finals,
                synthesized_audio_chunks=synthesized_audio_chunks,
                synthesized_audio_finals=synthesized_audio_finals,
            )
        if event_type != "INPUT":
            continue

        input_id = _required_event_text(event, "id")
        if input_id != "tts_text":
            raise TtsBackendNodeError(f"Unexpected DORA input id: {input_id!r}")

        metadata = validate_dora_tts_text_metadata(event.get("metadata"))
        if metadata.kind == "stream_final":
            validate_dora_tts_text_stream_final_marker(event.get("value"), metadata)
            tts_text_stream_finals += 1
            continue

        chunk = decode_tts_text_chunk_from_dora(event.get("value"), metadata)
        stream_summary = _post_text_and_send_outputs(node, config, transport, chunk)
        tts_text_chunks += 1
        synthesized_audio_chunks += stream_summary.audio_chunks
        synthesized_audio_finals += stream_summary.audio_done

    raise TtsBackendNodeError("DORA event stream ended before STOP")


def parse_tts_backend_event_line(line: str) -> TtsBackendEvent | None:
    """Parse one NDJSON or SSE data line from the external TTS backend."""

    event_json = _event_json_from_line(line)
    if event_json is None:
        return None
    try:
        return TTS_BACKEND_EVENT_ADAPTER.validate_json(event_json)
    except ValueError as exc:
        raise TtsBackendNodeError("TTS backend event line is invalid") from exc


def _post_text_and_send_outputs(
    node,
    config: TtsBackendConfig,
    transport: TtsBackendTransport,
    chunk: TtsTextChunk,
) -> TtsBackendRequestSummary:
    audio_chunks = 0
    audio_done = 0

    stream_validator = TtsResponseStreamValidator(chunk)
    request = TtsBackendPostRequest(chunk=chunk, voice_id=config.default_voice_id)
    for line in transport.post_tts_text(request):
        backend_event = parse_tts_backend_event_line(line)
        if backend_event is None:
            continue
        if audio_done:
            raise TtsBackendNodeError("TTS backend emitted event after audio_done")
        _validate_event_matches_text_chunk(chunk, backend_event)
        stream_validator.validate_next(backend_event)

        if isinstance(backend_event, TtsBackendAudioChunkEvent):
            _send_synthesized_audio_chunk(
                node,
                backend_event.to_contract(user_turn_id=chunk.user_turn_id),
            )
            audio_chunks += 1
        elif isinstance(backend_event, TtsBackendAudioDoneEvent):
            _send_synthesized_audio_done(node, backend_event, user_turn_id=chunk.user_turn_id)
            audio_done += 1

    if audio_chunks == 0:
        raise TtsBackendNodeError("TTS backend stream ended without audio_chunk")
    if audio_done != 1:
        raise TtsBackendNodeError("TTS backend stream ended without exactly one audio_done")
    return TtsBackendRequestSummary(audio_chunks=audio_chunks, audio_done=audio_done)


class TtsResponseStreamValidator:
    """Validate one external TTS response stream before speaker scheduling."""

    def __init__(self, chunk: TtsTextChunk) -> None:
        self._expected_response_seq = 0
        self._expected_audio_seq = 0
        self._expected_audio_sample_index = 0
        self._audio_format: AudioFormat | None = None

    def validate_next(self, backend_event: TtsBackendEvent) -> None:
        if backend_event.seq != self._expected_response_seq:
            raise TtsBackendNodeError(
                f"TTS backend event seq discontinuity: expected "
                f"{self._expected_response_seq}, got {backend_event.seq}"
            )
        self._expected_response_seq += 1
        if backend_event.audio_seq != self._expected_audio_seq:
            raise TtsBackendNodeError(
                f"TTS backend audio_seq discontinuity: expected "
                f"{self._expected_audio_seq}, got {backend_event.audio_seq}"
            )
        if backend_event.audio_sample_index != self._expected_audio_sample_index:
            raise TtsBackendNodeError(
                f"TTS backend audio_sample_index discontinuity: expected "
                f"{self._expected_audio_sample_index}, got {backend_event.audio_sample_index}"
            )
        self._validate_or_set_audio_format(backend_event.audio_format)
        if isinstance(backend_event, TtsBackendAudioChunkEvent):
            self._expected_audio_seq += 1
            self._expected_audio_sample_index += backend_event.audio_frame_count

    def _validate_or_set_audio_format(self, audio_format: AudioFormat) -> None:
        if self._audio_format is None:
            self._audio_format = audio_format
            return
        if self._audio_format != audio_format:
            raise TtsBackendNodeError("TTS backend audio format changed within one request")


def _send_synthesized_audio_chunk(node, chunk: SynthesizedAudioChunk) -> None:
    payload, metadata = encode_synthesized_audio_chunk_for_dora(chunk)
    node.send_output("synth_audio", payload, metadata=metadata.to_dora_metadata())


def _send_synthesized_audio_done(
    node,
    event: TtsBackendAudioDoneEvent,
    *,
    user_turn_id: str,
) -> None:
    payload, metadata = encode_synthesized_audio_final_marker_for_dora(
        request_id=event.request_id,
        session_id=event.session_id,
        user_turn_id=user_turn_id,
        assistant_turn_id=event.assistant_turn_id,
        seq=event.seq,
        audio_source_id=event.audio_source_id,
        audio_stream_id=event.audio_stream_id,
        audio_seq=event.audio_seq,
        audio_sample_index=event.audio_sample_index,
        audio_capture_time_ns=event.audio_capture_time_ns,
        audio_format=event.audio_format,
    )
    node.send_output("synth_audio", payload, metadata=metadata.to_dora_metadata())


def _event_json_from_line(line: str) -> str | None:
    stripped = line.strip()
    if stripped == "":
        return None
    if stripped.startswith("data:"):
        data = stripped.removeprefix("data:").strip()
        if data == "":
            raise TtsBackendNodeError("TTS backend SSE data line must not be empty")
        return data
    return stripped


def _validate_event_matches_text_chunk(
    chunk: TtsTextChunk,
    backend_event: TtsBackendEvent,
) -> None:
    if backend_event.request_id != chunk.request_id:
        raise TtsBackendNodeError("TTS backend event request_id did not match text chunk")
    if backend_event.session_id != chunk.session_id:
        raise TtsBackendNodeError("TTS backend event session_id did not match text chunk")
    if backend_event.assistant_turn_id != chunk.assistant_turn_id:
        raise TtsBackendNodeError(
            "TTS backend event assistant_turn_id did not match text chunk"
        )


def _validate_config_endpoint(config: TtsBackendConfig) -> None:
    if config.endpoint_url.strip() == "":
        raise TtsBackendNodeError("endpoint_url must not be empty")


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise TtsBackendNodeError(f"DORA event field {key!r} must be a string")
    return value


def _drain_dora_output_send(output_drain_seconds: float) -> None:
    time.sleep(output_drain_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
