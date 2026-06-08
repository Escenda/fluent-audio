# raw_pcm_source

Reads headerless PCM from disk and emits `AudioChunk`.

It must not decode, resample, infer format, or fill missing audio.

Current implementation provides the pure offline source logic and a CLI smoke wrapper.
DORA output is intentionally not implemented in this step.

Example:

```bash
python nodes/io/sources/raw_pcm_source/main.py \
  --input tests/fixtures/offline/input.s16le \
  --sample-rate-hz 16000 \
  --channels 1 \
  --sample-format s16le \
  --chunk-frames 320 \
  --source-id offline_file \
  --stream-id audio/offline/mono16k \
  --chunks-jsonl artifacts/offline/chunks.jsonl
```
