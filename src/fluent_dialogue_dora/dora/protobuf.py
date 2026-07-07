"""DORA transport codec for generated protobuf messages."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from typing import Literal, TypeAlias, TypeVar

import pyarrow as pa
from google.protobuf.message import DecodeError, Message
from pydantic import BaseModel, ConfigDict, Field

DoraMetadataPrimitive: TypeAlias = bool | int | float | str
DoraMetadataValue: TypeAlias = DoraMetadataPrimitive | list[DoraMetadataPrimitive]
DoraMetadataMapping: TypeAlias = Mapping[str, DoraMetadataValue]
DoraMetadataMutableMapping: TypeAlias = MutableMapping[str, DoraMetadataValue]
DoraProtobufPayloadInput: TypeAlias = bytes | pa.UInt8Array
DoraProtobufEncodedPayload: TypeAlias = pa.UInt8Array
ProtoMessageT = TypeVar("ProtoMessageT", bound=Message)

PROTOBUF_CODEC = "protobuf"
PROTOBUF_SCHEMA_VERSION = "fluent_dialogue_dora.v1"
PROTOBUF_CODEC_KEY = "fluent_dialogue_dora_codec"
PROTOBUF_SCHEMA_VERSION_KEY = "fluent_dialogue_dora_schema_version"
PROTOBUF_MESSAGE_TYPE_KEY = "fluent_dialogue_dora_message_type"
PROTOBUF_METADATA_FIELDS: tuple[str, ...] = (
    PROTOBUF_CODEC_KEY,
    PROTOBUF_SCHEMA_VERSION_KEY,
    PROTOBUF_MESSAGE_TYPE_KEY,
)


class DoraProtobufCodecError(ValueError):
    """Raised when a DORA protobuf payload or metadata frame is invalid."""


class DoraProtobufMetadata(BaseModel):
    """Thin DORA transport metadata for one protobuf payload."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    codec: Literal["protobuf"]
    schema_version: Literal["fluent_dialogue_dora.v1"]
    message_type: str = Field(min_length=1)

    def to_dora_metadata(self) -> DoraMetadataMutableMapping:
        return {
            PROTOBUF_CODEC_KEY: self.codec,
            PROTOBUF_SCHEMA_VERSION_KEY: self.schema_version,
            PROTOBUF_MESSAGE_TYPE_KEY: self.message_type,
        }

    @property
    def final(self) -> bool:
        return self.message_type.endswith("Final")

    @property
    def kind(self) -> str:
        if self.message_type.endswith("TranscriptDelta"):
            return "delta"
        if self.message_type.endswith("TranscriptPartial"):
            return "partial"
        if self.message_type.endswith("TranscriptFinal"):
            return "final"
        if self.message_type.endswith("TranscriptStreamFinal"):
            return "stream_final"
        if self.message_type.endswith("TtsTextChunk"):
            return "chunk"
        if self.message_type.endswith("TtsTextStreamFinal"):
            return "stream_final"
        return self.message_type.rsplit(".", maxsplit=1)[-1]


def encode_proto_message_for_dora(
    message: ProtoMessageT,
) -> tuple[DoraProtobufEncodedPayload, DoraProtobufMetadata]:
    message_type = message.DESCRIPTOR.full_name
    return (
        _encode_dora_protobuf_payload(message.SerializeToString()),
        DoraProtobufMetadata(
            codec=PROTOBUF_CODEC,
            schema_version=PROTOBUF_SCHEMA_VERSION,
            message_type=message_type,
        ),
    )


def decode_proto_message_from_dora(
    payload: DoraProtobufPayloadInput,
    metadata: DoraMetadataMapping | DoraProtobufMetadata | None,
    message_type: type[ProtoMessageT],
) -> ProtoMessageT:
    protobuf_metadata = validate_dora_protobuf_metadata(metadata)
    expected_message_type = message_type.DESCRIPTOR.full_name
    if protobuf_metadata.message_type != expected_message_type:
        raise DoraProtobufCodecError(
            "DORA protobuf message type mismatch: "
            f"expected {expected_message_type!r}, got {protobuf_metadata.message_type!r}"
        )
    message = message_type()
    try:
        message.ParseFromString(_decode_dora_protobuf_payload(payload))
    except DecodeError as exc:
        raise DoraProtobufCodecError(
            f"DORA protobuf payload could not decode as {expected_message_type}"
        ) from exc
    return message


def validate_dora_protobuf_metadata(
    metadata: DoraMetadataMapping | DoraProtobufMetadata | None,
) -> DoraProtobufMetadata:
    if metadata is None:
        raise DoraProtobufCodecError("DORA protobuf metadata is required")
    if isinstance(metadata, DoraProtobufMetadata):
        return metadata
    if not isinstance(metadata, Mapping):
        raise DoraProtobufCodecError("DORA protobuf metadata is invalid")

    missing_fields = [field for field in PROTOBUF_METADATA_FIELDS if field not in metadata]
    if missing_fields:
        missing = ", ".join(missing_fields)
        raise DoraProtobufCodecError(
            f"DORA protobuf metadata is invalid: missing required keys: {missing}"
        )
    try:
        return DoraProtobufMetadata.model_validate(
            {
                "codec": metadata[PROTOBUF_CODEC_KEY],
                "schema_version": metadata[PROTOBUF_SCHEMA_VERSION_KEY],
                "message_type": metadata[PROTOBUF_MESSAGE_TYPE_KEY],
            }
        )
    except ValueError as exc:
        raise DoraProtobufCodecError("DORA protobuf metadata is invalid") from exc


def _decode_dora_protobuf_payload(payload: DoraProtobufPayloadInput) -> bytes:
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, pa.UInt8Array):
        if payload.null_count != 0:
            raise DoraProtobufCodecError("DORA protobuf payload must not contain null values")
        return bytes(payload.to_pylist())
    payload_type = type(payload)
    raise DoraProtobufCodecError(
        f"DORA protobuf payload must be bytes or uint8 Arrow array, got "
        f"{payload_type.__module__}.{payload_type.__name__}"
    )


def _encode_dora_protobuf_payload(payload: bytes) -> DoraProtobufEncodedPayload:
    return pa.Array.from_buffers(
        pa.uint8(),
        len(payload),
        [None, pa.py_buffer(payload)],
    )
