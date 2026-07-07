"""Audio transport contracts for fluent-dialogue-dora."""

from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBytes,
    StringConstraints,
    model_validator,
)

SampleFormat = Literal["s16le", "f32le"]
ChannelLayout = Literal["interleaved"]
NonEmptyString = Annotated[str, StringConstraints(min_length=1)]


class AudioContractError(ValueError):
    """Raised when audio contract invariants are violated."""


class AudioChunkContinuityError(AudioContractError):
    """Raised when two audio chunks cannot be treated as contiguous."""


class AudioFormat(BaseModel):
    """PCM audio format carried by every audio chunk."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    sample_rate_hz: int = Field(gt=0)
    channels: int = Field(gt=0)
    sample_format: SampleFormat = "s16le"
    channel_layout: ChannelLayout = "interleaved"

    @property
    def bytes_per_sample(self) -> int:
        if self.sample_format == "s16le":
            return 2
        if self.sample_format == "f32le":
            return 4
        raise AudioContractError(f"Unsupported sample format: {self.sample_format}")

    @property
    def frame_size_bytes(self) -> int:
        return self.channels * self.bytes_per_sample


class AudioChunk(BaseModel):
    """A contiguous raw PCM payload with explicit timing and format."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    source_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    sample_index: int = Field(ge=0)
    capture_time_ns: int = Field(ge=0)
    frame_count: int = Field(gt=0)
    format: AudioFormat
    payload: StrictBytes

    @model_validator(mode="after")
    def validate_payload_size(self) -> "AudioChunk":
        expected_size = self.frame_count * self.format.frame_size_bytes
        actual_size = len(self.payload)
        if actual_size != expected_size:
            raise ValueError(
                "AudioChunk payload size mismatch: "
                f"expected {expected_size} bytes from frame_count={self.frame_count} "
                f"and frame_size_bytes={self.format.frame_size_bytes}, got {actual_size} bytes"
            )
        return self

    @property
    def payload_size_bytes(self) -> int:
        return len(self.payload)

    @property
    def next_seq(self) -> int:
        return self.seq + 1

    @property
    def next_sample_index(self) -> int:
        return self.sample_index + self.frame_count

    def require_contiguous_next(self, next_chunk: "AudioChunk") -> None:
        require_contiguous_audio_chunks(self, next_chunk)


def require_contiguous_audio_chunks(previous: AudioChunk, current: AudioChunk) -> None:
    """Require that ``current`` is the exact next chunk after ``previous``."""

    if current.source_id != previous.source_id:
        raise AudioChunkContinuityError(
            f"AudioChunk source mismatch: {previous.source_id!r} -> {current.source_id!r}"
        )
    if current.stream_id != previous.stream_id:
        raise AudioChunkContinuityError(
            f"AudioChunk stream mismatch: {previous.stream_id!r} -> {current.stream_id!r}"
        )
    if current.format != previous.format:
        raise AudioChunkContinuityError("AudioChunk format mismatch between contiguous chunks")
    if current.seq != previous.next_seq:
        raise AudioChunkContinuityError(
            f"AudioChunk seq discontinuity: expected {previous.next_seq}, got {current.seq}"
        )
    if current.sample_index != previous.next_sample_index:
        raise AudioChunkContinuityError(
            f"AudioChunk sample_index discontinuity: expected {previous.next_sample_index}, "
            f"got {current.sample_index}"
        )
