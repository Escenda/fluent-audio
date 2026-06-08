#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: dora_cargo_build.sh <Cargo.toml>" >&2
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

cargo build --manifest-path "$1"
