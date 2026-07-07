#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DEFAULT_CURRENT_PYTHON="${REPO_ROOT}/../daihen-physical-ai.audio/data/builds/envs/codex_vllm/current/venv/bin/python"

VLLM_PYTHON="${FLUENT_DIALOGUE_DORA_CODEX_VLLM_PYTHON:-}"
if [[ -z "${VLLM_PYTHON}" ]]; then
  if [[ -x "${DEFAULT_CURRENT_PYTHON}" ]]; then
    VLLM_PYTHON="${DEFAULT_CURRENT_PYTHON}"
  else
    echo "missing codex_vllm python; set FLUENT_DIALOGUE_DORA_CODEX_VLLM_PYTHON" >&2
    exit 66
  fi
fi

if [[ ! -x "${VLLM_PYTHON}" ]]; then
  echo "codex_vllm python is not executable: ${VLLM_PYTHON}" >&2
  exit 66
fi

VLLM_BIN_DIR="$(cd "$(dirname "${VLLM_PYTHON}")" && pwd)"
export PATH="${VLLM_BIN_DIR}:${PATH}"

HOST="${FLUENT_DIALOGUE_DORA_VLLM_HOST:-127.0.0.1}"
PORT="${FLUENT_DIALOGUE_DORA_VLLM_PORT:-18080}"
DEFAULT_MODEL="${REPO_ROOT}/data/models/fluent_dialogue_dora/Qwen3.6-27B-MTP-pi-tune-NVFP4"
MODEL="${FLUENT_DIALOGUE_DORA_VLLM_MODEL:-${DEFAULT_MODEL}}"
SERVED_MODEL_NAME="${FLUENT_DIALOGUE_DORA_VLLM_SERVED_MODEL_NAME:-qwen3.6-27b-mtp-pi-tune-nvfp4}"
MAX_MODEL_LEN="${FLUENT_DIALOGUE_DORA_VLLM_MAX_MODEL_LEN:-131072}"
MAX_NUM_SEQS="${FLUENT_DIALOGUE_DORA_VLLM_MAX_NUM_SEQS:-1}"
MAX_NUM_BATCHED_TOKENS="${FLUENT_DIALOGUE_DORA_VLLM_MAX_NUM_BATCHED_TOKENS:-8192}"
KV_CACHE_MEMORY_BYTES="${FLUENT_DIALOGUE_DORA_VLLM_KV_CACHE_MEMORY_BYTES:-9G}"
GPU_MEMORY_UTILIZATION="${FLUENT_DIALOGUE_DORA_VLLM_GPU_MEMORY_UTILIZATION:-0.18}"
TOOL_CALL_PARSER="${FLUENT_DIALOGUE_DORA_VLLM_TOOL_CALL_PARSER:-qwen3_xml}"
REASONING_PARSER="${FLUENT_DIALOGUE_DORA_VLLM_REASONING_PARSER:-}"
DEFAULT_LIMIT_MM_PER_PROMPT='{"image":0,"video":0}'
LIMIT_MM_PER_PROMPT="${FLUENT_DIALOGUE_DORA_VLLM_LIMIT_MM_PER_PROMPT:-${DEFAULT_LIMIT_MM_PER_PROMPT}}"
SPECULATIVE_CONFIG="${FLUENT_DIALOGUE_DORA_VLLM_SPECULATIVE_CONFIG:-}"
CHAT_TEMPLATE="${FLUENT_DIALOGUE_DORA_VLLM_CHAT_TEMPLATE:-${REPO_ROOT}/scripts/qwen3_codex_responses_chat_template.jinja}"

extra_args=()
if [[ ! -f "${CHAT_TEMPLATE}" ]]; then
  echo "missing vLLM chat template: ${CHAT_TEMPLATE}" >&2
  exit 66
fi
if [[ "${MODEL}" == "${DEFAULT_MODEL}" && ! -d "${MODEL}" ]]; then
  echo "missing local LLM model: ${MODEL}; run scripts/bootstrap_dev_env.sh --models or set FLUENT_DIALOGUE_DORA_VLLM_MODEL" >&2
  exit 66
fi
extra_args+=(--chat-template "${CHAT_TEMPLATE}")
if [[ -n "${REASONING_PARSER}" ]]; then
  extra_args+=(--reasoning-parser "${REASONING_PARSER}")
fi
if [[ -n "${LIMIT_MM_PER_PROMPT}" ]]; then
  extra_args+=(--limit-mm-per-prompt "${LIMIT_MM_PER_PROMPT}")
fi
if [[ -n "${SPECULATIVE_CONFIG}" ]]; then
  extra_args+=(--speculative-config "${SPECULATIVE_CONFIG}")
fi

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
  "${extra_args[@]}" \
  "$@"
