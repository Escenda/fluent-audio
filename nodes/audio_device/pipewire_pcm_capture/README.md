# pipewire_pcm_capture

DORA source node that captures raw PCM from a named PipeWire source through
`pw-record --target`.

Use this when the capture source must be explicit, such as a USB conference
speaker/microphone that appears as `PowerConf S3 Mono` in `wpctl status`.
Prefer the PipeWire `node.name` from `wpctl inspect <id>` because DORA graph
arguments are whitespace-delimited; display names with spaces should not be used
in generated dataflows.

The node emits fluent-audio `AudioChunk` protobuf payloads on `audio` and an
explicit audio stream final marker when the bounded capture ends.
