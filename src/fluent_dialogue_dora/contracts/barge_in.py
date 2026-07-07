"""Barge-in (user interruption) signal contracts."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NonEmptyString = Annotated[str, StringConstraints(min_length=1)]


class BargeInEvent(BaseModel):
    """Sustained user speech detected while the agent is actively speaking.

    Emitted by the barge_in_detector as a pure signal. The dialogue engine
    decides how to act (stop playback, cancel the turn, truncate context).
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    source_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    playback_request_id: NonEmptyString
    playback_stream_id: NonEmptyString
    played_frames: int = Field(ge=0)
    detected_sample_index: int = Field(ge=0)
    speech_probability: float = Field(ge=0.0, le=1.0)


class BargeInStreamFinal(BaseModel):
    """Terminal marker closing one barge-in signal stream."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    source_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
