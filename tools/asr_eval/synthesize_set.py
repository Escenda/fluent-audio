"""Synthesize the Japanese ASR evaluation set with pyopenjtalk.

Run inside the repo uv environment:

    uv run --extra tts python tools/asr_eval/synthesize_set.py \
        --sentences tools/asr_eval/sentences_ja.tsv \
        --output-dir artifacts/asr_eval/set_v1

Writes one 48 kHz mono s16 WAV per sentence plus ``manifest.jsonl`` with the
reference text. Resampling to the ASR rate happens in ``eval_nemotron.py``.
"""

from __future__ import annotations

import argparse
import json
import wave
from pathlib import Path


def parse_sentences(path: Path) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t", 2)
        if len(parts) != 3:
            raise ValueError(f"{path}:{line_number}: expected id<TAB>group<TAB>text")
        rows.append((parts[0], parts[1], parts[2]))
    if not rows:
        raise ValueError(f"{path}: no sentences found")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sentences", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--speed", type=float, default=1.0)
    args = parser.parse_args()

    import numpy as np
    import pyopenjtalk

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output_dir / "manifest.jsonl"

    with manifest_path.open("w", encoding="utf-8") as manifest:
        for utt_id, group, text in parse_sentences(args.sentences):
            if args.speed != 1.0:
                waveform, sample_rate_hz = pyopenjtalk.tts(text, speed=args.speed)
            else:
                waveform, sample_rate_hz = pyopenjtalk.tts(text)
            samples = np.asarray(waveform, dtype=np.float64)
            peak = float(np.max(np.abs(samples))) if samples.size else 0.0
            if peak > 32767.0:
                samples = samples * (32767.0 / peak)
            pcm = samples.astype(np.int16)

            wav_path = args.output_dir / f"{utt_id}.wav"
            with wave.open(str(wav_path), "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(int(sample_rate_hz))
                wav_file.writeframes(pcm.tobytes())

            entry = {
                "id": utt_id,
                "group": group,
                "text": text,
                "wav": str(wav_path),
                "sample_rate_hz": int(sample_rate_hz),
                "duration_s": round(len(pcm) / float(sample_rate_hz), 3),
                "tts": "pyopenjtalk",
                "speed": args.speed,
            }
            manifest.write(json.dumps(entry, ensure_ascii=False) + "\n")
            print(f"{utt_id} {len(pcm) / float(sample_rate_hz):6.2f}s {text}")

    print(f"\nwrote {manifest_path}")


if __name__ == "__main__":
    main()
