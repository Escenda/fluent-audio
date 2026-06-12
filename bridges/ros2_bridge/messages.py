"""ROS2 projection models for fluent-audio bridge boundaries.

These models mirror the intended ROS2 messages without importing rclpy or generated
ROS packages. The executable ROS2 node can translate these validated projections to
generated message classes at the outermost boundary.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBytes, StringConstraints, model_validator

from fluent_audio.contracts import (
    AgentApprovalRequest,
    AgentCancelRequest,
    AgentTextDelta,
    AgentToolEvent,
    AgentTurnDone,
    AsrCancel,
    AsrStart,
    AsrStop,
    AudioChunk,
    AudioFormat,
    DialogueEvent,
    PlaybackClear,
    PlaybackPause,
    PlaybackResume,
    PlaybackStop,
    PlaybackDone,
    PlaybackState,
    TranscriptDelta,
    TranscriptFinal,
    TranscriptPartial,
    TurnEvent,
    VoiceActivityEvent,
    VoiceSessionEvent,
)

NonEmptyString = Annotated[str, StringConstraints(min_length=1)]
Ros2AudioEncoding = Literal["PCM16LE", "FLOAT32LE"]
Ros2AudioLayout = Literal["interleaved"]
Ros2AsrAction = Literal["start", "stop", "cancel"]
Ros2TranscriptKind = Literal["delta", "partial", "final", "stream_final"]
Ros2PlaybackCommandName = Literal["stop", "pause", "resume", "clear"]


class Ros2BridgeMessageError(ValueError):
    """Raised when a ROS2 projection cannot preserve a fluent-audio contract."""


class Ros2Time(BaseModel):
    """Minimal ROS builtin_interfaces/Time equivalent."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    sec: int = Field(ge=0)
    nanosec: int = Field(ge=0, lt=1_000_000_000)

    @classmethod
    def from_unix_ns(cls, timestamp_ns: int) -> "Ros2Time":
        if timestamp_ns < 0:
            raise Ros2BridgeMessageError("timestamp_ns must be non-negative")
        return cls(sec=timestamp_ns // 1_000_000_000, nanosec=timestamp_ns % 1_000_000_000)

    def to_unix_ns(self) -> int:
        return (self.sec * 1_000_000_000) + self.nanosec


class Ros2Header(BaseModel):
    """Minimal std_msgs/Header equivalent."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    stamp: Ros2Time
    frame_id: str = ""


class Ros2AudioFrame(BaseModel):
    """ROS-facing raw audio frame or explicit stream final marker."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    header: Ros2Header
    source_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    sample_index: int = Field(ge=0)
    capture_time_ns: int = Field(ge=0)
    frame_count: int = Field(ge=0)
    encoding: Ros2AudioEncoding
    sample_rate_hz: int = Field(gt=0)
    channels: int = Field(gt=0)
    bit_depth: int = Field(gt=0)
    layout: Ros2AudioLayout
    data: StrictBytes
    final: bool

    @model_validator(mode="after")
    def validate_audio_frame(self) -> "Ros2AudioFrame":
        if self.capture_time_ns != self.header.stamp.to_unix_ns():
            raise ValueError("Ros2AudioFrame capture_time_ns must equal header stamp")
        expected_bit_depth = _bit_depth_from_ros_encoding(self.encoding)
        if self.bit_depth != expected_bit_depth:
            raise ValueError(
                "Ros2AudioFrame bit_depth mismatch: "
                f"expected {expected_bit_depth} for {self.encoding}, got {self.bit_depth}"
            )
        if self.final:
            if self.frame_count != 0:
                raise ValueError("Ros2AudioFrame final marker must have frame_count=0")
            if self.data != b"":
                raise ValueError("Ros2AudioFrame final marker must have empty data")
            return self
        if self.frame_count == 0:
            raise ValueError("Ros2AudioFrame data frame must have frame_count > 0")
        expected_bytes = self.frame_count * self.channels * (self.bit_depth // 8)
        if len(self.data) != expected_bytes:
            raise ValueError(
                "Ros2AudioFrame data size mismatch: "
                f"expected {expected_bytes} bytes, got {len(self.data)}"
            )
        return self

    def audio_format(self) -> AudioFormat:
        return AudioFormat(
            sample_rate_hz=self.sample_rate_hz,
            channels=self.channels,
            sample_format=_sample_format_from_ros_encoding(self.encoding),
            channel_layout=self.layout,
        )


class Ros2VoiceActivity(BaseModel):
    """ROS-facing voice activity event or explicit stream final marker."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    header: Ros2Header
    source_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    sample_index: int = Field(ge=0)
    frame_count: int = Field(ge=0)
    state: Literal["silence", "speech"]
    speech_probability: float = Field(ge=0.0, le=1.0)
    final: bool

    @model_validator(mode="after")
    def validate_final_marker(self) -> "Ros2VoiceActivity":
        if self.final:
            if self.frame_count != 0:
                raise ValueError("Ros2VoiceActivity final marker must have frame_count=0")
            if self.state != "silence":
                raise ValueError("Ros2VoiceActivity final marker must have state='silence'")
            if self.speech_probability != 0.0:
                raise ValueError("Ros2VoiceActivity final marker must have speech_probability=0.0")
        elif self.frame_count == 0:
            raise ValueError("Ros2VoiceActivity event must have frame_count > 0")
        return self


class Ros2TurnEvent(BaseModel):
    """ROS-facing turn boundary event or explicit stream final marker."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    header: Ros2Header
    session_id: NonEmptyString
    user_turn_id: str
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    sample_index: int = Field(ge=0)
    state: Literal["idle", "started", "active", "ended", "cancelled"]
    confidence_present: bool
    confidence: float = Field(ge=0.0, le=1.0)
    final: bool

    @model_validator(mode="after")
    def validate_turn_fields(self) -> "Ros2TurnEvent":
        if self.final:
            if self.user_turn_id != "":
                raise ValueError("Ros2TurnEvent final marker must have empty user_turn_id")
            if self.state != "idle":
                raise ValueError("Ros2TurnEvent final marker must have state='idle'")
            if self.confidence_present:
                raise ValueError("Ros2TurnEvent final marker must not carry confidence")
        elif self.user_turn_id == "":
            raise ValueError("Ros2TurnEvent event requires non-empty user_turn_id")
        if not self.confidence_present and self.confidence != 0.0:
            raise ValueError("Ros2TurnEvent confidence must be 0.0 when absent")
        return self


class Ros2AsrControl(BaseModel):
    """ROS-facing ASR lifecycle command."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    header: Ros2Header
    action: Ros2AsrAction
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    start_sample_index: int = Field(ge=0)
    stop_sample_index: int = Field(ge=0)
    reason: str

    @model_validator(mode="after")
    def validate_action_fields(self) -> "Ros2AsrControl":
        if self.action == "start":
            if self.stop_sample_index != 0:
                raise ValueError("Ros2AsrControl start must have stop_sample_index=0")
            if self.reason != "":
                raise ValueError("Ros2AsrControl start must have empty reason")
        elif self.action == "stop":
            if self.start_sample_index != 0:
                raise ValueError("Ros2AsrControl stop must have start_sample_index=0")
            if self.reason != "":
                raise ValueError("Ros2AsrControl stop must have empty reason")
        elif self.action == "cancel":
            if self.start_sample_index != 0 or self.stop_sample_index != 0:
                raise ValueError("Ros2AsrControl cancel must not carry sample bounds")
            if self.reason == "":
                raise ValueError("Ros2AsrControl cancel requires reason")
        return self


class Ros2Transcript(BaseModel):
    """ROS-facing ASR transcript event or explicit stream final marker."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    header: Ros2Header
    kind: Ros2TranscriptKind
    session_id: NonEmptyString
    user_turn_id: str
    stream_id: NonEmptyString
    seq: int = Field(ge=0)
    text: str
    start_sample_index: int = Field(ge=0)
    end_sample_index: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_transcript_kind(self) -> "Ros2Transcript":
        if self.kind == "delta":
            if self.user_turn_id == "":
                raise ValueError("Ros2Transcript delta requires user_turn_id")
            if self.text == "":
                raise ValueError("Ros2Transcript delta requires text")
            if self.start_sample_index != 0 or self.end_sample_index != 0:
                raise ValueError("Ros2Transcript delta must not carry sample bounds")
        elif self.kind == "final":
            if self.user_turn_id == "":
                raise ValueError("Ros2Transcript final requires user_turn_id")
            if self.text == "":
                raise ValueError("Ros2Transcript final requires text")
            if self.end_sample_index <= self.start_sample_index:
                raise ValueError("Ros2Transcript final requires end > start")
        elif self.kind == "stream_final":
            if self.user_turn_id != "":
                raise ValueError("Ros2Transcript stream_final must have empty user_turn_id")
            if self.text != "":
                raise ValueError("Ros2Transcript stream_final must have empty text")
            if self.end_sample_index != self.start_sample_index:
                raise ValueError("Ros2Transcript stream_final requires equal bounds")
        return self


class Ros2VoiceSessionEvent(BaseModel):
    """ROS-facing session state projection."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    header: Ros2Header
    event: str = Field(min_length=1)
    state: str = Field(min_length=1)
    seq: int = Field(ge=0)
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    assistant_turn_id: str
    message: str


class Ros2DialogueEvent(BaseModel):
    """ROS-facing dialogue and agent surface event."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    header: Ros2Header
    event: str = Field(min_length=1)
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    seq: int = Field(ge=0)
    text: str
    request_id: str
    message: str


class Ros2AgentTextDelta(BaseModel):
    """ROS-facing streaming agent text delta."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    header: Ros2Header
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    agent_turn_id: NonEmptyString
    seq: int = Field(ge=0)
    text: NonEmptyString


class Ros2AgentTurnDone(BaseModel):
    """ROS-facing terminal agent turn event."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    header: Ros2Header
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    agent_turn_id: NonEmptyString
    seq: int = Field(ge=0)
    status: Literal["completed", "cancelled", "failed"]
    message: str

    @model_validator(mode="after")
    def validate_message(self) -> "Ros2AgentTurnDone":
        if self.status == "failed" and self.message == "":
            raise ValueError("Ros2AgentTurnDone failed requires message")
        if self.status == "completed" and self.message != "":
            raise ValueError("Ros2AgentTurnDone completed must not carry message")
        return self


class Ros2AgentApprovalRequest(BaseModel):
    """ROS-facing approval request for robot or tool actions."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    header: Ros2Header
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    approval_id: NonEmptyString
    seq: int = Field(ge=0)
    prompt: NonEmptyString
    action_label: NonEmptyString


class Ros2AgentCancelRequest(BaseModel):
    """ROS-facing cancellation request for an active agent turn."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    header: Ros2Header
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    seq: int = Field(ge=0)
    reason_present: bool
    reason: str

    @model_validator(mode="after")
    def validate_reason(self) -> "Ros2AgentCancelRequest":
        if self.reason_present:
            if self.reason == "":
                raise ValueError("Ros2AgentCancelRequest reason is required when present")
        elif self.reason != "":
            raise ValueError("Ros2AgentCancelRequest reason must be empty when absent")
        return self


class Ros2AgentToolEvent(BaseModel):
    """ROS-facing agent tool execution event."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    header: Ros2Header
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    tool_call_id: NonEmptyString
    tool_name: NonEmptyString
    event: Literal["started", "completed", "failed"]
    seq: int = Field(ge=0)
    summary: str
    error_message: str

    @model_validator(mode="after")
    def validate_error_fields(self) -> "Ros2AgentToolEvent":
        if self.event == "failed" and self.error_message == "":
            raise ValueError("Ros2AgentToolEvent failed requires error_message")
        if self.event != "failed" and self.error_message != "":
            raise ValueError("Ros2AgentToolEvent error_message is only valid for failed events")
        return self


class Ros2PlaybackState(BaseModel):
    """ROS-facing playback state projection."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    header: Ros2Header
    request_id: NonEmptyString
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    stream_id: NonEmptyString
    state: Literal["queued", "playing", "paused", "stopped", "completed", "cancelled", "failed"]
    seq: int = Field(ge=0)
    played_frames: int = Field(ge=0)
    reason: str

    @model_validator(mode="after")
    def validate_reason(self) -> "Ros2PlaybackState":
        if self.state == "failed" and self.reason == "":
            raise ValueError("Ros2PlaybackState failed requires reason")
        if self.state != "failed" and self.reason != "":
            raise ValueError("Ros2PlaybackState reason is only valid for failed state")
        return self


class Ros2PlaybackCommand(BaseModel):
    """ROS-facing playback control command."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    header: Ros2Header
    command: Ros2PlaybackCommandName
    request_id: NonEmptyString
    stream_id: NonEmptyString
    seq: int = Field(ge=0)


class Ros2PlaybackDone(BaseModel):
    """ROS-facing terminal playback report."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    header: Ros2Header
    request_id: NonEmptyString
    session_id: NonEmptyString
    user_turn_id: NonEmptyString
    stream_id: NonEmptyString
    status: Literal["completed", "stopped", "cancelled", "failed"]
    final_sequence_present: bool
    final_sequence: int = Field(ge=0)
    total_frames_present: bool
    total_frames: int = Field(ge=0)
    reason: str

    @model_validator(mode="after")
    def validate_done_fields(self) -> "Ros2PlaybackDone":
        if not self.final_sequence_present and not self.total_frames_present:
            raise ValueError("Ros2PlaybackDone requires final_sequence or total_frames")
        if self.status == "failed" and self.reason == "":
            raise ValueError("Ros2PlaybackDone failed requires reason")
        if self.status != "failed" and self.reason != "":
            raise ValueError("Ros2PlaybackDone reason is only valid for failed status")
        return self


def audio_chunk_to_ros2(chunk: AudioChunk) -> Ros2AudioFrame:
    return Ros2AudioFrame(
        header=_header_from_ns(chunk.capture_time_ns, frame_id=chunk.stream_id),
        source_id=chunk.source_id,
        stream_id=chunk.stream_id,
        seq=chunk.seq,
        sample_index=chunk.sample_index,
        capture_time_ns=chunk.capture_time_ns,
        frame_count=chunk.frame_count,
        encoding=_ros_encoding_from_sample_format(chunk.format.sample_format),
        sample_rate_hz=chunk.format.sample_rate_hz,
        channels=chunk.format.channels,
        bit_depth=chunk.format.bytes_per_sample * 8,
        layout=chunk.format.channel_layout,
        data=chunk.payload,
        final=False,
    )


def audio_final_marker_to_ros2(
    *,
    source_id: str,
    stream_id: str,
    seq: int,
    sample_index: int,
    capture_time_ns: int,
    audio_format: AudioFormat,
) -> Ros2AudioFrame:
    return Ros2AudioFrame(
        header=_header_from_ns(capture_time_ns, frame_id=stream_id),
        source_id=source_id,
        stream_id=stream_id,
        seq=seq,
        sample_index=sample_index,
        capture_time_ns=capture_time_ns,
        frame_count=0,
        encoding=_ros_encoding_from_sample_format(audio_format.sample_format),
        sample_rate_hz=audio_format.sample_rate_hz,
        channels=audio_format.channels,
        bit_depth=audio_format.bytes_per_sample * 8,
        layout=audio_format.channel_layout,
        data=b"",
        final=True,
    )


def ros2_audio_to_chunk(frame: Ros2AudioFrame) -> AudioChunk:
    if frame.final:
        raise Ros2BridgeMessageError("Ros2AudioFrame final marker is not an AudioChunk")
    return AudioChunk(
        source_id=frame.source_id,
        stream_id=frame.stream_id,
        seq=frame.seq,
        sample_index=frame.sample_index,
        capture_time_ns=frame.capture_time_ns,
        frame_count=frame.frame_count,
        format=frame.audio_format(),
        payload=frame.data,
    )


def voice_activity_to_ros2(
    event: VoiceActivityEvent,
    *,
    timestamp_ns: int,
) -> Ros2VoiceActivity:
    return Ros2VoiceActivity(
        header=_header_from_ns(timestamp_ns, frame_id=event.stream_id),
        source_id=event.source_id,
        stream_id=event.stream_id,
        seq=event.seq,
        sample_index=event.sample_index,
        frame_count=event.frame_count,
        state=event.state,
        speech_probability=event.speech_probability,
        final=False,
    )


def voice_activity_final_marker_to_ros2(
    *,
    source_id: str,
    stream_id: str,
    seq: int,
    sample_index: int,
    timestamp_ns: int,
) -> Ros2VoiceActivity:
    return Ros2VoiceActivity(
        header=_header_from_ns(timestamp_ns, frame_id=stream_id),
        source_id=source_id,
        stream_id=stream_id,
        seq=seq,
        sample_index=sample_index,
        frame_count=0,
        state="silence",
        speech_probability=0.0,
        final=True,
    )


def ros2_voice_activity_to_event(message: Ros2VoiceActivity) -> VoiceActivityEvent:
    if message.final:
        raise Ros2BridgeMessageError("Ros2VoiceActivity final marker is not a VoiceActivityEvent")
    return VoiceActivityEvent(
        source_id=message.source_id,
        stream_id=message.stream_id,
        seq=message.seq,
        sample_index=message.sample_index,
        frame_count=message.frame_count,
        state=message.state,
        speech_probability=message.speech_probability,
    )


def turn_event_to_ros2(event: TurnEvent, *, timestamp_ns: int) -> Ros2TurnEvent:
    confidence_present = event.confidence is not None
    return Ros2TurnEvent(
        header=_header_from_ns(timestamp_ns, frame_id=event.stream_id),
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        stream_id=event.stream_id,
        seq=event.seq,
        sample_index=event.sample_index,
        state=event.state,
        confidence_present=confidence_present,
        confidence=event.confidence if confidence_present else 0.0,
        final=False,
    )


def turn_final_marker_to_ros2(
    *,
    session_id: str,
    stream_id: str,
    seq: int,
    sample_index: int,
    timestamp_ns: int,
) -> Ros2TurnEvent:
    return Ros2TurnEvent(
        header=_header_from_ns(timestamp_ns, frame_id=stream_id),
        session_id=session_id,
        user_turn_id="",
        stream_id=stream_id,
        seq=seq,
        sample_index=sample_index,
        state="idle",
        confidence_present=False,
        confidence=0.0,
        final=True,
    )


def ros2_turn_to_event(message: Ros2TurnEvent) -> TurnEvent:
    if message.final:
        raise Ros2BridgeMessageError("Ros2TurnEvent final marker is not a TurnEvent")
    return TurnEvent(
        session_id=message.session_id,
        user_turn_id=message.user_turn_id,
        stream_id=message.stream_id,
        seq=message.seq,
        sample_index=message.sample_index,
        state=message.state,
        confidence=message.confidence if message.confidence_present else None,
    )


def asr_control_to_ros2(
    control: AsrStart | AsrStop | AsrCancel,
    *,
    timestamp_ns: int,
) -> Ros2AsrControl:
    if isinstance(control, AsrStart):
        return Ros2AsrControl(
            header=_header_from_ns(timestamp_ns, frame_id=control.stream_id),
            action="start",
            session_id=control.session_id,
            user_turn_id=control.user_turn_id,
            stream_id=control.stream_id,
            seq=control.seq,
            start_sample_index=control.start_sample_index,
            stop_sample_index=0,
            reason="",
        )
    if isinstance(control, AsrStop):
        return Ros2AsrControl(
            header=_header_from_ns(timestamp_ns, frame_id=control.stream_id),
            action="stop",
            session_id=control.session_id,
            user_turn_id=control.user_turn_id,
            stream_id=control.stream_id,
            seq=control.seq,
            start_sample_index=0,
            stop_sample_index=control.stop_sample_index,
            reason="",
        )
    return Ros2AsrControl(
        header=_header_from_ns(timestamp_ns, frame_id=control.stream_id),
        action="cancel",
        session_id=control.session_id,
        user_turn_id=control.user_turn_id,
        stream_id=control.stream_id,
        seq=control.seq,
        start_sample_index=0,
        stop_sample_index=0,
        reason=control.reason,
    )


def ros2_asr_control_to_contract(message: Ros2AsrControl) -> AsrStart | AsrStop | AsrCancel:
    if message.action == "start":
        return AsrStart(
            action="start",
            session_id=message.session_id,
            user_turn_id=message.user_turn_id,
            stream_id=message.stream_id,
            seq=message.seq,
            start_sample_index=message.start_sample_index,
        )
    if message.action == "stop":
        return AsrStop(
            action="stop",
            session_id=message.session_id,
            user_turn_id=message.user_turn_id,
            stream_id=message.stream_id,
            seq=message.seq,
            stop_sample_index=message.stop_sample_index,
        )
    return AsrCancel(
        action="cancel",
        session_id=message.session_id,
        user_turn_id=message.user_turn_id,
        stream_id=message.stream_id,
        seq=message.seq,
        reason=message.reason,
    )


def transcript_delta_to_ros2(event: TranscriptDelta, *, timestamp_ns: int) -> Ros2Transcript:
    return Ros2Transcript(
        header=_header_from_ns(timestamp_ns, frame_id=event.stream_id),
        kind="delta",
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        stream_id=event.stream_id,
        seq=event.seq,
        text=event.text,
        start_sample_index=0,
        end_sample_index=0,
    )


def transcript_partial_to_ros2(event: TranscriptPartial, *, timestamp_ns: int) -> Ros2Transcript:
    return Ros2Transcript(
        header=_header_from_ns(timestamp_ns, frame_id=event.stream_id),
        kind="partial",
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        stream_id=event.stream_id,
        seq=event.seq,
        text=event.text,
        start_sample_index=0,
        end_sample_index=0,
    )


def transcript_final_to_ros2(event: TranscriptFinal, *, timestamp_ns: int) -> Ros2Transcript:
    return Ros2Transcript(
        header=_header_from_ns(timestamp_ns, frame_id=event.stream_id),
        kind="final",
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        stream_id=event.stream_id,
        seq=event.seq,
        text=event.text,
        start_sample_index=event.start_sample_index,
        end_sample_index=event.end_sample_index,
    )


def transcript_stream_final_to_ros2(
    *,
    session_id: str,
    stream_id: str,
    seq: int,
    sample_index: int,
    timestamp_ns: int,
) -> Ros2Transcript:
    return Ros2Transcript(
        header=_header_from_ns(timestamp_ns, frame_id=stream_id),
        kind="stream_final",
        session_id=session_id,
        user_turn_id="",
        stream_id=stream_id,
        seq=seq,
        text="",
        start_sample_index=sample_index,
        end_sample_index=sample_index,
    )


def ros2_transcript_to_contract(
    message: Ros2Transcript,
) -> TranscriptDelta | TranscriptPartial | TranscriptFinal:
    if message.kind == "stream_final":
        raise Ros2BridgeMessageError("Ros2Transcript stream_final marker is not a transcript")
    if message.kind == "delta":
        return TranscriptDelta(
            session_id=message.session_id,
            user_turn_id=message.user_turn_id,
            stream_id=message.stream_id,
            seq=message.seq,
            text=message.text,
        )
    if message.kind == "partial":
        return TranscriptPartial(
            session_id=message.session_id,
            user_turn_id=message.user_turn_id,
            stream_id=message.stream_id,
            seq=message.seq,
            text=message.text,
        )
    return TranscriptFinal(
        session_id=message.session_id,
        user_turn_id=message.user_turn_id,
        stream_id=message.stream_id,
        seq=message.seq,
        text=message.text,
        start_sample_index=message.start_sample_index,
        end_sample_index=message.end_sample_index,
    )


def voice_session_event_to_ros2(
    event: VoiceSessionEvent,
    *,
    timestamp_ns: int,
) -> Ros2VoiceSessionEvent:
    return Ros2VoiceSessionEvent(
        header=_header_from_ns(timestamp_ns, frame_id=event.turn_ids.session_id),
        event=event.event,
        state=event.state,
        seq=event.seq,
        session_id=event.turn_ids.session_id,
        user_turn_id=event.turn_ids.user_turn_id,
        assistant_turn_id=event.turn_ids.assistant_turn_id or "",
        message=event.message or "",
    )


def dialogue_event_to_ros2(event: DialogueEvent, *, timestamp_ns: int) -> Ros2DialogueEvent:
    return Ros2DialogueEvent(
        header=_header_from_ns(timestamp_ns, frame_id=event.session_id),
        event=event.event,
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        seq=event.seq,
        text=event.text or "",
        request_id=event.request_id or "",
        message=event.message or "",
    )


def agent_text_delta_to_ros2(event: AgentTextDelta, *, timestamp_ns: int) -> Ros2AgentTextDelta:
    return Ros2AgentTextDelta(
        header=_header_from_ns(timestamp_ns, frame_id=event.session_id),
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        agent_turn_id=event.agent_turn_id,
        seq=event.seq,
        text=event.text,
    )


def agent_turn_done_to_ros2(
    event: AgentTurnDone,
    *,
    timestamp_ns: int,
) -> Ros2AgentTurnDone:
    return Ros2AgentTurnDone(
        header=_header_from_ns(timestamp_ns, frame_id=event.session_id),
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        agent_turn_id=event.agent_turn_id,
        seq=event.seq,
        status=event.status,
        message=event.message or "",
    )


def agent_approval_request_to_ros2(
    event: AgentApprovalRequest,
    *,
    timestamp_ns: int,
) -> Ros2AgentApprovalRequest:
    return Ros2AgentApprovalRequest(
        header=_header_from_ns(timestamp_ns, frame_id=event.session_id),
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        approval_id=event.approval_id,
        seq=event.seq,
        prompt=event.prompt,
        action_label=event.action_label,
    )


def agent_cancel_request_to_ros2(
    event: AgentCancelRequest,
    *,
    timestamp_ns: int,
) -> Ros2AgentCancelRequest:
    reason_present = event.reason is not None
    return Ros2AgentCancelRequest(
        header=_header_from_ns(timestamp_ns, frame_id=event.session_id),
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        seq=event.seq,
        reason_present=reason_present,
        reason=event.reason if reason_present else "",
    )


def ros2_agent_cancel_request_to_contract(message: Ros2AgentCancelRequest) -> AgentCancelRequest:
    return AgentCancelRequest(
        session_id=message.session_id,
        user_turn_id=message.user_turn_id,
        seq=message.seq,
        reason=message.reason if message.reason_present else None,
    )


def agent_tool_event_to_ros2(event: AgentToolEvent, *, timestamp_ns: int) -> Ros2AgentToolEvent:
    return Ros2AgentToolEvent(
        header=_header_from_ns(timestamp_ns, frame_id=event.session_id),
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        tool_call_id=event.tool_call_id,
        tool_name=event.tool_name,
        event=event.event,
        seq=event.seq,
        summary=event.summary or "",
        error_message=event.error_message or "",
    )


def playback_state_to_ros2(event: PlaybackState, *, timestamp_ns: int) -> Ros2PlaybackState:
    return Ros2PlaybackState(
        header=_header_from_ns(timestamp_ns, frame_id=event.stream_id),
        request_id=event.request_id,
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        stream_id=event.stream_id,
        state=event.state,
        seq=event.seq,
        played_frames=event.played_frames,
        reason=event.reason or "",
    )


def playback_command_to_ros2(
    event: PlaybackStop | PlaybackPause | PlaybackResume | PlaybackClear,
    *,
    timestamp_ns: int,
) -> Ros2PlaybackCommand:
    return Ros2PlaybackCommand(
        header=_header_from_ns(timestamp_ns, frame_id=event.stream_id),
        command=event.command,
        request_id=event.request_id,
        stream_id=event.stream_id,
        seq=event.seq,
    )


def ros2_playback_command_to_contract(
    message: Ros2PlaybackCommand,
) -> PlaybackStop | PlaybackPause | PlaybackResume | PlaybackClear:
    if message.command == "stop":
        return PlaybackStop(
            command="stop",
            request_id=message.request_id,
            stream_id=message.stream_id,
            seq=message.seq,
        )
    if message.command == "pause":
        return PlaybackPause(
            command="pause",
            request_id=message.request_id,
            stream_id=message.stream_id,
            seq=message.seq,
        )
    if message.command == "resume":
        return PlaybackResume(
            command="resume",
            request_id=message.request_id,
            stream_id=message.stream_id,
            seq=message.seq,
        )
    return PlaybackClear(
        command="clear",
        request_id=message.request_id,
        stream_id=message.stream_id,
        seq=message.seq,
    )


def playback_done_to_ros2(event: PlaybackDone, *, timestamp_ns: int) -> Ros2PlaybackDone:
    final_sequence_present = event.final_sequence is not None
    total_frames_present = event.total_frames is not None
    return Ros2PlaybackDone(
        header=_header_from_ns(timestamp_ns, frame_id=event.stream_id),
        request_id=event.request_id,
        session_id=event.session_id,
        user_turn_id=event.user_turn_id,
        stream_id=event.stream_id,
        status=event.status,
        final_sequence_present=final_sequence_present,
        final_sequence=event.final_sequence if final_sequence_present else 0,
        total_frames_present=total_frames_present,
        total_frames=event.total_frames if total_frames_present else 0,
        reason=event.reason or "",
    )


def _header_from_ns(timestamp_ns: int, *, frame_id: str) -> Ros2Header:
    return Ros2Header(stamp=Ros2Time.from_unix_ns(timestamp_ns), frame_id=frame_id)


def _ros_encoding_from_sample_format(sample_format: str) -> Ros2AudioEncoding:
    if sample_format == "s16le":
        return "PCM16LE"
    if sample_format == "f32le":
        return "FLOAT32LE"
    raise Ros2BridgeMessageError(f"Unsupported sample_format for ROS2 bridge: {sample_format}")


def _sample_format_from_ros_encoding(encoding: str) -> Literal["s16le", "f32le"]:
    if encoding == "PCM16LE":
        return "s16le"
    if encoding == "FLOAT32LE":
        return "f32le"
    raise Ros2BridgeMessageError(f"Unsupported ROS2 audio encoding: {encoding}")


def _bit_depth_from_ros_encoding(encoding: str) -> int:
    if encoding == "PCM16LE":
        return 16
    if encoding == "FLOAT32LE":
        return 32
    raise Ros2BridgeMessageError(f"Unsupported ROS2 audio encoding: {encoding}")
