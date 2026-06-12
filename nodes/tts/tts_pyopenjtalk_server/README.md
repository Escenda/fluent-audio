# tts_pyopenjtalk_server

Fixed-voice PyOpenJTalk HTTP endpoint for the `tts_backend` contract.

Implemented endpoint:

- `GET /health`
- `POST /synthesize`

The server accepts `TtsBackendPostRequest` and returns NDJSON
`TtsBackendAudioChunkEvent` / `TtsBackendAudioDoneEvent` lines. It does not
become a DORA node; `tts_backend` remains the DORA-to-HTTP boundary.

Audio contract:

- output sample format: `f32le`
- channels: `1`
- layout: `interleaved`
- waveform input domains accepted from PyOpenJTalk: normalized `[-1.0, 1.0]`
  float or int16-scale `[-32768, 32768]` float, normalized to `f32le`
- non-mono, empty, non-finite, or out-of-range waveforms fail closed

Smoke:

```bash
scripts/run_tts_pyopenjtalk_smoke.sh
```
