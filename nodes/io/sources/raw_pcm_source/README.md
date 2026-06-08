# raw_pcm_source

Reads headerless PCM from disk and emits `AudioChunk`.

It must not decode, resample, infer format, or fill missing audio.

Current implementation provides the pure offline source logic, a CLI smoke wrapper,
and a DORA mode that sends raw PCM bytes on output `audio` with flat typed metadata.

Example:

```bash
python nodes/io/sources/raw_pcm_source/main.py \
  --input tests/fixtures/offline/input.s16le \
  --sample-rate-hz 16000 \
  --channels 1 \
  --sample-format s16le \
  --channel-layout interleaved \
  --chunk-frames 320 \
  --source-id offline_file \
  --stream-id audio/offline/mono16k \
  --start-capture-time-ns 0 \
  --chunks-jsonl artifacts/offline/chunks.jsonl
```

DORA mode:

```bash
python nodes/io/sources/raw_pcm_source/main.py \
  --dora \
  --input tests/fixtures/offline/input.s16le \
  --sample-rate-hz 16000 \
  --channels 1 \
  --sample-format s16le \
  --channel-layout interleaved \
  --chunk-frames 320 \
  --source-id offline_file \
  --stream-id audio/offline/mono16k \
  --start-capture-time-ns 0
```
