# fluent-audio

Standalone audio runtime for voice-agent and robotics integration.

The core runtime is not a ROS2 graph. ROS2 is a boundary bridge for robot ecosystem integration.

## Layer Order

```text
contracts
 -> raw PCM source/sink
 -> offline roundtrip dataflow
 -> CPAL capture/sink
 -> media graph
 -> VAD / turn detector / ASR
 -> dialogue engine
 -> agent runtime connection
 -> TTS
 -> playback queue
 -> bridges
```

## Directory Shape

Shared Python contracts and helpers live under `src/fluent_audio`.

Executable DORA nodes live under `nodes`. A node is a process boundary, so mixed-language nodes are not forced into the Python package.

Rust-heavy node implementation lives inside the owning node directory. There is no top-level `crates/` directory in this runtime scaffold.

```text
fluent-audio/
├── src/fluent_audio/
│   ├── contracts/
│   ├── dora/
│   └── offline/
├── nodes/
│   ├── io/
│   │   ├── sources/
│   │   └── sinks/
│   ├── media_graph/
│   ├── perception/
│   ├── synthesis/
│   ├── interaction/
│   ├── agent/
│   └── bridges/
├── dataflows/
├── docs/
└── tests/
```

See [docs/architecture/directory-structure.md](docs/architecture/directory-structure.md).
Build progress is tracked in [docs/architecture/build-plan.md](docs/architecture/build-plan.md).
