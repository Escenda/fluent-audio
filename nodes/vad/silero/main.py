"""DORA node wrapper for the Silero voice activity detector."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import math
import sys
import time
from collections.abc import Sequence
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, Field

from fluent_audio.contracts import (
    AudioChunk,
    AudioFormat,
    AudioLevelEvent,
    VoiceActivityEvent,
    require_contiguous_audio_chunks,
)
from fluent_audio.dora import (
    DoraAudioMetadata,
    decode_audio_chunk_from_dora,
    encode_audio_level_event_for_dora,
    encode_voice_activity_event_for_dora,
    encode_voice_activity_final_marker_for_dora,
    validate_dora_audio_final_marker,
    validate_dora_audio_metadata,
)
from nodes.vad.silero.silero import (
    DEFAULT_MODEL_PATH,
    SileroVadConfig,
    SileroVadResult,
    SileroVadSession,
    s16le_mono_16k_to_float32_waveform,
)

DORA_FINAL_MARKER_DRAIN_SECONDS = 0.1
DEFAULT_LEVEL_PERIOD_WINDOWS = 8
MIN_LEVEL_DBFS = -120.0

EXPECTED_AUDIO_FORMAT = AudioFormat(
    sample_rate_hz=16_000,
    channels=1,
    sample_format="s16le",
    channel_layout="interleaved",
)


class VadNodeError(ValueError):
    """Raised when the DORA VAD node receives invalid audio stream input."""


class VadNodeConfig(BaseModel):
    """Runtime configuration for the DORA Silero VAD node."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    input_source_id: str = Field(min_length=1)
    input_stream_id: str = Field(min_length=1)
    output_source_id: str = Field(min_length=1)
    output_stream_id: str = Field(min_length=1)
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    level_period_windows: int = Field(default=DEFAULT_LEVEL_PERIOD_WINDOWS, ge=1)
    model_path: Path | None = None

    def to_silero_config(self) -> SileroVadConfig:
        model_path = self.model_path if self.model_path is not None else DEFAULT_MODEL_PATH
        return SileroVadConfig(model_path=model_path, threshold=self.threshold)


class VadNodeSummary(BaseModel):
    """Validated processing summary for one DORA audio stream."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    input_chunks: int = Field(ge=0)
    input_frames: int = Field(ge=0)
    activity_events: int = Field(ge=0)
    level_events: int = Field(ge=0)
    speech_events: int = Field(ge=0)
    final_sample_index: int = Field(ge=0)


class AudioLevelWindow(BaseModel):
    """Level metrics for one finalized VAD evaluation window."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    rms_dbfs: float = Field(le=0.0)
    peak_dbfs: float = Field(le=0.0)


class AudioLevelTracker:
    """Mirrors VAD windowing so diagnostics line up with activity events."""

    def __init__(self, *, window_frames: int) -> None:
        self._window_frames = window_frames
        self._buffer = np.zeros((0,), dtype=np.float32)

    def push(self, waveform: NDArray[np.float32]) -> list[AudioLevelWindow]:
        samples = _validate_level_waveform(waveform)
        if samples.shape[0] == 0:
            return []
        self._buffer = np.concatenate((self._buffer, samples))
        windows: list[AudioLevelWindow] = []
        while self._buffer.shape[0] >= self._window_frames:
            window = self._buffer[: self._window_frames]
            self._buffer = self._buffer[self._window_frames :]
            windows.append(_audio_level_window(window))
        return windows

    def flush(self) -> list[AudioLevelWindow]:
        if self._buffer.shape[0] == 0:
            return []
        padded = np.zeros((self._window_frames,), dtype=np.float32)
        padded[: self._buffer.shape[0]] = self._buffer
        self._buffer = np.zeros((0,), dtype=np.float32)
        return [_audio_level_window(padded)]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Silero VAD over DORA audio input.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--input-source-id", required=True)
    parser.add_argument("--input-stream-id", required=True)
    parser.add_argument("--output-source-id", required=True)
    parser.add_argument("--output-stream-id", required=True)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument(
        "--level-period-windows",
        type=int,
        default=DEFAULT_LEVEL_PERIOD_WINDOWS,
    )
    parser.add_argument("--model-path", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("vad requires --dora")

    from dora import Node

    config = VadNodeConfig(
        input_source_id=args.input_source_id,
        input_stream_id=args.input_stream_id,
        output_source_id=args.output_source_id,
        output_stream_id=args.output_stream_id,
        threshold=args.threshold,
        level_period_windows=args.level_period_windows,
        model_path=args.model_path,
    )
    summary = run_vad_events(Node(), config)
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def run_vad_events(node, config: VadNodeConfig) -> VadNodeSummary:
    """Consume DORA audio events and emit DORA voice activity events."""

    session = SileroVadSession(config.to_silero_config())
    level_tracker = AudioLevelTracker(window_frames=session.config.window_frames)
    previous_chunk: AudioChunk | None = None
    input_chunks = 0
    input_frames = 0
    activity_seq = 0
    level_seq = 0
    processed_level_windows = 0
    speech_events = 0
    input_base_sample_index: int | None = None

    for event in node:
        if event is None:
            raise VadNodeError("DORA event stream ended before audio final marker")

        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            raise VadNodeError("DORA STOP arrived before audio final marker")
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id != "audio":
                raise VadNodeError(f"Unexpected DORA input id: {input_id!r}")
            raise VadNodeError("DORA input closed before audio final marker")
        if event_type != "INPUT":
            raise VadNodeError(f"Unexpected DORA event type: {event_type!r}")

        input_id = _required_event_text(event, "id")
        if input_id != "audio":
            raise VadNodeError(f"Unexpected DORA input id: {input_id!r}")

        payload = event.get("value")
        metadata = validate_dora_audio_metadata(event.get("metadata"))
        if metadata.final:
            final_marker = validate_dora_audio_final_marker(payload, metadata)
            _validate_final_marker(final_marker, previous_chunk, config)

            flushed_results = session.flush()
            flushed_levels = level_tracker.flush()
            _validate_level_alignment(flushed_results, flushed_levels)
            for result, level in zip(flushed_results, flushed_levels, strict=True):
                activity_seq, result_was_speech = _send_activity_result(
                    node,
                    config,
                    result,
                    activity_seq=activity_seq,
                    input_base_sample_index=input_base_sample_index
                    if input_base_sample_index is not None
                    else final_marker.sample_index,
                )
                if result_was_speech:
                    speech_events += 1
                should_send_level = _should_send_level_event(
                    processed_level_windows,
                    config,
                )
                level_seq = _send_level_result_if_needed(
                    node,
                    config,
                    result,
                    level,
                    level_seq=level_seq,
                    input_base_sample_index=input_base_sample_index
                    if input_base_sample_index is not None
                    else final_marker.sample_index,
                    should_send=should_send_level,
                )
                processed_level_windows += 1

            final_payload, final_metadata = encode_voice_activity_final_marker_for_dora(
                source_id=config.output_source_id,
                stream_id=config.output_stream_id,
                seq=activity_seq,
                sample_index=final_marker.sample_index,
            )
            node.send_output(
                "activity",
                final_payload,
                metadata=final_metadata.to_dora_metadata(),
            )
            _drain_dora_final_marker_send()
            return VadNodeSummary(
                input_chunks=input_chunks,
                input_frames=input_frames,
                activity_events=activity_seq,
                level_events=level_seq,
                speech_events=speech_events,
                final_sample_index=final_marker.sample_index,
            )

        chunk = decode_audio_chunk_from_dora(payload, metadata)
        _validate_audio_chunk(chunk, previous_chunk, config)
        if input_base_sample_index is None:
            input_base_sample_index = chunk.sample_index
        waveform = s16le_mono_16k_to_float32_waveform(
            chunk.payload,
            sample_rate_hz=chunk.format.sample_rate_hz,
        )
        results = session.push(waveform)
        level_windows = level_tracker.push(waveform)
        _validate_level_alignment(results, level_windows)
        for result, level in zip(results, level_windows, strict=True):
            activity_seq, result_was_speech = _send_activity_result(
                node,
                config,
                result,
                activity_seq=activity_seq,
                input_base_sample_index=input_base_sample_index,
            )
            if result_was_speech:
                speech_events += 1
            should_send_level = _should_send_level_event(processed_level_windows, config)
            level_seq = _send_level_result_if_needed(
                node,
                config,
                result,
                level,
                level_seq=level_seq,
                input_base_sample_index=input_base_sample_index,
                should_send=should_send_level,
            )
            processed_level_windows += 1

        previous_chunk = chunk
        input_chunks += 1
        input_frames += chunk.frame_count

    raise VadNodeError("DORA audio stream ended without final marker")


def _send_activity_result(
    node,
    config: VadNodeConfig,
    result: SileroVadResult,
    *,
    activity_seq: int,
    input_base_sample_index: int,
) -> tuple[int, bool]:
    # Padded flush results still represent the fixed Silero evaluation window.
    # The separate final marker carries the real audio end sample_index.
    event = VoiceActivityEvent(
        source_id=config.output_source_id,
        stream_id=config.output_stream_id,
        seq=activity_seq,
        sample_index=input_base_sample_index + result.window_start_frame,
        frame_count=_result_audio_frame_count(result),
        state="speech" if result.is_speech else "silence",
        speech_probability=result.probability,
    )
    payload, metadata = encode_voice_activity_event_for_dora(event)
    node.send_output("activity", payload, metadata=metadata.to_dora_metadata())
    return activity_seq + 1, result.is_speech


def _send_level_result_if_needed(
    node,
    config: VadNodeConfig,
    result: SileroVadResult,
    level: AudioLevelWindow,
    *,
    level_seq: int,
    input_base_sample_index: int,
    should_send: bool,
) -> int:
    if not should_send:
        return level_seq
    event = AudioLevelEvent(
        source_id=config.output_source_id,
        stream_id=f"{config.output_stream_id}/level",
        seq=level_seq,
        sample_index=input_base_sample_index + result.window_start_frame,
        frame_count=_result_audio_frame_count(result),
        rms_dbfs=level.rms_dbfs,
        peak_dbfs=level.peak_dbfs,
        speech_probability=result.probability,
    )
    payload, metadata = encode_audio_level_event_for_dora(event)
    node.send_output("meter", payload, metadata=metadata.to_dora_metadata())
    return level_seq + 1


def _should_send_level_event(processed_level_windows: int, config: VadNodeConfig) -> bool:
    return processed_level_windows % config.level_period_windows == 0


def _result_audio_frame_count(result: SileroVadResult) -> int:
    frame_count = result.window_frames - result.padded_frames
    if frame_count <= 0:
        raise VadNodeError("VAD result frame_count became non-positive after removing padding")
    return frame_count


def _validate_level_alignment(
    results: list[SileroVadResult],
    level_windows: list[AudioLevelWindow],
) -> None:
    if len(results) != len(level_windows):
        raise VadNodeError(
            "VAD level window alignment failed: "
            f"results={len(results)}, levels={len(level_windows)}"
        )


def _audio_level_window(window: NDArray[np.float32]) -> AudioLevelWindow:
    samples = _validate_level_waveform(window)
    peak = float(np.max(np.abs(samples))) if samples.shape[0] > 0 else 0.0
    rms = float(np.sqrt(np.mean(np.square(samples)))) if samples.shape[0] > 0 else 0.0
    return AudioLevelWindow(
        rms_dbfs=_linear_to_dbfs(rms),
        peak_dbfs=_linear_to_dbfs(peak),
    )


def _linear_to_dbfs(value: float) -> float:
    if value <= 0.0:
        return MIN_LEVEL_DBFS
    return min(0.0, 20.0 * math.log10(value))


def _validate_level_waveform(waveform: NDArray[np.float32]) -> NDArray[np.float32]:
    if waveform.ndim != 1:
        raise VadNodeError(f"Audio level expects mono waveform, got ndim={waveform.ndim}")
    if waveform.dtype != np.float32:
        raise VadNodeError(f"Audio level expects float32 waveform, got dtype={waveform.dtype}")
    return np.ascontiguousarray(waveform, dtype=np.float32)


def _validate_audio_chunk(
    chunk: AudioChunk,
    previous_chunk: AudioChunk | None,
    config: VadNodeConfig,
) -> None:
    if chunk.source_id != config.input_source_id:
        raise VadNodeError(
            "VAD input source mismatch: "
            f"expected {config.input_source_id!r}, got {chunk.source_id!r}"
        )
    if chunk.stream_id != config.input_stream_id:
        raise VadNodeError(
            "VAD input stream mismatch: "
            f"expected {config.input_stream_id!r}, got {chunk.stream_id!r}"
        )
    if chunk.format != EXPECTED_AUDIO_FORMAT:
        raise VadNodeError(
            "VAD input format mismatch: expected 16 kHz mono s16le interleaved, "
            f"got {chunk.format.model_dump(mode='json')}"
        )
    if previous_chunk is not None:
        try:
            require_contiguous_audio_chunks(previous_chunk, chunk)
        except ValueError as exc:
            raise VadNodeError("VAD input sequence discontinuity") from exc


def _validate_final_marker(
    final_marker: DoraAudioMetadata,
    previous_chunk: AudioChunk | None,
    config: VadNodeConfig,
) -> None:
    if final_marker.source_id != config.input_source_id:
        raise VadNodeError(
            "VAD final marker source mismatch: "
            f"expected {config.input_source_id!r}, got {final_marker.source_id!r}"
        )
    if final_marker.stream_id != config.input_stream_id:
        raise VadNodeError(
            "VAD final marker stream mismatch: "
            f"expected {config.input_stream_id!r}, got {final_marker.stream_id!r}"
        )
    if final_marker.to_audio_format() != EXPECTED_AUDIO_FORMAT:
        raise VadNodeError(
            "VAD final marker format mismatch: expected 16 kHz mono s16le interleaved, "
            f"got {final_marker.to_audio_format().model_dump(mode='json')}"
        )
    if previous_chunk is None:
        raise VadNodeError("VAD received final marker before audio chunks")

    expected_seq = previous_chunk.next_seq
    expected_sample_index = previous_chunk.next_sample_index
    if final_marker.seq != expected_seq:
        raise VadNodeError(
            f"VAD final marker seq discontinuity: expected {expected_seq}, "
            f"got {final_marker.seq}"
        )
    if final_marker.sample_index != expected_sample_index:
        raise VadNodeError(
            "VAD final marker sample_index discontinuity: "
            f"expected {expected_sample_index}, got {final_marker.sample_index}"
        )


def _drain_dora_final_marker_send() -> None:
    # The DORA Python API exposes no output flush/ack. Keep the node alive briefly
    # after sending the explicit final marker so process teardown cannot race daemon
    # ingestion; activity probes still fail closed if that marker is not observed.
    time.sleep(DORA_FINAL_MARKER_DRAIN_SECONDS)


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise VadNodeError(f"DORA event field {key!r} must be a string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
