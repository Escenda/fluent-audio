"""DORA protobuf helpers for speech synthesis contracts."""

from __future__ import annotations

from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field

from fluent_dialogue_dora.contracts import (
    AudioChunk,
    AudioFormat,
    SynthesizedAudioChunk,
    TtsTextChunk,
    TtsTextStreamFinal,
)
from fluent_dialogue_dora.dora.audio import _audio_format_from_proto, _audio_format_to_proto
from fluent_dialogue_dora.dora.protobuf import (
    DoraMetadataMapping,
    DoraProtobufEncodedPayload,
    DoraProtobufMetadata,
    DoraProtobufPayloadInput,
    decode_proto_message_from_dora,
    encode_proto_message_for_dora,
    validate_dora_protobuf_metadata,
)
from fluent_dialogue_dora_contracts.fluent_dialogue_dora.v1.audio_pb2 import AudioFrame
from fluent_dialogue_dora_contracts.fluent_dialogue_dora.v1.tts_pb2 import (
    SynthesizedAudioChunk as PbSynthesizedAudioChunk,
    SynthesizedAudioStreamFinal,
    TtsTextChunk as PbTtsTextChunk,
    TtsTextStreamFinal as PbTtsTextStreamFinal,
)

DoraTextPayloadInput: TypeAlias = DoraProtobufPayloadInput
DoraTextEncodedPayload: TypeAlias = DoraProtobufEncodedPayload
DoraSynthesizedAudioPayloadInput: TypeAlias = DoraProtobufPayloadInput
DoraSynthesizedAudioEncodedPayload: TypeAlias = DoraProtobufEncodedPayload
DoraTtsTextMetadata: TypeAlias = DoraProtobufMetadata
DoraSynthesizedAudioMetadata: TypeAlias = DoraProtobufMetadata


class DoraSynthesisMetadataError(ValueError):
    """Raised when DORA synthesis protobuf payloads cannot validate."""


class DoraSynthesizedAudioFinalMarkerError(DoraSynthesisMetadataError):
    """Raised when a synthesized audio final marker is decoded as a chunk."""


class DoraTtsTextStreamFinalMarkerError(DoraSynthesisMetadataError):
    """Raised when a TTS text stream marker is decoded as a chunk."""


class DoraSynthesizedAudioFinalMarker(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    request_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    user_turn_id: str = Field(min_length=1)
    assistant_turn_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    audio_source_id: str = Field(min_length=1)
    audio_stream_id: str = Field(min_length=1)
    audio_seq: int = Field(ge=0)
    audio_sample_index: int = Field(ge=0)
    audio_capture_time_ns: int = Field(ge=0)
    audio_format: AudioFormat


def encode_tts_text_chunk_for_dora(
    chunk: TtsTextChunk,
) -> tuple[DoraTextEncodedPayload, DoraTtsTextMetadata]:
    return encode_proto_message_for_dora(
        PbTtsTextChunk(
            request_id=chunk.request_id,
            session_id=chunk.session_id,
            user_turn_id=chunk.user_turn_id,
            assistant_turn_id=chunk.assistant_turn_id,
            seq=chunk.seq,
            text=chunk.text,
            is_final=chunk.is_final,
        )
    )


def encode_tts_text_stream_final_marker_for_dora(
    marker: TtsTextStreamFinal,
) -> tuple[DoraTextEncodedPayload, DoraTtsTextMetadata]:
    return encode_proto_message_for_dora(
        PbTtsTextStreamFinal(
            session_id=marker.session_id,
            user_turn_id=marker.user_turn_id,
            assistant_turn_id=marker.assistant_turn_id,
            seq=marker.seq,
        )
    )


def decode_tts_text_chunk_from_dora(
    payload: DoraTextPayloadInput,
    metadata: DoraMetadataMapping | DoraTtsTextMetadata | None,
) -> TtsTextChunk:
    text_metadata = validate_dora_tts_text_metadata(metadata)
    if text_metadata.message_type == PbTtsTextStreamFinal.DESCRIPTOR.full_name:
        raise DoraTtsTextStreamFinalMarkerError(
            "DORA TTS text stream final marker is not a TtsTextChunk"
        )
    try:
        chunk = decode_proto_message_from_dora(payload, text_metadata, PbTtsTextChunk)
        return TtsTextChunk(
            request_id=chunk.request_id,
            session_id=chunk.session_id,
            user_turn_id=chunk.user_turn_id,
            assistant_turn_id=chunk.assistant_turn_id,
            seq=chunk.seq,
            text=chunk.text,
            is_final=chunk.is_final,
        )
    except ValueError as exc:
        raise DoraSynthesisMetadataError(
            "DORA TTS text protobuf did not validate as TtsTextChunk"
        ) from exc


def validate_dora_tts_text_stream_final_marker(
    payload: DoraTextPayloadInput,
    metadata: DoraMetadataMapping | DoraTtsTextMetadata | None,
) -> TtsTextStreamFinal:
    text_metadata = validate_dora_tts_text_metadata(metadata)
    if text_metadata.message_type != PbTtsTextStreamFinal.DESCRIPTOR.full_name:
        raise DoraSynthesisMetadataError(
            "DORA TTS text metadata is not a stream final marker"
        )
    try:
        marker = decode_proto_message_from_dora(payload, text_metadata, PbTtsTextStreamFinal)
        return TtsTextStreamFinal(
            session_id=marker.session_id,
            user_turn_id=marker.user_turn_id,
            assistant_turn_id=marker.assistant_turn_id,
            seq=marker.seq,
        )
    except ValueError as exc:
        raise DoraSynthesisMetadataError(
            "DORA TTS text protobuf did not validate as TtsTextStreamFinal"
        ) from exc


def validate_dora_tts_text_metadata(
    metadata: DoraMetadataMapping | DoraTtsTextMetadata | None,
) -> DoraTtsTextMetadata:
    try:
        protobuf_metadata = validate_dora_protobuf_metadata(metadata)
    except ValueError as exc:
        raise DoraSynthesisMetadataError("DORA TTS text metadata is invalid") from exc
    if protobuf_metadata.message_type not in (
        PbTtsTextChunk.DESCRIPTOR.full_name,
        PbTtsTextStreamFinal.DESCRIPTOR.full_name,
    ):
        raise DoraSynthesisMetadataError(
            "DORA TTS text metadata message type is invalid: "
            f"{protobuf_metadata.message_type!r}"
        )
    return protobuf_metadata


def encode_synthesized_audio_chunk_for_dora(
    chunk: SynthesizedAudioChunk,
) -> tuple[DoraSynthesizedAudioEncodedPayload, DoraSynthesizedAudioMetadata]:
    audio = chunk.audio
    return encode_proto_message_for_dora(
        PbSynthesizedAudioChunk(
            request_id=chunk.request_id,
            session_id=chunk.session_id,
            user_turn_id=chunk.user_turn_id,
            assistant_turn_id=chunk.assistant_turn_id,
            seq=chunk.seq,
            audio=AudioFrame(
                source_id=audio.source_id,
                stream_id=audio.stream_id,
                seq=audio.seq,
                sample_index=audio.sample_index,
                capture_time_ns=audio.capture_time_ns,
                frame_count=audio.frame_count,
                format=_audio_format_to_proto(audio.format),
                payload=audio.payload,
            ),
        )
    )


def encode_synthesized_audio_final_marker_for_dora(
    *,
    request_id: str,
    session_id: str,
    user_turn_id: str,
    assistant_turn_id: str,
    seq: int,
    audio_source_id: str,
    audio_stream_id: str,
    audio_seq: int,
    audio_sample_index: int,
    audio_capture_time_ns: int,
    audio_format: AudioFormat,
) -> tuple[DoraSynthesizedAudioEncodedPayload, DoraSynthesizedAudioMetadata]:
    return encode_proto_message_for_dora(
        SynthesizedAudioStreamFinal(
            request_id=request_id,
            session_id=session_id,
            user_turn_id=user_turn_id,
            assistant_turn_id=assistant_turn_id,
            seq=seq,
            audio_source_id=audio_source_id,
            audio_stream_id=audio_stream_id,
            audio_seq=audio_seq,
            audio_sample_index=audio_sample_index,
            audio_capture_time_ns=audio_capture_time_ns,
            audio_format=_audio_format_to_proto(audio_format),
        )
    )


def decode_synthesized_audio_chunk_from_dora(
    payload: DoraSynthesizedAudioPayloadInput,
    metadata: DoraMetadataMapping | DoraSynthesizedAudioMetadata | None,
) -> SynthesizedAudioChunk:
    audio_metadata = validate_dora_synthesized_audio_metadata(metadata)
    if audio_metadata.message_type == SynthesizedAudioStreamFinal.DESCRIPTOR.full_name:
        raise DoraSynthesizedAudioFinalMarkerError(
            "DORA synthesized audio final marker is not a SynthesizedAudioChunk"
        )
    try:
        chunk = decode_proto_message_from_dora(
            payload,
            audio_metadata,
            PbSynthesizedAudioChunk,
        )
        audio = AudioChunk(
            source_id=chunk.audio.source_id,
            stream_id=chunk.audio.stream_id,
            seq=chunk.audio.seq,
            sample_index=chunk.audio.sample_index,
            capture_time_ns=chunk.audio.capture_time_ns,
            frame_count=chunk.audio.frame_count,
            format=_audio_format_from_proto(chunk.audio.format),
            payload=chunk.audio.payload,
        )
        return SynthesizedAudioChunk(
            request_id=chunk.request_id,
            session_id=chunk.session_id,
            user_turn_id=chunk.user_turn_id,
            assistant_turn_id=chunk.assistant_turn_id,
            seq=chunk.seq,
            audio=audio,
        )
    except ValueError as exc:
        raise DoraSynthesisMetadataError(
            "DORA synthesized audio protobuf did not validate as SynthesizedAudioChunk"
        ) from exc


def validate_dora_synthesized_audio_metadata(
    metadata: DoraMetadataMapping | DoraSynthesizedAudioMetadata | None,
) -> DoraSynthesizedAudioMetadata:
    try:
        protobuf_metadata = validate_dora_protobuf_metadata(metadata)
    except ValueError as exc:
        raise DoraSynthesisMetadataError("DORA synthesized audio metadata is invalid") from exc
    if protobuf_metadata.message_type not in (
        PbSynthesizedAudioChunk.DESCRIPTOR.full_name,
        SynthesizedAudioStreamFinal.DESCRIPTOR.full_name,
    ):
        raise DoraSynthesisMetadataError(
            "DORA synthesized audio metadata message type is invalid: "
            f"{protobuf_metadata.message_type!r}"
        )
    return protobuf_metadata


def validate_dora_synthesized_audio_final_marker(
    payload: DoraSynthesizedAudioPayloadInput,
    metadata: DoraMetadataMapping | DoraSynthesizedAudioMetadata | None,
) -> DoraSynthesizedAudioFinalMarker:
    audio_metadata = validate_dora_synthesized_audio_metadata(metadata)
    if audio_metadata.message_type != SynthesizedAudioStreamFinal.DESCRIPTOR.full_name:
        raise DoraSynthesisMetadataError(
            "DORA synthesized audio metadata is not a final marker"
        )
    try:
        final = decode_proto_message_from_dora(
            payload,
            audio_metadata,
            SynthesizedAudioStreamFinal,
        )
        return DoraSynthesizedAudioFinalMarker(
            request_id=final.request_id,
            session_id=final.session_id,
            user_turn_id=final.user_turn_id,
            assistant_turn_id=final.assistant_turn_id,
            seq=final.seq,
            audio_source_id=final.audio_source_id,
            audio_stream_id=final.audio_stream_id,
            audio_seq=final.audio_seq,
            audio_sample_index=final.audio_sample_index,
            audio_capture_time_ns=final.audio_capture_time_ns,
            audio_format=_audio_format_from_proto(final.audio_format),
        )
    except ValueError as exc:
        raise DoraSynthesisMetadataError(
            "DORA synthesized audio protobuf did not validate as SynthesizedAudioStreamFinal"
        ) from exc
