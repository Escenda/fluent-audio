"""Playback control contracts."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonEmptyString = Annotated[str, StringConstraints(min_length=1)]
PlaybackCommandKind = Literal["stop", "pause", "resume", "clear"]
PlaybackControlKind = Literal["flush"]
PlaybackDoneStatus = Literal["completed", "stopped", "cancelled", "failed"]
PlaybackStateKind = Literal["queued", "playing", "paused", "stopped", "completed", "cancelled", "failed"]


class PlaybackStop(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    command: Literal["stop"]
    request_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)


class PlaybackPause(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    command: Literal["pause"]
    request_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)


class PlaybackResume(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    command: Literal["resume"]
    request_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)


class PlaybackClear(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    command: Literal["clear"]
    request_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)


PlaybackCommand = Annotated[
    PlaybackStop | PlaybackPause | PlaybackResume | PlaybackClear,
    Field(discriminator="command"),
]


class PlaybackControlFlush(BaseModel):
    """Device-level flush for the speaker sink: drop buffered audio and fade out.

    Unlike PlaybackCommand this has no request_id; it acts on whatever is buffered
    in the sink, so a barge-in can clear the downstream tail.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    kind: Literal["flush"]
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    fade_out_ms: int = Field(ge=0)


class PlaybackDone(BaseModel):
    """Terminal playback report for a queued playback request."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    request_id: NonEmptyString
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    stream_id: NonEmptyString
    status: PlaybackDoneStatus
    final_sequence: int | None = Field(default=None, ge=0)
    total_frames: int | None = Field(default=None, ge=0)
    reason: NonEmptyString | None = None

    @model_validator(mode="after")
    def validate_completion_position(self) -> "PlaybackDone":
        if self.final_sequence is None and self.total_frames is None:
            raise ValueError("PlaybackDone requires final_sequence or total_frames")
        if self.status == "failed" and self.reason is None:
            raise ValueError("PlaybackDone with status='failed' requires reason")
        if self.status != "failed" and self.reason is not None:
            raise ValueError("PlaybackDone reason is only valid for status='failed'")
        return self


class PlaybackState(BaseModel):
    """Observable playback state for queue and speaker coordination."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    request_id: NonEmptyString
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    stream_id: NonEmptyString
    state: PlaybackStateKind
    seq: int = Field(ge=0)
    played_frames: int = Field(ge=0)
    reason: NonEmptyString | None = None

    @model_validator(mode="after")
    def validate_state_reason(self) -> "PlaybackState":
        if self.state == "failed" and self.reason is None:
            raise ValueError("PlaybackState failed requires reason")
        if self.state != "failed" and self.reason is not None:
            raise ValueError("PlaybackState reason is only valid for failed state")
        return self
