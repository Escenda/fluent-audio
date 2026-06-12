# tts_backend

Typed DORA-to-HTTP boundary for speech synthesis.

This node accepts `tts_text` DORA inputs, validates them as
`TtsTextChunk`, accepts `TtsTextStreamFinal` markers without calling the
backend, POSTs each text chunk as a typed JSON request to a configured HTTP
endpoint, and validates the returned NDJSON/SSE `audio_chunk` / `audio_done` stream.
Validated audio is emitted as `synth_audio` using the shared
`SynthesizedAudioChunk` DORA helpers.

This is not a TTS model runtime. It does not choose a voice, load a model, or
call a local audio library. `nodes/tts/tts_pyopenjtalk_server` is the
current fixed-voice HTTP runtime used for repository real-backend smoke tests.

Contract:

- input: `tts_text`
- output: `synth_audio`
- each `TtsTextChunk.request_id` must produce exactly one `audio_done`
- response `seq`, audio `seq`, audio `sample_index`, and audio format must stay
  continuous within one request
- missing `audio_done`, events after `audio_done`, correlation mismatch, invalid
  base64 payload, and audio format/payload mismatch fail closed

Representative smoke:

```bash
scripts/run_tts_pyopenjtalk_smoke.sh
```
