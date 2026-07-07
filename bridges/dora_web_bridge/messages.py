"""Typed HTTP models for the DORA-to-Web live topic bridge."""

from __future__ import annotations

from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, model_validator

from bridges.dora_web_bridge.projection import WebBridgeProjection


WebTrackTopic = Literal[
    "session/state",
    "audio/level",
    "vad/activity",
    "vad/turn",
    "asr/control",
    "asr/transcript",
    "dialogue/event",
    "agent/text",
    "agent/done",
    "agent/approval",
    "agent/user-input",
    "agent/mcp-elicitation",
    "agent/tool",
    "tts/text",
    "barge-in/event",
    "playback/state",
    "playback/done",
]
FinalMarkerInputId = Literal["activity", "turn", "transcript"]
OpenStreamInputId = Literal[
    "meter",
    "asr_control",
    "session",
    "dialogue",
    "agent_text",
    "agent_done",
    "agent_approval",
    "agent_user_input",
    "agent_mcp_elicitation",
    "agent_tool",
    "tts",
    "barge_in",
    "playback_state",
    "playback_done",
]
WebBridgeInputId = FinalMarkerInputId | OpenStreamInputId

FINAL_MARKER_INPUT_IDS: tuple[FinalMarkerInputId, ...] = ("activity", "turn", "transcript")
OPEN_STREAM_INPUT_IDS: tuple[OpenStreamInputId, ...] = (
    "meter",
    "asr_control",
    "session",
    "dialogue",
    "agent_text",
    "agent_done",
    "agent_approval",
    "agent_user_input",
    "agent_mcp_elicitation",
    "agent_tool",
    "tts",
    "barge_in",
    "playback_state",
    "playback_done",
)
WEB_BRIDGE_INPUT_IDS: tuple[WebBridgeInputId, ...] = (
    *FINAL_MARKER_INPUT_IDS,
    *OPEN_STREAM_INPUT_IDS,
)

ApprovalResponsePathParts: TypeAlias = tuple[str, str, str]


class DoraWebBridgeTopicEvent(BaseModel):
    """One decoded DORA input event exposed through the bridge transport."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    global_offset: int = Field(ge=0)
    topic_offset: int = Field(ge=0)
    topic: str = Field(min_length=1)
    input_id: WebBridgeInputId
    event: WebBridgeProjection


class DoraWebBridgeTrackFrame(BaseModel):
    """Latest typed frame for one dashboard track."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    topic: WebTrackTopic
    global_offset: int = Field(ge=0)
    event: WebBridgeProjection


class DoraWebBridgeTrackSnapshotResponse(BaseModel):
    """Current latest frame per dashboard track."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    tracks: tuple[DoraWebBridgeTrackFrame, ...]


class WebApprovalResponseSubmission(BaseModel):
    """Browser payload submitted to the Codex control REST plane."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    decision: Literal["accept", "decline", "cancel"]
    scope: Literal["turn", "session"] = "turn"
    reason: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_decision_scope(self) -> "WebApprovalResponseSubmission":
        if self.decision != "accept" and self.scope != "turn":
            raise ValueError("scope=session is only valid for accept")
        return self


class DoraWebBridgeTopicSummary(BaseModel):
    """Small listing row for one configured DORA input topic."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    topic: str = Field(min_length=1)
    input_id: WebBridgeInputId
    event_count: int = Field(ge=0)
    latest_event_type: str | None = None
    last_seen_ns: int | None = Field(default=None, ge=0)


class DoraWebBridgeTopicListResponse(BaseModel):
    """Response listing currently configured bridge topics."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    topics: tuple[DoraWebBridgeTopicSummary, ...]


class DoraWebBridgeTopicSnapshotResponse(BaseModel):
    """Recent event snapshot for one DORA input topic."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    topic: str = Field(min_length=1)
    input_id: WebBridgeInputId
    event_count: int = Field(ge=0)
    events: tuple[DoraWebBridgeTopicEvent, ...]


class DoraWebBridgeLatestResponse(BaseModel):
    """Latest event for one topic, when the topic has emitted at least once."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    topic: str = Field(min_length=1)
    input_id: WebBridgeInputId
    event_count: int = Field(ge=0)
    event: DoraWebBridgeTopicEvent | None = None


class DoraWebBridgeGlobalSnapshotResponse(BaseModel):
    """Recent global stream snapshot for all selected topics."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_count: int = Field(ge=0)
    events: tuple[DoraWebBridgeTopicEvent, ...]
