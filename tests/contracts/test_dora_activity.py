import pyarrow as pa
import pytest

from fluent_audio.contracts import AudioLevelEvent, VoiceActivityEvent
from fluent_audio.dora import (
    DoraAudioLevelMetadataError,
    DoraVoiceActivityFinalMarkerError,
    DoraVoiceActivityMetadataError,
    decode_audio_level_event_from_dora,
    decode_voice_activity_event_from_dora,
    encode_audio_level_event_for_dora,
    encode_voice_activity_event_for_dora,
    encode_voice_activity_final_marker_for_dora,
    validate_dora_audio_level_metadata,
    validate_dora_voice_activity_final_marker,
)
from fluent_audio_contracts.fluent_audio.v1.vad_pb2 import (
    AudioLevelEvent as PbAudioLevelEvent,
    VOICE_ACTIVITY_STATE_SPEECH,
    VoiceActivityEvent as PbVoiceActivityEvent,
)


def _activity_event() -> VoiceActivityEvent:
    return VoiceActivityEvent(
        source_id="fixture",
        stream_id="mic/main",
        seq=7,
        sample_index=1120,
        frame_count=160,
        state="speech",
        speech_probability=0.82,
    )


def test_voice_activity_event_dora_roundtrips_as_protobuf_payload() -> None:
    event = _activity_event()

    payload, metadata = encode_voice_activity_event_for_dora(event)
    decoded = decode_voice_activity_event_from_dora(payload, metadata.to_dora_metadata())
    proto = PbVoiceActivityEvent.FromString(bytes(payload.to_pylist()))

    assert payload.type == pa.uint8()
    assert proto.source_id == "fixture"
    assert metadata.final is False
    assert metadata.to_dora_metadata() == {
        "fluent_audio_codec": "protobuf",
        "fluent_audio_schema_version": "fluent_audio.v1",
        "fluent_audio_message_type": PbVoiceActivityEvent.DESCRIPTOR.full_name,
    }
    assert decoded == event


def test_audio_level_event_dora_roundtrips_as_protobuf_payload() -> None:
    event = AudioLevelEvent(
        source_id="vad",
        stream_id="activity/vad/level",
        seq=2,
        sample_index=4096,
        frame_count=512,
        rms_dbfs=-31.5,
        peak_dbfs=-12.25,
        speech_probability=0.44,
    )

    payload, metadata = encode_audio_level_event_for_dora(event)
    decoded = decode_audio_level_event_from_dora(payload, metadata.to_dora_metadata())
    proto = PbAudioLevelEvent.FromString(bytes(payload.to_pylist()))
    validated_metadata = validate_dora_audio_level_metadata(metadata.to_dora_metadata())

    assert payload.type == pa.uint8()
    assert proto.rms_dbfs == -31.5
    assert proto.peak_dbfs == -12.25
    assert metadata.final is False
    assert validated_metadata.message_type == PbAudioLevelEvent.DESCRIPTOR.full_name
    assert decoded == event


def test_voice_activity_final_marker_validates_and_is_not_an_event() -> None:
    payload, metadata = encode_voice_activity_final_marker_for_dora(
        source_id="fixture",
        stream_id="mic/main",
        seq=8,
        sample_index=1280,
    )

    final_marker = validate_dora_voice_activity_final_marker(
        payload,
        metadata.to_dora_metadata(),
    )

    assert metadata.final is True
    assert final_marker.source_id == "fixture"
    assert final_marker.stream_id == "mic/main"
    assert final_marker.seq == 8
    assert final_marker.sample_index == 1280
    with pytest.raises(DoraVoiceActivityFinalMarkerError):
        decode_voice_activity_event_from_dora(payload, metadata)


def test_voice_activity_dora_rejects_missing_transport_metadata() -> None:
    event = _activity_event()
    payload, metadata = encode_voice_activity_event_for_dora(event)
    missing_type_metadata = metadata.to_dora_metadata()
    del missing_type_metadata["fluent_audio_message_type"]

    with pytest.raises(DoraVoiceActivityMetadataError, match="metadata is invalid"):
        decode_voice_activity_event_from_dora(payload, None)
    with pytest.raises(DoraVoiceActivityMetadataError, match="metadata is invalid"):
        decode_voice_activity_event_from_dora(payload, missing_type_metadata)


def test_voice_activity_dora_rejects_invalid_payload() -> None:
    event = _activity_event()
    _, metadata = encode_voice_activity_event_for_dora(event)

    with pytest.raises(DoraVoiceActivityMetadataError, match="protobuf did not validate"):
        decode_voice_activity_event_from_dora(b"\x00", metadata)


def test_voice_activity_dora_rejects_invalid_state_from_proto_payload() -> None:
    event = _activity_event()
    _, metadata = encode_voice_activity_event_for_dora(event)
    invalid = PbVoiceActivityEvent(
        source_id=event.source_id,
        stream_id=event.stream_id,
        seq=event.seq,
        sample_index=event.sample_index,
        frame_count=event.frame_count,
        state=99,
        speech_probability=event.speech_probability,
    )

    with pytest.raises(DoraVoiceActivityMetadataError, match="protobuf did not validate"):
        decode_voice_activity_event_from_dora(invalid.SerializeToString(), metadata)


def test_voice_activity_dora_rejects_invalid_probability_from_proto_payload() -> None:
    event = _activity_event()
    _, metadata = encode_voice_activity_event_for_dora(event)
    invalid = PbVoiceActivityEvent(
        source_id=event.source_id,
        stream_id=event.stream_id,
        seq=event.seq,
        sample_index=event.sample_index,
        frame_count=event.frame_count,
        state=VOICE_ACTIVITY_STATE_SPEECH,
        speech_probability=1.01,
    )

    with pytest.raises(DoraVoiceActivityMetadataError, match="protobuf did not validate"):
        decode_voice_activity_event_from_dora(invalid.SerializeToString(), metadata)


def test_voice_activity_dora_rejects_message_type_mismatch() -> None:
    payload, metadata = encode_voice_activity_final_marker_for_dora(
        source_id="fixture",
        stream_id="mic/main",
        seq=8,
        sample_index=1280,
    )
    wrong_metadata = metadata.to_dora_metadata()
    wrong_metadata["fluent_audio_message_type"] = PbVoiceActivityEvent.DESCRIPTOR.full_name

    with pytest.raises(DoraVoiceActivityMetadataError, match="protobuf did not validate"):
        decode_voice_activity_event_from_dora(payload, wrong_metadata)


def test_audio_level_dora_rejects_activity_metadata() -> None:
    activity = _activity_event()
    payload, metadata = encode_voice_activity_event_for_dora(activity)

    with pytest.raises(DoraAudioLevelMetadataError, match="message type is invalid"):
        decode_audio_level_event_from_dora(payload, metadata)
