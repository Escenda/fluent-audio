"""DORA node adapting per-request playback audio into one speaker stream.

`playback_queue` emits audio final markers at TTS request boundaries. That is
useful for request-level smokes, but a long-lived speaker device must not close
after the first assistant response. This node validates those request boundary
markers, suppresses them, and emits one continuous speaker stream final only
when the upstream DORA input closes.
"""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fluent_audio.contracts import AudioChunk, AudioFormat
from fluent_audio.dora import (
    DoraAudioMetadata,
    decode_audio_chunk_from_dora,
    encode_audio_chunk_for_dora,
    encode_audio_final_marker_for_dora,
    validate_dora_audio_final_marker,
    validate_dora_audio_metadata,
)

DEFAULT_DORA_OUTPUT_DRAIN_SECONDS = 0.2


class SpeakerStreamAdapterError(ValueError):
    """Raised when playback audio cannot be adapted to a speaker stream."""


class SpeakerStreamAdapterConfig(BaseModel):
    """Runtime configuration for speaker stream adaptation."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    input_source_id: str = Field(min_length=1)
    input_stream_id: str = Field(min_length=1)
    output_source_id: str = Field(min_length=1)
    output_stream_id: str = Field(min_length=1)
    output_start_seq: int = Field(default=0, ge=0)
    output_start_sample_index: int = Field(default=0, ge=0)
    output_drain_seconds: float = Field(default=DEFAULT_DORA_OUTPUT_DRAIN_SECONDS, ge=0.0)


class SpeakerStreamAdapterSummary(BaseModel):
    """Validated counters for one speaker stream adapter run."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    input_chunks: int = Field(ge=0)
    input_request_finals: int = Field(ge=0)
    output_chunks: int = Field(ge=0)
    output_final_sent: bool
    final_sample_index: int = Field(ge=0)


class SpeakerStreamAdapterState:
    """Validates playback audio and reissues it as one continuous stream."""

    def __init__(self, config: SpeakerStreamAdapterConfig) -> None:
        self._config = config
        self._input_format: AudioFormat | None = None
        self._input_next_seq: int | None = None
        self._input_next_sample_index: int | None = None
        self._output_next_seq = config.output_start_seq
        self._output_next_sample_index = config.output_start_sample_index
        self._output_format: AudioFormat | None = None

    @property
    def output_format(self) -> AudioFormat | None:
        return self._output_format

    @property
    def output_next_seq(self) -> int:
        return self._output_next_seq

    @property
    def output_next_sample_index(self) -> int:
        return self._output_next_sample_index

    def push_chunk(self, chunk: AudioChunk) -> AudioChunk:
        self._validate_input_identity(chunk.source_id, chunk.stream_id)
        self._validate_or_set_input_format(chunk.format)
        self._validate_input_position(chunk.seq, chunk.sample_index)
        output_chunk = AudioChunk(
            source_id=self._config.output_source_id,
            stream_id=self._config.output_stream_id,
            seq=self._output_next_seq,
            sample_index=self._output_next_sample_index,
            capture_time_ns=_audio_timeline_time_ns(
                self._output_next_sample_index,
                chunk.format.sample_rate_hz,
            ),
            frame_count=chunk.frame_count,
            format=chunk.format,
            payload=chunk.payload,
        )
        self._input_next_seq = chunk.next_seq
        self._input_next_sample_index = chunk.next_sample_index
        self._output_next_seq = output_chunk.next_seq
        self._output_next_sample_index = output_chunk.next_sample_index
        self._output_format = output_chunk.format
        return output_chunk

    def push_request_final(self, final_marker: DoraAudioMetadata) -> None:
        self._validate_input_identity(final_marker.source_id, final_marker.stream_id)
        self._validate_or_set_input_format(final_marker.to_audio_format())
        self._validate_input_position(final_marker.seq, final_marker.sample_index)

    def _validate_input_identity(self, source_id: str, stream_id: str) -> None:
        if source_id != self._config.input_source_id:
            raise SpeakerStreamAdapterError(
                "Speaker stream input source mismatch: "
                f"expected {self._config.input_source_id!r}, got {source_id!r}"
            )
        if stream_id != self._config.input_stream_id:
            raise SpeakerStreamAdapterError(
                "Speaker stream input stream mismatch: "
                f"expected {self._config.input_stream_id!r}, got {stream_id!r}"
            )

    def _validate_or_set_input_format(self, audio_format: AudioFormat) -> None:
        if self._input_format is None:
            self._input_format = audio_format
            return
        if self._input_format != audio_format:
            raise SpeakerStreamAdapterError("Speaker stream input audio format changed")

    def _validate_input_position(self, seq: int, sample_index: int) -> None:
        if self._input_next_seq is None:
            if seq != 0:
                raise SpeakerStreamAdapterError(
                    f"First speaker stream input seq must be 0, got {seq}"
                )
            if sample_index != 0:
                raise SpeakerStreamAdapterError(
                    "First speaker stream input sample_index must be 0, "
                    f"got {sample_index}"
                )
            return
        if seq != self._input_next_seq:
            raise SpeakerStreamAdapterError(
                f"Speaker stream input seq discontinuity: "
                f"expected {self._input_next_seq}, got {seq}"
            )
        if sample_index != self._input_next_sample_index:
            raise SpeakerStreamAdapterError(
                "Speaker stream input sample_index discontinuity: "
                f"expected {self._input_next_sample_index}, got {sample_index}"
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Adapt request-final playback audio into a continuous speaker stream."
    )
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--input-source-id", required=True)
    parser.add_argument("--input-stream-id", required=True)
    parser.add_argument("--output-source-id", required=True)
    parser.add_argument("--output-stream-id", required=True)
    parser.add_argument("--output-start-seq", type=int, default=0)
    parser.add_argument("--output-start-sample-index", type=int, default=0)
    parser.add_argument(
        "--output-drain-seconds",
        type=float,
        default=DEFAULT_DORA_OUTPUT_DRAIN_SECONDS,
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("speaker_stream_adapter requires --dora")

    from dora import Node

    config = SpeakerStreamAdapterConfig(
        input_source_id=args.input_source_id,
        input_stream_id=args.input_stream_id,
        output_source_id=args.output_source_id,
        output_stream_id=args.output_stream_id,
        output_start_seq=args.output_start_seq,
        output_start_sample_index=args.output_start_sample_index,
        output_drain_seconds=args.output_drain_seconds,
    )
    summary = run_speaker_stream_adapter_events(Node(), config)
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def run_speaker_stream_adapter_events(
    node,
    config: SpeakerStreamAdapterConfig,
) -> SpeakerStreamAdapterSummary:
    state = SpeakerStreamAdapterState(config)
    input_chunks = 0
    input_request_finals = 0
    output_chunks = 0

    for event in node:
        if event is None:
            raise SpeakerStreamAdapterError(
                "DORA event stream ended before speaker stream input closed"
            )
        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            raise SpeakerStreamAdapterError("DORA STOP arrived before speaker stream input closed")
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id != "audio":
                raise SpeakerStreamAdapterError(f"Unexpected DORA input id: {input_id!r}")
            _send_output_final(node, state, config)
            time.sleep(config.output_drain_seconds)
            return SpeakerStreamAdapterSummary(
                input_chunks=input_chunks,
                input_request_finals=input_request_finals,
                output_chunks=output_chunks,
                output_final_sent=True,
                final_sample_index=state.output_next_sample_index,
            )
        if event_type != "INPUT":
            raise SpeakerStreamAdapterError(f"Unexpected DORA event type: {event_type!r}")

        input_id = _required_event_text(event, "id")
        if input_id != "audio":
            raise SpeakerStreamAdapterError(f"Unexpected DORA input id: {input_id!r}")

        payload = event.get("value")
        metadata = validate_dora_audio_metadata(event.get("metadata"))
        if metadata.final:
            final_marker = validate_dora_audio_final_marker(payload, metadata)
            state.push_request_final(final_marker)
            input_request_finals += 1
            continue

        output_chunk = state.push_chunk(decode_audio_chunk_from_dora(payload, metadata))
        encoded_payload, encoded_metadata = encode_audio_chunk_for_dora(output_chunk)
        node.send_output("audio", encoded_payload, metadata=encoded_metadata.to_dora_metadata())
        input_chunks += 1
        output_chunks += 1

    raise SpeakerStreamAdapterError("DORA event stream ended without input closure")


def _send_output_final(
    node,
    state: SpeakerStreamAdapterState,
    config: SpeakerStreamAdapterConfig,
) -> None:
    audio_format = state.output_format
    if audio_format is None:
        raise SpeakerStreamAdapterError("Speaker stream input closed before any audio chunk")
    payload, metadata = encode_audio_final_marker_for_dora(
        source_id=config.output_source_id,
        stream_id=config.output_stream_id,
        seq=state.output_next_seq,
        sample_index=state.output_next_sample_index,
        capture_time_ns=_audio_timeline_time_ns(
            state.output_next_sample_index,
            audio_format.sample_rate_hz,
        ),
        audio_format=audio_format,
    )
    node.send_output("audio", payload, metadata=metadata.to_dora_metadata())


def _audio_timeline_time_ns(sample_index: int, sample_rate_hz: int) -> int:
    return sample_index * 1_000_000_000 // sample_rate_hz


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise SpeakerStreamAdapterError(f"DORA event field {key!r} must be a string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
