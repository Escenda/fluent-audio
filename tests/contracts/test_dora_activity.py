import pyarrow as pa
import pytest
from pydantic import ValidationError

from fluent_audio.contracts import VoiceActivityEvent
from fluent_audio.dora import (
    DoraVoiceActivityFinalMarkerError,
    DoraVoiceActivityMetadata,
    DoraVoiceActivityMetadataError,
    decode_voice_activity_event_from_dora,
    encode_voice_activity_event_for_dora,
    encode_voice_activity_final_marker_for_dora,
    validate_dora_voice_activity_final_marker,
    validate_dora_voice_activity_metadata,
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


def test_voice_activity_event_dora_roundtrips_from_flat_metadata() -> None:
    event = _activity_event()

    payload, metadata = encode_voice_activity_event_for_dora(event)
    decoded = decode_voice_activity_event_from_dora(payload, metadata.to_dora_metadata())

    assert payload.type == pa.uint8()
    assert payload.to_pylist() == []
    assert metadata.final is False
    assert metadata.to_dora_metadata() == {
        "source_id": "fixture",
        "stream_id": "mic/main",
        "seq": 7,
        "sample_index": 1120,
        "frame_count": 160,
        "state": "speech",
        "speech_probability": 0.82,
        "final": False,
    }
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

    assert final_marker.final is True
    assert final_marker.frame_count == 0
    assert final_marker.state == "silence"
    assert final_marker.speech_probability == 0.0
    with pytest.raises(DoraVoiceActivityFinalMarkerError):
        decode_voice_activity_event_from_dora(payload, metadata)


def test_voice_activity_dora_rejects_missing_metadata() -> None:
    event = _activity_event()
    payload, metadata = encode_voice_activity_event_for_dora(event)
    missing_state_metadata = {
        "source_id": metadata.source_id,
        "stream_id": metadata.stream_id,
        "seq": metadata.seq,
        "sample_index": metadata.sample_index,
        "frame_count": metadata.frame_count,
        "speech_probability": metadata.speech_probability,
        "final": metadata.final,
    }

    with pytest.raises(DoraVoiceActivityMetadataError, match="metadata is required"):
        decode_voice_activity_event_from_dora(payload, None)
    with pytest.raises(DoraVoiceActivityMetadataError, match="missing required keys: state"):
        decode_voice_activity_event_from_dora(payload, missing_state_metadata)


def test_voice_activity_dora_rejects_invalid_payload() -> None:
    event = _activity_event()
    _, metadata = encode_voice_activity_event_for_dora(event)

    with pytest.raises(DoraVoiceActivityMetadataError, match="payload must be empty"):
        decode_voice_activity_event_from_dora(b"\x00", metadata)


def test_voice_activity_dora_rejects_invalid_state_with_pydantic_validation() -> None:
    event = _activity_event()
    _, metadata = encode_voice_activity_event_for_dora(event)
    invalid_state_metadata = metadata.to_dora_metadata()
    invalid_state_metadata["state"] = "noise"

    with pytest.raises(DoraVoiceActivityMetadataError) as exc_info:
        validate_dora_voice_activity_metadata(invalid_state_metadata)

    assert isinstance(exc_info.value.__cause__, ValidationError)


def test_voice_activity_dora_rejects_invalid_probability_with_pydantic_validation() -> None:
    event = _activity_event()
    _, metadata = encode_voice_activity_event_for_dora(event)
    invalid_probability_metadata = metadata.to_dora_metadata()
    invalid_probability_metadata["speech_probability"] = 1.01

    with pytest.raises(DoraVoiceActivityMetadataError) as exc_info:
        validate_dora_voice_activity_metadata(invalid_probability_metadata)

    assert isinstance(exc_info.value.__cause__, ValidationError)


def test_voice_activity_dora_metadata_rejects_invalid_final_marker_shape() -> None:
    with pytest.raises(ValidationError):
        DoraVoiceActivityMetadata(
            source_id="fixture",
            stream_id="mic/main",
            seq=8,
            sample_index=1280,
            frame_count=160,
            state="silence",
            speech_probability=0.0,
            final=True,
        )
