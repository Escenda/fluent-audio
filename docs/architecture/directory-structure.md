# Directory Structure

This repo separates three things that should not be mixed:

- shared contracts and library code
- executable DORA nodes
- dataflow declarations
- runtime verification material

## Top Level

```text
fluent-audio/
├── src/fluent_audio/
├── nodes/
├── dataflows/
├── docs/
└── tests/
```

## Shared Package

```text
src/fluent_audio/
├── contracts/
├── dora/
└── offline/
```

`src/fluent_audio` is not where every runtime node lives. It holds reusable contracts and helpers.
Contracts, DORA payload helpers, and offline helpers are added here only when they have explicit typed boundaries.

## Executable Nodes

```text
nodes/
├── io/
│   ├── sources/
│   │   ├── raw_pcm_source/
│   │   └── cpal_capture/
│   └── sinks/
│       ├── raw_pcm_sink/
│       └── cpal_sink/
├── media_graph/
├── perception/
│   ├── vad/
│   ├── turn_detector/
│   └── nemotron_streaming/
├── synthesis/
│   └── tts_backend/
├── interaction/
│   ├── dialogue_engine/
│   └── playback_queue/
├── agent/
│   └── codex_app_server/
└── bridges/
    ├── ros2_bridge/
    └── web_session_projection/
```

Each leaf node directory owns one process boundary. A node directory may be Python, Rust, or mixed-language implementation, but the implementation belongs to that node directory.

The `io` boundary is split into sources and sinks because production and consumption have different failure and validation surfaces.

`media_graph` remains a single DORA node. GStreamer or other in-process media graph taxonomy stays internal to that node and does not leak into repo directory names.

`perception` reads state or meaning from audio: VAD, turn detection, and ASR.

`synthesis` creates audio from text or other synthesis-ready inputs.

`interaction` owns conversation progression and playback control.

`agent` owns agent runtime connectivity. The app-server connector node is named `codex_app_server`.

`bridges` owns ROS2 and Web projection boundaries. Bridges validate external payloads before passing them inward.

Expected leaf node directory shape:

```text
nodes/<category>/.../<node_name>/
├── README.md
├── main.py            # Python node, when applicable
├── config.py          # typed config, when applicable
└── node.toml          # node metadata, when useful
```

Rust-heavy nodes keep their Rust code under the owning node directory. Do not restore a top-level `crates/` directory without explicit human approval.

## Dataflows

```text
dataflows/
├── offline_roundtrip_dataflow.yml
├── device_loopback_dataflow.yml
└── voice_turn_slice_dataflow.yml
```

Dataflows wire nodes together. They should not define hidden behavior. Format, sample rate, channel count, and queue policy must be explicit.

Dataflow declarations are added only when the referenced node scaffold exists and the verification command is known.
