#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SMOKE_ROOT="${FLUENT_DIALOGUE_DORA_ROS2_SMOKE_ROOT:-${REPO_ROOT}/artifacts/ros2_bridge_sidecar_smoke}"

if ! command -v ros2 >/dev/null; then
  echo "missing required command: ros2" >&2
  exit 127
fi

if ! command -v colcon >/dev/null; then
  echo "missing required command: colcon" >&2
  exit 127
fi

python3 - <<'PY'
import rclpy

print(f"rclpy={rclpy.__name__}")
PY

mkdir -p "${SMOKE_ROOT}"
colcon --log-base "${SMOKE_ROOT}/log" build \
  --base-paths "${REPO_ROOT}/bridges/ros2_bridge/fluent_dialogue_dora_interfaces" \
  --build-base "${SMOKE_ROOT}/build" \
  --install-base "${SMOKE_ROOT}/install"

set +u
source "${SMOKE_ROOT}/install/setup.bash"
set -u

cd "${REPO_ROOT}"
python3 - <<'PY'
import time
from dataclasses import dataclass

import pyarrow as pa
import rclpy
from fluent_dialogue_dora_interfaces.msg import AgentCancelRequest
from fluent_dialogue_dora_interfaces.msg import AsrControl
from fluent_dialogue_dora_interfaces.msg import PlaybackCommand
from fluent_dialogue_dora_interfaces.msg import VoiceSessionEvent as VoiceSessionEventMsg

from fluent_dialogue_dora.dora import DoraMetadataMutableMapping
from fluent_dialogue_dora.dora import decode_agent_cancel_request_from_dora
from fluent_dialogue_dora.dora import decode_asr_control_from_dora
from fluent_dialogue_dora.dora import decode_playback_command_from_dora
from bridges.ros2_bridge.ingress import Ros2BridgeIngressOutputId
from bridges.ros2_bridge.messages import Ros2Header
from bridges.ros2_bridge.messages import Ros2Time
from bridges.ros2_bridge.messages import Ros2VoiceSessionEvent
from bridges.ros2_bridge.sidecar import Ros2BridgeSidecar
from bridges.ros2_bridge.sidecar import Ros2BridgeSidecarConfig
from bridges.ros2_bridge.sidecar import build_parser


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


cancel = AgentCancelRequest()
cancel.session_id = "session-1"
cancel.user_turn_id = "user-turn-1"
cancel.seq = 0
cancel.reason_present = False
cancel.reason = ""

parser = build_parser()
parsed = parser.parse_args(["--dora"])

rclpy.init()
dora_node = CapturingDoraNode()
sidecar_node = rclpy.create_node("fluent_dialogue_dora_sidecar_smoke_sidecar")
peer_node = rclpy.create_node("fluent_dialogue_dora_sidecar_smoke_peer")
sidecar = Ros2BridgeSidecar(dora_node, sidecar_node, Ros2BridgeSidecarConfig())
received_sessions: list[VoiceSessionEventMsg] = []
peer_node.create_subscription(
    VoiceSessionEventMsg,
    "/fluent_dialogue_dora/session",
    lambda message: received_sessions.append(message),
    10,
)

cancel_publisher = peer_node.create_publisher(
    AgentCancelRequest,
    "/fluent_dialogue_dora/in/agent_cancel",
    10,
)
asr_control_publisher = peer_node.create_publisher(
    AsrControl,
    "/fluent_dialogue_dora/in/asr_control",
    10,
)
playback_command_publisher = peer_node.create_publisher(
    PlaybackCommand,
    "/fluent_dialogue_dora/in/playback_command",
    10,
)


def spin_until_ready() -> None:
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        rclpy.spin_once(sidecar_node, timeout_sec=0.02)
        rclpy.spin_once(peer_node, timeout_sec=0.02)
        if (
            cancel_publisher.get_subscription_count() > 0
            and asr_control_publisher.get_subscription_count() > 0
            and playback_command_publisher.get_subscription_count() > 0
        ):
            return
    raise RuntimeError("ROS2 ingress subscriptions were not discovered")


def spin_until_session_publisher_ready() -> None:
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        rclpy.spin_once(sidecar_node, timeout_sec=0.02)
        rclpy.spin_once(peer_node, timeout_sec=0.02)
        if peer_node.count_publishers("/fluent_dialogue_dora/session") > 0:
            return
    raise RuntimeError("ROS2 session publisher was not discovered")


def spin_until_outputs(expected_count: int) -> None:
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        rclpy.spin_once(sidecar_node, timeout_sec=0.02)
        rclpy.spin_once(peer_node, timeout_sec=0.02)
        if len(dora_node.outputs) >= expected_count:
            return
    raise RuntimeError("Timed out waiting for sidecar DORA ingress outputs")


def spin_until_session_received() -> VoiceSessionEventMsg:
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        rclpy.spin_once(sidecar_node, timeout_sec=0.02)
        rclpy.spin_once(peer_node, timeout_sec=0.02)
        if received_sessions:
            return received_sessions[0]
    raise RuntimeError("Timed out waiting for sidecar ROS2 session publish")


try:
    spin_until_session_publisher_ready()
    sidecar.publisher.publish_voice_session_event(
        Ros2VoiceSessionEvent(
            header=Ros2Header(stamp=Ros2Time(sec=1, nanosec=2), frame_id="dialogue"),
            event="assistant_started",
            state="responding",
            seq=5,
            session_id="session-1",
            user_turn_id="user-turn-1",
            assistant_turn_id="assistant-turn-1",
            message="",
        )
    )
    session_message = spin_until_session_received()
    assert session_message.session_id == "session-1"
    assert session_message.assistant_turn_id == "assistant-turn-1"
    assert session_message.state == "responding"

    spin_until_ready()

    cancel_publisher.publish(cancel)

    asr_control = AsrControl()
    asr_control.action = "cancel"
    asr_control.session_id = "session-1"
    asr_control.user_turn_id = "user-turn-1"
    asr_control.stream_id = "audio/main"
    asr_control.seq = 2
    asr_control.start_sample_index = 0
    asr_control.stop_sample_index = 0
    asr_control.reason = "operator_cancel"
    asr_control_publisher.publish(asr_control)

    playback_command = PlaybackCommand()
    playback_command.command = "stop"
    playback_command.request_id = "tts-1"
    playback_command.stream_id = "speaker/main"
    playback_command.seq = 3
    playback_command_publisher.publish(playback_command)

    spin_until_outputs(3)
finally:
    sidecar_node.destroy_node()
    peer_node.destroy_node()
    rclpy.shutdown()

outputs = {output.output_id: output for output in dora_node.outputs}
decoded_cancel = decode_agent_cancel_request_from_dora(
    outputs["agent_cancel"].payload,
    outputs["agent_cancel"].metadata,
)
decoded_asr_control = decode_asr_control_from_dora(
    outputs["asr_control"].payload,
    outputs["asr_control"].metadata,
)
decoded_playback_command = decode_playback_command_from_dora(
    outputs["playback_command"].payload,
    outputs["playback_command"].metadata,
)

assert decoded_cancel.session_id == "session-1"
assert decoded_asr_control.action == "cancel"
assert decoded_playback_command.command == "stop"

print(
    {
        "cancel_request": cancel.__class__.__name__,
        "ros2_session_publish": session_message.__class__.__name__,
        "dora_ingress_outputs": len(dora_node.outputs),
        "ingress_summary": {
            "cancel_requests": sidecar.ingress_summary.cancel_requests,
            "asr_controls": sidecar.ingress_summary.asr_controls,
            "playback_commands": sidecar.ingress_summary.playback_commands,
        },
        "sidecar_dora": parsed.dora,
    }
)
PY
