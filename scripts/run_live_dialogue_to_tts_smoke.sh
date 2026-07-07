#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MODE="${1:---run}"

if ! command -v codex >/dev/null; then
  echo "missing required command: codex" >&2
  exit 127
fi

if [[ "${MODE}" != "--run" && "${MODE}" != "--write-dataflow" ]]; then
  echo "usage: $0 [--run|--write-dataflow]" >&2
  exit 64
fi

if [[ "${MODE}" == "--run" && "${FLUENT_DIALOGUE_DORA_ALLOW_LIVE_CODEX_TURN:-}" != "1" ]]; then
  echo "live Codex turn not run: set FLUENT_DIALOGUE_DORA_ALLOW_LIVE_CODEX_TURN=1" >&2
  exit 64
fi

cd "${REPO_ROOT}"
mkdir -p graphs/out artifacts/live_dialogue_to_tts

CODEX_HOME_DIR="${FLUENT_DIALOGUE_DORA_CODEX_HOME:-${REPO_ROOT}/artifacts/codex_home/live_dialogue_to_tts}"
mkdir -p "${CODEX_HOME_DIR}"
export CODEX_HOME="${CODEX_HOME_DIR}"

LIVE_DATAFLOW="${FLUENT_DIALOGUE_DORA_LIVE_DIALOGUE_TO_TTS_DATAFLOW:-graphs/out/live_dialogue_to_tts_smoke.local.yml}"
TTS_PYOPENJTALK_PORT="${TTS_PYOPENJTALK_PORT:-18084}"
VLLM_BASE_URL="${FLUENT_DIALOGUE_DORA_VLLM_BASE_URL:-http://127.0.0.1:18080/v1}"
VLLM_MODEL="${FLUENT_DIALOGUE_DORA_CODEX_MODEL:-qwen3-1.7b-codex}"
VLLM_PROVIDER="${FLUENT_DIALOGUE_DORA_CODEX_MODEL_PROVIDER:-vllm_local}"
VLLM_WIRE_API="${FLUENT_DIALOGUE_DORA_CODEX_WIRE_API:-responses}"
export VLLM_API_KEY="${VLLM_API_KEY:-dummy}"

TTS_SERVER_PID=""
cleanup() {
  if [[ -n "${TTS_SERVER_PID}" ]] && kill -0 "${TTS_SERVER_PID}" 2>/dev/null; then
    kill "${TTS_SERVER_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT

python3 - "${LIVE_DATAFLOW}" "${REPO_ROOT}" "${VLLM_BASE_URL}" "${VLLM_MODEL}" "${VLLM_PROVIDER}" "${VLLM_WIRE_API}" "${TTS_PYOPENJTALK_PORT}" <<'PY'
import json
import os
import sys
from pathlib import Path


def quoted_args(tokens: list[str]) -> str:
    for token in tokens:
        if token.strip() != token or " " in token or "\t" in token or "\n" in token:
            raise ValueError(f"DORA arg token must not contain whitespace: {token!r}")
    return " ".join(tokens)


def yaml_args(tokens: list[str]) -> str:
    return json.dumps(quoted_args(tokens))


def write_payload(output_path: Path, name: str, value: str) -> Path:
    payload_dir = output_path.parent / f"{output_path.stem}.payloads"
    payload_dir.mkdir(parents=True, exist_ok=True)
    payload_path = payload_dir / name
    payload_path.write_text(value, encoding="utf-8")
    return payload_path.resolve()


output_path = Path(sys.argv[1])
repo_root = Path(sys.argv[2])
vllm_base_url = sys.argv[3]
vllm_model = sys.argv[4]
vllm_provider = sys.argv[5]
vllm_wire_api = sys.argv[6]
tts_port = sys.argv[7]

session_id = os.environ.get("FLUENT_DIALOGUE_DORA_LIVE_DIALOGUE_SESSION_ID", "live-dialogue-tts-smoke")
user_turn_id = os.environ.get("FLUENT_DIALOGUE_DORA_LIVE_DIALOGUE_USER_TURN_ID", "user-turn-live-dialogue-tts")
assistant_turn_id = "assistant-turn-000000"
expected_text = os.environ.get("FLUENT_DIALOGUE_DORA_LIVE_DIALOGUE_EXPECTED_TEXT", "こんにちは。")
transcript_text = os.environ.get(
    "FLUENT_DIALOGUE_DORA_LIVE_DIALOGUE_TRANSCRIPT_TEXT",
    "/no_think Respond with this exact Japanese sentence only: こんにちは。",
)
cwd = os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_CWD", "/tmp/fluent-dialogue-dora-codex-empty-cwd")
Path(cwd).mkdir(parents=True, exist_ok=True)

transcript_text_file = write_payload(output_path, "transcript_text.txt", transcript_text)

command_file = write_payload(
    output_path,
    "codex_app_server.command",
    "\n".join(
        [
            "codex",
            "app-server",
            "--listen",
            "stdio://",
            "--disable",
            "apps",
            "--disable",
            "multi_agent",
            "--disable",
            "multi_agent_v2",
            "--disable",
            "image_generation",
            "--disable",
            "web_search",
            "--disable",
            "browser_use",
            "--disable",
            "computer_use",
            "--disable",
            "standalone_web_search",
            "--disable",
            "web_search_request",
            "--disable",
            "web_search_cached",
            "-c",
            'web_search="disabled"',
            "-c",
            "tools.web_search=false",
            "-c",
            'plugins."creative-production".mcp_servers.creative_production_mcp.enabled=false',
            "-c",
            'plugins."data-analytics".mcp_servers.datascienceWidgets.enabled=false',
            "-c",
            f"model={json.dumps(vllm_model)}",
            "-c",
            f"model_provider={json.dumps(vllm_provider)}",
            "-c",
            f"model_providers.{vllm_provider}.name=\"Local vLLM\"",
            "-c",
            f"model_providers.{vllm_provider}.base_url={json.dumps(vllm_base_url)}",
            "-c",
            f"model_providers.{vllm_provider}.env_key=\"VLLM_API_KEY\"",
            "-c",
            f"model_providers.{vllm_provider}.wire_api={json.dumps(vllm_wire_api)}",
        ]
    )
    + "\n",
)

codex_args = [
    "../../nodes/dialogue_engine/codex_app_server/main.py",
    "--dora",
    "--timeout-seconds",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_TIMEOUT_SECONDS", "180"),
    "--approval-response-timeout-seconds",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_APPROVAL_TIMEOUT_SECONDS", "10"),
    "--cwd",
    cwd,
    "--sandbox",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_SANDBOX", "read-only"),
    "--approval-policy",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_APPROVAL_POLICY", "never"),
    "--approvals-reviewer",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_APPROVALS_REVIEWER", "user"),
    "--model",
    vllm_model,
    "--model-provider",
    vllm_provider,
    "--app-server-command-file",
    str(command_file),
]

lines = [
    "nodes:",
    "  - id: transcript_replay",
    "    path: python",
    "    args: " + yaml_args([
        "../../nodes/asr/transcript_replay/main.py",
        "--dora",
        "--session-id",
        session_id,
        "--user-turn-id",
        user_turn_id,
        "--stream-id",
        "asr/main",
        "--text-file",
        str(transcript_text_file),
        "--start-sample-index",
        "0",
        "--end-sample-index",
        "16000",
    ]),
    "    outputs:",
    "      - transcript",
    "",
    "  - id: dialogue_engine",
    "    path: python",
    "    args: " + yaml_args([
        "../../nodes/dialogue_engine/main.py",
        "--dora",
        "--session-id",
        session_id,
        "--transcript-stream-id",
        "asr/main",
        "--output-drain-seconds",
        "0.5",
    ]),
    "    inputs:",
    "      transcript:",
    "        source: transcript_replay/transcript",
    "        queue_size: 16",
    "        queue_policy: backpressure",
    "      agent_event:",
    "        source: codex_app_server/agent_event",
    "        queue_size: 16",
    "        queue_policy: backpressure",
    "      playback_done:",
    "        source: playback_queue/playback_done",
    "        queue_size: 16",
    "        queue_policy: backpressure",
    "    outputs:",
    "      - agent_turn",
    "      - agent_cancel",
    "      - session",
    "      - dialogue",
    "      - tts_text",
    "",
    "  - id: codex_app_server",
    "    path: python",
    "    args: " + yaml_args(codex_args),
    "    inputs:",
    "      agent_turn:",
    "        source: dialogue_engine/agent_turn",
    "        queue_size: 16",
    "        queue_policy: backpressure",
    "      agent_cancel:",
    "        source: dialogue_engine/agent_cancel",
    "        queue_size: 16",
    "        queue_policy: backpressure",
    "    outputs:",
    "      - agent_event",
    "      - agent_text",
    "      - agent_done",
    "      - agent_approval",
    "      - agent_tool",
    "",
    "  - id: agent_output_probe",
    "    path: python",
    "    args: " + yaml_args([
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
        "0",
        "--expected-tool-events",
        "0",
        "--expected-done-status",
        "completed",
        "--expected-text-contains",
        expected_text,
    ]),
    "    inputs:",
    "      agent_text:",
    "        source: codex_app_server/agent_text",
    "        queue_size: 32",
    "        queue_policy: backpressure",
    "      agent_done:",
    "        source: codex_app_server/agent_done",
    "        queue_size: 16",
    "        queue_policy: backpressure",
    "      agent_approval:",
    "        source: codex_app_server/agent_approval",
    "        queue_size: 16",
    "        queue_policy: backpressure",
    "      agent_tool:",
    "        source: codex_app_server/agent_tool",
    "        queue_size: 16",
    "        queue_policy: backpressure",
    "",
    "  - id: tts_text_probe",
    "    path: python",
    "    args: " + yaml_args([
        "../../tests/fixtures/dora/tts_text_probe.py",
        "--dora",
        "--session-id",
        session_id,
        "--user-turn-id",
        user_turn_id,
        "--assistant-turn-id",
        assistant_turn_id,
        "--expected-min-chunks",
        "1",
        "--expected-text-contains",
        expected_text,
        "--forbidden-text-contains",
        "<think>",
        "--forbidden-text-contains",
        "</think>",
    ]),
    "    inputs:",
    "      tts_text:",
    "        source: dialogue_engine/tts_text",
    "        queue_size: 16",
    "        queue_policy: backpressure",
    "",
    "  - id: tts_backend",
    "    path: python",
    "    args: " + yaml_args([
        "../../nodes/tts/tts_backend/main.py",
        "--dora",
        "--endpoint-url",
        f"http://127.0.0.1:{tts_port}/synthesize",
        "--timeout-seconds",
        "30",
        "--output-drain-seconds",
        "2.0",
    ]),
    "    inputs:",
    "      tts_text:",
    "        source: dialogue_engine/tts_text",
    "        queue_size: 16",
    "        queue_policy: backpressure",
    "    outputs:",
    "      - synth_audio",
    "",
    "  - id: synth_audio_probe",
    "    path: python",
    "    args: " + yaml_args([
        "../../nodes/tts/synth_audio_probe.py",
        "--dora",
        "--request-id",
        "tts-000000",
        "--session-id",
        session_id,
        "--user-turn-id",
        user_turn_id,
        "--assistant-turn-id",
        assistant_turn_id,
        "--audio-source-id",
        "tts_pyopenjtalk",
        "--audio-stream-id",
        "tts/pyopenjtalk",
        "--expected-min-chunks",
        "1",
        "--expected-min-frames",
        "1",
        "--expected-sample-format",
        "f32le",
        "--expected-channels",
        "1",
    ]),
    "    inputs:",
    "      synth_audio:",
    "        source: tts_backend/synth_audio",
    "        queue_size: 64",
    "        queue_policy: backpressure",
    "",
    "  - id: playback_queue",
    "    path: python",
    "    args: " + yaml_args([
        "../../nodes/playback/playback_queue/main.py",
        "--dora",
        "--output-source-id",
        "playback_queue",
        "--output-stream-id",
        "speaker/main",
        "--output-drain-seconds",
        "0.5",
    ]),
    "    inputs:",
    "      synth_audio:",
    "        source: tts_backend/synth_audio",
    "        queue_size: 64",
    "        queue_policy: backpressure",
    "    outputs:",
    "      - audio",
    "      - playback_state",
    "      - playback_done",
]
output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(output_path)
PY

if [[ "${MODE}" == "--write-dataflow" ]]; then
  exit 0
fi

python - "${VLLM_BASE_URL}" <<'PY'
from __future__ import annotations

import http.client
import os
import sys
import urllib.parse

url = urllib.parse.urlparse(sys.argv[1])
connection = http.client.HTTPConnection(url.hostname or "127.0.0.1", url.port or 80, timeout=2.0)
try:
    path = (url.path.rstrip("/") or "") + "/models"
    connection.request("GET", path, headers={"Authorization": f"Bearer {os.environ['VLLM_API_KEY']}"})
    response = connection.getresponse()
    body = response.read()
    if response.status != 200:
        raise SystemExit(f"local vLLM /models returned HTTP {response.status}: {body[:200]!r}")
finally:
    connection.close()
PY

OPENJTALK_DICT_DIR="$(
  uv run --extra dev --extra dora --extra tts python - <<'PY'
from pathlib import Path

import pyopenjtalk

dict_dir = pyopenjtalk.OPEN_JTALK_DICT_DIR
if isinstance(dict_dir, bytes):
    dict_dir = dict_dir.decode("utf-8")
print(Path(dict_dir))
PY
)"

uv run --extra dev --extra dora --extra tts python nodes/tts/tts_pyopenjtalk_server/main.py \
  --port "${TTS_PYOPENJTALK_PORT}" \
  --openjtalk-dict-dir "${OPENJTALK_DICT_DIR}" \
  --audio-source-id tts_pyopenjtalk \
  --audio-stream-id tts/pyopenjtalk \
  --chunk-frames 12000 &
TTS_SERVER_PID="$!"

python - "${TTS_PYOPENJTALK_PORT}" <<'PY'
from __future__ import annotations

import http.client
import sys
import time


def wait_for_port(port: int) -> None:
    deadline = time.monotonic() + 10.0
    last_error = ""
    while time.monotonic() < deadline:
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=0.2)
        try:
            connection.request("GET", "/health")
            response = connection.getresponse()
            response.read()
            if response.status == 200:
                return
            last_error = f"HTTP {response.status}"
        except OSError as exc:
            last_error = str(exc)
        finally:
            connection.close()
            time.sleep(0.05)
    raise SystemExit(f"PyOpenJTalk server on port {port} did not become ready: {last_error}")


wait_for_port(int(sys.argv[1]))
PY

uvx --from dora-rs-cli dora run "${LIVE_DATAFLOW}" --uv
