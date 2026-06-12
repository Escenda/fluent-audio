#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "${REPO_ROOT}"
uvx --from dora-rs-cli dora run graphs/codex_app_server_fixture_turn_smoke.yml --uv
