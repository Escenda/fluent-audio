#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TTS_PYOPENJTALK_PORT="${TTS_PYOPENJTALK_PORT:-18097}"

cd "${REPO_ROOT}"

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

TTS_SERVER_PID=""
cleanup() {
  if [[ -n "${TTS_SERVER_PID}" ]] && kill -0 "${TTS_SERVER_PID}" 2>/dev/null; then
    kill "${TTS_SERVER_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT

uv run --extra dev --extra dora --extra tts python nodes/tts/tts_pyopenjtalk_server/main.py \
  --port "${TTS_PYOPENJTALK_PORT}" \
  --openjtalk-dict-dir "${OPENJTALK_DICT_DIR}" \
  --audio-source-id tts_pyopenjtalk \
  --audio-stream-id tts/pyopenjtalk \
  --chunk-frames 12000 &
TTS_SERVER_PID="$!"

python - "${TTS_PYOPENJTALK_PORT}" <<'PY'
from __future__ import annotations

import http.client
import sys
import time

port = int(sys.argv[1])
deadline = time.monotonic() + 10.0
last_error = ""
while time.monotonic() < deadline:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=0.2)
    try:
        connection.request("GET", "/health")
        response = connection.getresponse()
        response.read()
        if response.status == 200:
            raise SystemExit(0)
        last_error = f"HTTP {response.status}"
    except OSError as exc:
        last_error = str(exc)
    finally:
        connection.close()
    time.sleep(0.05)
raise SystemExit(f"PyOpenJTalk server on port {port} did not become ready: {last_error}")
PY

uvx --from dora-rs-cli dora run graphs/tts_pyopenjtalk_cpal_smoke.yml --uv
