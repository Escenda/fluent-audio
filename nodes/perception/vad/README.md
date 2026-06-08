# vad

Silero ONNX VAD node for DORA audio streams.

## DORA ids

- Input id: `audio`
- Output id: `activity`

## CLI

```bash
python nodes/perception/vad/main.py \
  --dora \
  --input-source-id vad_speech_fixture \
  --input-stream-id audio/vad/speech \
  --output-source-id silero_vad \
  --output-stream-id activity/vad/speech \
  --threshold 0.5
```

`--model-path` is optional. When omitted, the node uses the pinned ONNX model at
`nodes/perception/vad/models/silero_vad_16k_op15.onnx`.

## Input contract

The node accepts only 16 kHz mono `s16le` interleaved PCM carried as typed DORA
`AudioChunk` events. `source_id`, `stream_id`, format, `seq`, and `sample_index` must
match the configured stream exactly.

The node fails closed on:

- format mismatch, including non-16 kHz input, non-mono input, or non-`s16le` input
- source or stream mismatch
- `seq` or `sample_index` discontinuity
- `STOP` before a completion signal, or `INPUT_CLOSED` before any audio chunk
- event stream end without an explicit DORA audio final marker or DORA `INPUT_CLOSED`

The node does not infer missing timing and does not use latest/empty/default audio as a
fallback.

## Output contract

Each Silero result becomes one `VoiceActivityEvent` encoded by
`encode_voice_activity_event_for_dora` and sent on DORA output `activity`.

`VoiceActivityEvent.sample_index` is the input stream sample index plus the Silero
`window_start_frame`. Full windows carry `frame_count=512`. A final partial window is
evaluated with explicit zero padding, but its emitted `frame_count` is the number of
source frames that actually existed. The activity final marker `sample_index` is copied
from the input audio final marker or exact DORA `INPUT_CLOSED` boundary.

After processing the input audio final marker, or DORA `INPUT_CLOSED` when prior chunks
make the final sample index exact, the node flushes the Silero session and sends one
`encode_voice_activity_final_marker_for_dora` marker on `activity`.

## Model provenance

- File: `nodes/perception/vad/models/silero_vad_16k_op15.onnx`
- SHA-256: `7ed98ddbad84ccac4cd0aeb3099049280713df825c610a8ed34543318f1b2c49`
- Provenance: pinned Silero VAD 16 kHz ONNX opset 15 model from the upstream Silero VAD project.
- License: upstream Silero VAD is distributed under the MIT license.

The runtime validates the model hash in `SileroVadConfig`; replacing the model requires
updating `EXPECTED_MODEL_SHA256` and rerunning the VAD test and DORA smoke paths.

## Fixture provenance

- `tests/fixtures/vad/harvard_16k_mono_32768f.s16le`: 16 kHz mono `s16le`, 32,768 frames, SHA-256 `88d29430409ce56fd5edfc29bbb6efa04a90397f2d8f07fcef229f7fa722b164`.
- `tests/fixtures/vad/silence_16k_mono_1024f.s16le`: 16 kHz mono `s16le`, 1,024 frames, SHA-256 `e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad`.

## Verification

```bash
uv run --extra dev --extra dora --extra vad python -m pytest tests/contracts tests/nodes/perception
uv run --extra dev --extra dora --extra vad python -m ruff check .
uvx --from dora-rs-cli dora run dataflows/vad_speech_smoke.yml --uv
```
