cmake_minimum_required(VERSION 3.8)
project(fluent_audio_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)

set(message_files
  "msg/AgentApprovalRequest.msg"
  "msg/AgentCancelRequest.msg"
  "msg/AgentTextDelta.msg"
  "msg/AgentToolEvent.msg"
  "msg/AgentTurnDone.msg"
  "msg/AsrControl.msg"
  "msg/AudioFrame.msg"
  "msg/DialogueEvent.msg"
  "msg/PlaybackCommand.msg"
  "msg/PlaybackDone.msg"
  "msg/PlaybackState.msg"
  "msg/Transcript.msg"
  "msg/TurnEvent.msg"
  "msg/VoiceActivity.msg"
  "msg/VoiceSessionEvent.msg"
)

rosidl_generate_interfaces(${PROJECT_NAME}
  ${message_files}
  DEPENDENCIES std_msgs
)

ament_export_dependencies(rosidl_default_runtime)

ament_package()
