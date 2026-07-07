import pytest
import pyarrow as pa

from fluent_dialogue_dora.contracts import (
    AgentCancelRequest,
    AsrCancel,
    PlaybackStop,
)
from fluent_dialogue_dora.dora import (
    DoraMetadataMutableMapping,
    decode_agent_cancel_request_from_dora,
    decode_asr_control_from_dora,
    decode_playback_command_from_dora,
)
from bridges.ros2_bridge.ingress import (
    Ros2BridgeIngressOutputId,
    publish_ros2_ingress_message,
)
from bridges.ros2_bridge.messages import (
    Ros2AgentCancelRequest,
    Ros2Header,
    Ros2Time,
    agent_cancel_request_to_ros2,
    asr_control_to_ros2,
    playback_command_to_ros2,
)


class CapturedIngressOutput:
    def __init__(
        self,
        output_id: Ros2BridgeIngressOutputId,
        payload: pa.UInt8Array,
        metadata: DoraMetadataMutableMapping,
    ) -> None:
        self.output_id = output_id
        self.payload = payload
        self.metadata = metadata


class CapturingIngressSender:
    def __init__(self) -> None:
        self.outputs: list[CapturedIngressOutput] = []

    def send_output(
        self,
        output_id: Ros2BridgeIngressOutputId,
        payload: pa.UInt8Array,
        metadata: DoraMetadataMutableMapping,
    ) -> None:
        self.outputs.append(CapturedIngressOutput(output_id, payload, metadata))


def test_agent_cancel_ingress_emits_dora_contract() -> None:
    sender = CapturingIngressSender()
    cancel = AgentCancelRequest(
        session_id="session-1",
        user_turn_id="turn-1",
        seq=1,
        reason="voice_cancel",
    )

    publish_ros2_ingress_message(sender, agent_cancel_request_to_ros2(cancel, timestamp_ns=2))

    assert len(sender.outputs) == 1
    output = sender.outputs[0]
    assert output.output_id == "agent_cancel"
    assert decode_agent_cancel_request_from_dora(output.payload, output.metadata) == cancel


def test_asr_control_ingress_emits_dora_contract() -> None:
    sender = CapturingIngressSender()
    control = AsrCancel(
        action="cancel",
        session_id="session-1",
        user_turn_id="turn-1",
        stream_id="audio/main",
        seq=2,
        reason="barge_in",
    )

    publish_ros2_ingress_message(sender, asr_control_to_ros2(control, timestamp_ns=3))

    assert len(sender.outputs) == 1
    output = sender.outputs[0]
    assert output.output_id == "asr_control"
    assert decode_asr_control_from_dora(output.payload, output.metadata) == control


def test_playback_command_ingress_emits_dora_contract() -> None:
    sender = CapturingIngressSender()
    command = PlaybackStop(
        command="stop",
        request_id="playback-1",
        stream_id="audio/playback",
        seq=3,
    )

    publish_ros2_ingress_message(sender, playback_command_to_ros2(command, timestamp_ns=4))

    assert len(sender.outputs) == 1
    output = sender.outputs[0]
    assert output.output_id == "playback_command"
    assert decode_playback_command_from_dora(output.payload, output.metadata) == command


def test_ingress_rejects_invalid_ros2_message_before_dora_emit() -> None:
    sender = CapturingIngressSender()
    invalid_header = Ros2Header(stamp=Ros2Time(sec=0, nanosec=0), frame_id="session-1")

    with pytest.raises(ValueError, match="reason is required"):
        Ros2AgentCancelRequest(
            header=invalid_header,
            session_id="session-1",
            user_turn_id="turn-1",
            seq=0,
            reason_present=True,
            reason="",
        )
    assert sender.outputs == []
