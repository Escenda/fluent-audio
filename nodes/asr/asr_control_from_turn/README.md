# asr_control_from_turn

Converts typed `TurnEvent` boundaries into typed ASR control commands.

Inputs:

- `turn`: `TurnEvent` stream from `turn_detector`

Output:

- `asr_control`: `AsrStart`, `AsrStop`, and `AsrCancel`

`started` emits `AsrStart`. `ended` emits `AsrStop`. `cancelled` emits
`AsrCancel`. `active` is observed for sequence validation but does not emit a
control command.

`--asr-prebuffer-frames` moves `AsrStart.start_sample_index` earlier than the
turn start sample so the ASR node can replay retained prebuffer audio.
