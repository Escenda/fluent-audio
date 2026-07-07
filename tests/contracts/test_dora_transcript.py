import pyarrow as pa
import pytest

from fluent_dialogue_dora.contracts import TranscriptDelta, TranscriptFinal, TranscriptPartial
from fluent_dialogue_dora.dora import (
    DoraTranscriptMetadataError,
    DoraTranscriptStreamFinalMarkerError,
    decode_transcript_delta_from_dora,
    decode_transcript_final_from_dora,
    decode_transcript_partial_from_dora,
    encode_transcript_delta_for_dora,
    encode_transcript_final_for_dora,
    encode_transcript_partial_for_dora,
    encode_transcript_stream_final_marker_for_dora,
    validate_dora_transcript_metadata,
    validate_dora_transcript_stream_final_marker,
)
from fluent_dialogue_dora_contracts.fluent_dialogue_dora.v1.asr_pb2 import (
    TranscriptDelta as PbTranscriptDelta,
    TranscriptFinal as PbTranscriptFinal,
    TranscriptPartial as PbTranscriptPartial,
    TranscriptStreamFinal,
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
    proto = PbTranscriptDelta.FromString(bytes(payload.to_pylist()))

    assert decoded == delta
    assert proto.text == "hello"
    assert metadata.kind == "delta"
    assert metadata.to_dora_metadata() == {
        "fluent_dialogue_dora_codec": "protobuf",
        "fluent_dialogue_dora_schema_version": "fluent_dialogue_dora.v1",
        "fluent_dialogue_dora_message_type": PbTranscriptDelta.DESCRIPTOR.full_name,
    }


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
    proto = PbTranscriptFinal.FromString(bytes(payload.to_pylist()))

    assert decoded == final
    assert proto.text == "hello world"
    assert metadata.kind == "final"


def test_transcript_partial_roundtrips_through_dora_boundary() -> None:
    partial = TranscriptPartial(
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="transcript/main",
        seq=1,
        text="hello wor",
    )

    payload, metadata = encode_transcript_partial_for_dora(partial)
    decoded = decode_transcript_partial_from_dora(payload, metadata)
    proto = PbTranscriptPartial.FromString(bytes(payload.to_pylist()))

    assert decoded == partial
    assert proto.text == "hello wor"
    assert metadata.kind == "partial"


def test_transcript_stream_final_marker_roundtrips_through_dora_boundary() -> None:
    payload, metadata = encode_transcript_stream_final_marker_for_dora(
        session_id="session-1",
        stream_id="transcript/main",
        seq=2,
        sample_index=3200,
    )

    final_marker = validate_dora_transcript_stream_final_marker(payload, metadata)

    assert metadata.kind == "stream_final"
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


def test_transcript_partial_rejects_delta_metadata_kind() -> None:
    delta = TranscriptDelta(
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="transcript/main",
        seq=0,
        text="hello",
    )
    payload, metadata = encode_transcript_delta_for_dora(delta)

    with pytest.raises(DoraTranscriptMetadataError, match="not a transcript partial"):
        decode_transcript_partial_from_dora(payload, metadata)


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
        decode_transcript_partial_from_dora(payload, metadata)
    with pytest.raises(DoraTranscriptStreamFinalMarkerError):
        decode_transcript_final_from_dora(payload, metadata)


def test_transcript_rejects_invalid_payload() -> None:
    delta = TranscriptDelta(
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="transcript/main",
        seq=0,
        text="hello",
    )
    _, metadata = encode_transcript_delta_for_dora(delta)

    with pytest.raises(DoraTranscriptMetadataError, match="protobuf did not validate"):
        decode_transcript_delta_from_dora(pa.array([255], type=pa.uint8()), metadata)


def test_transcript_metadata_rejects_invalid_message_type() -> None:
    with pytest.raises(DoraTranscriptMetadataError, match="message type is invalid"):
        validate_dora_transcript_metadata(
            {
                "fluent_dialogue_dora_codec": "protobuf",
                "fluent_dialogue_dora_schema_version": "fluent_dialogue_dora.v1",
                "fluent_dialogue_dora_message_type": "fluent_dialogue_dora.v1.AudioFrame",
            }
        )


def test_transcript_metadata_model_export_is_transport_frame() -> None:
    payload, metadata = encode_transcript_stream_final_marker_for_dora(
        session_id="session-1",
        stream_id="transcript/main",
        seq=2,
        sample_index=3200,
    )
    decoded = TranscriptStreamFinal.FromString(bytes(payload.to_pylist()))

    assert decoded.sample_index == 3200
    assert metadata.to_dora_metadata() == {
        "fluent_dialogue_dora_codec": "protobuf",
        "fluent_dialogue_dora_schema_version": "fluent_dialogue_dora.v1",
        "fluent_dialogue_dora_message_type": TranscriptStreamFinal.DESCRIPTOR.full_name,
    }
