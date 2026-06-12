#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DEFAULT_CURRENT_PYTHON="${REPO_ROOT}/../daihen-physical-ai.audio/data/builds/envs/codex_vllm/current/venv/bin/python"

VLLM_PYTHON="${FLUENT_AUDIO_CODEX_VLLM_PYTHON:-}"
if [[ -z "${VLLM_PYTHON}" ]]; then
  if [[ -x "${DEFAULT_CURRENT_PYTHON}" ]]; then
    VLLM_PYTHON="${DEFAULT_CURRENT_PYTHON}"
  else
    echo "missing codex_vllm python; set FLUENT_AUDIO_CODEX_VLLM_PYTHON" >&2
    exit 66
  fi
fi

if [[ ! -x "${VLLM_PYTHON}" ]]; then
  echo "codex_vllm python is not executable: ${VLLM_PYTHON}" >&2
  exit 66
fi

VLLM_BIN_DIR="$(cd "$(dirname "${VLLM_PYTHON}")" && pwd)"
export PATH="${VLLM_BIN_DIR}:${PATH}"

HOST="${FLUENT_AUDIO_VLLM_HOST:-127.0.0.1}"
PORT="${FLUENT_AUDIO_VLLM_PORT:-18080}"
MODEL="${FLUENT_AUDIO_VLLM_MODEL:-NVFP4/Qwen3-Coder-30B-A3B-Instruct-FP4}"
SERVED_MODEL_NAME="${FLUENT_AUDIO_VLLM_SERVED_MODEL_NAME:-qwen3-coder-30b-a3b-nvfp4}"
MAX_MODEL_LEN="${FLUENT_AUDIO_VLLM_MAX_MODEL_LEN:-131072}"
MAX_NUM_SEQS="${FLUENT_AUDIO_VLLM_MAX_NUM_SEQS:-1}"
MAX_NUM_BATCHED_TOKENS="${FLUENT_AUDIO_VLLM_MAX_NUM_BATCHED_TOKENS:-131072}"
KV_CACHE_MEMORY_BYTES="${FLUENT_AUDIO_VLLM_KV_CACHE_MEMORY_BYTES:-7G}"
GPU_MEMORY_UTILIZATION="${FLUENT_AUDIO_VLLM_GPU_MEMORY_UTILIZATION:-0.18}"
TOOL_CALL_PARSER="${FLUENT_AUDIO_VLLM_TOOL_CALL_PARSER:-hermes}"

exec "${VLLM_PYTHON}" \
  -m vllm.entrypoints.openai.api_server \
  --host "${HOST}" \
  --port "${PORT}" \
  --model "${MODEL}" \
  --served-model-name "${SERVED_MODEL_NAME}" \
  --enable-auto-tool-choice \
  --tool-call-parser "${TOOL_CALL_PARSER}" \
  --max-model-len "${MAX_MODEL_LEN}" \
  --max-num-seqs "${MAX_NUM_SEQS}" \
  --max-num-batched-tokens "${MAX_NUM_BATCHED_TOKENS}" \
  --kv-cache-memory-bytes "${KV_CACHE_MEMORY_BYTES}" \
  --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}" \
  --enforce-eager \
  "$@"
