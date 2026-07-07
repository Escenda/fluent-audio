# Graphs

DORA graphs are kept only when they verify a concrete boundary or representative
runtime path. Avoid adding overlapping smoke graphs whose only difference is an
older approval or fixture shape.

Representative groups:

- media/device foundations: `offline_roundtrip.yml`, `media_graph_passthrough.yml`,
  `media_graph_resample.yml`, `cpal_capture_smoke.yml`, `cpal_sink_smoke.yml`
- perception: `vad_speech_smoke.yml`, `turn_detector_smoke.yml`,
  `asr_nemotron_smoke.yml`
- agent/dialogue: `codex_app_server_fixture_turn_smoke.yml`,
  `codex_app_server_approval_fixture_smoke.yml`,
  `codex_app_server_permissions_approval_fixture_smoke.yml`,
  `codex_app_server_web_approval_fixture_smoke.yml`,
  `dialogue_to_cpal_smoke.yml`
- file-driven realtime session: generated
  `graphs/out/file_realtime_session_smoke.local.yml`
- live hardware voice session: generated
  `graphs/out/live_hardware_voice_session.local.yml`
- synthesis/playback: `tts_pyopenjtalk_smoke.yml`,
  `playback_queue_cpal_sink_smoke.yml`, `tts_pyopenjtalk_cpal_smoke.yml`
- guarded live Codex checks: `codex_app_server_live_turn_smoke.yml`,
  `codex_app_server_live_approval_smoke.yml`

Every dataflow must make format, sample rate, channel count, queue policy, and boundary validation explicit.

For a full non-live verification pass, run:

```bash
scripts/run_non_live_completion_smoke.sh
```

This aggregate runner intentionally does not start live Codex model turns or
live approval turns. By default it does run CPAL hardware smokes, the real
PyOpenJTalk smoke, the real Nemotron DORA smoke, and the Docker/Jazzy ROS2
sidecar smoke. Those may be explicitly excluded with the script's `--skip-*`
options when auditing a narrower environment. Live Codex model turns remain
guarded by `FLUENT_DIALOGUE_DORA_ALLOW_LIVE_CODEX_TURN=1`.

## File Realtime Session Smoke

`scripts/run_file_realtime_session_smoke.sh` replaces mic capture with
`wav_pcm_source` and replays a fixture WAV at mic-like pacing through the
realtime voice path:

`wav_pcm_source` -> `media_graph` -> `vad` -> `turn_detector` ->
`asr_control_from_turn` -> `nemotron_streaming` -> `dialogue_engine` ->
`codex_app_server` fixture -> `tts_backend` fixture -> `playback_queue` ->
`dora_web_bridge`.

The script uses the real Nemotron streaming ASR backend, but uses fixture
Codex/TTS endpoints so the smoke does not consume live model budget and does
not depend on speaker hardware. It writes an environment-specific dataflow
under `graphs/out`:

```bash
scripts/run_file_realtime_session_smoke.sh --write-dataflow
scripts/run_file_realtime_session_smoke.sh --run
```

`--run` starts the live DORA Web bridge inside the dataflow. The bridge is a
bounded live transport, so it does not persist a post-run dashboard snapshot.

## Live Hardware Voice Session

`scripts/run_live_hardware_voice_session.sh` is the live mic/speaker path:

`cpal_capture` -> `media_graph_asr` -> `vad` -> `turn_detector` ->
`asr_control_from_turn` -> `nemotron_streaming` -> `dialogue_engine` ->
live `codex_app_server` on local vLLM -> real `tts_pyopenjtalk_server` through
`tts_backend` -> `playback_queue` -> `speaker_stream_adapter` ->
`media_graph_speaker` -> `cpal_sink`, with live dashboard transport through
`dora_web_bridge`.

The speaker path uses `speaker_stream_adapter` because `playback_queue` emits
audio final markers at TTS request boundaries. The adapter keeps the hardware
speaker stream open across multiple assistant turns, then `media_graph_speaker`
converts PyOpenJTalk's `f32le` mono 48 kHz stream to the current CPAL sink
contract of `s16le` stereo 48 kHz.

Generate the local dataflow without starting live model turns:

```bash
scripts/run_live_hardware_voice_session.sh --write-dataflow
```

Start the live dashboard and hardware session:

```bash
FLUENT_DIALOGUE_DORA_ALLOW_LIVE_CODEX_TURN=1 scripts/run_live_hardware_voice_session.sh --serve
```

The default CPAL selector is the explicit device id used by the hardware smokes:
`alsa:hw:CARD=APE,DEV=0`. Override it without fallback by setting exactly one
selector for input and output:

```bash
FLUENT_DIALOGUE_DORA_CPAL_INPUT_DEVICE_ID=alsa:hw:CARD=APE,DEV=0
FLUENT_DIALOGUE_DORA_CPAL_OUTPUT_DEVICE_ID=alsa:hw:CARD=APE,DEV=0
FLUENT_DIALOGUE_DORA_USE_DEFAULT_INPUT_DEVICE=1
FLUENT_DIALOGUE_DORA_USE_DEFAULT_OUTPUT_DEVICE=1
```

For a bounded run instead of an open live session:

```bash
FLUENT_DIALOGUE_DORA_ALLOW_LIVE_CODEX_TURN=1 \
FLUENT_DIALOGUE_DORA_CAPTURE_MAX_CHUNKS=3000 \
scripts/run_live_hardware_voice_session.sh --run
```

## PyOpenJTalk To CPAL Speaker

`tts_pyopenjtalk_cpal_smoke.yml` verifies real TTS synthesis through the hardware
speaker path without starting Codex or vLLM:

`tts_text_replay` -> `tts_backend` -> real `tts_pyopenjtalk_server` ->
`playback_queue` -> `speaker_stream_adapter` -> `media_graph_speaker` ->
`cpal_sink`.

Run it with:

```bash
scripts/run_tts_pyopenjtalk_cpal_smoke.sh
```

## Offline Roundtrip

`offline_roundtrip.yml` wires `raw_pcm_source/audio` to `raw_pcm_sink/audio`.
The source reads `tests/fixtures/offline/input.s16le` as explicit mono 16 kHz
`s16le` interleaved PCM. The sink writes `artifacts/offline/output.s16le`
with overwrite enabled.

The sink does not create parent directories. Before a live DORA smoke, create
`artifacts/offline` explicitly, then run:

```bash
dora run graphs/offline_roundtrip.yml --uv
cmp tests/fixtures/offline/input.s16le artifacts/offline/output.s16le
```

## Codex App-Server Live Turn

`codex_app_server_fixture_turn_smoke.yml` verifies the direct DORA boundary
without a live model provider:

```bash
scripts/run_codex_app_server_fixture_smoke.sh
```

`codex_app_server_approval_fixture_smoke.yml` verifies the same direct boundary
with a fixture command approval request and a REST approval response through
`dora_web_bridge`:

```bash
uvx --from dora-rs-cli dora run graphs/codex_app_server_approval_fixture_smoke.yml --uv
```

`codex_app_server_permissions_approval_fixture_smoke.yml` verifies the same
REST approval loop for Codex `item/permissions/requestApproval`, whose JSON-RPC
response schema is `{permissions, scope}` rather than `{decision}`:

```bash
uvx --from dora-rs-cli dora run graphs/codex_app_server_permissions_approval_fixture_smoke.yml --uv
```

`codex_app_server_web_approval_fixture_smoke.yml` verifies the Web-mediated
approval loop without starting a live model turn:

`agent_turn_replay` -> `codex_app_server` -> `agent_approval` ->
`dora_web_bridge` / `dora_web_approval_submitter` -> Codex control REST ->
`codex_app_server`.

Run it through the script:

```bash
scripts/run_codex_app_server_web_approval_fixture_smoke.sh
```

`dialogue_to_cpal_smoke.yml` is the representative integrated voice path. Its
dialogue control edge uses ordered `codex_app_server/agent_event` into
`dialogue_engine`; split `agent_text`, `agent_done`, `agent_approval`, and
`agent_tool` outputs remain observation inputs for Web projection, ROS2
projection, and probes. This avoids treating separate DORA output ids as an
ordered control stream.

`codex_app_server_live_turn_smoke.yml` wires a typed `AgentTurnRequest` replay
source to the real `codex_app_server` DORA node and validates `agent_text` /
`agent_done` with `agent_output_probe`. It uses `--sandbox read-only` and
`--approval-policy never` because the smoke is only for model turn streaming,
not tool execution or approval routing.

Do not run the live turn smoke casually. Use the guarded script:

```bash
scripts/run_codex_app_server_live_smoke.sh --write-live-turn-dataflow
FLUENT_DIALOGUE_DORA_ALLOW_LIVE_CODEX_TURN=1 scripts/run_codex_app_server_live_smoke.sh --live-turn
```

The first command only writes the local generated dataflow under `graphs/out`
and does not start a model turn.

## Codex App-Server Live Approval

`codex_app_server_live_approval_smoke.yml` is the guarded representative shape
for real Codex command approval routing. It wires:

`agent_turn_replay` -> `codex_app_server` -> `agent_approval` ->
`dora_web_bridge` / `dora_web_approval_submitter` -> Codex control REST ->
`codex_app_server`, while
`agent_output_probe` validates the final agent output.

The static dataflow uses `--approval-policy on-request` because this smoke is
specifically for command/file approval routing. The script writes an
environment-specific dataflow under `graphs/out`:

```bash
scripts/run_codex_app_server_live_smoke.sh --write-live-approval-dataflow
FLUENT_DIALOGUE_DORA_ALLOW_LIVE_CODEX_TURN=1 scripts/run_codex_app_server_live_smoke.sh --live-approval
```

Like the live turn smoke, the approval smoke is guarded because it starts a real
model turn and can consume model/API budget.
