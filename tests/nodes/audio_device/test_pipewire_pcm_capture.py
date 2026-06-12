from io import BytesIO

from fluent_audio.contracts import AudioFormat
from nodes.audio_device.pipewire_pcm_capture.main import (
    PipeWirePcmCaptureConfig,
    build_pw_record_command,
    iter_exact_chunks,
)


def _config() -> PipeWirePcmCaptureConfig:
    return PipeWirePcmCaptureConfig(
        target="alsa_input.usb-Anker_PowerConf_S3_A3321-DEV-SN1-01.mono-fallback",
        latency="20ms",
        audio_format=AudioFormat(
            sample_rate_hz=16_000,
            channels=1,
            sample_format="s16le",
            channel_layout="interleaved",
        ),
        chunk_frames=2,
        source_id="pipewire_pcm_capture",
        stream_id="audio/pipewire_pcm_capture/live",
        start_seq=5,
        start_sample_index=100,
        start_capture_time_ns=10_000,
        max_chunks=2,
        output_drain_seconds=0.0,
    )


def test_iter_exact_chunks_keeps_partial_tail() -> None:
    chunks = list(iter_exact_chunks(BytesIO(b"abcdefghi"), 4))

    assert chunks == [b"abcd", b"efgh", b"i"]


def test_pw_record_command_targets_named_source_as_raw_s16_capture() -> None:
    command = build_pw_record_command(_config())

    assert command == (
        "pw-record",
        "--target",
        "alsa_input.usb-Anker_PowerConf_S3_A3321-DEV-SN1-01.mono-fallback",
        "--latency",
        "20ms",
        "--format",
        "s16",
        "--rate",
        "16000",
        "--channels",
        "1",
        "-",
    )
