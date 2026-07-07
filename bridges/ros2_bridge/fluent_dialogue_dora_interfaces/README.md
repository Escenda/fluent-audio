# fluent_dialogue_dora_interfaces

ROS2 message package for the `fluent-dialogue-dora` bridge boundary.

This package mirrors the typed projection models in
`bridges/ros2_bridge/messages.py`. It is not a compatibility layer for the
old `fa_interfaces` package; the new contract keeps string `session_id` /
`user_turn_id`, explicit audio/transcript/activity final markers, and audio
`seq` / `sample_index` fields. Agent approval responses and agent cancel
requests are included as ROS2-to-DORA ingress messages for robot-side approval
and interruption surfaces.

This repository can statically validate the IDL files without ROS2 installed.
Building the package still requires a sourced ROS2 environment and `colcon`.
