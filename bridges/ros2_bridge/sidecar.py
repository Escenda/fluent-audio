"""Real rclpy sidecar for fluent-audio ROS2 bridge runtime.

The sidecar publishes DORA inputs to ROS2 topics and subscribes to ROS2 command
topics that need to flow back into DORA. This module intentionally
imports rclpy and generated ROS2 message classes at module load time so a missing
ROS2 environment fails before the bridge can pretend to run.
"""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import rclpy
from builtin_interfaces.msg import Time as TimeMsg
from dora import Node as DoraNode
from fluent_audio_interfaces.msg import AgentApprovalRequest as AgentApprovalRequestMsg
from fluent_audio_interfaces.msg import AgentCancelRequest as AgentCancelRequestMsg
from fluent_audio_interfaces.msg import AgentTextDelta as AgentTextDeltaMsg
from fluent_audio_interfaces.msg import AgentToolEvent as AgentToolEventMsg
from fluent_audio_interfaces.msg import AgentTurnDone as AgentTurnDoneMsg
from fluent_audio_interfaces.msg import AsrControl as AsrControlMsg
from fluent_audio_interfaces.msg import AudioFrame as AudioFrameMsg
from fluent_audio_interfaces.msg import DialogueEvent as DialogueEventMsg
from fluent_audio_interfaces.msg import PlaybackCommand as PlaybackCommandMsg
from fluent_audio_interfaces.msg import PlaybackDone as PlaybackDoneMsg
from fluent_audio_interfaces.msg import PlaybackState as PlaybackStateMsg
from fluent_audio_interfaces.msg import Transcript as TranscriptMsg
from fluent_audio_interfaces.msg import TurnEvent as TurnEventMsg
from fluent_audio_interfaces.msg import VoiceActivity as VoiceActivityMsg
from fluent_audio_interfaces.msg import VoiceSessionEvent as VoiceSessionEventMsg
from rclpy.node import Node as RclpyNode
from std_msgs.msg import Header as HeaderMsg

from bridges.ros2_bridge.ingress import (
    Ros2BridgeIngressSummary,
    send_ros2_ingress_message_to_dora,
)
from bridges.ros2_bridge.main import (
    Ros2BridgeFiniteInputId,
    Ros2BridgeProjectionConfig,
    Ros2BridgeProjectionSummary,
    run_ros2_bridge_projection_events,
)
from bridges.ros2_bridge.messages import (
    Ros2AgentApprovalRequest,
    Ros2AgentCancelRequest,
    Ros2AgentTextDelta,
    Ros2AgentToolEvent,
    Ros2AgentTurnDone,
    Ros2AsrControl,
    Ros2AudioFrame,
    Ros2DialogueEvent,
    Ros2Header,
    Ros2PlaybackCommand,
    Ros2PlaybackDone,
    Ros2PlaybackState,
    Ros2Time,
    Ros2Transcript,
    Ros2TurnEvent,
    Ros2VoiceActivity,
    Ros2VoiceSessionEvent,
)


class TimeMessage(Protocol):
    sec: int
    nanosec: int


class HeaderMessage(Protocol):
    stamp: TimeMessage
    frame_id: str


class Ros2BridgeSidecarTopics(BaseModel):
    """ROS2 topic names for the bridge sidecar."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    audio: str = Field(default="/fluent_audio/audio", min_length=1)
    activity: str = Field(default="/fluent_audio/activity", min_length=1)
    turn: str = Field(default="/fluent_audio/turn", min_length=1)
    asr_control: str = Field(default="/fluent_audio/asr_control", min_length=1)
    transcript: str = Field(default="/fluent_audio/transcript", min_length=1)
    session: str = Field(default="/fluent_audio/session", min_length=1)
    dialogue: str = Field(default="/fluent_audio/dialogue", min_length=1)
    agent_text: str = Field(default="/fluent_audio/agent_text", min_length=1)
    agent_done: str = Field(default="/fluent_audio/agent_done", min_length=1)
    agent_approval: str = Field(default="/fluent_audio/agent_approval", min_length=1)
    agent_tool: str = Field(default="/fluent_audio/agent_tool", min_length=1)
    playback_command: str = Field(default="/fluent_audio/playback_command", min_length=1)
    playback_state: str = Field(default="/fluent_audio/playback_state", min_length=1)
    playback_done: str = Field(default="/fluent_audio/playback_done", min_length=1)
    agent_cancel: str = Field(default="/fluent_audio/in/agent_cancel", min_length=1)
    asr_control_ingress: str = Field(default="/fluent_audio/in/asr_control", min_length=1)
    playback_command_ingress: str = Field(
        default="/fluent_audio/in/playback_command",
        min_length=1,
    )


class Ros2BridgeSidecarConfig(BaseModel):
    """Runtime configuration for the real ROS2 sidecar."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    node_name: str = Field(default="fluent_audio_ros2_bridge", min_length=1)
    qos_depth: int = Field(default=10, gt=0)
    spin_timeout_seconds: float = Field(default=0.02, gt=0.0)
    required_final_inputs: tuple[Ros2BridgeFiniteInputId, ...] = Field(default=())
    topics: Ros2BridgeSidecarTopics = Field(default_factory=Ros2BridgeSidecarTopics)


@dataclass
class Ros2BridgeSidecarRunSummary:
    """Summary for one ROS2 bridge sidecar run."""

    projection: Ros2BridgeProjectionSummary
    ingress: Ros2BridgeIngressSummary


class RclpyRos2BridgeProjectionPublisher:
    """Publish typed ROS-facing projection models through generated ROS2 messages."""

    def __init__(
        self,
        node: RclpyNode,
        topics: Ros2BridgeSidecarTopics,
        qos_depth: int,
    ) -> None:
        self._audio = node.create_publisher(AudioFrameMsg, topics.audio, qos_depth)
        self._activity = node.create_publisher(VoiceActivityMsg, topics.activity, qos_depth)
        self._turn = node.create_publisher(TurnEventMsg, topics.turn, qos_depth)
        self._asr_control = node.create_publisher(AsrControlMsg, topics.asr_control, qos_depth)
        self._transcript = node.create_publisher(TranscriptMsg, topics.transcript, qos_depth)
        self._session = node.create_publisher(VoiceSessionEventMsg, topics.session, qos_depth)
        self._dialogue = node.create_publisher(DialogueEventMsg, topics.dialogue, qos_depth)
        self._agent_text = node.create_publisher(AgentTextDeltaMsg, topics.agent_text, qos_depth)
        self._agent_done = node.create_publisher(AgentTurnDoneMsg, topics.agent_done, qos_depth)
        self._agent_approval = node.create_publisher(
            AgentApprovalRequestMsg,
            topics.agent_approval,
            qos_depth,
        )
        self._agent_tool = node.create_publisher(AgentToolEventMsg, topics.agent_tool, qos_depth)
        self._playback_command = node.create_publisher(
            PlaybackCommandMsg,
            topics.playback_command,
            qos_depth,
        )
        self._playback_state = node.create_publisher(
            PlaybackStateMsg,
            topics.playback_state,
            qos_depth,
        )
        self._playback_done = node.create_publisher(
            PlaybackDoneMsg,
            topics.playback_done,
            qos_depth,
        )

    def publish_audio_frame(self, message: Ros2AudioFrame) -> None:
        self._audio.publish(_audio_frame_to_msg(message))

    def publish_voice_activity(self, message: Ros2VoiceActivity) -> None:
        self._activity.publish(_voice_activity_to_msg(message))

    def publish_turn_event(self, message: Ros2TurnEvent) -> None:
        self._turn.publish(_turn_event_to_msg(message))

    def publish_asr_control(self, message: Ros2AsrControl) -> None:
        self._asr_control.publish(_asr_control_to_msg(message))

    def publish_transcript(self, message: Ros2Transcript) -> None:
        self._transcript.publish(_transcript_to_msg(message))

    def publish_voice_session_event(self, message: Ros2VoiceSessionEvent) -> None:
        self._session.publish(_voice_session_event_to_msg(message))

    def publish_dialogue_event(self, message: Ros2DialogueEvent) -> None:
        self._dialogue.publish(_dialogue_event_to_msg(message))

    def publish_agent_text_delta(self, message: Ros2AgentTextDelta) -> None:
        self._agent_text.publish(_agent_text_delta_to_msg(message))

    def publish_agent_turn_done(self, message: Ros2AgentTurnDone) -> None:
        self._agent_done.publish(_agent_turn_done_to_msg(message))

    def publish_agent_approval_request(self, message: Ros2AgentApprovalRequest) -> None:
        self._agent_approval.publish(_agent_approval_request_to_msg(message))

    def publish_agent_tool_event(self, message: Ros2AgentToolEvent) -> None:
        self._agent_tool.publish(_agent_tool_event_to_msg(message))

    def publish_playback_command(self, message: Ros2PlaybackCommand) -> None:
        self._playback_command.publish(_playback_command_to_msg(message))

    def publish_playback_state(self, message: Ros2PlaybackState) -> None:
        self._playback_state.publish(_playback_state_to_msg(message))

    def publish_playback_done(self, message: Ros2PlaybackDone) -> None:
        self._playback_done.publish(_playback_done_to_msg(message))


class Ros2BridgeSidecar:
    """Bind ROS2 publishers/subscribers to one DORA bridge node."""

    def __init__(
        self,
        dora_node: DoraNode,
        ros_node: RclpyNode,
        config: Ros2BridgeSidecarConfig,
    ) -> None:
        self.ingress_summary = Ros2BridgeIngressSummary()
        self.publisher = RclpyRos2BridgeProjectionPublisher(
            ros_node,
            config.topics,
            config.qos_depth,
        )
        self._dora_node = dora_node
        self._agent_cancel_subscription = ros_node.create_subscription(
            AgentCancelRequestMsg,
            config.topics.agent_cancel,
            self._on_agent_cancel,
            config.qos_depth,
        )
        self._asr_control_ingress_subscription = ros_node.create_subscription(
            AsrControlMsg,
            config.topics.asr_control_ingress,
            self._on_asr_control,
            config.qos_depth,
        )
        self._playback_command_ingress_subscription = ros_node.create_subscription(
            PlaybackCommandMsg,
            config.topics.playback_command_ingress,
            self._on_playback_command,
            config.qos_depth,
        )

    def _on_agent_cancel(self, message: AgentCancelRequestMsg) -> None:
        send_ros2_ingress_message_to_dora(
            self._dora_node,
            _agent_cancel_request_from_msg(message),
            self.ingress_summary,
        )

    def _on_asr_control(self, message: AsrControlMsg) -> None:
        send_ros2_ingress_message_to_dora(
            self._dora_node,
            _asr_control_from_msg(message),
            self.ingress_summary,
        )

    def _on_playback_command(self, message: PlaybackCommandMsg) -> None:
        send_ros2_ingress_message_to_dora(
            self._dora_node,
            _playback_command_from_msg(message),
            self.ingress_summary,
        )


class RclpySpinThread:
    """Spin rclpy while the foreground thread consumes the DORA event stream."""

    def __init__(self, node: RclpyNode, timeout_seconds: float) -> None:
        self._node = node
        self._timeout_seconds = timeout_seconds
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, name="fluent-audio-ros2-spin")
        self._failure: BaseException | None = None

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._thread.join()

    def raise_if_failed(self) -> None:
        if self._failure is not None:
            raise self._failure

    def _run(self) -> None:
        try:
            while not self._stop_event.is_set() and rclpy.ok():
                rclpy.spin_once(self._node, timeout_sec=self._timeout_seconds)
        except BaseException as exc:
            self._failure = exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the fluent-audio ROS2 sidecar bridge.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--node-name", default="fluent_audio_ros2_bridge")
    parser.add_argument("--qos-depth", type=int, default=10)
    parser.add_argument("--spin-timeout-seconds", type=float, default=0.02)
    parser.add_argument(
        "--required-final-input",
        action="append",
        choices=["audio", "activity", "turn", "asr_control", "transcript"],
        dest="required_final_inputs",
    )
    parser.add_argument("--audio-topic", default="/fluent_audio/audio")
    parser.add_argument("--activity-topic", default="/fluent_audio/activity")
    parser.add_argument("--turn-topic", default="/fluent_audio/turn")
    parser.add_argument("--asr-control-topic", default="/fluent_audio/asr_control")
    parser.add_argument("--transcript-topic", default="/fluent_audio/transcript")
    parser.add_argument("--session-topic", default="/fluent_audio/session")
    parser.add_argument("--dialogue-topic", default="/fluent_audio/dialogue")
    parser.add_argument("--agent-text-topic", default="/fluent_audio/agent_text")
    parser.add_argument("--agent-done-topic", default="/fluent_audio/agent_done")
    parser.add_argument("--agent-approval-topic", default="/fluent_audio/agent_approval")
    parser.add_argument("--agent-tool-topic", default="/fluent_audio/agent_tool")
    parser.add_argument("--playback-command-topic", default="/fluent_audio/playback_command")
    parser.add_argument("--playback-state-topic", default="/fluent_audio/playback_state")
    parser.add_argument("--playback-done-topic", default="/fluent_audio/playback_done")
    parser.add_argument("--agent-cancel-topic", default="/fluent_audio/in/agent_cancel")
    parser.add_argument("--asr-control-ingress-topic", default="/fluent_audio/in/asr_control")
    parser.add_argument(
        "--playback-command-ingress-topic",
        default="/fluent_audio/in/playback_command",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("ros2_bridge sidecar requires --dora")

    summary = run_ros2_bridge_sidecar(_config_from_args(args))
    sys.stdout.write(_summary_json(summary))
    sys.stdout.write("\n")
    return 0


def run_ros2_bridge_sidecar(config: Ros2BridgeSidecarConfig) -> Ros2BridgeSidecarRunSummary:
    rclpy.init()
    ros_node = rclpy.create_node(config.node_name)
    dora_node = DoraNode()
    sidecar = Ros2BridgeSidecar(dora_node, ros_node, config)
    spinner = RclpySpinThread(ros_node, config.spin_timeout_seconds)
    spinner.start()
    try:
        projection_summary = run_ros2_bridge_projection_events(
            dora_node,
            Ros2BridgeProjectionConfig(required_final_inputs=config.required_final_inputs),
            sidecar.publisher,
        )
        spinner.raise_if_failed()
        return Ros2BridgeSidecarRunSummary(
            projection=projection_summary,
            ingress=sidecar.ingress_summary,
        )
    finally:
        spinner.stop()
        ros_node.destroy_node()
        rclpy.shutdown()


def _config_from_args(args: argparse.Namespace) -> Ros2BridgeSidecarConfig:
    return Ros2BridgeSidecarConfig(
        node_name=args.node_name,
        qos_depth=args.qos_depth,
        spin_timeout_seconds=args.spin_timeout_seconds,
        required_final_inputs=tuple(args.required_final_inputs or ()),
        topics=Ros2BridgeSidecarTopics(
            audio=args.audio_topic,
            activity=args.activity_topic,
            turn=args.turn_topic,
            asr_control=args.asr_control_topic,
            transcript=args.transcript_topic,
            session=args.session_topic,
            dialogue=args.dialogue_topic,
            agent_text=args.agent_text_topic,
            agent_done=args.agent_done_topic,
            agent_approval=args.agent_approval_topic,
            agent_tool=args.agent_tool_topic,
            playback_command=args.playback_command_topic,
            playback_state=args.playback_state_topic,
            playback_done=args.playback_done_topic,
            agent_cancel=args.agent_cancel_topic,
            asr_control_ingress=args.asr_control_ingress_topic,
            playback_command_ingress=args.playback_command_ingress_topic,
        ),
    )


def _time_to_msg(time: Ros2Time) -> TimeMsg:
    message = TimeMsg()
    message.sec = time.sec
    message.nanosec = time.nanosec
    return message


def _time_from_msg(message: TimeMessage) -> Ros2Time:
    return Ros2Time(sec=message.sec, nanosec=message.nanosec)


def _header_to_msg(header: Ros2Header) -> HeaderMsg:
    message = HeaderMsg()
    message.stamp = _time_to_msg(header.stamp)
    message.frame_id = header.frame_id
    return message


def _header_from_msg(message: HeaderMessage) -> Ros2Header:
    return Ros2Header(stamp=_time_from_msg(message.stamp), frame_id=message.frame_id)


def _audio_frame_to_msg(message: Ros2AudioFrame) -> AudioFrameMsg:
    ros_message = AudioFrameMsg()
    ros_message.header = _header_to_msg(message.header)
    ros_message.source_id = message.source_id
    ros_message.stream_id = message.stream_id
    ros_message.seq = message.seq
    ros_message.sample_index = message.sample_index
    ros_message.capture_time_ns = message.capture_time_ns
    ros_message.frame_count = message.frame_count
    ros_message.encoding = message.encoding
    ros_message.sample_rate_hz = message.sample_rate_hz
    ros_message.channels = message.channels
    ros_message.bit_depth = message.bit_depth
    ros_message.layout = message.layout
    ros_message.data = list(message.data)
    ros_message.final = message.final
    return ros_message


def _voice_activity_to_msg(message: Ros2VoiceActivity) -> VoiceActivityMsg:
    ros_message = VoiceActivityMsg()
    ros_message.header = _header_to_msg(message.header)
    ros_message.source_id = message.source_id
    ros_message.stream_id = message.stream_id
    ros_message.seq = message.seq
    ros_message.sample_index = message.sample_index
    ros_message.frame_count = message.frame_count
    ros_message.state = message.state
    ros_message.speech_probability = message.speech_probability
    ros_message.final = message.final
    return ros_message


def _turn_event_to_msg(message: Ros2TurnEvent) -> TurnEventMsg:
    ros_message = TurnEventMsg()
    ros_message.header = _header_to_msg(message.header)
    ros_message.session_id = message.session_id
    ros_message.user_turn_id = message.user_turn_id
    ros_message.stream_id = message.stream_id
    ros_message.seq = message.seq
    ros_message.sample_index = message.sample_index
    ros_message.state = message.state
    ros_message.confidence_present = message.confidence_present
    ros_message.confidence = message.confidence
    ros_message.final = message.final
    return ros_message


def _asr_control_to_msg(message: Ros2AsrControl) -> AsrControlMsg:
    ros_message = AsrControlMsg()
    ros_message.header = _header_to_msg(message.header)
    ros_message.action = message.action
    ros_message.session_id = message.session_id
    ros_message.user_turn_id = message.user_turn_id
    ros_message.stream_id = message.stream_id
    ros_message.seq = message.seq
    ros_message.start_sample_index = message.start_sample_index
    ros_message.stop_sample_index = message.stop_sample_index
    ros_message.reason = message.reason
    return ros_message


def _asr_control_from_msg(message: AsrControlMsg) -> Ros2AsrControl:
    return Ros2AsrControl(
        header=_header_from_msg(message.header),
        action=message.action,
        session_id=message.session_id,
        user_turn_id=message.user_turn_id,
        stream_id=message.stream_id,
        seq=message.seq,
        start_sample_index=message.start_sample_index,
        stop_sample_index=message.stop_sample_index,
        reason=message.reason,
    )


def _transcript_to_msg(message: Ros2Transcript) -> TranscriptMsg:
    ros_message = TranscriptMsg()
    ros_message.header = _header_to_msg(message.header)
    ros_message.kind = message.kind
    ros_message.session_id = message.session_id
    ros_message.user_turn_id = message.user_turn_id
    ros_message.stream_id = message.stream_id
    ros_message.seq = message.seq
    ros_message.text = message.text
    ros_message.start_sample_index = message.start_sample_index
    ros_message.end_sample_index = message.end_sample_index
    return ros_message


def _voice_session_event_to_msg(message: Ros2VoiceSessionEvent) -> VoiceSessionEventMsg:
    ros_message = VoiceSessionEventMsg()
    ros_message.header = _header_to_msg(message.header)
    ros_message.event = message.event
    ros_message.state = message.state
    ros_message.seq = message.seq
    ros_message.session_id = message.session_id
    ros_message.user_turn_id = message.user_turn_id
    ros_message.assistant_turn_id = message.assistant_turn_id
    ros_message.message = message.message
    return ros_message


def _dialogue_event_to_msg(message: Ros2DialogueEvent) -> DialogueEventMsg:
    ros_message = DialogueEventMsg()
    ros_message.header = _header_to_msg(message.header)
    ros_message.event = message.event
    ros_message.session_id = message.session_id
    ros_message.user_turn_id = message.user_turn_id
    ros_message.seq = message.seq
    ros_message.text = message.text
    ros_message.request_id = message.request_id
    ros_message.message = message.message
    return ros_message


def _agent_text_delta_to_msg(message: Ros2AgentTextDelta) -> AgentTextDeltaMsg:
    ros_message = AgentTextDeltaMsg()
    ros_message.header = _header_to_msg(message.header)
    ros_message.session_id = message.session_id
    ros_message.user_turn_id = message.user_turn_id
    ros_message.agent_turn_id = message.agent_turn_id
    ros_message.seq = message.seq
    ros_message.text = message.text
    return ros_message


def _agent_turn_done_to_msg(message: Ros2AgentTurnDone) -> AgentTurnDoneMsg:
    ros_message = AgentTurnDoneMsg()
    ros_message.header = _header_to_msg(message.header)
    ros_message.session_id = message.session_id
    ros_message.user_turn_id = message.user_turn_id
    ros_message.agent_turn_id = message.agent_turn_id
    ros_message.seq = message.seq
    ros_message.status = message.status
    ros_message.message = message.message
    return ros_message


def _agent_approval_request_to_msg(message: Ros2AgentApprovalRequest) -> AgentApprovalRequestMsg:
    ros_message = AgentApprovalRequestMsg()
    ros_message.header = _header_to_msg(message.header)
    ros_message.session_id = message.session_id
    ros_message.user_turn_id = message.user_turn_id
    ros_message.approval_id = message.approval_id
    ros_message.seq = message.seq
    ros_message.prompt = message.prompt
    ros_message.action_label = message.action_label
    return ros_message


def _agent_tool_event_to_msg(message: Ros2AgentToolEvent) -> AgentToolEventMsg:
    ros_message = AgentToolEventMsg()
    ros_message.header = _header_to_msg(message.header)
    ros_message.session_id = message.session_id
    ros_message.user_turn_id = message.user_turn_id
    ros_message.tool_call_id = message.tool_call_id
    ros_message.tool_name = message.tool_name
    ros_message.event = message.event
    ros_message.seq = message.seq
    ros_message.summary = message.summary
    ros_message.error_message = message.error_message
    return ros_message


def _playback_command_to_msg(message: Ros2PlaybackCommand) -> PlaybackCommandMsg:
    ros_message = PlaybackCommandMsg()
    ros_message.header = _header_to_msg(message.header)
    ros_message.command = message.command
    ros_message.request_id = message.request_id
    ros_message.stream_id = message.stream_id
    ros_message.seq = message.seq
    return ros_message


def _playback_command_from_msg(message: PlaybackCommandMsg) -> Ros2PlaybackCommand:
    return Ros2PlaybackCommand(
        header=_header_from_msg(message.header),
        command=message.command,
        request_id=message.request_id,
        stream_id=message.stream_id,
        seq=message.seq,
    )


def _playback_state_to_msg(message: Ros2PlaybackState) -> PlaybackStateMsg:
    ros_message = PlaybackStateMsg()
    ros_message.header = _header_to_msg(message.header)
    ros_message.request_id = message.request_id
    ros_message.session_id = message.session_id
    ros_message.user_turn_id = message.user_turn_id
    ros_message.stream_id = message.stream_id
    ros_message.state = message.state
    ros_message.seq = message.seq
    ros_message.played_frames = message.played_frames
    ros_message.reason = message.reason
    return ros_message


def _playback_done_to_msg(message: Ros2PlaybackDone) -> PlaybackDoneMsg:
    ros_message = PlaybackDoneMsg()
    ros_message.header = _header_to_msg(message.header)
    ros_message.request_id = message.request_id
    ros_message.session_id = message.session_id
    ros_message.user_turn_id = message.user_turn_id
    ros_message.stream_id = message.stream_id
    ros_message.status = message.status
    ros_message.final_sequence_present = message.final_sequence_present
    ros_message.final_sequence = message.final_sequence
    ros_message.total_frames_present = message.total_frames_present
    ros_message.total_frames = message.total_frames
    ros_message.reason = message.reason
    return ros_message


def _agent_cancel_request_from_msg(message: AgentCancelRequestMsg) -> Ros2AgentCancelRequest:
    return Ros2AgentCancelRequest(
        header=_header_from_msg(message.header),
        session_id=message.session_id,
        user_turn_id=message.user_turn_id,
        seq=message.seq,
        reason_present=message.reason_present,
        reason=message.reason,
    )


def _summary_json(summary: Ros2BridgeSidecarRunSummary) -> str:
    projection = summary.projection
    ingress = summary.ingress
    return (
        "{"
        f"\"processed_inputs\":{projection.processed_inputs},"
        f"\"published_messages\":{projection.published_messages},"
        f"\"final_inputs\":{projection.final_inputs},"
        f"\"audio_frames\":{projection.audio_frames},"
        f"\"audio_final_markers\":{projection.audio_final_markers},"
        f"\"activity_events\":{projection.activity_events},"
        f"\"activity_final_markers\":{projection.activity_final_markers},"
        f"\"turn_events\":{projection.turn_events},"
        f"\"turn_final_markers\":{projection.turn_final_markers},"
        f"\"asr_controls\":{projection.asr_controls},"
        f"\"asr_control_final_markers\":{projection.asr_control_final_markers},"
        f"\"transcript_deltas\":{projection.transcript_deltas},"
        f"\"transcript_finals\":{projection.transcript_finals},"
        f"\"transcript_stream_finals\":{projection.transcript_stream_finals},"
        f"\"session_events\":{projection.session_events},"
        f"\"dialogue_events\":{projection.dialogue_events},"
        f"\"agent_text_deltas\":{projection.agent_text_deltas},"
        f"\"agent_turn_done\":{projection.agent_turn_done},"
        f"\"agent_approval_requests\":{projection.agent_approval_requests},"
        f"\"agent_tool_events\":{projection.agent_tool_events},"
        f"\"playback_commands\":{projection.playback_commands},"
        f"\"playback_states\":{projection.playback_states},"
        f"\"playback_done\":{projection.playback_done},"
        f"\"agent_cancel_requests\":{ingress.cancel_requests},"
        f"\"asr_control_ingress\":{ingress.asr_controls},"
        f"\"playback_command_ingress\":{ingress.playback_commands}"
        "}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
