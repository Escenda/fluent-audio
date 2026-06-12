"""Backend selection surface for the Nemotron streaming ASR node."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from fluent_audio.contracts import (
    AsrCancel,
    AsrStart,
    AsrStop,
    AudioChunk,
    AudioFormat,
)
from nodes.asr.nemotron_streaming.logic import (
    AsrBackendFinalResult,
    AsrBackendPushResult,
    StreamingAsrBackend,
)

DEFAULT_NEMOTRON_MODEL_NAME = "nvidia/nemotron-3.5-asr-streaming-0.6b"
NEMOTRON_ATT_CONTEXT_RIGHT_FRAMES: tuple[int, ...] = (0, 1, 3, 6, 13)
NEMOTRON_RUNTIME_MODULES: tuple[str, ...] = (
    "numpy",
    "torch",
    "nemo.collections.asr.models",
    "nemo.collections.asr.parts.utils.streaming_utils",
)
LANG_TAG_PATTERN = re.compile(r"\s*<[a-z]{2}(?:-[A-Z]{2})?>\s*$")

NemotronBackendKind = Literal["nemo"]
NemotronComputeDtype = Literal["float32"]


class NemotronBackendError(ValueError):
    """Raised when a Nemotron backend cannot be constructed."""


class NemotronBackendUnavailableError(NemotronBackendError):
    """Raised when a configured backend has no implemented runtime yet."""


class NemotronBackendSettings(BaseModel):
    """Validated settings for an actual Nemotron backend implementation."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    backend: NemotronBackendKind
    model_name: str = Field(default=DEFAULT_NEMOTRON_MODEL_NAME, min_length=1)
    target_lang: str = Field(default="auto", min_length=1)
    strip_lang_tags: bool = True
    att_context_left_frames: int = Field(default=56, gt=0)
    att_context_right_frames: int = Field(default=3, ge=0)
    compute_dtype: NemotronComputeDtype = "float32"
    cuda_device: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_streaming_context(self) -> Self:
        if self.att_context_right_frames not in NEMOTRON_ATT_CONTEXT_RIGHT_FRAMES:
            allowed = ", ".join(str(value) for value in NEMOTRON_ATT_CONTEXT_RIGHT_FRAMES)
            raise ValueError(
                "Nemotron att_context_right_frames must be one of "
                f"{allowed}; got {self.att_context_right_frames}"
            )
        return self

    @property
    def att_context_size(self) -> tuple[int, int]:
        return (self.att_context_left_frames, self.att_context_right_frames)

    @property
    def chunk_duration_ms(self) -> int:
        return (1 + self.att_context_right_frames) * 80


def build_nemotron_backend(settings: NemotronBackendSettings) -> StreamingAsrBackend:
    """Construct the configured backend or fail closed when runtime deps are absent."""

    if settings.backend == "nemo":
        return NemoCacheAwareStreamingBackend(settings)
    raise NemotronBackendUnavailableError(f"Unsupported Nemotron backend: {settings.backend!r}")


class NemoCacheAwareStreamingBackend(StreamingAsrBackend):
    """Cache-aware NeMo RNNT backend for one active ASR turn at a time.

    The backend keeps NeMo's streaming buffer and encoder/decoder cache alive
    for the active turn. It emits only append-only hypothesis suffixes as live
    deltas; hypotheses that would rewrite already emitted text are held back and
    resolved by the final full-turn transcript.
    """

    def __init__(self, settings: NemotronBackendSettings) -> None:
        missing_modules = _missing_runtime_modules()
        if missing_modules:
            raise NemotronBackendUnavailableError(
                "NeMo backend requires runtime modules that are not installed: "
                + ", ".join(missing_modules)
            )

        import numpy as np
        import torch
        from nemo.collections.asr.models import ASRModel
        from nemo.collections.asr.parts.utils.streaming_utils import CacheAwareStreamingAudioBuffer

        self._settings = settings
        self._np = np
        self._torch = torch
        self._streaming_buffer_cls = CacheAwareStreamingAudioBuffer
        self._device = _resolve_cuda_device(torch, settings.cuda_device)
        model_ref = _resolve_model_ref(settings.model_name)
        if model_ref.is_file_path:
            self._model = ASRModel.restore_from(
                str(model_ref.path),
                map_location=str(self._device),
            )
        else:
            self._model = ASRModel.from_pretrained(
                model_name=settings.model_name,
                map_location=str(self._device),
            )
        self._model = self._model.to(self._device)
        self._model.eval()
        self._model.encoder.setup_streaming_params(att_context_size=list(settings.att_context_size))
        self._model.set_inference_prompt(settings.target_lang)
        self._sample_rate_hz = int(self._model.cfg.preprocessor.sample_rate)

        self._active = False
        self._pending_sample_chunks: list[bytes] = []
        self._pending_frame_count = 0
        self._emitted_text = ""
        self._streaming_buffer = None
        self._stream_id = -1
        self._cache_last_channel = None
        self._cache_last_time = None
        self._cache_last_channel_len = None
        self._previous_hypotheses = None
        self._stream_step_index = 0

    def start(self, control: AsrStart, audio_format: AudioFormat) -> None:
        if self._active:
            raise NemotronBackendError("NeMo backend start received while active")
        if audio_format.sample_rate_hz != self._sample_rate_hz:
            raise NemotronBackendError(
                "NeMo backend sample rate mismatch: "
                f"model={self._sample_rate_hz}, audio={audio_format.sample_rate_hz}"
            )
        if audio_format.channels != 1:
            raise NemotronBackendError("NeMo backend requires mono audio")

        self._active = True
        self._pending_sample_chunks = []
        self._pending_frame_count = 0
        self._emitted_text = ""
        self._streaming_buffer = self._streaming_buffer_cls(
            model=self._model,
            online_normalization=False,
        )
        (
            self._cache_last_channel,
            self._cache_last_time,
            self._cache_last_channel_len,
        ) = self._model.encoder.get_initial_cache_state(batch_size=1)
        self._previous_hypotheses = None
        self._stream_id = -1
        self._stream_step_index = 0

    def push_audio(self, chunk: AudioChunk) -> AsrBackendPushResult:
        self._require_active_turn()
        samples = self._decode_audio_samples(chunk)
        self._pending_sample_chunks.append(samples.tobytes())
        self._pending_frame_count += chunk.frame_count
        self._append_stream_audio(samples)
        partial_texts, delta_texts = self._consume_available_stream_updates()
        return AsrBackendPushResult(
            partial_texts=partial_texts,
            delta_texts=delta_texts,
        )

    def stop(self, control: AsrStop) -> AsrBackendFinalResult:
        self._require_active_turn()
        if self._pending_frame_count <= 0:
            raise NemotronBackendError("NeMo backend stop received before audio")
        samples = self._np.frombuffer(
            b"".join(self._pending_sample_chunks),
            dtype=self._np.dtype("<f4"),
        ).astype(self._np.float32, copy=True)
        text = self._transcribe_complete_turn(samples).strip()
        self._reset_active_stream()
        return AsrBackendFinalResult(text=text)

    def cancel(self, control: AsrCancel) -> None:
        self._reset_active_stream()

    def _decode_audio_samples(self, chunk: AudioChunk):
        if chunk.format.sample_format == "s16le":
            samples = self._np.frombuffer(chunk.payload, dtype=self._np.dtype("<i2"))
            return samples.astype(self._np.float32) / self._np.float32(32768.0)
        if chunk.format.sample_format == "f32le":
            samples = self._np.frombuffer(chunk.payload, dtype=self._np.dtype("<f4"))
            return samples.astype(self._np.float32, copy=True)
        raise NemotronBackendError(
            f"Unsupported NeMo backend audio sample_format: {chunk.format.sample_format!r}"
        )

    def _append_stream_audio(self, samples) -> None:
        if self._streaming_buffer is None:
            raise NemotronBackendError("NeMo backend streaming buffer is not initialized")
        _processed_signal, _processed_signal_length, stream_id = (
            self._streaming_buffer.append_audio(samples, stream_id=self._stream_id)
        )
        if self._stream_id < 0:
            self._stream_id = 0
        else:
            self._stream_id = int(stream_id)

    def _consume_available_stream_updates(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        if self._streaming_buffer is None:
            raise NemotronBackendError("NeMo backend streaming buffer is not initialized")
        if self._cache_last_channel is None:
            raise NemotronBackendError("NeMo backend encoder cache is not initialized")
        partial_texts: list[str] = []
        delta_texts: list[str] = []
        for chunk_audio, chunk_lengths in self._streaming_buffer:
            drop_extra_pre_encoded = 0
            if self._stream_step_index != 0:
                drop_extra_pre_encoded = self._model.encoder.streaming_cfg.drop_extra_pre_encoded
            with self._torch.inference_mode():
                result = self._model.conformer_stream_step(
                    processed_signal=chunk_audio,
                    processed_signal_length=chunk_lengths,
                    cache_last_channel=self._cache_last_channel,
                    cache_last_time=self._cache_last_time,
                    cache_last_channel_len=self._cache_last_channel_len,
                    keep_all_outputs=self._streaming_buffer.is_buffer_empty(),
                    previous_hypotheses=self._previous_hypotheses,
                    previous_pred_out=None,
                    drop_extra_pre_encoded=drop_extra_pre_encoded,
                    return_transcription=True,
                    return_log_probs=False,
                )
            (
                _greedy_predictions,
                transcribed,
                self._cache_last_channel,
                self._cache_last_time,
                self._cache_last_channel_len,
                self._previous_hypotheses,
            ) = result
            self._stream_step_index += 1
            normalized_text = self._normalized_hypothesis_text(transcribed)
            if not normalized_text:
                continue
            partial_texts.append(normalized_text)
            self._emitted_text, delta = _append_only_delta(
                emitted_text=self._emitted_text,
                hypothesis_text=normalized_text,
            )
            if delta is not None:
                delta_texts.append(delta)
        return tuple(partial_texts), tuple(delta_texts)

    def _transcribe_complete_turn(self, samples) -> str:
        streaming_buffer = self._streaming_buffer_cls(
            model=self._model,
            online_normalization=False,
        )
        streaming_buffer.append_audio(samples, stream_id=-1)
        (
            cache_last_channel,
            cache_last_time,
            cache_last_channel_len,
        ) = self._model.encoder.get_initial_cache_state(batch_size=1)
        previous_hypotheses = None
        current_text = ""
        emitted_text = ""
        for step_index, (chunk_audio, chunk_lengths) in enumerate(streaming_buffer):
            drop_extra_pre_encoded = 0
            if step_index != 0:
                drop_extra_pre_encoded = self._model.encoder.streaming_cfg.drop_extra_pre_encoded
            with self._torch.inference_mode():
                result = self._model.conformer_stream_step(
                    processed_signal=chunk_audio,
                    processed_signal_length=chunk_lengths,
                    cache_last_channel=cache_last_channel,
                    cache_last_time=cache_last_time,
                    cache_last_channel_len=cache_last_channel_len,
                    keep_all_outputs=streaming_buffer.is_buffer_empty(),
                    previous_hypotheses=previous_hypotheses,
                    previous_pred_out=None,
                    drop_extra_pre_encoded=drop_extra_pre_encoded,
                    return_transcription=True,
                    return_log_probs=False,
                )
            (
                _greedy_predictions,
                transcribed,
                cache_last_channel,
                cache_last_time,
                cache_last_channel_len,
                previous_hypotheses,
            ) = result
            normalized_text = self._normalized_hypothesis_text(transcribed)
            if not normalized_text:
                continue
            current_text = normalized_text
            emitted_text, _delta = _append_only_delta(
                emitted_text=emitted_text,
                hypothesis_text=normalized_text,
            )
        return current_text

    def _normalized_hypothesis_text(self, transcribed) -> str:
        hypothesis_text = _single_hypothesis_text(transcribed)
        normalized_text = (
            _strip_lang_tag(hypothesis_text) if self._settings.strip_lang_tags else hypothesis_text
        )
        return normalized_text.strip()

    def _require_active_turn(self) -> None:
        if not self._active:
            raise NemotronBackendError("NeMo backend has no active ASR turn")

    def _reset_active_stream(self) -> None:
        self._active = False
        self._pending_sample_chunks = []
        self._pending_frame_count = 0
        self._emitted_text = ""
        self._streaming_buffer = None
        self._stream_id = -1
        self._cache_last_channel = None
        self._cache_last_time = None
        self._cache_last_channel_len = None
        self._previous_hypotheses = None
        self._stream_step_index = 0


class _ResolvedModelRef(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    is_file_path: bool
    path: Path | None = None


def _missing_runtime_modules() -> tuple[str, ...]:
    missing: list[str] = []
    for module_name in NEMOTRON_RUNTIME_MODULES:
        if importlib.util.find_spec(module_name) is None:
            missing.append(module_name)
    return tuple(missing)


def _resolve_cuda_device(torch_module, cuda_device: int | None):
    if not torch_module.cuda.is_available():
        raise NemotronBackendUnavailableError("NeMo backend requires CUDA")
    if cuda_device is None:
        return torch_module.device("cuda")
    device_count = torch_module.cuda.device_count()
    if cuda_device >= device_count:
        raise NemotronBackendUnavailableError(
            f"Requested CUDA device {cuda_device}, but only {device_count} device(s) are visible"
        )
    return torch_module.device(f"cuda:{cuda_device}")


def _resolve_model_ref(model_name: str) -> _ResolvedModelRef:
    path = Path(model_name).expanduser()
    if path.is_file():
        return _ResolvedModelRef(is_file_path=True, path=path)
    if model_name.endswith(".nemo"):
        raise NemotronBackendError(f"Nemotron model file does not exist: {model_name}")
    return _ResolvedModelRef(is_file_path=False)


def _single_hypothesis_text(hypotheses) -> str:
    if len(hypotheses) != 1:
        raise NemotronBackendError(f"NeMo backend expected one hypothesis, got {len(hypotheses)}")
    text = hypotheses[0].text
    if not isinstance(text, str):
        raise NemotronBackendError("NeMo backend hypothesis text must be a string")
    return text


def _strip_lang_tag(text: str) -> str:
    return LANG_TAG_PATTERN.sub("", text)


def _append_only_delta(
    *,
    emitted_text: str,
    hypothesis_text: str,
) -> tuple[str, str | None]:
    if not hypothesis_text:
        return emitted_text, None
    if hypothesis_text == emitted_text:
        return emitted_text, None
    if not hypothesis_text.startswith(emitted_text):
        return emitted_text, None
    delta = hypothesis_text[len(emitted_text) :]
    if not delta:
        return emitted_text, None
    return hypothesis_text, delta
