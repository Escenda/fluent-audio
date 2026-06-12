#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

RUN_ROS2_DOCKER=1
RUN_TTS=1
RUN_CODEX_HANDSHAKE=1
RUN_DEVICE_SMOKES=1
RUN_NEMOTRON=1

usage() {
  cat <<'EOF'
Usage: scripts/run_non_live_completion_smoke.sh [options]

Runs the representative non-live verification set for fluent-audio.
Live Codex model turns and live approval turns are intentionally excluded.

Options:
  --skip-ros2-docker       Do not run the Docker/Jazzy ROS2 sidecar smoke.
  --skip-tts               Do not run the real PyOpenJTalk TTS smoke.
  --skip-codex-handshake   Do not run live codex app-server initialize/thread-start handshake.
  --skip-device-smokes     Do not run CPAL capture/sink/playback hardware smokes.
  --skip-nemotron          Do not run the real Nemotron DORA smoke.
  -h, --help               Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-ros2-docker)
      RUN_ROS2_DOCKER=0
      shift
      ;;
    --skip-tts)
      RUN_TTS=0
      shift
      ;;
    --skip-codex-handshake)
      RUN_CODEX_HANDSHAKE=0
      shift
      ;;
    --skip-device-smokes)
      RUN_DEVICE_SMOKES=0
      shift
      ;;
    --skip-nemotron)
      RUN_NEMOTRON=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

run_stage() {
  local label="$1"
  shift
  echo
  echo "==> ${label}"
  "$@"
}

run_shell_stage() {
  local label="$1"
  local command="$2"
  echo
  echo "==> ${label}"
  bash -lc "${command}"
}

assert_no_managed_source_absolute_home_paths() {
  local output_file="/tmp/fluent_audio_abs_paths.txt"
  rm -f "${output_file}"
  find . \
    \( -path './.git' \
      -o -path './target' \
      -o -path './graphs/out' \
      -o -path './.venv' \
      -o -path './.pytest_cache' \
      -o -path './.ruff_cache' \
      -o -path './artifacts' \
      -o -path '*/__pycache__' \
      -o -path './nodes/audio_device/cpal_sink/target' \
      -o -path './nodes/audio_device/cpal_capture/target' \
      -o -path './nodes/audio_device/rust_audio_boundary/target' \
    \) -prune -o -type f -print \
    | xargs grep -In "${HOME}" >"${output_file}" 2>/dev/null && {
      cat "${output_file}"
      return 1
    }
  test ! -s "${output_file}"
}

cd "${REPO_ROOT}"

run_stage "ruff" \
  uv run --extra dev --extra dora --extra vad --extra tts python -m ruff check .

run_stage "contracts and node tests" \
  uv run --extra dev --extra dora --extra vad --extra tts python -m pytest \
    tests/contracts \
    tests/nodes/dialogue_engine \
    tests/bridges \
    tests/nodes/playback \
    tests/nodes/audio_device \
    tests/nodes/media_graph \
    tests/nodes/asr \
    tests/nodes/vad \
    tests/nodes/tts \
    tests/fixtures \
    tests/ros2 \
    -q

run_shell_stage "offline PCM roundtrip DORA smoke" \
  "mkdir -p artifacts/offline && uvx --from dora-rs-cli dora run graphs/offline_roundtrip.yml --uv && cmp tests/fixtures/offline/input.s16le artifacts/offline/output.s16le"

run_shell_stage "media_graph passthrough DORA smoke" \
  "mkdir -p artifacts/media_graph && uvx --from dora-rs-cli dora run graphs/media_graph_passthrough.yml --uv && cmp tests/fixtures/offline/input.s16le artifacts/media_graph/passthrough_main.s16le && cmp tests/fixtures/offline/input.s16le artifacts/media_graph/passthrough_tap.s16le"

run_shell_stage "media_graph resample DORA smoke and GStreamer reference comparison" \
  "mkdir -p artifacts/media_graph && uvx --from dora-rs-cli dora run graphs/media_graph_resample.yml --uv && gst-launch-1.0 -q filesrc location=tests/fixtures/cpal/silence_48k_stereo_250ms.s16le ! rawaudioparse format=pcm pcm-format=s16le sample-rate=48000 num-channels=2 interleaved=true ! audioconvert ! audioresample ! audio/x-raw,format=S16LE,rate=16000,channels=2,layout=interleaved ! filesink location=/tmp/fluent_audio_gst_resampled_16k.s16le && cmp /tmp/fluent_audio_gst_resampled_16k.s16le artifacts/media_graph/resampled_16k.s16le"

if [[ "${RUN_DEVICE_SMOKES}" == "1" ]]; then
  run_stage "CPAL capture hardware build" \
    uvx --from dora-rs-cli dora build graphs/cpal_capture_smoke.yml --uv --local

  run_stage "CPAL capture hardware smoke" \
    uvx --from dora-rs-cli dora run graphs/cpal_capture_smoke.yml --uv

  run_stage "CPAL sink hardware build" \
    uvx --from dora-rs-cli dora build graphs/cpal_sink_smoke.yml --uv --local

  run_stage "CPAL sink hardware smoke" \
    uvx --from dora-rs-cli dora run graphs/cpal_sink_smoke.yml --uv

  run_stage "playback queue to CPAL sink build" \
    uvx --from dora-rs-cli dora build graphs/playback_queue_cpal_sink_smoke.yml --uv --local

  run_stage "playback queue to CPAL sink smoke" \
    uvx --from dora-rs-cli dora run graphs/playback_queue_cpal_sink_smoke.yml --uv
else
  echo
  echo "==> CPAL hardware smokes skipped by explicit option"
fi

run_stage "VAD speech DORA smoke" \
  uvx --from dora-rs-cli dora run graphs/vad_speech_smoke.yml --uv

run_stage "turn detector DORA smoke" \
  uvx --from dora-rs-cli dora run graphs/turn_detector_smoke.yml --uv

if [[ "${RUN_NEMOTRON}" == "1" ]]; then
  run_shell_stage "Nemotron real-model DORA smoke" \
    "cd graphs/out && uvx --from dora-rs-cli dora run asr_nemotron_smoke.local.yml --uv"
else
  echo
  echo "==> Nemotron real-model DORA smoke skipped by explicit option"
fi

run_stage "codex app-server fixture turn smoke" \
  "${SCRIPT_DIR}/run_codex_app_server_fixture_smoke.sh"

run_stage "codex app-server direct approval fixture smoke" \
  uvx --from dora-rs-cli dora run graphs/codex_app_server_approval_fixture_smoke.yml --uv

run_stage "codex app-server permissions approval fixture smoke" \
  uvx --from dora-rs-cli dora run graphs/codex_app_server_permissions_approval_fixture_smoke.yml --uv

run_stage "codex app-server Web-mediated approval fixture smoke" \
  "${SCRIPT_DIR}/run_codex_app_server_web_approval_fixture_smoke.sh"

run_stage "integrated dialogue to CPAL/Web/ROS2 projection smoke" \
  "${SCRIPT_DIR}/run_dialogue_to_cpal_smoke.sh"

if [[ "${RUN_TTS}" == "1" ]]; then
  run_stage "real PyOpenJTalk TTS smoke" \
    "${SCRIPT_DIR}/run_tts_pyopenjtalk_smoke.sh"
else
  echo
  echo "==> real PyOpenJTalk TTS smoke skipped by explicit option"
fi

if [[ "${RUN_CODEX_HANDSHAKE}" == "1" ]]; then
  run_stage "live codex app-server handshake without model turn" \
    "${SCRIPT_DIR}/run_codex_app_server_live_smoke.sh" --handshake-only

  run_stage "write guarded live codex turn dataflow without model turn" \
    "${SCRIPT_DIR}/run_codex_app_server_live_smoke.sh" --write-live-turn-dataflow

  run_stage "write guarded live codex approval dataflow without model turn" \
    "${SCRIPT_DIR}/run_codex_app_server_live_smoke.sh" --write-live-approval-dataflow
else
  echo
  echo "==> live codex app-server handshake/dataflow generation skipped by explicit option"
fi

if [[ "${RUN_ROS2_DOCKER}" == "1" ]]; then
  run_stage "ROS2 Jazzy sidecar Docker smoke" \
    "${SCRIPT_DIR}/run_ros2_bridge_sidecar_smoke_docker.sh"
else
  echo
  echo "==> ROS2 Jazzy sidecar Docker smoke skipped by explicit option"
fi

run_shell_stage "no forbidden loose contract typing patterns" \
  "grep -RInE 'dict\\[str, Any\\]|from typing import Any|: object|list\\[object\\]|dict\\[str, object\\]|# type: ignore|except ImportError' src nodes tests --exclude-dir=target --exclude-dir=__pycache__ --exclude-dir=.venv >/tmp/fluent_audio_forbidden_patterns.txt && { cat /tmp/fluent_audio_forbidden_patterns.txt; exit 1; } || test ! -s /tmp/fluent_audio_forbidden_patterns.txt"

run_stage "no managed-source absolute home paths" \
  assert_no_managed_source_absolute_home_paths

run_stage "git diff whitespace check" \
  git diff --check

echo
echo "non-live completion smoke passed"
