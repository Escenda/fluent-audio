# transcript_replay

Replay node for dialogue-layer integration tests.

It emits one `TranscriptFinal` followed by an explicit transcript stream-final
marker. It is not an ASR backend. It exists so the dialogue and downstream
agent/TTS/playback boundaries can be smoke-tested without running ASR.

Output:

- `transcript`: final transcript and stream-final marker encoded with
  `fluent_dialogue_dora.dora.transcript`.
