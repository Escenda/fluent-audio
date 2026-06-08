from pathlib import Path

import pytest
from pydantic import ValidationError

from fluent_audio.contracts import AudioChunk, AudioChunkContinuityError, AudioFormat
from fluent_audio.offline import (
    RawPcmChunkValidationError,
    RawPcmEmptyInputError,
    RawPcmFileNotFoundError,
    RawPcmFrameAlignmentError,
    RawPcmOutputError,
    RawPcmReadConfig,
    RawPcmWriteConfig,
    iter_raw_pcm_chunks,
    write_raw_pcm_chunks,
)
from nodes.io.sinks.raw_pcm_sink.main import main as sink_main
from nodes.io.sources.raw_pcm_source.main import main as source_main


def _audio_format(
    *,
    sample_rate_hz: int = 16_000,
    channels: int = 1,
    sample_format: str = "s16le",
) -> AudioFormat:
    return AudioFormat(
        sample_rate_hz=sample_rate_hz,
        channels=channels,
        sample_format=sample_format,
    )


def _read_config(
    path: Path,
    *,
    audio_format: AudioFormat | None = None,
    chunk_frames: int = 2,
    source_id: str = "offline_file",
    stream_id: str = "audio/offline",
    start_seq: int = 0,
    start_sample_index: int = 0,
) -> RawPcmReadConfig:
    return RawPcmReadConfig(
        path=path,
        audio_format=audio_format or _audio_format(),
        chunk_frames=chunk_frames,
        source_id=source_id,
        stream_id=stream_id,
        start_seq=start_seq,
        start_sample_index=start_sample_index,
    )


def _write_config(
    path: Path,
    *,
    audio_format: AudioFormat | None = None,
    source_id: str = "offline_file",
    stream_id: str = "audio/offline",
    overwrite: bool = False,
) -> RawPcmWriteConfig:
    return RawPcmWriteConfig(
        path=path,
        expected_format=audio_format or _audio_format(),
        source_id=source_id,
        stream_id=stream_id,
        overwrite=overwrite,
    )


def _chunk(
    *,
    seq: int,
    sample_index: int,
    frame_count: int = 2,
    audio_format: AudioFormat | None = None,
    source_id: str = "offline_file",
    stream_id: str = "audio/offline",
) -> AudioChunk:
    resolved_format = audio_format or _audio_format()
    return AudioChunk(
        source_id=source_id,
        stream_id=stream_id,
        seq=seq,
        sample_index=sample_index,
        capture_time_ns=(sample_index * 1_000_000_000) // resolved_format.sample_rate_hz,
        frame_count=frame_count,
        format=resolved_format,
        payload=b"\x00" * (frame_count * resolved_format.frame_size_bytes),
    )


def test_s16le_mono_source_emits_expected_timing_and_final_partial_chunk(tmp_path: Path) -> None:
    source_path = tmp_path / "input.s16le"
    source_path.write_bytes(b"abcdefghij")

    config = _read_config(
        source_path,
        audio_format=_audio_format(sample_rate_hz=1_000),
        chunk_frames=2,
        start_seq=10,
        start_sample_index=100,
    )
    chunks = list(iter_raw_pcm_chunks(config))

    assert [chunk.seq for chunk in chunks] == [10, 11, 12]
    assert [chunk.sample_index for chunk in chunks] == [100, 102, 104]
    assert [chunk.frame_count for chunk in chunks] == [2, 2, 1]
    assert [chunk.capture_time_ns for chunk in chunks] == [
        100_000_000,
        102_000_000,
        104_000_000,
    ]
    assert [chunk.payload for chunk in chunks] == [b"abcd", b"efgh", b"ij"]


def test_s16le_mono_roundtrip_byte_for_byte(tmp_path: Path) -> None:
    source_path = tmp_path / "input.s16le"
    output_path = tmp_path / "output.s16le"
    payload = b"abcdefghijkl"
    source_path.write_bytes(payload)

    chunks = iter_raw_pcm_chunks(_read_config(source_path, chunk_frames=2))
    summary = write_raw_pcm_chunks(_write_config(output_path), chunks)

    assert output_path.read_bytes() == payload
    assert summary.chunks_written == 3
    assert summary.frames_written == 6
    assert summary.bytes_written == len(payload)


def test_f32le_stereo_roundtrip_byte_for_byte(tmp_path: Path) -> None:
    source_path = tmp_path / "input.f32le"
    output_path = tmp_path / "output.f32le"
    payload = bytes(range(40))
    audio_format = _audio_format(sample_rate_hz=48_000, channels=2, sample_format="f32le")
    source_path.write_bytes(payload)

    chunks = iter_raw_pcm_chunks(
        _read_config(source_path, audio_format=audio_format, chunk_frames=3)
    )
    summary = write_raw_pcm_chunks(
        _write_config(output_path, audio_format=audio_format),
        chunks,
    )

    assert output_path.read_bytes() == payload
    assert summary.chunks_written == 2
    assert summary.frames_written == 5
    assert summary.bytes_written == len(payload)


def test_source_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(RawPcmFileNotFoundError):
        list(iter_raw_pcm_chunks(_read_config(tmp_path / "missing.s16le")))


def test_source_rejects_empty_file(tmp_path: Path) -> None:
    source_path = tmp_path / "empty.s16le"
    source_path.write_bytes(b"")

    with pytest.raises(RawPcmEmptyInputError):
        list(iter_raw_pcm_chunks(_read_config(source_path)))


def test_source_rejects_trailing_partial_frame_bytes(tmp_path: Path) -> None:
    source_path = tmp_path / "bad.s16le"
    source_path.write_bytes(b"abc")

    with pytest.raises(RawPcmFrameAlignmentError):
        list(iter_raw_pcm_chunks(_read_config(source_path)))


def test_source_rejects_invalid_chunk_size(tmp_path: Path) -> None:
    source_path = tmp_path / "input.s16le"
    source_path.write_bytes(b"abcd")

    with pytest.raises(ValidationError):
        RawPcmReadConfig(
            path=source_path,
            audio_format=_audio_format(),
            chunk_frames=0,
            source_id="offline_file",
            stream_id="audio/offline",
        )


def test_sink_rejects_overwrite_without_explicit_flag(tmp_path: Path) -> None:
    output_path = tmp_path / "output.s16le"
    output_path.write_bytes(b"existing")

    with pytest.raises(RawPcmOutputError):
        write_raw_pcm_chunks(_write_config(output_path), [_chunk(seq=0, sample_index=0)])


def test_sink_rejects_missing_parent_directory(tmp_path: Path) -> None:
    output_path = tmp_path / "missing" / "output.s16le"

    with pytest.raises(RawPcmOutputError):
        write_raw_pcm_chunks(_write_config(output_path), [_chunk(seq=0, sample_index=0)])


def test_sink_rejects_empty_chunk_stream(tmp_path: Path) -> None:
    output_path = tmp_path / "output.s16le"

    with pytest.raises(RawPcmEmptyInputError):
        write_raw_pcm_chunks(_write_config(output_path), [])

    assert not output_path.exists()


def test_sink_rejects_seq_gap(tmp_path: Path) -> None:
    output_path = tmp_path / "output.s16le"

    with pytest.raises(AudioChunkContinuityError, match="seq discontinuity"):
        write_raw_pcm_chunks(
            _write_config(output_path),
            [
                _chunk(seq=0, sample_index=0),
                _chunk(seq=2, sample_index=2),
            ],
        )


def test_sink_rejects_sample_index_gap(tmp_path: Path) -> None:
    output_path = tmp_path / "output.s16le"

    with pytest.raises(AudioChunkContinuityError, match="sample_index discontinuity"):
        write_raw_pcm_chunks(
            _write_config(output_path),
            [
                _chunk(seq=0, sample_index=0),
                _chunk(seq=1, sample_index=3),
            ],
        )


def test_sink_rejects_format_mismatch(tmp_path: Path) -> None:
    output_path = tmp_path / "output.s16le"

    with pytest.raises(RawPcmChunkValidationError, match="format mismatch"):
        write_raw_pcm_chunks(
            _write_config(output_path, audio_format=_audio_format(sample_rate_hz=48_000)),
            [_chunk(seq=0, sample_index=0)],
        )


def test_sink_rejects_source_id_mismatch(tmp_path: Path) -> None:
    output_path = tmp_path / "output.s16le"

    with pytest.raises(RawPcmChunkValidationError, match="source mismatch"):
        write_raw_pcm_chunks(
            _write_config(output_path, source_id="expected"),
            [_chunk(seq=0, sample_index=0, source_id="actual")],
        )


def test_sink_rejects_stream_id_mismatch(tmp_path: Path) -> None:
    output_path = tmp_path / "output.s16le"

    with pytest.raises(RawPcmChunkValidationError, match="stream mismatch"):
        write_raw_pcm_chunks(
            _write_config(output_path, stream_id="audio/expected"),
            [_chunk(seq=0, sample_index=0, stream_id="audio/actual")],
        )


def test_raw_pcm_source_and_sink_cli_smoke(tmp_path: Path) -> None:
    source_path = tmp_path / "input.s16le"
    chunks_jsonl_path = tmp_path / "chunks.jsonl"
    output_path = tmp_path / "output.s16le"
    payload = b"abcdefghijkl"
    source_path.write_bytes(payload)

    assert (
        source_main(
            [
                "--input",
                str(source_path),
                "--sample-rate-hz",
                "16000",
                "--channels",
                "1",
                "--sample-format",
                "s16le",
                "--chunk-frames",
                "2",
                "--source-id",
                "offline_file",
                "--stream-id",
                "audio/offline",
                "--chunks-jsonl",
                str(chunks_jsonl_path),
            ]
        )
        == 0
    )
    assert chunks_jsonl_path.exists()

    assert (
        sink_main(
            [
                "--chunks-jsonl",
                str(chunks_jsonl_path),
                "--output",
                str(output_path),
                "--sample-rate-hz",
                "16000",
                "--channels",
                "1",
                "--sample-format",
                "s16le",
                "--source-id",
                "offline_file",
                "--stream-id",
                "audio/offline",
            ]
        )
        == 0
    )
    assert output_path.read_bytes() == payload
