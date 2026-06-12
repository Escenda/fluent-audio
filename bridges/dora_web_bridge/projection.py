"""Web dashboard projection models for the DORA live topic bridge."""

from __future__ import annotations

from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from fluent_audio.contracts import (
    AgentApprovalRequest,
    AgentMcpElicitationRequest,
    AgentTextDelta,
    AgentToolEvent,
    AgentTurnDone,
    AgentUserInputRequest,
    AsrControl,
    AudioLevelEvent,
    DialogueEvent,
    PlaybackDone,
    PlaybackState,
    TranscriptDelta,
    TranscriptFinal,
    TranscriptPartial,
    TtsTextChunk,
    TurnEvent,
    VoiceActivityEvent,
    VoiceSessionEvent,
)

NonEmptyString = Annotated[str, StringConstraints(min_length=1)]


class WebBridgeProjectionError(ValueError):
    """Raised when a Web projection cannot preserve a fluent-audio contract."""


class WebSessionStateEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_type: Literal["session_state"] = "session_state"
    session_id: NonEmptyString
    seq: int = Field(ge=0)
    created_at_ns: int = Field(ge=0)
    event: Literal[
        "session_started",
        "state_changed",
        "user_turn_started",
        "user_turn_finalized",
        "assistant_turn_started",
        "assistant_turn_completed",
        "session_closed",
        "error",
    ]
    state: Literal[
        "idle",
        "listening",
        "user_speaking",
        "transcribing",
        "thinking",
        "speaking",
        "interrupted",
        "closed",
        "error",
    ]
    user_turn_id: NonEmptyString | None = None
    assistant_turn_id: NonEmptyString | None = None
    message: NonEmptyString | None = None

    @model_validator(mode="after")
    def validate_variant_payload(self) -> "WebSessionStateEvent":
        if self.event == "error" and self.message is None:
            raise ValueError("WebSessionStateEvent error requires message")
        return self


class WebAudioActivityEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_type: Literal["audio_activity"] = "audio_activity"
    source_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    created_at_ns: int = Field(ge=0)
    sample_index: int = Field(ge=0)
    frame_count: int = Field(gt=0)
    state: Literal["silence", "speech"]
    speech_probability: float = Field(ge=0.0, le=1.0)
    session_id: NonEmptyString


class WebAudioLevelEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_type: Literal["audio_level"] = "audio_level"
    source_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    created_at_ns: int = Field(ge=0)
    sample_index: int = Field(ge=0)
    frame_count: int = Field(gt=0)
    rms_dbfs: float = Field(le=0.0)
    peak_dbfs: float = Field(le=0.0)
    speech_probability: float = Field(ge=0.0, le=1.0)
    session_id: NonEmptyString


class WebTurnEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_type: Literal["turn"] = "turn"
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    created_at_ns: int = Field(ge=0)
    sample_index: int = Field(ge=0)
    state: Literal["idle", "started", "active", "ended", "cancelled"]
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class WebAsrControlEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_type: Literal["asr_control"] = "asr_control"
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    created_at_ns: int = Field(ge=0)
    action: Literal["start", "stop", "cancel"]
    start_sample_index: int | None = Field(default=None, ge=0)
    stop_sample_index: int | None = Field(default=None, ge=0)
    reason: NonEmptyString | None = None

    @model_validator(mode="after")
    def validate_variant_payload(self) -> "WebAsrControlEvent":
        if self.action == "start":
            if self.start_sample_index is None:
                raise ValueError("WebAsrControlEvent start requires start_sample_index")
            if self.stop_sample_index is not None or self.reason is not None:
                raise ValueError("WebAsrControlEvent start only accepts start_sample_index")
        if self.action == "stop":
            if self.stop_sample_index is None:
                raise ValueError("WebAsrControlEvent stop requires stop_sample_index")
            if self.start_sample_index is not None or self.reason is not None:
                raise ValueError("WebAsrControlEvent stop only accepts stop_sample_index")
        if self.action == "cancel":
            if self.reason is None:
                raise ValueError("WebAsrControlEvent cancel requires reason")
            if self.start_sample_index is not None or self.stop_sample_index is not None:
                raise ValueError("WebAsrControlEvent cancel only accepts reason")
        return self


class WebTranscriptDeltaEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_type: Literal["transcript_delta"] = "transcript_delta"
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    created_at_ns: int = Field(ge=0)
    text: NonEmptyString


class WebTranscriptPartialEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_type: Literal["transcript_partial"] = "transcript_partial"
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    created_at_ns: int = Field(ge=0)
    text: NonEmptyString


class WebTranscriptFinalEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_type: Literal["transcript_final"] = "transcript_final"
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    created_at_ns: int = Field(ge=0)
    text: NonEmptyString
    start_sample_index: int = Field(ge=0)
    end_sample_index: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_sample_range(self) -> "WebTranscriptFinalEvent":
        if self.end_sample_index <= self.start_sample_index:
            raise ValueError("WebTranscriptFinalEvent requires end_sample_index > start")
        return self


class WebDialogueEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_type: Literal["dialogue_event"] = "dialogue_event"
    event: Literal[
        "agent_text",
        "tts_text",
        "approval_requested",
        "tool_event",
        "cancelled",
        "error",
    ]
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    seq: int = Field(ge=0)
    created_at_ns: int = Field(ge=0)
    text: NonEmptyString | None = None
    request_id: NonEmptyString | None = None
    message: NonEmptyString | None = None

    @model_validator(mode="after")
    def validate_variant_payload(self) -> "WebDialogueEvent":
        if self.event in ("agent_text", "tts_text") and self.text is None:
            raise ValueError(f"WebDialogueEvent {self.event} requires text")
        if self.event == "error" and self.message is None:
            raise ValueError("WebDialogueEvent error requires message")
        return self


class WebAgentTextDeltaEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_type: Literal["agent_text_delta"] = "agent_text_delta"
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    agent_turn_id: NonEmptyString
    seq: int = Field(ge=0)
    created_at_ns: int = Field(ge=0)
    text: NonEmptyString


class WebAgentTurnDoneEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_type: Literal["agent_turn_done"] = "agent_turn_done"
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    agent_turn_id: NonEmptyString
    seq: int = Field(ge=0)
    created_at_ns: int = Field(ge=0)
    status: Literal["completed", "cancelled", "failed"]
    message: NonEmptyString | None = None

    @model_validator(mode="after")
    def validate_message(self) -> "WebAgentTurnDoneEvent":
        if self.status == "failed" and self.message is None:
            raise ValueError("WebAgentTurnDoneEvent failed requires message")
        if self.status == "completed" and self.message is not None:
            raise ValueError("WebAgentTurnDoneEvent completed must not carry message")
        return self


class WebTtsTextEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_type: Literal["tts_text"] = "tts_text"
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    request_id: NonEmptyString
    assistant_turn_id: NonEmptyString
    seq: int = Field(ge=0)
    created_at_ns: int = Field(ge=0)
    text: NonEmptyString
    is_final: bool


class WebApprovalRequestEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_type: Literal["approval_request"] = "approval_request"
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    approval_id: NonEmptyString
    seq: int = Field(ge=0)
    created_at_ns: int = Field(ge=0)
    prompt: NonEmptyString
    action_label: NonEmptyString


class WebAgentUserInputRequestEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_type: Literal["agent_user_input_request"] = "agent_user_input_request"
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    request_id: NonEmptyString
    seq: int = Field(ge=0)
    created_at_ns: int = Field(ge=0)
    questions: tuple[NonEmptyString, ...] = Field(min_length=1)


class WebAgentMcpElicitationRequestEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_type: Literal["agent_mcp_elicitation_request"] = "agent_mcp_elicitation_request"
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    request_id: NonEmptyString
    seq: int = Field(ge=0)
    created_at_ns: int = Field(ge=0)
    server_name: NonEmptyString
    mode: Literal["form", "url"]
    message: NonEmptyString
    url: NonEmptyString | None = None


class WebToolEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_type: Literal["tool_event"] = "tool_event"
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    tool_call_id: NonEmptyString
    tool_name: NonEmptyString
    event: Literal["started", "completed", "failed"]
    seq: int = Field(ge=0)
    created_at_ns: int = Field(ge=0)
    summary: NonEmptyString | None = None
    error_message: NonEmptyString | None = None

    @model_validator(mode="after")
    def validate_error_message(self) -> "WebToolEvent":
        if self.event == "failed" and self.error_message is None:
            raise ValueError("WebToolEvent failed requires error_message")
        if self.event != "failed" and self.error_message is not None:
            raise ValueError("WebToolEvent error_message is only valid for failed events")
        return self


class WebPlaybackStateEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_type: Literal["playback_state"] = "playback_state"
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    request_id: NonEmptyString
    stream_id: NonEmptyString
    state: Literal["queued", "playing", "paused", "stopped", "completed", "cancelled", "failed"]
    seq: int = Field(ge=0)
    created_at_ns: int = Field(ge=0)
    played_frames: int = Field(ge=0)
    reason: NonEmptyString | None = None

    @model_validator(mode="after")
    def validate_reason(self) -> "WebPlaybackStateEvent":
        if self.state == "failed" and self.reason is None:
            raise ValueError("WebPlaybackStateEvent failed requires reason")
        if self.state != "failed" and self.reason is not None:
            raise ValueError("WebPlaybackStateEvent reason is only valid for failed state")
        return self


class WebPlaybackDoneEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_type: Literal["playback_done"] = "playback_done"
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    request_id: NonEmptyString
    stream_id: NonEmptyString
    status: Literal["completed", "stopped", "cancelled", "failed"]
    created_at_ns: int = Field(ge=0)
    final_sequence: int | None = Field(default=None, ge=0)
    total_frames: int | None = Field(default=None, ge=0)
    reason: NonEmptyString | None = None

    @model_validator(mode="after")
    def validate_done_fields(self) -> "WebPlaybackDoneEvent":
        if self.final_sequence is None and self.total_frames is None:
            raise ValueError("WebPlaybackDoneEvent requires final_sequence or total_frames")
        if self.status == "failed" and self.reason is None:
            raise ValueError("WebPlaybackDoneEvent failed requires reason")
        if self.status != "failed" and self.reason is not None:
            raise ValueError("WebPlaybackDoneEvent reason is only valid for failed status")
        return self


WebBridgeProjection: TypeAlias = Annotated[
    WebSessionStateEvent
    | WebAudioActivityEvent
    | WebAudioLevelEvent
    | WebTurnEvent
    | WebAsrControlEvent
    | WebTranscriptDeltaEvent
    | WebTranscriptPartialEvent
    | WebTranscriptFinalEvent
    | WebDialogueEvent
    | WebAgentTextDeltaEvent
    | WebAgentTurnDoneEvent
    | WebTtsTextEvent
    | WebApprovalRequestEvent
    | WebAgentUserInputRequestEvent
    | WebAgentMcpElicitationRequestEvent
    | WebToolEvent
    | WebPlaybackStateEvent
    | WebPlaybackDoneEvent,
    Field(discriminator="event_type"),
]


def voice_session_event_to_web(
    event: VoiceSessionEvent,
    *,
    created_at_ns: int,
) -> WebSessionStateEvent:
    return WebSessionStateEvent(
        session_id=event.turn_ids.session_id,
        user_turn_id=event.turn_ids.user_turn_id,
        seq=event.seq,
        created_at_ns=created_at_ns,
        event=event.event,
        state=event.state,
        assistant_turn_id=event.turn_ids.assistant_turn_id,
        message=event.message,
    )


def voice_activity_to_web(
    event: VoiceActivityEvent,
    *,
    session_id: str,
    created_at_ns: int,
) -> WebAudioActivityEvent:
    return WebAudioActivityEvent(
        source_id=event.source_id,
        stream_id=event.stream_id,
        seq=event.seq,
        created_at_ns=created_at_ns,
        sample_index=event.sample_index,
        frame_count=event.frame_count,
        state=event.state,
        speech_probability=event.speech_probability,
        session_id=session_id,
    )


def audio_level_to_web(
    event: AudioLevelEvent,
    *,
    session_id: str,
    created_at_ns: int,
) -> WebAudioLevelEvent:
    return WebAudioLevelEvent(
        source_id=event.source_id,
        stream_id=event.stream_id,
        seq=event.seq,
        created_at_ns=created_at_ns,
        sample_index=event.sample_index,
        frame_count=event.frame_count,
        rms_dbfs=event.rms_dbfs,
        peak_dbfs=event.peak_dbfs,
        speech_probability=event.speech_probability,
        session_id=session_id,
    )


def turn_event_to_web(
    event: TurnEvent,
    *,
    created_at_ns: int,
) -> WebTurnEvent:
    return WebTurnEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        stream_id=event.stream_id,
        seq=event.seq,
        created_at_ns=created_at_ns,
        sample_index=event.sample_index,
        state=event.state,
        confidence=event.confidence,
    )


def asr_control_to_web(
    event: AsrControl,
    *,
    created_at_ns: int,
) -> WebAsrControlEvent:
    if event.action == "start":
        return WebAsrControlEvent(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            stream_id=event.stream_id,
            seq=event.seq,
            created_at_ns=created_at_ns,
            action="start",
            start_sample_index=event.start_sample_index,
        )
    if event.action == "stop":
        return WebAsrControlEvent(
            session_id=event.session_id,
            user_turn_id=event.user_turn_id,
            stream_id=event.stream_id,
            seq=event.seq,
            created_at_ns=created_at_ns,
            action="stop",
            stop_sample_index=event.stop_sample_index,
        )
    return WebAsrControlEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        stream_id=event.stream_id,
        seq=event.seq,
        created_at_ns=created_at_ns,
        action="cancel",
        reason=event.reason,
    )


def transcript_delta_to_web(
    event: TranscriptDelta,
    *,
    created_at_ns: int,
) -> WebTranscriptDeltaEvent:
    return WebTranscriptDeltaEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        stream_id=event.stream_id,
        seq=event.seq,
        created_at_ns=created_at_ns,
        text=event.text,
    )


def transcript_partial_to_web(
    event: TranscriptPartial,
    *,
    created_at_ns: int,
) -> WebTranscriptPartialEvent:
    return WebTranscriptPartialEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        stream_id=event.stream_id,
        seq=event.seq,
        created_at_ns=created_at_ns,
        text=event.text,
    )


def transcript_final_to_web(
    event: TranscriptFinal,
    *,
    created_at_ns: int,
) -> WebTranscriptFinalEvent:
    return WebTranscriptFinalEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        stream_id=event.stream_id,
        seq=event.seq,
        created_at_ns=created_at_ns,
        text=event.text,
        start_sample_index=event.start_sample_index,
        end_sample_index=event.end_sample_index,
    )


def dialogue_event_to_web(
    event: DialogueEvent,
    *,
    created_at_ns: int,
) -> WebDialogueEvent:
    return WebDialogueEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        seq=event.seq,
        created_at_ns=created_at_ns,
        event=event.event,
        text=event.text,
        request_id=event.request_id,
        message=event.message,
    )


def agent_text_delta_to_web(
    event: AgentTextDelta,
    *,
    created_at_ns: int,
) -> WebAgentTextDeltaEvent:
    return WebAgentTextDeltaEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        agent_turn_id=event.agent_turn_id,
        seq=event.seq,
        created_at_ns=created_at_ns,
        text=event.text,
    )


def agent_turn_done_to_web(
    event: AgentTurnDone,
    *,
    created_at_ns: int,
) -> WebAgentTurnDoneEvent:
    return WebAgentTurnDoneEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        agent_turn_id=event.agent_turn_id,
        seq=event.seq,
        created_at_ns=created_at_ns,
        status=event.status,
        message=event.message,
    )


def tts_text_chunk_to_web(
    event: TtsTextChunk,
    *,
    created_at_ns: int,
) -> WebTtsTextEvent:
    return WebTtsTextEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        request_id=event.request_id,
        assistant_turn_id=event.assistant_turn_id,
        seq=event.seq,
        created_at_ns=created_at_ns,
        text=event.text,
        is_final=event.is_final,
    )


def agent_approval_request_to_web(
    event: AgentApprovalRequest,
    *,
    created_at_ns: int,
) -> WebApprovalRequestEvent:
    return WebApprovalRequestEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        approval_id=event.approval_id,
        seq=event.seq,
        created_at_ns=created_at_ns,
        prompt=event.prompt,
        action_label=event.action_label,
    )


def agent_user_input_request_to_web(
    event: AgentUserInputRequest,
    *,
    created_at_ns: int,
) -> WebAgentUserInputRequestEvent:
    return WebAgentUserInputRequestEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        request_id=event.request_id,
        seq=event.seq,
        created_at_ns=created_at_ns,
        questions=tuple(question.question for question in event.questions),
    )


def agent_mcp_elicitation_request_to_web(
    event: AgentMcpElicitationRequest,
    *,
    created_at_ns: int,
) -> WebAgentMcpElicitationRequestEvent:
    return WebAgentMcpElicitationRequestEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        request_id=event.request_id,
        seq=event.seq,
        created_at_ns=created_at_ns,
        server_name=event.server_name,
        mode=event.mode,
        message=event.message,
        url=event.url,
    )


def agent_tool_event_to_web(
    event: AgentToolEvent,
    *,
    created_at_ns: int,
) -> WebToolEvent:
    return WebToolEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        tool_call_id=event.tool_call_id,
        tool_name=event.tool_name,
        event=event.event,
        seq=event.seq,
        created_at_ns=created_at_ns,
        summary=event.summary,
        error_message=event.error_message,
    )


def playback_state_to_web(
    event: PlaybackState,
    *,
    created_at_ns: int,
) -> WebPlaybackStateEvent:
    return WebPlaybackStateEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        request_id=event.request_id,
        stream_id=event.stream_id,
        state=event.state,
        seq=event.seq,
        created_at_ns=created_at_ns,
        played_frames=event.played_frames,
        reason=event.reason,
    )


def playback_done_to_web(
    event: PlaybackDone,
    *,
    created_at_ns: int,
) -> WebPlaybackDoneEvent:
    return WebPlaybackDoneEvent(
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        request_id=event.request_id,
        stream_id=event.stream_id,
        status=event.status,
        created_at_ns=created_at_ns,
        final_sequence=event.final_sequence,
        total_frames=event.total_frames,
        reason=event.reason,
    )
