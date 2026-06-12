import pyarrow as pa
import pytest

from fluent_audio.contracts import TurnEvent
from fluent_audio.dora import (
    DoraTurnFinalMarkerError,
    DoraTurnMetadataError,
    decode_turn_event_from_dora,
    encode_turn_event_for_dora,
    encode_turn_final_marker_for_dora,
    validate_dora_turn_final_marker,
)
from fluent_audio_contracts.fluent_audio.v1.vad_pb2 import (
    TURN_STATE_STARTED,
    TurnEvent as PbTurnEvent,
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


def test_turn_event_dora_roundtrips_as_protobuf_payload() -> None:
    event = _turn_event()

    payload, metadata = encode_turn_event_for_dora(event)
    decoded = decode_turn_event_from_dora(payload, metadata.to_dora_metadata())
    proto = PbTurnEvent.FromString(bytes(payload.to_pylist()))

    assert payload.type == pa.uint8()
    assert proto.session_id == "session-1"
    assert metadata.final is False
    assert metadata.to_dora_metadata() == {
        "fluent_audio_codec": "protobuf",
        "fluent_audio_schema_version": "fluent_audio.v1",
        "fluent_audio_message_type": PbTurnEvent.DESCRIPTOR.full_name,
    }
    assert decoded == event


def test_turn_event_dora_preserves_absent_confidence_in_proto_payload() -> None:
    event = _turn_event(confidence=None)

    payload, metadata = encode_turn_event_for_dora(event)
    decoded = decode_turn_event_from_dora(payload, metadata.to_dora_metadata())
    proto = PbTurnEvent.FromString(bytes(payload.to_pylist()))

    assert proto.HasField("confidence") is False
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

    assert metadata.final is True
    assert final_marker.session_id == "session-1"
    assert final_marker.stream_id == "mic/main"
    assert final_marker.seq == 8
    assert final_marker.sample_index == 1280
    with pytest.raises(DoraTurnFinalMarkerError):
        decode_turn_event_from_dora(payload, metadata)


def test_turn_dora_rejects_missing_transport_metadata() -> None:
    event = _turn_event()
    payload, metadata = encode_turn_event_for_dora(event)
    missing_type_metadata = metadata.to_dora_metadata()
    del missing_type_metadata["fluent_audio_message_type"]

    with pytest.raises(DoraTurnMetadataError, match="metadata is invalid"):
        decode_turn_event_from_dora(payload, None)
    with pytest.raises(DoraTurnMetadataError, match="metadata is invalid"):
        decode_turn_event_from_dora(payload, missing_type_metadata)


def test_turn_dora_rejects_invalid_payload() -> None:
    event = _turn_event()
    _, metadata = encode_turn_event_for_dora(event)

    with pytest.raises(DoraTurnMetadataError, match="protobuf did not validate"):
        decode_turn_event_from_dora(b"\x00", metadata)


def test_turn_dora_rejects_invalid_state_from_proto_payload() -> None:
    event = _turn_event()
    _, metadata = encode_turn_event_for_dora(event)
    invalid = PbTurnEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        stream_id=event.stream_id,
        seq=event.seq,
        sample_index=event.sample_index,
        state=99,
        confidence=event.confidence,
    )

    with pytest.raises(DoraTurnMetadataError, match="protobuf did not validate"):
        decode_turn_event_from_dora(invalid.SerializeToString(), metadata)


def test_turn_dora_rejects_invalid_confidence_from_proto_payload() -> None:
    event = _turn_event()
    _, metadata = encode_turn_event_for_dora(event)
    invalid = PbTurnEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        stream_id=event.stream_id,
        seq=event.seq,
        sample_index=event.sample_index,
        state=TURN_STATE_STARTED,
        confidence=1.01,
    )

    with pytest.raises(DoraTurnMetadataError, match="protobuf did not validate"):
        decode_turn_event_from_dora(invalid.SerializeToString(), metadata)
