"""Backend selection surface for the Nemotron streaming ASR node."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from nodes.perception.nemotron_streaming.logic import StreamingAsrBackend

DEFAULT_NEMOTRON_MODEL_NAME = "nvidia/nemotron-3.5-asr-streaming-0.6b"
NEMOTRON_ATT_CONTEXT_RIGHT_FRAMES: tuple[int, ...] = (0, 1, 3, 6, 13)

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
    """Construct the configured backend or fail closed if it is not implemented."""

    if settings.backend == "nemo":
        raise NemotronBackendUnavailableError(
            "NeMo backend is configured but not implemented in fluent-audio yet. "
            "Green status requires installing PyTorch/NeMo on target hardware, "
            f"downloading {settings.model_name!r}, wiring cache-aware streaming, "
            "and running a real-model smoke test."
        )
    raise NemotronBackendUnavailableError(
        f"Unsupported Nemotron backend: {settings.backend!r}"
    )
