"""Pure ONNX Silero VAD core."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

import numpy as np
import onnxruntime as ort
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, Field, model_validator

EXPECTED_MODEL_SHA256 = "7ed98ddbad84ccac4cd0aeb3099049280713df825c610a8ed34543318f1b2c49"
DEFAULT_MODEL_PATH = Path(__file__).parent / "models" / "silero_vad_16k_op15.onnx"

SileroSampleRate = Literal[16000]


class SileroVadError(ValueError):
    """Raised when Silero VAD input or model execution violates the ONNX contract."""


class SileroVadConfig(BaseModel):
    """Configuration for the 16 kHz ONNX-only Silero VAD core."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    model_path: Path = DEFAULT_MODEL_PATH
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    sample_rate_hz: SileroSampleRate = 16_000
    window_frames: int = Field(default=512, gt=0)
    context_frames: int = Field(default=64, gt=0)

    @model_validator(mode="after")
    def validate_model_file(self) -> "SileroVadConfig":
        if self.window_frames != 512:
            raise ValueError("Silero ONNX VAD at 16 kHz requires window_frames=512")
        if self.context_frames != 64:
            raise ValueError("Silero ONNX VAD at 16 kHz requires context_frames=64")
        if not self.model_path.exists():
            raise ValueError(f"Silero ONNX model does not exist: {self.model_path}")
        if not self.model_path.is_file():
            raise ValueError(f"Silero ONNX model path is not a file: {self.model_path}")

        model_hash = sha256_file(self.model_path)
        if model_hash != EXPECTED_MODEL_SHA256:
            raise ValueError(
                "Silero ONNX model sha256 mismatch: "
                f"expected {EXPECTED_MODEL_SHA256}, got {model_hash}, path={self.model_path}"
            )
        return self


class SileroVadResult(BaseModel):
    """Probability for one finalized Silero VAD window."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    probability: float = Field(ge=0.0, le=1.0)
    is_speech: bool
    window_start_frame: int = Field(ge=0)
    window_frames: int = Field(gt=0)
    padded_frames: int = Field(default=0, ge=0)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as model_file:
        while True:
            chunk = model_file.read(1024 * 1024)
            if chunk == b"":
                break
            digest.update(chunk)
    return digest.hexdigest()


def s16le_mono_16k_to_float32_waveform(
    payload: bytes,
    *,
    sample_rate_hz: SileroSampleRate = 16_000,
) -> NDArray[np.float32]:
    """Convert explicit 16 kHz mono s16le PCM bytes into normalized float32 samples."""

    if sample_rate_hz != 16_000:
        raise SileroVadError(
            f"Silero ONNX VAD requires 16000 Hz input, got {sample_rate_hz} Hz"
        )
    if len(payload) % 2 != 0:
        raise SileroVadError(
            f"s16le mono payload byte length must be even, got {len(payload)} bytes"
        )

    pcm = np.frombuffer(payload, dtype="<i2")
    return (pcm.astype(np.float32) / np.float32(32768.0)).copy()


def pad_final_window(
    waveform: NDArray[np.float32],
    *,
    window_frames: int = 512,
) -> NDArray[np.float32]:
    """Return a final window with explicit zero padding when fewer than 512 frames remain."""

    if waveform.ndim != 1:
        raise SileroVadError(f"Silero VAD expects mono waveform, got ndim={waveform.ndim}")
    if waveform.dtype != np.float32:
        raise SileroVadError(f"Silero VAD expects float32 waveform, got dtype={waveform.dtype}")
    if window_frames <= 0:
        raise SileroVadError(f"window_frames must be positive, got {window_frames}")
    if waveform.shape[0] > window_frames:
        raise SileroVadError(
            "final flush window cannot exceed configured window size: "
            f"frames={waveform.shape[0]}, window_frames={window_frames}"
        )
    if waveform.shape[0] == window_frames:
        return np.ascontiguousarray(waveform, dtype=np.float32)

    padded = np.zeros((window_frames,), dtype=np.float32)
    padded[: waveform.shape[0]] = waveform.astype(np.float32, copy=False)
    return padded


class SileroVadSession:
    """Stateful Silero ONNX VAD session for contiguous 16 kHz mono audio."""

    def __init__(self, config: SileroVadConfig) -> None:
        self.config = config
        self._session = ort.InferenceSession(
            str(config.model_path),
            providers=["CPUExecutionProvider"],
        )
        self._validate_onnx_contract()
        self._state = np.zeros((2, 1, 128), dtype=np.float32)
        self._context = np.zeros((config.context_frames,), dtype=np.float32)
        self._buffer = np.zeros((0,), dtype=np.float32)
        self._next_window_start_frame = 0

    @property
    def buffered_frames(self) -> int:
        return int(self._buffer.shape[0])

    def reset(self) -> None:
        self._state.fill(0.0)
        self._context.fill(0.0)
        self._buffer = np.zeros((0,), dtype=np.float32)
        self._next_window_start_frame = 0

    def push(self, waveform: NDArray[np.float32]) -> list[SileroVadResult]:
        """Consume samples and return probabilities for complete 512-frame windows only."""

        samples = self._validate_waveform(waveform)
        if samples.shape[0] == 0:
            return []

        self._buffer = np.concatenate((self._buffer, samples))
        results: list[SileroVadResult] = []
        while self._buffer.shape[0] >= self.config.window_frames:
            window = self._buffer[: self.config.window_frames]
            self._buffer = self._buffer[self.config.window_frames :]
            results.append(self._run_window(window, padded_frames=0))
        return results

    def flush(self) -> list[SileroVadResult]:
        """Flush a final partial window using explicit zero padding."""

        if self._buffer.shape[0] == 0:
            return []

        remaining_frames = int(self._buffer.shape[0])
        padded = pad_final_window(self._buffer, window_frames=self.config.window_frames)
        self._buffer = np.zeros((0,), dtype=np.float32)
        return [
            self._run_window(
                padded,
                padded_frames=self.config.window_frames - remaining_frames,
            )
        ]

    def _run_window(
        self,
        window: NDArray[np.float32],
        *,
        padded_frames: int,
    ) -> SileroVadResult:
        if window.shape != (self.config.window_frames,):
            raise SileroVadError(
                "Silero VAD window shape mismatch: "
                f"expected ({self.config.window_frames},), got {window.shape}"
            )

        model_input = np.concatenate((self._context, window)).astype(np.float32, copy=False)
        input_feed: dict[str, NDArray[np.float32] | NDArray[np.int64]] = {
            "input": model_input.reshape(1, -1),
            "state": self._state,
            "sr": np.array(self.config.sample_rate_hz, dtype=np.int64),
        }
        raw_outputs = self._session.run(["output", "stateN"], input_feed)
        if len(raw_outputs) != 2:
            raise SileroVadError(
                f"Silero ONNX model returned {len(raw_outputs)} outputs, expected 2"
            )

        probability_array = np.asarray(raw_outputs[0], dtype=np.float32)
        next_state = np.asarray(raw_outputs[1], dtype=np.float32)
        if probability_array.shape != (1, 1):
            raise SileroVadError(
                "Silero ONNX output shape mismatch: "
                f"expected (1, 1), got {probability_array.shape}"
            )
        if next_state.shape != (2, 1, 128):
            raise SileroVadError(
                "Silero ONNX state shape mismatch: "
                f"expected (2, 1, 128), got {next_state.shape}"
            )

        self._state = next_state
        self._context = window[-self.config.context_frames :].astype(np.float32, copy=True)
        probability = float(probability_array[0, 0])
        result = SileroVadResult(
            probability=probability,
            is_speech=probability >= self.config.threshold,
            window_start_frame=self._next_window_start_frame,
            window_frames=self.config.window_frames,
            padded_frames=padded_frames,
        )
        self._next_window_start_frame += self.config.window_frames
        return result

    def _validate_onnx_contract(self) -> None:
        input_names = [node.name for node in self._session.get_inputs()]
        output_names = [node.name for node in self._session.get_outputs()]
        if input_names != ["input", "state", "sr"]:
            raise SileroVadError(f"Silero ONNX input contract mismatch: {input_names}")
        if output_names != ["output", "stateN"]:
            raise SileroVadError(f"Silero ONNX output contract mismatch: {output_names}")

    def _validate_waveform(self, waveform: NDArray[np.float32]) -> NDArray[np.float32]:
        if waveform.ndim != 1:
            raise SileroVadError(f"Silero VAD expects mono waveform, got ndim={waveform.ndim}")
        if waveform.dtype != np.float32:
            raise SileroVadError(f"Silero VAD expects float32 waveform, got dtype={waveform.dtype}")
        return np.ascontiguousarray(waveform, dtype=np.float32)
