"""Dialogue surface and agent event contracts."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonEmptyString = Annotated[str, StringConstraints(min_length=1)]
DialogueInputKind = Literal["transcript_final", "cancel", "playback_done"]
DialogueEventKind = Literal["agent_text", "tts_text", "approval_requested", "tool_event", "cancelled", "error"]
AgentToolEventKind = Literal["started", "completed", "failed"]


class DialogueInput(BaseModel):
    """Input event consumed by the dialogue engine voice surface."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    input_type: DialogueInputKind
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    seq: int = Field(ge=0)
    text: NonEmptyString | None = None
    request_id: NonEmptyString | None = None

    @model_validator(mode="after")
    def validate_variant_payload(self) -> "DialogueInput":
        if self.input_type == "transcript_final" and self.text is None:
            raise ValueError("DialogueInput transcript_final requires text")
        if self.input_type == "playback_done" and self.request_id is None:
            raise ValueError("DialogueInput playback_done requires request_id")
        if self.input_type == "cancel" and (self.text is not None or self.request_id is not None):
            raise ValueError("DialogueInput cancel must not carry text or request_id")
        return self


class DialogueEvent(BaseModel):
    """Output event emitted by the dialogue engine voice surface."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event: DialogueEventKind
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    seq: int = Field(ge=0)
    text: NonEmptyString | None = None
    request_id: NonEmptyString | None = None
    message: NonEmptyString | None = None

    @model_validator(mode="after")
    def validate_variant_payload(self) -> "DialogueEvent":
        if self.event in ("agent_text", "tts_text") and self.text is None:
            raise ValueError(f"DialogueEvent {self.event} requires text")
        if self.event == "error" and self.message is None:
            raise ValueError("DialogueEvent error requires message")
        return self


class AgentTextDelta(BaseModel):
    """Streaming text emitted by the agent runtime."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    agent_turn_id: NonEmptyString
    seq: int = Field(ge=0)
    text: NonEmptyString


class AgentApprovalRequest(BaseModel):
    """Voice-surface approval request for a potentially unsafe agent action."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    approval_id: NonEmptyString
    seq: int = Field(ge=0)
    prompt: NonEmptyString
    action_label: NonEmptyString


class AgentToolEvent(BaseModel):
    """Tool execution state projected from the agent runtime."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    tool_call_id: NonEmptyString
    tool_name: NonEmptyString
    event: AgentToolEventKind
    seq: int = Field(ge=0)
    summary: NonEmptyString | None = None
    error_message: NonEmptyString | None = None

    @model_validator(mode="after")
    def validate_variant_payload(self) -> "AgentToolEvent":
        if self.event == "failed" and self.error_message is None:
            raise ValueError("AgentToolEvent failed requires error_message")
        if self.event != "failed" and self.error_message is not None:
            raise ValueError("AgentToolEvent error_message is only valid for failed events")
        return self


class AgentCancelRequest(BaseModel):
    """Cancellation request sent from voice interaction to the agent runtime."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    seq: int = Field(ge=0)
    reason: NonEmptyString | None = None
