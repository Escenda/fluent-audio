#!/usr/bin/env bash
set -euo pipefail

release_flag=()
if [[ "${1:-}" == "--release" ]]; then
  release_flag=(--release)
  shift
fi

if [[ $# -ne 1 ]]; then
  echo "usage: dora_cargo_build.sh [--release] <Cargo.toml>" >&2
  exit 64
fi

if ! command -v cargo >/dev/null 2>&1; then
  cargo_env="${CARGO_HOME:-$HOME/.cargo}/env"
  if [[ -r "$cargo_env" ]]; then
    # shellcheck disable=SC1090
    source "$cargo_env"
  fi
fi

if ! command -v cargo >/dev/null 2>&1; then
  echo "cargo is not available on PATH and ${CARGO_HOME:-$HOME/.cargo}/env is not readable" >&2
  exit 127
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOCAL_LIBCLANG="${REPO_ROOT}/artifacts/build_deps/libclang/clang/native/libclang.so"
if [[ -z "${LIBCLANG_PATH:-}" && -f "${LOCAL_LIBCLANG}" ]]; then
  export LIBCLANG_PATH="$(dirname "${LOCAL_LIBCLANG}")"
fi

if [[ -z "${BINDGEN_EXTRA_CLANG_ARGS:-}" ]]; then
  export BINDGEN_EXTRA_CLANG_ARGS="-I/usr/lib/gcc/aarch64-linux-gnu/13/include -I/usr/include/aarch64-linux-gnu -I/usr/include"
fi

cargo build "${release_flag[@]}" --manifest-path "$1"
