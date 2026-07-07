"""Decode configured fluent-dialogue-dora DORA inputs into Web bridge events."""
# ruff: noqa: E402

from __future__ import annotations

import sys
import time
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fluent_dialogue_dora.dora import (
    DoraAsrControlFinalMarkerError,
    DoraBargeInFinalMarkerError,
    decode_agent_approval_request_from_dora,
    decode_agent_mcp_elicitation_request_from_dora,
    decode_agent_text_delta_from_dora,
    decode_agent_tool_event_from_dora,
    decode_agent_turn_done_from_dora,
    decode_agent_user_input_request_from_dora,
    decode_asr_control_from_dora,
    decode_audio_level_event_from_dora,
    decode_barge_in_event_from_dora,
    decode_dialogue_event_from_dora,
    decode_playback_done_from_dora,
    decode_playback_state_from_dora,
    decode_transcript_delta_from_dora,
    decode_transcript_final_from_dora,
    decode_transcript_partial_from_dora,
    decode_turn_event_from_dora,
    decode_tts_text_chunk_from_dora,
    decode_voice_session_event_from_dora,
    decode_voice_activity_event_from_dora,
    validate_dora_agent_approval_metadata,
    validate_dora_agent_mcp_elicitation_request_metadata,
    validate_dora_agent_text_metadata,
    validate_dora_agent_tool_metadata,
    validate_dora_agent_turn_done_metadata,
    validate_dora_agent_user_input_request_metadata,
    validate_dora_asr_control_final_marker,
    validate_dora_asr_control_metadata,
    validate_dora_audio_level_metadata,
    validate_dora_barge_in_final_marker,
    validate_dora_barge_in_metadata,
    validate_dora_dialogue_event_metadata,
    validate_dora_playback_done_metadata,
    validate_dora_playback_state_metadata,
    validate_dora_transcript_metadata,
    validate_dora_transcript_stream_final_marker,
    validate_dora_turn_final_marker,
    validate_dora_turn_metadata,
    validate_dora_tts_text_metadata,
    validate_dora_tts_text_stream_final_marker,
    validate_dora_voice_session_metadata,
    validate_dora_voice_activity_final_marker,
    validate_dora_voice_activity_metadata,
)
from bridges.dora_web_bridge.messages import WEB_BRIDGE_INPUT_IDS, WebBridgeInputId
from bridges.dora_web_bridge.projection import (
    WebBridgeProjection,
    agent_approval_request_to_web,
    agent_mcp_elicitation_request_to_web,
    agent_text_delta_to_web,
    agent_tool_event_to_web,
    agent_turn_done_to_web,
    agent_user_input_request_to_web,
    asr_control_to_web,
    audio_level_to_web,
    barge_in_event_to_web,
    dialogue_event_to_web,
    playback_done_to_web,
    playback_state_to_web,
    transcript_delta_to_web,
    transcript_final_to_web,
    transcript_partial_to_web,
    turn_event_to_web,
    tts_text_chunk_to_web,
    voice_session_event_to_web,
    voice_activity_to_web,
)


class DoraWebBridgeDecodeError(ValueError):
    """Raised when a DORA input cannot be decoded for Web transport."""


class DoraWebBridgeDecodeConfig(BaseModel):
    """Stable decode context that is not part of the DORA payload."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: str = Field(min_length=1)


def decode_dora_input_for_web_bridge(
    input_id: WebBridgeInputId,
    event,
    config: DoraWebBridgeDecodeConfig,
) -> WebBridgeProjection | None:
    """Decode one DORA INPUT event into a typed Web projection.

    A return value of ``None`` means the input was an explicit final marker, not
    a Web-visible live topic event.
    """

    payload = event.get("value")
    metadata = event.get("metadata")
    created_at_ns = time.time_ns()
    if input_id == "activity":
        activity_metadata = validate_dora_voice_activity_metadata(metadata)
        if activity_metadata.final:
            validate_dora_voice_activity_final_marker(payload, activity_metadata)
            return None
        return voice_activity_to_web(
            decode_voice_activity_event_from_dora(payload, activity_metadata),
            session_id=config.session_id,
            created_at_ns=created_at_ns,
        )
    if input_id == "meter":
        level_metadata = validate_dora_audio_level_metadata(metadata)
        return audio_level_to_web(
            decode_audio_level_event_from_dora(payload, level_metadata),
            session_id=config.session_id,
            created_at_ns=created_at_ns,
        )
    if input_id == "turn":
        turn_metadata = validate_dora_turn_metadata(metadata)
        if turn_metadata.final:
            validate_dora_turn_final_marker(payload, turn_metadata)
            return None
        return turn_event_to_web(
            decode_turn_event_from_dora(payload, turn_metadata),
            created_at_ns=created_at_ns,
        )
    if input_id == "asr_control":
        asr_control_metadata = validate_dora_asr_control_metadata(metadata)
        try:
            control = decode_asr_control_from_dora(payload, asr_control_metadata)
        except DoraAsrControlFinalMarkerError:
            validate_dora_asr_control_final_marker(payload, asr_control_metadata)
            return None
        return asr_control_to_web(control, created_at_ns=created_at_ns)
    if input_id == "transcript":
        transcript_metadata = validate_dora_transcript_metadata(metadata)
        if transcript_metadata.kind == "stream_final":
            validate_dora_transcript_stream_final_marker(payload, transcript_metadata)
            return None
        if transcript_metadata.kind == "delta":
            return transcript_delta_to_web(
                decode_transcript_delta_from_dora(payload, transcript_metadata),
                created_at_ns=created_at_ns,
            )
        if transcript_metadata.kind == "partial":
            return transcript_partial_to_web(
                decode_transcript_partial_from_dora(payload, transcript_metadata),
                created_at_ns=created_at_ns,
            )
        return transcript_final_to_web(
            decode_transcript_final_from_dora(payload, transcript_metadata),
            created_at_ns=created_at_ns,
        )
    if input_id == "session":
        session_metadata = validate_dora_voice_session_metadata(metadata)
        return voice_session_event_to_web(
            decode_voice_session_event_from_dora(payload, session_metadata),
            created_at_ns=created_at_ns,
        )
    if input_id == "dialogue":
        dialogue_metadata = validate_dora_dialogue_event_metadata(metadata)
        return dialogue_event_to_web(
            decode_dialogue_event_from_dora(payload, dialogue_metadata),
            created_at_ns=created_at_ns,
        )
    if input_id == "agent_text":
        agent_text_metadata = validate_dora_agent_text_metadata(metadata)
        return agent_text_delta_to_web(
            decode_agent_text_delta_from_dora(payload, agent_text_metadata),
            created_at_ns=created_at_ns,
        )
    if input_id == "agent_done":
        agent_done_metadata = validate_dora_agent_turn_done_metadata(metadata)
        return agent_turn_done_to_web(
            decode_agent_turn_done_from_dora(payload, agent_done_metadata),
            created_at_ns=created_at_ns,
        )
    if input_id == "agent_approval":
        approval_metadata = validate_dora_agent_approval_metadata(metadata)
        return agent_approval_request_to_web(
            decode_agent_approval_request_from_dora(payload, approval_metadata),
            created_at_ns=created_at_ns,
        )
    if input_id == "agent_user_input":
        user_input_metadata = validate_dora_agent_user_input_request_metadata(metadata)
        return agent_user_input_request_to_web(
            decode_agent_user_input_request_from_dora(payload, user_input_metadata),
            created_at_ns=created_at_ns,
        )
    if input_id == "agent_mcp_elicitation":
        elicitation_metadata = validate_dora_agent_mcp_elicitation_request_metadata(metadata)
        return agent_mcp_elicitation_request_to_web(
            decode_agent_mcp_elicitation_request_from_dora(payload, elicitation_metadata),
            created_at_ns=created_at_ns,
        )
    if input_id == "agent_tool":
        tool_metadata = validate_dora_agent_tool_metadata(metadata)
        return agent_tool_event_to_web(
            decode_agent_tool_event_from_dora(payload, tool_metadata),
            created_at_ns=created_at_ns,
        )
    if input_id == "tts":
        tts_metadata = validate_dora_tts_text_metadata(metadata)
        if tts_metadata.kind == "stream_final":
            validate_dora_tts_text_stream_final_marker(payload, tts_metadata)
            return None
        return tts_text_chunk_to_web(
            decode_tts_text_chunk_from_dora(payload, tts_metadata),
            created_at_ns=created_at_ns,
        )
    if input_id == "barge_in":
        barge_in_metadata = validate_dora_barge_in_metadata(metadata)
        try:
            event = decode_barge_in_event_from_dora(payload, barge_in_metadata)
        except DoraBargeInFinalMarkerError:
            validate_dora_barge_in_final_marker(payload, barge_in_metadata)
            return None
        return barge_in_event_to_web(event, created_at_ns=created_at_ns)
    if input_id == "playback_state":
        playback_metadata = validate_dora_playback_state_metadata(metadata)
        return playback_state_to_web(
            decode_playback_state_from_dora(payload, playback_metadata),
            created_at_ns=created_at_ns,
        )
    if input_id == "playback_done":
        playback_metadata = validate_dora_playback_done_metadata(metadata)
        return playback_done_to_web(
            decode_playback_done_from_dora(payload, playback_metadata),
            created_at_ns=created_at_ns,
        )
    raise DoraWebBridgeDecodeError(f"Unsupported DORA input id: {input_id!r}")


def input_id_from_dora_event(event) -> WebBridgeInputId:
    """Read and validate the DORA input id."""

    raw = required_event_text(event, "id")
    if raw in WEB_BRIDGE_INPUT_IDS:
        return raw
    raise DoraWebBridgeDecodeError(f"Unexpected DORA input id: {raw!r}")


def required_event_text(event, key: str) -> str:
    """Read a required text field from a DORA event mapping."""

    value = event.get(key)
    if not isinstance(value, str):
        raise DoraWebBridgeDecodeError(f"DORA event field {key!r} must be a string")
    return value
