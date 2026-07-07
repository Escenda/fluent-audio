# codex_app_server

Typed DORA boundary between `dialogue_engine` and Codex app-server JSON-RPC.

This node does not embed Codex core and does not implement a model runtime,
tool registry, MCP execution, approval policy, or model-provider layer. It:

- reads DORA `agent_turn` and `agent_cancel`
- reads DORA `agent_user_input_response` while a tool user-input request is pending
- reads DORA `agent_mcp_elicitation_response` while an MCP elicitation request is pending
- accepts HTTP approval responses on its control REST endpoint while a
  command/file/permissions approval is pending
- starts or reuses a Codex thread per voice session
- sends text turns through Codex `turn/start`
- sends cancellation through Codex `turn/interrupt`
- sends JSON-RPC responses to Codex command/file/permissions approval requests
- sends JSON-RPC responses to Codex tool user-input and MCP elicitation requests
- validates Codex JSON-RPC server messages
- emits ordered DORA `agent_event` for dialogue control
- emits split DORA `agent_text`, `agent_done`, `agent_approval`,
  `agent_user_input`, `agent_mcp_elicitation`, and `agent_tool` for
  observation/projection

## Inputs

- `agent_turn`: decoded with `decode_agent_turn_request_from_dora`
- `agent_cancel`: decoded with `decode_agent_cancel_request_from_dora`
- `agent_user_input_response`: decoded with
  `decode_agent_user_input_response_from_dora`
- `agent_mcp_elicitation_response`: decoded with
  `decode_agent_mcp_elicitation_response_from_dora`

Browser approval responses are submitted over HTTP to the control REST endpoint,
not through a DORA input.

## Outputs

- `agent_event`: ordered control stream carrying `AgentTextDelta`,
  `AgentTurnDone`, `AgentApprovalRequest`, `AgentUserInputRequest`,
  `AgentMcpElicitationRequest`, or `AgentToolEvent`
- `agent_text`: `AgentTextDelta`
- `agent_done`: `AgentTurnDone`
- `agent_approval`: `AgentApprovalRequest`
- `agent_user_input`: `AgentUserInputRequest`
- `agent_mcp_elicitation`: `AgentMcpElicitationRequest`
- `agent_tool`: `AgentToolEvent`

## Codex Boundary

The default process command is:

```bash
codex app-server --listen stdio://
```

The command can be overridden with exactly one of
`--app-server-command ...`, `--app-server-command-json`, or
`--app-server-command-file`. Use the file form for DORA dataflows and
fixtures; it stores one argument per nonblank, non-comment UTF-8 line and
avoids `argparse.REMAINDER` ambiguity inside DORA `args` strings. The node
speaks line-oriented JSON-RPC messages using the Codex app-server schema
shape:

- `thread/start`
- `turn/start`
- `turn/interrupt`
- `item/agentMessage/delta`
- `turn/completed`
- `item/started`
- `item/completed`
- `item/commandExecution/requestApproval`
- `item/fileChange/requestApproval`
- `item/permissions/requestApproval`
- `item/tool/requestUserInput`
- `mcpServer/elicitation/request`
- `serverRequest/resolved`

Subprocess stdout/stderr are consumed by queue-backed reader threads. This is
part of the runtime contract: line buffering in Python `TextIOWrapper` can hold
a complete JSON-RPC line after `readline()`, so readiness must not depend on
`select()` against the underlying file descriptor.

The live Codex app-server protocol requires `initialize` followed by the
client `initialized` notification before `thread/start`. The node sends that
handshake on subprocess startup and ignores typed non-turn notifications such as
`configWarning` and `remoteControl/status/changed` while waiting for responses.
`--sandbox` can be supplied explicitly when a deployment wants to override the
Codex thread sandbox; the node does not silently escalate it.

`item/permissions/requestApproval` is parsed, projected as
`AgentApprovalRequest`, tracked as a permissions approval, and answered with a
permission-profile JSON-RPC response derived from the typed HTTP approval
response submitted to the control REST endpoint. `item/tool/requestUserInput`
and `mcpServer/elicitation/request` are
projected as dedicated voice requests and answered only by matching typed DORA
responses.

Browser approval responses are not DORA inputs. Codex stdout events are projected
directly to DORA outputs by the stdout reader, while the DORA input loop remains
responsible only for incoming turns, cancellations, and typed DORA responses.
Approval responses are submitted through the control REST endpoint and never
require the Codex node to poll DORA while waiting for REST input.

Each turn stream must end with exactly one `turn_done`. Missing terminal events,
events after `turn_done`, thread/turn mismatch, invalid JSON, unsupported
server requests, or Codex JSON-RPC errors raise node errors instead of being
hidden.

## Current Status

Implemented:

- typed DORA boundary
- Codex JSON-RPC stdio transport
- live app-server `initialize` / `initialized` handshake
- `thread/start`, `turn/start`, `turn/interrupt`
- ordered `agent_event` projection for text delta, turn completion,
  command/file/permissions approval requests, tool user-input requests, MCP
  elicitation requests, and MCP/dynamic tool lifecycle events
- split observation outputs for Web/ROS2/probes
- command/file/permissions approval response routing through the Codex control
  REST plane
- tool user-input response routing through DORA `agent_user_input_response`
- MCP elicitation response routing through DORA `agent_mcp_elicitation_response`
- unit tests with fake transport and JSON-RPC message projection, including
  tool user-input and MCP elicitation DORA-loop responses

Verified:

- direct DORA fixture smoke with `agent_turn_replay` ->
  `codex_app_server` -> `agent_output_probe`
- command approval fixture smoke with `agent_turn_replay` ->
  `codex_app_server` -> `dora_web_bridge` / `dora_web_approval_submitter` ->
  Codex control REST -> `codex_app_server` -> `agent_output_probe`
- permissions approval fixture smoke for Codex
  `item/permissions/requestApproval`, including `{permissions, scope}` JSON-RPC
  response routing through the same control REST plane
- Web-mediated approval fixture smoke with `agent_turn_replay` ->
  `codex_app_server` -> `dora_web_bridge` / `dora_web_approval_submitter` ->
  Codex control REST -> `codex_app_server` ->
  `agent_output_probe`
- schema-shaped JSON-RPC fixture smoke with one command approval
  request/response is covered by `dialogue_to_cpal_smoke`, using
  `--app-server-command-file tests/fixtures/jsonrpc/codex_app_server_smoke.command`
- live `codex app-server --listen stdio://` initialization and `thread/start`
  handshake without starting a model turn through
  `scripts/run_codex_app_server_live_smoke.sh --handshake-only`

Not yet verified:

- live permission-profile approval response routing against the real Codex
  process.
- live tool user-input request/response routing against the real Codex process.
- live MCP elicitation request/response routing against the real Codex process.
