"""Pure voice-activity to turn-event transition logic."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from fluent_dialogue_dora.contracts import TurnEvent, VoiceActivityEvent

NonEmptyString = Annotated[str, StringConstraints(min_length=1)]


class TurnDetectorError(ValueError):
    """Raised when turn detector logic receives an invalid event sequence."""


class TurnDetectorConfig(BaseModel):
    """Configuration for pure turn detector state transitions."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    output_stream_id: NonEmptyString
    end_silence_frames: int = Field(default=1024, gt=0)
    user_turn_id_prefix: NonEmptyString = "user-turn"


class TurnDetectorState:
    """Stateful transition logic for one contiguous voice-activity stream."""

    def __init__(self, config: TurnDetectorConfig) -> None:
        self._config = config
        self._next_output_seq = 0
        self._next_turn_number = 1
        self._previous_input_seq: int | None = None
        self._previous_input_start_sample_index: int | None = None
        self._previous_input_end_sample_index: int | None = None
        self._active_turn_id: str | None = None
        self._last_speech_end_sample_index: int | None = None
        self._silence_frames = 0

    def push(self, activity_event: VoiceActivityEvent) -> list[TurnEvent]:
        """Push one contiguous activity event and return derived turn events."""

        self._validate_contiguous_input(activity_event)
        self._previous_input_seq = activity_event.seq
        self._previous_input_start_sample_index = activity_event.sample_index
        self._previous_input_end_sample_index = activity_event.sample_index + activity_event.frame_count

        if activity_event.state == "speech":
            return self._push_speech(activity_event)
        return self._push_silence(activity_event)

    def finish(self, final_sample_index: int) -> list[TurnEvent]:
        """Flush an unfinished active turn at stream end."""

        if final_sample_index < 0:
            raise TurnDetectorError("Turn detector final_sample_index must be non-negative")
        if self._previous_input_start_sample_index is not None and (
            final_sample_index <= self._previous_input_start_sample_index
            or (
                self._previous_input_end_sample_index is not None
                and final_sample_index > self._previous_input_end_sample_index
            )
        ):
            raise TurnDetectorError(
                "Turn detector final_sample_index is outside the last activity event span"
            )
        if (
            self._last_speech_end_sample_index is not None
            and self._last_speech_end_sample_index > final_sample_index
        ):
            self._last_speech_end_sample_index = final_sample_index
        if self._active_turn_id is None:
            return []
        return [self._end_active_turn()]

    def _push_speech(self, activity_event: VoiceActivityEvent) -> list[TurnEvent]:
        self._silence_frames = 0
        self._last_speech_end_sample_index = activity_event.sample_index + activity_event.frame_count

        if self._active_turn_id is None:
            self._active_turn_id = self._new_turn_id()
            state = "started"
        else:
            state = "active"

        return [
            self._build_event(
                user_turn_id=self._active_turn_id,
                sample_index=activity_event.sample_index,
                state=state,
            )
        ]

    def _push_silence(self, activity_event: VoiceActivityEvent) -> list[TurnEvent]:
        if self._active_turn_id is None:
            return []

        self._silence_frames += activity_event.frame_count
        if self._silence_frames < self._config.end_silence_frames:
            return []

        return [self._end_active_turn()]

    def _end_active_turn(self) -> TurnEvent:
        if self._active_turn_id is None or self._last_speech_end_sample_index is None:
            raise TurnDetectorError("Turn detector cannot end a turn without speech")

        event = self._build_event(
            user_turn_id=self._active_turn_id,
            sample_index=self._last_speech_end_sample_index,
            state="ended",
        )
        self._active_turn_id = None
        self._last_speech_end_sample_index = None
        self._silence_frames = 0
        return event

    def _build_event(
        self,
        *,
        user_turn_id: str,
        sample_index: int,
        state: str,
    ) -> TurnEvent:
        event = TurnEvent(
            session_id=self._config.session_id,
            user_turn_id=user_turn_id,
            stream_id=self._config.output_stream_id,
            seq=self._next_output_seq,
            sample_index=sample_index,
            state=state,
        )
        self._next_output_seq += 1
        return event

    def _new_turn_id(self) -> str:
        user_turn_id = f"{self._config.user_turn_id_prefix}-{self._next_turn_number:06d}"
        self._next_turn_number += 1
        return user_turn_id

    def _validate_contiguous_input(self, activity_event: VoiceActivityEvent) -> None:
        if self._previous_input_seq is None or self._previous_input_end_sample_index is None:
            return

        expected_seq = self._previous_input_seq + 1
        if activity_event.seq != expected_seq:
            raise TurnDetectorError(
                f"Turn detector input seq discontinuity: "
                f"expected {expected_seq}, got {activity_event.seq}"
            )

        if activity_event.sample_index != self._previous_input_end_sample_index:
            raise TurnDetectorError(
                "Turn detector input sample_index discontinuity: "
                f"expected {self._previous_input_end_sample_index}, "
                f"got {activity_event.sample_index}"
            )
