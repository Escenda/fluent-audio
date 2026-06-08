# raw_pcm_source

Reads headerless PCM from disk and emits `AudioChunk`.

It must not decode, resample, infer format, or fill missing audio.
