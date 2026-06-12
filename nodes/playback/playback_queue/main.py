"""DORA node for synthesized-audio playback queueing.

This node owns the boundary between synthesized speech audio and the downstream
speaker audio path. It does not synthesize audio and it does not talk to CPAL.
"""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Sequence
from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import TypeAlias

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pydantic import BaseModel, ConfigDict, Field

from fluent_audio.contracts import (
    AudioChunk,
    AudioFormat,
    PlaybackDone,
    PlaybackDoneStatus,
    PlaybackState,
    PlaybackStateKind,
    SynthesizedAudioChunk,
)
from fluent_audio.dora import (
    DoraSynthesizedAudioMetadata,
    decode_playback_command_from_dora,
    decode_synthesized_audio_chunk_from_dora,
    encode_audio_chunk_for_dora,
    encode_audio_final_marker_for_dora,
    encode_playback_done_for_dora,
    encode_playback_state_for_dora,
    validate_dora_playback_command_metadata,
    validate_dora_synthesized_audio_final_marker,
    validate_dora_synthesized_audio_metadata,
)
from fluent_audio.dora.playback import PlaybackCommandEvent

DEFAULT_MAX_QUEUED_AUDIO_CHUNKS = 256
DEFAULT_DORA_OUTPUT_DRAIN_SECONDS = 0.2
DEFAULT_OUTPUT_SOURCE_ID = "playback_queue"
DEFAULT_OUTPUT_STREAM_ID = "speaker/main"


class PlaybackQueueError(ValueError):
    """Raised when playback queue ordering or lifecycle contracts are violated."""


class PlaybackQueueConfig(BaseModel):
    """Runtime configuration for one playback queue node."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    max_queued_audio_chunks: int = Field(default=DEFAULT_MAX_QUEUED_AUDIO_CHUNKS, ge=1)
    output_source_id: str = Field(default=DEFAULT_OUTPUT_SOURCE_ID, min_length=1)
    output_stream_id: str = Field(default=DEFAULT_OUTPUT_STREAM_ID, min_length=1)
    output_drain_seconds: float = Field(default=DEFAULT_DORA_OUTPUT_DRAIN_SECONDS, ge=0.0)


class PlaybackQueueSummary(BaseModel):
    """Validated counters for one playback queue run."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    synthesized_audio_chunks: int = Field(ge=0)
    synthesized_audio_finals: int = Field(ge=0)
    playback_commands: int = Field(ge=0)
    audio_chunks_sent: int = Field(ge=0)
    audio_finals_sent: int = Field(ge=0)
    playback_states: int = Field(ge=0)
    playback_done: int = Field(ge=0)
    stopped_requests: int = Field(ge=0)
    cleared_requests: int = Field(ge=0)
    paused_requests: int = Field(ge=0)
    resumed_requests: int = Field(ge=0)


@dataclass(frozen=True)
class PlaybackQueueAudioOutput:
    audio: AudioChunk


@dataclass(frozen=True)
class PlaybackQueueAudioFinalOutput:
    source_id: str
    stream_id: str
    seq: int
    sample_index: int
    capture_time_ns: int
    audio_format: AudioFormat


@dataclass(frozen=True)
class PlaybackQueueStateOutput:
    state: PlaybackState


@dataclass(frozen=True)
class PlaybackQueueDoneOutput:
    done: PlaybackDone


PlaybackQueueOutputEvent: TypeAlias = (
    PlaybackQueueAudioOutput
    | PlaybackQueueAudioFinalOutput
    | PlaybackQueueStateOutput
    | PlaybackQueueDoneOutput
)


@dataclass(frozen=True)
class PlaybackQueueOutput:
    """Ordered events emitted by a playback queue state transition."""

    events: tuple[PlaybackQueueOutputEvent, ...] = ()

    @property
    def audio_chunk_count(self) -> int:
        return len(
            tuple(event for event in self.events if isinstance(event, PlaybackQueueAudioOutput))
        )

    @property
    def audio_final_count(self) -> int:
        return len(
            tuple(
                event for event in self.events if isinstance(event, PlaybackQueueAudioFinalOutput)
            )
        )

    @property
    def playback_state_count(self) -> int:
        return len(
            tuple(event for event in self.events if isinstance(event, PlaybackQueueStateOutput))
        )

    @property
    def playback_done_count(self) -> int:
        return len(
            tuple(event for event in self.events if isinstance(event, PlaybackQueueDoneOutput))
        )


@dataclass
class ActivePlayback:
    request_id: str
    session_id: str
    user_turn_id: str
    assistant_turn_id: str
    input_audio_source_id: str
    input_audio_stream_id: str
    audio_format: AudioFormat
    next_synth_seq: int
    next_audio_seq: int
    next_sample_index: int
    played_frames: int = 0
    next_state_seq: int = 0
    next_command_seq: int = 0
    paused: bool = False
    queued_chunks: list[SynthesizedAudioChunk] = dataclass_field(default_factory=list)
    pending_final_marker: DoraSynthesizedAudioMetadata | None = None


class PlaybackQueueRuntime:
    """State machine for synthesized-audio queueing and playback observability."""

    def __init__(self, config: PlaybackQueueConfig) -> None:
        self._config = config
        self._active: ActivePlayback | None = None
        self._failed_request_ids: set[str] = set()
        self._output_format: AudioFormat | None = None
        self._next_output_seq = 0
        self._next_output_sample_index = 0

    @property
    def idle(self) -> bool:
        return self._active is None

    def handle_synthesized_audio_chunk(
        self,
        chunk: SynthesizedAudioChunk,
    ) -> PlaybackQueueOutput:
        if chunk.request_id in self._failed_request_ids:
            return PlaybackQueueOutput()
        active = self._ensure_active_for_chunk(chunk)
        if active.paused:
            self._enqueue_chunk(active, chunk)
            return PlaybackQueueOutput(
                events=(PlaybackQueueStateOutput(self._state(active, "queued")),),
            )
        return self._emit_audio_chunk(active, chunk)

    def handle_synthesized_audio_final(
        self,
        final_marker: DoraSynthesizedAudioMetadata,
    ) -> PlaybackQueueOutput:
        if final_marker.request_id in self._failed_request_ids:
            self._failed_request_ids.remove(final_marker.request_id)
            return PlaybackQueueOutput()
        active = self._require_active()
        self._validate_final_marker(active, final_marker)
        if active.pending_final_marker is not None:
            raise PlaybackQueueError("synthesized audio final marker arrived twice")
        active.pending_final_marker = final_marker
        if active.paused or active.queued_chunks:
            return PlaybackQueueOutput(
                events=(PlaybackQueueStateOutput(self._state(active, "queued")),),
            )
        return self._complete_active_request(active)

    def handle_playback_command(
        self,
        command: PlaybackCommandEvent,
    ) -> PlaybackQueueOutput:
        active = self._require_matching_command(command)
        self._validate_command_sequence(active, command.seq)

        if command.command == "pause":
            if active.paused:
                raise PlaybackQueueError("pause command arrived while playback is already paused")
            active.paused = True
            return PlaybackQueueOutput(
                events=(PlaybackQueueStateOutput(self._state(active, "paused")),)
            )

        if command.command == "resume":
            if not active.paused:
                raise PlaybackQueueError("resume command arrived while playback is not paused")
            active.paused = False
            return self._resume_active_request(active)

        if command.command == "stop":
            return self._terminate_active_request(active, "stopped", "stopped")

        return self._terminate_active_request(active, "cancelled", "cancelled")

    def fail_active_request(self, reason: str) -> PlaybackQueueOutput | None:
        active = self._active
        if active is None:
            return None
        self._failed_request_ids.add(active.request_id)
        return self._terminate_active_request(
            active,
            "failed",
            "failed",
            reason=reason,
        )

    def _ensure_active_for_chunk(self, chunk: SynthesizedAudioChunk) -> ActivePlayback:
        if self._active is None:
            if chunk.seq != 0:
                raise PlaybackQueueError("first synthesized audio chunk must have seq=0")
            if chunk.audio.seq != 0:
                raise PlaybackQueueError("first synthesized audio chunk audio.seq must be 0")
            if chunk.audio.sample_index != 0:
                raise PlaybackQueueError(
                    "first synthesized audio chunk audio.sample_index must be 0"
                )
            self._active = ActivePlayback(
                request_id=chunk.request_id,
                session_id=chunk.session_id,
                user_turn_id=chunk.user_turn_id,
                assistant_turn_id=chunk.assistant_turn_id,
                input_audio_source_id=chunk.audio.source_id,
                input_audio_stream_id=chunk.audio.stream_id,
                audio_format=chunk.audio.format,
                next_synth_seq=0,
                next_audio_seq=0,
                next_sample_index=0,
            )
        active = self._require_active()
        self._validate_next_chunk(active, chunk)
        active.next_synth_seq = chunk.seq + 1
        active.next_audio_seq = chunk.audio.seq + 1
        active.next_sample_index = chunk.audio.next_sample_index
        return active

    def _validate_next_chunk(
        self,
        active: ActivePlayback,
        chunk: SynthesizedAudioChunk,
    ) -> None:
        if chunk.request_id != active.request_id:
            raise PlaybackQueueError("synthesized audio request_id changed while active")
        if chunk.session_id != active.session_id:
            raise PlaybackQueueError("synthesized audio session_id changed while active")
        if chunk.user_turn_id != active.user_turn_id:
            raise PlaybackQueueError("synthesized audio user_turn_id changed while active")
        if chunk.assistant_turn_id != active.assistant_turn_id:
            raise PlaybackQueueError("synthesized audio assistant_turn_id changed while active")
        if chunk.audio.source_id != active.input_audio_source_id:
            raise PlaybackQueueError("synthesized audio source_id changed while active")
        if chunk.audio.stream_id != active.input_audio_stream_id:
            raise PlaybackQueueError("synthesized audio stream_id changed while active")
        if chunk.audio.format != active.audio_format:
            raise PlaybackQueueError("synthesized audio format changed while active")
        if chunk.seq != active.next_synth_seq:
            raise PlaybackQueueError(
                f"synthesized audio seq discontinuity: expected {active.next_synth_seq}, "
                f"got {chunk.seq}"
            )
        if chunk.audio.seq != active.next_audio_seq:
            raise PlaybackQueueError(
                f"synthesized audio audio.seq discontinuity: expected "
                f"{active.next_audio_seq}, got {chunk.audio.seq}"
            )
        if chunk.audio.sample_index != active.next_sample_index:
            raise PlaybackQueueError(
                f"synthesized audio sample_index discontinuity: expected "
                f"{active.next_sample_index}, got {chunk.audio.sample_index}"
            )

    def _validate_final_marker(
        self,
        active: ActivePlayback,
        final_marker: DoraSynthesizedAudioMetadata,
    ) -> None:
        if final_marker.request_id != active.request_id:
            raise PlaybackQueueError("synthesized audio final request_id mismatch")
        if final_marker.session_id != active.session_id:
            raise PlaybackQueueError("synthesized audio final session_id mismatch")
        if final_marker.user_turn_id != active.user_turn_id:
            raise PlaybackQueueError("synthesized audio final user_turn_id mismatch")
        if final_marker.assistant_turn_id != active.assistant_turn_id:
            raise PlaybackQueueError("synthesized audio final assistant_turn_id mismatch")
        if final_marker.audio_source_id != active.input_audio_source_id:
            raise PlaybackQueueError("synthesized audio final source_id mismatch")
        if final_marker.audio_stream_id != active.input_audio_stream_id:
            raise PlaybackQueueError("synthesized audio final stream_id mismatch")
        if final_marker.audio_format != active.audio_format:
            raise PlaybackQueueError("synthesized audio final format mismatch")
        if final_marker.seq != active.next_synth_seq:
            raise PlaybackQueueError(
                f"synthesized audio final seq discontinuity: expected "
                f"{active.next_synth_seq}, got {final_marker.seq}"
            )
        if final_marker.audio_seq != active.next_audio_seq:
            raise PlaybackQueueError(
                f"synthesized audio final audio_seq discontinuity: expected "
                f"{active.next_audio_seq}, got {final_marker.audio_seq}"
            )
        if final_marker.audio_sample_index != active.next_sample_index:
            raise PlaybackQueueError(
                f"synthesized audio final sample_index discontinuity: expected "
                f"{active.next_sample_index}, got {final_marker.audio_sample_index}"
            )

    def _enqueue_chunk(
        self,
        active: ActivePlayback,
        chunk: SynthesizedAudioChunk,
    ) -> None:
        if len(active.queued_chunks) >= self._config.max_queued_audio_chunks:
            raise PlaybackQueueError("paused playback queue is full")
        active.queued_chunks.append(chunk)

    def _emit_audio_chunk(
        self,
        active: ActivePlayback,
        chunk: SynthesizedAudioChunk,
    ) -> PlaybackQueueOutput:
        events: list[PlaybackQueueOutputEvent] = []
        if active.played_frames == 0 and chunk.seq == 0:
            events.append(PlaybackQueueStateOutput(self._state(active, "queued")))
        output_audio = self._output_audio_chunk(chunk.audio)
        events.append(PlaybackQueueAudioOutput(output_audio))
        active.played_frames += output_audio.frame_count
        events.append(PlaybackQueueStateOutput(self._state(active, "playing")))
        return PlaybackQueueOutput(events=tuple(events))

    def _resume_active_request(self, active: ActivePlayback) -> PlaybackQueueOutput:
        events: list[PlaybackQueueOutputEvent] = [
            PlaybackQueueStateOutput(self._state(active, "playing"))
        ]
        queued_chunks = tuple(active.queued_chunks)
        active.queued_chunks.clear()
        for chunk in queued_chunks:
            output_audio = self._output_audio_chunk(chunk.audio)
            events.append(PlaybackQueueAudioOutput(output_audio))
            active.played_frames += output_audio.frame_count
            events.append(PlaybackQueueStateOutput(self._state(active, "playing")))
        if active.pending_final_marker is None:
            return PlaybackQueueOutput(events=tuple(events))
        completion = self._complete_active_request(active)
        return PlaybackQueueOutput(events=tuple([*events, *completion.events]))

    def _complete_active_request(self, active: ActivePlayback) -> PlaybackQueueOutput:
        final_marker = active.pending_final_marker
        if final_marker is None:
            raise PlaybackQueueError(
                "cannot complete playback without synthesized audio final marker"
            )
        audio_final = self._output_audio_final_marker(active)
        state = self._state(active, "completed")
        done = PlaybackDone(
            request_id=active.request_id,
            session_id=active.session_id,
            user_turn_id=active.user_turn_id,
            stream_id=self._config.output_stream_id,
            status="completed",
            final_sequence=final_marker.seq,
            total_frames=active.played_frames,
        )
        self._active = None
        return PlaybackQueueOutput(
            events=(
                PlaybackQueueAudioFinalOutput(*audio_final),
                PlaybackQueueStateOutput(state),
                PlaybackQueueDoneOutput(done),
            )
        )

    def _terminate_active_request(
        self,
        active: ActivePlayback,
        state_kind: PlaybackStateKind,
        done_status: PlaybackDoneStatus,
        *,
        reason: str | None = None,
    ) -> PlaybackQueueOutput:
        state = self._state(active, state_kind, reason=reason)
        done = PlaybackDone(
            request_id=active.request_id,
            session_id=active.session_id,
            user_turn_id=active.user_turn_id,
            stream_id=self._config.output_stream_id,
            status=done_status,
            final_sequence=active.next_synth_seq,
            total_frames=active.played_frames,
            reason=reason,
        )
        audio_final = self._output_audio_final_marker(active)
        active.queued_chunks.clear()
        active.pending_final_marker = None
        self._active = None
        return PlaybackQueueOutput(
            events=(
                PlaybackQueueAudioFinalOutput(*audio_final),
                PlaybackQueueStateOutput(state),
                PlaybackQueueDoneOutput(done),
            )
        )

    def _require_active(self) -> ActivePlayback:
        active = self._active
        if active is None:
            raise PlaybackQueueError("playback event arrived without an active request")
        return active

    def _require_matching_command(self, command: PlaybackCommandEvent) -> ActivePlayback:
        active = self._require_active()
        if command.request_id != active.request_id:
            raise PlaybackQueueError("playback command request_id mismatch")
        if command.stream_id != self._config.output_stream_id:
            raise PlaybackQueueError("playback command stream_id mismatch")
        return active

    def _validate_command_sequence(self, active: ActivePlayback, seq: int) -> None:
        if seq != active.next_command_seq:
            raise PlaybackQueueError(
                f"playback command seq discontinuity: expected {active.next_command_seq}, got {seq}"
            )
        active.next_command_seq += 1

    def _state(
        self,
        active: ActivePlayback,
        state: PlaybackStateKind,
        *,
        reason: str | None = None,
    ) -> PlaybackState:
        playback_state = PlaybackState(
            request_id=active.request_id,
            session_id=active.session_id,
            user_turn_id=active.user_turn_id,
            stream_id=self._config.output_stream_id,
            state=state,
            seq=active.next_state_seq,
            played_frames=active.played_frames,
            reason=reason,
        )
        active.next_state_seq += 1
        return playback_state

    def _output_audio_chunk(self, audio: AudioChunk) -> AudioChunk:
        self._validate_or_set_output_format(audio.format)
        output_audio = AudioChunk(
            source_id=self._config.output_source_id,
            stream_id=self._config.output_stream_id,
            seq=self._next_output_seq,
            sample_index=self._next_output_sample_index,
            capture_time_ns=_audio_timeline_time_ns(
                self._next_output_sample_index,
                audio.format.sample_rate_hz,
            ),
            frame_count=audio.frame_count,
            format=audio.format,
            payload=audio.payload,
        )
        self._next_output_seq += 1
        self._next_output_sample_index = output_audio.next_sample_index
        return output_audio

    def _output_audio_final_marker(
        self,
        active: ActivePlayback,
    ) -> tuple[str, str, int, int, int, AudioFormat]:
        self._validate_or_set_output_format(active.audio_format)
        return (
            self._config.output_source_id,
            self._config.output_stream_id,
            self._next_output_seq,
            self._next_output_sample_index,
            _audio_timeline_time_ns(
                self._next_output_sample_index,
                active.audio_format.sample_rate_hz,
            ),
            active.audio_format,
        )

    def _validate_or_set_output_format(self, audio_format: AudioFormat) -> None:
        if self._output_format is None:
            self._output_format = audio_format
            return
        if self._output_format != audio_format:
            raise PlaybackQueueError("speaker output format changed while playback queue is active")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the fluent-audio playback queue.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument(
        "--max-queued-audio-chunks",
        type=int,
        default=DEFAULT_MAX_QUEUED_AUDIO_CHUNKS,
    )
    parser.add_argument("--output-source-id", default=DEFAULT_OUTPUT_SOURCE_ID)
    parser.add_argument("--output-stream-id", default=DEFAULT_OUTPUT_STREAM_ID)
    parser.add_argument(
        "--output-drain-seconds",
        type=float,
        default=DEFAULT_DORA_OUTPUT_DRAIN_SECONDS,
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("playback_queue requires --dora")

    from dora import Node

    config = PlaybackQueueConfig(
        max_queued_audio_chunks=args.max_queued_audio_chunks,
        output_source_id=args.output_source_id,
        output_stream_id=args.output_stream_id,
        output_drain_seconds=args.output_drain_seconds,
    )
    summary = run_playback_queue_events(Node(), config)
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def run_playback_queue_events(
    node,
    config: PlaybackQueueConfig,
) -> PlaybackQueueSummary:
    runtime = PlaybackQueueRuntime(config)
    synthesized_audio_chunks = 0
    synthesized_audio_finals = 0
    playback_commands = 0
    audio_chunks_sent = 0
    audio_finals_sent = 0
    playback_states = 0
    playback_done = 0
    stopped_requests = 0
    cleared_requests = 0
    paused_requests = 0
    resumed_requests = 0

    for event in node:
        if event is None:
            raise PlaybackQueueError("DORA event stream ended before STOP")
        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            if not runtime.idle:
                raise PlaybackQueueError("DORA STOP arrived while playback request is active")
            _drain_dora_output_send(config.output_drain_seconds)
            return PlaybackQueueSummary(
                synthesized_audio_chunks=synthesized_audio_chunks,
                synthesized_audio_finals=synthesized_audio_finals,
                playback_commands=playback_commands,
                audio_chunks_sent=audio_chunks_sent,
                audio_finals_sent=audio_finals_sent,
                playback_states=playback_states,
                playback_done=playback_done,
                stopped_requests=stopped_requests,
                cleared_requests=cleared_requests,
                paused_requests=paused_requests,
                resumed_requests=resumed_requests,
            )
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id == "synth_audio":
                if not runtime.idle:
                    raise PlaybackQueueError(
                        "synth_audio input closed while playback request is active"
                    )
                _drain_dora_output_send(config.output_drain_seconds)
                return PlaybackQueueSummary(
                    synthesized_audio_chunks=synthesized_audio_chunks,
                    synthesized_audio_finals=synthesized_audio_finals,
                    playback_commands=playback_commands,
                    audio_chunks_sent=audio_chunks_sent,
                    audio_finals_sent=audio_finals_sent,
                    playback_states=playback_states,
                    playback_done=playback_done,
                    stopped_requests=stopped_requests,
                    cleared_requests=cleared_requests,
                    paused_requests=paused_requests,
                    resumed_requests=resumed_requests,
                )
            if input_id != "playback_command":
                raise PlaybackQueueError(f"Unexpected DORA input id: {input_id!r}")
            continue
        if event_type != "INPUT":
            raise PlaybackQueueError(f"Unexpected DORA event type: {event_type!r}")

        input_id = _required_event_text(event, "id")
        try:
            outputs = _handle_input_event(runtime, input_id, event)
        except PlaybackQueueError as exc:
            failed_outputs = runtime.fail_active_request(str(exc))
            if failed_outputs is None:
                raise
            outputs = failed_outputs
        _send_outputs(node, outputs)
        audio_chunks_sent += outputs.audio_chunk_count
        audio_finals_sent += outputs.audio_final_count
        playback_states += outputs.playback_state_count
        playback_done += outputs.playback_done_count

        if input_id == "synth_audio":
            metadata = validate_dora_synthesized_audio_metadata(event.get("metadata"))
            if metadata.final:
                synthesized_audio_finals += 1
            else:
                synthesized_audio_chunks += 1
        elif input_id == "playback_command":
            metadata = validate_dora_playback_command_metadata(event.get("metadata"))
            command = decode_playback_command_from_dora(event.get("value"), metadata)
            playback_commands += 1
            if command.command == "stop":
                stopped_requests += 1
            elif command.command == "clear":
                cleared_requests += 1
            elif command.command == "pause":
                paused_requests += 1
            elif command.command == "resume":
                resumed_requests += 1

    raise PlaybackQueueError("DORA event stream ended before STOP")


def _handle_input_event(
    runtime: PlaybackQueueRuntime,
    input_id: str,
    event,
) -> PlaybackQueueOutput:
    payload = event.get("value")
    metadata = event.get("metadata")
    if input_id == "synth_audio":
        synth_metadata = validate_dora_synthesized_audio_metadata(metadata)
        if synth_metadata.final:
            final_marker = validate_dora_synthesized_audio_final_marker(
                payload,
                synth_metadata,
            )
            return runtime.handle_synthesized_audio_final(final_marker)
        return runtime.handle_synthesized_audio_chunk(
            decode_synthesized_audio_chunk_from_dora(payload, synth_metadata)
        )
    if input_id == "playback_command":
        command_metadata = validate_dora_playback_command_metadata(metadata)
        return runtime.handle_playback_command(
            decode_playback_command_from_dora(payload, command_metadata)
        )
    raise PlaybackQueueError(f"Unexpected DORA input id: {input_id!r}")


def _send_outputs(node, outputs: PlaybackQueueOutput) -> None:
    for event in outputs.events:
        if isinstance(event, PlaybackQueueAudioOutput):
            payload, metadata = encode_audio_chunk_for_dora(event.audio)
            node.send_output("audio", payload, metadata=metadata.to_dora_metadata())
        elif isinstance(event, PlaybackQueueAudioFinalOutput):
            payload, metadata = encode_audio_final_marker_for_dora(
                source_id=event.source_id,
                stream_id=event.stream_id,
                seq=event.seq,
                sample_index=event.sample_index,
                capture_time_ns=event.capture_time_ns,
                audio_format=event.audio_format,
            )
            node.send_output("audio", payload, metadata=metadata.to_dora_metadata())
        elif isinstance(event, PlaybackQueueStateOutput):
            payload, metadata = encode_playback_state_for_dora(event.state)
            node.send_output("playback_state", payload, metadata=metadata.to_dora_metadata())
        elif isinstance(event, PlaybackQueueDoneOutput):
            payload, metadata = encode_playback_done_for_dora(event.done)
            node.send_output("playback_done", payload, metadata=metadata.to_dora_metadata())


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise PlaybackQueueError(f"DORA event field {key!r} must be a string")
    return value


def _audio_timeline_time_ns(sample_index: int, sample_rate_hz: int) -> int:
    return (sample_index * 1_000_000_000) // sample_rate_hz


def _drain_dora_output_send(output_drain_seconds: float) -> None:
    time.sleep(output_drain_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
