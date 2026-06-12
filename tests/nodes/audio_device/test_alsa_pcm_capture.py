from io import BytesIO

from fluent_audio.contracts import AudioFormat
from nodes.audio_device.alsa_pcm_capture.main import (
    AlsaPcmCaptureConfig,
    build_arecord_command,
    iter_exact_chunks,
)


def _config() -> AlsaPcmCaptureConfig:
    return AlsaPcmCaptureConfig(
        device="pipewire",
        audio_format=AudioFormat(
            sample_rate_hz=16_000,
            channels=1,
            sample_format="s16le",
            channel_layout="interleaved",
        ),
        chunk_frames=2,
        source_id="alsa_pcm_capture",
        stream_id="audio/alsa_pcm_capture/live",
        start_seq=5,
        start_sample_index=100,
        start_capture_time_ns=10_000,
        max_chunks=2,
        output_drain_seconds=0.0,
    )


def test_iter_exact_chunks_keeps_partial_tail() -> None:
    chunks = list(iter_exact_chunks(BytesIO(b"abcdefghi"), 4))

    assert chunks == [b"abcd", b"efgh", b"i"]


def test_arecord_command_is_explicit_raw_s16le_capture() -> None:
    command = build_arecord_command(_config())

    assert command == (
        "arecord",
        "-q",
        "-D",
        "pipewire",
        "-f",
        "S16_LE",
        "-c",
        "1",
        "-r",
        "16000",
        "-t",
        "raw",
        "-",
    )
