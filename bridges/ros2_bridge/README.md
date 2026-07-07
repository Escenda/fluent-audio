# ros2_bridge

Bridges fluent-dialogue-dora core events, commands, status, and optional audio taps into ROS2.

The core runtime itself must not become a ROS2 graph.

## Boundary Contract

The bridge projects validated fluent-dialogue-dora contracts into ROS2-facing messages.
It does not reimplement VAD, ASR, turn detection, dialogue, TTS, playback, or
media graph logic.

Implemented pure projection models:

- `Ros2AudioFrame`: raw PCM `AudioChunk` plus explicit stream final marker.
- `Ros2VoiceActivity`: `VoiceActivityEvent` plus explicit stream final marker.
- `Ros2TurnEvent`: `TurnEvent` plus explicit stream final marker.
- `Ros2AsrControl`: `AsrStart`, `AsrStop`, `AsrCancel`.
- `Ros2Transcript`: `TranscriptDelta`, `TranscriptPartial`, `TranscriptFinal`, and transcript stream final marker.
- `Ros2VoiceSessionEvent`: `VoiceSessionEvent`.
- `Ros2DialogueEvent`: `DialogueEvent`.
- `Ros2AgentTextDelta`, `Ros2AgentTurnDone`, `Ros2AgentApprovalRequest`, `Ros2AgentCancelRequest`, `Ros2AgentToolEvent`.
- `Ros2PlaybackCommand`: `PlaybackStop`, `PlaybackPause`, `PlaybackResume`, `PlaybackClear`.
- `Ros2PlaybackState`, `Ros2PlaybackDone`.

`user_turn_id` is a string at the ROS2-facing boundary. The older
`fluent_dialogue_dora_ros2` `uint32 user_turn_id` shape is not preserved because the new
runtime contract uses stable string identifiers.

## Pure Runner

`main.py` implements `run_ros2_bridge_projection_events()`, a rclpy-free DORA
event runner. It decodes validated DORA payload/metadata contracts and publishes
typed ROS2 projection models through `Ros2BridgeProjectionPublisher`.

The executable `--dora` entrypoint can write those typed projections to JSONL
with `--jsonl-output`. This is a smoke-test sink, not a ROS2 publisher. It
exists so the DORA boundary can be verified in environments without ROS2.

Covered DORA inputs:

- `audio`: `AudioChunk` and audio stream final marker.
- `activity`: `VoiceActivityEvent` and activity stream final marker.
- `turn`: `TurnEvent` and turn stream final marker.
- `asr_control`: `AsrStart`, `AsrStop`, `AsrCancel`; the ASR control final
  marker is consumed for completion accounting and is not published as a ROS2
  command.
- `transcript`: `TranscriptDelta`, `TranscriptPartial`, `TranscriptFinal`, and transcript stream
  final marker.
- `session`, `dialogue`, `agent_text`, `agent_done`, `agent_approval`, `agent_tool`.
- `playback_command`, `playback_state`, `playback_done`.

When an input is listed in `required_final_inputs`, the runner fails if the DORA
transport closes or the event stream ends before that explicit final marker.

## ROS2 Ingress

`ingress.py` implements the rclpy-free ROS2-to-DORA command ingress for:

- `agent_cancel`
- `asr_control`
- `playback_command`

These paths convert ROS2-facing Pydantic projections back into existing
fluent-dialogue-dora contracts and DORA metadata. They do not define new command
semantics.

Agent approval responses are intentionally not DORA ingress. Approval requests
are observable on `agent_approval`; responses go to the Codex control plane over
REST so Web and non-Web operators share one explicit control boundary.

## rclpy Sidecar

`sidecar.py` is the real ROS2 generated-message boundary. It publishes DORA
inputs to `/fluent_dialogue_dora/*` ROS2 topics and subscribes to explicit
`/fluent_dialogue_dora/in/*` command topics for DORA ingress. This file imports
`rclpy` and `fluent_dialogue_dora_interfaces`, so it is intentionally outside the
normal rclpy-free unit-test path.

`bridges/ros2_bridge/fluent_dialogue_dora_interfaces` defines the intended ROS2 message package,
including agent cancel ingress messages. ASR control and playback command ingress
reuse the same explicit command message contracts that are projected outward on
their observation topics.
`scripts/run_ros2_bridge_sidecar_smoke.sh` builds the IDL package, imports the
generated messages, publishes a sidecar DORA event to a real ROS2 topic, and
publishes real ROS2 ingress messages back into typed DORA outputs when a
ROS2/colcon environment is available. `scripts/run_ros2_bridge_sidecar_smoke_docker.sh`
runs the same sidecar smoke in `ros:jazzy-ros-base`.

## Not Connected Yet

- The ASR control stream-final marker has no ROS2 command message shape yet; it
  only closes the pure projection stream.
