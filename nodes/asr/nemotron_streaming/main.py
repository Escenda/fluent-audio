"""DORA node shell for streaming ASR over Nemotron-compatible backends."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Sequence
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pydantic import BaseModel, ConfigDict, Field

from fluent_audio.contracts import (
    AsrStart,
    AsrStop,
    AudioChunk,
    AudioFormat,
    TranscriptDelta,
    TranscriptFinal,
    TranscriptPartial,
)
from fluent_audio.dora import (
    DoraAudioMetadata,
    decode_asr_control_from_dora,
    decode_audio_chunk_from_dora,
    encode_transcript_delta_for_dora,
    encode_transcript_final_for_dora,
    encode_transcript_partial_for_dora,
    encode_transcript_stream_final_marker_for_dora,
    validate_dora_asr_control_final_marker,
    validate_dora_asr_control_metadata,
    validate_dora_audio_final_marker,
    validate_dora_audio_metadata,
)
from nodes.asr.nemotron_streaming.backend import (
    DEFAULT_NEMOTRON_MODEL_NAME,
    NemotronBackendError,
    NemotronBackendSettings,
    build_nemotron_backend,
)
from nodes.asr.nemotron_streaming.logic import (
    NemotronStreamingConfig,
    NemotronStreamingError,
    NemotronStreamingRuntime,
    StreamingAsrBackend,
)

DORA_FINAL_MARKER_DRAIN_SECONDS = 0.1


class NemotronStreamingNodeError(ValueError):
    """Raised when the Nemotron streaming DORA node receives invalid input."""


class NemotronStreamingNodeConfig(BaseModel):
    """Runtime configuration for one Nemotron streaming DORA node."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    input_audio_source_id: str = Field(min_length=1)
    input_audio_stream_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    output_stream_id: str = Field(min_length=1)
    prebuffer_frames: int = Field(default=16_000, gt=0)
    control_holdback_frames: int = Field(default=4_096, ge=0)
    late_stop_tolerance_frames: int = Field(default=16_000, ge=0)
    warmup_frames: int = Field(default=16_000, ge=0)
    sample_rate_hz: int = Field(default=16_000, gt=0)
    channels: int = Field(default=1, gt=0)
    sample_format: str = "s16le"
    channel_layout: str = "interleaved"

    def audio_format(self) -> AudioFormat:
        return AudioFormat(
            sample_rate_hz=self.sample_rate_hz,
            channels=self.channels,
            sample_format=self.sample_format,
            channel_layout=self.channel_layout,
        )

    def to_logic_config(self) -> NemotronStreamingConfig:
        return NemotronStreamingConfig(
            input_audio_source_id=self.input_audio_source_id,
            input_audio_stream_id=self.input_audio_stream_id,
            output_stream_id=self.output_stream_id,
            expected_audio_format=self.audio_format(),
            prebuffer_frames=self.prebuffer_frames,
            control_holdback_frames=self.control_holdback_frames,
            late_stop_tolerance_frames=self.late_stop_tolerance_frames,
        )


class NemotronStreamingNodeSummary(BaseModel):
    """Validated processing summary for one ASR node run."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    input_chunks: int = Field(ge=0)
    input_frames: int = Field(ge=0)
    control_events: int = Field(ge=0)
    transcript_deltas: int = Field(ge=0)
    transcript_partials: int = Field(ge=0)
    transcript_finals: int = Field(ge=0)
    final_sample_index: int = Field(ge=0)
    first_start_sample_index: int | None = Field(default=None, ge=0)
    last_stop_sample_index: int | None = Field(default=None, ge=0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run streaming ASR over DORA audio input.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--input-audio-source-id", required=True)
    parser.add_argument("--input-audio-stream-id", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--output-stream-id", required=True)
    parser.add_argument("--prebuffer-frames", type=int, default=16_000)
    parser.add_argument("--control-holdback-frames", type=int, default=4_096)
    parser.add_argument("--late-stop-tolerance-frames", type=int, default=16_000)
    parser.add_argument("--warmup-frames", type=int, default=16_000)
    parser.add_argument("--sample-rate-hz", type=int, default=16_000)
    parser.add_argument("--channels", type=int, default=1)
    parser.add_argument("--sample-format", default="s16le")
    parser.add_argument("--channel-layout", default="interleaved")
    parser.add_argument("--backend", choices=["nemo"], required=True)
    parser.add_argument("--model-name", default=DEFAULT_NEMOTRON_MODEL_NAME)
    parser.add_argument("--target-lang", default="auto")
    parser.add_argument("--strip-lang-tags", action="store_true", default=True)
    parser.add_argument("--keep-lang-tags", action="store_true")
    parser.add_argument("--att-context-right-frames", type=int, default=3)
    parser.add_argument("--cuda-device", type=int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("nemotron_streaming requires --dora")

    config = _node_config_from_args(args)
    backend_settings = _backend_settings_from_args(args)
    try:
        backend = build_nemotron_backend(backend_settings)
        warmup_streaming_backend(backend, config)
    except NemotronBackendError as exc:
        raise NemotronStreamingNodeError(str(exc)) from exc

    from dora import Node

    summary = run_nemotron_streaming_events(Node(), config, backend)
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def _node_config_from_args(args: argparse.Namespace) -> NemotronStreamingNodeConfig:
    return NemotronStreamingNodeConfig(
        input_audio_source_id=args.input_audio_source_id,
        input_audio_stream_id=args.input_audio_stream_id,
        session_id=args.session_id,
        output_stream_id=args.output_stream_id,
        prebuffer_frames=args.prebuffer_frames,
        control_holdback_frames=args.control_holdback_frames,
        late_stop_tolerance_frames=args.late_stop_tolerance_frames,
        warmup_frames=args.warmup_frames,
        sample_rate_hz=args.sample_rate_hz,
        channels=args.channels,
        sample_format=args.sample_format,
        channel_layout=args.channel_layout,
    )


def warmup_streaming_backend(
    backend: StreamingAsrBackend,
    config: NemotronStreamingNodeConfig,
) -> None:
    if config.warmup_frames == 0:
        return
    audio_format = config.audio_format()
    warmup_turn_id = "nemotron-warmup-turn"
    backend.start(
        AsrStart(
            action="start",
            session_id=config.session_id,
            user_turn_id=warmup_turn_id,
            stream_id=config.input_audio_stream_id,
            seq=0,
            start_sample_index=0,
        ),
        audio_format,
    )
    backend.push_audio(
        AudioChunk(
            source_id=config.input_audio_source_id,
            stream_id=config.input_audio_stream_id,
            seq=0,
            sample_index=0,
            capture_time_ns=0,
            frame_count=config.warmup_frames,
            format=audio_format,
            payload=bytes(config.warmup_frames * audio_format.frame_size_bytes),
        )
    )
    backend.stop(
        AsrStop(
            action="stop",
            session_id=config.session_id,
            user_turn_id=warmup_turn_id,
            stream_id=config.input_audio_stream_id,
            seq=1,
            stop_sample_index=config.warmup_frames,
        )
    )


def _backend_settings_from_args(args: argparse.Namespace) -> NemotronBackendSettings:
    return NemotronBackendSettings(
        backend=args.backend,
        model_name=args.model_name,
        target_lang=args.target_lang,
        strip_lang_tags=not args.keep_lang_tags if args.keep_lang_tags else args.strip_lang_tags,
        att_context_right_frames=args.att_context_right_frames,
        cuda_device=args.cuda_device,
    )


def run_nemotron_streaming_events(
    node,
    config: NemotronStreamingNodeConfig,
    backend: StreamingAsrBackend,
) -> NemotronStreamingNodeSummary:
    runtime = NemotronStreamingRuntime(config.to_logic_config(), backend)
    input_chunks = 0
    input_frames = 0
    control_events = 0
    transcript_deltas = 0
    transcript_partials = 0
    transcript_finals = 0
    previous_audio: AudioChunk | None = None
    control_completed = False
    control_transport_closed = False
    audio_transport_closed = False
    audio_closed_sample_index: int | None = None
    first_start_sample_index: int | None = None
    last_stop_sample_index: int | None = None

    for event in node:
        if event is None:
            summary = _maybe_finish_after_input_completion(
                node,
                config,
                runtime,
                input_chunks=input_chunks,
                input_frames=input_frames,
                control_events=control_events,
                transcript_deltas=transcript_deltas,
                transcript_partials=transcript_partials,
                transcript_finals=transcript_finals,
                audio_closed_sample_index=audio_closed_sample_index,
                control_completed=control_completed,
                first_start_sample_index=first_start_sample_index,
                last_stop_sample_index=last_stop_sample_index,
            )
            if summary is not None:
                return summary
            raise NemotronStreamingNodeError("DORA event stream ended before audio completion")

        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            summary = _maybe_finish_after_input_completion(
                node,
                config,
                runtime,
                input_chunks=input_chunks,
                input_frames=input_frames,
                control_events=control_events,
                transcript_deltas=transcript_deltas,
                transcript_partials=transcript_partials,
                transcript_finals=transcript_finals,
                audio_closed_sample_index=audio_closed_sample_index,
                control_completed=control_completed,
                first_start_sample_index=first_start_sample_index,
                last_stop_sample_index=last_stop_sample_index,
            )
            if summary is not None:
                return summary
            raise NemotronStreamingNodeError("DORA STOP arrived before audio completion")
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id == "asr_control":
                control_transport_closed = True
                summary = _maybe_finish_after_input_completion(
                    node,
                    config,
                    runtime,
                    input_chunks=input_chunks,
                    input_frames=input_frames,
                    control_events=control_events,
                    transcript_deltas=transcript_deltas,
                    transcript_partials=transcript_partials,
                    transcript_finals=transcript_finals,
                    audio_closed_sample_index=audio_closed_sample_index,
                    control_completed=control_completed,
                    first_start_sample_index=first_start_sample_index,
                    last_stop_sample_index=last_stop_sample_index,
                )
                if summary is not None:
                    return summary
                continue
            if input_id == "audio":
                audio_transport_closed = True
                summary = _maybe_finish_after_input_completion(
                    node,
                    config,
                    runtime,
                    input_chunks=input_chunks,
                    input_frames=input_frames,
                    control_events=control_events,
                    transcript_deltas=transcript_deltas,
                    transcript_partials=transcript_partials,
                    transcript_finals=transcript_finals,
                    audio_closed_sample_index=audio_closed_sample_index,
                    control_completed=control_completed,
                    first_start_sample_index=first_start_sample_index,
                    last_stop_sample_index=last_stop_sample_index,
                )
                if summary is not None:
                    return summary
                continue
            raise NemotronStreamingNodeError(f"Unexpected DORA input id: {input_id!r}")
        if event_type != "INPUT":
            raise NemotronStreamingNodeError(f"Unexpected DORA event type: {event_type!r}")

        input_id = _required_event_text(event, "id")
        payload = event.get("value")
        if input_id == "audio":
            if audio_closed_sample_index is not None:
                raise NemotronStreamingNodeError("Audio arrived after ASR audio completion")
            metadata = validate_dora_audio_metadata(event.get("metadata"))
            if metadata.final:
                final_marker = validate_dora_audio_final_marker(payload, metadata)
                audio_closed_sample_index = _validate_audio_final_marker(
                    final_marker,
                    previous_audio,
                    config,
                )
                summary = _maybe_finish_after_input_completion(
                    node,
                    config,
                    runtime,
                    input_chunks=input_chunks,
                    input_frames=input_frames,
                    control_events=control_events,
                    transcript_deltas=transcript_deltas,
                    transcript_partials=transcript_partials,
                    transcript_finals=transcript_finals,
                    audio_closed_sample_index=audio_closed_sample_index,
                    control_completed=control_completed,
                    first_start_sample_index=first_start_sample_index,
                    last_stop_sample_index=last_stop_sample_index,
                )
                if summary is not None:
                    return summary
                continue

            chunk = decode_audio_chunk_from_dora(payload, metadata)
            try:
                transcript_events = runtime.push_audio(chunk)
            except NemotronStreamingError as exc:
                raise NemotronStreamingNodeError("Nemotron streaming audio error") from exc
            sent_deltas, sent_partials, sent_finals = _send_transcript_events(
                node,
                transcript_events,
            )
            transcript_deltas += sent_deltas
            transcript_partials += sent_partials
            transcript_finals += sent_finals
            input_chunks += 1
            input_frames += chunk.frame_count
            previous_audio = chunk
            continue

        if input_id == "asr_control":
            if control_completed and runtime.active_turn is None:
                raise NemotronStreamingNodeError(
                    "ASR control arrived after ASR control final marker"
                )
            metadata = validate_dora_asr_control_metadata(event.get("metadata"))
            if metadata.final:
                final_marker = validate_dora_asr_control_final_marker(payload, metadata)
                if final_marker.session_id != config.session_id:
                    raise NemotronStreamingNodeError(
                        "ASR control final session mismatch: "
                        f"expected {config.session_id!r}, got {final_marker.session_id!r}"
                    )
                if final_marker.stream_id != config.input_audio_stream_id:
                    raise NemotronStreamingNodeError(
                        "ASR control final stream mismatch: "
                        f"expected {config.input_audio_stream_id!r}, got {final_marker.stream_id!r}"
                    )
                control_completed = True
                summary = _maybe_finish_after_input_completion(
                    node,
                    config,
                    runtime,
                    input_chunks=input_chunks,
                    input_frames=input_frames,
                    control_events=control_events,
                    transcript_deltas=transcript_deltas,
                    transcript_partials=transcript_partials,
                    transcript_finals=transcript_finals,
                    audio_closed_sample_index=audio_closed_sample_index,
                    control_completed=control_completed,
                    first_start_sample_index=first_start_sample_index,
                    last_stop_sample_index=last_stop_sample_index,
                )
                if summary is not None:
                    return summary
                continue
            control = decode_asr_control_from_dora(payload, metadata)
            if isinstance(control, AsrStart) and first_start_sample_index is None:
                first_start_sample_index = control.start_sample_index
            if isinstance(control, AsrStop):
                last_stop_sample_index = control.stop_sample_index
            try:
                transcript_events = runtime.push_control(control)
            except NemotronStreamingError as exc:
                raise NemotronStreamingNodeError("Nemotron streaming control error") from exc
            sent_deltas, sent_partials, sent_finals = _send_transcript_events(
                node,
                transcript_events,
            )
            transcript_deltas += sent_deltas
            transcript_partials += sent_partials
            transcript_finals += sent_finals
            control_events += 1
            summary = _maybe_finish_after_input_completion(
                node,
                config,
                runtime,
                input_chunks=input_chunks,
                input_frames=input_frames,
                control_events=control_events,
                transcript_deltas=transcript_deltas,
                transcript_partials=transcript_partials,
                transcript_finals=transcript_finals,
                audio_closed_sample_index=audio_closed_sample_index,
                control_completed=control_completed,
                first_start_sample_index=first_start_sample_index,
                last_stop_sample_index=last_stop_sample_index,
            )
            if summary is not None:
                return summary
            continue

        raise NemotronStreamingNodeError(f"Unexpected DORA input id: {input_id!r}")

    if control_transport_closed and runtime.active_turn is not None:
        raise NemotronStreamingNodeError(
            "DORA ASR control input closed while an ASR turn is still active"
        )
    if control_transport_closed and not control_completed:
        raise NemotronStreamingNodeError(
            "DORA ASR control input closed before ASR control final marker"
        )
    if audio_transport_closed and audio_closed_sample_index is None:
        raise NemotronStreamingNodeError("DORA audio input closed before audio final marker")
    if audio_closed_sample_index is not None:
        raise NemotronStreamingNodeError("DORA event stream ended before ASR control final marker")
    raise NemotronStreamingNodeError("DORA audio stream ended without completion")


def _send_transcript_events(
    node,
    events: list[TranscriptDelta | TranscriptFinal | TranscriptPartial],
) -> tuple[int, int, int]:
    sent_deltas = 0
    sent_partials = 0
    sent_finals = 0
    for event in events:
        if isinstance(event, TranscriptDelta):
            payload, metadata = encode_transcript_delta_for_dora(event)
            sent_deltas += 1
        elif isinstance(event, TranscriptPartial):
            payload, metadata = encode_transcript_partial_for_dora(event)
            sent_partials += 1
        else:
            payload, metadata = encode_transcript_final_for_dora(event)
            sent_finals += 1
        node.send_output("transcript", payload, metadata=metadata.to_dora_metadata())
    return sent_deltas, sent_partials, sent_finals


def _maybe_finish_after_input_completion(
    node,
    config: NemotronStreamingNodeConfig,
    runtime: NemotronStreamingRuntime,
    *,
    input_chunks: int,
    input_frames: int,
    control_events: int,
    transcript_deltas: int,
    transcript_partials: int,
    transcript_finals: int,
    audio_closed_sample_index: int | None,
    control_completed: bool,
    first_start_sample_index: int | None,
    last_stop_sample_index: int | None,
) -> NemotronStreamingNodeSummary | None:
    if audio_closed_sample_index is None:
        return None
    if not control_completed:
        return None
    final_sample_index = audio_closed_sample_index
    _finish_audio_after_input_completion(runtime, final_sample_index)
    _send_transcript_final_marker(
        node,
        config,
        seq=runtime.next_transcript_seq,
        sample_index=final_sample_index,
    )
    return NemotronStreamingNodeSummary(
        input_chunks=input_chunks,
        input_frames=input_frames,
        control_events=control_events,
        transcript_deltas=transcript_deltas,
        transcript_partials=transcript_partials,
        transcript_finals=transcript_finals,
        final_sample_index=final_sample_index,
        first_start_sample_index=first_start_sample_index,
        last_stop_sample_index=last_stop_sample_index,
    )


def _send_transcript_final_marker(
    node,
    config: NemotronStreamingNodeConfig,
    *,
    seq: int,
    sample_index: int,
) -> None:
    payload, metadata = encode_transcript_stream_final_marker_for_dora(
        session_id=config.session_id,
        stream_id=config.output_stream_id,
        seq=seq,
        sample_index=sample_index,
    )
    node.send_output("transcript", payload, metadata=metadata.to_dora_metadata())
    _drain_dora_final_marker_send()


def _validate_audio_final_marker(
    final_marker: DoraAudioMetadata,
    previous_audio: AudioChunk | None,
    config: NemotronStreamingNodeConfig,
) -> int:
    if final_marker.source_id != config.input_audio_source_id:
        raise NemotronStreamingNodeError(
            "ASR audio final source mismatch: "
            f"expected {config.input_audio_source_id!r}, got {final_marker.source_id!r}"
        )
    if final_marker.stream_id != config.input_audio_stream_id:
        raise NemotronStreamingNodeError(
            "ASR audio final stream mismatch: "
            f"expected {config.input_audio_stream_id!r}, got {final_marker.stream_id!r}"
        )
    if final_marker.to_audio_format() != config.audio_format():
        raise NemotronStreamingNodeError("ASR audio final format mismatch")
    if previous_audio is None:
        raise NemotronStreamingNodeError("ASR audio final marker arrived before audio chunks")
    expected_seq = previous_audio.seq + 1
    expected_sample_index = previous_audio.sample_index + previous_audio.frame_count
    if final_marker.seq != expected_seq:
        raise NemotronStreamingNodeError(
            f"ASR audio final seq discontinuity: expected {expected_seq}, got {final_marker.seq}"
        )
    if final_marker.sample_index != expected_sample_index:
        raise NemotronStreamingNodeError(
            "ASR audio final sample_index discontinuity: "
            f"expected {expected_sample_index}, got {final_marker.sample_index}"
        )
    return final_marker.sample_index


def _finish_audio_after_input_completion(
    runtime: NemotronStreamingRuntime,
    final_sample_index: int,
) -> None:
    try:
        runtime.finish_audio(final_sample_index)
    except NemotronStreamingError as exc:
        raise NemotronStreamingNodeError(
            f"Nemotron streaming finalization error after input completion: {exc}"
        ) from exc


def _drain_dora_final_marker_send() -> None:
    # The DORA Python API exposes no output flush/ack. Keep the node alive briefly
    # after sending the explicit final marker so process teardown cannot race daemon
    # ingestion; downstream probes still fail closed if that marker is not observed.
    time.sleep(DORA_FINAL_MARKER_DRAIN_SECONDS)


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise NemotronStreamingNodeError(f"DORA event field {key!r} must be a string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
