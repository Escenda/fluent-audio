#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MODE="${1:---run}"

if [[ "${MODE}" != "--run" && "${MODE}" != "--write-dataflow" ]]; then
  echo "usage: $0 [--run|--write-dataflow]" >&2
  exit 64
fi

if ! command -v codex >/dev/null; then
  echo "missing required command: codex" >&2
  exit 127
fi

if [[ "${MODE}" == "--run" && "${FLUENT_AUDIO_ALLOW_LIVE_CODEX_TURN:-}" != "1" ]]; then
  echo "live Codex turn not run: set FLUENT_AUDIO_ALLOW_LIVE_CODEX_TURN=1" >&2
  exit 64
fi

cd "${REPO_ROOT}"
export PYTHONPATH="${REPO_ROOT}/src:${REPO_ROOT}/contracts/python/src${PYTHONPATH:+:${PYTHONPATH}}"

mkdir -p artifacts/file_live_voice_session graphs/out

CODEX_HOME_DIR="${FLUENT_AUDIO_CODEX_HOME:-${REPO_ROOT}/artifacts/codex_home/file_live_voice_session}"
mkdir -p "${CODEX_HOME_DIR}"
export CODEX_HOME="${CODEX_HOME_DIR}"

RUNTIME_LOG="${FLUENT_AUDIO_FILE_LIVE_RUNTIME_LOG:-artifacts/file_live_voice_session/runtime.log}"
RUNTIME_LOG_RESOLVED="$(
  python -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "${RUNTIME_LOG}"
)"
if [[ "${MODE}" != "--write-dataflow" ]]; then
  : > "${RUNTIME_LOG_RESOLVED}"
  exec > >(tee -a "${RUNTIME_LOG_RESOLVED}") 2>&1
  echo "runtime log: ${RUNTIME_LOG_RESOLVED}"
fi

NEMOTRON_VENV_WRAPPER="graphs/out/nemotron_venv_python.sh"
if [[ ! -f "${NEMOTRON_VENV_WRAPPER}" ]]; then
  echo "missing ${NEMOTRON_VENV_WRAPPER}; build the fluent_audio nemotron_streaming_asr venv first" >&2
  exit 66
fi

NEMOTRON_MODEL_PATH="${FLUENT_AUDIO_NEMOTRON_MODEL_PATH:-../daihen-physical-ai.audio/data/models/fluent_audio/nemotron-3.5-asr-streaming-0.6b/nemotron-3.5-asr-streaming-0.6b.nemo}"
if [[ ! -s "${NEMOTRON_MODEL_PATH}" ]]; then
  echo "missing Nemotron model: ${NEMOTRON_MODEL_PATH}" >&2
  exit 66
fi

INPUT_WAV_PATH="$(
python - <<'PY'
from pathlib import Path
import os
import wave

repo_root = Path.cwd()
raw_path = repo_root / "tests/fixtures/vad/harvard_16k_mono_32768f.s16le"
turn_count_text = os.environ.get("FLUENT_AUDIO_FILE_LIVE_TURN_COUNT", "1")
inter_turn_silence_frames_text = os.environ.get(
    "FLUENT_AUDIO_FILE_LIVE_INTER_TURN_SILENCE_FRAMES",
    "20000",
)
tail_silence_frames_text = os.environ.get(
    "FLUENT_AUDIO_FILE_LIVE_TAIL_SILENCE_FRAMES",
    "20000",
)
try:
    turn_count = int(turn_count_text)
    inter_turn_silence_frames = int(inter_turn_silence_frames_text)
    tail_silence_frames = int(tail_silence_frames_text)
except ValueError as exc:
    raise SystemExit("file live turn/silence counts must be integers") from exc
if turn_count < 1:
    raise SystemExit("FLUENT_AUDIO_FILE_LIVE_TURN_COUNT must be positive")
if inter_turn_silence_frames < 0 or tail_silence_frames < 0:
    raise SystemExit("file live silence frame counts must be non-negative")

wav_name = (
    "harvard_16k_mono_32768f.wav"
    if turn_count == 1
    else f"harvard_16k_mono_32768f_{turn_count}turn.wav"
)
wav_path = repo_root / "artifacts/file_live_voice_session" / wav_name
payload = raw_path.read_bytes()
if not payload:
    raise SystemExit("fixture raw PCM is empty")
silence_between = b"\0\0" * inter_turn_silence_frames
silence_tail = b"\0\0" * tail_silence_frames
payload_parts: list[bytes] = []
for index in range(turn_count):
    if index > 0:
        payload_parts.append(silence_between)
    payload_parts.append(payload)
if turn_count > 1:
    payload_parts.append(silence_tail)
output_payload = b"".join(payload_parts)
with wave.open(str(wav_path), "wb") as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(16000)
    wav_file.writeframes(output_payload)
print(wav_path)
PY
)"
echo "${INPUT_WAV_PATH}"

DATAFLOW_PATH="${FLUENT_AUDIO_FILE_LIVE_DATAFLOW:-graphs/out/file_live_voice_session.local.yml}"
SESSION_ID="${FLUENT_AUDIO_FILE_LIVE_SESSION_ID:-file-live-voice-session}"
USER_TURN_ID="${FLUENT_AUDIO_FILE_LIVE_USER_TURN_ID:-user-turn-000001}"
ASSISTANT_TURN_ID="${FLUENT_AUDIO_FILE_LIVE_ASSISTANT_TURN_ID:-assistant-turn-000000}"
WEB_BRIDGE_PORT="${DORA_WEB_BRIDGE_PORT:-18098}"
CODEX_CONTROL_PORT="${CODEX_CONTROL_PORT:-18198}"
TTS_PYOPENJTALK_PORT="${TTS_PYOPENJTALK_PORT:-18097}"
VLLM_BASE_URL="${FLUENT_AUDIO_VLLM_BASE_URL:-http://127.0.0.1:18080/v1}"
VLLM_MODEL="${FLUENT_AUDIO_CODEX_MODEL:-qwen3-coder-30b-a3b-nvfp4}"
VLLM_PROVIDER="${FLUENT_AUDIO_CODEX_MODEL_PROVIDER:-vllm_local}"
export VLLM_API_KEY="${VLLM_API_KEY:-dummy}"

NEMOTRON_MODEL_RESOLVED="$(python -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "${NEMOTRON_MODEL_PATH}")"
INPUT_WAV_PATH_RESOLVED="$(python -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "${INPUT_WAV_PATH}")"
FILE_LIVE_TURN_COUNT="${FLUENT_AUDIO_FILE_LIVE_TURN_COUNT:-1}"

python - "${DATAFLOW_PATH}" "${SESSION_ID}" "${USER_TURN_ID}" "${ASSISTANT_TURN_ID}" "${WEB_BRIDGE_PORT}" "${CODEX_CONTROL_PORT}" "${TTS_PYOPENJTALK_PORT}" "${VLLM_BASE_URL}" "${VLLM_MODEL}" "${VLLM_PROVIDER}" "${NEMOTRON_MODEL_RESOLVED}" "${INPUT_WAV_PATH_RESOLVED}" "${FILE_LIVE_TURN_COUNT}" "${RUNTIME_LOG_RESOLVED}" <<'PY'
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


def write_payload(output_path: Path, name: str, value: str) -> Path:
    payload_dir = output_path.parent / f"{output_path.stem}.payloads"
    payload_dir.mkdir(parents=True, exist_ok=True)
    payload_path = payload_dir / name
    payload_path.write_text(value, encoding="utf-8")
    return payload_path.resolve()


def positive_int_env(name: str, default: str) -> str:
    text = os.environ.get(name, default)
    try:
        value = int(text)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return text


def remove_node_blocks(lines: list[str], node_ids: set[str]) -> list[str]:
    filtered: list[str] = []
    skipping = False
    for line in lines:
        if line.startswith("  - id: "):
            node_id = line.removeprefix("  - id: ")
            skipping = node_id in node_ids
        if not skipping:
            filtered.append(line)
    return filtered


def output_device_args() -> list[str]:
    use_default = os.environ.get("FLUENT_AUDIO_USE_DEFAULT_OUTPUT_DEVICE") == "1"
    device_name = os.environ.get("FLUENT_AUDIO_CPAL_OUTPUT_DEVICE_NAME")
    device_id = _device_id_or_default(
        env_name="FLUENT_AUDIO_CPAL_OUTPUT_DEVICE_ID",
        default_value="alsa:hw:CARD=S3,DEV=0",
        device_name=device_name,
        use_default=use_default,
    )
    return _single_device_selector(
        device_id=device_id,
        device_name=device_name,
        use_default=use_default,
        default_flag="--default-output-device",
    )


def _device_id_or_default(
    *,
    env_name: str,
    default_value: str,
    device_name: str | None,
    use_default: bool,
) -> str | None:
    if use_default or device_name:
        return os.environ.get(env_name) or None
    return os.environ.get(env_name) or default_value


def _single_device_selector(
    *,
    device_id: str | None,
    device_name: str | None,
    use_default: bool,
    default_flag: str,
) -> list[str]:
    selected = int(bool(device_id)) + int(bool(device_name)) + int(use_default)
    if selected != 1:
        raise ValueError("select exactly one CPAL output device selector")
    if use_default:
        return [default_flag]
    if device_name:
        return ["--device-name", device_name]
    if device_id:
        return ["--device-id", device_id]
    raise ValueError("unreachable CPAL selector state")


output_path = Path(sys.argv[1])
session_id = sys.argv[2]
user_turn_id = sys.argv[3]
assistant_turn_id = sys.argv[4]
web_port = sys.argv[5]
codex_control_port = sys.argv[6]
tts_port = sys.argv[7]
vllm_base_url = sys.argv[8]
vllm_model = sys.argv[9]
vllm_provider = sys.argv[10]
nemotron_model_path = sys.argv[11]
input_wav_path = sys.argv[12]
try:
    file_live_turn_count = int(sys.argv[13])
except ValueError as exc:
    raise SystemExit("file live turn count must be an integer") from exc
if file_live_turn_count < 1:
    raise SystemExit("file live turn count must be positive")
runtime_log_path = sys.argv[14]
asr_audio_queue_size = positive_int_env("FLUENT_AUDIO_ASR_AUDIO_QUEUE_SIZE", "4096")

cwd = os.environ.get("FLUENT_AUDIO_CODEX_CWD", "/tmp/fluent-audio-codex-empty-cwd")
Path(cwd).mkdir(parents=True, exist_ok=True)

developer_instructions = os.environ.get(
    "FLUENT_AUDIO_VOICE_DEVELOPER_INSTRUCTIONS",
    (
        "あなたは音声対話でユーザーに聞こえる返答本文だけを書きます。"
        "返答本文はTTSで即座に読み上げられるため、自然な短い日本語にしてください。"
        "原則として一文か二文で、最初の文で直接答えてください。"
        "最初の文は短くし、必ず句点「。」または疑問符「？」で閉じてください。"
        "最初の文がそのまま先に読み上げられる前提で、前置きや能力紹介を書かないでください。"
        "Markdown、箇条書き、コードブロック、ファイルパス、コマンド例、長い列挙、内部タグ、思考タグ、未加工のツール出力は禁止です。"
        "ファイル作成、ファイル編集、Python、JavaScript、コード、コマンド、ツールの機能一覧は読み上げ本文に出してはいけません。"
        "詳細や一覧が必要な場合は、読み上げ本文では「詳細は画面に出します。」のように短く述べるだけにしてください。"
        "能力紹介、機能一覧、ファイル作成・編集・コード生成などの例示を、ユーザーが明示的に求めていない限り話さないでください。"
        "ユーザーが何ができるか、どんなツールを使えるかを聞いても、CLI、Codex、ファイル操作、コード編集の機能一覧を読み上げないでください。"
        "その場合は、必要に応じて確認や作業を進められることだけを短く伝え、具体的な希望を一つ尋ねてください。"
        "ツール実行や詳しい調査が必要なときも、読み上げ本文では短く状況だけ伝え、詳細は画面やログに出す前提で進めてください。"
        "質問が曖昧な場合は、短い確認質問を一つだけ返してください。"
    ),
)
developer_instructions_file = write_payload(
    output_path,
    "voice_developer_instructions.txt",
    developer_instructions,
)

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
            f"model_providers.{vllm_provider}.wire_api=\"responses\"",
        ]
    )
    + "\n",
)

codex_args = [
    "./nemotron_venv_python.sh",
    "../../nodes/dialogue_engine/codex_app_server/main.py",
    "--dora",
    "--timeout-seconds",
    os.environ.get("FLUENT_AUDIO_CODEX_TIMEOUT_SECONDS", "240"),
    "--approval-response-timeout-seconds",
    os.environ.get("FLUENT_AUDIO_CODEX_APPROVAL_TIMEOUT_SECONDS", "30"),
    "--cwd",
    cwd,
    "--sandbox",
    os.environ.get("FLUENT_AUDIO_CODEX_SANDBOX", "read-only"),
    "--approval-policy",
    os.environ.get("FLUENT_AUDIO_CODEX_APPROVAL_POLICY", "never"),
    "--approvals-reviewer",
    os.environ.get("FLUENT_AUDIO_CODEX_APPROVALS_REVIEWER", "user"),
    "--model",
    vllm_model,
    "--model-provider",
    vllm_provider,
    "--developer-instructions-file",
    str(developer_instructions_file),
    "--app-server-command-file",
    str(command_file),
    "--control-host",
    "127.0.0.1",
    "--control-port",
    codex_control_port,
]

lines: list[str] = [
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
            input_wav_path,
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
            os.environ.get("FLUENT_AUDIO_FILE_REPLAY_SPEED", "1.0"),
        ]
    ),
    "    outputs:",
    "      - audio",
    "",
    "  - id: media_graph_asr",
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
            os.environ.get("FLUENT_AUDIO_VAD_THRESHOLD", "0.5"),
            "--level-period-windows",
            os.environ.get("FLUENT_AUDIO_VAD_LEVEL_PERIOD_WINDOWS", "8"),
        ]
    ),
    "    inputs:",
    "      audio:",
    "        source: media_graph_asr/audio",
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
            os.environ.get("FLUENT_AUDIO_TURN_END_SILENCE_FRAMES", "12000"),
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
            os.environ.get("FLUENT_AUDIO_ASR_PREBUFFER_FRAMES", "16000"),
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
            os.environ.get("FLUENT_AUDIO_NEMOTRON_PREBUFFER_FRAMES", "32768"),
            "--control-holdback-frames",
            os.environ.get("FLUENT_AUDIO_NEMOTRON_CONTROL_HOLDBACK_FRAMES", "4096"),
            "--late-stop-tolerance-frames",
            os.environ.get("FLUENT_AUDIO_NEMOTRON_LATE_STOP_TOLERANCE_FRAMES", "16000"),
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
            nemotron_model_path,
            "--target-lang",
            os.environ.get("FLUENT_AUDIO_ASR_TARGET_LANG", "en-US"),
            "--att-context-right-frames",
            os.environ.get("FLUENT_AUDIO_NEMOTRON_ATT_CONTEXT_RIGHT_FRAMES", "3"),
        ]
    ),
    "    inputs:",
    "      audio:",
    "        source: media_graph_asr/audio",
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
            "--expected-min-deltas",
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
            "--forbidden-text-contains",
            "<think>",
            "--forbidden-text-contains",
            "</think>",
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
            "2.0",
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
    "  - id: synth_audio_probe",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            "./nemotron_venv_python.sh",
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
        ]
    ),
    "    inputs:",
    "      synth_audio:",
    "        source: tts_backend/synth_audio",
    "        queue_size: 64",
    "        queue_policy: backpressure",
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
    "  - id: speaker_stream_adapter",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            "./nemotron_venv_python.sh",
            "../../nodes/playback/speaker_stream_adapter/main.py",
            "--dora",
            "--input-source-id",
            "playback_queue",
            "--input-stream-id",
            "speaker/main",
            "--output-source-id",
            "speaker_stream",
            "--output-stream-id",
            "speaker/continuous",
            "--output-drain-seconds",
            "0.5",
        ]
    ),
    "    inputs:",
    "      audio:",
    "        source: playback_queue/audio",
    "        queue_size: 64",
    "        queue_policy: backpressure",
    "    outputs:",
    "      - audio",
    "",
    "  - id: media_graph_speaker",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            "./nemotron_venv_python.sh",
            "../../nodes/media_graph/main.py",
            "--dora",
            "--input-source-id",
            "speaker_stream",
            "--input-stream-id",
            "speaker/continuous",
            "--input-sample-rate-hz",
            "48000",
            "--input-channels",
            "1",
            "--input-sample-format",
            "f32le",
            "--input-channel-layout",
            "interleaved",
            "--output-source-id",
            "speaker_media_graph",
            "--output-stream-id",
            "speaker/cpal",
            "--output-sample-rate-hz",
            "48000",
            "--output-channels",
            "2",
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
    "        source: speaker_stream_adapter/audio",
    "        queue_size: 64",
    "        queue_policy: backpressure",
    "    outputs:",
    "      - audio",
    "",
    "  - id: cpal_sink",
    "    build: ../../scripts/dora_cargo_build.sh ../../nodes/audio_device/cpal_sink/Cargo.toml",
    "    path: ../../nodes/audio_device/cpal_sink/target/debug/cpal_sink",
    "    args: "
    + yaml_args(
        [
            *output_device_args(),
            "--sample-rate-hz",
            "48000",
            "--channels",
            "2",
            "--sample-format",
            "s16le",
            "--channel-layout",
            "interleaved",
            "--buffer-size-frames",
            os.environ.get("FLUENT_AUDIO_OUTPUT_BUFFER_SIZE_FRAMES", "480"),
            "--queue-capacity-chunks",
            os.environ.get("FLUENT_AUDIO_OUTPUT_QUEUE_CAPACITY_CHUNKS", "128"),
            "--startup-buffer-chunks",
            os.environ.get("FLUENT_AUDIO_OUTPUT_STARTUP_BUFFER_CHUNKS", "64"),
            "--source-id",
            "speaker_media_graph",
            "--stream-id",
            "speaker/cpal",
            "--completion-timeout-ms",
            os.environ.get("FLUENT_AUDIO_OUTPUT_COMPLETION_TIMEOUT_MS", "30000"),
        ]
    ),
    "    inputs:",
    "      audio:",
    "        source: media_graph_speaker/audio",
    "        queue_size: 128",
    "        queue_policy: backpressure",
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
            "--codex-control-url",
            f"http://127.0.0.1:{codex_control_port}",
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
            "--runtime-log",
            runtime_log_path,
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
    "        queue_size: 32",
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

if file_live_turn_count > 1:
    lines = remove_node_blocks(
        lines,
        {
            "transcript_probe",
            "agent_output_probe",
            "tts_text_probe",
            "synth_audio_probe",
        },
    )

output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(output_path)
PY

if [[ "${MODE}" == "--write-dataflow" ]]; then
  exit 0
fi

scripts/dora_cargo_build.sh nodes/audio_device/cpal_sink/Cargo.toml

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

TTS_SERVER_PID=""
cleanup() {
  if [[ -n "${TTS_SERVER_PID}" ]] && kill -0 "${TTS_SERVER_PID}" 2>/dev/null; then
    kill "${TTS_SERVER_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT

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
    deadline = time.monotonic() + 15.0
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

echo "web dashboard: http://127.0.0.1:${WEB_BRIDGE_PORT}/?session=${SESSION_ID}" >&2
uvx --from dora-rs-cli dora run "${DATAFLOW_PATH}" --uv

if [[ "${FILE_LIVE_TURN_COUNT}" != "1" ]]; then
  python - "${WEB_BRIDGE_PORT}" "${FILE_LIVE_TURN_COUNT}" <<'PY'
from __future__ import annotations

import http.client
import json
import sys

port = int(sys.argv[1])
expected_turns = int(sys.argv[2])
path = "/api/events.json?tail=500"
connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5.0)
try:
    connection.request("GET", path)
    response = connection.getresponse()
    body = response.read()
    if response.status != 200:
        raise SystemExit(f"dora web bridge event query returned HTTP {response.status}: {body[:200]!r}")
finally:
    connection.close()

snapshot = json.loads(body.decode("utf-8"))
events = [item["event"] for item in snapshot["events"]]
transcript_turns = {
    event["user_turn_id"]
    for event in events
    if event["event_type"] == "transcript_final"
}
agent_done = [
    event
    for event in events
    if event["event_type"] == "agent_turn_done"
]
tts_chunks = [
    event
    for event in events
    if event["event_type"] == "tts_text"
]
playback_done = [
    event
    for event in events
    if event["event_type"] == "playback_done"
]
failed_agent_done = [
    event
    for event in agent_done
    if event["status"] != "completed"
]
failed_playback = [
    event
    for event in playback_done
    if event["status"] != "completed"
]
error_events = [
    event
    for event in events
    if (
        event["event_type"] == "session_state"
        and event["event"] == "error"
    )
    or (
        event["event_type"] == "dialogue_event"
        and event["event"] == "error"
    )
]
if len(transcript_turns) < expected_turns:
    raise SystemExit(
        "file live session transcript turn count below expectation: "
        f"expected at least {expected_turns}, got {len(transcript_turns)}"
    )
if len(agent_done) < expected_turns:
    raise SystemExit(
        "file live session agent done count below expectation: "
        f"expected at least {expected_turns}, got {len(agent_done)}"
    )
if len(tts_chunks) < expected_turns:
    raise SystemExit(
        "file live session TTS text chunk count below expectation: "
        f"expected at least {expected_turns}, got {len(tts_chunks)}"
    )
if len(playback_done) < expected_turns:
    raise SystemExit(
        "file live session playback done count below expectation: "
        f"expected at least {expected_turns}, got {len(playback_done)}"
    )
if failed_agent_done:
    raise SystemExit(f"file live session contains failed agent turns: {failed_agent_done!r}")
if failed_playback:
    raise SystemExit(f"file live session contains failed playback: {failed_playback!r}")
if error_events:
    raise SystemExit(f"file live session contains error events: {error_events!r}")

print(
    json.dumps(
        {
            "session_id": session_id,
            "event_count": snapshot["event_count"],
            "transcript_turns": sorted(transcript_turns),
            "agent_done": len(agent_done),
            "tts_chunks": len(tts_chunks),
            "playback_done": len(playback_done),
        },
        ensure_ascii=False,
    )
)
PY
fi
