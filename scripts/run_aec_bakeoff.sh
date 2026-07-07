#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

RUN_DIR="${FLUENT_DIALOGUE_DORA_AEC_BAKEOFF_DIR:-artifacts/aec_bakeoff/$(date +%Y%m%d-%H%M%S)}"
DELAY_MS="${FLUENT_DIALOGUE_DORA_AEC_BAKEOFF_DELAY_MS:-80}"
AEC_BACKEND="${FLUENT_DIALOGUE_DORA_AEC_BACKEND:-webrtc}"
STIMULUS_TEXT="${FLUENT_DIALOGUE_DORA_AEC_STIMULUS_TEXT:-こんにちは。これはエコーキャンセル評価用の読み上げ音声です。マイクがこれを発話として検知するか確認します。}"
STIMULUS_GAIN="${FLUENT_DIALOGUE_DORA_AEC_STIMULUS_GAIN:-0.55}"
VAD_THRESHOLD="${FLUENT_DIALOGUE_DORA_AEC_VAD_THRESHOLD:-0.5}"
BARGE_IN_SPEECH_FRAMES="${FLUENT_DIALOGUE_DORA_BARGE_IN_SPEECH_FRAMES:-4800}"
BARGE_IN_SILENCE_RESET_FRAMES="${FLUENT_DIALOGUE_DORA_BARGE_IN_SILENCE_RESET_FRAMES:-2048}"

mkdir -p "${RUN_DIR}"

set +e
FLUENT_DIALOGUE_DORA_AEC_STREAM_DELAY_MS="${DELAY_MS}" \
  FLUENT_DIALOGUE_DORA_AEC_BACKEND="${AEC_BACKEND}" \
  scripts/run_aec_hardware_validation.sh \
  >"${RUN_DIR}/capture_and_${AEC_BACKEND}.log" 2>&1
validation_rc=$?
set -e

for path in stimulus_48k_stereo.s16le near_16k_mono.s16le aec_16k_mono.s16le report.json; do
  if [ -f "artifacts/aec_hardware_validation/${path}" ]; then
    cp "artifacts/aec_hardware_validation/${path}" "${RUN_DIR}/${path}"
  fi
done

if [ ! -f "${RUN_DIR}/stimulus_48k_stereo.s16le" ] \
  || [ ! -f "${RUN_DIR}/near_16k_mono.s16le" ] \
  || [ ! -f "${RUN_DIR}/aec_16k_mono.s16le" ]; then
  echo "AEC bakeoff capture did not produce required PCM artifacts" >&2
  tail -n 80 "${RUN_DIR}/capture_and_${AEC_BACKEND}.log" >&2 || true
  exit 1
fi

uv run --extra vad python tools/aec_eval/analyze_pair.py \
  --candidate-name no_aec \
  --reference-near "${RUN_DIR}/near_16k_mono.s16le" \
  --candidate "${RUN_DIR}/near_16k_mono.s16le" \
  --far-stimulus "${RUN_DIR}/stimulus_48k_stereo.s16le" \
  --output "${RUN_DIR}/no_aec.report.json" \
  --stream-delay-ms none \
  --stimulus-text "${STIMULUS_TEXT}" \
  --stimulus-gain "${STIMULUS_GAIN}" \
  --vad-threshold "${VAD_THRESHOLD}" \
  --barge-in-speech-frames "${BARGE_IN_SPEECH_FRAMES}" \
  --barge-in-silence-reset-frames "${BARGE_IN_SILENCE_RESET_FRAMES}" \
  >"${RUN_DIR}/no_aec.analyze.log"

uv run --extra vad python tools/aec_eval/analyze_pair.py \
  --candidate-name "${AEC_BACKEND}_aec3" \
  --reference-near "${RUN_DIR}/near_16k_mono.s16le" \
  --candidate "${RUN_DIR}/aec_16k_mono.s16le" \
  --far-stimulus "${RUN_DIR}/stimulus_48k_stereo.s16le" \
  --output "${RUN_DIR}/${AEC_BACKEND}_aec3.report.json" \
  --stream-delay-ms "${DELAY_MS}" \
  --stimulus-text "${STIMULUS_TEXT}" \
  --stimulus-gain "${STIMULUS_GAIN}" \
  --vad-threshold "${VAD_THRESHOLD}" \
  --barge-in-speech-frames "${BARGE_IN_SPEECH_FRAMES}" \
  --barge-in-silence-reset-frames "${BARGE_IN_SILENCE_RESET_FRAMES}" \
  >"${RUN_DIR}/${AEC_BACKEND}_aec3.analyze.log"

python - "${validation_rc}" "${RUN_DIR}" "${AEC_BACKEND}" <<'PY'
import json
import sys
from pathlib import Path

validation_rc = sys.argv[1]
run_dir = Path(sys.argv[2])
backend = sys.argv[3]
summary = run_dir / "summary.tsv"
reports = [run_dir / "no_aec.report.json", run_dir / f"{backend}_aec3.report.json"]
with summary.open("w", encoding="utf-8") as f:
    f.write(
        "candidate\toverall_pass\techo_reduction_db\trms_attenuation_db\t"
        "candidate_vad\tcandidate_ratio\tcandidate_max_run\tbarge_in_fires\t"
        "max_probability\treport\n"
    )
    for path in reports:
        report = json.loads(path.read_text(encoding="utf-8"))
        f.write(
            "\t".join(
                [
                    report["candidate_name"],
                    str(int(report["passed"]["overall"])),
                    f"{report['rms']['baseline_subtracted_echo_reduction_db']:.3f}",
                    f"{report['rms']['rms_attenuation_db']:.3f}",
                    str(report["vad"]["candidate"]["speech_events"]),
                    f"{report['vad']['candidate_speech_event_ratio']:.3f}",
                    str(report["vad"]["candidate"]["max_contiguous_speech_events"]),
                    str(report["vad"]["candidate"]["simulated_barge_in_count"]),
                    f"{report['vad']['candidate']['max_speech_probability']:.3f}",
                    str(path),
                ]
            )
            + "\n"
        )
print(f"validation_rc={validation_rc}")
print(f"summary={summary}")
print(summary.read_text(encoding="utf-8"), end="")
PY
