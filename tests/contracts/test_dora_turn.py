import pyarrow as pa
import pytest
from pydantic import ValidationError

from fluent_audio.contracts import TurnEvent
from fluent_audio.dora import (
    DoraTurnFinalMarkerError,
    DoraTurnMetadata,
    DoraTurnMetadataError,
    decode_turn_event_from_dora,
    encode_turn_event_for_dora,
    encode_turn_final_marker_for_dora,
    validate_dora_turn_final_marker,
    validate_dora_turn_metadata,
)


def _turn_event(confidence: float | None = 0.75) -> TurnEvent:
    return TurnEvent(
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="mic/main",
        seq=7,
        sample_index=1120,
        state="started",
        confidence=confidence,
    )


def test_turn_event_dora_roundtrips_from_flat_metadata() -> None:
    event = _turn_event()

    payload, metadata = encode_turn_event_for_dora(event)
    decoded = decode_turn_event_from_dora(payload, metadata.to_dora_metadata())

    assert payload.type == pa.uint8()
    assert payload.to_pylist() == []
    assert metadata.final is False
    assert metadata.to_dora_metadata() == {
        "session_id": "session-1",
        "user_turn_id": "user-turn-1",
        "stream_id": "mic/main",
        "seq": 7,
        "sample_index": 1120,
        "state": "started",
        "confidence_present": True,
        "confidence": 0.75,
        "final": False,
    }
    assert decoded == event


def test_turn_event_dora_preserves_absent_confidence_explicitly() -> None:
    event = _turn_event(confidence=None)

    payload, metadata = encode_turn_event_for_dora(event)
    decoded = decode_turn_event_from_dora(payload, metadata.to_dora_metadata())

    assert metadata.confidence_present is False
    assert metadata.confidence == 0.0
    assert metadata.to_dora_metadata()["confidence_present"] is False
    assert metadata.to_dora_metadata()["confidence"] == 0.0
    assert decoded == event


def test_turn_final_marker_validates_and_is_not_an_event() -> None:
    payload, metadata = encode_turn_final_marker_for_dora(
        "session-1",
        "mic/main",
        8,
        1280,
    )

    final_marker = validate_dora_turn_final_marker(
        payload,
        metadata.to_dora_metadata(),
    )

    assert final_marker.final is True
    assert final_marker.user_turn_id == ""
    assert final_marker.state == "idle"
    assert final_marker.confidence_present is False
    assert final_marker.confidence == 0.0
    with pytest.raises(DoraTurnFinalMarkerError):
        decode_turn_event_from_dora(payload, metadata)


def test_turn_dora_rejects_missing_metadata() -> None:
    event = _turn_event()
    payload, metadata = encode_turn_event_for_dora(event)
    missing_state_metadata = {
        "session_id": metadata.session_id,
        "user_turn_id": metadata.user_turn_id,
        "stream_id": metadata.stream_id,
        "seq": metadata.seq,
        "sample_index": metadata.sample_index,
        "confidence_present": metadata.confidence_present,
        "confidence": metadata.confidence,
        "final": metadata.final,
    }

    with pytest.raises(DoraTurnMetadataError, match="metadata is required"):
        decode_turn_event_from_dora(payload, None)
    with pytest.raises(DoraTurnMetadataError, match="missing required keys: state"):
        decode_turn_event_from_dora(payload, missing_state_metadata)


def test_turn_dora_rejects_invalid_payload() -> None:
    event = _turn_event()
    _, metadata = encode_turn_event_for_dora(event)

    with pytest.raises(DoraTurnMetadataError, match="payload must be empty"):
        decode_turn_event_from_dora(b"\x00", metadata)


def test_turn_dora_rejects_invalid_state_with_pydantic_validation() -> None:
    event = _turn_event()
    _, metadata = encode_turn_event_for_dora(event)
    invalid_state_metadata = metadata.to_dora_metadata()
    invalid_state_metadata["state"] = "interrupted"

    with pytest.raises(DoraTurnMetadataError) as exc_info:
        validate_dora_turn_metadata(invalid_state_metadata)

    assert isinstance(exc_info.value.__cause__, ValidationError)


def test_turn_dora_rejects_invalid_confidence_with_pydantic_validation() -> None:
    event = _turn_event()
    _, metadata = encode_turn_event_for_dora(event)
    invalid_confidence_metadata = metadata.to_dora_metadata()
    invalid_confidence_metadata["confidence"] = 1.01

    with pytest.raises(DoraTurnMetadataError) as exc_info:
        validate_dora_turn_metadata(invalid_confidence_metadata)

    assert isinstance(exc_info.value.__cause__, ValidationError)


def test_turn_dora_rejects_absent_confidence_with_nonzero_value() -> None:
    event = _turn_event(confidence=None)
    _, metadata = encode_turn_event_for_dora(event)
    invalid_confidence_metadata = metadata.to_dora_metadata()
    invalid_confidence_metadata["confidence"] = 0.5

    with pytest.raises(DoraTurnMetadataError) as exc_info:
        validate_dora_turn_metadata(invalid_confidence_metadata)

    assert isinstance(exc_info.value.__cause__, ValidationError)


def test_turn_dora_metadata_rejects_invalid_final_marker_shape() -> None:
    with pytest.raises(ValidationError):
        DoraTurnMetadata(
            session_id="session-1",
            user_turn_id="user-turn-1",
            stream_id="mic/main",
            seq=8,
            sample_index=1280,
            state="idle",
            confidence_present=False,
            confidence=0.0,
            final=True,
        )
