# Bridges

Bridges connect the fluent-audio core runtime to external ecosystems.

- `ros2_bridge` projects core state, commands, events, and selected data taps to
  ROS2.
- `dora_web_bridge` exposes selected DORA topics to the dashboard through live
  REST/SSE transport and proxies browser approval responses to the Codex control
  REST plane.
