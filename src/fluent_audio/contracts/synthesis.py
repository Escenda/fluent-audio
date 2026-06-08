"""Speech synthesis contracts."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from fluent_audio.contracts.audio import AudioChunk

NonEmptyString = Annotated[str, StringConstraints(min_length=1)]


class TtsTextChunk(BaseModel):
    """Text chunk ready for speech synthesis."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    request_id: NonEmptyString
    session_id: NonEmptyString
    assistant_turn_id: NonEmptyString
    seq: int = Field(ge=0)
    text: NonEmptyString
    is_final: bool


class SynthesizedAudioChunk(BaseModel):
    """Synthesized speech audio tied back to one TTS request."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    request_id: NonEmptyString
    session_id: NonEmptyString
    assistant_turn_id: NonEmptyString
    seq: int = Field(ge=0)
    audio: AudioChunk
