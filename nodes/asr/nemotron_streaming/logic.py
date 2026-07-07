"""Session and prebuffer logic for the Nemotron streaming ASR node."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from fluent_dialogue_dora.contracts import (
    AsrCancel,
    AsrStart,
    AsrStop,
    AudioChunk,
    AudioChunkContinuityError,
    AudioFormat,
    TranscriptFinal,
    TranscriptPartial,
    require_contiguous_audio_chunks,
)

NonEmptyString = Annotated[str, StringConstraints(min_length=1)]


class NemotronStreamingError(ValueError):
    """Raised when streaming ASR session state or input contracts are invalid."""


class AsrBackendPushResult(BaseModel):
    """Text emitted by the ASR backend after receiving one audio span."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    partial_texts: tuple[NonEmptyString, ...] = ()


class AsrBackendFinalResult(BaseModel):
    """Final text emitted by the ASR backend after a stop command.

    Empty text means the backend consumed the bounded turn audio but did not
    recognize a user utterance. The runtime treats that as an explicit no-op
    turn and does not emit an external TranscriptFinal.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    text: str


class StreamingAsrBackend(ABC):
    """Streaming ASR backend interface used by the DORA node."""

    @abstractmethod
    def start(self, control: AsrStart, audio_format: AudioFormat) -> None:
        """Start one user turn."""

    @abstractmethod
    def push_audio(self, chunk: AudioChunk) -> AsrBackendPushResult:
        """Push one contiguous PCM span to the backend."""

    @abstractmethod
    def stop(self, control: AsrStop) -> AsrBackendFinalResult:
        """Finish the active user turn and return final text."""

    @abstractmethod
    def cancel(self, control: AsrCancel) -> None:
        """Cancel the active user turn."""


class NemotronStreamingConfig(BaseModel):
    """Configuration for ASR stream orchestration around the backend."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    input_audio_source_id: NonEmptyString
    input_audio_stream_id: NonEmptyString
    output_stream_id: NonEmptyString
    expected_audio_format: AudioFormat = Field(
        default_factory=lambda: AudioFormat(
            sample_rate_hz=16_000,
            channels=1,
            sample_format="s16le",
            channel_layout="interleaved",
        )
    )
    prebuffer_frames: int = Field(default=16_000, gt=0)
    control_holdback_frames: int = Field(default=4_096, ge=0)
    late_stop_tolerance_frames: int = Field(default=16_000, ge=0)


class ActiveAsrTurn(BaseModel):
    """State for the active ASR user turn."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    start_sample_index: int = Field(ge=0)
    next_sample_index: int = Field(ge=0)
    pending_stop: AsrStop | None = None


class AudioHistoryBuffer:
    """Bounded contiguous audio history used to replay ASR prebuffer."""

    def __init__(self, max_frames: int) -> None:
        if max_frames <= 0:
            raise NemotronStreamingError("Audio history max_frames must be > 0")
        self._max_frames = max_frames
        self._chunks: list[AudioChunk] = []

    @property
    def has_audio(self) -> bool:
        return bool(self._chunks)

    @property
    def earliest_sample_index(self) -> int | None:
        if not self._chunks:
            return None
        return self._chunks[0].sample_index

    @property
    def latest_sample_index(self) -> int | None:
        if not self._chunks:
            return None
        return self._chunks[-1].next_sample_index

    def append(self, chunk: AudioChunk) -> None:
        if self._chunks:
            try:
                require_contiguous_audio_chunks(self._chunks[-1], chunk)
            except AudioChunkContinuityError as exc:
                raise NemotronStreamingError("Audio history received non-contiguous audio") from exc
        self._chunks.append(chunk)
        self._prune()

    def span(self, start_sample_index: int, end_sample_index: int) -> list[AudioChunk]:
        if start_sample_index < 0:
            raise NemotronStreamingError("Audio span start_sample_index must be >= 0")
        if end_sample_index < start_sample_index:
            raise NemotronStreamingError(
                "Audio span end_sample_index must be >= start_sample_index"
            )
        if start_sample_index == end_sample_index:
            return []
        if not self._chunks:
            raise NemotronStreamingError("Audio history is empty")

        earliest = self._chunks[0].sample_index
        latest = self._chunks[-1].next_sample_index
        if start_sample_index < earliest:
            raise NemotronStreamingError(
                "ASR start_sample_index is older than retained prebuffer: "
                f"start={start_sample_index}, earliest={earliest}"
            )
        if end_sample_index > latest:
            raise NemotronStreamingError(
                "Requested audio span extends beyond received audio: "
                f"end={end_sample_index}, latest={latest}"
            )

        spans: list[AudioChunk] = []
        next_sample_index = start_sample_index
        for chunk in self._chunks:
            if chunk.next_sample_index <= start_sample_index:
                continue
            if chunk.sample_index >= end_sample_index:
                break
            sliced = slice_audio_chunk(
                chunk,
                start_sample_index=max(start_sample_index, chunk.sample_index),
                end_sample_index=min(end_sample_index, chunk.next_sample_index),
            )
            if sliced.sample_index != next_sample_index:
                raise NemotronStreamingError(
                    f"Audio history span is not contiguous at sample_index {next_sample_index}"
                )
            next_sample_index = sliced.next_sample_index
            spans.append(sliced)

        if next_sample_index != end_sample_index:
            raise NemotronStreamingError(
                "Audio history span ended before requested end_sample_index"
            )
        return spans

    def _prune(self) -> None:
        latest = self.latest_sample_index
        if latest is None:
            return
        min_sample_index = max(0, latest - self._max_frames)
        while len(self._chunks) > 1 and self._chunks[0].next_sample_index <= min_sample_index:
            self._chunks.pop(0)


class NemotronStreamingRuntime:
    """Coordinates DORA audio/control inputs with one streaming ASR backend."""

    def __init__(
        self,
        config: NemotronStreamingConfig,
        backend: StreamingAsrBackend,
    ) -> None:
        self._config = config
        self._backend = backend
        self._history = AudioHistoryBuffer(
            max_frames=config.prebuffer_frames + config.control_holdback_frames
        )
        self._active_turn: ActiveAsrTurn | None = None
        self._pending_controls: list[AsrStart | AsrStop | AsrCancel] = []
        self._previous_audio_chunk: AudioChunk | None = None
        self._expected_control_seq = 0
        self._next_transcript_seq = 0

    @property
    def active_turn(self) -> ActiveAsrTurn | None:
        return self._active_turn

    @property
    def next_transcript_seq(self) -> int:
        return self._next_transcript_seq

    @property
    def latest_audio_sample_index(self) -> int | None:
        return self._history.latest_sample_index

    def push_audio(
        self,
        chunk: AudioChunk,
    ) -> list[TranscriptFinal | TranscriptPartial]:
        self._validate_audio_chunk_identity_and_format(chunk)
        self._handle_audio_continuity(chunk)
        self._history.append(chunk)
        self._previous_audio_chunk = chunk
        if self._active_turn is None:
            return []
        return self._push_available_active_audio()

    def push_control(
        self,
        control: AsrStart | AsrStop | AsrCancel,
    ) -> list[TranscriptFinal | TranscriptPartial]:
        self._validate_control(control)
        if self._should_queue_control(control):
            self._pending_controls.append(control)
            return []
        transcript_events = self._apply_control(control)
        if self._active_turn is None:
            transcript_events.extend(self._drain_pending_controls())
        return transcript_events

    def _apply_control(
        self,
        control: AsrStart | AsrStop | AsrCancel,
    ) -> list[TranscriptFinal | TranscriptPartial]:
        if isinstance(control, AsrStart):
            return self._start_turn(control)
        if isinstance(control, AsrStop):
            return self._stop_turn(control)
        return self._cancel_turn(control)

    def _should_queue_control(self, control: AsrStart | AsrStop | AsrCancel) -> bool:
        if self._pending_controls:
            return True
        active_turn = self._active_turn
        if active_turn is None or active_turn.pending_stop is None:
            return False
        if (
            isinstance(control, AsrCancel)
            and control.session_id == active_turn.session_id
            and control.user_turn_id == active_turn.user_turn_id
        ):
            return False
        return True

    def _drain_pending_controls(
        self,
    ) -> list[TranscriptFinal | TranscriptPartial]:
        transcript_events: list[TranscriptFinal | TranscriptPartial] = []
        while self._pending_controls:
            next_control = self._pending_controls[0]
            if self._active_turn is not None and isinstance(next_control, AsrStart):
                break
            self._pending_controls.pop(0)
            transcript_events.extend(self._apply_control(next_control))
        return transcript_events

    def finish_audio(self, final_sample_index: int) -> None:
        latest_sample_index = self._history.latest_sample_index
        if latest_sample_index is None:
            raise NemotronStreamingError("ASR audio stream finished before audio chunks")
        if final_sample_index != latest_sample_index:
            raise NemotronStreamingError(
                "ASR audio final sample_index does not match received audio: "
                f"final={final_sample_index}, latest={latest_sample_index}"
            )
        if self._active_turn is not None:
            raise NemotronStreamingError("ASR audio stream finished while a turn is still active")
        if self._pending_controls:
            raise NemotronStreamingError(
                "ASR audio stream finished while controls are still pending"
            )

    def _start_turn(self, control: AsrStart) -> list[TranscriptPartial]:
        if self._active_turn is not None:
            raise NemotronStreamingError("ASR start received while another turn is active")

        self._backend.start(control, self._config.expected_audio_format)
        self._active_turn = ActiveAsrTurn(
            session_id=control.session_id,
            user_turn_id=control.user_turn_id,
            start_sample_index=control.start_sample_index,
            next_sample_index=control.start_sample_index,
        )

        latest_sample_index = self._history.latest_sample_index
        if latest_sample_index is None:
            return []
        earliest_sample_index = self._history.earliest_sample_index
        if earliest_sample_index is not None and control.start_sample_index < earliest_sample_index:
            raise NemotronStreamingError(
                "ASR start_sample_index is older than retained prebuffer: "
                f"start={control.start_sample_index}, earliest={earliest_sample_index}"
            )

        return self._push_available_active_audio()

    def _stop_turn(
        self,
        control: AsrStop,
    ) -> list[TranscriptFinal | TranscriptPartial]:
        active_turn = self._require_active_turn(control.session_id, control.user_turn_id)
        if active_turn.pending_stop is not None:
            raise NemotronStreamingError("ASR stop received while another stop is pending")
        if control.stop_sample_index < active_turn.start_sample_index:
            raise NemotronStreamingError(
                "ASR stop_sample_index must be after turn start_sample_index"
            )
        if control.stop_sample_index == active_turn.start_sample_index:
            raise NemotronStreamingError(
                "ASR stop_sample_index must be after turn start_sample_index"
            )
        if control.stop_sample_index < active_turn.next_sample_index:
            overshoot_frames = active_turn.next_sample_index - control.stop_sample_index
            if overshoot_frames > self._config.late_stop_tolerance_frames:
                raise NemotronStreamingError(
                    "ASR stop_sample_index is behind audio already pushed to backend: "
                    f"stop={control.stop_sample_index}, pushed={active_turn.next_sample_index}, "
                    f"overshoot={overshoot_frames}, "
                    f"tolerance={self._config.late_stop_tolerance_frames}"
                )
            adjusted_control = control.model_copy(
                update={"stop_sample_index": active_turn.next_sample_index}
            )
            final_event = self._finalize_active_turn(adjusted_control)
            if final_event is None:
                return []
            return [final_event]
        if control.stop_sample_index == active_turn.next_sample_index:
            final_event = self._finalize_active_turn(control)
            if final_event is None:
                return []
            return [final_event]

        latest_sample_index = self._history.latest_sample_index
        if latest_sample_index is not None and control.stop_sample_index <= latest_sample_index:
            replay_chunks = self._history.span(
                active_turn.next_sample_index,
                control.stop_sample_index,
            )
            transcript_events: list[TranscriptFinal | TranscriptPartial] = []
            for chunk in replay_chunks:
                transcript_events.extend(self._push_backend_audio(chunk))
            final_event = self._finalize_active_turn(control)
            if final_event is not None:
                transcript_events.append(final_event)
            return transcript_events

        self._active_turn = active_turn.model_copy(update={"pending_stop": control})
        return []

    def _cancel_turn(
        self,
        control: AsrCancel,
    ) -> list[TranscriptFinal | TranscriptPartial]:
        self._require_active_turn(control.session_id, control.user_turn_id)
        self._backend.cancel(control)
        self._active_turn = None
        return []

    def _push_available_active_audio(
        self,
    ) -> list[TranscriptFinal | TranscriptPartial]:
        active_turn = self._active_turn
        if active_turn is None:
            return []

        latest_sample_index = self._history.latest_sample_index
        if latest_sample_index is None:
            return []

        if active_turn.pending_stop is not None:
            target_end_sample_index = min(
                latest_sample_index,
                active_turn.pending_stop.stop_sample_index,
            )
        else:
            target_end_sample_index = max(
                0,
                latest_sample_index - self._config.control_holdback_frames,
            )
        if target_end_sample_index <= active_turn.next_sample_index:
            return []

        transcript_events: list[TranscriptFinal | TranscriptPartial] = []
        chunks_to_push = self._history.span(
            active_turn.next_sample_index,
            target_end_sample_index,
        )
        for chunk in chunks_to_push:
            transcript_events.extend(self._push_backend_audio(chunk))

        active_turn = self._active_turn
        if active_turn is not None and active_turn.pending_stop is not None:
            if active_turn.next_sample_index == active_turn.pending_stop.stop_sample_index:
                final_event = self._finalize_active_turn(active_turn.pending_stop)
                if final_event is not None:
                    transcript_events.append(final_event)
                transcript_events.extend(self._drain_pending_controls())
        return transcript_events

    def _push_backend_audio(self, chunk: AudioChunk) -> list[TranscriptPartial]:
        active_turn = self._active_turn
        if active_turn is None:
            raise NemotronStreamingError("Cannot push ASR audio without active turn")
        result = self._backend.push_audio(chunk)
        self._active_turn = active_turn.model_copy(
            update={"next_sample_index": chunk.next_sample_index}
        )
        transcript_events: list[TranscriptPartial] = []
        for text in result.partial_texts:
            transcript_events.append(
                TranscriptPartial(
                    session_id=active_turn.session_id,
                    user_turn_id=active_turn.user_turn_id,
                    stream_id=self._config.output_stream_id,
                    seq=self._next_transcript_seq,
                    text=text,
                )
            )
            self._next_transcript_seq += 1
        return transcript_events

    def _finalize_active_turn(self, control: AsrStop) -> TranscriptFinal | None:
        active_turn = self._require_active_turn(control.session_id, control.user_turn_id)
        final_result = self._backend.stop(control)
        self._active_turn = None
        if not final_result.text.strip():
            return None
        final_event = TranscriptFinal(
            session_id=active_turn.session_id,
            user_turn_id=active_turn.user_turn_id,
            stream_id=self._config.output_stream_id,
            seq=self._next_transcript_seq,
            text=final_result.text,
            start_sample_index=active_turn.start_sample_index,
            end_sample_index=control.stop_sample_index,
        )
        self._next_transcript_seq += 1
        return final_event

    def _require_active_turn(
        self,
        session_id: str,
        user_turn_id: str,
    ) -> ActiveAsrTurn:
        if self._active_turn is None:
            raise NemotronStreamingError("ASR control received without active turn")
        if self._active_turn.session_id != session_id:
            raise NemotronStreamingError(
                "ASR control session mismatch: "
                f"expected {self._active_turn.session_id!r}, got {session_id!r}"
            )
        if self._active_turn.user_turn_id != user_turn_id:
            raise NemotronStreamingError(
                "ASR control user_turn_id mismatch: "
                f"expected {self._active_turn.user_turn_id!r}, got {user_turn_id!r}"
            )
        return self._active_turn

    def _validate_audio_chunk_identity_and_format(self, chunk: AudioChunk) -> None:
        if chunk.source_id != self._config.input_audio_source_id:
            raise NemotronStreamingError(
                "ASR audio source mismatch: "
                f"expected {self._config.input_audio_source_id!r}, got {chunk.source_id!r}"
            )
        if chunk.stream_id != self._config.input_audio_stream_id:
            raise NemotronStreamingError(
                "ASR audio stream mismatch: "
                f"expected {self._config.input_audio_stream_id!r}, got {chunk.stream_id!r}"
            )
        if chunk.format != self._config.expected_audio_format:
            raise NemotronStreamingError(
                "ASR audio format mismatch: "
                f"expected {self._config.expected_audio_format!r}, got {chunk.format!r}"
            )

    def _handle_audio_continuity(self, chunk: AudioChunk) -> None:
        if self._previous_audio_chunk is not None:
            try:
                require_contiguous_audio_chunks(self._previous_audio_chunk, chunk)
            except AudioChunkContinuityError as exc:
                if self._active_turn is None:
                    self._history = AudioHistoryBuffer(
                        max_frames=(
                            self._config.prebuffer_frames + self._config.control_holdback_frames
                        )
                    )
                    self._previous_audio_chunk = None
                    return
                raise NemotronStreamingError("ASR audio discontinuity") from exc

    def _validate_control(self, control: AsrStart | AsrStop | AsrCancel) -> None:
        if control.stream_id != self._config.input_audio_stream_id:
            raise NemotronStreamingError(
                "ASR control stream mismatch: "
                f"expected {self._config.input_audio_stream_id!r}, got {control.stream_id!r}"
            )
        if control.seq != self._expected_control_seq:
            raise NemotronStreamingError(
                "ASR control seq discontinuity: "
                f"expected {self._expected_control_seq}, got {control.seq}"
            )
        self._expected_control_seq += 1


def slice_audio_chunk(
    chunk: AudioChunk,
    *,
    start_sample_index: int,
    end_sample_index: int,
) -> AudioChunk:
    """Return the chunk subspan covering ``[start_sample_index, end_sample_index)``."""

    if start_sample_index < chunk.sample_index:
        raise NemotronStreamingError("Cannot slice audio before chunk start")
    if end_sample_index > chunk.next_sample_index:
        raise NemotronStreamingError("Cannot slice audio after chunk end")
    if end_sample_index <= start_sample_index:
        raise NemotronStreamingError("Audio slice must contain at least one frame")

    frame_offset = start_sample_index - chunk.sample_index
    frame_count = end_sample_index - start_sample_index
    frame_size_bytes = chunk.format.frame_size_bytes
    byte_start = frame_offset * frame_size_bytes
    byte_end = byte_start + frame_count * frame_size_bytes
    capture_time_ns = (
        chunk.capture_time_ns + (frame_offset * 1_000_000_000) // chunk.format.sample_rate_hz
    )
    return AudioChunk(
        source_id=chunk.source_id,
        stream_id=chunk.stream_id,
        seq=chunk.seq,
        sample_index=start_sample_index,
        capture_time_ns=capture_time_ns,
        frame_count=frame_count,
        format=chunk.format,
        payload=chunk.payload[byte_start:byte_end],
    )
