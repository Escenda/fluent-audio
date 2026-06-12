# dialogue_engine

Owns the voice interaction surface: turns, interruption, TTS chunk scheduling, approval voice loop, and agent event mapping.

It is not the agent runtime itself.

## Current status

Green. The executable DORA node is unit-tested as a typed voice surface and is
wired into the representative `dialogue_to_cpal` dataflow with
`codex_app_server`, TTS, playback, Web projection, Web approval response ingress,
and ROS2 JSONL projection.

## DORA ids

Inputs:

- `transcript`: typed `TranscriptFinal` and transcript stream final marker from ASR
- `dialogue_input`: typed `DialogueInput` for cancel/playback surface commands
- `agent_event`: ordered agent runtime event from the agent boundary. It carries
  `AgentTextDelta`, `AgentTurnDone`, `AgentApprovalRequest`, or
  `AgentToolEvent`.
- `playback_done`: typed `PlaybackDone` from playback

Outputs:

- `agent_turn`: typed `AgentTurnRequest` to the agent boundary
- `agent_cancel`: typed `AgentCancelRequest` to the agent boundary
- `session`: typed `VoiceSessionEvent`
- `dialogue`: typed `DialogueEvent`
- `tts_text`: typed `TtsTextChunk` and `TtsTextStreamFinal` marker

## Implemented behavior

- converts final transcripts into agent turn requests
- emits session events for user turn finalization, assistant start, completion, interruption, and errors
- forwards ordered agent text deltas as dialogue events
- chunks agent text on configured punctuation delimiters for TTS
- flushes residual TTS text when `AgentTurnDone(status="completed")` arrives
- emits an explicit TTS text stream-final marker when the assistant turn completes
- emits agent cancel requests when the voice surface receives cancel input
- rejects shutdown while an agent turn is still active

The node does not create model clients, tool registries, MCP connections, or
approval policy. Those belong to the external agent runtime boundary.

## Verification

```bash
uv run --extra dev --extra dora python -m pytest \
  tests/contracts/test_dialogue.py \
  tests/contracts/test_dora_dialogue.py \
  tests/contracts/test_synthesis.py \
  tests/contracts/test_dora_synthesis.py \
  tests/nodes/dialogue_engine/test_dialogue_engine_node.py
uv run --extra dev --extra dora python -m ruff check \
  src/fluent_audio/contracts/dialogue.py \
  src/fluent_audio/dora/dialogue.py \
  src/fluent_audio/contracts/synthesis.py \
  src/fluent_audio/dora/synthesis.py \
  nodes/dialogue_engine \
  tests/nodes/dialogue_engine/test_dialogue_engine_node.py
scripts/run_dialogue_to_cpal_smoke.sh
```
