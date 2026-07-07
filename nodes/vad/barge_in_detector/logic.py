"""Pure barge-in detection state machine.

Detects the start of sustained user speech while the agent is actively playing
back synthesized speech. It is a signal-only concern: it emits a BargeInEvent
and lets the dialogue engine decide how to react (stop playback, cancel, etc.).
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from fluent_dialogue_dora.contracts import BargeInEvent, PlaybackState, VoiceActivityEvent

NonEmptyString = Annotated[str, StringConstraints(min_length=1)]

# Playback states that mean the agent is no longer actively producing speaker
# audio, so a barge-in window should disarm.
_NON_PLAYING_STATES = frozenset(
    {"queued", "paused", "stopped", "completed", "cancelled", "failed"}
)


class BargeInDetectorError(ValueError):
    """Raised when the barge-in detector receives an invalid event sequence."""


class BargeInDetectorConfig(BaseModel):
    """Configuration for pure barge-in detection."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    source_id: NonEmptyString
    output_stream_id: NonEmptyString
    # Sustained speech (in 16 kHz frames) required before declaring a barge-in.
    barge_in_speech_frames: int = Field(default=4800, gt=0)
    # Contiguous silence (in 16 kHz frames) that resets an in-progress speech run.
    silence_reset_frames: int = Field(default=2048, gt=0)
    min_speech_probability: float = Field(default=0.5, ge=0.0, le=1.0)


class BargeInDetectorState:
    """Stateful barge-in detection for one session.

    Armed only while the agent is playing (learned from PlaybackState). Fires at
    most once per playback request; a new request re-arms it.
    """

    def __init__(self, config: BargeInDetectorConfig) -> None:
        self._config = config
        self._next_output_seq = 0
        self._playing = False
        self._active_request_id: str | None = None
        self._active_playback_stream_id: str | None = None
        self._last_played_frames = 0
        self._speech_run_frames = 0
        self._silence_run_frames = 0
        self._fired_request_id: str | None = None

    def on_playback_state(self, state: PlaybackState) -> None:
        """Track whether the agent is actively playing and which request."""

        if state.state == "playing":
            if state.request_id != self._active_request_id:
                # A new request started playing: re-arm.
                self._active_request_id = state.request_id
                self._active_playback_stream_id = state.stream_id
                self._reset_run()
                if self._fired_request_id != state.request_id:
                    self._fired_request_id = None
            self._active_playback_stream_id = state.stream_id
            self._last_played_frames = state.played_frames
            self._playing = True
            return
        if state.state in _NON_PLAYING_STATES:
            # Agent stopped/paused producing audio for this request: disarm.
            if state.request_id == self._active_request_id:
                self._playing = False
                self._reset_run()
            return
        raise BargeInDetectorError(f"Unsupported playback state: {state.state!r}")

    def on_activity(self, event: VoiceActivityEvent) -> list[BargeInEvent]:
        """Accumulate speech while armed; emit a barge-in once the threshold trips."""

        if not self._playing or self._active_request_id is None:
            return []
        if self._fired_request_id == self._active_request_id:
            return []

        if event.state == "speech":
            if event.speech_probability < self._config.min_speech_probability:
                return []
            self._silence_run_frames = 0
            self._speech_run_frames += event.frame_count
            if self._speech_run_frames >= self._config.barge_in_speech_frames:
                return [self._fire(event)]
            return []

        if event.state == "silence":
            self._silence_run_frames += event.frame_count
            if self._silence_run_frames >= self._config.silence_reset_frames:
                self._speech_run_frames = 0
            return []

        raise BargeInDetectorError(f"Unsupported voice activity state: {event.state!r}")

    def _fire(self, event: VoiceActivityEvent) -> BargeInEvent:
        if self._active_request_id is None or self._active_playback_stream_id is None:
            raise BargeInDetectorError("cannot fire barge-in without an active playback request")
        barge_in = BargeInEvent(
            session_id=self._config.session_id,
            source_id=self._config.source_id,
            stream_id=self._config.output_stream_id,
            seq=self._next_output_seq,
            playback_request_id=self._active_request_id,
            playback_stream_id=self._active_playback_stream_id,
            played_frames=self._last_played_frames,
            detected_sample_index=event.sample_index + event.frame_count,
            speech_probability=event.speech_probability,
        )
        self._next_output_seq += 1
        self._fired_request_id = self._active_request_id
        self._playing = False
        self._reset_run()
        return barge_in

    def _reset_run(self) -> None:
        self._speech_run_frames = 0
        self._silence_run_frames = 0

    @property
    def next_output_seq(self) -> int:
        return self._next_output_seq
