import pyarrow as pa
import pytest

from fluent_audio.contracts import AsrCancel, AsrStart, AsrStop
from fluent_audio.dora import (
    DoraAsrControlFinalMarkerError,
    DoraAsrControlMetadataError,
    decode_asr_control_from_dora,
    encode_asr_control_final_marker_for_dora,
    encode_asr_control_for_dora,
    validate_dora_asr_control_final_marker,
    validate_dora_asr_control_metadata,
)
from fluent_audio_contracts.fluent_audio.v1.asr_pb2 import (
    AsrControl,
    AsrControlStreamFinal,
)


def test_asr_start_roundtrips_through_dora_boundary() -> None:
    start = AsrStart(
        action="start",
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="asr/main",
        seq=0,
        start_sample_index=320,
    )

    payload, metadata = encode_asr_control_for_dora(start)
    decoded = decode_asr_control_from_dora(payload, metadata)
    proto = AsrControl.FromString(bytes(payload.to_pylist()))

    assert isinstance(decoded, AsrStart)
    assert decoded == start
    assert proto.WhichOneof("control") == "start"
    assert proto.start.start_sample_index == 320
    assert metadata.final is False
    assert metadata.to_dora_metadata() == {
        "fluent_audio_codec": "protobuf",
        "fluent_audio_schema_version": "fluent_audio.v1",
        "fluent_audio_message_type": AsrControl.DESCRIPTOR.full_name,
    }


def test_asr_stop_roundtrips_through_dora_boundary() -> None:
    stop = AsrStop(
        action="stop",
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="asr/main",
        seq=1,
        stop_sample_index=3200,
    )

    payload, metadata = encode_asr_control_for_dora(stop)
    decoded = decode_asr_control_from_dora(payload, metadata)
    proto = AsrControl.FromString(bytes(payload.to_pylist()))

    assert isinstance(decoded, AsrStop)
    assert decoded == stop
    assert proto.WhichOneof("control") == "stop"
    assert proto.stop.stop_sample_index == 3200


def test_asr_cancel_roundtrips_through_dora_boundary() -> None:
    cancel = AsrCancel(
        action="cancel",
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="asr/main",
        seq=2,
        reason="barge-in",
    )

    payload, metadata = encode_asr_control_for_dora(cancel)
    decoded = decode_asr_control_from_dora(payload, metadata)
    proto = AsrControl.FromString(bytes(payload.to_pylist()))

    assert isinstance(decoded, AsrCancel)
    assert decoded == cancel
    assert proto.WhichOneof("control") == "cancel"
    assert proto.cancel.reason == "barge-in"


def test_asr_control_rejects_invalid_payload() -> None:
    start = AsrStart(
        action="start",
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="asr/main",
        seq=0,
        start_sample_index=320,
    )
    _, metadata = encode_asr_control_for_dora(start)

    with pytest.raises(DoraAsrControlMetadataError, match="protobuf did not validate"):
        decode_asr_control_from_dora(pa.array([1], type=pa.uint8()), metadata)


def test_asr_control_rejects_missing_oneof_control() -> None:
    start = AsrStart(
        action="start",
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="asr/main",
        seq=0,
        start_sample_index=320,
    )
    _, metadata = encode_asr_control_for_dora(start)

    with pytest.raises(DoraAsrControlMetadataError, match="missing oneof control"):
        decode_asr_control_from_dora(AsrControl().SerializeToString(), metadata)


def test_asr_control_rejects_missing_transport_metadata() -> None:
    with pytest.raises(DoraAsrControlMetadataError, match="metadata is invalid"):
        validate_dora_asr_control_metadata({"fluent_audio_codec": "protobuf"})


def test_asr_control_metadata_model_export_is_transport_frame() -> None:
    payload, metadata = encode_asr_control_final_marker_for_dora(
        session_id="session-1",
        stream_id="asr/main",
        seq=4,
    )
    final_marker = validate_dora_asr_control_final_marker(payload, metadata)

    assert metadata.to_dora_metadata() == {
        "fluent_audio_codec": "protobuf",
        "fluent_audio_schema_version": "fluent_audio.v1",
        "fluent_audio_message_type": AsrControlStreamFinal.DESCRIPTOR.full_name,
    }
    assert final_marker.session_id == "session-1"


def test_asr_control_final_marker_validates_and_rejects_decode_as_control() -> None:
    payload, metadata = encode_asr_control_final_marker_for_dora(
        session_id="session-1",
        stream_id="asr/main",
        seq=4,
    )

    final_marker = validate_dora_asr_control_final_marker(payload, metadata)

    assert metadata.final is True
    assert final_marker.session_id == "session-1"
    assert final_marker.stream_id == "asr/main"
    assert final_marker.seq == 4
    with pytest.raises(DoraAsrControlFinalMarkerError):
        decode_asr_control_from_dora(payload, metadata)
