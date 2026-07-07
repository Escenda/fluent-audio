#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MODE="${1:---run}"

if [[ "${MODE}" != "--run" && "${MODE}" != "--write-dataflow" ]]; then
  echo "usage: $0 [--run|--write-dataflow]" >&2
  exit 64
fi

TTS_FIXTURE_PORT="${TTS_FIXTURE_PORT:-18092}"
DORA_WEB_BRIDGE_PORT="${DORA_WEB_BRIDGE_PORT:-18093}"
SESSION_ID="${FLUENT_DIALOGUE_DORA_FILE_SESSION_ID:-file-realtime-session}"
USER_TURN_ID="${FLUENT_DIALOGUE_DORA_FILE_USER_TURN_ID:-user-turn-000001}"
ASSISTANT_TURN_ID="${FLUENT_DIALOGUE_DORA_FILE_ASSISTANT_TURN_ID:-assistant-turn-000000}"
AGENT_TEXT="${FLUENT_DIALOGUE_DORA_FILE_AGENT_TEXT:-file-realtime-agent-ok.}"
NEMOTRON_MODEL_PATH="${FLUENT_DIALOGUE_DORA_NEMOTRON_MODEL_PATH:-data/models/fluent_dialogue_dora/nemotron-3.5-asr-streaming-0.6b/nemotron-3.5-asr-streaming-0.6b.nemo}"

cd "${REPO_ROOT}"
export PYTHONPATH="${REPO_ROOT}/src:${REPO_ROOT}/contracts/python/src${PYTHONPATH:+:${PYTHONPATH}}"

NEMOTRON_VENV_WRAPPER="graphs/out/nemotron_venv_python.sh"
if [[ ! -f "${NEMOTRON_VENV_WRAPPER}" ]]; then
  echo "missing ${NEMOTRON_VENV_WRAPPER}; build the fluent_dialogue_dora nemotron_streaming_asr venv first" >&2
  exit 66
fi
if [[ ! -s "${NEMOTRON_MODEL_PATH}" ]]; then
  echo "missing Nemotron model: ${NEMOTRON_MODEL_PATH}" >&2
  exit 66
fi

mkdir -p artifacts/file_realtime_session graphs/out

python - <<'PY'
from pathlib import Path
import wave

repo_root = Path.cwd()
raw_path = repo_root / "tests/fixtures/vad/harvard_16k_mono_32768f.s16le"
wav_path = repo_root / "artifacts/file_realtime_session/harvard_16k_mono_32768f.wav"
payload = raw_path.read_bytes()
if not payload:
    raise SystemExit("fixture raw PCM is empty")
with wave.open(str(wav_path), "wb") as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(16000)
    wav_file.writeframes(payload)
print(wav_path)
PY

NEMOTRON_MODEL_RESOLVED="$(python -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "${NEMOTRON_MODEL_PATH}")"
DATAFLOW_PATH="graphs/out/file_realtime_session_smoke.local.yml"
COMMAND_FILE="artifacts/file_realtime_session/codex_app_server.command"

python - "${DATAFLOW_PATH}" "${COMMAND_FILE}" "${SESSION_ID}" "${USER_TURN_ID}" "${ASSISTANT_TURN_ID}" "${AGENT_TEXT}" "${TTS_FIXTURE_PORT}" "${DORA_WEB_BRIDGE_PORT}" "${NEMOTRON_MODEL_RESOLVED}" <<'PY'
from __future__ import annotations

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


def positive_int_env(name: str, default: str) -> str:
    text = os.environ.get(name, default)
    try:
        value = int(text)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return text


dataflow_path = Path(sys.argv[1])
command_file = Path(sys.argv[2])
session_id = sys.argv[3]
user_turn_id = sys.argv[4]
assistant_turn_id = sys.argv[5]
agent_text = sys.argv[6]
tts_port = sys.argv[7]
web_port = sys.argv[8]
model_path = sys.argv[9]
asr_audio_queue_size = positive_int_env("FLUENT_DIALOGUE_DORA_ASR_AUDIO_QUEUE_SIZE", "4096")

command_file.write_text(
    "\n".join(
        [
            "python",
            "../../tests/fixtures/jsonrpc/codex_app_server_jsonrpc_fixture.py",
            "--text",
            agent_text,
            "--expected-turns",
            "1",
        ]
    )
    + "\n",
    encoding="utf-8",
)

nodes: list[str] = [
    "nodes:",
    "  - id: wav_pcm_source",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            "./nemotron_venv_python.sh",
            "../../nodes/audio_device/wav_pcm_source/main.py",
            "--dora",
            "--input",
            "../../artifacts/file_realtime_session/harvard_16k_mono_32768f.wav",
            "--chunk-frames",
            "512",
            "--source-id",
            "wav_fixture",
            "--stream-id",
            "audio/file/harvard",
            "--start-seq",
            "0",
            "--start-sample-index",
            "0",
            "--start-capture-time-ns",
            "0",
            "--expected-sample-rate-hz",
            "16000",
            "--expected-channels",
            "1",
            "--replay-speed",
            "1.0",
        ]
    ),
    "    outputs:",
    "      - audio",
    "",
    "  - id: media_graph",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            "./nemotron_venv_python.sh",
            "../../nodes/media_graph/main.py",
            "--dora",
            "--input-source-id",
            "wav_fixture",
            "--input-stream-id",
            "audio/file/harvard",
            "--input-sample-rate-hz",
            "16000",
            "--input-channels",
            "1",
            "--input-sample-format",
            "s16le",
            "--input-channel-layout",
            "interleaved",
            "--output-source-id",
            "media_graph",
            "--output-stream-id",
            "audio/media_graph/asr",
            "--output-sample-rate-hz",
            "16000",
            "--output-channels",
            "1",
            "--output-sample-format",
            "s16le",
            "--output-channel-layout",
            "interleaved",
            "--output-start-seq",
            "0",
            "--output-start-sample-index",
            "0",
            "--output-start-capture-time-ns",
            "0",
        ]
    ),
    "    inputs:",
    "      audio:",
    "        source: wav_pcm_source/audio",
    "        queue_size: 128",
    "        queue_policy: backpressure",
    "    outputs:",
    "      - audio",
    "",
    "  - id: vad",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            "./nemotron_venv_python.sh",
            "../../nodes/vad/silero/main.py",
            "--dora",
            "--input-source-id",
            "media_graph",
            "--input-stream-id",
            "audio/media_graph/asr",
            "--output-source-id",
            "silero_vad",
            "--output-stream-id",
            "activity/vad/asr",
            "--threshold",
            "0.5",
            "--level-period-windows",
            os.environ.get("FLUENT_DIALOGUE_DORA_VAD_LEVEL_PERIOD_WINDOWS", "8"),
        ]
    ),
    "    inputs:",
    "      audio:",
    "        source: media_graph/audio",
    "        queue_size: 128",
    "        queue_policy: backpressure",
    "    outputs:",
    "      - activity",
    "      - meter",
    "",
    "  - id: turn_detector",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            "./nemotron_venv_python.sh",
            "../../nodes/vad/turn_detector/main.py",
            "--dora",
            "--input-source-id",
            "silero_vad",
            "--input-stream-id",
            "activity/vad/asr",
            "--session-id",
            session_id,
            "--output-stream-id",
            f"turn/{session_id}",
            "--end-silence-frames",
            "12000",
        ]
    ),
    "    inputs:",
    "      activity:",
    "        source: vad/activity",
    "        queue_size: 128",
    "        queue_policy: backpressure",
    "    outputs:",
    "      - turn",
    "",
    "  - id: asr_control_from_turn",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            "./nemotron_venv_python.sh",
            "../../nodes/asr/asr_control_from_turn/main.py",
            "--dora",
            "--input-session-id",
            session_id,
            "--input-turn-stream-id",
            f"turn/{session_id}",
            "--output-audio-stream-id",
            "audio/media_graph/asr",
            "--asr-prebuffer-frames",
            "16000",
            "--output-drain-seconds",
            "5.0",
        ]
    ),
    "    inputs:",
    "      turn:",
    "        source: turn_detector/turn",
    "        queue_size: 128",
    "        queue_policy: backpressure",
    "    outputs:",
    "      - asr_control",
    "",
    "  - id: nemotron_streaming",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            "./nemotron_venv_python.sh",
            "../../nodes/asr/nemotron_streaming/main.py",
            "--dora",
            "--input-audio-source-id",
            "media_graph",
            "--input-audio-stream-id",
            "audio/media_graph/asr",
            "--session-id",
            session_id,
            "--output-stream-id",
            f"transcript/{session_id}",
            "--prebuffer-frames",
            "32768",
            "--control-holdback-frames",
            "4096",
            "--sample-rate-hz",
            "16000",
            "--channels",
            "1",
            "--sample-format",
            "s16le",
            "--channel-layout",
            "interleaved",
            "--backend",
            "nemo",
            "--model-name",
            model_path,
            "--target-lang",
            "en-US",
            "--att-context-right-frames",
            "3",
        ]
    ),
    "    inputs:",
    "      audio:",
    "        source: media_graph/audio",
    f"        queue_size: {asr_audio_queue_size}",
    "        queue_policy: backpressure",
    "      asr_control:",
    "        source: asr_control_from_turn/asr_control",
    "        queue_size: 32",
    "        queue_policy: backpressure",
    "    outputs:",
    "      - transcript",
    "",
    "  - id: transcript_probe",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            "./nemotron_venv_python.sh",
            "../../nodes/asr/nemotron_streaming/transcript_probe.py",
            "--dora",
            "--session-id",
            session_id,
            "--stream-id",
            f"transcript/{session_id}",
            "--expected-min-partials",
            "0",
            "--expected-finals",
            "1",
            "--expected-final-sample-index",
            "32768",
            "--expected-min-last-text-length",
            "1",
        ]
    ),
    "    inputs:",
    "      transcript:",
    "        source: nemotron_streaming/transcript",
    "        queue_size: 128",
    "        queue_policy: backpressure",
    "",
    "  - id: dialogue_engine",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            "./nemotron_venv_python.sh",
            "../../nodes/dialogue_engine/main.py",
            "--dora",
            "--session-id",
            session_id,
            "--transcript-stream-id",
            f"transcript/{session_id}",
            "--output-drain-seconds",
            "0.5",
        ]
    ),
    "    inputs:",
    "      transcript:",
    "        source: nemotron_streaming/transcript",
    "        queue_size: 128",
    "        queue_policy: backpressure",
    "      agent_event:",
    "        source: codex_app_server/agent_event",
    "        queue_size: 32",
    "        queue_policy: backpressure",
    "      playback_done:",
    "        source: playback_queue/playback_done",
    "        queue_size: 32",
    "        queue_policy: backpressure",
    "    outputs:",
    "      - agent_turn",
    "      - agent_cancel",
    "      - session",
    "      - dialogue",
    "      - tts_text",
    "",
    "  - id: codex_app_server",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            "./nemotron_venv_python.sh",
            "../../nodes/dialogue_engine/codex_app_server/main.py",
            "--dora",
            "--timeout-seconds",
            "30",
            "--approval-response-timeout-seconds",
            "10",
            "--app-server-command-file",
            f"../../{command_file.as_posix()}",
        ]
    ),
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
    "      - agent_user_input",
    "      - agent_mcp_elicitation",
    "      - agent_tool",
    "",
    "  - id: agent_output_probe",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            "./nemotron_venv_python.sh",
            "../../nodes/dialogue_engine/agent_output_probe.py",
            "--dora",
            "--session-id",
            session_id,
            "--user-turn-id",
            user_turn_id,
            "--agent-turn-id",
            assistant_turn_id,
            "--expected-min-text-deltas",
            "1",
            "--expected-approval-requests",
            "0",
            "--expected-tool-events",
            "0",
            "--expected-done-status",
            "completed",
            "--expected-text-contains",
            agent_text,
        ]
    ),
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
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            "./nemotron_venv_python.sh",
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
            agent_text,
        ]
    ),
    "    inputs:",
    "      tts_text:",
    "        source: dialogue_engine/tts_text",
    "        queue_size: 16",
    "        queue_policy: backpressure",
    "",
    "  - id: tts_backend",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            "./nemotron_venv_python.sh",
            "../../nodes/tts/tts_backend/main.py",
            "--dora",
            "--endpoint-url",
            f"http://127.0.0.1:{tts_port}/synthesize",
            "--timeout-seconds",
            "30",
            "--output-drain-seconds",
            "0.5",
        ]
    ),
    "    inputs:",
    "      tts_text:",
    "        source: dialogue_engine/tts_text",
    "        queue_size: 16",
    "        queue_policy: backpressure",
    "    outputs:",
    "      - synth_audio",
    "",
    "  - id: playback_queue",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            "./nemotron_venv_python.sh",
            "../../nodes/playback/playback_queue/main.py",
            "--dora",
            "--output-source-id",
            "playback_queue",
            "--output-stream-id",
            "speaker/main",
            "--output-drain-seconds",
            "0.5",
        ]
    ),
    "    inputs:",
    "      synth_audio:",
    "        source: tts_backend/synth_audio",
    "        queue_size: 64",
    "        queue_policy: backpressure",
    "    outputs:",
    "      - audio",
    "      - playback_state",
    "      - playback_done",
    "",
    "  - id: dora_web_bridge",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            "./nemotron_venv_python.sh",
            "../../bridges/dora_web_bridge/main.py",
            "--dora",
            "--session-id",
            session_id,
            "--port",
            web_port,
            "--input",
            "activity",
            "--input",
            "turn",
            "--input",
            "transcript",
            "--input",
            "meter",
            "--input",
            "asr_control",
            "--input",
            "session",
            "--input",
            "dialogue",
            "--input",
            "agent_text",
            "--input",
            "agent_done",
            "--input",
            "agent_approval",
            "--input",
            "agent_user_input",
            "--input",
            "agent_mcp_elicitation",
            "--input",
            "agent_tool",
            "--input",
            "tts",
            "--input",
            "playback_state",
            "--input",
            "playback_done",
        ]
    ),
    "    inputs:",
    "      activity:",
    "        source: vad/activity",
    "        queue_size: 128",
    "        queue_policy: backpressure",
    "      meter:",
    "        source: vad/meter",
    "        queue_size: 32",
    "        queue_policy: backpressure",
    "      turn:",
    "        source: turn_detector/turn",
    "        queue_size: 128",
    "        queue_policy: backpressure",
    "      asr_control:",
    "        source: asr_control_from_turn/asr_control",
    "        queue_size: 128",
    "        queue_policy: backpressure",
    "      transcript:",
    "        source: nemotron_streaming/transcript",
    "        queue_size: 128",
    "        queue_policy: backpressure",
    "      session:",
    "        source: dialogue_engine/session",
    "        queue_size: 32",
    "        queue_policy: backpressure",
    "      dialogue:",
    "        source: dialogue_engine/dialogue",
    "        queue_size: 32",
    "        queue_policy: backpressure",
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
    "      agent_user_input:",
    "        source: codex_app_server/agent_user_input",
    "        queue_size: 16",
    "        queue_policy: backpressure",
    "      agent_mcp_elicitation:",
    "        source: codex_app_server/agent_mcp_elicitation",
    "        queue_size: 16",
    "        queue_policy: backpressure",
    "      agent_tool:",
    "        source: codex_app_server/agent_tool",
    "        queue_size: 16",
    "        queue_policy: backpressure",
    "      tts:",
    "        source: dialogue_engine/tts_text",
    "        queue_size: 16",
    "        queue_policy: backpressure",
    "      playback_state:",
    "        source: playback_queue/playback_state",
    "        queue_size: 16",
    "        queue_policy: backpressure",
    "      playback_done:",
    "        source: playback_queue/playback_done",
    "        queue_size: 16",
    "        queue_policy: backpressure",
]

dataflow_path.write_text("\n".join(nodes) + "\n", encoding="utf-8")
print(dataflow_path)
PY

if [[ "${MODE}" == "--write-dataflow" ]]; then
  exit 0
fi

TTS_PID=""

cleanup() {
  if [[ -n "${TTS_PID}" ]] && kill -0 "${TTS_PID}" 2>/dev/null; then
    kill "${TTS_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT

uv run --extra dev --extra dora python tests/fixtures/http/tts_backend_fixture.py \
  --port "${TTS_FIXTURE_PORT}" \
  --audio-file tests/fixtures/cpal/silence_48k_stereo_250ms.s16le \
  --sample-rate-hz 48000 \
  --channels 2 \
  --sample-format s16le \
  --channel-layout interleaved \
  --audio-source-id tts_fixture \
  --audio-stream-id tts/fixture/file-realtime \
  --expected-requests 1 &
TTS_PID="$!"

python - "${TTS_FIXTURE_PORT}" <<'PY'
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
    raise SystemExit(f"server on port {port} did not become ready: {last_error}")


wait_for_port(int(sys.argv[1]))
PY

(
  cd graphs/out
  uvx --from dora-rs-cli dora run "$(basename "${DATAFLOW_PATH}")" --uv
)

wait "${TTS_PID}"
TTS_PID=""
