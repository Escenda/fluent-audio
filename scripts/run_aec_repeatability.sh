#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

AEC_BACKEND="${FLUENT_DIALOGUE_DORA_AEC_BACKEND:-webrtc}"
DELAY_MS="${FLUENT_DIALOGUE_DORA_AEC_STREAM_DELAY_MS:-40}"
RUNS="${FLUENT_DIALOGUE_DORA_AEC_REPEATABILITY_RUNS:-3}"
OUT="${FLUENT_DIALOGUE_DORA_AEC_REPEATABILITY_DIR:-artifacts/aec_repeatability/${AEC_BACKEND}_${DELAY_MS}_$(date +%Y%m%d-%H%M%S)}"
SUMMARY="${OUT}/summary.tsv"

if ! [[ "${RUNS}" =~ ^[1-9][0-9]*$ ]]; then
  echo "FLUENT_DIALOGUE_DORA_AEC_REPEATABILITY_RUNS must be a positive integer" >&2
  exit 64
fi

mkdir -p "${OUT}"
printf "run\trc\toverall_pass\techo_reduction_db\trms_attenuation_db\tcandidate_vad\tcandidate_ratio\tcandidate_max_run\tbarge_in_fires\tmax_probability\treport\n" >"${SUMMARY}"

for run in $(seq 1 "${RUNS}"); do
  log_path="${OUT}/run_${run}.log"
  report_path="${OUT}/run_${run}.report.json"
  echo "=== run ${run}/${RUNS}: backend=${AEC_BACKEND} delay_ms=${DELAY_MS} ==="
  set +e
  FLUENT_DIALOGUE_DORA_AEC_BACKEND="${AEC_BACKEND}" \
    FLUENT_DIALOGUE_DORA_AEC_STREAM_DELAY_MS="${DELAY_MS}" \
    scripts/run_aec_hardware_validation.sh >"${log_path}" 2>&1
  rc=$?
  set -e
  if [ -f artifacts/aec_hardware_validation/report.json ]; then
    cp artifacts/aec_hardware_validation/report.json "${report_path}"
    python - "${run}" "${rc}" "${report_path}" >>"${SUMMARY}" <<'PY'
import json
import sys
from pathlib import Path

run = sys.argv[1]
rc = sys.argv[2]
report_path = Path(sys.argv[3])
report = json.loads(report_path.read_text(encoding="utf-8"))
row = [
    run,
    rc,
    str(int(report["passed"]["overall"])),
    f"{report['rms']['baseline_subtracted_echo_reduction_db']:.3f}",
    f"{report['rms']['rms_attenuation_db']:.3f}",
    str(report["vad"]["candidate"]["speech_events"]),
    f"{report['vad']['candidate_speech_event_ratio']:.3f}",
    str(report["vad"]["candidate"]["max_contiguous_speech_events"]),
    str(report["vad"]["candidate"]["simulated_barge_in_count"]),
    f"{report['vad']['candidate']['max_speech_probability']:.3f}",
    str(report_path),
]
print("\t".join(row))
PY
  else
    printf "%s\t%s\t0\tNA\tNA\tNA\tNA\tNA\tNA\tNA\t%s\n" "${run}" "${rc}" "${log_path}" >>"${SUMMARY}"
  fi
  tail -n 12 "${log_path}" || true
done

echo "summary=${SUMMARY}"
