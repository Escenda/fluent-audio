"""DORA media graph node backed by an internal GStreamer pipeline."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from fluent_dialogue_dora.contracts import AudioChunk, AudioFormat, require_contiguous_audio_chunks
from fluent_dialogue_dora.dora import (
    DoraAudioFinalMarker,
    decode_audio_chunk_from_dora,
    encode_audio_chunk_for_dora,
    encode_audio_final_marker_for_dora,
    validate_dora_audio_final_marker,
    validate_dora_audio_metadata,
)

SYSTEM_GI_DIST_PACKAGES = Path("/usr/lib/python3/dist-packages")


class MediaGraphError(ValueError):
    """Raised when media graph processing cannot preserve the audio contract."""


class MediaGraphConfigError(MediaGraphError):
    """Raised when the media graph configuration is invalid."""


class MediaGraphInputError(MediaGraphError):
    """Raised when a DORA audio input event violates the configured stream."""


class MediaGraphGStreamerError(MediaGraphError):
    """Raised when GStreamer rejects or fails processing."""


class MediaGraphConfig(BaseModel):
    """Explicit configuration for a single media graph DORA node."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    input_source_id: str = Field(min_length=1)
    input_stream_id: str = Field(min_length=1)
    input_format: AudioFormat
    output_source_id: str = Field(min_length=1)
    output_stream_id: str = Field(min_length=1)
    output_format: AudioFormat
    output_start_seq: int = Field(default=0, ge=0)
    output_start_sample_index: int = Field(default=0, ge=0)
    output_start_capture_time_ns: int = Field(ge=0)
    enable_tap: bool = False
    tap_source_id: str | None = None
    tap_stream_id: str | None = None
    tap_start_seq: int = Field(default=0, ge=0)
    tap_start_sample_index: int = Field(default=0, ge=0)
    tap_start_capture_time_ns: int = Field(default=0, ge=0)
    linear_gain: float = Field(default=1.0, gt=0.0, le=10.0)
    pull_timeout_ms: int = Field(default=1_000, gt=0)

    @model_validator(mode="after")
    def validate_tap_contract(self) -> Self:
        if self.enable_tap:
            if self.tap_source_id is None or self.tap_source_id == "":
                raise ValueError("tap_source_id is required when enable_tap is true")
            if self.tap_stream_id is None or self.tap_stream_id == "":
                raise ValueError("tap_stream_id is required when enable_tap is true")
        else:
            if self.tap_source_id is not None or self.tap_stream_id is not None:
                raise ValueError("tap ids must not be set when enable_tap is false")
        return self


@dataclass
class MediaGraphRunSummary:
    input_chunks: int
    main_output_chunks: int
    tap_output_chunks: int


@dataclass
class InputClosureState:
    input_closed_before_final: bool = False
    stop_before_final: bool = False


@dataclass
class InputStreamState:
    config: MediaGraphConfig
    previous_chunk: AudioChunk | None = None
    chunks_seen: int = 0

    def accept_chunk(self, chunk: AudioChunk) -> None:
        if chunk.source_id != self.config.input_source_id:
            raise MediaGraphInputError(
                "Media graph input source mismatch: "
                f"expected {self.config.input_source_id!r}, got {chunk.source_id!r}"
            )
        if chunk.stream_id != self.config.input_stream_id:
            raise MediaGraphInputError(
                "Media graph input stream mismatch: "
                f"expected {self.config.input_stream_id!r}, got {chunk.stream_id!r}"
            )
        if chunk.format != self.config.input_format:
            raise MediaGraphInputError("Media graph input format mismatch")
        if self.previous_chunk is not None:
            require_contiguous_audio_chunks(self.previous_chunk, chunk)

        self.previous_chunk = chunk
        self.chunks_seen += 1

    def accept_final(self, marker: DoraAudioFinalMarker) -> None:
        if self.previous_chunk is None:
            raise MediaGraphInputError("Media graph received final marker before audio chunks")
        if marker.source_id != self.config.input_source_id:
            raise MediaGraphInputError(
                "Media graph final source mismatch: "
                f"expected {self.config.input_source_id!r}, got {marker.source_id!r}"
            )
        if marker.stream_id != self.config.input_stream_id:
            raise MediaGraphInputError(
                "Media graph final stream mismatch: "
                f"expected {self.config.input_stream_id!r}, got {marker.stream_id!r}"
            )
        if marker.to_audio_format() != self.config.input_format:
            raise MediaGraphInputError("Media graph final format mismatch")
        if marker.seq != self.previous_chunk.next_seq:
            raise MediaGraphInputError(
                "Media graph final seq mismatch: "
                f"expected {self.previous_chunk.next_seq}, got {marker.seq}"
            )
        if marker.sample_index != self.previous_chunk.next_sample_index:
            raise MediaGraphInputError(
                "Media graph final sample_index mismatch: "
                f"expected {self.previous_chunk.next_sample_index}, got {marker.sample_index}"
            )


@dataclass
class OutputStreamCursor:
    source_id: str
    stream_id: str
    audio_format: AudioFormat
    next_seq: int
    next_sample_index: int
    start_sample_index: int
    start_capture_time_ns: int
    chunks_sent: int = 0

    def send_payload(self, node, output_id: str, payload: bytes) -> None:
        frame_size_bytes = self.audio_format.frame_size_bytes
        if payload == b"":
            raise MediaGraphGStreamerError("GStreamer emitted an empty audio buffer")
        if len(payload) % frame_size_bytes != 0:
            raise MediaGraphGStreamerError(
                "GStreamer output buffer is not aligned to complete audio frames: "
                f"size={len(payload)}, frame_size_bytes={frame_size_bytes}"
            )

        frame_count = len(payload) // frame_size_bytes
        chunk = AudioChunk(
            source_id=self.source_id,
            stream_id=self.stream_id,
            seq=self.next_seq,
            sample_index=self.next_sample_index,
            capture_time_ns=self._capture_time_ns(),
            frame_count=frame_count,
            format=self.audio_format,
            payload=payload,
        )
        encoded_payload, metadata = encode_audio_chunk_for_dora(chunk)
        node.send_output(output_id, encoded_payload, metadata=metadata.to_dora_metadata())

        self.next_seq = chunk.next_seq
        self.next_sample_index = chunk.next_sample_index
        self.chunks_sent += 1

    def send_final(self, node, output_id: str) -> None:
        payload, metadata = encode_audio_final_marker_for_dora(
            source_id=self.source_id,
            stream_id=self.stream_id,
            seq=self.next_seq,
            sample_index=self.next_sample_index,
            capture_time_ns=self._capture_time_ns(),
            audio_format=self.audio_format,
        )
        node.send_output(output_id, payload, metadata=metadata.to_dora_metadata())

    def _capture_time_ns(self) -> int:
        frame_offset = self.next_sample_index - self.start_sample_index
        return (
            self.start_capture_time_ns
            + (frame_offset * 1_000_000_000) // self.audio_format.sample_rate_hz
        )


class GStreamerMediaGraph:
    """Push raw PCM through an appsrc/appsink GStreamer graph."""

    def __init__(self, config: MediaGraphConfig) -> None:
        self.config = config
        self.Gst = import_gstreamer()
        self.pipeline = self.Gst.parse_launch(build_pipeline_description(config))
        self.appsrc = self._required_element("audio_src")
        self.main_sink = self._required_element("audio_sink")
        self.tap_sink = self._optional_tap_sink()
        self.main_cursor = OutputStreamCursor(
            source_id=config.output_source_id,
            stream_id=config.output_stream_id,
            audio_format=config.output_format,
            next_seq=config.output_start_seq,
            next_sample_index=config.output_start_sample_index,
            start_sample_index=config.output_start_sample_index,
            start_capture_time_ns=config.output_start_capture_time_ns,
        )
        self.tap_cursor = self._build_tap_cursor()
        self._configure_caps()
        self._start_pipeline()

    def push_chunk(self, chunk: AudioChunk, node) -> None:
        buffer = self.Gst.Buffer.new_allocate(None, len(chunk.payload), None)
        buffer.fill(0, chunk.payload)
        buffer.pts = (chunk.sample_index * 1_000_000_000) // chunk.format.sample_rate_hz
        buffer.duration = (chunk.frame_count * 1_000_000_000) // chunk.format.sample_rate_hz

        flow_return = self.appsrc.emit("push-buffer", buffer)
        if flow_return != self.Gst.FlowReturn.OK:
            raise MediaGraphGStreamerError(f"GStreamer appsrc push failed: {flow_return}")
        self.drain_available(node)

    def finish(self, node) -> None:
        self.drain_available(node)
        flow_return = self.appsrc.emit("end-of-stream")
        if flow_return != self.Gst.FlowReturn.OK:
            raise MediaGraphGStreamerError(f"GStreamer appsrc EOS failed: {flow_return}")
        self._wait_for_eos_then_drain_empty(node)
        self.main_cursor.send_final(node, "audio")
        if self.tap_cursor is not None:
            self.tap_cursor.send_final(node, "tap_audio")

    def drain_available(self, node) -> bool:
        self._raise_pending_error()
        main_samples = self._drain_sink(self.main_sink, self.main_cursor, node, "audio")
        tap_samples = 0
        if self.tap_sink is not None and self.tap_cursor is not None:
            tap_samples = self._drain_sink(self.tap_sink, self.tap_cursor, node, "tap_audio")
        self._raise_pending_error()
        return main_samples == 0 and tap_samples == 0

    def close(self) -> None:
        self.pipeline.set_state(self.Gst.State.NULL)

    def _required_element(self, name: str):
        element = self.pipeline.get_by_name(name)
        if element is None:
            raise MediaGraphGStreamerError(f"GStreamer pipeline missing element {name!r}")
        return element

    def _optional_tap_sink(self):
        if not self.config.enable_tap:
            return None
        return self._required_element("tap_audio_sink")

    def _build_tap_cursor(self) -> OutputStreamCursor | None:
        if not self.config.enable_tap:
            return None
        if self.config.tap_source_id is None or self.config.tap_stream_id is None:
            raise MediaGraphConfigError("tap source and stream ids are required")
        return OutputStreamCursor(
            source_id=self.config.tap_source_id,
            stream_id=self.config.tap_stream_id,
            audio_format=self.config.output_format,
            next_seq=self.config.tap_start_seq,
            next_sample_index=self.config.tap_start_sample_index,
            start_sample_index=self.config.tap_start_sample_index,
            start_capture_time_ns=self.config.tap_start_capture_time_ns,
        )

    def _configure_caps(self) -> None:
        input_caps = self.Gst.Caps.from_string(build_audio_caps(self.config.input_format))
        output_caps = self.Gst.Caps.from_string(build_audio_caps(self.config.output_format))
        self.appsrc.set_property("caps", input_caps)
        self._required_element("input_caps").set_property("caps", input_caps)
        self._required_element("output_caps").set_property("caps", output_caps)

    def _start_pipeline(self) -> None:
        state_change = self.pipeline.set_state(self.Gst.State.PLAYING)
        if state_change == self.Gst.StateChangeReturn.FAILURE:
            raise MediaGraphGStreamerError("GStreamer pipeline failed to enter PLAYING")
        self._raise_pending_error()

    def _drain_sink(
        self,
        sink,
        cursor: OutputStreamCursor,
        node,
        output_id: str,
        timeout_ns: int = 0,
    ) -> int:
        samples_drained = 0
        while True:
            sample = sink.emit("try-pull-sample", timeout_ns)
            if sample is None:
                return samples_drained
            cursor.send_payload(node, output_id, sample_to_bytes(sample, self.Gst))
            samples_drained += 1

    def _wait_for_eos_then_drain_empty(self, node) -> None:
        self._wait_for_bus_eos()
        while True:
            if self._drain_after_eos_until_empty(node):
                return

    def _drain_after_eos_until_empty(self, node) -> bool:
        self._raise_pending_error()
        timeout_ns = self.config.pull_timeout_ms * 1_000_000
        main_samples = self._drain_sink(self.main_sink, self.main_cursor, node, "audio", timeout_ns)
        tap_samples = 0
        if self.tap_sink is not None and self.tap_cursor is not None:
            tap_samples = self._drain_sink(
                self.tap_sink,
                self.tap_cursor,
                node,
                "tap_audio",
                timeout_ns,
            )
        self._raise_pending_error()
        return main_samples == 0 and tap_samples == 0

    def _wait_for_bus_eos(self) -> None:
        bus = self.pipeline.get_bus()
        timeout_ns = self.config.pull_timeout_ms * 1_000_000
        while True:
            message = bus.timed_pop_filtered(
                timeout_ns,
                self.Gst.MessageType.ERROR | self.Gst.MessageType.EOS,
            )
            if message is None:
                raise MediaGraphGStreamerError("Timed out waiting for GStreamer EOS")
            if message.type == self.Gst.MessageType.ERROR:
                raise_gstreamer_message_error(message)
            if message.type == self.Gst.MessageType.EOS:
                return

    def _raise_pending_error(self) -> None:
        bus = self.pipeline.get_bus()
        message = bus.timed_pop_filtered(0, self.Gst.MessageType.ERROR)
        if message is not None:
            raise_gstreamer_message_error(message)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the fluent-dialogue-dora GStreamer media graph.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--input-source-id", required=True)
    parser.add_argument("--input-stream-id", required=True)
    parser.add_argument("--input-sample-rate-hz", required=True, type=int)
    parser.add_argument("--input-channels", required=True, type=int)
    parser.add_argument("--input-sample-format", required=True, choices=("s16le", "f32le"))
    parser.add_argument("--input-channel-layout", required=True, choices=("interleaved",))
    parser.add_argument("--output-source-id", required=True)
    parser.add_argument("--output-stream-id", required=True)
    parser.add_argument("--output-sample-rate-hz", required=True, type=int)
    parser.add_argument("--output-channels", required=True, type=int)
    parser.add_argument("--output-sample-format", required=True, choices=("s16le", "f32le"))
    parser.add_argument("--output-channel-layout", required=True, choices=("interleaved",))
    parser.add_argument("--output-start-seq", required=True, type=int)
    parser.add_argument("--output-start-sample-index", required=True, type=int)
    parser.add_argument("--output-start-capture-time-ns", required=True, type=int)
    parser.add_argument("--enable-tap", action="store_true")
    parser.add_argument("--tap-source-id")
    parser.add_argument("--tap-stream-id")
    parser.add_argument("--tap-start-seq", type=int, default=0)
    parser.add_argument("--tap-start-sample-index", type=int, default=0)
    parser.add_argument("--tap-start-capture-time-ns", type=int, default=0)
    parser.add_argument("--linear-gain", type=float, default=1.0)
    parser.add_argument("--pull-timeout-ms", type=int, default=1_000)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("media_graph requires --dora")

    from dora import Node

    run_media_graph_dora(Node(), config_from_args(args))
    return 0


def config_from_args(args: argparse.Namespace) -> MediaGraphConfig:
    return MediaGraphConfig(
        input_source_id=args.input_source_id,
        input_stream_id=args.input_stream_id,
        input_format=AudioFormat(
            sample_rate_hz=args.input_sample_rate_hz,
            channels=args.input_channels,
            sample_format=args.input_sample_format,
            channel_layout=args.input_channel_layout,
        ),
        output_source_id=args.output_source_id,
        output_stream_id=args.output_stream_id,
        output_format=AudioFormat(
            sample_rate_hz=args.output_sample_rate_hz,
            channels=args.output_channels,
            sample_format=args.output_sample_format,
            channel_layout=args.output_channel_layout,
        ),
        output_start_seq=args.output_start_seq,
        output_start_sample_index=args.output_start_sample_index,
        output_start_capture_time_ns=args.output_start_capture_time_ns,
        enable_tap=args.enable_tap,
        tap_source_id=args.tap_source_id,
        tap_stream_id=args.tap_stream_id,
        tap_start_seq=args.tap_start_seq,
        tap_start_sample_index=args.tap_start_sample_index,
        tap_start_capture_time_ns=args.tap_start_capture_time_ns,
        linear_gain=args.linear_gain,
        pull_timeout_ms=args.pull_timeout_ms,
    )


def run_media_graph_dora(node, config: MediaGraphConfig) -> MediaGraphRunSummary:
    return run_media_graph_events(node, node, config)


def run_media_graph_events(
    events,
    output_node,
    config: MediaGraphConfig,
) -> MediaGraphRunSummary:
    input_state = InputStreamState(config=config)
    closure_state = InputClosureState()
    graph: GStreamerMediaGraph | None = None
    completed_summary: MediaGraphRunSummary | None = None
    try:
        for event in events:
            if event is None:
                break

            event_type = required_event_text(event, "type")
            if event_type == "STOP":
                if completed_summary is not None:
                    return completed_summary
                closure_state.stop_before_final = True
                continue
            if event_type == "INPUT_CLOSED":
                input_id = required_event_text(event, "id")
                if input_id != "audio":
                    raise MediaGraphInputError(f"Unexpected DORA input id: {input_id!r}")
                if completed_summary is not None:
                    return completed_summary
                closure_state.input_closed_before_final = True
                continue
            if event_type != "INPUT":
                continue

            if completed_summary is not None:
                raise MediaGraphInputError("DORA audio input arrived after final marker")

            input_id = required_event_text(event, "id")
            if input_id != "audio":
                raise MediaGraphInputError(f"Unexpected DORA input id: {input_id!r}")

            payload = event.get("value")
            metadata = validate_dora_audio_metadata(event.get("metadata"))
            if metadata.final:
                final_marker = validate_dora_audio_final_marker(payload, metadata)
                input_state.accept_final(final_marker)
                if graph is None:
                    raise MediaGraphInputError(
                        "Media graph received final marker before graph start"
                    )
                graph.finish(output_node)
                completed_summary = MediaGraphRunSummary(
                    input_chunks=input_state.chunks_seen,
                    main_output_chunks=graph.main_cursor.chunks_sent,
                    tap_output_chunks=graph.tap_cursor.chunks_sent
                    if graph.tap_cursor is not None
                    else 0,
                )
                continue

            chunk = decode_audio_chunk_from_dora(payload, metadata)
            input_state.accept_chunk(chunk)
            if graph is None:
                graph = GStreamerMediaGraph(config)
            graph.push_chunk(chunk, output_node)

        if completed_summary is not None:
            return completed_summary
        if closure_state.input_closed_before_final:
            raise MediaGraphInputError("DORA audio input closed before explicit final marker")
        if closure_state.stop_before_final:
            raise MediaGraphInputError("DORA STOP arrived before explicit final marker")
        raise MediaGraphInputError("DORA audio stream ended without explicit final marker")
    finally:
        if graph is not None:
            graph.close()


def build_pipeline_description(config: MediaGraphConfig) -> str:
    appsrc = "appsrc name=audio_src is-live=false format=time block=true do-timestamp=false"
    processing = (
        "! capsfilter name=input_caps ! audioconvert "
        f"! volume name=audio_gain volume={config.linear_gain:g} "
        "! audioresample ! capsfilter name=output_caps"
    )
    appsink = "appsink name=audio_sink emit-signals=false sync=false async=false wait-on-eos=false"
    if not config.enable_tap:
        return f"{appsrc} {processing} ! {appsink}"

    tap_sink = (
        "appsink name=tap_audio_sink emit-signals=false sync=false async=false wait-on-eos=false"
    )
    queue_limits = "max-size-buffers=8 max-size-bytes=0 max-size-time=0"
    return (
        f"{appsrc} {processing} ! tee name=audio_tee "
        f"audio_tee. ! queue name=audio_queue {queue_limits} ! {appsink} "
        f"audio_tee. ! queue name=tap_audio_queue {queue_limits} ! {tap_sink}"
    )


def build_audio_caps(audio_format: AudioFormat) -> str:
    return (
        "audio/x-raw,"
        f"format={sample_format_to_gst(audio_format.sample_format)},"
        f"rate={audio_format.sample_rate_hz},"
        f"channels={audio_format.channels},"
        f"layout={channel_layout_to_gst(audio_format.channel_layout)}"
    )


def sample_format_to_gst(sample_format: str) -> str:
    if sample_format == "s16le":
        return "S16LE"
    if sample_format == "f32le":
        return "F32LE"
    raise MediaGraphConfigError(f"Unsupported GStreamer sample format: {sample_format!r}")


def channel_layout_to_gst(channel_layout: str) -> str:
    if channel_layout == "interleaved":
        return "interleaved"
    raise MediaGraphConfigError(f"Unsupported GStreamer channel layout: {channel_layout!r}")


def sample_to_bytes(sample, Gst) -> bytes:
    buffer = sample.get_buffer()
    if buffer is None:
        raise MediaGraphGStreamerError("GStreamer sample did not contain a buffer")
    mapped, map_info = buffer.map(Gst.MapFlags.READ)
    if not mapped:
        raise MediaGraphGStreamerError("GStreamer buffer could not be mapped for reading")
    try:
        return bytes(map_info.data)
    finally:
        buffer.unmap(map_info)


def import_gstreamer():
    system_gi_path = str(SYSTEM_GI_DIST_PACKAGES)
    if system_gi_path not in sys.path:
        sys.path.append(system_gi_path)

    import gi

    gi.require_version("Gst", "1.0")
    from gi.repository import Gst

    Gst.init(None)
    return Gst


def raise_gstreamer_message_error(message) -> None:
    error, debug = message.parse_error()
    raise MediaGraphGStreamerError(f"GStreamer error: {error.message}; debug={debug}")


def required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise MediaGraphInputError(f"DORA event field {key!r} must be a string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
