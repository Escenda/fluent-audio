# fluent-dialogue-dora

`fluent-dialogue-dora` は、音声対話を DORA のプロセス境界で組み立てる E2E ランタイムです。
マイク入力、VAD、ASR、対話エンジン、TTS、再生、外部ブリッジを別々のノードとして扱います。

ROS2 は中心の実行基盤ではありません。
ROS2 はロボット側のエコシステムへイベントやコマンドを投影するための境界です。

## 初回セットアップ

開発環境は次のスクリプトでそろえます。

```bash
scripts/bootstrap_dev_env.sh --verify
```

このスクリプトは OS パッケージ、Python 依存、Rust toolchain、TypeScript 依存をそろえます。
`--verify` を付けると、代表テストと Rust ビルド確認まで実行します。

OS 依存をすでに入れてある場合は、`apt` を省略できます。

```bash
scripts/bootstrap_dev_env.sh --no-system --verify
```

## モデル重みの取得

モデル重みも初回セットアップに含める場合は、`--models` を付けます。

```bash
scripts/bootstrap_dev_env.sh --models --verify
```

モデルだけ取得する場合は、次のコマンドを使います。

```bash
uv run python scripts/download_models.py
```

個別に取得することもできます。

```bash
uv run python scripts/download_models.py --target nemotron
uv run python scripts/download_models.py --target kokoro
uv run python scripts/download_models.py --target llm
```

既定では、モデルは `data/models/fluent_dialogue_dora/` に保存されます。
このディレクトリは `.gitignore` に入っているため、重みを Git に含めません。

Hugging Face の gated model や private model を取得する場合は、`HF_TOKEN` または `HUGGINGFACE_HUB_TOKEN` を設定します。

```bash
export HF_TOKEN=...
scripts/bootstrap_dev_env.sh --models
```

既定で取得するモデルは次のとおりです。

- **Nemotron ASR**：`nvidia/nemotron-3.5-asr-streaming-0.6b`
- **Kokoro TTS**：`hexgrad/Kokoro-82M`
- **LLM**：`sakamakismile/Qwen3.6-27B-MTP-pi-tune-NVFP4`

Silero VAD の ONNX モデルはリポジトリに同梱しています。
そのため、通常は別途ダウンロードしません。

## 検証

通常の代表検証は次のコマンドで実行します。

```bash
uv run python -m pytest tests
```

TypeScript の生成 contract は次のコマンドで確認します。

```bash
npm run --prefix contracts/typescript typecheck
```

Rust ノードは個別の `Cargo.toml` を指定して確認します。

```bash
cargo check --manifest-path contracts/rust/Cargo.toml --locked
cargo check --manifest-path nodes/audio_device/rust_audio_boundary/Cargo.toml --locked
cargo check --manifest-path nodes/audio_device/cpal_capture/Cargo.toml --locked
cargo check --manifest-path nodes/audio_device/cpal_sink/Cargo.toml --locked
cargo check --manifest-path nodes/audio_device/barge_in_aec/Cargo.toml --locked
```

`barge_in_aec` は `bindgen` を使うため、`libclang.so` が必要です。
Ubuntu 系では `libclang-dev` と `clang` を入れると解決します。

## 実行入口

ローカル LLM の vLLM サーバーは次のスクリプトで起動します。

```bash
scripts/run_qwen3_coder_vllm_server.sh
```

ライブ音声対話は、実機のマイクとスピーカーを使います。
Codex 側の live turn を明示的に許可してから起動します。

```bash
FLUENT_DIALOGUE_DORA_ALLOW_LIVE_CODEX_TURN=1 \
scripts/run_live_hardware_voice_session.sh --serve
```

ファイル入力でライブ経路に近い構成を動かす場合は、次のスクリプトを使います。

```bash
FLUENT_DIALOGUE_DORA_ALLOW_LIVE_CODEX_TURN=1 \
scripts/run_file_live_voice_session.sh --run
```

実行中のセッションは状態確認と停止ができます。

```bash
scripts/run_live_hardware_voice_session.sh --status
scripts/run_live_hardware_voice_session.sh --stop
```

## ディレクトリ構成

contract の schema は `contracts/proto` を source of truth とします。
生成済みの Python protobuf binding は `contracts/python` に置きます。

ランタイムの補助コードは `src/fluent_dialogue_dora` に置きます。
ここには生成 contract ではない Python の型、DORA payload helper、offline I/O helper が入ります。

実行可能な DORA ノードは `nodes` に置きます。
Rust を多く含むノードも、所有するノードディレクトリの中に実装します。

```text
fluent-dialogue-dora/
├── contracts/
│   ├── proto/
│   ├── python/
│   ├── rust/
│   └── typescript/
├── nodes/
│   ├── audio_device/
│   ├── media_graph/
│   ├── vad/
│   ├── asr/
│   ├── dialogue_engine/
│   ├── tts/
│   ├── playback/
│   └── diagnostics/
├── bridges/
├── apps/
├── graphs/
├── environments/
├── tools/
├── docs/
└── tests/
```

`bridges` は外部システムとの境界です。
ROS2 bridge と Web bridge は、内部 contract を外部の表現へ変換します。

`graphs` は DORA dataflow を置く場所です。
実行時に生成する dataflow は `graphs/out/` に置きます。

`artifacts/` と `data/models/` はローカル実行物です。
どちらも Git には含めません。

## 設計上の境界

音声、時刻、sequence、device、model の失敗は暗黙にフォールバックしません。
外部 payload は境界で検証してから内側へ渡します。

DORA のプロセス境界と、GStreamer などの in-process media graph は分けます。
プロセス間の接続は DORA が担い、単一プロセス内の音声変換は owning node が担います。

legacy compatibility path は、人間が明示的に承認した場合だけ残します。
contract の escape hatch として `Any`、`dict[str, Any]`、`object` を増やしません。

## 関連文書

リポジトリ構成の詳細は [docs/設計/repository-structure.md](docs/設計/repository-structure.md) を参照してください。
実装状況は [docs/architecture/build-plan.md](docs/architecture/build-plan.md) にあります。
