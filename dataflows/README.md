# Dataflows

Dataflows are added only when their referenced nodes exist.

Planned order:

1. `offline_roundtrip.yml`
2. `device_loopback_dataflow.yml`
3. `voice_turn_slice_dataflow.yml`

Every dataflow must make format, sample rate, channel count, queue policy, and boundary validation explicit.

## Offline Roundtrip

`offline_roundtrip.yml` wires `raw_pcm_source/audio` to `raw_pcm_sink/audio`.
The source reads `tests/fixtures/offline/input.s16le` as explicit mono 16 kHz
`s16le` interleaved PCM. The sink writes `artifacts/offline/output.s16le`
with overwrite enabled.

The sink does not create parent directories. Before a live DORA smoke, create
`artifacts/offline` explicitly, then run:

```bash
dora run dataflows/offline_roundtrip.yml --uv
cmp tests/fixtures/offline/input.s16le artifacts/offline/output.s16le
```
