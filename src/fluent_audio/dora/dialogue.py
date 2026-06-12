"""DORA protobuf helpers for dialogue and agent runtime contracts."""

from __future__ import annotations

import json
from typing import TypeAlias

from google.protobuf.json_format import MessageToJson, Parse
from google.protobuf.struct_pb2 import Value
from pydantic import TypeAdapter

from fluent_audio.contracts import (
    AgentApprovalRequest,
    AgentCancelRequest,
    AgentMcpElicitationRequest,
    AgentMcpElicitationResponse,
    AgentTextDelta,
    AgentToolEvent,
    AgentTurnDone,
    AgentTurnRequest,
    AgentUserInputAnswer,
    AgentUserInputOption,
    AgentUserInputQuestion,
    AgentUserInputRequest,
    AgentUserInputResponse,
    DialogueEvent,
    DialogueInput,
    JsonValue,
)
from fluent_audio.dora.protobuf import (
    DoraMetadataMapping,
    DoraProtobufEncodedPayload,
    DoraProtobufMetadata,
    DoraProtobufPayloadInput,
    decode_proto_message_from_dora,
    encode_proto_message_for_dora,
    validate_dora_protobuf_metadata,
)
from fluent_audio_contracts.fluent_audio.v1 import dialogue_pb2 as dialogue_pb

AgentRuntimeEvent: TypeAlias = (
    AgentTextDelta
    | AgentTurnDone
    | AgentApprovalRequest
    | AgentUserInputRequest
    | AgentMcpElicitationRequest
    | AgentToolEvent
)
DoraDialoguePayloadInput: TypeAlias = DoraProtobufPayloadInput
DoraDialogueEncodedPayload: TypeAlias = DoraProtobufEncodedPayload
DoraDialogueInputMetadata: TypeAlias = DoraProtobufMetadata
DoraDialogueEventMetadata: TypeAlias = DoraProtobufMetadata
DoraAgentTextMetadata: TypeAlias = DoraProtobufMetadata
DoraAgentTurnRequestMetadata: TypeAlias = DoraProtobufMetadata
DoraAgentTurnDoneMetadata: TypeAlias = DoraProtobufMetadata
DoraAgentApprovalMetadata: TypeAlias = DoraProtobufMetadata
DoraAgentUserInputRequestMetadata: TypeAlias = DoraProtobufMetadata
DoraAgentUserInputResponseMetadata: TypeAlias = DoraProtobufMetadata
DoraAgentMcpElicitationRequestMetadata: TypeAlias = DoraProtobufMetadata
DoraAgentMcpElicitationResponseMetadata: TypeAlias = DoraProtobufMetadata
DoraAgentToolMetadata: TypeAlias = DoraProtobufMetadata
DoraAgentRuntimeEventMetadata: TypeAlias = DoraProtobufMetadata
DoraAgentCancelMetadata: TypeAlias = DoraProtobufMetadata

_JSON_VALUE_ADAPTER = TypeAdapter(JsonValue)


class DoraDialogueMetadataError(ValueError):
    """Raised when DORA dialogue protobuf payloads cannot validate."""


def encode_dialogue_input_for_dora(
    event: DialogueInput,
) -> tuple[DoraDialogueEncodedPayload, DoraDialogueInputMetadata]:
    proto_event = dialogue_pb.DialogueInput(
        input_type=_dialogue_input_kind_to_proto(event.input_type),
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        seq=event.seq,
    )
    if event.text is not None:
        proto_event.text = event.text
    if event.request_id is not None:
        proto_event.request_id = event.request_id
    return encode_proto_message_for_dora(proto_event)


def decode_dialogue_input_from_dora(
    payload: DoraDialoguePayloadInput,
    metadata: DoraMetadataMapping | DoraDialogueInputMetadata | None,
) -> DialogueInput:
    dialogue_metadata = validate_dora_dialogue_input_metadata(metadata)
    try:
        event = decode_proto_message_from_dora(payload, dialogue_metadata, dialogue_pb.DialogueInput)
        return DialogueInput(
            input_type=_dialogue_input_kind_from_proto(event.input_type),
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            seq=event.seq,
            text=event.text if event.HasField("text") else None,
            request_id=event.request_id if event.HasField("request_id") else None,
        )
    except ValueError as exc:
        raise DoraDialogueMetadataError(
            "DORA dialogue input protobuf did not validate as DialogueInput"
        ) from exc


def encode_dialogue_event_for_dora(
    event: DialogueEvent,
) -> tuple[DoraDialogueEncodedPayload, DoraDialogueEventMetadata]:
    proto_event = dialogue_pb.DialogueEvent(
        event=_dialogue_event_kind_to_proto(event.event),
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        seq=event.seq,
    )
    if event.text is not None:
        proto_event.text = event.text
    if event.request_id is not None:
        proto_event.request_id = event.request_id
    if event.message is not None:
        proto_event.message = event.message
    return encode_proto_message_for_dora(proto_event)


def decode_dialogue_event_from_dora(
    payload: DoraDialoguePayloadInput,
    metadata: DoraMetadataMapping | DoraDialogueEventMetadata | None,
) -> DialogueEvent:
    dialogue_metadata = validate_dora_dialogue_event_metadata(metadata)
    try:
        event = decode_proto_message_from_dora(payload, dialogue_metadata, dialogue_pb.DialogueEvent)
        return DialogueEvent(
            event=_dialogue_event_kind_from_proto(event.event),
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            seq=event.seq,
            text=event.text if event.HasField("text") else None,
            request_id=event.request_id if event.HasField("request_id") else None,
            message=event.message if event.HasField("message") else None,
        )
    except ValueError as exc:
        raise DoraDialogueMetadataError(
            "DORA dialogue event protobuf did not validate as DialogueEvent"
        ) from exc


def encode_agent_text_delta_for_dora(
    event: AgentTextDelta,
) -> tuple[DoraDialogueEncodedPayload, DoraAgentTextMetadata]:
    return encode_proto_message_for_dora(
        dialogue_pb.AgentTextDelta(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            agent_turn_id=event.agent_turn_id,
            seq=event.seq,
            text=event.text,
        )
    )


def decode_agent_text_delta_from_dora(
    payload: DoraDialoguePayloadInput,
    metadata: DoraMetadataMapping | DoraAgentTextMetadata | None,
) -> AgentTextDelta:
    agent_metadata = validate_dora_agent_text_metadata(metadata)
    try:
        event = decode_proto_message_from_dora(payload, agent_metadata, dialogue_pb.AgentTextDelta)
        return AgentTextDelta(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            agent_turn_id=event.agent_turn_id,
            seq=event.seq,
            text=event.text,
        )
    except ValueError as exc:
        raise DoraDialogueMetadataError(
            "DORA agent text protobuf did not validate as AgentTextDelta"
        ) from exc


def encode_agent_turn_request_for_dora(
    event: AgentTurnRequest,
) -> tuple[DoraDialogueEncodedPayload, DoraAgentTurnRequestMetadata]:
    return encode_proto_message_for_dora(
        dialogue_pb.AgentTurnRequest(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            assistant_turn_id=event.assistant_turn_id,
            seq=event.seq,
            text=event.text,
        )
    )


def decode_agent_turn_request_from_dora(
    payload: DoraDialoguePayloadInput,
    metadata: DoraMetadataMapping | DoraAgentTurnRequestMetadata | None,
) -> AgentTurnRequest:
    turn_metadata = validate_dora_agent_turn_request_metadata(metadata)
    try:
        event = decode_proto_message_from_dora(payload, turn_metadata, dialogue_pb.AgentTurnRequest)
        return AgentTurnRequest(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            assistant_turn_id=event.assistant_turn_id,
            seq=event.seq,
            text=event.text,
        )
    except ValueError as exc:
        raise DoraDialogueMetadataError(
            "DORA agent turn request protobuf did not validate as AgentTurnRequest"
        ) from exc


def encode_agent_turn_done_for_dora(
    event: AgentTurnDone,
) -> tuple[DoraDialogueEncodedPayload, DoraAgentTurnDoneMetadata]:
    proto_event = dialogue_pb.AgentTurnDone(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        agent_turn_id=event.agent_turn_id,
        seq=event.seq,
        status=_agent_turn_done_status_to_proto(event.status),
    )
    if event.message is not None:
        proto_event.reason = event.message
    return encode_proto_message_for_dora(proto_event)


def decode_agent_turn_done_from_dora(
    payload: DoraDialoguePayloadInput,
    metadata: DoraMetadataMapping | DoraAgentTurnDoneMetadata | None,
) -> AgentTurnDone:
    done_metadata = validate_dora_agent_turn_done_metadata(metadata)
    try:
        event = decode_proto_message_from_dora(payload, done_metadata, dialogue_pb.AgentTurnDone)
        return AgentTurnDone(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            agent_turn_id=event.agent_turn_id,
            seq=event.seq,
            status=_agent_turn_done_status_from_proto(event.status),
            message=event.reason if event.HasField("reason") else None,
        )
    except ValueError as exc:
        raise DoraDialogueMetadataError(
            "DORA agent turn done protobuf did not validate as AgentTurnDone"
        ) from exc


def encode_agent_approval_request_for_dora(
    event: AgentApprovalRequest,
) -> tuple[DoraDialogueEncodedPayload, DoraAgentApprovalMetadata]:
    return encode_proto_message_for_dora(
        dialogue_pb.AgentApprovalRequest(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            approval_id=event.approval_id,
            seq=event.seq,
            prompt=event.prompt,
            action_label=event.action_label,
        )
    )


def decode_agent_approval_request_from_dora(
    payload: DoraDialoguePayloadInput,
    metadata: DoraMetadataMapping | DoraAgentApprovalMetadata | None,
) -> AgentApprovalRequest:
    approval_metadata = validate_dora_agent_approval_metadata(metadata)
    try:
        event = decode_proto_message_from_dora(
            payload,
            approval_metadata,
            dialogue_pb.AgentApprovalRequest,
        )
        return AgentApprovalRequest(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            approval_id=event.approval_id,
            seq=event.seq,
            prompt=event.prompt,
            action_label=event.action_label,
        )
    except ValueError as exc:
        raise DoraDialogueMetadataError(
            "DORA agent approval protobuf did not validate as AgentApprovalRequest"
        ) from exc


def encode_agent_user_input_request_for_dora(
    event: AgentUserInputRequest,
) -> tuple[DoraDialogueEncodedPayload, DoraAgentUserInputRequestMetadata]:
    return encode_proto_message_for_dora(
        dialogue_pb.AgentUserInputRequest(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            request_id=event.request_id,
            seq=event.seq,
            questions=[_user_input_question_to_proto(question) for question in event.questions],
        )
    )


def decode_agent_user_input_request_from_dora(
    payload: DoraDialoguePayloadInput,
    metadata: DoraMetadataMapping | DoraAgentUserInputRequestMetadata | None,
) -> AgentUserInputRequest:
    request_metadata = validate_dora_agent_user_input_request_metadata(metadata)
    try:
        event = decode_proto_message_from_dora(
            payload,
            request_metadata,
            dialogue_pb.AgentUserInputRequest,
        )
        return AgentUserInputRequest(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            request_id=event.request_id,
            seq=event.seq,
            questions=tuple(_user_input_question_from_proto(question) for question in event.questions),
        )
    except ValueError as exc:
        raise DoraDialogueMetadataError(
            "DORA agent user input protobuf did not validate as AgentUserInputRequest"
        ) from exc


def encode_agent_user_input_response_for_dora(
    event: AgentUserInputResponse,
) -> tuple[DoraDialogueEncodedPayload, DoraAgentUserInputResponseMetadata]:
    return encode_proto_message_for_dora(
        dialogue_pb.AgentUserInputResponse(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            request_id=event.request_id,
            seq=event.seq,
            answers=[
                dialogue_pb.AgentUserInputAnswer(
                    question_id=answer.question_id,
                    answers=list(answer.answers),
                )
                for answer in event.answers
            ],
        )
    )


def decode_agent_user_input_response_from_dora(
    payload: DoraDialoguePayloadInput,
    metadata: DoraMetadataMapping | DoraAgentUserInputResponseMetadata | None,
) -> AgentUserInputResponse:
    response_metadata = validate_dora_agent_user_input_response_metadata(metadata)
    try:
        event = decode_proto_message_from_dora(
            payload,
            response_metadata,
            dialogue_pb.AgentUserInputResponse,
        )
        return AgentUserInputResponse(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            request_id=event.request_id,
            seq=event.seq,
            answers=tuple(
                AgentUserInputAnswer(
                    question_id=answer.question_id,
                    answers=tuple(answer.answers),
                )
                for answer in event.answers
            ),
        )
    except ValueError as exc:
        raise DoraDialogueMetadataError(
            "DORA agent user input protobuf did not validate as AgentUserInputResponse"
        ) from exc


def encode_agent_mcp_elicitation_request_for_dora(
    event: AgentMcpElicitationRequest,
) -> tuple[DoraDialogueEncodedPayload, DoraAgentMcpElicitationRequestMetadata]:
    proto_event = dialogue_pb.AgentMcpElicitationRequest(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        request_id=event.request_id,
        seq=event.seq,
        server_name=event.server_name,
        mode=_mcp_elicitation_mode_to_proto(event.mode),
        message=event.message,
    )
    if event.url is not None:
        proto_event.url = event.url
    if event.elicitation_id is not None:
        proto_event.elicitation_id = event.elicitation_id
    if event.requested_schema is not None:
        proto_event.requested_schema.CopyFrom(_json_value_to_proto(event.requested_schema))
    if event.meta is not None:
        proto_event.meta.CopyFrom(_json_value_to_proto(event.meta))
    return encode_proto_message_for_dora(proto_event)


def decode_agent_mcp_elicitation_request_from_dora(
    payload: DoraDialoguePayloadInput,
    metadata: DoraMetadataMapping | DoraAgentMcpElicitationRequestMetadata | None,
) -> AgentMcpElicitationRequest:
    request_metadata = validate_dora_agent_mcp_elicitation_request_metadata(metadata)
    try:
        event = decode_proto_message_from_dora(
            payload,
            request_metadata,
            dialogue_pb.AgentMcpElicitationRequest,
        )
        return AgentMcpElicitationRequest(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            request_id=event.request_id,
            seq=event.seq,
            server_name=event.server_name,
            mode=_mcp_elicitation_mode_from_proto(event.mode),
            message=event.message,
            url=event.url if event.HasField("url") else None,
            elicitation_id=event.elicitation_id if event.HasField("elicitation_id") else None,
            requested_schema=_json_value_from_proto(event.requested_schema)
            if event.HasField("requested_schema")
            else None,
            meta=_json_value_from_proto(event.meta) if event.HasField("meta") else None,
        )
    except ValueError as exc:
        raise DoraDialogueMetadataError(
            "DORA MCP elicitation protobuf did not validate as AgentMcpElicitationRequest"
        ) from exc


def encode_agent_mcp_elicitation_response_for_dora(
    event: AgentMcpElicitationResponse,
) -> tuple[DoraDialogueEncodedPayload, DoraAgentMcpElicitationResponseMetadata]:
    proto_event = dialogue_pb.AgentMcpElicitationResponse(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        request_id=event.request_id,
        seq=event.seq,
        action=_mcp_elicitation_action_to_proto(event.action),
    )
    if event.content is not None:
        proto_event.content.CopyFrom(_json_value_to_proto(event.content))
    if event.meta is not None:
        proto_event.meta.CopyFrom(_json_value_to_proto(event.meta))
    return encode_proto_message_for_dora(proto_event)


def decode_agent_mcp_elicitation_response_from_dora(
    payload: DoraDialoguePayloadInput,
    metadata: DoraMetadataMapping | DoraAgentMcpElicitationResponseMetadata | None,
) -> AgentMcpElicitationResponse:
    response_metadata = validate_dora_agent_mcp_elicitation_response_metadata(metadata)
    try:
        event = decode_proto_message_from_dora(
            payload,
            response_metadata,
            dialogue_pb.AgentMcpElicitationResponse,
        )
        return AgentMcpElicitationResponse(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            request_id=event.request_id,
            seq=event.seq,
            action=_mcp_elicitation_action_from_proto(event.action),
            content=_json_value_from_proto(event.content) if event.HasField("content") else None,
            meta=_json_value_from_proto(event.meta) if event.HasField("meta") else None,
        )
    except ValueError as exc:
        raise DoraDialogueMetadataError(
            "DORA MCP elicitation protobuf did not validate as AgentMcpElicitationResponse"
        ) from exc


def encode_agent_tool_event_for_dora(
    event: AgentToolEvent,
) -> tuple[DoraDialogueEncodedPayload, DoraAgentToolMetadata]:
    proto_event = dialogue_pb.AgentToolEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        tool_call_id=event.tool_call_id,
        seq=event.seq,
        event=_tool_event_kind_to_proto(event.event),
        name=event.tool_name,
    )
    if event.summary is not None:
        proto_event.summary = event.summary
    if event.error_message is not None:
        proto_event.error_message = event.error_message
    return encode_proto_message_for_dora(proto_event)


def decode_agent_tool_event_from_dora(
    payload: DoraDialoguePayloadInput,
    metadata: DoraMetadataMapping | DoraAgentToolMetadata | None,
) -> AgentToolEvent:
    tool_metadata = validate_dora_agent_tool_metadata(metadata)
    try:
        event = decode_proto_message_from_dora(payload, tool_metadata, dialogue_pb.AgentToolEvent)
        event_kind = _tool_event_kind_from_proto(event.event)
        return AgentToolEvent(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            tool_call_id=event.tool_call_id,
            tool_name=event.name,
            seq=event.seq,
            event=event_kind,
            summary=event.summary if event.HasField("summary") else None,
            error_message=event.error_message if event.HasField("error_message") else None,
        )
    except ValueError as exc:
        raise DoraDialogueMetadataError(
            "DORA agent tool protobuf did not validate as AgentToolEvent"
        ) from exc


def encode_agent_runtime_event_for_dora(
    event: AgentRuntimeEvent,
) -> tuple[DoraDialogueEncodedPayload, DoraAgentRuntimeEventMetadata]:
    if isinstance(event, AgentTextDelta):
        return encode_agent_text_delta_for_dora(event)
    if isinstance(event, AgentTurnDone):
        return encode_agent_turn_done_for_dora(event)
    if isinstance(event, AgentApprovalRequest):
        return encode_agent_approval_request_for_dora(event)
    if isinstance(event, AgentUserInputRequest):
        return encode_agent_user_input_request_for_dora(event)
    if isinstance(event, AgentMcpElicitationRequest):
        return encode_agent_mcp_elicitation_request_for_dora(event)
    if isinstance(event, AgentToolEvent):
        return encode_agent_tool_event_for_dora(event)
    event_type = type(event)
    raise DoraDialogueMetadataError(
        "Agent runtime event has unsupported type "
        f"{event_type.__module__}.{event_type.__name__}"
    )


def decode_agent_runtime_event_from_dora(
    payload: DoraDialoguePayloadInput,
    metadata: DoraMetadataMapping | DoraAgentRuntimeEventMetadata | None,
) -> AgentRuntimeEvent:
    runtime_metadata = validate_dora_agent_runtime_event_metadata(metadata)
    if runtime_metadata.message_type == dialogue_pb.AgentTextDelta.DESCRIPTOR.full_name:
        return decode_agent_text_delta_from_dora(payload, runtime_metadata)
    if runtime_metadata.message_type == dialogue_pb.AgentTurnDone.DESCRIPTOR.full_name:
        return decode_agent_turn_done_from_dora(payload, runtime_metadata)
    if runtime_metadata.message_type == dialogue_pb.AgentApprovalRequest.DESCRIPTOR.full_name:
        return decode_agent_approval_request_from_dora(payload, runtime_metadata)
    if runtime_metadata.message_type == dialogue_pb.AgentUserInputRequest.DESCRIPTOR.full_name:
        return decode_agent_user_input_request_from_dora(payload, runtime_metadata)
    if runtime_metadata.message_type == dialogue_pb.AgentMcpElicitationRequest.DESCRIPTOR.full_name:
        return decode_agent_mcp_elicitation_request_from_dora(payload, runtime_metadata)
    if runtime_metadata.message_type == dialogue_pb.AgentToolEvent.DESCRIPTOR.full_name:
        return decode_agent_tool_event_from_dora(payload, runtime_metadata)
    raise DoraDialogueMetadataError(
        "DORA agent runtime metadata message type is invalid: "
        f"{runtime_metadata.message_type!r}"
    )


def encode_agent_cancel_request_for_dora(
    event: AgentCancelRequest,
) -> tuple[DoraDialogueEncodedPayload, DoraAgentCancelMetadata]:
    proto_event = dialogue_pb.AgentCancelRequest(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        seq=event.seq,
    )
    if event.reason is not None:
        proto_event.reason = event.reason
    return encode_proto_message_for_dora(proto_event)


def decode_agent_cancel_request_from_dora(
    payload: DoraDialoguePayloadInput,
    metadata: DoraMetadataMapping | DoraAgentCancelMetadata | None,
) -> AgentCancelRequest:
    cancel_metadata = validate_dora_agent_cancel_metadata(metadata)
    try:
        event = decode_proto_message_from_dora(payload, cancel_metadata, dialogue_pb.AgentCancelRequest)
        return AgentCancelRequest(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            seq=event.seq,
            reason=event.reason if event.HasField("reason") else None,
        )
    except ValueError as exc:
        raise DoraDialogueMetadataError(
            "DORA agent cancel protobuf did not validate as AgentCancelRequest"
        ) from exc


def validate_dora_dialogue_input_metadata(
    metadata: DoraMetadataMapping | DoraDialogueInputMetadata | None,
) -> DoraDialogueInputMetadata:
    return _validate_dialogue_metadata(metadata, dialogue_pb.DialogueInput.DESCRIPTOR.full_name)


def validate_dora_dialogue_event_metadata(
    metadata: DoraMetadataMapping | DoraDialogueEventMetadata | None,
) -> DoraDialogueEventMetadata:
    return _validate_dialogue_metadata(metadata, dialogue_pb.DialogueEvent.DESCRIPTOR.full_name)


def validate_dora_agent_text_metadata(
    metadata: DoraMetadataMapping | DoraAgentTextMetadata | None,
) -> DoraAgentTextMetadata:
    return _validate_dialogue_metadata(metadata, dialogue_pb.AgentTextDelta.DESCRIPTOR.full_name)


def validate_dora_agent_turn_request_metadata(
    metadata: DoraMetadataMapping | DoraAgentTurnRequestMetadata | None,
) -> DoraAgentTurnRequestMetadata:
    return _validate_dialogue_metadata(metadata, dialogue_pb.AgentTurnRequest.DESCRIPTOR.full_name)


def validate_dora_agent_turn_done_metadata(
    metadata: DoraMetadataMapping | DoraAgentTurnDoneMetadata | None,
) -> DoraAgentTurnDoneMetadata:
    return _validate_dialogue_metadata(metadata, dialogue_pb.AgentTurnDone.DESCRIPTOR.full_name)


def validate_dora_agent_approval_metadata(
    metadata: DoraMetadataMapping | DoraAgentApprovalMetadata | None,
) -> DoraAgentApprovalMetadata:
    return _validate_dialogue_metadata(metadata, dialogue_pb.AgentApprovalRequest.DESCRIPTOR.full_name)


def validate_dora_agent_user_input_request_metadata(
    metadata: DoraMetadataMapping | DoraAgentUserInputRequestMetadata | None,
) -> DoraAgentUserInputRequestMetadata:
    return _validate_dialogue_metadata(
        metadata,
        dialogue_pb.AgentUserInputRequest.DESCRIPTOR.full_name,
    )


def validate_dora_agent_user_input_response_metadata(
    metadata: DoraMetadataMapping | DoraAgentUserInputResponseMetadata | None,
) -> DoraAgentUserInputResponseMetadata:
    return _validate_dialogue_metadata(
        metadata,
        dialogue_pb.AgentUserInputResponse.DESCRIPTOR.full_name,
    )


def validate_dora_agent_mcp_elicitation_request_metadata(
    metadata: DoraMetadataMapping | DoraAgentMcpElicitationRequestMetadata | None,
) -> DoraAgentMcpElicitationRequestMetadata:
    return _validate_dialogue_metadata(
        metadata,
        dialogue_pb.AgentMcpElicitationRequest.DESCRIPTOR.full_name,
    )


def validate_dora_agent_mcp_elicitation_response_metadata(
    metadata: DoraMetadataMapping | DoraAgentMcpElicitationResponseMetadata | None,
) -> DoraAgentMcpElicitationResponseMetadata:
    return _validate_dialogue_metadata(
        metadata,
        dialogue_pb.AgentMcpElicitationResponse.DESCRIPTOR.full_name,
    )


def validate_dora_agent_tool_metadata(
    metadata: DoraMetadataMapping | DoraAgentToolMetadata | None,
) -> DoraAgentToolMetadata:
    return _validate_dialogue_metadata(metadata, dialogue_pb.AgentToolEvent.DESCRIPTOR.full_name)


def validate_dora_agent_runtime_event_metadata(
    metadata: DoraMetadataMapping | DoraAgentRuntimeEventMetadata | None,
) -> DoraAgentRuntimeEventMetadata:
    runtime_metadata = _validate_dialogue_metadata_only(metadata)
    if runtime_metadata.message_type not in _agent_runtime_message_types():
        raise DoraDialogueMetadataError(
            "DORA agent runtime metadata message type is invalid: "
            f"{runtime_metadata.message_type!r}"
        )
    return runtime_metadata


def validate_dora_agent_cancel_metadata(
    metadata: DoraMetadataMapping | DoraAgentCancelMetadata | None,
) -> DoraAgentCancelMetadata:
    return _validate_dialogue_metadata(metadata, dialogue_pb.AgentCancelRequest.DESCRIPTOR.full_name)


def _validate_dialogue_metadata(
    metadata: DoraMetadataMapping | DoraProtobufMetadata | None,
    message_type: str,
) -> DoraProtobufMetadata:
    dialogue_metadata = _validate_dialogue_metadata_only(metadata)
    if dialogue_metadata.message_type != message_type:
        raise DoraDialogueMetadataError(
            "DORA dialogue metadata message type is invalid: "
            f"expected {message_type!r}, got {dialogue_metadata.message_type!r}"
        )
    return dialogue_metadata


def _validate_dialogue_metadata_only(
    metadata: DoraMetadataMapping | DoraProtobufMetadata | None,
) -> DoraProtobufMetadata:
    try:
        return validate_dora_protobuf_metadata(metadata)
    except ValueError as exc:
        raise DoraDialogueMetadataError("DORA dialogue metadata is invalid") from exc


def _agent_runtime_message_types() -> tuple[str, ...]:
    return (
        dialogue_pb.AgentTextDelta.DESCRIPTOR.full_name,
        dialogue_pb.AgentTurnDone.DESCRIPTOR.full_name,
        dialogue_pb.AgentApprovalRequest.DESCRIPTOR.full_name,
        dialogue_pb.AgentUserInputRequest.DESCRIPTOR.full_name,
        dialogue_pb.AgentMcpElicitationRequest.DESCRIPTOR.full_name,
        dialogue_pb.AgentToolEvent.DESCRIPTOR.full_name,
    )


def _user_input_question_to_proto(
    question: AgentUserInputQuestion,
) -> dialogue_pb.AgentUserInputQuestion:
    return dialogue_pb.AgentUserInputQuestion(
        id=question.id,
        header=question.header,
        question=question.question,
        is_other=question.is_other,
        is_secret=question.is_secret,
        options=[
            dialogue_pb.AgentUserInputOption(
                label=option.label,
                description=option.description,
            )
            for option in question.options or ()
        ],
    )


def _user_input_question_from_proto(
    question: dialogue_pb.AgentUserInputQuestion,
) -> AgentUserInputQuestion:
    options = tuple(
        AgentUserInputOption(label=option.label, description=option.description)
        for option in question.options
    )
    return AgentUserInputQuestion(
        id=question.id,
        header=question.header,
        question=question.question,
        is_other=question.is_other,
        is_secret=question.is_secret,
        options=options if options else None,
    )


def _json_value_to_proto(value: JsonValue) -> Value:
    proto_value = Value()
    Parse(json.dumps(value, separators=(",", ":")), proto_value)
    return proto_value


def _json_value_from_proto(value: Value) -> JsonValue:
    parsed = json.loads(MessageToJson(value))
    return _JSON_VALUE_ADAPTER.validate_python(parsed)


def _dialogue_input_kind_to_proto(kind: str) -> int:
    mapping = {
        "transcript_final": dialogue_pb.DIALOGUE_INPUT_KIND_TRANSCRIPT_FINAL,
        "cancel": dialogue_pb.DIALOGUE_INPUT_KIND_CANCEL,
        "playback_done": dialogue_pb.DIALOGUE_INPUT_KIND_PLAYBACK_DONE,
    }
    if kind not in mapping:
        raise DoraDialogueMetadataError(f"Unsupported dialogue input kind: {kind!r}")
    return mapping[kind]


def _dialogue_input_kind_from_proto(kind: int) -> str:
    mapping = {
        dialogue_pb.DIALOGUE_INPUT_KIND_TRANSCRIPT_FINAL: "transcript_final",
        dialogue_pb.DIALOGUE_INPUT_KIND_CANCEL: "cancel",
        dialogue_pb.DIALOGUE_INPUT_KIND_PLAYBACK_DONE: "playback_done",
    }
    if kind not in mapping:
        raise DoraDialogueMetadataError(f"Unsupported protobuf dialogue input kind: {kind}")
    return mapping[kind]


def _dialogue_event_kind_to_proto(kind: str) -> int:
    mapping = {
        "agent_text": dialogue_pb.DIALOGUE_EVENT_KIND_AGENT_TEXT,
        "tts_text": dialogue_pb.DIALOGUE_EVENT_KIND_TTS_TEXT,
        "approval_requested": dialogue_pb.DIALOGUE_EVENT_KIND_APPROVAL_REQUESTED,
        "user_input_requested": dialogue_pb.DIALOGUE_EVENT_KIND_USER_INPUT_REQUESTED,
        "mcp_elicitation_requested": dialogue_pb.DIALOGUE_EVENT_KIND_MCP_ELICITATION_REQUESTED,
        "tool_event": dialogue_pb.DIALOGUE_EVENT_KIND_TOOL_EVENT,
        "cancelled": dialogue_pb.DIALOGUE_EVENT_KIND_CANCELLED,
        "error": dialogue_pb.DIALOGUE_EVENT_KIND_ERROR,
    }
    if kind not in mapping:
        raise DoraDialogueMetadataError(f"Unsupported dialogue event kind: {kind!r}")
    return mapping[kind]


def _dialogue_event_kind_from_proto(kind: int) -> str:
    mapping = {
        dialogue_pb.DIALOGUE_EVENT_KIND_AGENT_TEXT: "agent_text",
        dialogue_pb.DIALOGUE_EVENT_KIND_TTS_TEXT: "tts_text",
        dialogue_pb.DIALOGUE_EVENT_KIND_APPROVAL_REQUESTED: "approval_requested",
        dialogue_pb.DIALOGUE_EVENT_KIND_USER_INPUT_REQUESTED: "user_input_requested",
        dialogue_pb.DIALOGUE_EVENT_KIND_MCP_ELICITATION_REQUESTED: "mcp_elicitation_requested",
        dialogue_pb.DIALOGUE_EVENT_KIND_TOOL_EVENT: "tool_event",
        dialogue_pb.DIALOGUE_EVENT_KIND_CANCELLED: "cancelled",
        dialogue_pb.DIALOGUE_EVENT_KIND_ERROR: "error",
    }
    if kind not in mapping:
        raise DoraDialogueMetadataError(f"Unsupported protobuf dialogue event kind: {kind}")
    return mapping[kind]


def _agent_turn_done_status_to_proto(status: str) -> int:
    mapping = {
        "completed": dialogue_pb.AGENT_TURN_DONE_STATUS_COMPLETED,
        "cancelled": dialogue_pb.AGENT_TURN_DONE_STATUS_CANCELLED,
        "failed": dialogue_pb.AGENT_TURN_DONE_STATUS_FAILED,
    }
    if status not in mapping:
        raise DoraDialogueMetadataError(f"Unsupported agent turn done status: {status!r}")
    return mapping[status]


def _agent_turn_done_status_from_proto(status: int) -> str:
    mapping = {
        dialogue_pb.AGENT_TURN_DONE_STATUS_COMPLETED: "completed",
        dialogue_pb.AGENT_TURN_DONE_STATUS_CANCELLED: "cancelled",
        dialogue_pb.AGENT_TURN_DONE_STATUS_FAILED: "failed",
    }
    if status not in mapping:
        raise DoraDialogueMetadataError(
            f"Unsupported protobuf agent turn done status: {status}"
        )
    return mapping[status]


def _approval_decision_to_proto(decision: str) -> int:
    mapping = {
        "accept": dialogue_pb.AGENT_APPROVAL_DECISION_ACCEPT,
        "decline": dialogue_pb.AGENT_APPROVAL_DECISION_DECLINE,
        "cancel": dialogue_pb.AGENT_APPROVAL_DECISION_CANCEL,
    }
    if decision not in mapping:
        raise DoraDialogueMetadataError(f"Unsupported approval decision: {decision!r}")
    return mapping[decision]


def _approval_decision_from_proto(decision: int) -> str:
    mapping = {
        dialogue_pb.AGENT_APPROVAL_DECISION_ACCEPT: "accept",
        dialogue_pb.AGENT_APPROVAL_DECISION_DECLINE: "decline",
        dialogue_pb.AGENT_APPROVAL_DECISION_CANCEL: "cancel",
    }
    if decision not in mapping:
        raise DoraDialogueMetadataError(f"Unsupported protobuf approval decision: {decision}")
    return mapping[decision]


def _approval_scope_to_proto(scope: str) -> int:
    mapping = {
        "turn": dialogue_pb.AGENT_APPROVAL_SCOPE_TURN,
        "session": dialogue_pb.AGENT_APPROVAL_SCOPE_SESSION,
    }
    if scope not in mapping:
        raise DoraDialogueMetadataError(f"Unsupported approval scope: {scope!r}")
    return mapping[scope]


def _approval_scope_from_proto(scope: int) -> str:
    mapping = {
        dialogue_pb.AGENT_APPROVAL_SCOPE_TURN: "turn",
        dialogue_pb.AGENT_APPROVAL_SCOPE_SESSION: "session",
    }
    if scope not in mapping:
        raise DoraDialogueMetadataError(f"Unsupported protobuf approval scope: {scope}")
    return mapping[scope]


def _tool_event_kind_to_proto(kind: str) -> int:
    mapping = {
        "started": dialogue_pb.AGENT_TOOL_EVENT_KIND_STARTED,
        "completed": dialogue_pb.AGENT_TOOL_EVENT_KIND_COMPLETED,
        "failed": dialogue_pb.AGENT_TOOL_EVENT_KIND_FAILED,
    }
    if kind not in mapping:
        raise DoraDialogueMetadataError(f"Unsupported tool event kind: {kind!r}")
    return mapping[kind]


def _tool_event_kind_from_proto(kind: int) -> str:
    mapping = {
        dialogue_pb.AGENT_TOOL_EVENT_KIND_STARTED: "started",
        dialogue_pb.AGENT_TOOL_EVENT_KIND_COMPLETED: "completed",
        dialogue_pb.AGENT_TOOL_EVENT_KIND_FAILED: "failed",
    }
    if kind not in mapping:
        raise DoraDialogueMetadataError(f"Unsupported protobuf tool event kind: {kind}")
    return mapping[kind]


def _mcp_elicitation_mode_to_proto(mode: str) -> int:
    mapping = {
        "form": dialogue_pb.AGENT_MCP_ELICITATION_MODE_FORM,
        "url": dialogue_pb.AGENT_MCP_ELICITATION_MODE_URL,
    }
    if mode not in mapping:
        raise DoraDialogueMetadataError(f"Unsupported MCP elicitation mode: {mode!r}")
    return mapping[mode]


def _mcp_elicitation_mode_from_proto(mode: int) -> str:
    mapping = {
        dialogue_pb.AGENT_MCP_ELICITATION_MODE_FORM: "form",
        dialogue_pb.AGENT_MCP_ELICITATION_MODE_URL: "url",
    }
    if mode not in mapping:
        raise DoraDialogueMetadataError(f"Unsupported protobuf MCP elicitation mode: {mode}")
    return mapping[mode]


def _mcp_elicitation_action_to_proto(action: str) -> int:
    mapping = {
        "accept": dialogue_pb.AGENT_MCP_ELICITATION_ACTION_ACCEPT,
        "decline": dialogue_pb.AGENT_MCP_ELICITATION_ACTION_DECLINE,
        "cancel": dialogue_pb.AGENT_MCP_ELICITATION_ACTION_CANCEL,
    }
    if action not in mapping:
        raise DoraDialogueMetadataError(f"Unsupported MCP elicitation action: {action!r}")
    return mapping[action]


def _mcp_elicitation_action_from_proto(action: int) -> str:
    mapping = {
        dialogue_pb.AGENT_MCP_ELICITATION_ACTION_ACCEPT: "accept",
        dialogue_pb.AGENT_MCP_ELICITATION_ACTION_DECLINE: "decline",
        dialogue_pb.AGENT_MCP_ELICITATION_ACTION_CANCEL: "cancel",
    }
    if action not in mapping:
        raise DoraDialogueMetadataError(
            f"Unsupported protobuf MCP elicitation action: {action}"
        )
    return mapping[action]
