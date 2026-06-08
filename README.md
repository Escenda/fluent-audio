# fluent-audio

Standalone audio runtime for voice-agent and robotics integration.

The core runtime is not a ROS2 graph. ROS2 is a boundary bridge for robot ecosystem integration.

## Layer Order

```text
offline/raw audio contract
 -> device capture/playback
 -> media graph
 -> VAD / audio window / ASR
 -> dialogue engine
 -> agent connector
 -> TTS
 -> playback
 -> bridges
```

## Directory Shape

Shared Python contracts and helpers live under `src/fluent_audio`.

Executable DORA nodes live under `nodes`. A node is a process boundary, so mixed-language nodes are not forced into the Python package.

Rust-heavy node crates live under `crates`.

See [docs/architecture/directory-structure.md](docs/architecture/directory-structure.md).
