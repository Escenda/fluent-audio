"""DORA probe for TTS-facing text chunks emitted by dialogue_engine."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fluent_audio.contracts import TtsTextChunk
from fluent_audio.dora import (
    decode_tts_text_chunk_from_dora,
    validate_dora_tts_text_metadata,
    validate_dora_tts_text_stream_final_marker,
)


class TtsTextProbeError(ValueError):
    """Raised when a TTS text stream violates the smoke contract."""


class TtsTextProbeConfig(BaseModel):
    """Expected TTS text stream identity and text assertions."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: str = Field(min_length=1)
    user_turn_id: str = Field(min_length=1)
    assistant_turn_id: str = Field(min_length=1)
    expected_min_chunks: int = Field(ge=0)
    expected_text_contains: tuple[str, ...] = Field(default=())
    forbidden_text_contains: tuple[str, ...] = Field(default=())


class TtsTextProbeSummary(BaseModel):
    """Validated smoke summary for a DORA TTS text stream."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    chunks: int = Field(ge=0)
    final_seen: bool
    text: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and discard DORA TTS text chunks.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--user-turn-id", required=True)
    parser.add_argument("--assistant-turn-id", required=True)
    parser.add_argument("--expected-min-chunks", type=int, default=1)
    parser.add_argument("--expected-text-contains", action="append", default=[])
    parser.add_argument("--forbidden-text-contains", action="append", default=[])
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("tts_text_probe requires --dora")

    from dora import Node

    config = TtsTextProbeConfig(
        session_id=args.session_id,
        user_turn_id=args.user_turn_id,
        assistant_turn_id=args.assistant_turn_id,
        expected_min_chunks=args.expected_min_chunks,
        expected_text_contains=tuple(args.expected_text_contains),
        forbidden_text_contains=tuple(args.forbidden_text_contains),
    )
    summary = run_tts_text_probe_dora(Node(), config)
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def run_tts_text_probe_dora(node, config: TtsTextProbeConfig) -> TtsTextProbeSummary:
    chunks: list[TtsTextChunk] = []
    for event in node:
        if event is None:
            raise TtsTextProbeError("DORA event stream ended before TTS text final marker")
        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            raise TtsTextProbeError("DORA STOP arrived before TTS text final marker")
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id != "tts_text":
                raise TtsTextProbeError(f"Unexpected DORA input id: {input_id!r}")
            raise TtsTextProbeError("DORA tts_text input closed before final marker")
        if event_type != "INPUT":
            raise TtsTextProbeError(f"Unexpected DORA event type: {event_type!r}")

        input_id = _required_event_text(event, "id")
        if input_id != "tts_text":
            raise TtsTextProbeError(f"Unexpected DORA input id: {input_id!r}")
        payload = event.get("value")
        metadata = validate_dora_tts_text_metadata(event.get("metadata"))
        if metadata.kind == "stream_final":
            final = validate_dora_tts_text_stream_final_marker(payload, metadata)
            _validate_identity(
                final.session_id,
                final.user_turn_id,
                final.assistant_turn_id,
                config=config,
            )
            if final.seq != len(chunks):
                raise TtsTextProbeError("TTS text final seq must follow the last chunk seq")
            return _build_summary(chunks, config)

        chunk = decode_tts_text_chunk_from_dora(payload, metadata)
        _validate_chunk(chunk, expected_seq=len(chunks), config=config)
        chunks.append(chunk)
    raise TtsTextProbeError("DORA event stream ended before TTS text final marker")


def _build_summary(
    chunks: list[TtsTextChunk],
    config: TtsTextProbeConfig,
) -> TtsTextProbeSummary:
    if len(chunks) < config.expected_min_chunks:
        raise TtsTextProbeError(
            "TTS text chunk count below expectation: "
            f"expected at least {config.expected_min_chunks}, got {len(chunks)}"
        )
    text = "".join(chunk.text for chunk in chunks)
    for expected in config.expected_text_contains:
        if expected not in text:
            raise TtsTextProbeError(f"TTS text did not contain expected text: {expected!r}")
    for forbidden in config.forbidden_text_contains:
        if forbidden in text:
            raise TtsTextProbeError(f"TTS text contained forbidden text: {forbidden!r}")
    return TtsTextProbeSummary(chunks=len(chunks), final_seen=True, text=text)


def _validate_chunk(
    chunk: TtsTextChunk,
    *,
    expected_seq: int,
    config: TtsTextProbeConfig,
) -> None:
    _validate_identity(
        chunk.session_id,
        chunk.user_turn_id,
        chunk.assistant_turn_id,
        config=config,
    )
    if chunk.seq != expected_seq:
        raise TtsTextProbeError(
            f"TTS text chunk seq mismatch: expected {expected_seq}, got {chunk.seq}"
        )
    if chunk.request_id == "":
        raise TtsTextProbeError("TTS text chunk request_id must not be empty")


def _validate_identity(
    session_id: str,
    user_turn_id: str,
    assistant_turn_id: str,
    *,
    config: TtsTextProbeConfig,
) -> None:
    if session_id != config.session_id:
        raise TtsTextProbeError("TTS text session_id mismatch")
    if user_turn_id != config.user_turn_id:
        raise TtsTextProbeError("TTS text user_turn_id mismatch")
    if assistant_turn_id != config.assistant_turn_id:
        raise TtsTextProbeError("TTS text assistant_turn_id mismatch")


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise TtsTextProbeError(f"DORA event field {key!r} must be a string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
