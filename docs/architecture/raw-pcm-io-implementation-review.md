# Raw PCM IO Implementation Review

Status: source and sink green; offline dataflow yellow.

Review target:

- `src/fluent_audio/dora/audio.py`
- `src/fluent_audio/offline/raw_pcm.py`
- `nodes/audio_device/raw_pcm_source/main.py`
- `nodes/audio_device/raw_pcm_sink/main.py`
- `graphs/offline_roundtrip.yml`
- `tests/nodes/audio_device/test_raw_pcm.py`

## Verdict

`raw_pcm_source` and `raw_pcm_sink` satisfy the DORA node boundary requirements in
[raw-pcm-io-implementation-task.md](raw-pcm-io-implementation-task.md) and
[raw-pcm-io-review-gate.md](raw-pcm-io-review-gate.md).

`offline_roundtrip_dataflow` remains Yellow. The dataflow exists, but the local
environment does not provide a `dora` CLI executable, so the live dataflow smoke
and byte comparison were not run.

## Verified Commands

```bash
uv run --extra dev --extra dora python -m pytest tests/contracts tests/nodes/audio_device
```

Result: 64 passed.

```bash
uv run --extra dev --extra dora python -m ruff check src/fluent_audio/offline src/fluent_audio/dora nodes/audio_device tests/nodes/audio_device
```

Result: passed.

```bash
uv run --extra dora python -c "from dora import Node; print(Node)"
```

Result: `<class 'builtins.Node'>`.

```bash
uv run --extra dora dora --help
command -v dora
```

Result: `dora` CLI unavailable.

```bash
grep -R -n -E 'Any|dict\[str|object|type: ignore' nodes/audio_device src/fluent_audio/offline src/fluent_audio/dora tests/nodes/audio_device
grep -R -n -E '"sequence"|sequence=' nodes/audio_device src/fluent_audio/offline src/fluent_audio/dora tests/nodes/audio_device
```

Result: no matches.

## Boundary Check

Implemented:

- Source DORA output id: `audio`
- Sink DORA input id: `audio`
- Payload: raw PCM `bytes`
- Metadata: flat typed `DoraAudioMetadata`
- Decode path: payload plus metadata reconstructs `AudioChunk`
- Completion: explicit DORA final marker with `final=true` and empty payload
- Sink termination: explicit final marker or DORA `STOP`

The JSONL CLI path remains only an offline smoke utility and is not used as the
runtime transport.

## Remaining Yellow Item

`offline_roundtrip_dataflow` can become Green only after this live path passes:

```bash
dora run graphs/offline_roundtrip.yml --uv
cmp tests/fixtures/offline/input.s16le artifacts/offline/output.s16le
```

The sink intentionally refuses to create parent directories. A live smoke
environment must create `artifacts/offline` explicitly before running the
dataflow.
