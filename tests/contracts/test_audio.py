import pytest
from pydantic import ValidationError

from fluent_dialogue_dora.contracts import (
    AudioChunk,
    AudioChunkContinuityError,
    AudioFormat,
    require_contiguous_audio_chunks,
)


def _chunk(
    *,
    seq: int = 0,
    sample_index: int = 0,
    capture_time_ns: int = 1_000,
    frame_count: int = 160,
    audio_format: AudioFormat | None = None,
    payload: bytes | None = None,
) -> AudioChunk:
    resolved_format = audio_format or AudioFormat(sample_rate_hz=16_000, channels=1)
    resolved_payload = payload
    if resolved_payload is None:
        resolved_payload = b"\x00" * (frame_count * resolved_format.frame_size_bytes)
    return AudioChunk(
        source_id="fixture",
        stream_id="mic/main",
        seq=seq,
        sample_index=sample_index,
        capture_time_ns=capture_time_ns,
        frame_count=frame_count,
        format=resolved_format,
        payload=resolved_payload,
    )


def test_audio_format_byte_sizes() -> None:
    s16 = AudioFormat(sample_rate_hz=16_000, channels=1, sample_format="s16le")
    f32_stereo = AudioFormat(sample_rate_hz=48_000, channels=2, sample_format="f32le")

    assert s16.bytes_per_sample == 2
    assert s16.frame_size_bytes == 2
    assert f32_stereo.bytes_per_sample == 4
    assert f32_stereo.frame_size_bytes == 8


def test_audio_format_dump_roundtrips_without_computed_helpers() -> None:
    audio_format = AudioFormat(sample_rate_hz=16_000, channels=1)
    dumped = audio_format.model_dump()

    assert "bytes_per_sample" not in dumped
    assert "frame_size_bytes" not in dumped
    assert AudioFormat.model_validate(dumped) == audio_format


def test_audio_chunk_accepts_s16le_payload() -> None:
    chunk = _chunk(frame_count=160)

    assert chunk.payload_size_bytes == 320
    assert chunk.next_seq == 1
    assert chunk.next_sample_index == 160


def test_audio_chunk_accepts_f32le_payload() -> None:
    audio_format = AudioFormat(sample_rate_hz=48_000, channels=2, sample_format="f32le")
    chunk = _chunk(frame_count=64, audio_format=audio_format)

    assert chunk.format.bytes_per_sample == 4
    assert chunk.payload_size_bytes == 512


def test_audio_chunk_dump_roundtrips_without_computed_helpers() -> None:
    chunk = _chunk(frame_count=1, payload=b"\x00\x00")
    dumped = chunk.model_dump()

    assert "payload_size_bytes" not in dumped
    assert "next_seq" not in dumped
    assert "next_sample_index" not in dumped
    assert "bytes_per_sample" not in dumped["format"]
    assert "frame_size_bytes" not in dumped["format"]
    assert AudioChunk.model_validate(dumped) == chunk


def test_audio_format_rejects_zero_or_negative_shape() -> None:
    with pytest.raises(ValidationError):
        AudioFormat(sample_rate_hz=0, channels=1)
    with pytest.raises(ValidationError):
        AudioFormat(sample_rate_hz=16_000, channels=0)


def test_audio_chunk_rejects_empty_ids() -> None:
    with pytest.raises(ValidationError):
        AudioChunk(
            source_id="",
            stream_id="mic/main",
            seq=0,
            sample_index=0,
            capture_time_ns=0,
            frame_count=1,
            format=AudioFormat(sample_rate_hz=16_000, channels=1),
            payload=b"\x00\x00",
        )
    with pytest.raises(ValidationError):
        AudioChunk(
            source_id="fixture",
            stream_id="",
            seq=0,
            sample_index=0,
            capture_time_ns=0,
            frame_count=1,
            format=AudioFormat(sample_rate_hz=16_000, channels=1),
            payload=b"\x00\x00",
        )


def test_audio_chunk_rejects_payload_length_mismatch() -> None:
    with pytest.raises(ValidationError, match="payload size mismatch"):
        _chunk(frame_count=160, payload=b"\x00")


def test_audio_chunk_rejects_zero_frame_empty_payload() -> None:
    with pytest.raises(ValidationError):
        _chunk(frame_count=0, payload=b"")


def test_audio_chunk_rejects_text_payload_coercion() -> None:
    with pytest.raises(ValidationError):
        AudioChunk(
            source_id="fixture",
            stream_id="mic/main",
            seq=0,
            sample_index=0,
            capture_time_ns=0,
            frame_count=1,
            format=AudioFormat(sample_rate_hz=16_000, channels=1),
            payload="not-bytes",
        )


def test_audio_chunk_continuity_accepts_exact_next_chunk() -> None:
    previous = _chunk(seq=7, sample_index=1120, frame_count=160)
    current = _chunk(seq=8, sample_index=1280, frame_count=160)

    require_contiguous_audio_chunks(previous, current)
    previous.require_contiguous_next(current)


def test_audio_chunk_continuity_rejects_seq_gap() -> None:
    previous = _chunk(seq=7, sample_index=1120, frame_count=160)
    current = _chunk(seq=9, sample_index=1280, frame_count=160)

    with pytest.raises(AudioChunkContinuityError, match="seq discontinuity"):
        require_contiguous_audio_chunks(previous, current)


def test_audio_chunk_continuity_rejects_sample_index_gap() -> None:
    previous = _chunk(seq=7, sample_index=1120, frame_count=160)
    current = _chunk(seq=8, sample_index=1440, frame_count=160)

    with pytest.raises(AudioChunkContinuityError, match="sample_index discontinuity"):
        require_contiguous_audio_chunks(previous, current)


def test_audio_chunk_continuity_rejects_format_mismatch() -> None:
    previous = _chunk(
        seq=7,
        sample_index=1120,
        frame_count=160,
        audio_format=AudioFormat(sample_rate_hz=16_000, channels=1),
    )
    current = _chunk(
        seq=8,
        sample_index=1280,
        frame_count=160,
        audio_format=AudioFormat(sample_rate_hz=48_000, channels=1),
        payload=b"\x00" * 320,
    )

    with pytest.raises(AudioChunkContinuityError, match="format mismatch"):
        require_contiguous_audio_chunks(previous, current)
