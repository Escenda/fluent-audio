# Directory Structure

This repo separates the things that should not be mixed:

- generated contracts and runtime helper code
- executable DORA nodes
- bridge boundaries
- graph declarations
- runtime verification material

## Top Level

```text
fluent-audio/
├── contracts/
├── nodes/
├── bridges/
├── apps/
├── graphs/
├── environments/
├── tools/
├── src/fluent_audio/
├── docs/
└── tests/
```

## Contracts

```text
contracts/
├── proto/
│   └── fluent_audio/
│       └── v1/
├── python/
├── rust/
└── typescript/
```

`contracts/proto` is the schema source of truth. Generated language packages
live under `contracts/<language>`.

`src/fluent_audio` holds runtime helpers that are not generated contract code:
DORA payload helpers, offline IO helpers, and shared typed utilities.

## Executable Nodes

```text
nodes/
├── audio_device/
│   ├── raw_pcm_source/
│   ├── wav_pcm_source/
│   ├── raw_pcm_sink/
│   ├── audio_probe/
│   ├── cpal_capture/
│   ├── cpal_sink/
│   └── rust_audio_boundary/
├── media_graph/
├── vad/
│   ├── silero/
│   ├── turn_detector/
├── asr/
│   ├── asr_control_from_turn/
│   ├── nemotron_streaming/
│   └── transcript_replay/
├── dialogue_engine/
│   ├── main.py
│   ├── agent_output_probe.py
│   └── codex_app_server/
├── tts/
│   ├── tts_backend/
│   ├── tts_pyopenjtalk_server/
│   ├── synth_audio_replay/
│   └── synth_audio_probe.py
├── playback/
│   ├── playback_queue/
│   └── speaker_stream_adapter/
└── diagnostics/
```

Each leaf node directory owns one process boundary. A node directory may be
Python, Rust, or mixed-language implementation, but implementation belongs to
that node directory.

`audio_device` owns audio ingress/egress, including file-backed replay nodes and
CPAL hardware nodes.

`media_graph` remains a single DORA node. GStreamer or other in-process media graph taxonomy stays internal to that node and does not leak into repo directory names.

`vad` owns speech activity and turn-boundary detection.

`asr` owns ASR control, streaming ASR, and transcript replay/probing.

`dialogue_engine` owns voice-surface orchestration and the Codex app-server
boundary used by that surface.

`tts` owns text-to-speech boundaries and synthesis probes.

`playback` owns playback scheduling and speaker-stream adaptation.

## Bridges

```text
bridges/
├── ros2_bridge/
│   ├── fluent_audio_interfaces/
│   ├── main.py
│   ├── ingress.py
│   ├── messages.py
│   └── sidecar.py
└── dora_web_bridge/
    ├── dashboard.html
    ├── decoder.py
    ├── main.py
    ├── messages.py
    └── projection.py
```

Bridges validate external payloads before passing them inward. ROS2 and Web are
outside the primary audio and agent execution path.

Rust-heavy nodes keep their Rust code under the owning node directory. Do not restore a top-level `crates/` directory without explicit human approval.

## Graphs

```text
graphs/
├── offline_roundtrip.yml
├── media_graph_passthrough.yml
├── vad_speech_smoke.yml
└── out/
```

Graphs wire nodes together. They should not define hidden behavior. Format,
sample rate, channel count, and queue policy must be explicit.

Generated local graph variants live under `graphs/out`.
