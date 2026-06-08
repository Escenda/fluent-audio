# turn_detector

Deterministically converts DORA voice activity events into typed DORA turn events.

## DORA ids

- Input id: `activity`
- Output id: `turn`

## CLI

```bash
python nodes/perception/turn_detector/main.py \
  --dora \
  --input-source-id silero_vad \
  --input-stream-id activity/vad/speech \
  --session-id session-smoke \
  --output-stream-id turn/session-smoke \
  --end-silence-frames 2048
```

## Input contract

The node consumes `VoiceActivityEvent` values encoded by
`decode_voice_activity_event_from_dora`. Input `source_id`, `stream_id`, `seq`, and
`sample_index` must match the configured stream exactly. Completion is accepted either
as an explicit voice activity final marker or as DORA `INPUT_CLOSED` after at least one
activity event, where the last event gives an exact final sample index.

The node fails closed on:

- source or stream mismatch
- activity `seq` or `sample_index` discontinuity
- `STOP` before activity completion
- `INPUT_CLOSED` before any activity event
- event stream end without completion

## Output contract

Each emitted `TurnEvent` is encoded by `encode_turn_event_for_dora` and sent on DORA
output `turn`.

Rules:

- first speech in idle state emits `started`
- additional speech in the same turn emits `active`
- silence after speech accumulates evidence
- once accumulated silence reaches `end_silence_frames`, the node emits `ended`
- `ended.sample_index` is the last speech end, not the silence end
- stream completion flushes an active turn as `ended`
- silence-only streams emit no turn events

After activity completion, the node sends one `encode_turn_final_marker_for_dora`
marker on `turn`.

## Verification

```bash
uv run --extra dev --extra dora --extra vad python -m pytest tests/contracts tests/nodes/perception
uv run --extra dev --extra dora --extra vad python -m ruff check .
uvx --from dora-rs-cli dora run dataflows/turn_detector_smoke.yml --uv
```
