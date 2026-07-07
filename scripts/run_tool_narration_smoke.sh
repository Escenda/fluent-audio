#!/usr/bin/env bash
# ツール実行前ナレーションのタイミング検証 (docs/課題/voice-dialogue-quality.md 課題2)
#
# fixture codex が「プリアンブル文 → tool started → 4秒待ち → tool completed →
# 結びの文 → turn completed」を流し、プリアンブル音声の再生開始(playing)が
# tool completed より前に起きることを ros2 projection のタイムスタンプで検証する。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

TTS_FIXTURE_PORT="${TTS_FIXTURE_PORT:-18082}"

cd "${REPO_ROOT}"
mkdir -p artifacts/tool_narration
rm -f artifacts/tool_narration/ros2_projection.jsonl

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

uvx --from dora-rs-cli dora run graphs/tool_narration_fixture_smoke.yml --uv

python3 - artifacts/tool_narration/ros2_projection.jsonl <<'PY'
from __future__ import annotations

import json
import sys

events = []
for line in open(sys.argv[1], encoding="utf-8"):
    if not line.strip():
        continue
    row = json.loads(line)
    payload = json.loads(row["payload_json"])
    stamp = payload.get("header", {}).get("stamp")
    if stamp is None:
        continue
    timestamp_s = stamp["sec"] + stamp["nanosec"] / 1e9
    events.append((timestamp_s, row["topic"], payload))

events.sort(key=lambda item: item[0])
if not events:
    raise SystemExit("FAIL: projection jsonl is empty")
# transcript_replay は stamp 0 で投入されるため、実時刻を持つ最初のイベントを基準にする
real_stamps = [ts for ts, _, _ in events if ts > 1e6]
origin_s = real_stamps[0] if real_stamps else events[0][0]

first_text_s = None
tool_started_s = None
tool_completed_s = None
first_playing_s = None
playing_before_tool_done = 0

print("=== timeline (relative seconds) ===")
for timestamp_s, topic, payload in events:
    relative_s = timestamp_s - origin_s
    if topic == "agent_text" and first_text_s is None:
        first_text_s = timestamp_s
        print(f"{relative_s:7.3f}s agent_text first delta: {payload.get('text', '')!r}")
    elif topic == "agent_tool":
        event_kind = payload.get("event")
        print(f"{relative_s:7.3f}s agent_tool {event_kind} ({payload.get('tool_name')})")
        if event_kind == "started" and tool_started_s is None:
            tool_started_s = timestamp_s
        if event_kind == "completed" and tool_completed_s is None:
            tool_completed_s = timestamp_s
    elif topic == "playback_state":
        state = payload.get("state")
        if state == "playing":
            if first_playing_s is None:
                first_playing_s = timestamp_s
                print(f"{relative_s:7.3f}s playback_state playing (request {payload.get('request_id')})")
            if tool_completed_s is None:
                playing_before_tool_done += 1

print("\n=== verdict ===")
if first_playing_s is None:
    raise SystemExit("FAIL: no playback_state playing event observed")
if tool_completed_s is None:
    raise SystemExit("FAIL: no agent_tool completed event observed")
margin_s = tool_completed_s - first_playing_s
print(f"first playing: {first_playing_s - origin_s:.3f}s")
print(f"tool completed: {tool_completed_s - origin_s:.3f}s")
print(f"margin (tool_completed - first_playing): {margin_s:.3f}s")
print(f"playing events before tool completion: {playing_before_tool_done}")
if margin_s <= 0:
    raise SystemExit("FAIL: preamble playback did not start before tool completion")
print("PASS: preamble audio started playing before the tool call completed")
PY

cleanup
TTS_PID=""
