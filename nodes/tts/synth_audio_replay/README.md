# synth_audio_replay

Replay node for tests and offline evaluation.

It reads explicit-format headerless PCM and emits one synthesized-audio request:
`SynthesizedAudioChunk` events followed by a synthesized-audio final marker.

This is not a TTS backend and does not choose or emulate a voice. It exists so
the downstream speech-output path can be verified without binding the project to
a production TTS runtime.

Output:

- `synth_audio`: chunks and final marker encoded with
  `fluent_audio.dora.synthesis`.
