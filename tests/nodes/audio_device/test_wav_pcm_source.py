from pathlib import Path
import wave

import pytest

from fluent_dialogue_dora.dora import validate_dora_audio_final_marker
from fluent_dialogue_dora.offline import (
    WavPcmEmptyInputError,
    WavPcmReadConfig,
    WavPcmUnsupportedFormatError,
    iter_wav_pcm_chunks,
)
from nodes.audio_device.wav_pcm_source.main import WavPcmReplayPacingConfig
from nodes.audio_device.wav_pcm_source.main import send_wav_pcm_source_dora


class FakeDoraSourceNode:
    def __init__(self) -> None:
        self.sent = []

    def send_output(self, output_id, data, metadata=None) -> None:
        self.sent.append((output_id, data, metadata))


def _write_wav(path: Path, payload: bytes, *, sample_rate_hz: int = 16000) -> None:
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate_hz)
        wav_file.writeframes(payload)


def _config(path: Path, *, chunk_frames: int = 2) -> WavPcmReadConfig:
    return WavPcmReadConfig(
        path=path,
        chunk_frames=chunk_frames,
        source_id="wav_fixture",
        stream_id="audio/file/wav",
        start_seq=5,
        start_sample_index=10,
        start_capture_time_ns=1000,
        expected_sample_rate_hz=16000,
        expected_channels=1,
    )


def test_wav_source_emits_timed_chunks(tmp_path: Path) -> None:
    wav_path = tmp_path / "input.wav"
    _write_wav(wav_path, b"abcdefghijkl")

    chunks = tuple(iter_wav_pcm_chunks(_config(wav_path)))

    assert [chunk.seq for chunk in chunks] == [5, 6, 7]
    assert [chunk.sample_index for chunk in chunks] == [10, 12, 14]
    assert [chunk.frame_count for chunk in chunks] == [2, 2, 2]
    assert [chunk.capture_time_ns for chunk in chunks] == [1000, 126000, 251000]
    assert chunks[0].format.sample_rate_hz == 16000
    assert chunks[0].format.sample_format == "s16le"


def test_wav_source_rejects_expected_sample_rate_mismatch(tmp_path: Path) -> None:
    wav_path = tmp_path / "input.wav"
    _write_wav(wav_path, b"abcd", sample_rate_hz=8000)

    with pytest.raises(WavPcmUnsupportedFormatError):
        tuple(iter_wav_pcm_chunks(_config(wav_path)))


def test_wav_source_rejects_empty_wav(tmp_path: Path) -> None:
    wav_path = tmp_path / "empty.wav"
    _write_wav(wav_path, b"")

    with pytest.raises(WavPcmEmptyInputError):
        tuple(iter_wav_pcm_chunks(_config(wav_path)))


def test_wav_dora_source_emits_final_marker_and_replay_sleep(tmp_path: Path) -> None:
    wav_path = tmp_path / "input.wav"
    _write_wav(wav_path, b"abcdefgh")
    node = FakeDoraSourceNode()
    sleep_calls: list[float] = []

    sent = send_wav_pcm_source_dora(
        node,
        _config(wav_path, chunk_frames=2),
        pacing_config=WavPcmReplayPacingConfig(replay_speed=2.0),
        sleep=sleep_calls.append,
    )

    assert sent == 2
    assert [item[0] for item in node.sent] == ["audio", "audio", "audio"]
    assert sleep_calls == [0.0000625, 0.0000625]
    final_payload = node.sent[-1][1]
    final_metadata = node.sent[-1][2]
    final_marker = validate_dora_audio_final_marker(final_payload, final_metadata)
    assert final_marker.seq == 7
