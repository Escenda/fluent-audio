#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
usage: scripts/bootstrap_dev_env.sh [--no-system] [--models] [--verify]

Installs the local development environment for fluent-dialogue-dora.

  --no-system   skip apt packages
  --models      download local model weights
  --verify      run representative checks after install
USAGE
}

install_system=1
download_models=0
verify=0
for arg in "$@"; do
  case "$arg" in
    --no-system) install_system=0 ;;
    --models) download_models=1 ;;
    --verify) verify=1 ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 64
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$REPO_ROOT"

if [[ "$install_system" -eq 1 ]]; then
  if ! command -v apt-get >/dev/null 2>&1; then
    echo "apt-get not found; rerun with --no-system and install OS deps manually" >&2
    exit 1
  fi
  sudo apt-get update
  sudo apt-get install -y \
    alsa-utils \
    build-essential \
    ca-certificates \
    clang \
    cmake \
    curl \
    espeak-ng \
    git \
    gir1.2-gstreamer-1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-tools \
    libasound2-dev \
    libclang-dev \
    ninja-build \
    nodejs \
    npm \
    pipewire-bin \
    pkg-config \
    protobuf-compiler \
    python3 \
    python3-gi \
    python3-gst-1.0 \
    python3-venv
fi

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="${HOME}/.local/bin:${PATH}"
fi

if ! command -v cargo >/dev/null 2>&1; then
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal
  # shellcheck disable=SC1091
  source "${CARGO_HOME:-$HOME/.cargo}/env"
fi

if [[ -z "${LIBCLANG_PATH:-}" ]]; then
  libclang="$(find /usr/lib /lib /opt -name 'libclang.so*' 2>/dev/null | sort | head -n 1 || true)"
  if [[ -n "$libclang" ]]; then
    export LIBCLANG_PATH="$(dirname "$libclang")"
  fi
fi

uv sync --all-extras
npm install --prefix contracts/typescript

if [[ "$download_models" -eq 1 ]]; then
  uv run python scripts/download_models.py
fi

if [[ "$verify" -eq 1 ]]; then
  uv run python -m pytest tests
  npm run --prefix contracts/typescript typecheck
  cargo check --manifest-path contracts/rust/Cargo.toml --locked
  cargo check --manifest-path nodes/audio_device/rust_audio_boundary/Cargo.toml --locked
  cargo check --manifest-path nodes/audio_device/cpal_capture/Cargo.toml --locked
  cargo check --manifest-path nodes/audio_device/cpal_sink/Cargo.toml --locked
  cargo check --manifest-path nodes/audio_device/barge_in_aec/Cargo.toml --locked
fi

echo "bootstrap complete"
