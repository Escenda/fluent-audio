#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

OUT="artifacts/aec_hardware_validation"
GRAPH="graphs/out/aec_hardware_validation.yml"
STIM="${OUT}/stimulus_48k_stereo.s16le"
NEAR="${OUT}/near_16k_mono.s16le"
AEC="${OUT}/aec_16k_mono.s16le"
REPORT="${OUT}/report.json"
AEC_STREAM_DELAY_MS="${FLUENT_DIALOGUE_DORA_AEC_STREAM_DELAY_MS:-120}"
AEC_BACKEND="${FLUENT_DIALOGUE_DORA_AEC_BACKEND:-webrtc}"
SPEAKER_DEVICE_ID="${FLUENT_DIALOGUE_DORA_AEC_SPEAKER_DEVICE_ID:-alsa:hw:CARD=S3,DEV=0}"
MIC_DEVICE_ID="${FLUENT_DIALOGUE_DORA_AEC_MIC_DEVICE_ID:-alsa:plughw:CARD=Rx,DEV=0}"
STIMULUS_TEXT="${FLUENT_DIALOGUE_DORA_AEC_STIMULUS_TEXT:-こんにちは。これはエコーキャンセル評価用の読み上げ音声です。マイクがこれを発話として検知するか確認します。}"
STIMULUS_GAIN="${FLUENT_DIALOGUE_DORA_AEC_STIMULUS_GAIN:-0.55}"
VAD_THRESHOLD="${FLUENT_DIALOGUE_DORA_AEC_VAD_THRESHOLD:-0.5}"
MAX_AEC_SPEECH_RATIO="${FLUENT_DIALOGUE_DORA_AEC_MAX_VAD_SPEECH_RATIO:-0.25}"
MAX_AEC_CONTIGUOUS_SPEECH_EVENTS="${FLUENT_DIALOGUE_DORA_AEC_MAX_CONTIGUOUS_SPEECH_EVENTS:-9}"
BARGE_IN_SPEECH_FRAMES="${FLUENT_DIALOGUE_DORA_BARGE_IN_SPEECH_FRAMES:-4800}"
BARGE_IN_SILENCE_RESET_FRAMES="${FLUENT_DIALOGUE_DORA_BARGE_IN_SILENCE_RESET_FRAMES:-2048}"
mkdir -p "${OUT}" graphs/out

if [[ "${AEC_STREAM_DELAY_MS}" == "auto" ]]; then
  AEC_STREAM_DELAY_ARGS=""
elif [[ "${AEC_STREAM_DELAY_MS}" =~ ^[0-9]+$ ]]; then
  AEC_STREAM_DELAY_ARGS="--stream-delay-ms ${AEC_STREAM_DELAY_MS}"
else
  echo "FLUENT_DIALOGUE_DORA_AEC_STREAM_DELAY_MS must be an integer millisecond value or auto" >&2
  exit 64
fi
if [[ "${AEC_BACKEND}" != "webrtc" && "${AEC_BACKEND}" != "sonora" ]]; then
  echo "FLUENT_DIALOGUE_DORA_AEC_BACKEND must be webrtc or sonora" >&2
  exit 64
fi
if [[ "${AEC_BACKEND}" == "sonora" && "${AEC_STREAM_DELAY_MS}" == "auto" ]]; then
  echo "FLUENT_DIALOGUE_DORA_AEC_STREAM_DELAY_MS=auto is only valid for the webrtc backend" >&2
  exit 64
fi
if ! [[ "${BARGE_IN_SPEECH_FRAMES}" =~ ^[0-9]+$ ]]; then
  echo "FLUENT_DIALOGUE_DORA_BARGE_IN_SPEECH_FRAMES must be an integer frame count" >&2
  exit 64
fi
if ! [[ "${BARGE_IN_SILENCE_RESET_FRAMES}" =~ ^[0-9]+$ ]]; then
  echo "FLUENT_DIALOGUE_DORA_BARGE_IN_SILENCE_RESET_FRAMES must be an integer frame count" >&2
  exit 64
fi

uv run --extra dev --extra dora --extra tts python - "${STIMULUS_TEXT}" "${STIMULUS_GAIN}" <<'PY'
import struct
import sys
from pathlib import Path

import numpy as np
import pyopenjtalk

path = Path("artifacts/aec_hardware_validation/stimulus_48k_stereo.s16le")
text = sys.argv[1]
gain = float(sys.argv[2])
if not 0.0 < gain <= 1.0:
    raise SystemExit("FLUENT_DIALOGUE_DORA_AEC_STIMULUS_GAIN must be in (0.0, 1.0]")
target_rate = 48_000
silence = np.zeros(target_rate, dtype=np.float32)
waveform_raw, sample_rate_hz = pyopenjtalk.tts(text)
waveform = np.asarray(waveform_raw, dtype=np.float32)
if waveform.ndim != 1 or waveform.size == 0:
    raise SystemExit("pyopenjtalk produced invalid mono waveform")
peak = float(np.max(np.abs(waveform)))
if peak > 1.0:
    waveform = waveform / (32768.0 if peak <= 32768.0 else peak)
if int(sample_rate_hz) != target_rate:
    src_t = np.arange(waveform.shape[0], dtype=np.float64) / float(sample_rate_hz)
    dst_len = max(1, round(waveform.shape[0] * target_rate / float(sample_rate_hz)))
    dst_t = np.arange(dst_len, dtype=np.float64) / float(target_rate)
    waveform = np.interp(dst_t, src_t, waveform).astype(np.float32)
speech = waveform[: 4 * target_rate]
if speech.shape[0] < 4 * target_rate:
    speech = np.pad(speech, (0, 4 * target_rate - speech.shape[0]))
fade_len = int(0.03 * target_rate)
fade = np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
speech[:fade_len] *= fade
speech[-fade_len:] *= fade[::-1]
stimulus = np.concatenate((silence, speech * np.float32(gain), silence))
with path.open("wb") as f:
    for value in stimulus:
        sample = int(float(np.clip(value, -1.0, 1.0)) * 32767)
        f.write(struct.pack("<hh", sample, sample))
PY

cat >"${GRAPH}" <<YAML
nodes:
  - id: stimulus_source
    path: python
    args: ../../nodes/audio_device/raw_pcm_source/main.py --dora --input ../../${STIM} --sample-rate-hz 48000 --channels 2 --sample-format s16le --channel-layout interleaved --chunk-frames 480 --source-id aec_validation_stimulus --stream-id audio/aec_validation/stimulus --start-seq 0 --start-sample-index 0 --start-capture-time-ns 0 --replay-speed 1.0
    outputs:
      - audio

  - id: cpal_sink
    build: ../../scripts/dora_cargo_build.sh ../../nodes/audio_device/cpal_sink/Cargo.toml
    path: ../../nodes/audio_device/cpal_sink/target/debug/cpal_sink
    args: --device-id ${SPEAKER_DEVICE_ID} --sample-rate-hz 48000 --channels 2 --sample-format s16le --channel-layout interleaved --buffer-size-frames 480 --queue-capacity-chunks 64 --startup-buffer-chunks 2 --empty-queue-policy silence --source-id aec_validation_stimulus --stream-id audio/aec_validation/stimulus --completion-timeout-ms 10000 --render-reference-source-id cpal_sink --render-reference-stream-id audio/cpal_sink/aec_validation_render_reference
    inputs:
      audio:
        source: stimulus_source/audio
        queue_size: 64
        queue_policy: backpressure
    outputs:
      - render_reference

  - id: cpal_capture
    build: ../../scripts/dora_cargo_build.sh ../../nodes/audio_device/cpal_capture/Cargo.toml
    path: ../../nodes/audio_device/cpal_capture/target/debug/cpal_capture
    args: --device-id ${MIC_DEVICE_ID} --sample-rate-hz 48000 --channels 2 --sample-format f32le --channel-layout interleaved --chunk-frames 960 --buffer-size-frames 2048 --queue-capacity-chunks 512 --source-id cpal_capture --stream-id audio/cpal_capture/aec_validation --start-seq 0 --start-sample-index 0 --start-capture-time-ns 0 --max-chunks 360 --capture-timeout-ms 3000
    outputs:
      - audio

  - id: media_graph_asr
    path: python
    args: ../../nodes/media_graph/main.py --dora --input-source-id cpal_capture --input-stream-id audio/cpal_capture/aec_validation --input-sample-rate-hz 48000 --input-channels 2 --input-sample-format f32le --input-channel-layout interleaved --output-source-id media_graph --output-stream-id audio/media_graph/aec_validation_near --output-sample-rate-hz 16000 --output-channels 1 --output-sample-format s16le --output-channel-layout interleaved --output-start-seq 0 --output-start-sample-index 0 --output-start-capture-time-ns 0 --linear-gain 4.0
    inputs:
      audio:
        source: cpal_capture/audio
        queue_size: 512
        queue_policy: backpressure
    outputs:
      - audio

  - id: near_sink
    path: python
    args: ../../nodes/audio_device/raw_pcm_sink/main.py --dora --output ../../${NEAR} --sample-rate-hz 16000 --channels 1 --sample-format s16le --channel-layout interleaved --source-id media_graph --stream-id audio/media_graph/aec_validation_near --overwrite
    inputs:
      audio:
        source: media_graph_asr/audio
        queue_size: 512
        queue_policy: backpressure

  - id: barge_in_aec
    build: ../../scripts/dora_cargo_build.sh --release ../../nodes/audio_device/barge_in_aec/Cargo.toml
    path: ../../nodes/audio_device/barge_in_aec/target/release/barge_in_aec
    args: --output-source-id barge_in_aec --output-stream-id audio/aec_validation/clean --far-buffer-max-samples 64000 --backend ${AEC_BACKEND} ${AEC_STREAM_DELAY_ARGS}
    inputs:
      near:
        source: media_graph_asr/audio
        queue_size: 512
        queue_policy: backpressure
      far:
        source: cpal_sink/render_reference
        queue_size: 512
        queue_policy: backpressure
    outputs:
      - audio

  - id: aec_sink
    path: python
    args: ../../nodes/audio_device/raw_pcm_sink/main.py --dora --output ../../${AEC} --sample-rate-hz 16000 --channels 1 --sample-format s16le --channel-layout interleaved --source-id barge_in_aec --stream-id audio/aec_validation/clean --overwrite
    inputs:
      audio:
        source: barge_in_aec/audio
        queue_size: 512
        queue_policy: backpressure
YAML

rm -f "${NEAR}" "${AEC}" "${REPORT}"
uvx --from dora-rs-cli dora run "${GRAPH}" --uv

uv run --extra vad python tools/aec_eval/analyze_pair.py \
  --candidate-name "${AEC_BACKEND}_aec3" \
  --reference-near "${NEAR}" \
  --candidate "${AEC}" \
  --far-stimulus "${STIM}" \
  --output "${REPORT}" \
  --stream-delay-ms "${AEC_STREAM_DELAY_MS}" \
  --stimulus-text "${STIMULUS_TEXT}" \
  --stimulus-gain "${STIMULUS_GAIN}" \
  --vad-threshold "${VAD_THRESHOLD}" \
  --max-vad-speech-ratio "${MAX_AEC_SPEECH_RATIO}" \
  --max-contiguous-speech-events "${MAX_AEC_CONTIGUOUS_SPEECH_EVENTS}" \
  --barge-in-speech-frames "${BARGE_IN_SPEECH_FRAMES}" \
  --barge-in-silence-reset-frames "${BARGE_IN_SILENCE_RESET_FRAMES}"

python - "${REPORT}" <<'PY'
import json
import sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
rms = report["rms"]
vad = report["vad"]
candidate = vad["candidate"]
reference = vad["reference"]
print(f"reference_rms_playback_dbfs={rms['reference_playback_dbfs']:.2f}")
print(f"candidate_rms_playback_dbfs={rms['candidate_playback_dbfs']:.2f}")
print(f"rms_attenuation_db={rms['rms_attenuation_db']:.2f}")
print(f"baseline_subtracted_echo_reduction_db={rms['baseline_subtracted_echo_reduction_db']:.2f}")
print(f"reference_vs_far_corr={rms['reference_vs_far_corr']:.4f} lag_samples={rms['reference_vs_far_corr_lag_samples']}")
print(f"candidate_vs_far_corr={rms['candidate_vs_far_corr']:.4f} lag_samples={rms['candidate_vs_far_corr_lag_samples']}")
print(f"corr_attenuation_db={rms['corr_attenuation_db']:.2f}")
print(f"reference_baseline_dbfs={rms['reference_baseline_dbfs']:.2f}")
print(f"candidate_baseline_dbfs={rms['candidate_baseline_dbfs']:.2f}")
print(f"reference_vad_speech_events={reference['speech_events']}")
print(f"candidate_vad_speech_events={candidate['speech_events']}")
print(f"candidate_vad_speech_event_ratio={vad['candidate_speech_event_ratio']:.3f}")
print(f"reference_vad_max_contiguous_speech_events={reference['max_contiguous_speech_events']}")
print(f"candidate_vad_max_contiguous_speech_events={candidate['max_contiguous_speech_events']}")
print(f"reference_simulated_barge_in_count={reference['simulated_barge_in_count']}")
print(f"candidate_simulated_barge_in_count={candidate['simulated_barge_in_count']}")
print(f"report={sys.argv[1]}")
if not report["passed"]["overall"]:
    raise SystemExit("FAIL: AEC candidate did not pass all hardware validation gates")
PY
