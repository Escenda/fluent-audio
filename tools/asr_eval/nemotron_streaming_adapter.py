"""Small ASR session adapter for streaming evaluation harnesses."""

from __future__ import annotations

import argparse
import sys
import threading
import time
from array import array
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from fluent_dialogue_dora.contracts import AsrCancel, AsrStart, AsrStop, AudioChunk, AudioFormat
from nodes.asr.nemotron_streaming.backend import (
    DEFAULT_NEMOTRON_MODEL_NAME,
    NemotronBackendSettings,
    build_nemotron_backend,
)
from nodes.asr.nemotron_streaming.logic import StreamingAsrBackend

ASR_SAMPLE_RATE_HZ = 16_000
ASR_SOURCE_ID = "asr_eval"
ASR_STREAM_ID = "audio/asr-eval"
ASR_SESSION_ID = "asr-web-harness"


@dataclass(frozen=True, slots=True)
class PartialTranscript:
    seq: int
    text: str
    chunk_index: int
    sample_index: int
    elapsed_audio_s: float
    push_wall_s: float


@dataclass(frozen=True, slots=True)
class FinalTranscript:
    text: str
    sample_count: int
    stop_wall_s: float


class StreamingAsrSession(Protocol):
    def start(self) -> None:
        """Start one utterance."""

    def push_audio(
        self,
        samples: Sequence[float],
        *,
        sample_index: int,
        chunk_index: int,
    ) -> tuple[PartialTranscript, ...]:
        """Push one 16 kHz mono float32 audio chunk."""

    def stop(self, *, sample_count: int) -> FinalTranscript:
        """Finish the utterance and return final text."""

    def cancel(self, *, reason: str) -> None:
        """Cancel the active utterance."""


class StreamingAsrSessionFactory(Protocol):
    def create(self, utterance_id: str) -> StreamingAsrSession:
        """Create a session for one utterance."""


class NemotronSessionFactory:
    """Constructs sessions backed by the real Nemotron 3.5 streaming backend."""

    def __init__(
        self,
        *,
        model_name: str = DEFAULT_NEMOTRON_MODEL_NAME,
        model_extracted_dir: str | None = None,
        target_lang: str = "ja-JP",
        att_context_right_frames: int = 3,
        partial_agreement_steps: int = 1,
        partial_holdback_chars: int = 0,
        final_transcript_mode: str = "retranscribe",
        cuda_device: int | None = None,
    ) -> None:
        self._settings = NemotronBackendSettings(
            backend="nemo",
            model_name=model_name,
            model_extracted_dir=Path(model_extracted_dir) if model_extracted_dir is not None else None,
            target_lang=target_lang,
            att_context_right_frames=att_context_right_frames,
            partial_agreement_steps=partial_agreement_steps,
            partial_holdback_chars=partial_holdback_chars,
            final_transcript_mode=final_transcript_mode,
            cuda_device=cuda_device,
        )
        self._backend: StreamingAsrBackend | None = None
        self._lock = threading.Lock()

    def load_backend(self) -> None:
        with self._lock:
            if self._backend is None:
                self._backend = build_nemotron_backend(self._settings)

    def set_target_lang(self, target_lang: str) -> None:
        if not target_lang:
            raise ValueError("target_lang must be non-empty")
        with self._lock:
            self._settings = self._settings.model_copy(update={"target_lang": target_lang})
            if self._backend is not None:
                set_target_lang = getattr(self._backend, "set_target_lang", None)
                if set_target_lang is None:
                    raise RuntimeError("Nemotron backend does not support target_lang switching")
                set_target_lang(target_lang)

    def create(self, utterance_id: str) -> StreamingAsrSession:
        self.load_backend()
        if self._backend is None:
            raise RuntimeError("Nemotron backend was not loaded")
        return NemotronStreamingSession(self._backend, utterance_id=utterance_id)


class NemotronStreamingSession:
    def __init__(self, backend: StreamingAsrBackend, *, utterance_id: str) -> None:
        self._backend = backend
        self._utterance_id = utterance_id
        self._audio_format = AudioFormat(
            sample_rate_hz=ASR_SAMPLE_RATE_HZ,
            channels=1,
            sample_format="f32le",
            channel_layout="interleaved",
        )
        self._started = False
        self._stopped = False
        self._next_sample_index = 0
        self._next_partial_seq = 0

    def start(self) -> None:
        if self._started:
            raise ValueError("ASR session already started")
        self._backend.start(
            AsrStart(
                action="start",
                session_id=ASR_SESSION_ID,
                user_turn_id=self._utterance_id,
                stream_id=ASR_STREAM_ID,
                seq=0,
                start_sample_index=0,
            ),
            self._audio_format,
        )
        self._started = True

    def push_audio(
        self,
        samples: Sequence[float],
        *,
        sample_index: int,
        chunk_index: int,
    ) -> tuple[PartialTranscript, ...]:
        self._require_active()
        if sample_index != self._next_sample_index:
            raise ValueError(
                "ASR session sample_index discontinuity: "
                f"expected {self._next_sample_index}, got {sample_index}"
            )
        payload, frame_count = _float32_payload(samples)
        if frame_count == 0:
            return ()

        chunk = AudioChunk(
            source_id=ASR_SOURCE_ID,
            stream_id=ASR_STREAM_ID,
            seq=chunk_index,
            sample_index=sample_index,
            capture_time_ns=(sample_index * 1_000_000_000) // ASR_SAMPLE_RATE_HZ,
            frame_count=frame_count,
            format=self._audio_format,
            payload=payload,
        )
        started = time.perf_counter()
        push_result = self._backend.push_audio(chunk)
        push_wall_s = time.perf_counter() - started
        self._next_sample_index += frame_count

        partials: list[PartialTranscript] = []
        elapsed_audio_s = self._next_sample_index / ASR_SAMPLE_RATE_HZ
        for text in push_result.partial_texts:
            partials.append(
                PartialTranscript(
                    seq=self._next_partial_seq,
                    text=text,
                    chunk_index=chunk_index,
                    sample_index=self._next_sample_index,
                    elapsed_audio_s=elapsed_audio_s,
                    push_wall_s=push_wall_s,
                )
            )
            self._next_partial_seq += 1
        return tuple(partials)

    def stop(self, *, sample_count: int) -> FinalTranscript:
        self._require_active()
        if sample_count != self._next_sample_index:
            raise ValueError(
                "ASR session stop sample_count does not match pushed audio: "
                f"stop={sample_count}, pushed={self._next_sample_index}"
            )
        started = time.perf_counter()
        final_result = self._backend.stop(
            AsrStop(
                action="stop",
                session_id=ASR_SESSION_ID,
                user_turn_id=self._utterance_id,
                stream_id=ASR_STREAM_ID,
                seq=1,
                stop_sample_index=sample_count,
            )
        )
        self._stopped = True
        return FinalTranscript(
            text=final_result.text,
            sample_count=sample_count,
            stop_wall_s=time.perf_counter() - started,
        )

    def cancel(self, *, reason: str) -> None:
        if not self._started or self._stopped:
            return
        self._backend.cancel(
            AsrCancel(
                action="cancel",
                session_id=ASR_SESSION_ID,
                user_turn_id=self._utterance_id,
                stream_id=ASR_STREAM_ID,
                seq=1,
                reason=reason,
            )
        )
        self._stopped = True

    def _require_active(self) -> None:
        if not self._started:
            raise ValueError("ASR session is not started")
        if self._stopped:
            raise ValueError("ASR session is already stopped")


def add_nemotron_session_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--model-name", default=DEFAULT_NEMOTRON_MODEL_NAME)
    parser.add_argument("--model-extracted-dir")
    parser.add_argument("--target-lang", default="ja-JP")
    parser.add_argument("--att-context-right-frames", type=int, default=3)
    parser.add_argument("--partial-agreement-steps", type=int, default=1)
    parser.add_argument("--partial-holdback-chars", type=int, default=0)
    parser.add_argument(
        "--final-transcript-mode",
        choices=["retranscribe", "streaming"],
        default="retranscribe",
    )
    parser.add_argument("--cuda-device", type=int)


def nemotron_session_factory_from_args(args: argparse.Namespace) -> NemotronSessionFactory:
    return NemotronSessionFactory(
        model_name=args.model_name,
        model_extracted_dir=args.model_extracted_dir,
        target_lang=args.target_lang,
        att_context_right_frames=args.att_context_right_frames,
        partial_agreement_steps=args.partial_agreement_steps,
        partial_holdback_chars=args.partial_holdback_chars,
        final_transcript_mode=args.final_transcript_mode,
        cuda_device=args.cuda_device,
    )


def _float32_payload(samples: Sequence[float]) -> tuple[bytes, int]:
    dimensions = getattr(samples, "ndim", 1)
    if dimensions != 1:
        raise ValueError(f"ASR audio chunk must be mono 1-D samples, got {dimensions} dimensions")
    data = array("f", samples)
    if data.itemsize != 4:
        raise ValueError(f"ASR float array itemsize must be 4 bytes, got {data.itemsize}")
    if sys.byteorder != "little":
        data.byteswap()
    return data.tobytes(), len(data)
