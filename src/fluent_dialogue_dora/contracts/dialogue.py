"""Dialogue surface and agent event contracts."""

from typing import Annotated, Literal, TypeAlias

from typing_extensions import TypeAliasType

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonEmptyString = Annotated[str, StringConstraints(min_length=1)]
JsonPrimitive: TypeAlias = str | int | float | bool | None
JsonValue = TypeAliasType(
    "JsonValue",
    JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"],
)
DialogueInputKind = Literal["transcript_final", "cancel", "playback_done"]
DialogueEventKind = Literal[
    "agent_text",
    "tts_text",
    "approval_requested",
    "user_input_requested",
    "mcp_elicitation_requested",
    "tool_event",
    "cancelled",
    "error",
]
AgentToolEventKind = Literal["started", "completed", "failed"]
AgentTurnDoneStatus = Literal["completed", "cancelled", "failed"]
AgentApprovalDecision = Literal["accept", "decline", "cancel"]
AgentApprovalScope = Literal["turn", "session"]
AgentMcpElicitationMode = Literal["form", "url"]
AgentMcpElicitationAction = Literal["accept", "decline", "cancel"]


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
        if self.event in (
            "approval_requested",
            "user_input_requested",
            "mcp_elicitation_requested",
            "tool_event",
            "cancelled",
        ) and (self.text is not None or self.message is not None):
            raise ValueError(f"DialogueEvent {self.event} must not carry text or message")
        return self


class AgentUserInputOption(BaseModel):
    """Selectable option for an agent runtime user-input question."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    label: NonEmptyString
    description: NonEmptyString


class AgentUserInputQuestion(BaseModel):
    """One question emitted by an agent tool while a turn is in progress."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: NonEmptyString
    header: NonEmptyString
    question: NonEmptyString
    is_other: bool = False
    is_secret: bool = False
    options: tuple[AgentUserInputOption, ...] | None = Field(default=None, min_length=1)


class AgentUserInputRequest(BaseModel):
    """Voice-surface request for structured user input required by a tool."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    request_id: NonEmptyString
    seq: int = Field(ge=0)
    questions: tuple[AgentUserInputQuestion, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_question_ids(self) -> "AgentUserInputRequest":
        question_ids = tuple(question.id for question in self.questions)
        if len(set(question_ids)) != len(question_ids):
            raise ValueError("AgentUserInputRequest question ids must be unique")
        return self


class AgentUserInputAnswer(BaseModel):
    """Answer to one agent user-input question."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    question_id: NonEmptyString
    answers: tuple[NonEmptyString, ...] = Field(min_length=1)


class AgentUserInputResponse(BaseModel):
    """Voice-surface response to an agent user-input request."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    request_id: NonEmptyString
    seq: int = Field(ge=0)
    answers: tuple[AgentUserInputAnswer, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_answer_question_ids(self) -> "AgentUserInputResponse":
        question_ids = tuple(answer.question_id for answer in self.answers)
        if len(set(question_ids)) != len(question_ids):
            raise ValueError("AgentUserInputResponse answer question ids must be unique")
        return self


class AgentMcpElicitationRequest(BaseModel):
    """Voice-surface request for MCP elicitation raised during an agent turn."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    request_id: NonEmptyString
    seq: int = Field(ge=0)
    server_name: NonEmptyString
    mode: AgentMcpElicitationMode
    message: NonEmptyString
    url: NonEmptyString | None = None
    elicitation_id: NonEmptyString | None = None
    requested_schema: JsonValue | None = None
    meta: JsonValue | None = None

    @model_validator(mode="after")
    def validate_mode_payload(self) -> "AgentMcpElicitationRequest":
        if self.mode == "url":
            if self.url is None or self.elicitation_id is None:
                raise ValueError("AgentMcpElicitationRequest url mode requires url and elicitation_id")
            if self.requested_schema is not None:
                raise ValueError("AgentMcpElicitationRequest url mode must not carry requested_schema")
        if self.mode == "form":
            if self.requested_schema is None:
                raise ValueError("AgentMcpElicitationRequest form mode requires requested_schema")
            if self.url is not None or self.elicitation_id is not None:
                raise ValueError(
                    "AgentMcpElicitationRequest form mode must not carry url or elicitation_id"
                )
        return self


class AgentMcpElicitationResponse(BaseModel):
    """Voice-surface response to an MCP elicitation request."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    request_id: NonEmptyString
    seq: int = Field(ge=0)
    action: AgentMcpElicitationAction
    content: JsonValue | None = None
    meta: JsonValue | None = None

    @model_validator(mode="after")
    def validate_action_payload(self) -> "AgentMcpElicitationResponse":
        if self.action != "accept" and self.content is not None:
            raise ValueError("MCP elicitation decline/cancel responses must not carry content")
        return self


class AgentTextDelta(BaseModel):
    """Streaming text emitted by the agent runtime."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    agent_turn_id: NonEmptyString
    seq: int = Field(ge=0)
    text: NonEmptyString


class AgentTurnRequest(BaseModel):
    """One finalized user transcript sent from the voice surface to the agent runtime."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    assistant_turn_id: NonEmptyString
    seq: int = Field(ge=0)
    text: NonEmptyString


class AgentTurnDone(BaseModel):
    """Terminal agent turn event consumed by the voice surface."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    agent_turn_id: NonEmptyString
    seq: int = Field(ge=0)
    status: AgentTurnDoneStatus
    message: NonEmptyString | None = None

    @model_validator(mode="after")
    def validate_variant_payload(self) -> "AgentTurnDone":
        if self.status == "failed" and self.message is None:
            raise ValueError("AgentTurnDone failed requires message")
        if self.status == "completed" and self.message is not None:
            raise ValueError("AgentTurnDone completed must not carry message")
        return self


class AgentApprovalRequest(BaseModel):
    """Voice-surface approval request for a potentially unsafe agent action."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    approval_id: NonEmptyString
    seq: int = Field(ge=0)
    prompt: NonEmptyString
    action_label: NonEmptyString


class AgentApprovalResponse(BaseModel):
    """Voice-surface response to a pending agent approval request."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    approval_id: NonEmptyString
    seq: int = Field(ge=0)
    decision: AgentApprovalDecision
    scope: AgentApprovalScope = "turn"
    reason: NonEmptyString | None = None

    @model_validator(mode="after")
    def validate_variant_payload(self) -> "AgentApprovalResponse":
        if self.decision != "accept" and self.scope != "turn":
            raise ValueError("AgentApprovalResponse scope=session is only valid for accept")
        return self


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
    heard_text: NonEmptyString | None = None
