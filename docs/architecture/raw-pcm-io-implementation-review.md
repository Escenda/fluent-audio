# Raw PCM IO Implementation Review

Status: not green.

Review target: current uncommitted raw PCM IO implementation candidate:

- `src/fluent_audio/offline/raw_pcm.py`
- `nodes/io/sources/raw_pcm_source/main.py`
- `nodes/io/sinks/raw_pcm_sink/main.py`
- `tests/nodes/io/test_raw_pcm.py`

## Verdict

Do not mark `raw_pcm_source`, `raw_pcm_sink`, or `offline_roundtrip_dataflow` Green yet.

The current candidate adds useful offline helper code, CLI wrappers, and tests. It is closer, but it still does not satisfy [raw-pcm-io-implementation-task.md](raw-pcm-io-implementation-task.md) or [raw-pcm-io-review-gate.md](raw-pcm-io-review-gate.md).

## Verified Commands

```bash
uv run --extra dev python -m ruff check src/fluent_audio/offline/raw_pcm.py
uv run --extra dev python -m pytest tests/nodes/io
uv run --extra dev python -m ruff check .
uv run --extra dev python - <<'PY'
from fluent_audio.offline.raw_pcm import RawPcmReadConfig, iter_raw_pcm_chunks
print(RawPcmReadConfig.__name__)
print(iter_raw_pcm_chunks.__name__)
PY
grep -R "Any\\|dict\\[str\\|object\\|type: ignore" -n nodes/io src/fluent_audio/offline tests/nodes/io || true
grep -R '"sequence"\\|sequence=' -n nodes/io src/fluent_audio/offline tests/nodes/io || true
```

Results:

- ruff passed
- import passed
- `tests/nodes/io`: 16 passed
- no `Any`, `dict[str, Any]`, `object`, or `type: ignore` matches

This command still cannot be used in this environment:

```bash
dora run dataflows/offline_roundtrip.yml --uv
```

Result:

- `dora` CLI is unavailable and `dataflows/offline_roundtrip.yml` does not exist

## Blocking Gaps

### DORA node boundary is not implemented

The current node files are JSONL CLI wrappers. They are useful smoke wrappers, but they do not use the DORA Python API for process IO.

The task requires DORA node IO:

- source DORA output `audio`
- sink DORA input `audio`
- audio bytes as payload
- typed metadata sufficient to reconstruct and validate `AudioChunk`

Until that boundary exists, the raw PCM source/sink should stay Yellow.

### CLI JSONL must not be confused with the runtime transport

`RawPcmChunkJsonRecord` and `--chunks-jsonl` may remain as an offline smoke utility, but they must not be treated as the runtime data path.

If the implementation keeps JSONL, docs/tests must make clear it is an offline diagnostic path, not the DORA audio transport.

### Missing offline roundtrip dataflow

`dataflows/offline_roundtrip.yml` does not exist. Therefore `offline_roundtrip_dataflow` remains Yellow.

### Source config does not accept explicit `capture_time_ns`

[raw-pcm-io-implementation-task.md](raw-pcm-io-implementation-task.md) requires the source to accept explicit `capture_time_ns`.

The current `RawPcmReadConfig` computes capture time from `sample_index` and `sample_rate_hz` instead. That may be useful as a deterministic helper, but it does not satisfy the current explicit source configuration contract.

### Review-gate tests are still incomplete

The suite covers many core cases, but the review gate also requires:

- repeated `seq` rejection
- explicit `capture_time_ns` configuration
- DORA boundary behavior or an explicit not-green report for it

## Correction Request

Send this back to the raw PCM IO implementation subagent:

```text
The current raw PCM IO candidate is not green.

Please continue against:

- docs/architecture/raw-pcm-io-implementation-task.md
- docs/architecture/raw-pcm-io-review-gate.md

Required corrections:

1. Add the remaining review-gate tests, including repeated seq and explicit capture_time_ns configuration.
2. Replace or supplement JSONL CLI wrappers with DORA Python API node IO.
3. Add dataflows/offline_roundtrip.yml only when node entrypoints exist.
4. Change source configuration so explicit capture_time_ns is accepted as required.
5. Keep raw_pcm_source/raw_pcm_sink Yellow until tests/nodes/io and ruff pass.
6. Keep offline_roundtrip_dataflow Yellow unless an actual DORA dataflow smoke and byte comparison pass.

Do not touch src/fluent_audio/contracts/.
Do not infer audio format from path, extension, content, or byte length.
Do not introduce Any, dict[str, Any], object, or type: ignore.
```
