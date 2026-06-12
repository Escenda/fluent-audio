"""Pure ROS2-to-DORA ingress helpers for fluent-audio bridge commands."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol, TypeAlias

import pyarrow as pa

from fluent_audio.dora import (
    DoraMetadataMutableMapping,
    encode_agent_cancel_request_for_dora,
    encode_asr_control_for_dora,
    encode_playback_command_for_dora,
)
from bridges.ros2_bridge.messages import (
    Ros2AgentCancelRequest,
    Ros2AsrControl,
    Ros2PlaybackCommand,
    ros2_agent_cancel_request_to_contract,
    ros2_asr_control_to_contract,
    ros2_playback_command_to_contract,
)

Ros2BridgeIngressOutputId: TypeAlias = Literal[
    "agent_cancel",
    "asr_control",
    "playback_command",
]
Ros2BridgeIngressMessage: TypeAlias = (
    Ros2AgentCancelRequest | Ros2AsrControl | Ros2PlaybackCommand
)


class Ros2BridgeIngressError(ValueError):
    """Raised when a ROS2 ingress message cannot be emitted to DORA."""


@dataclass
class Ros2BridgeIngressSummary:
    """Counters for ROS2-to-DORA command ingress."""

    cancel_requests: int = 0
    asr_controls: int = 0
    playback_commands: int = 0


@dataclass
class Ros2BridgeIngressEncodedOutput:
    """One encoded DORA output produced from a ROS2 ingress message."""

    output_id: Ros2BridgeIngressOutputId
    payload: pa.UInt8Array
    metadata: DoraMetadataMutableMapping


class Ros2BridgeIngressSender(Protocol):
    def send_output(
        self,
        output_id: Ros2BridgeIngressOutputId,
        payload: pa.UInt8Array,
        metadata: DoraMetadataMutableMapping,
    ) -> None: ...


def encode_ros2_ingress_message(message: Ros2BridgeIngressMessage) -> Ros2BridgeIngressEncodedOutput:
    if isinstance(message, Ros2AgentCancelRequest):
        payload, metadata = encode_agent_cancel_request_for_dora(
            ros2_agent_cancel_request_to_contract(message)
        )
        return Ros2BridgeIngressEncodedOutput(
            output_id="agent_cancel",
            payload=payload,
            metadata=metadata.to_dora_metadata(),
        )
    if isinstance(message, Ros2AsrControl):
        payload, metadata = encode_asr_control_for_dora(ros2_asr_control_to_contract(message))
        return Ros2BridgeIngressEncodedOutput(
            output_id="asr_control",
            payload=payload,
            metadata=metadata.to_dora_metadata(),
        )
    if isinstance(message, Ros2PlaybackCommand):
        payload, metadata = encode_playback_command_for_dora(
            ros2_playback_command_to_contract(message)
        )
        return Ros2BridgeIngressEncodedOutput(
            output_id="playback_command",
            payload=payload,
            metadata=metadata.to_dora_metadata(),
        )
    raise Ros2BridgeIngressError("Unsupported ROS2 ingress message")


def publish_ros2_ingress_message(
    sender: Ros2BridgeIngressSender,
    message: Ros2BridgeIngressMessage,
) -> None:
    encoded = encode_ros2_ingress_message(message)
    sender.send_output(encoded.output_id, encoded.payload, encoded.metadata)


def send_ros2_ingress_message_to_dora(
    sender: Ros2BridgeIngressSender,
    message: Ros2BridgeIngressMessage,
    summary: Ros2BridgeIngressSummary | None = None,
) -> None:
    encoded = encode_ros2_ingress_message(message)
    sender.send_output(encoded.output_id, encoded.payload, metadata=encoded.metadata)
    if summary is not None:
        _increment_summary(summary, encoded.output_id)


def _increment_summary(
    summary: Ros2BridgeIngressSummary,
    output_id: Ros2BridgeIngressOutputId,
) -> None:
    if output_id == "agent_cancel":
        summary.cancel_requests += 1
    elif output_id == "asr_control":
        summary.asr_controls += 1
    elif output_id == "playback_command":
        summary.playback_commands += 1
