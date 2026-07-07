"""Record the Japanese ASR eval set with the real microphone (arecord).

実マイク録音セットを作る対話ツール。標準ライブラリのみで動く。

    python3 tools/asr_eval/record_set.py \
        --sentences tools/asr_eval/sentences_ja.tsv \
        --output-dir artifacts/asr_eval/set_mic_v1 \
        --device plughw:CARD=S3,DEV=0

操作: 文が表示されたら Enter で録音開始 → 読み上げて Enter で停止。
その後 Enter=次へ / r=録り直し / q=中断(それまでの分は manifest に保存)。
"""

from __future__ import annotations

import argparse
import json
import signal
import subprocess
import sys
import time
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


def record_once(wav_path: Path, *, device: str, sample_rate_hz: int, channels: int) -> float:
    command = [
        "arecord",
        "-D", device,
        "-f", "S16_LE",
        "-r", str(sample_rate_hz),
        "-c", str(channels),
        "-q",
        str(wav_path),
    ]
    process = subprocess.Popen(command)
    try:
        input("  録音中... 読み終えたら Enter >")
        # Enter が語尾と同時に押されると末尾が欠けるため、停止前に猶予を取る
        # (set_mic_v1 では 35 件中 18 件で語尾 200ms 未満の切断が起きた)
        time.sleep(0.8)
    finally:
        process.send_signal(signal.SIGINT)
        process.wait(timeout=5)
    with wave.open(str(wav_path), "rb") as wav_file:
        return wav_file.getnframes() / float(wav_file.getframerate())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sentences", type=Path, default=Path("tools/asr_eval/sentences_ja.tsv"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="plughw:CARD=S3,DEV=0")
    parser.add_argument("--sample-rate-hz", type=int, default=48000)
    parser.add_argument("--channels", type=int, default=1)
    args = parser.parse_args()

    sentences = parse_sentences(args.sentences)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output_dir / "manifest.jsonl"
    records: list[dict] = []

    print(f"録音デバイス: {args.device} / {args.sample_rate_hz}Hz {args.channels}ch")
    print(f"全 {len(sentences)} 文。普段エージェントに話しかける位置・距離・声量で読んでください。\n")

    try:
        for index, (utt_id, group, text) in enumerate(sentences, 1):
            wav_path = args.output_dir / f"{utt_id}.wav"
            while True:
                print(f"[{index}/{len(sentences)}] {utt_id}")
                print(f"  ▶ {text}")
                input("  Enter で録音開始 >")
                duration_s = record_once(
                    wav_path,
                    device=args.device,
                    sample_rate_hz=args.sample_rate_hz,
                    channels=args.channels,
                )
                if duration_s < 0.5:
                    print(f"  ! 録音が短すぎます ({duration_s:.2f}s)。録り直してください。")
                    continue
                print(f"  録音 {duration_s:.2f}s")
                choice = input("  Enter=次へ / r=録り直し / q=中断保存 >").strip().lower()
                if choice == "r":
                    continue
                records.append(
                    {
                        "id": utt_id,
                        "group": group,
                        "text": text,
                        "wav": str(wav_path),
                        "sample_rate_hz": args.sample_rate_hz,
                        "duration_s": round(duration_s, 3),
                        "source": "mic",
                        "device": args.device,
                    }
                )
                if choice == "q":
                    raise KeyboardInterrupt
                print()
                break
    except KeyboardInterrupt:
        print("\n中断しました。ここまでの分を保存します。")

    with manifest_path.open("w", encoding="utf-8") as manifest:
        for record in records:
            manifest.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"\n{len(records)} 発話を記録: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
