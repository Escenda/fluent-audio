# wav_pcm_source

`wav_pcm_source` replays a 16-bit PCM WAV file as timed `AudioChunk` DORA
events. It is meant to replace `cpal_capture` in automated runs when the rest
of the graph should see mic-like chunk timing.

It does not decode compressed formats and does not resample. Use `media_graph`
after this node for format conversion, or prepare the WAV explicitly.

Example:

```bash
python nodes/audio_device/wav_pcm_source/main.py \
  --dora \
  --input tests/fixtures/vad/harvard_16k_mono.wav \
  --chunk-frames 512 \
  --source-id wav_fixture \
  --stream-id audio/file/harvard \
  --start-capture-time-ns 0 \
  --expected-sample-rate-hz 16000 \
  --expected-channels 1 \
  --replay-speed 1.0
```
