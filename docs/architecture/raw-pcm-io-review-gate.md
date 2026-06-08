# Raw PCM IO Review Gate

Use this checklist when reviewing a raw PCM IO implementation candidate.

The implementation is not green until this gate passes. Passing only a subset of unit tests is not enough.

## Scope Check

Allowed changed paths:

- `nodes/io/sources/raw_pcm_source/`
- `nodes/io/sinks/raw_pcm_sink/`
- `src/fluent_audio/offline/`
- `src/fluent_audio/dora/`, only for typed DORA payload encode/decode helpers needed by these nodes
- `dataflows/offline_roundtrip.yml`
- `dataflows/README.md`
- `tests/nodes/io/`
- `tests/fixtures/offline/`
- `docs/architecture/build-plan.md`
- `docs/architecture/raw-pcm-io-implementation-review.md`
- `docs/architecture/raw-pcm-io-review-gate.md`
- `docs/architecture/raw-pcm-io-subagent-prompt.md`

Reject or request correction if the candidate changes:

- `src/fluent_audio/contracts/`
- CPAL, media graph, perception, synthesis, interaction, agent, or bridge nodes
- `pyproject.toml` without a concrete dependency justification

## Contract Check

The implementation must use the existing public contracts:

- `AudioChunk`
- `AudioFormat`
- `SampleFormat`
- `ChannelLayout`
- `require_contiguous_audio_chunks`

It must not define a second audio payload shape.

Required `AudioChunk` field names are:

- `source_id`
- `stream_id`
- `seq`
- `sample_index`
- `capture_time_ns`
- `frame_count`
- `format`
- `payload`

Reject implementations that use `sequence` as a compatibility alias.

## Source Check

`raw_pcm_source` must:

- read only headerless PCM bytes
- require explicit path, format, ids, `chunk_frames`, `start_seq`, `start_sample_index`, and `start_capture_time_ns`
- support `s16le` and `f32le`
- reject missing file
- reject invalid chunk size
- reject file size that is not divisible by frame size
- emit a final partial chunk only when it still contains a whole number of frames
- never infer format from path, extension, content, or byte length
- never decode, resample, normalize, pad, trim, or channel-convert audio

## Sink Check

`raw_pcm_sink` must:

- write bytes exactly as received
- require explicit output path and expected format/source/stream
- reject overwrite unless explicitly enabled
- reject missing parent directory
- reject source or stream mismatch
- reject format mismatch
- reject payload/frame mismatch through `AudioChunk`
- reject repeated `seq`, skipped `seq`, and wrong `sample_index`
- never write WAV headers or sidecar metadata in this path

## DORA Boundary Check

Binary PCM must not go through stdout.

The DORA boundary must keep:

- audio bytes as payload
- typed contract fields as metadata
- reconstruction/validation through `AudioChunk` at the receiving boundary

If helper code is needed in `src/fluent_audio/dora/`, it must expose typed encode/decode functions and must not leak untyped mappings into deeper runtime code.

## Test Check

Required tests:

- source emits expected chunk count and frame counts for `s16le`
- source emits expected chunk count and frame counts for `f32le`
- source rejects missing file
- source rejects file size not divisible by frame size
- source rejects invalid chunk size
- sink writes byte-for-byte output for valid chunk sequence
- sink rejects overwrite when output exists and overwrite is false
- sink rejects missing parent directory
- sink rejects format mismatch
- sink rejects source/stream mismatch
- sink rejects skipped sequence
- sink rejects repeated sequence
- sink rejects wrong `sample_index`
- pure source-to-sink roundtrip writes byte-identical output
- DORA encode/decode roundtrip
- DORA decode rejects missing or invalid metadata
- source DORA send uses bytes payload and flat metadata
- sink DORA receive writes byte-identical output
- source supports explicit starting capture time in ns

## Verification Commands

Always run:

```bash
uv run --extra dev python -m pytest tests/nodes/io
uv run --extra dev python -m ruff check .
uv run --extra dev python -c "import fluent_audio; print(fluent_audio.__file__)"
grep -R "Any\\|dict\\[str\\|object\\|type: ignore" -n nodes/io src/fluent_audio/offline src/fluent_audio/dora tests/nodes/io || true
grep -R '"sequence"\\|sequence=' -n nodes/io src/fluent_audio/offline src/fluent_audio/dora tests/nodes/io || true
```

`raw_pcm_source` and `raw_pcm_sink` may become Green only after these checks pass and the review checks above are satisfied.

For the DORA boundary phase, also run:

```bash
uv run --extra dev --extra dora python -m pytest tests/contracts tests/nodes/io
uv run --extra dev --extra dora python -m ruff check src/fluent_audio/offline src/fluent_audio/dora nodes/io tests/nodes/io
uv run --extra dora python -c "from dora import Node; print(Node)"
uv run --extra dora dora --help
```

If the final command cannot spawn the `dora` CLI, report that explicitly and keep
`offline_roundtrip_dataflow` Yellow.

## DORA Dataflow Green Rule

`offline_roundtrip_dataflow` stays Yellow unless this exact runtime path is verified:

```bash
dora run dataflows/offline_roundtrip.yml --uv
cmp tests/fixtures/offline/input.s16le artifacts/offline/output.s16le
```

If the `dora` CLI is unavailable, report that explicitly and keep `offline_roundtrip_dataflow` Yellow.
