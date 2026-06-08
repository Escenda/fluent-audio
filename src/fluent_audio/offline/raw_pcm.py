"""Headerless raw PCM offline read and write helpers."""

from __future__ import annotations

import base64
import binascii
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict, Field

from fluent_audio.contracts import (
    AudioChunk,
    AudioFormat,
    require_contiguous_audio_chunks,
)


class RawPcmError(ValueError):
    """Raised when raw PCM offline IO cannot preserve the audio contract."""


class RawPcmFileNotFoundError(FileNotFoundError):
    """Raised when an explicit raw PCM input path is missing."""


class RawPcmEmptyInputError(RawPcmError):
    """Raised when a raw PCM stream contains no complete audio frames."""


class RawPcmFrameAlignmentError(RawPcmError):
    """Raised when raw PCM bytes do not align to the configured frame size."""


class RawPcmOutputError(RawPcmError):
    """Raised when raw PCM output cannot be written as requested."""


class RawPcmChunkValidationError(RawPcmError):
    """Raised when an audio chunk does not match the configured stream."""


class RawPcmChunkJsonlError(RawPcmError):
    """Raised when chunk JSONL cannot be decoded into valid audio chunks."""


class RawPcmReadConfig(BaseModel):
    """Explicit configuration for reading headerless raw PCM."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    path: Path
    audio_format: AudioFormat
    chunk_frames: int = Field(gt=0)
    source_id: str = Field(min_length=1)
    stream_id: str = Field(min_length=1)
    start_seq: int = Field(default=0, ge=0)
    start_sample_index: int = Field(default=0, ge=0)


class RawPcmWriteConfig(BaseModel):
    """Explicit configuration for writing headerless raw PCM."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    path: Path
    expected_format: AudioFormat
    source_id: str = Field(min_length=1)
    stream_id: str = Field(min_length=1)
    overwrite: bool = False


class RawPcmWriteSummary(BaseModel):
    """Summary for a completed raw PCM write."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    path: Path
    chunks_written: int = Field(gt=0)
    frames_written: int = Field(gt=0)
    bytes_written: int = Field(gt=0)
    first_seq: int = Field(ge=0)
    last_seq: int = Field(ge=0)
    first_sample_index: int = Field(ge=0)
    next_sample_index: int = Field(ge=0)


class RawPcmChunkJsonRecord(BaseModel):
    """JSONL record used only for offline CLI smoke runs."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    source_id: str = Field(min_length=1)
    stream_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    sample_index: int = Field(ge=0)
    capture_time_ns: int = Field(ge=0)
    frame_count: int = Field(gt=0)
    format: AudioFormat
    payload_base64: str = Field(min_length=1)

    @classmethod
    def from_audio_chunk(cls, chunk: AudioChunk) -> Self:
        payload_base64 = base64.b64encode(chunk.payload).decode("ascii")
        return cls(
            source_id=chunk.source_id,
            stream_id=chunk.stream_id,
            seq=chunk.seq,
            sample_index=chunk.sample_index,
            capture_time_ns=chunk.capture_time_ns,
            frame_count=chunk.frame_count,
            format=chunk.format,
            payload_base64=payload_base64,
        )

    def to_audio_chunk(self) -> AudioChunk:
        try:
            payload = base64.b64decode(self.payload_base64, validate=True)
        except binascii.Error as exc:
            raise RawPcmChunkJsonlError("Invalid base64 payload in raw PCM chunk JSONL") from exc

        return AudioChunk(
            source_id=self.source_id,
            stream_id=self.stream_id,
            seq=self.seq,
            sample_index=self.sample_index,
            capture_time_ns=self.capture_time_ns,
            frame_count=self.frame_count,
            format=self.format,
            payload=payload,
        )


def capture_time_ns_for_sample_index(sample_index: int, sample_rate_hz: int) -> int:
    """Return deterministic offline capture time for an absolute sample index."""

    if sample_index < 0:
        raise RawPcmError(f"sample_index must be non-negative, got {sample_index}")
    if sample_rate_hz <= 0:
        raise RawPcmError(f"sample_rate_hz must be positive, got {sample_rate_hz}")
    return (sample_index * 1_000_000_000) // sample_rate_hz


def iter_raw_pcm_chunks(config: RawPcmReadConfig) -> Iterator[AudioChunk]:
    """Read headerless PCM and yield validated ``AudioChunk`` values."""

    path = config.path
    if not path.exists():
        raise RawPcmFileNotFoundError(f"Raw PCM input file does not exist: {path}")
    if not path.is_file():
        raise RawPcmError(f"Raw PCM input path is not a file: {path}")

    file_size_bytes = path.stat().st_size
    if file_size_bytes == 0:
        raise RawPcmEmptyInputError(f"Raw PCM input file is empty: {path}")

    frame_size_bytes = config.audio_format.frame_size_bytes
    if file_size_bytes % frame_size_bytes != 0:
        raise RawPcmFrameAlignmentError(
            "Raw PCM input size is not aligned to a complete frame: "
            f"size={file_size_bytes}, frame_size_bytes={frame_size_bytes}, path={path}"
        )

    chunk_size_bytes = config.chunk_frames * frame_size_bytes
    seq = config.start_seq
    sample_index = config.start_sample_index

    with path.open("rb") as raw_file:
        while True:
            payload = raw_file.read(chunk_size_bytes)
            if payload == b"":
                break
            if len(payload) % frame_size_bytes != 0:
                raise RawPcmFrameAlignmentError(
                    "Raw PCM chunk size is not aligned to a complete frame: "
                    f"size={len(payload)}, frame_size_bytes={frame_size_bytes}, path={path}"
                )

            frame_count = len(payload) // frame_size_bytes
            yield AudioChunk(
                source_id=config.source_id,
                stream_id=config.stream_id,
                seq=seq,
                sample_index=sample_index,
                capture_time_ns=capture_time_ns_for_sample_index(
                    sample_index,
                    config.audio_format.sample_rate_hz,
                ),
                frame_count=frame_count,
                format=config.audio_format,
                payload=payload,
            )
            seq += 1
            sample_index += frame_count


def write_raw_pcm_chunks(
    config: RawPcmWriteConfig,
    chunks: Iterable[AudioChunk],
) -> RawPcmWriteSummary:
    """Validate and write chunks as headerless PCM bytes."""

    _validate_output_target(config)

    temp_path = _temporary_output_path(config.path)
    if temp_path.exists():
        raise RawPcmOutputError(f"Temporary raw PCM output already exists: {temp_path}")

    chunks_written = 0
    frames_written = 0
    bytes_written = 0
    first_seq = 0
    last_seq = 0
    first_sample_index = 0
    next_sample_index = 0
    previous_chunk: AudioChunk | None = None

    try:
        with temp_path.open("xb") as output_file:
            for chunk in chunks:
                _validate_sink_chunk(config, previous_chunk, chunk)

                if chunks_written == 0:
                    first_seq = chunk.seq
                    first_sample_index = chunk.sample_index

                output_file.write(chunk.payload)
                chunks_written += 1
                frames_written += chunk.frame_count
                bytes_written += chunk.payload_size_bytes
                last_seq = chunk.seq
                next_sample_index = chunk.next_sample_index
                previous_chunk = chunk

            if chunks_written == 0:
                raise RawPcmEmptyInputError("Cannot write an empty raw PCM chunk stream")

        if config.path.exists() and not config.overwrite:
            raise RawPcmOutputError(f"Raw PCM output already exists: {config.path}")
        temp_path.replace(config.path)
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise

    return RawPcmWriteSummary(
        path=config.path,
        chunks_written=chunks_written,
        frames_written=frames_written,
        bytes_written=bytes_written,
        first_seq=first_seq,
        last_seq=last_seq,
        first_sample_index=first_sample_index,
        next_sample_index=next_sample_index,
    )


def write_raw_pcm_chunk_jsonl(
    path: Path,
    chunks: Iterable[AudioChunk],
    *,
    overwrite: bool,
) -> int:
    """Write chunk JSONL for offline CLI smoke runs."""

    _validate_jsonl_output_target(path, overwrite=overwrite)
    records_written = 0

    with path.open("x" if not overwrite else "w", encoding="utf-8") as jsonl_file:
        for chunk in chunks:
            record = RawPcmChunkJsonRecord.from_audio_chunk(chunk)
            jsonl_file.write(record.model_dump_json())
            jsonl_file.write("\n")
            records_written += 1

    if records_written == 0:
        path.unlink()
        raise RawPcmEmptyInputError("Cannot write an empty raw PCM chunk JSONL stream")

    return records_written


def iter_raw_pcm_chunk_jsonl(path: Path) -> Iterator[AudioChunk]:
    """Read offline chunk JSONL and yield validated audio chunks."""

    if not path.exists():
        raise RawPcmFileNotFoundError(f"Raw PCM chunk JSONL file does not exist: {path}")
    if not path.is_file():
        raise RawPcmError(f"Raw PCM chunk JSONL path is not a file: {path}")

    with path.open("r", encoding="utf-8") as jsonl_file:
        for line_number, line in enumerate(jsonl_file, start=1):
            stripped = line.strip()
            if stripped == "":
                raise RawPcmChunkJsonlError(
                    f"Raw PCM chunk JSONL contains an empty line at {path}:{line_number}"
                )
            try:
                record = RawPcmChunkJsonRecord.model_validate_json(stripped)
            except ValueError as exc:
                raise RawPcmChunkJsonlError(
                    f"Raw PCM chunk JSONL validation failed at {path}:{line_number}"
                ) from exc
            yield record.to_audio_chunk()


def _validate_output_target(config: RawPcmWriteConfig) -> None:
    path = config.path
    parent = path.parent
    if not parent.exists() or not parent.is_dir():
        raise RawPcmOutputError(f"Raw PCM output parent directory does not exist: {parent}")
    if path.exists() and path.is_dir():
        raise RawPcmOutputError(f"Raw PCM output path is a directory: {path}")
    if path.exists() and not config.overwrite:
        raise RawPcmOutputError(f"Raw PCM output already exists: {path}")


def _validate_jsonl_output_target(path: Path, *, overwrite: bool) -> None:
    parent = path.parent
    if not parent.exists() or not parent.is_dir():
        raise RawPcmOutputError(f"Raw PCM chunk JSONL parent directory does not exist: {parent}")
    if path.exists() and path.is_dir():
        raise RawPcmOutputError(f"Raw PCM chunk JSONL path is a directory: {path}")
    if path.exists() and not overwrite:
        raise RawPcmOutputError(f"Raw PCM chunk JSONL already exists: {path}")


def _temporary_output_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.tmp")


def _validate_sink_chunk(
    config: RawPcmWriteConfig,
    previous_chunk: AudioChunk | None,
    chunk: AudioChunk,
) -> None:
    if chunk.source_id != config.source_id:
        raise RawPcmChunkValidationError(
            f"Raw PCM source mismatch: expected {config.source_id!r}, got {chunk.source_id!r}"
        )
    if chunk.stream_id != config.stream_id:
        raise RawPcmChunkValidationError(
            f"Raw PCM stream mismatch: expected {config.stream_id!r}, got {chunk.stream_id!r}"
        )
    if chunk.format != config.expected_format:
        raise RawPcmChunkValidationError("Raw PCM format mismatch")
    if previous_chunk is not None:
        require_contiguous_audio_chunks(previous_chunk, chunk)
