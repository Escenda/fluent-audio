from fluent_dialogue_dora_contracts.fluent_dialogue_dora.v1.asr_pb2 import AsrControl, AsrStart
from fluent_dialogue_dora_contracts.fluent_dialogue_dora.v1.audio_pb2 import (
    CHANNEL_LAYOUT_INTERLEAVED,
    SAMPLE_FORMAT_S16LE,
    AudioFormat,
    AudioFrame,
)
from fluent_dialogue_dora_contracts.fluent_dialogue_dora.v1.tts_pb2 import SynthesizedAudioChunk


def test_generated_audio_frame_imports_and_serializes() -> None:
    audio_format = AudioFormat(
        sample_rate_hz=16_000,
        channels=1,
        sample_format=SAMPLE_FORMAT_S16LE,
        channel_layout=CHANNEL_LAYOUT_INTERLEAVED,
    )
    frame = AudioFrame(
        source_id="fixture",
        stream_id="mic/main",
        seq=1,
        sample_index=160,
        capture_time_ns=1_000,
        frame_count=2,
        format=audio_format,
        payload=b"\x00\x00\x00\x00",
    )

    decoded = AudioFrame.FromString(frame.SerializeToString())

    assert decoded == frame
    assert decoded.format.sample_rate_hz == 16_000


def test_generated_cross_file_import_uses_package_prefix() -> None:
    chunk = SynthesizedAudioChunk(
        request_id="tts-1",
        session_id="session-1",
        user_turn_id="user-turn-1",
        assistant_turn_id="assistant-turn-1",
        seq=0,
        audio=AudioFrame(
            source_id="tts",
            stream_id="speaker/main",
            seq=0,
            sample_index=0,
            capture_time_ns=1_000,
            frame_count=1,
            format=AudioFormat(
                sample_rate_hz=48_000,
                channels=1,
                sample_format=SAMPLE_FORMAT_S16LE,
                channel_layout=CHANNEL_LAYOUT_INTERLEAVED,
            ),
            payload=b"\x00\x00",
        ),
    )

    assert chunk.audio.stream_id == "speaker/main"


def test_generated_oneof_control_shape() -> None:
    control = AsrControl(
        start=AsrStart(
            session_id="session-1",
            user_turn_id="user-turn-1",
            stream_id="mic/main",
            seq=1,
            start_sample_index=320,
        )
    )

    assert control.WhichOneof("control") == "start"
