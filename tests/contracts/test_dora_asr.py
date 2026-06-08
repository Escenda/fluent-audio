import pyarrow as pa
import pytest

from fluent_audio.contracts import AsrCancel, AsrStart, AsrStop
from fluent_audio.dora import (
    DoraAsrControlMetadata,
    DoraAsrControlMetadataError,
    decode_asr_control_from_dora,
    encode_asr_control_for_dora,
    validate_dora_asr_control_metadata,
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

    assert isinstance(decoded, AsrStart)
    assert decoded == start
    assert metadata.to_dora_metadata()["start_sample_index"] == 320


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

    assert isinstance(decoded, AsrStop)
    assert decoded == stop
    assert metadata.to_dora_metadata()["stop_sample_index"] == 3200


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

    assert isinstance(decoded, AsrCancel)
    assert decoded == cancel
    assert metadata.to_dora_metadata()["reason"] == "barge-in"


def test_asr_control_rejects_non_empty_payload() -> None:
    start = AsrStart(
        action="start",
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="asr/main",
        seq=0,
        start_sample_index=320,
    )
    _, metadata = encode_asr_control_for_dora(start)

    with pytest.raises(DoraAsrControlMetadataError, match="payload must be empty"):
        decode_asr_control_from_dora(pa.array([1], type=pa.uint8()), metadata)


def test_asr_control_rejects_variant_field_mismatch() -> None:
    with pytest.raises(DoraAsrControlMetadataError, match="metadata is invalid"):
        validate_dora_asr_control_metadata(
            {
                "action": "start",
                "session_id": "session-1",
                "user_turn_id": "user-turn-1",
                "stream_id": "asr/main",
                "seq": 0,
                "start_sample_index": 320,
                "stop_sample_index": 3200,
                "reason": "",
            }
        )


def test_asr_control_rejects_missing_required_metadata() -> None:
    with pytest.raises(DoraAsrControlMetadataError, match="missing required keys"):
        validate_dora_asr_control_metadata({"action": "start"})


def test_asr_control_metadata_model_export_is_flat() -> None:
    metadata = DoraAsrControlMetadata(
        action="cancel",
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="asr/main",
        seq=3,
        start_sample_index=0,
        stop_sample_index=0,
        reason="user-cancelled",
    )

    assert metadata.to_dora_metadata() == {
        "action": "cancel",
        "session_id": "session-1",
        "user_turn_id": "user-turn-1",
        "stream_id": "asr/main",
        "seq": 3,
        "start_sample_index": 0,
        "stop_sample_index": 0,
        "reason": "user-cancelled",
    }
