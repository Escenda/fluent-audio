# nemotron_streaming

Owns streaming ASR session orchestration for a Nemotron-compatible backend.

## Current status

Green for the real-model DORA node boundary. The DORA node boundary,
session/prebuffer logic, explicit NeMo backend configuration surface, NeMo cache-aware
backend, and target-hardware DORA smoke are implemented and verified with
`nvidia/nemotron-3.5-asr-streaming-0.6b`.

The current representative DORA smoke verifies non-empty `TranscriptFinal` delivery.
It does not prove low-latency transcript delta behavior because the short fixture emitted
zero deltas before the final transcript.

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
- rejects stop commands that exceed `control_holdback_frames` beyond audio already pushed to the backend
- rejects stop commands that point behind audio already pushed to the backend
- rejects duplicate starts, stop/cancel without an active turn, mismatched ids, stream mismatch,
  control sequence discontinuity, audio discontinuity, and audio final while a turn is active
- treats DORA `asr_control` `INPUT_CLOSED` as a transport-close signal; already queued
  control commands may still arrive after it, and completion is accepted only after no ASR turn
  remains active
- emits a transcript stream final marker only after explicit audio completion
- validates explicit NeMo backend settings through `--backend nemo`
- loads the NeMo cache-aware RNNT model from either a local `.nemo` file or a model name
- buffers one bounded user turn for the NeMo backend and runs the cache-aware ASR path at stop
- emits a non-empty `TranscriptFinal` at turn stop when ASR recognizes text
- consumes empty final backend results as explicit no-transcript turns without
  emitting `TranscriptFinal`

## CLI backend surface

The CLI requires an explicit backend:

```bash
python nodes/asr/nemotron_streaming/main.py \
  --dora \
  --input-audio-source-id media_graph \
  --input-audio-stream-id audio/asr/input \
  --session-id session-1 \
  --output-stream-id transcript/main \
  --backend nemo \
  --model-name nvidia/nemotron-3.5-asr-streaming-0.6b \
  --target-lang auto \
  --att-context-right-frames 3
```

`--att-context-right-frames` must be one of `0`, `1`, `3`, `6`, or `13`,
corresponding to 80 ms, 160 ms, 320 ms, 560 ms, and 1120 ms chunk settings.

## Remaining work

- production model cache policy for `--model-name` when a Hugging Face id is used
- latency/throughput measurement under expected microphone chunk sizes
- a longer or live-input fixture that proves low-latency `TranscriptDelta` behavior
- backend work to make true live deltas reliable with Nemotron's cache-aware streaming path

The current Nemotron backend intentionally emits final transcripts only. Direct tiny-chunk
`append_audio()` attempts produced unstable hypotheses on the smoke fixture; live delta support
must be reintroduced only after the backend can emit append-only deltas without rewrites.

## Verification

Unit verification:

```bash
uv run --extra dev --extra dora python -m pytest \
  tests/nodes/asr/test_nemotron_streaming_backend.py \
  tests/nodes/asr/test_nemotron_streaming_logic.py \
  tests/nodes/asr/test_nemotron_streaming_node.py
uv run --extra dev --extra dora python -m ruff check \
  nodes/asr/nemotron_streaming \
  tests/nodes/asr/test_nemotron_streaming_backend.py \
  tests/nodes/asr/test_nemotron_streaming_logic.py \
  tests/nodes/asr/test_nemotron_streaming_node.py
```

Target-hardware DORA smoke already run:

- Python:
  `$FLUENT_AUDIO_NEMOTRON_PYTHON`
- Model:
  `$FLUENT_AUDIO_NEMOTRON_MODEL`
- Audio:
  `$FLUENT_AUDIO_NEMOTRON_SMOKE_WAV`
- Result:
  `TranscriptFinal(text="The stales")` through
  `raw_pcm_source -> media_graph -> vad -> turn_detector -> asr_control_from_turn -> nemotron_streaming -> transcript_probe`
- Command:
  `uvx --from dora-rs-cli dora run graphs/out/asr_nemotron_smoke.local.yml`
