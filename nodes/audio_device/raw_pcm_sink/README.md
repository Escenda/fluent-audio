# raw_pcm_sink

Receives `AudioChunk` and writes headerless PCM to disk.

It must reject sequence gaps, format changes, and frame count mismatch.

Current implementation provides the pure offline sink logic, a CLI smoke wrapper
that reads chunk JSONL created by `raw_pcm_source`, and a DORA mode that receives
input `audio` as raw PCM bytes with flat typed metadata.
