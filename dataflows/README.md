# Dataflows

Dataflows are added only when their referenced nodes exist.

Planned order:

1. `offline_roundtrip_dataflow.yml`
2. `device_loopback_dataflow.yml`
3. `voice_turn_slice_dataflow.yml`

Every dataflow must make format, sample rate, channel count, queue policy, and boundary validation explicit.
