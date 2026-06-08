# raw_pcm_sink

Receives `AudioChunk` and writes headerless PCM to disk.

It must reject sequence gaps, format changes, and frame count mismatch.

Current implementation provides the pure offline sink logic and a CLI smoke wrapper
that reads chunk JSONL created by `raw_pcm_source`. DORA input is intentionally not
implemented in this step.
