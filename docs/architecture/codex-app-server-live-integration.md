# Codex App-Server Live Integration

## Boundary

`nodes/dialogue_engine/codex_app_server` is the voice runtime boundary to
`codex app-server --listen stdio://`.

DORA inputs:

- `agent_turn`: finalized user turn text
- `agent_cancel`: voice/runtime cancellation
- `agent_user_input_response`: response to a pending Codex tool user-input request
- `agent_mcp_elicitation_response`: response to a pending MCP elicitation request

DORA outputs:

- `agent_event`: ordered control stream consumed by `dialogue_engine`
- `agent_text`, `agent_done`, `agent_approval`, `agent_user_input`,
  `agent_mcp_elicitation`, `agent_tool`: split observation streams for
  dashboard/ROS2/probes

Browser approval responses are not DORA inputs. They are submitted through HTTP:

```text
Browser
  -> dora_web_bridge REST
  -> codex_app_server control REST
  -> pending Codex JSON-RPC request
```

The `dora_web_bridge` owns only live topic transport. It does not store approval
history or decide whether an approval is pending. Pending approval ownership
lives in `CodexControlQueue` inside `codex_app_server`.

## Approval Runtime Shape

1. `codex_app_server` receives `agent_turn` and starts a Codex turn.
2. Codex emits a JSON-RPC approval request.
3. `codex_app_server` emits the request on ordered `agent_event` and split
   `agent_approval`.
4. `dora_web_bridge` exposes `agent_approval` as a live Web topic.
5. The browser posts a decision to `dora_web_bridge`.
6. `dora_web_bridge` proxies the typed POST body to the `codex_app_server`
   control REST endpoint.
7. `CodexControlQueue` validates that the approval is pending and wakes the
   blocked Codex turn.
8. `codex_app_server` writes the JSON-RPC response to the original Codex request
   id and continues streaming until `agent_done`.

This shape intentionally avoids a Web-approval-to-DORA-output loop. DORA remains
the dataflow and observability plane; approval response is control plane.

## Implemented Mapping

- subprocess startup -> `initialize`
- successful initialize -> client `initialized`
- first turn per session -> `thread/start`
- each `AgentTurnRequest` -> `turn/start`
- `AgentCancelRequest` -> `turn/interrupt`
- `item/agentMessage/delta` -> `agent_event` and `agent_text`
- `turn/completed` -> `agent_event` and `agent_done`
- `item/started` / `item/completed` tool-call items -> `agent_event` and
  `agent_tool`
- `item/commandExecution/requestApproval`,
  `item/fileChange/requestApproval`, and `item/permissions/requestApproval` ->
  `agent_event` and `agent_approval`
- HTTP approval response -> JSON-RPC response for the pending Codex request
- `item/tool/requestUserInput` -> `agent_event` and `agent_user_input`
- `agent_user_input_response` -> JSON-RPC response with Codex `answers`
- `mcpServer/elicitation/request` -> `agent_event` and `agent_mcp_elicitation`
- `agent_mcp_elicitation_response` -> JSON-RPC response with Codex elicitation
  content

Non-turn Codex notifications such as reasoning deltas, rate-limit updates,
startup status, config warnings, and token usage are parsed or consumed without
becoming dialogue control events.

## Verification Targets

Representative non-live checks:

```bash
uv run --extra dev --extra dora python -m pytest \
  tests/nodes/dialogue_engine/test_codex_app_server_node.py \
  tests/bridges/test_dora_web_bridge_node.py

scripts/run_codex_app_server_web_approval_fixture_smoke.sh
uvx --from dora-rs-cli dora run graphs/codex_app_server_approval_fixture_smoke.yml --uv
uvx --from dora-rs-cli dora run graphs/codex_app_server_permissions_approval_fixture_smoke.yml --uv
```

Guarded live checks:

```bash
scripts/run_codex_app_server_live_smoke.sh --write-live-turn-dataflow
FLUENT_AUDIO_ALLOW_LIVE_CODEX_TURN=1 scripts/run_codex_app_server_live_smoke.sh --live-turn

scripts/run_codex_app_server_live_smoke.sh --write-live-approval-dataflow
FLUENT_AUDIO_ALLOW_LIVE_CODEX_TURN=1 scripts/run_codex_app_server_live_smoke.sh --live-approval
```

Do not treat the guarded live checks as complete unless a local model provider
is running and the command output confirms the Codex turn completed.

## Local vLLM Notes

For the larger Qwen3-Coder 30B NVFP4 local server, use
`scripts/run_qwen3_coder_vllm_server.sh`. The script keeps a 128k context and
limits KV reservation with `--max-num-seqs 1`,
`--max-num-batched-tokens 131072`, `--kv-cache-memory-bytes 7G`, and
`--gpu-memory-utilization 0.18`.

The smaller verified local route serves `Qwen/Qwen3-1.7B` with OpenAI-compatible
Responses API, `--enable-auto-tool-choice`, and `--tool-call-parser hermes`.
Do not add `--reasoning-parser qwen3` for this Codex route: it can hide
tool-call JSON inside reasoning output. Raw `agent_text` remains visible, while
`dialogue_engine` performs TTS-facing filtering for literal `<think>...</think>`
blocks.
