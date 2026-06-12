import pyarrow as pa
import pytest

from fluent_audio.contracts import (
    AudioChunk,
    AudioFormat,
    SynthesizedAudioChunk,
    TtsTextChunk,
    TtsTextStreamFinal,
)
from fluent_audio.dora import (
    DoraSynthesizedAudioFinalMarkerError,
    DoraSynthesisMetadataError,
    DoraTtsTextStreamFinalMarkerError,
    decode_synthesized_audio_chunk_from_dora,
    decode_tts_text_chunk_from_dora,
    encode_synthesized_audio_chunk_for_dora,
    encode_synthesized_audio_final_marker_for_dora,
    encode_tts_text_chunk_for_dora,
    encode_tts_text_stream_final_marker_for_dora,
    validate_dora_synthesized_audio_final_marker,
    validate_dora_tts_text_stream_final_marker,
)


def test_tts_text_chunk_roundtrips_through_dora() -> None:
    chunk = TtsTextChunk(
        request_id="tts-1",
        session_id="session-1",
        user_turn_id="user-turn-1",
        assistant_turn_id="assistant-turn-1",
        seq=2,
        text="こんにちは",
        is_final=False,
    )

    payload, metadata = encode_tts_text_chunk_for_dora(chunk)
    decoded = decode_tts_text_chunk_from_dora(payload, metadata.to_dora_metadata())

    assert decoded == chunk
    assert metadata.kind == "chunk"


def test_tts_text_stream_final_marker_roundtrips_through_dora() -> None:
    marker = TtsTextStreamFinal(
        session_id="session-1",
        user_turn_id="user-turn-1",
        assistant_turn_id="assistant-turn-1",
        seq=3,
    )

    payload, metadata = encode_tts_text_stream_final_marker_for_dora(marker)
    decoded = validate_dora_tts_text_stream_final_marker(payload, metadata.to_dora_metadata())

    assert decoded == marker
    assert metadata.kind == "stream_final"
    with pytest.raises(DoraTtsTextStreamFinalMarkerError, match="stream final marker"):
        decode_tts_text_chunk_from_dora(payload, metadata)


def test_tts_text_rejects_invalid_payload() -> None:
    chunk = TtsTextChunk(
        request_id="tts-1",
        session_id="session-1",
        user_turn_id="user-turn-1",
        assistant_turn_id="assistant-turn-1",
        seq=2,
        text="hello",
        is_final=True,
    )
    _, metadata = encode_tts_text_chunk_for_dora(chunk)

    with pytest.raises(DoraSynthesisMetadataError, match="protobuf did not validate"):
        decode_tts_text_chunk_from_dora(pa.array([255], type=pa.uint8()), metadata)


def test_tts_text_stream_final_rejects_invalid_payload() -> None:
    marker = TtsTextStreamFinal(
        session_id="session-1",
        user_turn_id="user-turn-1",
        assistant_turn_id="assistant-turn-1",
        seq=3,
    )
    _, metadata = encode_tts_text_stream_final_marker_for_dora(marker)

    with pytest.raises(DoraSynthesisMetadataError, match="protobuf did not validate"):
        validate_dora_tts_text_stream_final_marker(b"not-empty", metadata)


def test_synthesized_audio_chunk_roundtrips_through_dora() -> None:
    audio = AudioChunk(
        source_id="tts",
        stream_id="audio/tts",
        seq=4,
        sample_index=1024,
        capture_time_ns=64_000_000,
        frame_count=4,
        format=AudioFormat(sample_rate_hz=16_000, channels=1, sample_format="s16le"),
        payload=b"\x01\x00\x02\x00\x03\x00\x04\x00",
    )
    chunk = SynthesizedAudioChunk(
        request_id="tts-1",
        session_id="session-1",
        user_turn_id="user-turn-1",
        assistant_turn_id="assistant-turn-1",
        seq=3,
        audio=audio,
    )

    payload, metadata = encode_synthesized_audio_chunk_for_dora(chunk)
    decoded = decode_synthesized_audio_chunk_from_dora(payload, metadata.to_dora_metadata())

    assert decoded == chunk


def test_synthesized_audio_final_marker_is_not_decoded_as_chunk() -> None:
    payload, metadata = encode_synthesized_audio_final_marker_for_dora(
        request_id="tts-1",
        session_id="session-1",
        user_turn_id="user-turn-1",
        assistant_turn_id="assistant-turn-1",
        seq=4,
        audio_source_id="tts",
        audio_stream_id="audio/tts",
        audio_seq=5,
        audio_sample_index=2048,
        audio_capture_time_ns=128_000_000,
        audio_format=AudioFormat(sample_rate_hz=16_000, channels=1, sample_format="s16le"),
    )

    final_marker = validate_dora_synthesized_audio_final_marker(payload, metadata.to_dora_metadata())

    assert metadata.final is True
    assert final_marker.audio_seq == 5
    assert final_marker.audio_sample_index == 2048
    with pytest.raises(DoraSynthesizedAudioFinalMarkerError, match="final marker"):
        decode_synthesized_audio_chunk_from_dora(payload, metadata)


def test_synthesized_audio_rejects_payload_size_mismatch() -> None:
    audio = AudioChunk(
        source_id="tts",
        stream_id="audio/tts",
        seq=4,
        sample_index=1024,
        capture_time_ns=64_000_000,
        frame_count=4,
        format=AudioFormat(sample_rate_hz=16_000, channels=1, sample_format="s16le"),
        payload=b"\x01\x00\x02\x00\x03\x00\x04\x00",
    )
    chunk = SynthesizedAudioChunk(
        request_id="tts-1",
        session_id="session-1",
        user_turn_id="user-turn-1",
        assistant_turn_id="assistant-turn-1",
        seq=3,
        audio=audio,
    )
    _, metadata = encode_synthesized_audio_chunk_for_dora(chunk)

    with pytest.raises(DoraSynthesisMetadataError, match="SynthesizedAudioChunk"):
        decode_synthesized_audio_chunk_from_dora(b"\x00\x00", metadata)
