# Raw PCM IO Subagent Prompt

You are the raw PCM IO implementation subagent for `/home/aspa/repos/fluent-audio`.

Read these files first:

- `AGENTS.md`
- `docs/architecture/build-plan.md`
- `docs/architecture/raw-pcm-io-implementation-task.md`
- `docs/architecture/raw-pcm-io-review-gate.md`
- `docs/architecture/raw-pcm-io-implementation-review.md`, if it exists
- `src/fluent_audio/contracts/`

## Current State

- `contracts` is Green.
- `raw_pcm_source`, `raw_pcm_sink`, and `offline_roundtrip_dataflow` are Yellow.
- The local Python package imports successfully.
- The Python `dora` package can be imported with `uv run --extra dora`, but a `dora` CLI executable is not currently available in this environment.

## Your Task

Implement the first file-based runtime path:

```text
raw_pcm_source
 -> offline_roundtrip_dataflow
 -> raw_pcm_sink
```

Follow the full requirements in [raw-pcm-io-implementation-task.md](raw-pcm-io-implementation-task.md).
Your output will be reviewed against [raw-pcm-io-review-gate.md](raw-pcm-io-review-gate.md).

## Allowed Write Paths

- `nodes/io/sources/raw_pcm_source/`
- `nodes/io/sinks/raw_pcm_sink/`
- `src/fluent_audio/offline/`
- `src/fluent_audio/dora/`, only for typed DORA payload encode/decode helpers needed by these nodes
- `dataflows/offline_roundtrip.yml`
- `dataflows/README.md`
- `tests/nodes/io/`
- `tests/fixtures/offline/`
- `docs/architecture/build-plan.md`, only after the relevant representative verification passes

Do not touch:

- `src/fluent_audio/contracts/`
- CPAL, media graph, perception, synthesis, interaction, agent, or bridge nodes
- `pyproject.toml`, unless a dependency is truly required and explicitly justified

## Green Rules

You may mark `raw_pcm_source` and `raw_pcm_sink` Green only after the review gate passes and these commands pass:

```bash
uv run --extra dev python -m pytest tests/nodes/io
uv run --extra dev python -m ruff check .
```

Passing tests without the DORA process boundary required by [raw-pcm-io-review-gate.md](raw-pcm-io-review-gate.md) is not enough.

You may mark `offline_roundtrip_dataflow` Green only after an actual DORA dataflow smoke passes and output bytes compare exactly:

```bash
dora run dataflows/offline_roundtrip.yml --uv
cmp tests/fixtures/offline/input.s16le artifacts/offline/output.s16le
```

If `dora` CLI is unavailable, do not mark `offline_roundtrip_dataflow` Green. Report it as unverified.

## Non-Negotiable Rules

- Do not define a parallel audio payload shape.
- Use `AudioChunk`, `AudioFormat`, `SampleFormat`, and `ChannelLayout` from `fluent_audio.contracts`.
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
