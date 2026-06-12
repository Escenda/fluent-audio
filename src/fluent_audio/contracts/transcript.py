"""Streaming transcript contracts."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonEmptyString = Annotated[str, StringConstraints(min_length=1)]


class TranscriptDelta(BaseModel):
    """Incremental ASR transcript for a user turn."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    text: NonEmptyString


class TranscriptPartial(BaseModel):
    """Replacement ASR hypothesis for a user turn."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    text: NonEmptyString


class TranscriptFinal(BaseModel):
    """Final ASR transcript for a bounded user audio span."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    text: NonEmptyString
    start_sample_index: int = Field(ge=0)
    end_sample_index: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_sample_range(self) -> "TranscriptFinal":
        if self.end_sample_index <= self.start_sample_index:
            raise ValueError(
                "TranscriptFinal end_sample_index must be greater than start_sample_index"
            )
        return self
