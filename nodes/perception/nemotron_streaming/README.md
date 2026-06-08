# nemotron_streaming

Owns streaming ASR session orchestration for a Nemotron-compatible backend.

## Current status

Yellow. The DORA node boundary and session/prebuffer logic are implemented and tested,
but the actual NeMo/Nemotron backend is not wired or smoke-tested yet. Do not mark this
node green until the real model runs on target hardware.

## DORA ids

Inputs:

- `audio`: typed `AudioChunk` stream from `media_graph`
- `asr_control`: typed `AsrStart` / `AsrStop` / `AsrCancel`

Output:

- `transcript`: typed `TranscriptDelta`, `TranscriptFinal`, and transcript stream final marker

## Stream id convention

`AsrControl.stream_id` identifies the input audio stream that should be transcribed.
`TranscriptDelta.stream_id` and `TranscriptFinal.stream_id` use this node's configured
output transcript stream id.

Downstream nodes must correlate transcript events by `session_id` and `user_turn_id`,
not by assuming the transcript stream id equals the source audio stream id.

## Implemented behavior

The node currently:

- requires explicit 16 kHz mono `s16le` input unless configured otherwise
- keeps a bounded audio history for ASR prebuffer replay
- slices retained audio exactly when `AsrStart.start_sample_index` lands inside a chunk
- starts the backend on `AsrStart`
- replays retained audio from `start_sample_index`
- pushes live audio while a turn is active
- waits when `AsrStop.stop_sample_index` points to future audio
- slices the final active chunk at `stop_sample_index`
- rejects stop commands that would require undoing audio already pushed to the backend
- rejects duplicate starts, stop/cancel without an active turn, mismatched ids, stream mismatch,
  control sequence discontinuity, audio discontinuity, and audio final while a turn is active
- emits a transcript stream final marker only after explicit audio completion

## Not implemented yet

- NeMo/PyTorch dependency profile for this target machine
- `nvidia/nemotron-3.5-asr-streaming-0.6b` model download/cache setup
- real cache-aware FastConformer-RNNT backend wiring
- target-hardware streaming smoke
- conversion from NeMo growing hypotheses into true transcript deltas, if NeMo returns
  full interim hypotheses rather than append-only deltas

The production backend must not emit growing hypotheses as `TranscriptDelta` unless it computes
the actual appended text delta first.

## Verification

Current partial verification:

```bash
uv run --extra dev --extra dora python -m pytest \
  tests/nodes/perception/test_nemotron_streaming_logic.py \
  tests/nodes/perception/test_nemotron_streaming_node.py
uv run --extra dev --extra dora python -m ruff check \
  nodes/perception/nemotron_streaming \
  tests/nodes/perception/test_nemotron_streaming_logic.py \
  tests/nodes/perception/test_nemotron_streaming_node.py
```
