#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/live_session_lifecycle.sh"

usage() {
  echo "usage: $0 [--serve|--run|--write-dataflow|--status|--stop|--restart [--serve|--run]]" >&2
}

LIVE_SESSION_STATE_FILE="${REPO_ROOT}/artifacts/live_hardware_voice_session/run.env"
REQUESTED_MODE="${1:---serve}"
RESTART_REQUESTED=0

case "${REQUESTED_MODE}" in
  --serve | --run | --write-dataflow)
    if [[ $# -gt 1 ]]; then
      usage
      exit 64
    fi
    MODE="${REQUESTED_MODE}"
    ;;
  --status)
    if [[ $# -gt 1 ]]; then
      usage
      exit 64
    fi
    live_session_status
    exit 0
    ;;
  --stop)
    if [[ $# -gt 1 ]]; then
      usage
      exit 64
    fi
    live_session_stop
    exit $?
    ;;
  --restart)
    if [[ $# -gt 2 ]]; then
      usage
      exit 64
    fi
    MODE="${2:---serve}"
    if [[ "${MODE}" != "--serve" && "${MODE}" != "--run" ]]; then
      usage
      exit 64
    fi
    RESTART_REQUESTED=1
    ;;
  *)
    usage
    exit 64
    ;;
esac

if [[ "${RESTART_REQUESTED}" == "1" ]]; then
  live_session_stop
fi

cd "${REPO_ROOT}"
export PYTHONPATH="${REPO_ROOT}/src:${REPO_ROOT}/contracts/python/src${PYTHONPATH:+:${PYTHONPATH}}"
mkdir -p artifacts/live_hardware_voice_session graphs/out

CODEX_HOME_DIR="${FLUENT_DIALOGUE_DORA_CODEX_HOME:-${REPO_ROOT}/artifacts/codex_home/live_hardware_voice_session}"
mkdir -p "${CODEX_HOME_DIR}"
export CODEX_HOME="${CODEX_HOME_DIR}"

LIVE_DATAFLOW="${FLUENT_DIALOGUE_DORA_LIVE_HARDWARE_DATAFLOW:-graphs/out/live_hardware_voice_session.local.yml}"
SESSION_ID="${FLUENT_DIALOGUE_DORA_LIVE_HARDWARE_SESSION_ID:-live-hardware-session}"
WEB_BRIDGE_PORT="${DORA_WEB_BRIDGE_PORT:-18096}"
CODEX_CONTROL_PORT="${CODEX_CONTROL_PORT:-18196}"
TTS_PYOPENJTALK_PORT="${TTS_PYOPENJTALK_PORT:-18095}"
VLLM_BASE_URL="${FLUENT_DIALOGUE_DORA_VLLM_BASE_URL:-http://127.0.0.1:18080/v1}"
VLLM_MODEL="${FLUENT_DIALOGUE_DORA_CODEX_MODEL:-qwen3.6-27b-mtp-pi-tune-nvfp4}"
VLLM_PROVIDER="${FLUENT_DIALOGUE_DORA_CODEX_MODEL_PROVIDER:-vllm_local}"
VLLM_WIRE_API="${FLUENT_DIALOGUE_DORA_CODEX_WIRE_API:-responses}"
export VLLM_API_KEY="${VLLM_API_KEY:-dummy}"

LIVE_RUNTIME_LOG="${FLUENT_DIALOGUE_DORA_LIVE_RUNTIME_LOG:-artifacts/live_hardware_voice_session/runtime.log}"
mkdir -p "$(dirname "${LIVE_RUNTIME_LOG}")"
LIVE_RUNTIME_LOG_RESOLVED="$(
  python -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "${LIVE_RUNTIME_LOG}"
)"
LIVE_DATAFLOW_RESOLVED="$(
  python -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "${LIVE_DATAFLOW}"
)"
if [[ "${MODE}" != "--write-dataflow" ]]; then
  if live_session_start_guard; then
    :
  else
    guard_status=$?
    if [[ "${guard_status}" -eq 75 ]]; then
      exit 0
    fi
    exit "${guard_status}"
  fi
  : > "${LIVE_RUNTIME_LOG_RESOLVED}"
  exec > >(tee -a "${LIVE_RUNTIME_LOG_RESOLVED}") 2>&1
  echo "runtime log: ${LIVE_RUNTIME_LOG_RESOLVED}"
  LIVE_SESSION_NAME="live_hardware_voice_session"
  LIVE_SESSION_ID="${SESSION_ID}"
  LIVE_SESSION_MODE="${MODE}"
  LIVE_SESSION_DATAFLOW="${LIVE_DATAFLOW_RESOLVED}"
  LIVE_SESSION_RUNTIME_LOG="${LIVE_RUNTIME_LOG_RESOLVED}"
  LIVE_SESSION_WEB_BRIDGE_PORT="${WEB_BRIDGE_PORT}"
  LIVE_SESSION_CODEX_CONTROL_PORT="${CODEX_CONTROL_PORT}"
  LIVE_SESSION_TTS_PORT="${TTS_PYOPENJTALK_PORT}"
  LIVE_SESSION_VLLM_BASE_URL="${VLLM_BASE_URL}"
  LIVE_SESSION_DORA_PID=""
  LIVE_SESSION_DORA_PGID=""
  LIVE_SESSION_DORA_SID=""
  LIVE_SESSION_TTS_SERVER_PID=""
  LIVE_SESSION_TTS_SERVER_PGID=""
  LIVE_SESSION_TTS_SERVER_SID=""
  LIVE_SESSION_STATE_ACTIVE=1
  cleanup() {
    local status=$?
    trap - EXIT
    if [[ "${LIVE_SESSION_STATE_ACTIVE:-0}" == "1" ]]; then
      if live_session_stop_current; then
        live_session_clear_state
      else
        echo "live session processes remain; state retained: ${LIVE_SESSION_STATE_FILE}" >&2
      fi
    fi
    return "${status}"
  }
  trap cleanup EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM
  live_session_write_state
fi

if ! command -v codex >/dev/null; then
  echo "missing required command: codex" >&2
  exit 127
fi

if [[ "${MODE}" != "--write-dataflow" && "${FLUENT_DIALOGUE_DORA_ALLOW_LIVE_CODEX_TURN:-}" != "1" ]]; then
  echo "live Codex turn not run: set FLUENT_DIALOGUE_DORA_ALLOW_LIVE_CODEX_TURN=1" >&2
  exit 64
fi

NEMOTRON_VENV_WRAPPER="graphs/out/nemotron_venv_python.sh"
if [[ ! -f "${NEMOTRON_VENV_WRAPPER}" ]]; then
  echo "missing ${NEMOTRON_VENV_WRAPPER}; build the fluent_dialogue_dora nemotron_streaming_asr venv first" >&2
  exit 66
fi

NEMOTRON_MODEL_PATH="${FLUENT_DIALOGUE_DORA_NEMOTRON_MODEL_PATH:-data/models/fluent_dialogue_dora/nemotron-3.5-asr-streaming-0.6b/nemotron-3.5-asr-streaming-0.6b.nemo}"
if [[ ! -s "${NEMOTRON_MODEL_PATH}" ]]; then
  echo "missing Nemotron model: ${NEMOTRON_MODEL_PATH}" >&2
  exit 66
fi

NEMOTRON_MODEL_RESOLVED="$(python -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "${NEMOTRON_MODEL_PATH}")"
NEMOTRON_VENV_WRAPPER_RESOLVED="$(python -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "${NEMOTRON_VENV_WRAPPER}")"

python - "${LIVE_DATAFLOW}" "${MODE}" "${SESSION_ID}" "${WEB_BRIDGE_PORT}" "${CODEX_CONTROL_PORT}" "${TTS_PYOPENJTALK_PORT}" "${VLLM_BASE_URL}" "${VLLM_MODEL}" "${VLLM_PROVIDER}" "${VLLM_WIRE_API}" "${NEMOTRON_MODEL_RESOLVED}" "${NEMOTRON_VENV_WRAPPER_RESOLVED}" "${LIVE_RUNTIME_LOG_RESOLVED}" <<'PY'
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


def bounded_positive_float_env(name: str, default: str, upper: float) -> str:
    text = os.environ.get(name, default)
    try:
        value = float(text)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc
    if value <= 0.0 or value > upper:
        raise ValueError(f"{name} must be > 0 and <= {upper:g}")
    return text


def input_device_args() -> list[str]:
    use_default = os.environ.get("FLUENT_DIALOGUE_DORA_USE_DEFAULT_INPUT_DEVICE") == "1"
    device_name = os.environ.get("FLUENT_DIALOGUE_DORA_CPAL_INPUT_DEVICE_NAME")
    # Live ASR/barge-in uses the DJI Mic Rx. PowerConf S3 input was not usable
    # for recognition; echo suppression is handled downstream by software AEC.
    device_id = _device_id_or_default(
        env_name="FLUENT_DIALOGUE_DORA_CPAL_INPUT_DEVICE_ID",
        default_value="alsa:plughw:CARD=Rx,DEV=0",
        device_name=device_name,
        use_default=use_default,
    )
    return _single_device_selector(
        device_id=device_id,
        device_name=device_name,
        use_default=use_default,
        default_flag="--default-input-device",
    )


def output_device_args() -> list[str]:
    use_default = os.environ.get("FLUENT_DIALOGUE_DORA_USE_DEFAULT_OUTPUT_DEVICE") == "1"
    device_name = os.environ.get("FLUENT_DIALOGUE_DORA_CPAL_OUTPUT_DEVICE_NAME")
    device_id = _device_id_or_default(
        env_name="FLUENT_DIALOGUE_DORA_CPAL_OUTPUT_DEVICE_ID",
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
        raise ValueError(
            "select exactly one CPAL device selector by id, name, or default-device flag"
        )
    if use_default:
        return [default_flag]
    if device_name:
        return ["--device-name", device_name]
    if device_id:
        return ["--device-id", device_id]
    raise ValueError("unreachable CPAL selector state")


output_path = Path(sys.argv[1])
mode = sys.argv[2]
session_id = sys.argv[3]
web_port = sys.argv[4]
codex_control_port = sys.argv[5]
tts_port = sys.argv[6]
vllm_base_url = sys.argv[7]
vllm_model = sys.argv[8]
vllm_provider = sys.argv[9]
vllm_wire_api = sys.argv[10]
nemotron_model_path = sys.argv[11]
nemotron_venv_wrapper = sys.argv[12]
runtime_log_path = sys.argv[13]

cwd = os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_CWD", "/tmp/fluent-dialogue-dora-codex-empty-cwd")
Path(cwd).mkdir(parents=True, exist_ok=True)

developer_instructions = os.environ.get(
    "FLUENT_DIALOGUE_DORA_VOICE_DEVELOPER_INSTRUCTIONS",
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
            f"model_providers.{vllm_provider}.wire_api={json.dumps(vllm_wire_api)}",
        ]
    )
    + "\n",
)

input_backend = os.environ.get("FLUENT_DIALOGUE_DORA_INPUT_BACKEND", "cpal")
if input_backend not in ("cpal", "alsa_pcm", "pipewire_pcm"):
    raise ValueError("FLUENT_DIALOGUE_DORA_INPUT_BACKEND must be cpal, alsa_pcm, or pipewire_pcm")
capture_max_chunks = os.environ.get("FLUENT_DIALOGUE_DORA_CAPTURE_MAX_CHUNKS")
if mode == "--run" and capture_max_chunks is None:
    capture_max_chunks = "3000"
default_capture_sample_rate_hz = "48000" if input_backend == "cpal" else "16000"
default_capture_chunk_frames = "960" if input_backend == "cpal" else "320"
capture_sample_rate_hz = os.environ.get(
    "FLUENT_DIALOGUE_DORA_CAPTURE_SAMPLE_RATE_HZ",
    default_capture_sample_rate_hz,
)
# cpal の既定入力は Rx(ステレオ 2ch ネイティブ)。media_graph が 2ch→1ch に
# ダウンミックスする。他バックエンドの既定デバイス(S3)はモノラル。
default_capture_channels = "2" if input_backend == "cpal" else "1"
capture_channels = os.environ.get("FLUENT_DIALOGUE_DORA_CAPTURE_CHANNELS", default_capture_channels)
# cpal は Rx を plughw 経由で開く。cpal 0.18.1 は S24_3LE 非対応なので、ALSA plug に
# 不可避なビット深度変換だけをさせる際、非可逆な s16 化を入力層で焼かないよう
# 可逆な f32le で受ける。16bit 化・リサンプル・ダウンミックスは media_graph が担う。
# arecord/pipewire バックエンドは s16le 出力のみ対応のため据え置き。
capture_sample_format = "f32le" if input_backend == "cpal" else "s16le"
asr_audio_queue_size = positive_int_env("FLUENT_DIALOGUE_DORA_ASR_AUDIO_QUEUE_SIZE", "4096")
# Barge-in AEC: cancel the agent's own TTS (played out the S3 speaker) from the
# DJI mic before VAD/ASR, so the barge-in detector reacts to the user, not the
# echo (docs/課題/voice-dialogue-quality.md 課題1 Phase 4). When enabled the
# ASR audio path is media_graph_asr -> barge_in_aec -> {vad, nemotron}; the AEC
# output replaces media_graph_asr/audio as the source for vad / asr_control /
# nemotron. Disable with FLUENT_DIALOGUE_DORA_ENABLE_AEC=0 to fall back to the direct path.
enable_aec = os.environ.get("FLUENT_DIALOGUE_DORA_ENABLE_AEC", "1") == "1"
if enable_aec:
    asr_audio_source_id = "barge_in_aec"
    asr_audio_stream_id = f"audio/aec/{session_id}"
    asr_audio_dora_source = "barge_in_aec/audio"
else:
    asr_audio_source_id = "media_graph"
    asr_audio_stream_id = "audio/media_graph/asr"
    asr_audio_dora_source = "media_graph_asr/audio"
default_asr_linear_gain = "4.0" if input_backend == "cpal" else "1.0"
asr_linear_gain = bounded_positive_float_env(
    "FLUENT_DIALOGUE_DORA_ASR_LINEAR_GAIN",
    default_asr_linear_gain,
    10.0,
)

capture_node_id = {
    "alsa_pcm": "alsa_pcm_capture",
    "cpal": "cpal_capture",
    "pipewire_pcm": "pipewire_pcm_capture",
}[input_backend]
capture_source_id = capture_node_id
capture_stream_id = f"audio/{capture_node_id}/live"
capture_args: list[str]
if input_backend == "cpal":
    capture_args = [
        *input_device_args(),
        "--sample-rate-hz",
        capture_sample_rate_hz,
        "--channels",
        capture_channels,
        "--sample-format",
        capture_sample_format,
        "--channel-layout",
        "interleaved",
        "--chunk-frames",
        os.environ.get("FLUENT_DIALOGUE_DORA_CAPTURE_CHUNK_FRAMES", default_capture_chunk_frames),
        "--buffer-size-frames",
        os.environ.get("FLUENT_DIALOGUE_DORA_CAPTURE_BUFFER_SIZE_FRAMES", "2048"),
        "--queue-capacity-chunks",
        os.environ.get("FLUENT_DIALOGUE_DORA_CAPTURE_QUEUE_CAPACITY_CHUNKS", "2048"),
        "--source-id",
        capture_source_id,
        "--stream-id",
        capture_stream_id,
        "--start-seq",
        "0",
        "--start-sample-index",
        "0",
        "--start-capture-time-ns",
        "0",
        "--capture-timeout-ms",
        os.environ.get("FLUENT_DIALOGUE_DORA_CAPTURE_TIMEOUT_MS", "3000"),
    ]
elif input_backend == "alsa_pcm":
    capture_args = [
        nemotron_venv_wrapper,
        "../../nodes/audio_device/alsa_pcm_capture/main.py",
        "--dora",
        "--device",
        os.environ.get("FLUENT_DIALOGUE_DORA_ALSA_CAPTURE_DEVICE", "pipewire"),
        "--sample-rate-hz",
        capture_sample_rate_hz,
        "--channels",
        capture_channels,
        "--sample-format",
        "s16le",
        "--channel-layout",
        "interleaved",
        "--chunk-frames",
        os.environ.get("FLUENT_DIALOGUE_DORA_CAPTURE_CHUNK_FRAMES", default_capture_chunk_frames),
        "--source-id",
        capture_source_id,
        "--stream-id",
        capture_stream_id,
        "--start-seq",
        "0",
        "--start-sample-index",
        "0",
        "--start-capture-time-ns",
        "0",
        "--output-drain-seconds",
        "0.1",
    ]
else:
    capture_args = [
        nemotron_venv_wrapper,
        "../../nodes/audio_device/pipewire_pcm_capture/main.py",
        "--dora",
        "--target",
        os.environ.get(
            "FLUENT_DIALOGUE_DORA_PIPEWIRE_CAPTURE_TARGET",
            "alsa_input.usb-Anker_PowerConf_S3_A3321-DEV-SN1-01.mono-fallback",
        ),
        "--latency",
        os.environ.get("FLUENT_DIALOGUE_DORA_PIPEWIRE_CAPTURE_LATENCY", "20ms"),
        "--sample-rate-hz",
        capture_sample_rate_hz,
        "--channels",
        capture_channels,
        "--sample-format",
        "s16le",
        "--channel-layout",
        "interleaved",
        "--chunk-frames",
        os.environ.get("FLUENT_DIALOGUE_DORA_CAPTURE_CHUNK_FRAMES", default_capture_chunk_frames),
        "--source-id",
        capture_source_id,
        "--stream-id",
        capture_stream_id,
        "--start-seq",
        "0",
        "--start-sample-index",
        "0",
        "--start-capture-time-ns",
        "0",
        "--output-drain-seconds",
        "0.1",
    ]
if capture_max_chunks is not None:
    capture_args.extend(["--max-chunks", capture_max_chunks])

codex_args = [
    nemotron_venv_wrapper,
    "../../nodes/dialogue_engine/codex_app_server/main.py",
    "--dora",
    "--timeout-seconds",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_TIMEOUT_SECONDS", "180"),
    "--approval-response-timeout-seconds",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_APPROVAL_TIMEOUT_SECONDS", "900"),
    "--cwd",
    cwd,
    # この機体の tegra カーネルは Landlock 無効で read-only sandbox が機能しない
    # (docs/課題/voice-dialogue-quality.md 課題5)。サンドボックスなし実行を許容し、
    # 危険コマンドはダッシュボード承認ゲート(untrusted)で抑止する方針 (2026-06-12 合意)。
    "--sandbox",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_SANDBOX", "danger-full-access"),
    "--approval-policy",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_APPROVAL_POLICY", "untrusted"),
    "--approvals-reviewer",
    os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_APPROVALS_REVIEWER", "user"),
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

lines: list[str] = ["nodes:"]
if input_backend == "cpal":
    lines.extend(
        [
            "  - id: cpal_capture",
            "    build: ../../scripts/dora_cargo_build.sh ../../nodes/audio_device/cpal_capture/Cargo.toml",
            "    path: ../../nodes/audio_device/cpal_capture/target/debug/cpal_capture",
            "    args: " + yaml_args(capture_args),
            "    outputs:",
            "      - audio",
            "",
        ]
    )
elif input_backend == "alsa_pcm":
    lines.extend(
        [
            "  - id: alsa_pcm_capture",
            "    path: /bin/bash",
            "    args: " + yaml_args(capture_args),
            "    outputs:",
            "      - audio",
            "",
        ]
    )
else:
    lines.extend(
        [
            "  - id: pipewire_pcm_capture",
            "    path: /bin/bash",
            "    args: " + yaml_args(capture_args),
            "    outputs:",
            "      - audio",
            "",
        ]
    )

lines.extend(
    [
    "  - id: media_graph_asr",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            nemotron_venv_wrapper,
            "../../nodes/media_graph/main.py",
            "--dora",
            "--input-source-id",
            capture_source_id,
            "--input-stream-id",
            capture_stream_id,
            "--input-sample-rate-hz",
            capture_sample_rate_hz,
            "--input-channels",
            capture_channels,
            "--input-sample-format",
            capture_sample_format,
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
            "--linear-gain",
            asr_linear_gain,
        ]
    ),
    "    inputs:",
    "      audio:",
    f"        source: {capture_node_id}/audio",
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
            nemotron_venv_wrapper,
            "../../nodes/vad/silero/main.py",
            "--dora",
            "--input-source-id",
            asr_audio_source_id,
            "--input-stream-id",
            asr_audio_stream_id,
            "--output-source-id",
            "silero_vad",
            "--output-stream-id",
            "activity/vad/asr",
            "--threshold",
            os.environ.get("FLUENT_DIALOGUE_DORA_VAD_THRESHOLD", "0.5"),
            "--level-period-windows",
            os.environ.get("FLUENT_DIALOGUE_DORA_VAD_LEVEL_PERIOD_WINDOWS", "8"),
        ]
    ),
    "    inputs:",
    "      audio:",
    f"        source: {asr_audio_dora_source}",
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
            nemotron_venv_wrapper,
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
            os.environ.get("FLUENT_DIALOGUE_DORA_TURN_END_SILENCE_FRAMES", "12000"),
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
            nemotron_venv_wrapper,
            "../../nodes/asr/asr_control_from_turn/main.py",
            "--dora",
            "--input-session-id",
            session_id,
            "--input-turn-stream-id",
            f"turn/{session_id}",
            "--output-audio-stream-id",
            asr_audio_stream_id,
            "--asr-prebuffer-frames",
            os.environ.get("FLUENT_DIALOGUE_DORA_ASR_PREBUFFER_FRAMES", "16000"),
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
            nemotron_venv_wrapper,
            "../../nodes/asr/nemotron_streaming/main.py",
            "--dora",
            "--input-audio-source-id",
            asr_audio_source_id,
            "--input-audio-stream-id",
            asr_audio_stream_id,
            "--session-id",
            session_id,
            "--output-stream-id",
            f"transcript/{session_id}",
            "--prebuffer-frames",
            os.environ.get("FLUENT_DIALOGUE_DORA_NEMOTRON_PREBUFFER_FRAMES", "32768"),
            "--control-holdback-frames",
            os.environ.get("FLUENT_DIALOGUE_DORA_NEMOTRON_CONTROL_HOLDBACK_FRAMES", "4096"),
            "--late-stop-tolerance-frames",
            os.environ.get("FLUENT_DIALOGUE_DORA_NEMOTRON_LATE_STOP_TOLERANCE_FRAMES", "16000"),
            "--warmup-frames",
            os.environ.get("FLUENT_DIALOGUE_DORA_NEMOTRON_WARMUP_FRAMES", "16000"),
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
            "--model-extracted-dir",
            os.environ.get(
                "FLUENT_DIALOGUE_DORA_NEMOTRON_MODEL_EXTRACTED_DIR",
                str(Path(nemotron_model_path).parent / "extracted"),
            ),
            "--target-lang",
            os.environ.get("FLUENT_DIALOGUE_DORA_ASR_TARGET_LANG", "ja-JP"),
            "--att-context-right-frames",
            os.environ.get("FLUENT_DIALOGUE_DORA_NEMOTRON_ATT_CONTEXT_RIGHT_FRAMES", "3"),
            "--final-transcript-mode",
            os.environ.get("FLUENT_DIALOGUE_DORA_NEMOTRON_FINAL_TRANSCRIPT_MODE", "streaming"),
        ]
    ),
    "    inputs:",
    "      audio:",
    f"        source: {asr_audio_dora_source}",
    f"        queue_size: {asr_audio_queue_size}",
    "        queue_policy: backpressure",
    "      asr_control:",
    "        source: asr_control_from_turn/asr_control",
    "        queue_size: 32",
    "        queue_policy: backpressure",
    "    outputs:",
    "      - transcript",
    "",
    "  - id: dialogue_engine",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            nemotron_venv_wrapper,
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
    "      playback_state:",
    "        source: playback_queue/playback_state",
    "        queue_size: 64",
    "        queue_policy: backpressure",
    "      barge_in:",
    "        source: barge_in_detector/barge_in",
    "        queue_size: 16",
    "        queue_policy: backpressure",
    "    outputs:",
    "      - agent_turn",
    "      - agent_cancel",
    "      - session",
    "      - dialogue",
    "      - tts_text",
    "      - playback_command",
    "      - playback_control",
    "",
    "  - id: barge_in_detector",
    "    path: /bin/bash",
    "    args: "
    + yaml_args(
        [
            nemotron_venv_wrapper,
            "../../nodes/vad/barge_in_detector/main.py",
            "--dora",
            "--session-id",
            session_id,
            "--source-id",
            "barge_in_detector",
            "--output-stream-id",
            f"barge_in/{session_id}",
            "--barge-in-speech-frames",
            os.environ.get("FLUENT_DIALOGUE_DORA_BARGE_IN_SPEECH_FRAMES", "4800"),
            "--silence-reset-frames",
            os.environ.get("FLUENT_DIALOGUE_DORA_BARGE_IN_SILENCE_RESET_FRAMES", "2048"),
            "--min-speech-probability",
            os.environ.get("FLUENT_DIALOGUE_DORA_BARGE_IN_MIN_SPEECH_PROBABILITY", "0.5"),
        ]
    ),
    "    inputs:",
    "      activity:",
    "        source: vad/activity",
    "        queue_size: 64",
    "        queue_policy: backpressure",
    "      playback_state:",
    "        source: playback_queue/playback_state",
    "        queue_size: 64",
    "        queue_policy: backpressure",
    "    outputs:",
    "      - barge_in",
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
    ]
)

lines.extend(
    [
        "    outputs:",
        "      - agent_event",
        "      - agent_text",
        "      - agent_done",
        "      - agent_approval",
        "      - agent_user_input",
        "      - agent_mcp_elicitation",
        "      - agent_tool",
        "",
    ]
)

lines.extend(
    [
        "  - id: tts_backend",
        "    path: /bin/bash",
        "    args: "
        + yaml_args(
            [
                nemotron_venv_wrapper,
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
        "        queue_size: 32",
        "        queue_policy: backpressure",
        "    outputs:",
        "      - synth_audio",
        "",
        "  - id: playback_queue",
        "    path: /bin/bash",
        "    args: "
        + yaml_args(
            [
                nemotron_venv_wrapper,
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
        f"        queue_size: {os.environ.get('FLUENT_DIALOGUE_DORA_SYNTH_AUDIO_QUEUE_SIZE', '4096')}",
        "        queue_policy: backpressure",
        "      playback_command:",
        "        source: dialogue_engine/playback_command",
        "        queue_size: 16",
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
                nemotron_venv_wrapper,
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
        f"        queue_size: {os.environ.get('FLUENT_DIALOGUE_DORA_SPEAKER_UPSTREAM_QUEUE_SIZE', '4096')}",
        "        queue_policy: backpressure",
        "    outputs:",
        "      - audio",
        "",
        "  - id: media_graph_speaker",
        "    path: /bin/bash",
        "    args: "
        + yaml_args(
            [
                nemotron_venv_wrapper,
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
        f"        queue_size: {os.environ.get('FLUENT_DIALOGUE_DORA_SPEAKER_UPSTREAM_QUEUE_SIZE', '4096')}",
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
                os.environ.get("FLUENT_DIALOGUE_DORA_OUTPUT_BUFFER_SIZE_FRAMES", "480"),
                "--queue-capacity-chunks",
                os.environ.get("FLUENT_DIALOGUE_DORA_OUTPUT_QUEUE_CAPACITY_CHUNKS", "128"),
                "--startup-buffer-chunks",
                os.environ.get("FLUENT_DIALOGUE_DORA_OUTPUT_STARTUP_BUFFER_CHUNKS", "2"),
                "--empty-queue-policy",
                os.environ.get("FLUENT_DIALOGUE_DORA_OUTPUT_EMPTY_QUEUE_POLICY", "silence"),
                "--source-id",
                "speaker_media_graph",
                "--stream-id",
                "speaker/cpal",
                "--completion-timeout-ms",
                os.environ.get("FLUENT_DIALOGUE_DORA_OUTPUT_COMPLETION_TIMEOUT_MS", "30000"),
                "--render-reference-source-id",
                "cpal_sink",
                "--render-reference-stream-id",
                "audio/cpal_sink/render_reference",
            ]
        ),
        "    inputs:",
        "      audio:",
        "        source: media_graph_speaker/audio",
        f"        queue_size: {os.environ.get('FLUENT_DIALOGUE_DORA_CPAL_SINK_EDGE_QUEUE_SIZE', '4096')}",
        "        queue_policy: backpressure",
        "      playback_control:",
        "        source: dialogue_engine/playback_control",
        "        queue_size: 16",
        "        queue_policy: backpressure",
        "    outputs:",
        "      - render_reference",
        "",
        "  - id: dora_web_bridge",
        "    path: /bin/bash",
        "    args: "
        + yaml_args(
            [
                nemotron_venv_wrapper,
                "../../bridges/dora_web_bridge/main.py",
                "--dora",
                "--dataflow",
                str(output_path.resolve()),
                "--session-id",
                session_id,
                "--port",
                web_port,
                "--host",
                os.environ.get("FLUENT_DIALOGUE_DORA_WEB_BRIDGE_HOST", "127.0.0.1"),
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
                "barge_in",
                "--input",
                "playback_state",
                "--input",
                "playback_done",
                "--runtime-log",
                runtime_log_path,
                *(["--keep-http-after-dora-stop"] if os.environ.get("FLUENT_DIALOGUE_DORA_KEEP_HTTP_AFTER_DORA_STOP") == "1" else []),
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
        "      barge_in:",
        "        source: barge_in_detector/barge_in",
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
)

if enable_aec:
    aec_args = [
        "--output-source-id",
        asr_audio_source_id,
        "--output-stream-id",
        asr_audio_stream_id,
        "--far-buffer-max-samples",
        os.environ.get("FLUENT_DIALOGUE_DORA_AEC_FAR_BUFFER_MAX_SAMPLES", "32000"),
        "--backend",
        os.environ.get("FLUENT_DIALOGUE_DORA_AEC_BACKEND", "webrtc"),
    ]
    # Default delay is tuned for the local S3 mic/speaker live path. Override
    # FLUENT_DIALOGUE_DORA_AEC_STREAM_DELAY_MS when the acoustic path or device changes.
    stream_delay_ms = positive_int_env("FLUENT_DIALOGUE_DORA_AEC_STREAM_DELAY_MS", "40")
    aec_args.extend(["--stream-delay-ms", stream_delay_ms])
    lines.extend(
        [
            "",
            "  - id: barge_in_aec",
            "    build: ../../scripts/dora_cargo_build.sh --release "
            "../../nodes/audio_device/barge_in_aec/Cargo.toml",
            "    path: ../../nodes/audio_device/barge_in_aec/target/release/barge_in_aec",
            "    args: " + yaml_args(aec_args),
            "    inputs:",
            "      near:",
            "        source: media_graph_asr/audio",
            "        queue_size: 128",
            "        queue_policy: backpressure",
            "      far:",
            "        source: cpal_sink/render_reference",
            f"        queue_size: {os.environ.get('FLUENT_DIALOGUE_DORA_AEC_FAR_EDGE_QUEUE_SIZE', '4')}",
            "        queue_policy: backpressure",
            "    outputs:",
            "      - audio",
        ]
    )

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

scripts/dora_cargo_build.sh nodes/audio_device/cpal_capture/Cargo.toml
scripts/dora_cargo_build.sh nodes/audio_device/cpal_sink/Cargo.toml
scripts/dora_cargo_build.sh --release nodes/audio_device/barge_in_aec/Cargo.toml

TTS_BACKEND="${FLUENT_DIALOGUE_DORA_TTS_BACKEND:-pyopenjtalk}"
if [[ "${TTS_BACKEND}" == "kokoro" ]]; then
  KOKORO_PYTHON="${FLUENT_DIALOGUE_DORA_KOKORO_PYTHON:-${REPO_ROOT}/../daihen-physical-ai.audio/data/builds/envs/tts_kokoro/current/venv/bin/python}"
  if [[ ! -x "${KOKORO_PYTHON}" ]]; then
    echo "missing tts_kokoro venv python: ${KOKORO_PYTHON}" >&2
    exit 66
  fi
  "${KOKORO_PYTHON}" nodes/tts/tts_kokoro_server/main.py \
    --port "${TTS_PYOPENJTALK_PORT}" \
    --repo-id "${FLUENT_DIALOGUE_DORA_KOKORO_REPO_ID:-${REPO_ROOT}/data/models/fluent_dialogue_dora/Kokoro-82M}" \
    --default-voice-id "${FLUENT_DIALOGUE_DORA_KOKORO_VOICE:-jf_alpha}" \
    --chunk-frames "${FLUENT_DIALOGUE_DORA_TTS_CHUNK_FRAMES:-2400}" &
elif [[ "${TTS_BACKEND}" == "pyopenjtalk" ]]; then
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
    --chunk-frames "${FLUENT_DIALOGUE_DORA_TTS_CHUNK_FRAMES:-2400}" &
else
  echo "unsupported FLUENT_DIALOGUE_DORA_TTS_BACKEND: ${TTS_BACKEND} (kokoro|pyopenjtalk)" >&2
  exit 64
fi
TTS_SERVER_PID="$!"
LIVE_SESSION_TTS_SERVER_PID="${TTS_SERVER_PID}"
LIVE_SESSION_TTS_SERVER_PGID="$(live_session_pgid "${TTS_SERVER_PID}")"
LIVE_SESSION_TTS_SERVER_SID="$(live_session_sid "${TTS_SERVER_PID}")"
live_session_write_state

python - "${TTS_PYOPENJTALK_PORT}" <<'PY'
from __future__ import annotations

import http.client
import sys
import time


def wait_for_port(port: int) -> None:
    # Kokoro opens its port only after torch import + model load + warmup.
    deadline = time.monotonic() + 90.0
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

if [[ "${FLUENT_DIALOGUE_DORA_INPUT_BACKEND:-alsa_pcm}" == "pipewire_pcm" ]]; then
  PIPEWIRE_CAPTURE_TARGET="${FLUENT_DIALOGUE_DORA_PIPEWIRE_CAPTURE_TARGET:-alsa_input.usb-Anker_PowerConf_S3_A3321-DEV-SN1-01.mono-fallback}"
  PIPEWIRE_CAPTURE_SOURCE_ID="$(
    python - "${PIPEWIRE_CAPTURE_TARGET}" <<'PY'
from __future__ import annotations

import json
import subprocess
import sys

target = sys.argv[1]
items = json.loads(subprocess.check_output(["pw-dump"], text=True))
for item in items:
    props = item.get("info", {}).get("props", {})
    if props.get("node.name") == target:
        media_class = props.get("media.class")
        if media_class != "Audio/Source":
            raise SystemExit(f"PipeWire target is not an Audio/Source: {target} ({media_class})")
        print(item["id"])
        raise SystemExit(0)
raise SystemExit(f"PipeWire capture target not found: {target}")
PY
  )"
  wpctl set-default "${PIPEWIRE_CAPTURE_SOURCE_ID}"
  echo "pipewire capture default-source: ${PIPEWIRE_CAPTURE_TARGET} (id ${PIPEWIRE_CAPTURE_SOURCE_ID})" >&2
fi

echo "web dashboard: http://127.0.0.1:${WEB_BRIDGE_PORT}/?session=${SESSION_ID}" >&2
live_session_run_dora uvx --from dora-rs-cli dora run "${LIVE_DATAFLOW}" --uv
