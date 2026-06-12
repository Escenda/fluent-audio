#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

TTS_FIXTURE_PORT="${TTS_FIXTURE_PORT:-18082}"

cd "${REPO_ROOT}"
mkdir -p artifacts/dialogue_to_cpal
rm -f artifacts/dialogue_to_cpal/ros2_projection.jsonl

TTS_PID=""

cleanup() {
  if [[ -n "${TTS_PID}" ]] && kill -0 "${TTS_PID}" 2>/dev/null; then
    kill "${TTS_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT

uv run --extra dev --extra dora python tests/fixtures/http/tts_backend_fixture.py \
  --port "${TTS_FIXTURE_PORT}" \
  --audio-file tests/fixtures/cpal/silence_48k_stereo_250ms.s16le \
  --sample-rate-hz 48000 \
  --channels 2 \
  --sample-format s16le \
  --channel-layout interleaved \
  --audio-source-id tts_fixture \
  --audio-stream-id tts/fixture/smoke \
  --expected-requests 2 &
TTS_PID="$!"

python - "${TTS_FIXTURE_PORT}" <<'PY'
from __future__ import annotations

import http.client
import sys
import time


def wait_for_port(port: int) -> None:
    deadline = time.monotonic() + 5.0
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
    raise SystemExit(f"fixture server on port {port} did not become ready: {last_error}")


wait_for_port(int(sys.argv[1]))
PY

DIALOGUE_TO_CPAL_DATAFLOW="${DIALOGUE_TO_CPAL_DATAFLOW:-graphs/dialogue_to_cpal_smoke.yml}"
uvx --from dora-rs-cli dora run "${DIALOGUE_TO_CPAL_DATAFLOW}" --uv

wait "${TTS_PID}"
TTS_PID=""
