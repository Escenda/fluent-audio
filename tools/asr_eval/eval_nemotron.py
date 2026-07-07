"""Evaluate the Nemotron streaming ASR backend on a wav+reference manifest.

Runs the same ``NemoCacheAwareStreamingBackend`` the DORA node uses, feeding
audio in pipeline-sized chunks, and reports per-utterance and corpus CER
(character error rate), streaming/finalize latency, and how many live
partial hypotheses the backend actually produced.

Run inside the nemotron_streaming venv (CUDA required):

    /home/aspa/repos/daihen-physical-ai.audio/data/builds/envs/\
nemotron_streaming_asr/current/venv/bin/python \
        tools/asr_eval/eval_nemotron.py \
        --manifest artifacts/asr_eval/set_v1/manifest.jsonl \
        --model-name <path/to/model.nemo> \
        --target-lang ja-JP \
        --run-name baseline_ja
"""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import datetime
import json
import math
import statistics
import sys
import time
import unicodedata
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fluent_dialogue_dora.contracts import AsrStart, AsrStop, AudioChunk, AudioFormat
from nodes.asr.nemotron_streaming.backend import (
    NemotronBackendSettings,
    build_nemotron_backend,
)

ASR_SAMPLE_RATE_HZ = 16000

# 句読点・空白・引用符のみ除去する。長音「ー」は音韻情報なので残す。
_STRIP_CHARS = set('。、，．・！？!?,.;:｡､「」『』（）()[]{}“”"\'…‥　 \t\n')


def normalize_for_cer(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    return "".join(ch for ch in normalized if ch not in _STRIP_CHARS)


def edit_distance(reference: str, hypothesis: str) -> int:
    if not reference:
        return len(hypothesis)
    if not hypothesis:
        return len(reference)
    previous = list(range(len(hypothesis) + 1))
    for i, ref_char in enumerate(reference, 1):
        current = [i]
        for j, hyp_char in enumerate(hypothesis, 1):
            cost = 0 if ref_char == hyp_char else 1
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + cost))
        previous = current
    return previous[-1]


def load_manifest(path: Path) -> list[dict]:
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    if not entries:
        raise ValueError(f"{path}: empty manifest")
    return entries


def load_wav_as_16k_f32(wav_path: Path, *, linear_gain: float = 1.0) -> "object":
    import numpy as np
    import soundfile

    samples, sample_rate_hz = soundfile.read(str(wav_path), dtype="float32", always_2d=False)
    if getattr(samples, "ndim", 1) > 1:
        samples = samples.mean(axis=1)
    if sample_rate_hz != ASR_SAMPLE_RATE_HZ:
        from scipy.signal import resample_poly

        gcd = math.gcd(int(sample_rate_hz), ASR_SAMPLE_RATE_HZ)
        samples = resample_poly(
            samples, ASR_SAMPLE_RATE_HZ // gcd, int(sample_rate_hz) // gcd
        ).astype(np.float32)
    if linear_gain != 1.0:
        # live 経路の media_graph --linear-gain 相当(飽和あり)を再現する
        samples = np.clip(samples * linear_gain, -1.0, 1.0).astype(np.float32)
    return samples


def run_utterance(
    backend,
    *,
    utt_id: str,
    samples,
    chunk_frames: int,
) -> dict:
    audio_format = AudioFormat(
        sample_rate_hz=ASR_SAMPLE_RATE_HZ,
        channels=1,
        sample_format="f32le",
        channel_layout="interleaved",
    )
    backend.start(
        AsrStart(
            action="start",
            session_id="asr-eval",
            user_turn_id=f"utt-{utt_id}",
            stream_id="audio/asr-eval",
            seq=0,
            start_sample_index=0,
        ),
        audio_format,
    )

    partial_count = 0
    push_wall_s = 0.0
    sample_index = 0
    seq = 0
    total_frames = len(samples)
    while sample_index < total_frames:
        block = samples[sample_index : sample_index + chunk_frames]
        chunk = AudioChunk(
            source_id="asr_eval",
            stream_id="audio/asr-eval",
            seq=seq,
            sample_index=sample_index,
            capture_time_ns=0,
            frame_count=len(block),
            format=audio_format,
            payload=block.astype("<f4").tobytes(),
        )
        started = time.perf_counter()
        push_result = backend.push_audio(chunk)
        push_wall_s += time.perf_counter() - started
        partial_count += len(push_result.partial_texts)
        sample_index += len(block)
        seq += 1

    started = time.perf_counter()
    final_result = backend.stop(
        AsrStop(
            action="stop",
            session_id="asr-eval",
            user_turn_id=f"utt-{utt_id}",
            stream_id="audio/asr-eval",
            seq=1,
            stop_sample_index=total_frames,
        )
    )
    stop_wall_s = time.perf_counter() - started

    return {
        "hypothesis": final_result.text,
        "push_wall_s": push_wall_s,
        "stop_wall_s": stop_wall_s,
        "partial_count": partial_count,
    }


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round(fraction * (len(ordered) - 1))))
    return ordered[index]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--model-extracted-dir", type=Path)
    parser.add_argument("--target-lang", default="ja-JP")
    parser.add_argument("--att-context-right-frames", type=int, default=3)
    parser.add_argument("--chunk-frames", type=int, default=512)
    parser.add_argument(
        "--linear-gain",
        type=float,
        default=1.0,
        help="live 経路再現用のソフトウェアゲイン(media_graph --linear-gain 相当、飽和あり)",
    )
    parser.add_argument("--run-name", default=None)
    parser.add_argument("--output-root", type=Path, default=_REPO_ROOT / "artifacts/asr_eval/runs")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    entries = load_manifest(args.manifest)
    if args.limit is not None:
        entries = entries[: args.limit]

    run_name = args.run_name or (
        f"{datetime.datetime.now():%Y%m%d-%H%M%S}"
        f"_lang-{args.target_lang}_att-{args.att_context_right_frames}"
    )
    output_dir = args.output_root / run_name
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"loading model: {args.model_name}", flush=True)
    load_started = time.perf_counter()
    backend = build_nemotron_backend(
        NemotronBackendSettings(
            backend="nemo",
            model_name=args.model_name,
            model_extracted_dir=args.model_extracted_dir,
            target_lang=args.target_lang,
            att_context_right_frames=args.att_context_right_frames,
        )
    )
    model_load_s = time.perf_counter() - load_started
    print(f"model loaded in {model_load_s:.1f}s", flush=True)

    # 1発話目をウォームアップとして計測対象外で実行(CUDA初期化コストを除外)
    warmup_samples = load_wav_as_16k_f32(Path(entries[0]["wav"]), linear_gain=args.linear_gain)
    run_utterance(backend, utt_id="warmup", samples=warmup_samples, chunk_frames=args.chunk_frames)
    print("warmup done", flush=True)

    results = []
    for entry in entries:
        samples = load_wav_as_16k_f32(Path(entry["wav"]), linear_gain=args.linear_gain)
        duration_s = len(samples) / ASR_SAMPLE_RATE_HZ
        outcome = run_utterance(
            backend, utt_id=entry["id"], samples=samples, chunk_frames=args.chunk_frames
        )
        reference_normalized = normalize_for_cer(entry["text"])
        hypothesis_normalized = normalize_for_cer(outcome["hypothesis"])
        edits = edit_distance(reference_normalized, hypothesis_normalized)
        cer = edits / max(1, len(reference_normalized))
        record = {
            "id": entry["id"],
            "group": entry["group"],
            "reference": entry["text"],
            "hypothesis": outcome["hypothesis"],
            "reference_normalized": reference_normalized,
            "hypothesis_normalized": hypothesis_normalized,
            "edits": edits,
            "reference_chars": len(reference_normalized),
            "cer": round(cer, 4),
            "duration_s": round(duration_s, 3),
            "push_wall_s": round(outcome["push_wall_s"], 4),
            "stop_wall_s": round(outcome["stop_wall_s"], 4),
            "rtf_stream": round(outcome["push_wall_s"] / duration_s, 4),
            "rtf_finalize": round(outcome["stop_wall_s"] / duration_s, 4),
            "partial_count": outcome["partial_count"],
        }
        results.append(record)
        print(
            f"{entry['id']} cer={cer:5.1%} stop={outcome['stop_wall_s']:.2f}s "
            f"partials={outcome['partial_count']} "
            f"hyp={outcome['hypothesis']!r}",
            flush=True,
        )

    results_path = output_dir / "results.jsonl"
    with results_path.open("w", encoding="utf-8") as results_file:
        for record in results:
            results_file.write(json.dumps(record, ensure_ascii=False) + "\n")

    def corpus_cer(group: str) -> tuple[float, int]:
        group_results = [r for r in results if r["group"] == group]
        total_edits = sum(r["edits"] for r in group_results)
        total_chars = sum(r["reference_chars"] for r in group_results)
        return (total_edits / max(1, total_chars), len(group_results))

    core_cer, core_n = corpus_cer("core")
    numeric_cer, numeric_n = corpus_cer("numeric")
    stop_walls = [r["stop_wall_s"] for r in results]
    summary = {
        "run_name": run_name,
        "model_name": args.model_name,
        "target_lang": args.target_lang,
        "att_context_right_frames": args.att_context_right_frames,
        "chunk_frames": args.chunk_frames,
        "linear_gain": args.linear_gain,
        "model_load_s": round(model_load_s, 1),
        "core": {"utterances": core_n, "cer": round(core_cer, 4)},
        "numeric": {"utterances": numeric_n, "cer": round(numeric_cer, 4)},
        "stop_wall_s": {
            "mean": round(statistics.mean(stop_walls), 3),
            "p50": round(percentile(stop_walls, 0.5), 3),
            "p95": round(percentile(stop_walls, 0.95), 3),
            "max": round(max(stop_walls), 3),
        },
        "rtf_stream_mean": round(statistics.mean(r["rtf_stream"] for r in results), 4),
        "rtf_finalize_mean": round(statistics.mean(r["rtf_finalize"] for r in results), 4),
        "total_partials": sum(r["partial_count"] for r in results),
        "utterances_with_partials": sum(1 for r in results if r["partial_count"] > 0),
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== summary ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nwrote {results_path}\nwrote {summary_path}")


if __name__ == "__main__":
    main()
