# Raw PCM IO Implementation Task

This task is for the implementation subagent that will build the first verified IO path after `contracts` is green.

## Dependency

Do not start this task until `contracts` is green in [build-plan.md](build-plan.md).

The raw PCM source and sink must use the public contracts from `src/fluent_audio/contracts/`. They must not define a parallel audio payload shape.

## Goal

Implement the first file-based runtime path:

```text
raw_pcm_source
 -> offline_roundtrip_dataflow
 -> raw_pcm_sink
```

This path exists to verify the audio transport contract before CPAL, GStreamer, VAD, or ASR are introduced.

## Write Scope

Allowed paths:

- `nodes/io/sources/raw_pcm_source/`
- `nodes/io/sinks/raw_pcm_sink/`
- `src/fluent_audio/offline/`
- `src/fluent_audio/dora/`, only for typed DORA payload encode/decode helpers needed by these nodes
- `dataflows/offline_roundtrip.yml`
- `dataflows/README.md`
- `tests/nodes/io/`
- `tests/fixtures/offline/`
- `docs/architecture/build-plan.md`, only after the representative verification passes

Do not touch:

- `src/fluent_audio/contracts/`, except to report a missing contract requirement
- CPAL, media graph, perception, synthesis, interaction, agent, or bridge nodes
- `pyproject.toml`, unless a dependency is truly required and explicitly justified in the report

## raw_pcm_source Requirements

`raw_pcm_source` reads headerless PCM from disk and emits ordered `AudioChunk` records.

Required behavior:

- Accept explicit input path.
- Accept explicit `AudioFormat`: sample rate, channel count, sample format, and channel layout.
- Accept explicit `source_id`, `stream_id`, `chunk_frames`, `start_seq`, `start_sample_index`, and `capture_time_ns`.
- Support `s16le` and `f32le`, matching the contract phase.
- Reject missing files.
- Reject `chunk_frames <= 0`.
- Reject file sizes that are not divisible by one frame.
- Emit the final partial chunk if the file has a partial chunk boundary but a whole number of frames.
- Never infer format from file extension, payload length, file name, or content.
- Never decode, resample, channel-convert, normalize, pad, trim, or fill audio.

Required outputs:

- DORA output: `audio`
- Payload: audio bytes
- Metadata: typed fields sufficient to reconstruct and validate `AudioChunk`

The implementation may have a small pure function for iterating chunks so unit tests can verify behavior without launching DORA.

## raw_pcm_sink Requirements

`raw_pcm_sink` receives `AudioChunk` records and writes headerless PCM bytes to disk.

Required behavior:

- Accept explicit output path.
- Accept explicit expected `AudioFormat`, `source_id`, and `stream_id`.
- Accept explicit overwrite behavior. Refuse to overwrite unless enabled.
- Reject missing parent directory instead of creating it implicitly.
- Reject format mismatch.
- Reject source or stream mismatch.
- Reject payload/frame mismatch through `AudioChunk` validation.
- Reject sequence gaps, repeated sequence numbers, and wrong `sample_index`.
- Write bytes exactly as received.
- Do not write WAV headers or sidecar metadata in this path.

Required inputs:

- DORA input: `audio`
- Payload: audio bytes
- Metadata: typed fields sufficient to reconstruct and validate `AudioChunk`

The implementation may have a small pure writer/validator class so unit tests can verify behavior without launching DORA.

## DORA Encoding

Use the DORA Python API for node IO. Do not use stdout for binary PCM.

The DORA boundary should be explicit:

- audio bytes travel as payload
- contract fields travel as metadata
- metadata is validated back into `AudioChunk` at the receiving boundary

If DORA metadata cannot carry a required type directly, introduce a typed encode/decode helper under `src/fluent_audio/dora/`. Do not use untyped dictionaries past that boundary.

## Offline Roundtrip Dataflow

Add `dataflows/offline_roundtrip.yml`.

Required properties:

- Wires `raw_pcm_source/audio` to `raw_pcm_sink/audio`.
- Uses explicit sample rate, channel count, sample format, channel layout, source id, stream id, chunk frames, and queue policy.
- Uses fixture paths under `tests/fixtures/offline/` for testable local smoke runs.
- Does not hide decode, resample, or conversion behavior in node args.

## Tests

Add tests under `tests/nodes/io/`.

Required coverage:

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
- sink rejects wrong `sample_index`
- source-to-sink pure roundtrip writes byte-identical output

Do not mark DORA dataflow green based only on pure unit tests.

## Green Update

Only after all representative verification commands pass:

- Update [build-plan.md](build-plan.md).
- Change `raw_pcm_source` and `raw_pcm_sink` from Yellow to Green after their unit tests pass.
- Change `offline_roundtrip_dataflow` from Yellow to Green only after the DORA dataflow smoke and byte comparison pass.
- Keep CPAL and later runtime nodes Yellow.

Representative verification:

```bash
uv run --extra dev python -m pytest tests/nodes/io
uv run --extra dev python -m ruff check .
dora run dataflows/offline_roundtrip.yml --uv
cmp tests/fixtures/offline/input.s16le artifacts/offline/output.s16le
```

If `dora` is unavailable in the local environment, report that explicitly and do not make `offline_roundtrip_dataflow` green.

## Report

Report:

- files changed
- public node entrypoints added
- pure IO helpers added
- exact validation behavior implemented
- exact verification commands and results
- whether the DORA smoke was actually run
- which build-plan items were made green and why
