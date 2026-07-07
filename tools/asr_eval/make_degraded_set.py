"""Create acoustically degraded variants of an ASR eval set (noise + gain).

Approximates far-mic conditions to separate "model capability" from
"acoustic conditions" (docs/課題/voice-dialogue-quality.md 課題3).

    <python> tools/asr_eval/make_degraded_set.py \
        --manifest artifacts/asr_eval/set_v1/manifest.jsonl \
        --output-dir artifacts/asr_eval/set_v1_snr10 \
        --snr-db 10 --gain-db -6 --seed 20260612
"""

from __future__ import annotations

import argparse
import json
import wave
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--snr-db", type=float, required=True)
    parser.add_argument("--gain-db", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=20260612)
    args = parser.parse_args()

    import numpy as np

    rng = np.random.default_rng(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_manifest = args.output_dir / "manifest.jsonl"

    with output_manifest.open("w", encoding="utf-8") as manifest_file:
        for line in args.manifest.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            with wave.open(entry["wav"], "rb") as wav_file:
                if wav_file.getnchannels() != 1 or wav_file.getsampwidth() != 2:
                    raise ValueError(f"{entry['wav']}: expected mono s16 wav")
                sample_rate_hz = wav_file.getframerate()
                pcm = np.frombuffer(
                    wav_file.readframes(wav_file.getnframes()), dtype=np.int16
                ).astype(np.float64)

            gain = 10.0 ** (args.gain_db / 20.0)
            speech = pcm * gain
            speech_rms = float(np.sqrt(np.mean(np.square(speech)))) or 1.0
            noise_rms = speech_rms / (10.0 ** (args.snr_db / 20.0))
            noise = rng.standard_normal(len(speech)) * noise_rms
            mixed = np.clip(speech + noise, -32768, 32767).astype(np.int16)

            wav_path = args.output_dir / f"{entry['id']}.wav"
            with wave.open(str(wav_path), "wb") as out_file:
                out_file.setnchannels(1)
                out_file.setsampwidth(2)
                out_file.setframerate(sample_rate_hz)
                out_file.writeframes(mixed.tobytes())

            entry = dict(entry)
            entry["wav"] = str(wav_path)
            entry["degradation"] = {"snr_db": args.snr_db, "gain_db": args.gain_db}
            manifest_file.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"wrote {output_manifest}")


if __name__ == "__main__":
    main()
