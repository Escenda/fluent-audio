"""Streaming ASR control contracts."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NonEmptyString = Annotated[str, StringConstraints(min_length=1)]
AsrControlKind = Literal["start", "stop", "cancel"]


class AsrStart(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    action: Literal["start"]
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    start_sample_index: int = Field(ge=0)


class AsrStop(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    action: Literal["stop"]
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    stop_sample_index: int = Field(ge=0)


class AsrCancel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    action: Literal["cancel"]
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    reason: NonEmptyString


AsrControl = Annotated[AsrStart | AsrStop | AsrCancel, Field(discriminator="action")]
