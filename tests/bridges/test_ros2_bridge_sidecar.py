import importlib
import sys
from collections.abc import Callable
from dataclasses import dataclass
from types import ModuleType

import pyarrow as pa
import pytest

from fluent_dialogue_dora.contracts import AudioFormat
from fluent_dialogue_dora.dora import (
    DoraMetadataMutableMapping,
    decode_agent_cancel_request_from_dora,
    decode_asr_control_from_dora,
    decode_playback_command_from_dora,
)
from bridges.ros2_bridge.ingress import Ros2BridgeIngressOutputId
from bridges.ros2_bridge.messages import (
    Ros2AudioFrame,
    Ros2Header,
    Ros2Time,
    audio_final_marker_to_ros2,
)


class FakeGeneratedMessage:
    pass


class FakeTimeMsg(FakeGeneratedMessage):
    def __init__(self) -> None:
        self.sec = 0
        self.nanosec = 0


class FakeHeaderMsg(FakeGeneratedMessage):
    def __init__(self) -> None:
        self.stamp = FakeTimeMsg()
        self.frame_id = ""


class FakeAgentApprovalRequestMsg(FakeGeneratedMessage):
    pass


class FakeAgentCancelRequestMsg(FakeGeneratedMessage):
    pass


class FakeAgentTextDeltaMsg(FakeGeneratedMessage):
    pass


class FakeAgentToolEventMsg(FakeGeneratedMessage):
    pass


class FakeAgentTurnDoneMsg(FakeGeneratedMessage):
    pass


class FakeAsrControlMsg(FakeGeneratedMessage):
    pass


class FakeAudioFrameMsg(FakeGeneratedMessage):
    pass


class FakeDialogueEventMsg(FakeGeneratedMessage):
    pass


class FakePlaybackCommandMsg(FakeGeneratedMessage):
    pass


class FakePlaybackDoneMsg(FakeGeneratedMessage):
    pass


class FakePlaybackStateMsg(FakeGeneratedMessage):
    pass


class FakeTranscriptMsg(FakeGeneratedMessage):
    pass


class FakeTurnEventMsg(FakeGeneratedMessage):
    pass


class FakeVoiceActivityMsg(FakeGeneratedMessage):
    pass


class FakeVoiceSessionEventMsg(FakeGeneratedMessage):
    pass


@dataclass
class FakePublisher:
    message_type: type[FakeGeneratedMessage]
    topic: str
    qos_depth: int
    messages: list[FakeGeneratedMessage]

    def publish(self, message: FakeGeneratedMessage) -> None:
        self.messages.append(message)


@dataclass
class FakeSubscription:
    message_type: type[FakeGeneratedMessage]
    topic: str
    callback: Callable[[FakeGeneratedMessage], None]
    qos_depth: int


class FakeRclpyNode:
    def __init__(self) -> None:
        self.publishers: list[FakePublisher] = []
        self.subscriptions: list[FakeSubscription] = []
        self.destroyed = False

    def create_publisher(
        self,
        message_type: type[FakeGeneratedMessage],
        topic: str,
        qos_depth: int,
    ) -> FakePublisher:
        publisher = FakePublisher(
            message_type=message_type,
            topic=topic,
            qos_depth=qos_depth,
            messages=[],
        )
        self.publishers.append(publisher)
        return publisher

    def create_subscription(
        self,
        message_type: type[FakeGeneratedMessage],
        topic: str,
        callback: Callable[[FakeGeneratedMessage], None],
        qos_depth: int,
    ) -> FakeSubscription:
        subscription = FakeSubscription(
            message_type=message_type,
            topic=topic,
            callback=callback,
            qos_depth=qos_depth,
        )
        self.subscriptions.append(subscription)
        return subscription

    def destroy_node(self) -> None:
        self.destroyed = True


@dataclass
class CapturedDoraOutput:
    output_id: Ros2BridgeIngressOutputId
    payload: pa.UInt8Array
    metadata: DoraMetadataMutableMapping


class CapturingDoraNode:
    def __init__(self) -> None:
        self.outputs: list[CapturedDoraOutput] = []

    def send_output(
        self,
        output_id: Ros2BridgeIngressOutputId,
        payload: pa.UInt8Array,
        metadata: DoraMetadataMutableMapping,
    ) -> None:
        self.outputs.append(CapturedDoraOutput(output_id, payload, metadata))


def test_sidecar_imports_with_fake_ros_modules_and_keeps_ingress_topics_separate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sidecar = _import_sidecar_with_fake_ros(monkeypatch)

    args = sidecar.build_parser().parse_args(["--dora"])
    config = sidecar._config_from_args(args)

    assert config.topics.asr_control == "/fluent_dialogue_dora/asr_control"
    assert config.topics.asr_control_ingress == "/fluent_dialogue_dora/in/asr_control"
    assert config.topics.playback_command == "/fluent_dialogue_dora/playback_command"
    assert config.topics.playback_command_ingress == "/fluent_dialogue_dora/in/playback_command"
    assert config.topics.agent_cancel == "/fluent_dialogue_dora/in/agent_cancel"


def test_sidecar_generated_message_projection_conversion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sidecar = _import_sidecar_with_fake_ros(monkeypatch)
    frame = Ros2AudioFrame(
        header=Ros2Header(stamp=Ros2Time(sec=12, nanosec=34), frame_id="audio/main"),
        source_id="speaker",
        stream_id="audio/main",
        seq=3,
        sample_index=480,
        capture_time_ns=12_000_000_034,
        frame_count=2,
        encoding="PCM16LE",
        sample_rate_hz=48_000,
        channels=1,
        bit_depth=16,
        layout="interleaved",
        data=b"\x01\x00\x02\x00",
        final=False,
    )

    generated = sidecar._audio_frame_to_msg(frame)

    assert generated.header.stamp.sec == 12
    assert generated.header.stamp.nanosec == 34
    assert generated.header.frame_id == "audio/main"
    assert generated.source_id == "speaker"
    assert generated.data == [1, 0, 2, 0]
    assert generated.final is False


def test_sidecar_command_ingress_subscriptions_emit_dora_outputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sidecar = _import_sidecar_with_fake_ros(monkeypatch)
    ros_node = FakeRclpyNode()
    dora_node = CapturingDoraNode()
    bridge = sidecar.Ros2BridgeSidecar(dora_node, ros_node, sidecar.Ros2BridgeSidecarConfig())

    cancel_message = FakeAgentCancelRequestMsg()
    cancel_message.header = _fake_header("operator_ui")
    cancel_message.session_id = "session-1"
    cancel_message.user_turn_id = "turn-1"
    cancel_message.seq = 2
    cancel_message.reason_present = True
    cancel_message.reason = "voice_cancel"

    asr_control_message = FakeAsrControlMsg()
    asr_control_message.header = _fake_header("audio/main")
    asr_control_message.action = "cancel"
    asr_control_message.session_id = "session-1"
    asr_control_message.user_turn_id = "turn-1"
    asr_control_message.stream_id = "audio/main"
    asr_control_message.seq = 3
    asr_control_message.start_sample_index = 0
    asr_control_message.stop_sample_index = 0
    asr_control_message.reason = "barge_in"

    playback_command_message = FakePlaybackCommandMsg()
    playback_command_message.header = _fake_header("audio/playback")
    playback_command_message.command = "stop"
    playback_command_message.request_id = "tts-1"
    playback_command_message.stream_id = "audio/playback"
    playback_command_message.seq = 4

    _subscription_for_topic(ros_node, "/fluent_dialogue_dora/in/agent_cancel").callback(cancel_message)
    _subscription_for_topic(ros_node, "/fluent_dialogue_dora/in/asr_control").callback(asr_control_message)
    _subscription_for_topic(ros_node, "/fluent_dialogue_dora/in/playback_command").callback(
        playback_command_message
    )

    assert bridge.ingress_summary.cancel_requests == 1
    assert bridge.ingress_summary.asr_controls == 1
    assert bridge.ingress_summary.playback_commands == 1
    assert [output.output_id for output in dora_node.outputs] == [
        "agent_cancel",
        "asr_control",
        "playback_command",
    ]

    cancel = decode_agent_cancel_request_from_dora(
        dora_node.outputs[0].payload,
        dora_node.outputs[0].metadata,
    )
    asr_control = decode_asr_control_from_dora(
        dora_node.outputs[1].payload,
        dora_node.outputs[1].metadata,
    )
    playback_command = decode_playback_command_from_dora(
        dora_node.outputs[2].payload,
        dora_node.outputs[2].metadata,
    )

    assert cancel.reason == "voice_cancel"
    assert asr_control.action == "cancel"
    assert asr_control.reason == "barge_in"
    assert playback_command.command == "stop"
    assert playback_command.request_id == "tts-1"


def test_sidecar_publisher_emits_generated_message_to_registered_topic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sidecar = _import_sidecar_with_fake_ros(monkeypatch)
    ros_node = FakeRclpyNode()
    publisher = sidecar.RclpyRos2BridgeProjectionPublisher(
        ros_node,
        sidecar.Ros2BridgeSidecarTopics(),
        qos_depth=4,
    )

    publisher.publish_audio_frame(
        audio_final_marker_to_ros2(
            source_id="speaker",
            stream_id="audio/main",
            seq=8,
            sample_index=960,
            capture_time_ns=99,
            audio_format=AudioFormat(sample_rate_hz=48_000, channels=1, sample_format="s16le"),
        )
    )

    audio_publisher = _publisher_for_topic(ros_node, "/fluent_dialogue_dora/audio")
    assert audio_publisher.qos_depth == 4
    assert len(audio_publisher.messages) == 1
    generated = audio_publisher.messages[0]
    assert generated.source_id == "speaker"
    assert generated.final is True
    assert generated.data == []


def _import_sidecar_with_fake_ros(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    _install_fake_ros_modules(monkeypatch)
    module_name = "bridges.ros2_bridge.sidecar"
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)


def _install_fake_ros_modules(monkeypatch: pytest.MonkeyPatch) -> None:
    rclpy_module = ModuleType("rclpy")
    rclpy_node_module = ModuleType("rclpy.node")
    builtin_interfaces_module = ModuleType("builtin_interfaces")
    builtin_interfaces_msg_module = ModuleType("builtin_interfaces.msg")
    std_msgs_module = ModuleType("std_msgs")
    std_msgs_msg_module = ModuleType("std_msgs.msg")
    fluent_interfaces_module = ModuleType("fluent_dialogue_dora_interfaces")
    fluent_interfaces_msg_module = ModuleType("fluent_dialogue_dora_interfaces.msg")
    dora_module = ModuleType("dora")

    rclpy_module.init = _fake_rclpy_init
    rclpy_module.shutdown = _fake_rclpy_shutdown
    rclpy_module.ok = _fake_rclpy_ok
    rclpy_module.spin_once = _fake_rclpy_spin_once
    rclpy_module.create_node = _fake_rclpy_create_node
    rclpy_node_module.Node = FakeRclpyNode
    builtin_interfaces_msg_module.Time = FakeTimeMsg
    std_msgs_msg_module.Header = FakeHeaderMsg
    dora_module.Node = CapturingDoraNode

    fluent_interfaces_msg_module.AgentApprovalRequest = FakeAgentApprovalRequestMsg
    fluent_interfaces_msg_module.AgentCancelRequest = FakeAgentCancelRequestMsg
    fluent_interfaces_msg_module.AgentTextDelta = FakeAgentTextDeltaMsg
    fluent_interfaces_msg_module.AgentToolEvent = FakeAgentToolEventMsg
    fluent_interfaces_msg_module.AgentTurnDone = FakeAgentTurnDoneMsg
    fluent_interfaces_msg_module.AsrControl = FakeAsrControlMsg
    fluent_interfaces_msg_module.AudioFrame = FakeAudioFrameMsg
    fluent_interfaces_msg_module.DialogueEvent = FakeDialogueEventMsg
    fluent_interfaces_msg_module.PlaybackCommand = FakePlaybackCommandMsg
    fluent_interfaces_msg_module.PlaybackDone = FakePlaybackDoneMsg
    fluent_interfaces_msg_module.PlaybackState = FakePlaybackStateMsg
    fluent_interfaces_msg_module.Transcript = FakeTranscriptMsg
    fluent_interfaces_msg_module.TurnEvent = FakeTurnEventMsg
    fluent_interfaces_msg_module.VoiceActivity = FakeVoiceActivityMsg
    fluent_interfaces_msg_module.VoiceSessionEvent = FakeVoiceSessionEventMsg

    monkeypatch.setitem(sys.modules, "rclpy", rclpy_module)
    monkeypatch.setitem(sys.modules, "rclpy.node", rclpy_node_module)
    monkeypatch.setitem(sys.modules, "builtin_interfaces", builtin_interfaces_module)
    monkeypatch.setitem(sys.modules, "builtin_interfaces.msg", builtin_interfaces_msg_module)
    monkeypatch.setitem(sys.modules, "std_msgs", std_msgs_module)
    monkeypatch.setitem(sys.modules, "std_msgs.msg", std_msgs_msg_module)
    monkeypatch.setitem(sys.modules, "fluent_dialogue_dora_interfaces", fluent_interfaces_module)
    monkeypatch.setitem(sys.modules, "fluent_dialogue_dora_interfaces.msg", fluent_interfaces_msg_module)
    monkeypatch.setitem(sys.modules, "dora", dora_module)


def _fake_rclpy_init() -> None:
    return None


def _fake_rclpy_shutdown() -> None:
    return None


def _fake_rclpy_ok() -> bool:
    return False


def _fake_rclpy_spin_once(node: FakeRclpyNode, timeout_sec: float) -> None:
    _ = (node, timeout_sec)


def _fake_rclpy_create_node(name: str) -> FakeRclpyNode:
    _ = name
    return FakeRclpyNode()


def _fake_header(frame_id: str) -> FakeHeaderMsg:
    header = FakeHeaderMsg()
    header.frame_id = frame_id
    return header


def _subscription_for_topic(node: FakeRclpyNode, topic: str) -> FakeSubscription:
    for subscription in node.subscriptions:
        if subscription.topic == topic:
            return subscription
    raise AssertionError(f"missing subscription for {topic}")


def _publisher_for_topic(node: FakeRclpyNode, topic: str) -> FakePublisher:
    for publisher in node.publishers:
        if publisher.topic == topic:
            return publisher
    raise AssertionError(f"missing publisher for {topic}")
