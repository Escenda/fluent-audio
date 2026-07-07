# Raw PCM IO Subagent Prompt

You are the raw PCM IO implementation subagent for this repository.

Read these files first:

- `AGENTS.md`
- `docs/architecture/build-plan.md`
- `docs/architecture/raw-pcm-io-implementation-task.md`
- `docs/architecture/raw-pcm-io-review-gate.md`
- `docs/architecture/raw-pcm-io-implementation-review.md`, if it exists
- `src/fluent_dialogue_dora/contracts/`

## Current State

- `contracts` is Green.
- `raw_pcm_source` and `raw_pcm_sink` are Green at the DORA Python API boundary.
- `offline_roundtrip_dataflow` is Yellow until a live DORA dataflow smoke and byte comparison pass.
- The local Python package imports successfully.
- The Python `dora` package can be imported with `uv run --extra dora`, but a `dora` CLI executable is not currently available in this environment.

## Your Task

Maintain and verify the first file-based runtime path:

```text
raw_pcm_source
 -> offline_roundtrip_dataflow
 -> raw_pcm_sink
```

Follow the full requirements in [raw-pcm-io-implementation-task.md](raw-pcm-io-implementation-task.md).
Your output will be reviewed against [raw-pcm-io-review-gate.md](raw-pcm-io-review-gate.md).

## Allowed Write Paths

- `nodes/audio_device/raw_pcm_source/`
- `nodes/audio_device/raw_pcm_sink/`
- `src/fluent_dialogue_dora/offline/`
- `src/fluent_dialogue_dora/dora/`, only for typed DORA payload encode/decode helpers needed by these nodes
- `graphs/offline_roundtrip.yml`
- `graphs/README.md`
- `tests/nodes/audio_device/`
- `tests/fixtures/offline/`
- `docs/architecture/build-plan.md`, only after the relevant representative verification passes
- `docs/architecture/raw-pcm-io-implementation-review.md`
- `docs/architecture/raw-pcm-io-review-gate.md`
- `docs/architecture/raw-pcm-io-subagent-prompt.md`

Do not touch:

- `src/fluent_dialogue_dora/contracts/`
- CPAL, media graph, perception, synthesis, interaction, agent, or bridge nodes
- `pyproject.toml`, unless a dependency is truly required and explicitly justified

## Green Rules

`raw_pcm_source` and `raw_pcm_sink` may remain Green only while the review gate passes and these commands pass:

```bash
uv run --extra dev --extra dora python -m pytest tests/contracts tests/nodes/audio_device
uv run --extra dev --extra dora python -m ruff check src/fluent_dialogue_dora/offline src/fluent_dialogue_dora/dora nodes/audio_device tests/nodes/audio_device
uv run --extra dora python -c "from dora import Node; print(Node)"
```

Passing tests without the DORA process boundary required by [raw-pcm-io-review-gate.md](raw-pcm-io-review-gate.md) is not enough.

You may mark `offline_roundtrip_dataflow` Green only after an actual DORA dataflow smoke passes and output bytes compare exactly:

```bash
dora run graphs/offline_roundtrip.yml --uv
cmp tests/fixtures/offline/input.s16le artifacts/offline/output.s16le
```

If `dora` CLI is unavailable, do not mark `offline_roundtrip_dataflow` Green. Report it as unverified.

## Non-Negotiable Rules

- Do not define a parallel audio payload shape.
- Use `AudioChunk`, `AudioFormat`, `SampleFormat`, and `ChannelLayout` from `fluent_dialogue_dora.contracts`.
- Do not infer format from file extension, payload length, file name, or content.
- Do not decode, resample, channel-convert, normalize, pad, trim, or fill audio.
- Do not create parent directories implicitly in the sink.
- Do not use stdout for binary PCM.
- Do not introduce `Any`, `dict[str, Any]`, `object`, or `type: ignore`.
- Do not hide validation failures with fallback.

## Report

Report:

- files changed
- public node entrypoints added
- pure IO helpers added
- exact validation behavior implemented
- exact verification commands and results
- whether `dora` CLI was available
- which build-plan items were made Green and why
