"""Voice session correlation contracts."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NonEmptyString = Annotated[str, StringConstraints(min_length=1)]
VoiceSessionState = Literal[
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
VoiceSessionEventKind = Literal[
    "session_started",
    "state_changed",
    "user_turn_started",
    "user_turn_finalized",
    "assistant_turn_started",
    "assistant_turn_completed",
    "session_closed",
    "error",
]


class TurnIds(BaseModel):
    """Identifiers that correlate user and assistant work inside one voice session."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    assistant_turn_id: NonEmptyString | None = None


class VoiceSessionEvent(BaseModel):
    """Session state transition emitted by the dialogue surface."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event: VoiceSessionEventKind
    state: VoiceSessionState
    seq: int = Field(ge=0)
    turn_ids: TurnIds
    message: NonEmptyString | None = None
