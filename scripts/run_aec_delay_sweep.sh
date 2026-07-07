#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

OUT="artifacts/aec_hardware_validation/sweep"
AEC_BACKEND="${FLUENT_DIALOGUE_DORA_AEC_BACKEND:-webrtc}"
SUMMARY="${OUT}/${AEC_BACKEND}_summary.tsv"
mkdir -p "${OUT}"

if [ "$#" -gt 0 ]; then
  DELAYS=("$@")
else
  DELAYS=(0 40 80 100 120 auto)
fi

printf "backend\tdelay_ms\trc\techo_reduction_db\trms_attenuation_db\tnear_vad\taec_vad\taec_ratio\taec_max_run\taec_detector_fires\taec_max_probability\treport\n" >"${SUMMARY}"

for delay in "${DELAYS[@]}"; do
  safe_delay="${delay//[^A-Za-z0-9_.-]/_}"
  log_path="${OUT}/${AEC_BACKEND}_delay_${safe_delay}.log"
  report_path="${OUT}/${AEC_BACKEND}_report_${safe_delay}.json"
  echo "=== FLUENT_DIALOGUE_DORA_AEC_BACKEND=${AEC_BACKEND} FLUENT_DIALOGUE_DORA_AEC_STREAM_DELAY_MS=${delay} ==="
  set +e
  FLUENT_DIALOGUE_DORA_AEC_STREAM_DELAY_MS="${delay}" scripts/run_aec_hardware_validation.sh >"${log_path}" 2>&1
  rc=$?
  set -e
  if [ -f artifacts/aec_hardware_validation/report.json ]; then
    cp artifacts/aec_hardware_validation/report.json "${report_path}"
    python - "${AEC_BACKEND}" "${delay}" "${rc}" "${report_path}" >>"${SUMMARY}" <<'PY'
import json
import sys
from pathlib import Path

backend = sys.argv[1]
delay = sys.argv[2]
rc = sys.argv[3]
report_path = Path(sys.argv[4])
report = json.loads(report_path.read_text(encoding="utf-8"))
vad = report["vad"]
rms = report["rms"]
row = [
    backend,
    delay,
    rc,
    f"{rms['baseline_subtracted_echo_reduction_db']:.3f}",
    f"{rms['rms_attenuation_db']:.3f}",
    str(vad["reference"]["speech_events"]),
    str(vad["candidate"]["speech_events"]),
    f"{vad['candidate_speech_event_ratio']:.3f}",
    str(vad["candidate"]["max_contiguous_speech_events"]),
    str(vad["candidate"]["simulated_barge_in_count"]),
    f"{vad['candidate']['max_speech_probability']:.3f}",
    str(report_path),
]
print("\t".join(row))
PY
  else
    printf "%s\t%s\t%s\tNA\tNA\tNA\tNA\tNA\tNA\tNA\tNA\t%s\n" "${AEC_BACKEND}" "${delay}" "${rc}" "${log_path}" >>"${SUMMARY}"
  fi
  tail -n 12 "${log_path}" || true
done

echo "summary=${SUMMARY}"
