"""Voice activity and turn boundary contracts."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NonEmptyString = Annotated[str, StringConstraints(min_length=1)]
VoiceActivityState = Literal["silence", "speech"]
TurnState = Literal["idle", "started", "active", "ended", "cancelled"]


class VoiceActivityEvent(BaseModel):
    """Backend-neutral VAD output for one audio span."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    source_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    sample_index: int = Field(ge=0)
    frame_count: int = Field(gt=0)
    state: VoiceActivityState
    speech_probability: float = Field(ge=0.0, le=1.0)


class TurnEvent(BaseModel):
    """Turn boundary signal derived from activity and ASR context."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    sample_index: int = Field(ge=0)
    state: TurnState
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
