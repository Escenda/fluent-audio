# Directory Structure

This repo separates three things that should not be mixed:

- shared contracts and library code
- executable DORA nodes
- dataflow declarations

## Top Level

```text
fluent-audio/
├── src/fluent_audio/
├── nodes/
├── crates/
├── dataflows/
├── tests/
└── docs/
```

## Shared Package

```text
src/fluent_audio/
├── contracts/
│   ├── audio.py
│   ├── playback.py
│   ├── vad.py
│   ├── asr.py
│   └── session.py
├── offline/
│   ├── raw_pcm.py
│   └── wav.py
└── dora/
    ├── encoding.py
    └── node_io.py
```

`src/fluent_audio` is not where every runtime node lives. It holds reusable contracts and helpers.

## Executable Nodes

```text
nodes/
├── offline/
│   ├── raw_pcm_source/
│   └── raw_pcm_sink/
├── device/
│   ├── cpal_capture/
│   └── cpal_sink/
├── media/
│   └── media_graph/
├── activity/
│   ├── vad/
│   ├── audio_window/
│   └── turn_detector/
├── asr/
│   └── nemotron_streaming/
├── dialogue/
│   └── dialogue_engine/
├── agent/
│   └── codex_app_server_connector/
├── tts/
│   └── tts_backend/
├── playback/
│   └── playback_queue/
└── bridges/
    ├── ros2_bridge/
    └── web_session_projection/
```

Each node directory owns one process boundary. A node directory may be Python, Rust, or a thin launcher over a Rust crate.

Expected node directory shape:

```text
nodes/<layer>/<node_name>/
├── README.md
├── main.py            # Python node, when applicable
├── config.py          # typed config, when applicable
└── node.toml          # node metadata, when useful
```

Rust-heavy nodes are implemented in `crates/nodes/<node_name>` and launched from the matching `nodes/<layer>/<node_name>` directory.

## Rust Node Crates

```text
crates/nodes/
├── cpal_capture/
├── cpal_sink/
└── media_graph/
```

CPAL and GStreamer belong here because they are low-level runtime components, not Python application logic.

## Dataflows

```text
dataflows/
├── 00_offline_audio_roundtrip.yml
├── 01_device_loopback.yml
└── 02_voice_turn_slice.yml
```

Dataflows wire nodes together. They should not define hidden behavior. Format, sample rate, channel count, and queue policy must be explicit.
