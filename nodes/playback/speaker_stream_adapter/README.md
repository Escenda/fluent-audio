# speaker_stream_adapter

Adapts `playback_queue` request-boundary audio into one continuous speaker
stream.

`playback_queue` emits an audio final marker after each TTS request. That is a
request boundary, not necessarily the end of a long-lived speaker device. This
node validates those request final markers, suppresses them, and emits a single
speaker stream final only when the upstream DORA audio input closes.

Use this node before `media_graph` / `cpal_sink` in live multi-turn sessions.
