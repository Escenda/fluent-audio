# asr_eval

日本語 ASR の CER（文字誤り率）・遅延・パーシャル出力数を実測する評価ハーネス。
`docs/課題/voice-dialogue-quality.md` 課題 3 の検証手順 1–2 に対応する。

## 構成

- `sentences_ja.tsv` — 評価文セット（`core` = CER 集計対象 / `numeric` = 数値表記揺れの観察用）
- `synthesize_set.py` — pyopenjtalk で評価 WAV + `manifest.jsonl` を生成（uv 環境）
- `eval_nemotron.py` — DORA ノードと同一の `NemoCacheAwareStreamingBackend` を直接駆動して評価（nemotron venv / CUDA）

## 使い方

```bash
# 1. 評価セット合成（48kHz mono s16 WAV）
uv run --extra tts python tools/asr_eval/synthesize_set.py \
  --sentences tools/asr_eval/sentences_ja.tsv \
  --output-dir artifacts/asr_eval/set_v1

# 2. 評価実行（16kHz へは内部でリサンプル）
/home/aspa/repos/daihen-physical-ai.audio/data/builds/envs/nemotron_streaming_asr/current/venv/bin/python \
  tools/asr_eval/eval_nemotron.py \
  --manifest artifacts/asr_eval/set_v1/manifest.jsonl \
  --model-name <model.nemo へのパス> \
  --target-lang ja-JP --att-context-right-frames 3 \
  --run-name baseline_ja_att3
```

結果は `artifacts/asr_eval/runs/<run-name>/` に `results.jsonl`（発話別）と
`summary.json`（コーパス CER / stop 遅延 p50/p95 / RTF / パーシャル数）で出る。

## 計測の意味

- `cer` — NFKC 正規化 + 句読点除去後の文字編集距離 / 参照文字数。長音「ー」は保持。
- `stop_wall_s` — `AsrStop` での全区間再転写（= 現行パイプラインでターン終了後に
  ユーザーが待つ ASR 由来遅延）。
- `rtf_stream` — push_audio 合計 / 音声長。1 を超えるとリアルタイム処理不可。
- `partial_count` / `delta_count` — ストリーミング中に backend が返した
  仮説数。課題 3 の「パーシャルが出ない」問題の定量値。

## 既知の制約

- 評価音声は pyopenjtalk 合成（クリーン・単一話者）。実マイク・実話者より
  CER は楽観値になる。マイク実録の WAV を `manifest.jsonl` 形式
  （`{"id","group","text","wav"}`）で用意すれば同じハーネスで評価できる。
- 漢字/かな表記揺れ（例: ください/下さい）は誤りとして数える。結果の
  `results.jsonl` を目視確認し、表記揺れ起因が支配的なら正規化を拡張する。
- 数値の表記（七時 vs 7時）は `numeric` グループに分離し別掲。
