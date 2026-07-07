#!/usr/bin/env bash
# shellcheck shell=bash

live_session_quote() {
  printf "%q" "$1"
}

live_session_pgid() {
  ps -o pgid= -p "$1" 2>/dev/null | tr -d "[:space:]"
}

live_session_sid() {
  ps -o sid= -p "$1" 2>/dev/null | tr -d "[:space:]"
}

live_session_pid_alive() {
  [[ -n "${1:-}" ]] && kill -0 "$1" 2>/dev/null
}

live_session_group_alive() {
  [[ -n "${1:-}" ]] && kill -0 -- "-$1" 2>/dev/null
}

live_session_pid_matches() {
  local pid="$1"
  local pgid="${2:-}"
  local sid="${3:-}"
  live_session_pid_alive "${pid}" || return 1
  if [[ -n "${pgid}" && "$(live_session_pgid "${pid}")" != "${pgid}" ]]; then
    return 1
  fi
  if [[ -n "${sid}" && "$(live_session_sid "${pid}")" != "${sid}" ]]; then
    return 1
  fi
}

live_session_load_state() {
  [[ -f "${LIVE_SESSION_STATE_FILE}" ]] || return 1
  FLUENT_DIALOGUE_DORA_RUN_STATE_VERSION=""
  FLUENT_DIALOGUE_DORA_RUN_SESSION=""
  FLUENT_DIALOGUE_DORA_RUN_SESSION_ID=""
  FLUENT_DIALOGUE_DORA_RUN_MODE=""
  FLUENT_DIALOGUE_DORA_RUN_ROOT_PID=""
  FLUENT_DIALOGUE_DORA_RUN_ROOT_PGID=""
  FLUENT_DIALOGUE_DORA_RUN_ROOT_SID=""
  FLUENT_DIALOGUE_DORA_RUN_DORA_PID=""
  FLUENT_DIALOGUE_DORA_RUN_DORA_PGID=""
  FLUENT_DIALOGUE_DORA_RUN_DORA_SID=""
  FLUENT_DIALOGUE_DORA_RUN_TTS_SERVER_PID=""
  FLUENT_DIALOGUE_DORA_RUN_TTS_SERVER_PGID=""
  FLUENT_DIALOGUE_DORA_RUN_TTS_SERVER_SID=""
  FLUENT_DIALOGUE_DORA_RUN_WEB_BRIDGE_PORT=""
  FLUENT_DIALOGUE_DORA_RUN_CODEX_CONTROL_PORT=""
  FLUENT_DIALOGUE_DORA_RUN_TTS_PORT=""
  FLUENT_DIALOGUE_DORA_RUN_DATAFLOW=""
  FLUENT_DIALOGUE_DORA_RUN_RUNTIME_LOG=""
  FLUENT_DIALOGUE_DORA_RUN_VLLM_BASE_URL=""
  # run.env is the authoritative state file written by these scripts.
  # shellcheck disable=SC1090
  source "${LIVE_SESSION_STATE_FILE}"
}

live_session_state_root_alive() {
  live_session_pid_matches \
    "${FLUENT_DIALOGUE_DORA_RUN_ROOT_PID:-}" \
    "${FLUENT_DIALOGUE_DORA_RUN_ROOT_PGID:-}" \
    "${FLUENT_DIALOGUE_DORA_RUN_ROOT_SID:-}"
}

live_session_state_dora_alive() {
  if live_session_pid_matches \
    "${FLUENT_DIALOGUE_DORA_RUN_DORA_PID:-}" \
    "${FLUENT_DIALOGUE_DORA_RUN_DORA_PGID:-}" \
    "${FLUENT_DIALOGUE_DORA_RUN_DORA_SID:-}"; then
    return 0
  fi
  live_session_group_alive "${FLUENT_DIALOGUE_DORA_RUN_DORA_PGID:-}"
}

live_session_state_tts_alive() {
  live_session_pid_matches \
    "${FLUENT_DIALOGUE_DORA_RUN_TTS_SERVER_PID:-}" \
    "${FLUENT_DIALOGUE_DORA_RUN_TTS_SERVER_PGID:-}" \
    "${FLUENT_DIALOGUE_DORA_RUN_TTS_SERVER_SID:-}"
}

live_session_state_alive() {
  live_session_state_root_alive \
    || live_session_state_dora_alive \
    || live_session_state_tts_alive
}

live_session_write_state() {
  mkdir -p "$(dirname "${LIVE_SESSION_STATE_FILE}")"
  local root_pid="${BASHPID}"
  local root_pgid root_sid tts_pgid tts_sid dora_pgid dora_sid tmp
  root_pgid="$(live_session_pgid "${root_pid}")"
  root_sid="$(live_session_sid "${root_pid}")"
  dora_pgid="${LIVE_SESSION_DORA_PGID:-}"
  dora_sid="${LIVE_SESSION_DORA_SID:-}"
  if [[ -n "${LIVE_SESSION_DORA_PID:-}" ]]; then
    dora_pgid="${dora_pgid:-$(live_session_pgid "${LIVE_SESSION_DORA_PID}")}"
    dora_sid="${dora_sid:-$(live_session_sid "${LIVE_SESSION_DORA_PID}")}"
  fi
  tts_pgid="${LIVE_SESSION_TTS_SERVER_PGID:-}"
  tts_sid="${LIVE_SESSION_TTS_SERVER_SID:-}"
  if [[ -n "${LIVE_SESSION_TTS_SERVER_PID:-}" ]]; then
    tts_pgid="${tts_pgid:-$(live_session_pgid "${LIVE_SESSION_TTS_SERVER_PID}")}"
    tts_sid="${tts_sid:-$(live_session_sid "${LIVE_SESSION_TTS_SERVER_PID}")}"
  fi
  tmp="${LIVE_SESSION_STATE_FILE}.$$"
  {
    printf "FLUENT_DIALOGUE_DORA_RUN_STATE_VERSION=%s\n" "$(live_session_quote "1")"
    printf "FLUENT_DIALOGUE_DORA_RUN_SESSION=%s\n" "$(live_session_quote "${LIVE_SESSION_NAME}")"
    printf "FLUENT_DIALOGUE_DORA_RUN_SESSION_ID=%s\n" "$(live_session_quote "${LIVE_SESSION_ID}")"
    printf "FLUENT_DIALOGUE_DORA_RUN_MODE=%s\n" "$(live_session_quote "${LIVE_SESSION_MODE}")"
    printf "FLUENT_DIALOGUE_DORA_RUN_STARTED_AT=%s\n" "$(live_session_quote "$(date -u +%Y-%m-%dT%H:%M:%SZ)")"
    printf "FLUENT_DIALOGUE_DORA_RUN_ROOT_PID=%s\n" "$(live_session_quote "${root_pid}")"
    printf "FLUENT_DIALOGUE_DORA_RUN_ROOT_PGID=%s\n" "$(live_session_quote "${root_pgid}")"
    printf "FLUENT_DIALOGUE_DORA_RUN_ROOT_SID=%s\n" "$(live_session_quote "${root_sid}")"
    printf "FLUENT_DIALOGUE_DORA_RUN_DORA_PID=%s\n" "$(live_session_quote "${LIVE_SESSION_DORA_PID:-}")"
    printf "FLUENT_DIALOGUE_DORA_RUN_DORA_PGID=%s\n" "$(live_session_quote "${dora_pgid}")"
    printf "FLUENT_DIALOGUE_DORA_RUN_DORA_SID=%s\n" "$(live_session_quote "${dora_sid}")"
    printf "FLUENT_DIALOGUE_DORA_RUN_TTS_SERVER_PID=%s\n" "$(live_session_quote "${LIVE_SESSION_TTS_SERVER_PID:-}")"
    printf "FLUENT_DIALOGUE_DORA_RUN_TTS_SERVER_PGID=%s\n" "$(live_session_quote "${tts_pgid}")"
    printf "FLUENT_DIALOGUE_DORA_RUN_TTS_SERVER_SID=%s\n" "$(live_session_quote "${tts_sid}")"
    printf "FLUENT_DIALOGUE_DORA_RUN_WEB_BRIDGE_PORT=%s\n" "$(live_session_quote "${LIVE_SESSION_WEB_BRIDGE_PORT}")"
    printf "FLUENT_DIALOGUE_DORA_RUN_CODEX_CONTROL_PORT=%s\n" "$(live_session_quote "${LIVE_SESSION_CODEX_CONTROL_PORT}")"
    printf "FLUENT_DIALOGUE_DORA_RUN_TTS_PORT=%s\n" "$(live_session_quote "${LIVE_SESSION_TTS_PORT}")"
    printf "FLUENT_DIALOGUE_DORA_RUN_DATAFLOW=%s\n" "$(live_session_quote "${LIVE_SESSION_DATAFLOW}")"
    printf "FLUENT_DIALOGUE_DORA_RUN_RUNTIME_LOG=%s\n" "$(live_session_quote "${LIVE_SESSION_RUNTIME_LOG}")"
    printf "FLUENT_DIALOGUE_DORA_RUN_VLLM_BASE_URL=%s\n" "$(live_session_quote "${LIVE_SESSION_VLLM_BASE_URL}")"
  } >"${tmp}"
  mv "${tmp}" "${LIVE_SESSION_STATE_FILE}"
}

live_session_clear_state() {
  rm -f "${LIVE_SESSION_STATE_FILE}"
}

live_session_targets_stopped() {
  local -n target_groups="$1"
  local -n target_pids="$2"
  local group pid
  for group in "${target_groups[@]}"; do
    if live_session_group_alive "${group}"; then
      return 1
    fi
  done
  for pid in "${target_pids[@]}"; do
    if live_session_pid_alive "${pid}"; then
      return 1
    fi
  done
}

live_session_wait_targets_stopped() {
  local groups_name="$1"
  local pids_name="$2"
  local _attempt
  for _attempt in 1 2 3 4 5 6 7 8 9 10; do
    if live_session_targets_stopped "${groups_name}" "${pids_name}"; then
      return 0
    fi
    sleep 0.2
  done
  live_session_targets_stopped "${groups_name}" "${pids_name}"
}

live_session_signal_targets() {
  local signal="$1"
  local -n target_groups="$2"
  local -n target_pids="$3"
  local group pid
  for group in "${target_groups[@]}"; do
    if live_session_group_alive "${group}"; then
      kill "-${signal}" -- "-${group}" 2>/dev/null || true
    fi
  done
  for pid in "${target_pids[@]}"; do
    if live_session_pid_alive "${pid}"; then
      kill "-${signal}" -- "${pid}" 2>/dev/null || true
    fi
  done
}

live_session_stop_targets() {
  local groups_name="$1"
  local pids_name="$2"
  local signal
  if live_session_targets_stopped "${groups_name}" "${pids_name}"; then
    return 0
  fi
  for signal in INT TERM KILL; do
    live_session_signal_targets "${signal}" "${groups_name}" "${pids_name}"
    if live_session_wait_targets_stopped "${groups_name}" "${pids_name}"; then
      return 0
    fi
  done
  return 1
}

live_session_stop_current() {
  local -a groups=()
  local -a pids=()
  if [[ -n "${LIVE_SESSION_DORA_PGID:-}" ]]; then
    groups+=("${LIVE_SESSION_DORA_PGID}")
  fi
  if [[ -n "${LIVE_SESSION_TTS_SERVER_PID:-}" ]]; then
    pids+=("${LIVE_SESSION_TTS_SERVER_PID}")
  fi
  live_session_stop_targets groups pids
}

live_session_collect_state_targets() {
  LIVE_SESSION_STATE_GROUPS=()
  LIVE_SESSION_STATE_PIDS=()
  if live_session_state_dora_alive && [[ -n "${FLUENT_DIALOGUE_DORA_RUN_DORA_PGID:-}" ]]; then
    LIVE_SESSION_STATE_GROUPS+=("${FLUENT_DIALOGUE_DORA_RUN_DORA_PGID}")
  fi
  if live_session_state_tts_alive; then
    LIVE_SESSION_STATE_PIDS+=("${FLUENT_DIALOGUE_DORA_RUN_TTS_SERVER_PID}")
  fi
  if live_session_state_root_alive; then
    LIVE_SESSION_STATE_PIDS+=("${FLUENT_DIALOGUE_DORA_RUN_ROOT_PID}")
  fi
  local current_pgid
  current_pgid="$(live_session_pgid "${BASHPID}")"
  if ((${#LIVE_SESSION_STATE_GROUPS[@]} == 0)) \
    && [[ -n "${FLUENT_DIALOGUE_DORA_RUN_ROOT_PGID:-}" ]] \
    && [[ "${FLUENT_DIALOGUE_DORA_RUN_ROOT_PGID}" != "${current_pgid}" ]] \
    && live_session_group_alive "${FLUENT_DIALOGUE_DORA_RUN_ROOT_PGID}"; then
    LIVE_SESSION_STATE_GROUPS+=("${FLUENT_DIALOGUE_DORA_RUN_ROOT_PGID}")
  fi
}

live_session_stop() {
  if ! live_session_load_state; then
    echo "stopped: ${LIVE_SESSION_STATE_FILE} not found"
    return 0
  fi
  if ! live_session_state_alive; then
    echo "stale state removed: ${LIVE_SESSION_STATE_FILE}"
    live_session_clear_state
    return 0
  fi
  live_session_collect_state_targets
  echo "stopping ${FLUENT_DIALOGUE_DORA_RUN_SESSION:-live session} from ${LIVE_SESSION_STATE_FILE}"
  if live_session_stop_targets LIVE_SESSION_STATE_GROUPS LIVE_SESSION_STATE_PIDS; then
    live_session_clear_state
    echo "stopped"
    return 0
  fi
  echo "failed to stop all recorded live-session processes; state retained: ${LIVE_SESSION_STATE_FILE}" >&2
  return 1
}

live_session_start_guard() {
  if ! live_session_load_state; then
    return 0
  fi
  if live_session_state_root_alive; then
    echo "already running: ${FLUENT_DIALOGUE_DORA_RUN_SESSION} root_pid=${FLUENT_DIALOGUE_DORA_RUN_ROOT_PID} web=http://127.0.0.1:${FLUENT_DIALOGUE_DORA_RUN_WEB_BRIDGE_PORT}/?session=${FLUENT_DIALOGUE_DORA_RUN_SESSION_ID}"
    return 75
  fi
  if live_session_state_alive; then
    echo "cleaning stale live-session processes from ${LIVE_SESSION_STATE_FILE}"
    live_session_stop || return $?
    return 0
  fi
  echo "stale state removed: ${LIVE_SESSION_STATE_FILE}"
  live_session_clear_state
}

live_session_status_vllm() {
  local base_url="$1"
  [[ -n "${base_url}" ]] || return 0
  if python - "${base_url}" <<'PY' >/dev/null 2>&1
from __future__ import annotations

import http.client
import os
import sys
import urllib.parse

url = urllib.parse.urlparse(sys.argv[1])
connection = http.client.HTTPConnection(url.hostname or "127.0.0.1", url.port or 80, timeout=1.0)
try:
    path = (url.path.rstrip("/") or "") + "/models"
    connection.request("GET", path, headers={"Authorization": f"Bearer {os.environ.get('VLLM_API_KEY', 'dummy')}"})
    response = connection.getresponse()
    response.read()
    if response.status != 200:
        raise SystemExit(1)
finally:
    connection.close()
PY
  then
    echo "vllm: up ${base_url} (external, not managed)"
  else
    echo "vllm: down ${base_url} (external, not managed)"
  fi
}

live_session_status() {
  if ! live_session_load_state; then
    echo "stopped: ${LIVE_SESSION_STATE_FILE} not found"
    return 0
  fi
  echo "state: ${LIVE_SESSION_STATE_FILE}"
  echo "session: ${FLUENT_DIALOGUE_DORA_RUN_SESSION:-unknown}"
  echo "session_id: ${FLUENT_DIALOGUE_DORA_RUN_SESSION_ID:-unknown}"
  echo "mode: ${FLUENT_DIALOGUE_DORA_RUN_MODE:-unknown}"
  echo "root: pid=${FLUENT_DIALOGUE_DORA_RUN_ROOT_PID:-} pgid=${FLUENT_DIALOGUE_DORA_RUN_ROOT_PGID:-} sid=${FLUENT_DIALOGUE_DORA_RUN_ROOT_SID:-} alive=$(live_session_state_root_alive && echo yes || echo no)"
  echo "dora: pid=${FLUENT_DIALOGUE_DORA_RUN_DORA_PID:-} pgid=${FLUENT_DIALOGUE_DORA_RUN_DORA_PGID:-} sid=${FLUENT_DIALOGUE_DORA_RUN_DORA_SID:-} alive=$(live_session_state_dora_alive && echo yes || echo no)"
  echo "tts: pid=${FLUENT_DIALOGUE_DORA_RUN_TTS_SERVER_PID:-} port=${FLUENT_DIALOGUE_DORA_RUN_TTS_PORT:-} alive=$(live_session_state_tts_alive && echo yes || echo no)"
  echo "web: http://127.0.0.1:${FLUENT_DIALOGUE_DORA_RUN_WEB_BRIDGE_PORT:-}/?session=${FLUENT_DIALOGUE_DORA_RUN_SESSION_ID:-}"
  echo "codex_control_port: ${FLUENT_DIALOGUE_DORA_RUN_CODEX_CONTROL_PORT:-}"
  echo "dataflow: ${FLUENT_DIALOGUE_DORA_RUN_DATAFLOW:-}"
  echo "runtime_log: ${FLUENT_DIALOGUE_DORA_RUN_RUNTIME_LOG:-}"
  if ! live_session_state_alive; then
    echo "status: stale"
  else
    echo "status: running"
  fi
  live_session_status_vllm "${FLUENT_DIALOGUE_DORA_RUN_VLLM_BASE_URL:-}"
}

live_session_run_dora() {
  if ! command -v setsid >/dev/null; then
    echo "missing required command: setsid" >&2
    return 127
  fi
  setsid "$@" &
  LIVE_SESSION_DORA_PID="$!"
  LIVE_SESSION_DORA_PGID="$(live_session_pgid "${LIVE_SESSION_DORA_PID}")"
  LIVE_SESSION_DORA_SID="$(live_session_sid "${LIVE_SESSION_DORA_PID}")"
  live_session_write_state
  wait "${LIVE_SESSION_DORA_PID}"
}

live_session_self_check() {
  local tmp
  tmp="$(mktemp -d)"
  LIVE_SESSION_STATE_FILE="${tmp}/run.env"
  LIVE_SESSION_NAME="self-check"
  LIVE_SESSION_ID="self-check-session"
  LIVE_SESSION_MODE="--run"
  LIVE_SESSION_DORA_PID=""
  LIVE_SESSION_DORA_PGID=""
  LIVE_SESSION_DORA_SID=""
  LIVE_SESSION_TTS_SERVER_PID=""
  LIVE_SESSION_TTS_SERVER_PGID=""
  LIVE_SESSION_TTS_SERVER_SID=""
  LIVE_SESSION_WEB_BRIDGE_PORT="18000"
  LIVE_SESSION_CODEX_CONTROL_PORT="18100"
  LIVE_SESSION_TTS_PORT="18200"
  LIVE_SESSION_DATAFLOW="${tmp}/graph.yml"
  LIVE_SESSION_RUNTIME_LOG="${tmp}/runtime.log"
  LIVE_SESSION_VLLM_BASE_URL="http://127.0.0.1:18080/v1"
  live_session_write_state
  live_session_load_state
  [[ "${FLUENT_DIALOGUE_DORA_RUN_SESSION}" == "self-check" ]]
  [[ "${FLUENT_DIALOGUE_DORA_RUN_WEB_BRIDGE_PORT}" == "18000" ]]
  live_session_clear_state
  rmdir "${tmp}"
  echo "live_session_lifecycle self-check: ok"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  case "${1:-}" in
    --self-check)
      live_session_self_check
      ;;
    *)
      echo "usage: $0 --self-check" >&2
      exit 64
      ;;
  esac
fi
