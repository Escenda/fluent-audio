# Contracts Implementation Task

This task is for the implementation subagent that will turn `contracts` from scaffold to verified runtime foundation.

## Goal

Implement the typed contracts required by the first fluent-audio vertical slice:

```text
raw PCM source/sink
 -> media graph
 -> VAD / turn detector / streaming ASR
 -> dialogue engine
 -> Codex app-server connector
 -> TTS backend
 -> playback queue
```

This is not a demo layer. These contracts are the package-level boundary used by DORA nodes and tests.

## Write Scope

Allowed paths:

- `src/fluent_audio/contracts/`
- `tests/contracts/`
- `docs/architecture/build-plan.md`, only after the representative verification passes

Do not touch:

- `nodes/`
- `dataflows/`
- `src/fluent_audio/dora/`
- `src/fluent_audio/offline/`
- `pyproject.toml`, unless a dependency is truly required and explicitly justified in the report

## Required Contract Modules

Use Pydantic v2 `BaseModel` for boundary payloads. Use `Literal`, `Enum`, and concrete nested models. Do not introduce `Any`, `dict[str, Any]`, or `object`.

Suggested module split:

```text
src/fluent_audio/contracts/
├── __init__.py
├── audio.py
├── activity.py
├── transcript.py
├── dialogue.py
├── synthesis.py
└── playback.py
```

The exact filenames can differ if the public imports remain clear.

## Required Payloads

### Audio

Implement:

- `SampleFormat`
- `ChannelLayout`
- `AudioFormat`
- `AudioChunk`

`AudioChunk` must include:

- `source_id`
- `stream_id`
- `seq`
- `sample_index`
- `capture_time_ns`
- `format`
- `frame_count`
- `payload`

Validation requirements:

- `source_id` and `stream_id` are non-empty.
- `seq`, `sample_index`, `capture_time_ns`, and `frame_count` are non-negative.
- `sample_rate_hz` and `channels` are positive.
- `payload` byte length exactly equals `frame_count * channels * bytes_per_sample`.
- Unsupported sample formats fail closed.
- No file extension, device name, payload length, or content is used to guess format.

Add an explicit continuity check method or helper for adjacent chunks. It must reject stream mismatch, format mismatch, non-monotonic `seq`, and incorrect `sample_index`.

Supported sample formats for this phase:

- `s16le`
- `f32le`

Do not add lineage, drop, discontinuity, or clock-domain metadata in this phase.

### Activity / Turn

Implement:

- `VoiceActivityState`
- `VoiceActivityEvent`
- `TurnState`
- `TurnEvent`

These contracts should represent VAD and turn boundary signals without deciding the VAD backend. Keep confidence/probability fields explicit and bounded when present.

### Transcript

Implement:

- `TranscriptDelta`
- `TranscriptFinal`

These must be able to represent streaming ASR output from Nemotron 3.5 ASR Streaming 0.6B without naming that backend in the generic contract.

### Dialogue

Implement:

- `DialogueInput`
- `DialogueEvent`
- `AgentTextDelta`
- `AgentApprovalRequest`
- `AgentToolEvent`
- `AgentCancelRequest`

These are voice-surface contracts. Do not implement a model adapter, tool registry, memory store, or Codex runtime here.

### Synthesis / Playback

Implement:

- `TtsTextChunk`
- `SynthesizedAudioChunk`
- `PlaybackCommand`
- `PlaybackState`
- `PlaybackDone`

`SynthesizedAudioChunk` should reuse `AudioFormat`/audio payload validation rather than defining a second audio shape.

## Tests

Add tests under `tests/contracts/`.

Required coverage:

- valid `AudioChunk` for `s16le`
- valid `AudioChunk` for `f32le`
- payload size mismatch fails
- zero/negative sample rate or channel count fails
- empty `source_id` / `stream_id` fails
- adjacent continuity succeeds for correct next chunk
- adjacent continuity fails for skipped `seq`
- adjacent continuity fails for wrong `sample_index`
- adjacent continuity fails for format mismatch
- VAD probability/confidence bounds fail when out of range
- transcript delta/final models preserve turn/session ids and text
- playback command/state/done models validate explicit command and correlation ids

Do not use broad `Exception` assertions when a specific Pydantic validation error is expected.

## Green Update

Only after all representative verification commands pass:

- Update `docs/architecture/build-plan.md`.
- Change `contracts` from Yellow to Green in the graph and table.
- Keep runtime nodes Yellow.

Representative verification:

```bash
uv run --extra dev python -m pytest tests/contracts
uv run --extra dev python -m ruff check .
```

## Report

Report:

- files changed
- public contract classes added
- validation behavior implemented
- exact verification commands and results
- anything intentionally left out, especially metadata that should not be added before node-level evidence exists
