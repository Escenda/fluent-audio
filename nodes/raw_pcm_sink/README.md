# raw_pcm_sink

Receives `AudioChunk` and writes headerless PCM to disk.

It must reject sequence gaps, format changes, and frame count mismatch.
