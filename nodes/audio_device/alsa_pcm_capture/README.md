# alsa_pcm_capture

DORA source node that captures explicit PCM from an ALSA PCM device such as
`pipewire` by spawning `arecord` and framing stdout as fluent-dialogue-dora
`AudioChunk` protobuf payloads.

This is an explicit capture backend, not a fallback for CPAL. Select it in the
live hardware graph with:

```bash
FLUENT_DIALOGUE_DORA_INPUT_BACKEND=alsa_pcm
FLUENT_DIALOGUE_DORA_ALSA_CAPTURE_DEVICE=pipewire
```
