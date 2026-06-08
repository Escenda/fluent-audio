import pyarrow as pa
import pytest

from fluent_audio.contracts import TranscriptDelta, TranscriptFinal
from fluent_audio.dora import (
    DoraTranscriptMetadata,
    DoraTranscriptMetadataError,
    DoraTranscriptStreamFinalMarkerError,
    decode_transcript_delta_from_dora,
    decode_transcript_final_from_dora,
    encode_transcript_delta_for_dora,
    encode_transcript_final_for_dora,
    encode_transcript_stream_final_marker_for_dora,
    validate_dora_transcript_metadata,
    validate_dora_transcript_stream_final_marker,
)


def test_transcript_delta_roundtrips_through_dora_boundary() -> None:
    delta = TranscriptDelta(
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="transcript/main",
        seq=0,
        text="hello",
    )

    payload, metadata = encode_transcript_delta_for_dora(delta)
    decoded = decode_transcript_delta_from_dora(payload, metadata)

    assert decoded == delta
    assert bytes(payload.to_pylist()) == b"hello"
    assert metadata.to_dora_metadata()["kind"] == "delta"


def test_transcript_final_roundtrips_through_dora_boundary() -> None:
    final = TranscriptFinal(
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="transcript/main",
        seq=1,
        text="hello world",
        start_sample_index=320,
        end_sample_index=3200,
    )

    payload, metadata = encode_transcript_final_for_dora(final)
    decoded = decode_transcript_final_from_dora(payload, metadata)

    assert decoded == final
    assert bytes(payload.to_pylist()) == b"hello world"
    assert metadata.to_dora_metadata()["kind"] == "final"


def test_transcript_stream_final_marker_roundtrips_through_dora_boundary() -> None:
    payload, metadata = encode_transcript_stream_final_marker_for_dora(
        session_id="session-1",
        stream_id="transcript/main",
        seq=2,
        sample_index=3200,
    )

    final_marker = validate_dora_transcript_stream_final_marker(payload, metadata)

    assert final_marker.kind == "stream_final"
    assert final_marker.seq == 2
    assert final_marker.start_sample_index == 3200
    assert final_marker.end_sample_index == 3200


def test_transcript_delta_rejects_final_metadata_kind() -> None:
    final = TranscriptFinal(
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="transcript/main",
        seq=1,
        text="hello world",
        start_sample_index=320,
        end_sample_index=3200,
    )
    payload, metadata = encode_transcript_final_for_dora(final)

    with pytest.raises(DoraTranscriptMetadataError, match="not a transcript delta"):
        decode_transcript_delta_from_dora(payload, metadata)


def test_transcript_final_rejects_delta_metadata_kind() -> None:
    delta = TranscriptDelta(
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="transcript/main",
        seq=0,
        text="hello",
    )
    payload, metadata = encode_transcript_delta_for_dora(delta)

    with pytest.raises(DoraTranscriptMetadataError, match="not a transcript final"):
        decode_transcript_final_from_dora(payload, metadata)


def test_transcript_decoders_reject_stream_final_marker_as_transcript() -> None:
    payload, metadata = encode_transcript_stream_final_marker_for_dora(
        session_id="session-1",
        stream_id="transcript/main",
        seq=2,
        sample_index=3200,
    )

    with pytest.raises(DoraTranscriptStreamFinalMarkerError):
        decode_transcript_delta_from_dora(payload, metadata)
    with pytest.raises(DoraTranscriptStreamFinalMarkerError):
        decode_transcript_final_from_dora(payload, metadata)


def test_transcript_rejects_invalid_utf8_payload() -> None:
    delta = TranscriptDelta(
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="transcript/main",
        seq=0,
        text="hello",
    )
    _, metadata = encode_transcript_delta_for_dora(delta)

    with pytest.raises(DoraTranscriptMetadataError, match="valid UTF-8"):
        decode_transcript_delta_from_dora(pa.array([255], type=pa.uint8()), metadata)


def test_transcript_metadata_rejects_invalid_final_range() -> None:
    with pytest.raises(DoraTranscriptMetadataError, match="metadata is invalid"):
        validate_dora_transcript_metadata(
            {
                "kind": "final",
                "session_id": "session-1",
                "user_turn_id": "user-turn-1",
                "stream_id": "transcript/main",
                "seq": 1,
                "start_sample_index": 3200,
                "end_sample_index": 3200,
            }
        )


def test_transcript_metadata_model_export_is_flat() -> None:
    metadata = DoraTranscriptMetadata(
        kind="stream_final",
        session_id="session-1",
        user_turn_id="",
        stream_id="transcript/main",
        seq=2,
        start_sample_index=3200,
        end_sample_index=3200,
    )

    assert metadata.to_dora_metadata() == {
        "kind": "stream_final",
        "session_id": "session-1",
        "user_turn_id": "",
        "stream_id": "transcript/main",
        "seq": 2,
        "start_sample_index": 3200,
        "end_sample_index": 3200,
    }
