# Repository Structure

Current target layout:

```text
fluent-dialogue-dora/
├── contracts/
│   ├── proto/
│   │   └── fluent_dialogue_dora/
│   │       └── v1/
│   ├── python/
│   ├── rust/
│   └── typescript/
├── nodes/
│   ├── audio_device/
│   ├── media_graph/
│   ├── vad/
│   ├── asr/
│   ├── dialogue_engine/
│   ├── tts/
│   ├── playback/
│   └── diagnostics/
├── bridges/
│   ├── ros2_bridge/
│   └── dora_web_bridge/
├── apps/
│   ├── live_agent/
│   ├── file_replay/
│   └── dashboard/
├── graphs/
├── environments/
├── docs/
├── tools/
└── tests/
```

`contracts/proto` is the contract source of truth. Generated language bindings
must be reproducible from those proto files.

`nodes` owns DORA process boundaries. In-process media topology stays inside the
owning node, especially `media_graph`.

`bridges` owns external projection boundaries. ROS2 and Web are not the primary
audio execution substrate.

`apps` owns runnable use cases. Apps wire nodes and graphs; they do not define
new message contracts.
