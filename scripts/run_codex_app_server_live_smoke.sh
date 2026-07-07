#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:---handshake-only}"

if ! command -v codex >/dev/null; then
  echo "missing required command: codex" >&2
  exit 127
fi

case "${MODE}" in
  --handshake-only)
    cd "${REPO_ROOT}"
    uv run --extra dev --extra dora python - <<'PY'
import os
from pathlib import Path

from nodes.dialogue_engine.codex_app_server.main import (
    CodexAppServerConfig,
    SubprocessCodexJsonRpcTransport,
    resolve_app_server_command,
)

command_file = os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_APP_SERVER_COMMAND_FILE")
command = resolve_app_server_command(
    command_remainder=(),
    command_json=os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_APP_SERVER_COMMAND_JSON"),
    command_file=Path(command_file) if command_file else None,
)

config = CodexAppServerConfig(
    command=command,
    timeout_seconds=float(os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_TIMEOUT_SECONDS", "10")),
    cwd=os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_CWD", os.getcwd()),
    model=os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_MODEL"),
    model_provider=os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_MODEL_PROVIDER"),
    base_instructions=os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_BASE_INSTRUCTIONS"),
    developer_instructions=os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_DEVELOPER_INSTRUCTIONS"),
    sandbox=os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_SANDBOX", "read-only"),
    approval_policy=os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_APPROVAL_POLICY", "never"),
    approvals_reviewer=os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_APPROVALS_REVIEWER", "user"),
)
transport = SubprocessCodexJsonRpcTransport(config)
try:
    thread = transport.ensure_thread_started(
        os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_SESSION_ID", "live-stdio-handshake")
    )
    print(
        {
            "mode": "handshake-only",
            "session_id": thread.session_id,
            "thread_id_present": thread.thread_id != "",
        }
    )
finally:
    transport.close()
PY
    ;;
  --live-turn|--write-live-turn-dataflow|--live-approval|--write-live-approval-dataflow)
    if [[ "${MODE}" == "--live-turn" && "${FLUENT_DIALOGUE_DORA_ALLOW_LIVE_CODEX_TURN:-}" != "1" ]]; then
      echo "live Codex turn not run: set FLUENT_DIALOGUE_DORA_ALLOW_LIVE_CODEX_TURN=1" >&2
      exit 64
    fi
    if [[ "${MODE}" == "--live-approval" && "${FLUENT_DIALOGUE_DORA_ALLOW_LIVE_CODEX_TURN:-}" != "1" ]]; then
      echo "live Codex approval turn not run: set FLUENT_DIALOGUE_DORA_ALLOW_LIVE_CODEX_TURN=1" >&2
      exit 64
    fi
    cd "${REPO_ROOT}"
    mkdir -p graphs/out
    if [[ "${MODE}" == "--live-approval" || "${MODE}" == "--write-live-approval-dataflow" ]]; then
      LIVE_DATAFLOW="graphs/out/codex_app_server_live_approval_smoke.local.yml"
      DATAFLOW_KIND="approval"
    else
      LIVE_DATAFLOW="graphs/out/codex_app_server_live_turn_smoke.local.yml"
      DATAFLOW_KIND="turn"
    fi
    python3 - "${LIVE_DATAFLOW}" "${REPO_ROOT}" "${DATAFLOW_KIND}" <<'PY'
import json
import os
import shlex
import sys
from pathlib import Path


def quoted_args(tokens: list[str]) -> str:
    return " ".join(shlex.quote(token) for token in tokens)


def yaml_args(tokens: list[str]) -> str:
    return json.dumps(quoted_args(tokens))


def write_temp_payload(output_path: Path, name: str, value: str) -> Path:
    payload_dir = output_path.parent / f"{output_path.stem}.payloads"
    payload_dir.mkdir(parents=True, exist_ok=True)
    payload_path = payload_dir / name
    payload_path.write_text(value, encoding="utf-8")
    return payload_path.resolve()


output_path = Path(sys.argv[1])
repo_root = Path(sys.argv[2])
dataflow_kind = sys.argv[3]
session_id = os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_SESSION_ID", "live-turn-smoke")
user_turn_id = os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_USER_TURN_ID", "user-turn-live-smoke")
assistant_turn_id = os.environ.get(
    "FLUENT_DIALOGUE_DORA_CODEX_ASSISTANT_TURN_ID",
    "assistant-turn-live-smoke",
)
expected_text = os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_EXPECTED_TEXT", "fa-live-ok-314159")
if dataflow_kind == "approval":
    session_id = os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_SESSION_ID", "live-approval-smoke")
    user_turn_id = os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_USER_TURN_ID", "user-turn-live-approval")
    assistant_turn_id = os.environ.get(
        "FLUENT_DIALOGUE_DORA_CODEX_ASSISTANT_TURN_ID",
        "assistant-turn-live-approval",
    )
    expected_text = os.environ.get(
        "FLUENT_DIALOGUE_DORA_CODEX_EXPECTED_TEXT",
        "fa-live-approval-ok-271828",
    )
    turn_text = os.environ.get(
        "FLUENT_DIALOGUE_DORA_CODEX_TURN_TEXT",
        "/no_think Use the available shell command tool to run exactly: "
        "printf fa-live-approval-ok-271828. "
        "After the command completes, respond with this exact token only: "
        "fa-live-approval-ok-271828",
    )
else:
    turn_text = os.environ.get(
        "FLUENT_DIALOGUE_DORA_CODEX_TURN_TEXT",
        "/no_think Respond with this exact token only: fa-live-ok-314159",
    )
default_approval_policy = "untrusted" if dataflow_kind == "approval" else "never"
web_bridge_port = os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_WEB_PORT", "18084")
codex_control_port = os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_CONTROL_PORT", "18184")

codex_args = [
    "../../nodes/dialogue_engine/codex_app_server/main.py",
    "--dora",
    "--timeout-seconds",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_TIMEOUT_SECONDS", "60"),
    "--approval-response-timeout-seconds",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_APPROVAL_TIMEOUT_SECONDS", "10"),
    "--cwd",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_CWD", str(repo_root)),
    "--sandbox",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_SANDBOX", "read-only"),
    "--approval-policy",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_APPROVAL_POLICY", default_approval_policy),
    "--approvals-reviewer",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_APPROVALS_REVIEWER", "user"),
]
if dataflow_kind == "approval":
    codex_args.extend(
        [
            "--control-host",
            "127.0.0.1",
            "--control-port",
            codex_control_port,
        ]
    )
optional_args = (
    ("FLUENT_DIALOGUE_DORA_CODEX_MODEL", "--model"),
    ("FLUENT_DIALOGUE_DORA_CODEX_MODEL_PROVIDER", "--model-provider"),
    ("FLUENT_DIALOGUE_DORA_CODEX_APP_SERVER_COMMAND_JSON", "--app-server-command-json"),
    ("FLUENT_DIALOGUE_DORA_CODEX_APP_SERVER_COMMAND_FILE", "--app-server-command-file"),
)
for env_name, flag in optional_args:
    value = os.environ.get(env_name)
    if value:
        codex_args.extend((flag, value))
instruction_file_args = (
    ("FLUENT_DIALOGUE_DORA_CODEX_BASE_INSTRUCTIONS", "--base-instructions-file", "base_instructions.txt"),
    (
        "FLUENT_DIALOGUE_DORA_CODEX_DEVELOPER_INSTRUCTIONS",
        "--developer-instructions-file",
        "developer_instructions.txt",
    ),
)
for env_name, flag, file_name in instruction_file_args:
    value = os.environ.get(env_name)
    if value:
        codex_args.extend((flag, str(write_temp_payload(output_path, file_name, value))))

turn_text_file = write_temp_payload(output_path, "agent_turn_text.txt", turn_text)
agent_turn_node = (
    "  - id: agent_turn_replay\n"
    "    path: python\n"
    "    args: "
    + yaml_args(
        [
            "../../tests/fixtures/dora/agent_turn_replay.py",
            "--dora",
            "--session-id",
            session_id,
            "--user-turn-id",
            user_turn_id,
            "--assistant-turn-id",
            assistant_turn_id,
            "--text-file",
            str(turn_text_file),
        ]
    )
    + "\n"
    "    outputs:\n"
    "      - agent_turn\n"
)

codex_inputs = (
    "      agent_turn:\n"
    "        source: agent_turn_replay/agent_turn\n"
    "        queue_size: 16\n"
    "        queue_policy: backpressure\n"
)
codex_node = (
    "  - id: codex_app_server\n"
    "    path: python\n"
    "    args: "
    + yaml_args(codex_args)
    + "\n"
    "    inputs:\n"
    + codex_inputs
    + "    outputs:\n"
    "      - agent_event\n"
    "      - agent_text\n"
    "      - agent_done\n"
    "      - agent_approval\n"
    "      - agent_tool\n"
)

probe_args = [
    "../../nodes/dialogue_engine/agent_output_probe.py",
    "--dora",
    "--session-id",
    session_id,
    "--user-turn-id",
    user_turn_id,
    "--agent-turn-id",
    assistant_turn_id,
    "--expected-min-text-deltas",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_EXPECTED_MIN_TEXT_DELTAS", "1"),
    "--expected-approval-requests",
    os.environ.get(
        "FLUENT_DIALOGUE_DORA_CODEX_EXPECTED_APPROVAL_REQUESTS",
        "1" if dataflow_kind == "approval" else "0",
    ),
    "--expected-tool-events",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_EXPECTED_TOOL_EVENTS", "0"),
    "--expected-done-status",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_EXPECTED_DONE_STATUS", "completed"),
    "--expected-text-contains",
    expected_text,
]
probe_node = (
    "  - id: agent_output_probe\n"
    "    path: python\n"
    "    args: "
    + yaml_args(probe_args)
    + "\n"
    "    inputs:\n"
    "      agent_text:\n"
    "        source: codex_app_server/agent_text\n"
    "        queue_size: 64\n"
    "        queue_policy: backpressure\n"
    "      agent_done:\n"
    "        source: codex_app_server/agent_done\n"
    "        queue_size: 16\n"
    "        queue_policy: backpressure\n"
    "      agent_approval:\n"
    "        source: codex_app_server/agent_approval\n"
    "        queue_size: 16\n"
    "        queue_policy: backpressure\n"
    "      agent_tool:\n"
    "        source: codex_app_server/agent_tool\n"
    "        queue_size: 16\n"
    "        queue_policy: backpressure\n"
)

approval_nodes = ""
if dataflow_kind == "approval":
    bridge_url = os.environ.get(
        "FLUENT_DIALOGUE_DORA_CODEX_WEB_BRIDGE_URL",
        "http://127.0.0.1:" + web_bridge_port,
    )
    approval_nodes = (
        "\n"
        "  - id: transcript_replay\n"
        "    path: python\n"
        "    args: "
        + yaml_args(
            [
                "../../nodes/asr/transcript_replay/main.py",
                "--dora",
                "--session-id",
                session_id,
                "--user-turn-id",
                user_turn_id,
                "--stream-id",
                "asr/live-approval-smoke",
                "--text",
                "live-approval-smoke",
                "--start-sample-index",
                "0",
                "--end-sample-index",
                "16000",
            ]
        )
        + "\n"
        "    outputs:\n"
        "      - transcript\n"
        "\n"
        "  - id: dora_web_bridge\n"
        "    path: python\n"
        "    args: "
        + yaml_args(
            [
                "../../bridges/dora_web_bridge/main.py",
                "--dora",
                "--session-id",
                session_id,
                "--port",
                web_bridge_port,
                "--codex-control-url",
                "http://127.0.0.1:" + codex_control_port,
                "--input",
                "transcript",
                "--input",
                "agent_approval",
            ]
        )
        + "\n"
        "    inputs:\n"
        "      transcript:\n"
        "        source: transcript_replay/transcript\n"
        "        queue_size: 16\n"
        "        queue_policy: backpressure\n"
        "      agent_approval:\n"
        "        source: codex_app_server/agent_approval\n"
        "        queue_size: 16\n"
        "        queue_policy: backpressure\n"
        "\n"
        "  - id: dora_web_approval_submitter\n"
        "    path: python\n"
        "    args: "
        + yaml_args(
            [
                "../../tests/fixtures/dora/dora_web_approval_submitter.py",
                "--dora",
                "--bridge-url",
                bridge_url,
                "--decision",
                os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_APPROVAL_DECISION", "accept"),
                "--timeout-seconds",
                os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_APPROVAL_TIMEOUT_SECONDS", "20"),
            ]
        )
        + "\n"
        "    inputs:\n"
        "      agent_approval:\n"
        "        source: codex_app_server/agent_approval\n"
        "        queue_size: 16\n"
        "        queue_policy: backpressure\n"
    )

output_path.write_text(
    "nodes:\n" + agent_turn_node + "\n\n" + codex_node + approval_nodes + "\n" + probe_node,
    encoding="utf-8",
)
print(output_path)
PY
    if [[ "${MODE}" == "--write-live-turn-dataflow" || "${MODE}" == "--write-live-approval-dataflow" ]]; then
      exit 0
    fi
    uvx --from dora-rs-cli dora run "${LIVE_DATAFLOW}" --uv
    ;;
  *)
    echo "usage: ${0} [--handshake-only|--write-live-turn-dataflow|--live-turn|--write-live-approval-dataflow|--live-approval]" >&2
    exit 2
    ;;
esac
