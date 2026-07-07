from pathlib import Path

import pytest
import pyarrow as pa
from pydantic import ValidationError

from fluent_dialogue_dora.contracts import AudioChunk, AudioChunkContinuityError, AudioFormat
from fluent_dialogue_dora.dora import (
    DoraAudioMetadataError,
    decode_audio_chunk_from_dora,
    encode_audio_chunk_for_dora,
    encode_audio_final_marker_for_dora,
    validate_dora_audio_final_marker,
    validate_dora_audio_metadata,
)
from fluent_dialogue_dora.offline import (
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
from nodes.audio_device.raw_pcm_sink.main import main as sink_main
from nodes.audio_device.raw_pcm_sink.main import write_raw_pcm_sink_dora
from nodes.audio_device.raw_pcm_source.main import main as source_main
from nodes.audio_device.raw_pcm_source.main import RawPcmReplayPacingConfig
from nodes.audio_device.raw_pcm_source.main import send_raw_pcm_source_dora


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
    start_capture_time_ns: int = 0,
) -> RawPcmReadConfig:
    return RawPcmReadConfig(
        path=path,
        audio_format=audio_format or _audio_format(),
        chunk_frames=chunk_frames,
        source_id=source_id,
        stream_id=stream_id,
        start_seq=start_seq,
        start_sample_index=start_sample_index,
        start_capture_time_ns=start_capture_time_ns,
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
    payload: bytes | None = None,
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
        payload=payload
        if payload is not None
        else b"\x00" * (frame_count * resolved_format.frame_size_bytes),
    )


class FakeDoraSourceNode:
    def __init__(self) -> None:
        self.sent = []

    def send_output(self, output_id, data, metadata=None) -> None:
        self.sent.append((output_id, data, metadata))


def _dora_input_event(chunk: AudioChunk):
    payload, metadata = encode_audio_chunk_for_dora(chunk)
    return {
        "type": "INPUT",
        "id": "audio",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _dora_final_event(
    *,
    seq: int,
    sample_index: int,
    capture_time_ns: int,
    audio_format: AudioFormat | None = None,
):
    payload, metadata = encode_audio_final_marker_for_dora(
        source_id="offline_file",
        stream_id="audio/offline",
        seq=seq,
        sample_index=sample_index,
        capture_time_ns=capture_time_ns,
        audio_format=audio_format or _audio_format(),
    )
    return {
        "type": "INPUT",
        "id": "audio",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def test_s16le_mono_source_emits_expected_timing_and_final_partial_chunk(tmp_path: Path) -> None:
    source_path = tmp_path / "input.s16le"
    source_path.write_bytes(b"abcdefghij")

    config = _read_config(
        source_path,
        audio_format=_audio_format(sample_rate_hz=1_000),
        chunk_frames=2,
        start_seq=10,
        start_sample_index=100,
        start_capture_time_ns=100_000_000,
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


def test_source_uses_explicit_start_capture_time_ns(tmp_path: Path) -> None:
    source_path = tmp_path / "input.s16le"
    source_path.write_bytes(b"abcdefgh")

    chunks = list(
        iter_raw_pcm_chunks(
            _read_config(
                source_path,
                audio_format=_audio_format(sample_rate_hz=1_000),
                chunk_frames=1,
                start_sample_index=100,
                start_capture_time_ns=7_000,
            )
        )
    )

    assert [chunk.capture_time_ns for chunk in chunks] == [
        7_000,
        1_007_000,
        2_007_000,
        3_007_000,
    ]


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
            start_capture_time_ns=0,
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


def test_sink_rejects_repeated_seq(tmp_path: Path) -> None:
    output_path = tmp_path / "output.s16le"

    with pytest.raises(AudioChunkContinuityError, match="seq discontinuity"):
        write_raw_pcm_chunks(
            _write_config(output_path),
            [
                _chunk(seq=0, sample_index=0),
                _chunk(seq=0, sample_index=2),
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
                "--channel-layout",
                "interleaved",
                "--chunk-frames",
                "2",
                "--source-id",
                "offline_file",
                "--stream-id",
                "audio/offline",
                "--start-capture-time-ns",
                "0",
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
                "--channel-layout",
                "interleaved",
                "--source-id",
                "offline_file",
                "--stream-id",
                "audio/offline",
            ]
        )
        == 0
    )
    assert output_path.read_bytes() == payload


def test_dora_audio_encode_decode_roundtrip() -> None:
    chunk = _chunk(seq=3, sample_index=6)

    payload, metadata = encode_audio_chunk_for_dora(chunk)
    decoded = decode_audio_chunk_from_dora(payload, metadata)

    assert payload.type == pa.uint8()
    assert decoded == chunk
    assert metadata.to_dora_metadata() == {
        "fluent_dialogue_dora_codec": "protobuf",
        "fluent_dialogue_dora_schema_version": "fluent_dialogue_dora.v1",
        "fluent_dialogue_dora_message_type": "fluent_dialogue_dora.v1.AudioFrame",
    }


def test_dora_audio_decode_ignores_transport_timestamp_metadata() -> None:
    chunk = _chunk(seq=3, sample_index=6)
    payload, metadata = encode_audio_chunk_for_dora(chunk)
    runtime_metadata = metadata.to_dora_metadata()
    runtime_metadata["timestamp"] = 1_718_000_000_000_000_000

    decoded = decode_audio_chunk_from_dora(payload, runtime_metadata)

    assert decoded == chunk


def test_dora_audio_decode_accepts_uint8_arrow_payload() -> None:
    chunk = _chunk(seq=3, sample_index=6)
    arrow_payload, metadata = encode_audio_chunk_for_dora(chunk)

    decoded = decode_audio_chunk_from_dora(arrow_payload, metadata)

    assert decoded == chunk


def test_dora_audio_decode_rejects_missing_metadata() -> None:
    with pytest.raises(DoraAudioMetadataError, match="metadata is invalid"):
        decode_audio_chunk_from_dora(b"\x00\x00", None)


def test_dora_audio_decode_rejects_invalid_metadata() -> None:
    with pytest.raises(DoraAudioMetadataError, match="metadata is invalid"):
        decode_audio_chunk_from_dora(
            b"\x00\x00",
            {
                "source_id": "offline_file",
                "stream_id": "audio/offline",
                "sample_index": 0,
                "capture_time_ns": 0,
                "frame_count": 1,
                "sample_rate_hz": 16_000,
                "channels": 1,
                "sample_format": "s16le",
                "channel_layout": "interleaved",
                "final": False,
            },
        )


def test_dora_audio_decode_rejects_old_flat_audio_metadata() -> None:
    with pytest.raises(DoraAudioMetadataError, match="metadata is invalid"):
        decode_audio_chunk_from_dora(
            b"\x00\x00",
            {
                "timestamp": 1_718_000_000_000_000_000,
                "source_id": "offline_file",
                "stream_id": "audio/offline",
                "sample_index": 0,
                "capture_time_ns": 0,
                "frame_count": 1,
                "sample_rate_hz": 16_000,
                "channels": 1,
                "sample_format": "s16le",
                "channel_layout": "interleaved",
                "final": False,
            },
        )


def test_raw_pcm_source_dora_send_uses_uint8_arrow_protobuf_payload_and_transport_metadata(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "input.s16le"
    source_path.write_bytes(b"abcdefgh")
    fake_node = FakeDoraSourceNode()

    chunks_sent = send_raw_pcm_source_dora(
        fake_node,
        _read_config(
            source_path,
            audio_format=_audio_format(sample_rate_hz=1_000),
            chunk_frames=2,
            start_capture_time_ns=50_000,
        ),
    )

    assert chunks_sent == 2
    assert len(fake_node.sent) == 3
    assert [sent[0] for sent in fake_node.sent] == ["audio", "audio", "audio"]
    decoded_chunks = [
        decode_audio_chunk_from_dora(payload, validate_dora_audio_metadata(metadata))
        for _output_id, payload, metadata in fake_node.sent[:2]
    ]
    final_marker = validate_dora_audio_final_marker(
        fake_node.sent[-1][1],
        fake_node.sent[-1][2],
    )

    assert [chunk.payload for chunk in decoded_chunks] == [b"abcd", b"efgh"]
    assert [chunk.seq for chunk in decoded_chunks] == [0, 1]
    assert final_marker.seq == 2
    assert final_marker.sample_index == 4
    assert final_marker.capture_time_ns == 4_050_000

    for _, payload, metadata in fake_node.sent:
        assert isinstance(payload, pa.UInt8Array)
        for value in metadata.values():
            assert isinstance(value, bool | int | float | str | list)
            assert not isinstance(value, dict)


def test_raw_pcm_source_dora_replay_pacing_sleeps_after_each_chunk(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "input.s16le"
    source_path.write_bytes(b"abcdefgh")
    fake_node = FakeDoraSourceNode()
    sleep_durations = []

    chunks_sent = send_raw_pcm_source_dora(
        fake_node,
        _read_config(
            source_path,
            audio_format=_audio_format(sample_rate_hz=1_000),
            chunk_frames=2,
            start_capture_time_ns=0,
        ),
        pacing_config=RawPcmReplayPacingConfig(replay_speed=2.0),
        sleep=sleep_durations.append,
    )

    assert chunks_sent == 2
    assert sleep_durations == [0.001, 0.001]
    assert validate_dora_audio_metadata(fake_node.sent[-1][2]).final is True


def test_raw_pcm_sink_dora_receive_writes_byte_identical_output(tmp_path: Path) -> None:
    output_path = tmp_path / "output.s16le"
    first = _chunk(seq=0, sample_index=0, payload=b"abcd")
    second = _chunk(seq=1, sample_index=2, payload=b"efgh")

    summary = write_raw_pcm_sink_dora(
        [
            _dora_input_event(first),
            _dora_input_event(second),
            _dora_final_event(seq=2, sample_index=4, capture_time_ns=250_000),
        ],
        _write_config(output_path),
    )

    assert output_path.read_bytes() == b"abcdefgh"
    assert summary.chunks_written == 2
    assert summary.bytes_written == 8


def test_raw_pcm_sink_dora_input_closed_finishes_stream(tmp_path: Path) -> None:
    output_path = tmp_path / "output.s16le"
    first = _chunk(seq=0, sample_index=0, payload=b"abcd")
    second = _chunk(seq=1, sample_index=2, payload=b"efgh")

    summary = write_raw_pcm_sink_dora(
        [
            _dora_input_event(first),
            _dora_input_event(second),
            {"type": "INPUT_CLOSED", "id": "audio"},
        ],
        _write_config(output_path),
    )

    assert output_path.read_bytes() == b"abcdefgh"
    assert summary.chunks_written == 2
    assert summary.bytes_written == 8
