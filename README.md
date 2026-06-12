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

Proto contracts live under `contracts/proto` and generated Python bindings live
under `contracts/python`.

Executable DORA nodes live under `nodes`. A node is a process boundary, so
mixed-language nodes are not forced into the Python package.

Rust-heavy node implementation lives inside the owning node directory. There is
no top-level `crates/` directory in this runtime scaffold.

```text
fluent-audio/
├── contracts/
│   ├── proto/
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
├── apps/
├── graphs/
├── environments/
├── tools/
├── docs/
└── tests/
```

See [docs/設計/repository-structure.md](docs/設計/repository-structure.md).
Build progress is tracked in [docs/architecture/build-plan.md](docs/architecture/build-plan.md).
