"""PCM WAV offline read helpers."""

from __future__ import annotations

import wave
from collections.abc import Iterator
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from fluent_dialogue_dora.contracts import AudioChunk, AudioFormat
from fluent_dialogue_dora.offline.raw_pcm import capture_time_ns_for_frame_offset


class WavPcmError(ValueError):
    """Raised when WAV input cannot preserve the fluent-dialogue-dora audio contract."""


class WavPcmFileNotFoundError(FileNotFoundError):
    """Raised when an explicit WAV input path is missing."""


class WavPcmEmptyInputError(WavPcmError):
    """Raised when a WAV stream contains no complete audio frames."""


class WavPcmUnsupportedFormatError(WavPcmError):
    """Raised when a WAV stream uses an unsupported audio format."""


class WavPcmReadConfig(BaseModel):
    """Explicit configuration for reading PCM WAV as timed audio chunks."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    path: Path
    chunk_frames: int = Field(gt=0)
    source_id: str = Field(min_length=1)
    stream_id: str = Field(min_length=1)
    start_seq: int = Field(default=0, ge=0)
    start_sample_index: int = Field(default=0, ge=0)
    start_capture_time_ns: int = Field(ge=0)
    expected_sample_rate_hz: int | None = Field(default=None, gt=0)
    expected_channels: int | None = Field(default=None, gt=0)


def iter_wav_pcm_chunks(config: WavPcmReadConfig) -> Iterator[AudioChunk]:
    """Read PCM WAV and yield validated ``AudioChunk`` values."""

    _validate_input_path(config.path)
    with wave.open(str(config.path), "rb") as wav_file:
        audio_format = _audio_format_from_wav(config, wav_file)
        total_frames = wav_file.getnframes()
        if total_frames <= 0:
            raise WavPcmEmptyInputError(f"WAV input contains no frames: {config.path}")

        seq = config.start_seq
        sample_index = config.start_sample_index
        frames_remaining = total_frames
        while frames_remaining > 0:
            frames_to_read = min(config.chunk_frames, frames_remaining)
            payload = wav_file.readframes(frames_to_read)
            frame_count = _validated_payload_frame_count(
                config=config,
                payload=payload,
                audio_format=audio_format,
            )
            if frame_count <= 0:
                raise WavPcmEmptyInputError(f"WAV input ended before expected frames: {config.path}")
            yield AudioChunk(
                source_id=config.source_id,
                stream_id=config.stream_id,
                seq=seq,
                sample_index=sample_index,
                capture_time_ns=capture_time_ns_for_frame_offset(
                    config.start_capture_time_ns,
                    sample_index - config.start_sample_index,
                    audio_format.sample_rate_hz,
                ),
                frame_count=frame_count,
                format=audio_format,
                payload=payload,
            )
            seq += 1
            sample_index += frame_count
            frames_remaining -= frame_count


def _validate_input_path(path: Path) -> None:
    if not path.exists():
        raise WavPcmFileNotFoundError(f"WAV input file does not exist: {path}")
    if not path.is_file():
        raise WavPcmError(f"WAV input path is not a file: {path}")


def _audio_format_from_wav(
    config: WavPcmReadConfig,
    wav_file: wave.Wave_read,
) -> AudioFormat:
    if wav_file.getcomptype() != "NONE":
        raise WavPcmUnsupportedFormatError(
            f"WAV compression is not supported: {wav_file.getcomptype()}"
        )
    sample_width_bytes = wav_file.getsampwidth()
    if sample_width_bytes != 2:
        raise WavPcmUnsupportedFormatError(
            "Only 16-bit PCM WAV is supported by wav_pcm_source: "
            f"sample_width_bytes={sample_width_bytes}"
        )
    sample_rate_hz = wav_file.getframerate()
    channels = wav_file.getnchannels()
    if config.expected_sample_rate_hz is not None and (
        sample_rate_hz != config.expected_sample_rate_hz
    ):
        raise WavPcmUnsupportedFormatError(
            "WAV sample_rate_hz does not match expectation: "
            f"expected={config.expected_sample_rate_hz}, actual={sample_rate_hz}"
        )
    if config.expected_channels is not None and channels != config.expected_channels:
        raise WavPcmUnsupportedFormatError(
            "WAV channels does not match expectation: "
            f"expected={config.expected_channels}, actual={channels}"
        )
    return AudioFormat(
        sample_rate_hz=sample_rate_hz,
        channels=channels,
        sample_format="s16le",
        channel_layout="interleaved",
    )


def _validated_payload_frame_count(
    *,
    config: WavPcmReadConfig,
    payload: bytes,
    audio_format: AudioFormat,
) -> int:
    frame_size_bytes = audio_format.frame_size_bytes
    if len(payload) % frame_size_bytes != 0:
        raise WavPcmUnsupportedFormatError(
            "WAV payload size is not aligned to complete frames: "
            f"size={len(payload)}, frame_size_bytes={frame_size_bytes}, path={config.path}"
        )
    return len(payload) // frame_size_bytes
