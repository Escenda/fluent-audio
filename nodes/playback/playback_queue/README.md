# playback_queue

`playback_queue` is the typed DORA boundary between synthesized speech audio and
the downstream speaker audio path.

It is not a TTS backend. It does not generate audio.

It is not a CPAL sink. The downstream `audio` output is intended for a speaker
node such as a CPAL sink.

## Inputs

- `synth_audio`: `SynthesizedAudioChunk` encoded by
  `fluent_audio.dora.synthesis.encode_synthesized_audio_chunk_for_dora`.
- `synth_audio` final marker: explicit synthesized-audio request completion
  encoded by `encode_synthesized_audio_final_marker_for_dora`.
- `playback_command`: `stop`, `pause`, `resume`, or `clear` decoded by
  `fluent_audio.dora.playback.decode_playback_command_from_dora`.

## Outputs

- `audio`: speaker-stream `AudioChunk` encoded with
  `fluent_audio.dora.audio.encode_audio_chunk_for_dora`.
- `audio` final marker: explicit speaker-stream completion encoded with
  `fluent_audio.dora.audio.encode_audio_final_marker_for_dora`.
- `playback_state`: queue/playback state encoded with
  `fluent_audio.dora.playback.encode_playback_state_for_dora`.
- `playback_done`: terminal request report encoded with
  `fluent_audio.dora.playback.encode_playback_done_for_dora`.

## Queue Semantics

The node tracks one active synthesized-audio request at a time. For each
request, `request_id`, synthesized `seq`, input audio `seq`, and input audio
`sample_index` must be strictly contiguous. A new synthesized request starts at
synthesized `seq=0`, input audio `seq=0`, and input audio `sample_index=0`.

The downstream speaker `audio` output has its own continuous `seq` and
`sample_index` owned by `playback_queue`. Those counters do not reset when a new
TTS request starts.

`played_frames` is the number of frames this node has handed to the downstream
`audio` boundary. It is not a hardware playback acknowledgement from CPAL.

When playback is paused, incoming `synth_audio` chunks are retained in a bounded
queue. They are not implicitly dropped. If the bounded queue is full, the node
fails closed with an error.

`stop` terminates the active request as `stopped`. `clear` terminates it as
`cancelled`. Both clear retained queued audio and emit speaker audio final
markers plus `playback_done`.

Normal completion requires the synthesized-audio final marker. A DORA `STOP`
while an active request remains is an error and is not reported as completed.
