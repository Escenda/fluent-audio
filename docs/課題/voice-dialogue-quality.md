# 音声対話品質 課題整理

作成日: 2026-06-12
対象: Codex バックエンド音声対話（`scripts/run_live_hardware_voice_session.sh` 系統）

この文書は音声対話品質に関する既知の課題を一元管理するロードマップである。
課題ごとに「現状分析 → 精査・検証手順 → 改善方針 → 完了条件」を持ち、1 つずつ
精査しながら解決していく。コード参照は 2026-06-12 時点（`main` @ 2a90900）。

ステータス凡例:

- `未着手` / `精査中` / `対応中` / `検証待ち` / `完了`
- 本文中の「確認済み」はコードを読んで確定した事実、「要実測」は実行して
  測定しないと確定しない事項を指す。

| # | 課題 | 種別 | ステータス |
| --- | --- | --- | --- |
| 1 | ユーザー割り込み（バージイン）処理が存在しない | 機能不足 | **実装完了・ライブ確認待ち**（2026-06-13: Phase 0-4 完了=検知+停止+フェード+キャンセル+トランケーション+AEC、全テスト合格。残: Phase 5 実マイク検証=ユーザー実施） |
| 2 | ツール実行前ナレーションの音声化が機能するか未検証 | 動作検証 | **検証完了**（2026-06-12: fixture PASS + 実モデルのナレーション確認） |
| 3 | Nemotron ASR の認識精度・パーシャル表示 | 性能 | **主因確定**（2026-06-13: PowerConf S3 の DSP が主因。DJI マイクで CER 13.5%→6.4%。対策=マイク分離。残: パーシャル/finalize） |
| 4 | LLM の日本語対話品質 | 性能 | **切り分け完了**（2026-06-12: H1+H2+H3 すべて実在。次: 長さガード・モデルA/B） |
| 5 | Codex ツール実行がこの環境で機能しない | 不具合（新規発見） | **案 A 適用済み・実行実証済み**（2026-06-12。残: ライブ一気通貫確認、構文リークガード） |

---

## 0. 前提: 現行パイプラインと設定値

```text
mic (cpal/alsa/pipewire, 48kHz)
 → media_graph_asr (16kHz mono s16le へリサンプル)
 → silero VAD (16kHz, threshold 0.5)
 → turn_detector (無音 12000 frames = 750ms でターン終了)
 → asr_control_from_turn (AsrStart/Stop/Cancel, prebuffer 16000 frames = 1.0s)
 → nemotron_streaming ASR (nemotron-3.5-asr-streaming-0.6b, NeMo cache-aware)
 → dialogue_engine (TranscriptFinal のみ消費)
 → codex_app_server (codex app-server JSON-RPC, vLLM ローカル Qwen3.6 27B MTP pi-tune NVFP4)
 → dialogue_engine (delta を句読点チャンクして TTS テキスト化)
 → tts_backend (HTTP) → tts_pyopenjtalk_server (一括合成 → 250ms チャンク分割)
 → playback_queue → speaker_stream_adapter → media_graph_speaker (48kHz stereo)
 → cpal_sink (queue 128 chunks / startup 64 chunks, 途中破棄不可)

dora_web_bridge が transcript / agent_event / playback_state 等を SSE で
ダッシュボードへ投影。承認は REST 経由で codex_app_server へ戻る。
```

主要な確定値（確認済み）:

| 項目 | 値 | 根拠 |
| --- | --- | --- |
| ターン終了無音 | 750ms（12000 frames @16kHz） | `graphs/out/file_live_voice_session.local.yml:33` |
| ASR プリバッファ | 1.0s（16000 frames） | 同 `:44` |
| ASR チャンク | 320ms（att_context (56,3)） | `nodes/asr/nemotron_streaming/backend.py:76` |
| ASR 制御ホールドバック | 256ms（4096 frames） | 同グラフ `:55` |
| ASR 言語 | live hardware は既定 `ja-JP` / file セッションは `en-US`（英語 fixture 用） | `scripts/run_live_hardware_voice_session.sh:647` |
| LLM | `Qwen3.6-27B-MTP-pi-tune-NVFP4`（vLLM, ctx 131072, `wire_api="responses"`, `qwen3_xml` tool parser, `qwen3` reasoning parser） | `scripts/run_qwen3_coder_vllm_server.sh:29-54` |
| TTS チャンク | 250ms（12000 frames @48kHz）。テキスト単位では一括合成後に分割 | `scripts/run_live_hardware_voice_session.sh:1068`, `nodes/tts/tts_pyopenjtalk_server/main.py:212` |
| TTS テキスト分割 | 句読点 `.!?。！？、，,\n` で随時フラッシュ | `nodes/dialogue_engine/main.py:65` |
| 再生キュー | pause/resume/stop/clear コマンド実装済み・**未配線** | `nodes/playback/playback_queue/main.py:219-243` |
| cpal_sink | queue 128 chunks / startup 64 chunks、バッファ済み音声の破棄手段なし | 同グラフ `:209` |
| AEC | 無し（リポジトリ内に echo/aec 関連実装ゼロ） | 全 nodes grep 確認 |

ハードウェア前提: Jetson（Linux tegra, aarch64）。GPU は vLLM
（`gpu_memory_utilization 0.18` + KV 7G）と Nemotron ASR が同居。

---

## 1. ユーザー割り込み（バージイン）処理 — 機能不足

### 1.1 現状（確認済み）

割り込みの**部品は半分存在するが、繋がっていない**。

- 再生制御基盤は実装済み: `playback_queue` は `playback_command` 入力で
  pause（チャンク留置→resume で順次フラッシュ）/ stop / clear を処理できる
  （`nodes/playback/playback_queue/main.py:219-243`、proto は
  `contracts/proto/fluent_dialogue_dora/v1/playback.proto`）。**ただしどのグラフにも
  この入力が配線されておらず、コマンドを発行するノードも存在しない。**
- テキストレベルの割り込みは既に存在: `dialogue_engine` は実行中のエージェント
  ターン中に新しい `TranscriptFinal` を受けると `_cancel_active_agent("new_user_turn")`
  で Codex ターンをキャンセルし、TTS テキストバッファをクリアする
  （`nodes/dialogue_engine/main.py:332-336, 665-689`）。
- つまり現状の割り込み時挙動は: **エージェントはユーザーの発話中も最後まで
  喋り続け**（再生済みキュー分）、ユーザーの新発話が 750ms 無音で確定した後に
  LLM 側だけがキャンセルされる。合成済み・再生キュー内の音声は止まらない
  （orphan audio）。
- 検知系も意味論レベルが無い: `turn_detector` は無音タイムアウトのみの
  状態機械（`nodes/vad/turn_detector/logic.py:97-105`）。VAD は Silero。
- **AEC が無くマイクは常時オン**（フルデュプレックス）。スピーカー出力が
  マイクに回り込むと、エージェント自身の発話を「ユーザー発話」として VAD が
  拾い、誤ターン → 誤キャンセルを起こし得る（現状は再生停止が無いので
  実害は LLM キャンセルのみだが、バージイン実装後は致命的になる）。
- `cpal_sink` はバッファ済みフレームを破棄できない（`sync_channel` を消費する
  のみ）。停止コマンドを上流に入れても、sink に滞留した分は鳴り終わるまで
  止まらない。停止即応性は sink のキュー深度に依存（要実測）。

### 1.2 旧方式（vegetalia-robotics/aspa-base）との比較

旧方式 = TTS 音声を細かいチャンクに分割して逐次再生し、チャンク境界で
一時停止・再開。割り込み検知は VAD + ターン検知モデルで意味論的に判定。

2026 年時点の調査（下記 1.3）でも、ローカル・カスケード型エージェントの
合意アーキテクチャは本質的にこの方式のままである。本リポジトリは
「250ms チャンク逐次再生」「pause/resume 基盤」を既に持っているため、
旧方式の再実装ではなく**配線と判定ロジックの追加**が作業の中心になる。

### 1.3 調査結果: 2026 年時点の到達点（外部調査済み・要裏取り)

主要 OSS フレームワークの方式比較:

- **LiveKit Agents**: Silero VAD で割り込みトリガ、別途 transcript ベースの
  turn-detector モデル（Qwen2.5-0.5B 蒸留, INT8 ONNX, **日本語対応**, CPU ~25ms）で
  ターン終了判定。誤割り込み対策として `min_duration`、Adaptive Interruption
  Handling（VAD 発火後に CNN 音声分類器で相槌/咳を除外）、
  `resume_false_interruption`（ASR が何も確定しなければ**中断点から再開**）、
  および OpenAI Realtime 流の**会話履歴トランケーション**（実際に再生された
  分だけを履歴に残す）を持つ。
- **Pipecat**: smart-turn v3.1（Whisper-Tiny encoder + head, **8M params /
  int8 ONNX 8MB**, 23 言語で**日本語対応**, BSD-2, CPU 数十 ms）を VAD 停止時の
  ターン完了判定に使用。割り込みは `StartInterruptionFrame` がキューを
  バイパスして即時フラッシュ。`MinWordsInterruptionStrategy` で相槌除外。
- **TEN**: TEN VAD（306KB, 低レイテンシ）+ TEN Turn Detection（Qwen2.5-7B,
  **日本語非対応**）。
- **京大 MaAI / VAP**（Inoue et al.）: ユーザー ch + エージェント ch の
  ステレオ音声から連続的に P(turn-shift) と **P(相槌)** を予測。
  **日本語専用モデルあり、CPU リアルタイム**。相槌（あいづち）と真の割り込みの
  区別を音声レベルでできる唯一級のオープン実装。モデルライセンスは要確認。
- **フルデュプレックス系**（Moshi / NVIDIA PersonaPlex / J-Moshi）: 割り込みは
  創発的に処理されるが、J-Moshi（日本語）は CC BY-NC（研究限定）かつ
  ツール呼び出し不可、PersonaPlex は英語のみ。**Codex ツール実行を伴う本系統
  には時期尚早**。方向性としてのみ追跡。
- **AEC**: ローカルスタックの実用解は WebRTC AEC3。Rust なら
  `webrtc-audio-processing` crate か `sonora`（純 Rust AEC3, NEON 対応・成熟度
  要確認）、システムレベルなら PipeWire `module-echo-cancel`。本リポジトリは
  再生ストリームを自前で持っているため、far-end 参照信号を正確に渡せる
  **パイプライン内 AEC ノードが第一候補**。

### 1.4 改善方針（段階導入）

**Tier 1 — 配線のみで成立する最小バージイン**（新規モデル不要）:

1. 割り込み判定ノード（または turn_detector 拡張）を新設し、
   `playback_state`（再生中か）と VAD/turn イベントを購読。
   「エージェント発話中に速度 ≥250–500ms の連続 speech」で
   `playback_command: pause` を発行 → `playback_queue` に配線。
2. 真の割り込み確定（その後 ASR partial/final が相槌以外を返す）で
   `stop`/`clear` + `dialogue_input: cancel`（既存のキャンセル経路
   `nodes/dialogue_engine/main.py:369-370` を発火）。
   誤検知（無言・相槌のみ）なら `resume`（LiveKit の
   false-interruption-resume パターン）。
3. `cpal_sink` に flush/clear 制御を追加（現状破棄不可）し、停止即応性を
   確保。sink のキュー深度を浅くして滞留を減らす設計も併せて検討。
4. **履歴トランケーション**: 再生済みチャンク数 → TTS 元テキストの
   文字オフセットを対応付け、中断時に「実際に聞こえたところまで」を
   Codex 側の会話履歴に反映する（OpenAI `conversation.item.truncate` 相当）。
   これが無いと LLM は「言い終えたつもり」で会話を続ける。
5. カット時のクリックノイズ対策に 10–30ms のフェードアウト。

Tier 1 の既知の限界: AEC が無いため、スピーカー音量によっては自己発話で
誤発火する。マイク/スピーカー配置依存（要実測）。相槌でも止まる。

**Tier 2 — 標準形（推奨ターゲット）**:

1. **AEC ノード**（Rust, WebRTC AEC3）: mic フレームと再生参照ストリーム
   （playback 経路から分岐）を入力し、エコー除去済み音声を VAD/ASR へ。
2. **意味論ターン判定**: smart-turn v3.1（音声ベース・日本語対応・8MB）を
   VAD 停止時に実行し、固定 750ms 無音より賢いターン終了判定にする
   （早すぎる応答と間延びの両方を削減）。transcript ベースの LiveKit
   turn-detector も比較候補。
3. **相槌（あいづち）フィルタ**: 発話中の「うん/はい/ええ/なるほど」等は
   割り込みとして扱わない。レキシカルフィルタ（ASR partial に対する語彙 +
   モーラ数/持続時間しきい値）から始め、必要なら MaAI VAP 日本語モデルで
   P(backchannel) を判定。
4. **duck-then-confirm**: VAD 発火で即時に再生ゲインを -6〜-12dB に下げ、
   判定確定（150–300ms 後）で停止 or 復帰。誤判定のコストがほぼゼロになり、
   人間の譲り方に近い。
5. ポリシー: 真の割り込み = 残りを破棄 + 履歴トランケート + 新入力に応答。
   誤割り込み = 中断点から再開。

**Tier 3 — 将来**: VAP による turn-shift 先読みでの投機的応答生成、
エージェント側相槌注入、フルデュプレックスモデル（日本語 + 商用可 +
ツール呼び出し対応のものが出たら再評価）。

### 1.5 精査・検証手順

1. 要実測: 現状の割り込み時挙動の録画（割り込み発話 → 何秒喋り続けるか、
   LLM キャンセルがいつ効くか）。`playback_state` / `dialogue_event` の
   タイムスタンプで定量化。
2. 要実測: スピーカー再生中の VAD 誤発火率（AEC 無しの現状値）。
   これが Tier 1 の成立条件を決める。
3. cpal_sink 滞留量の実測（停止コマンド→無音までの遅延上限）。
4. Tier 2 候補モデルの Jetson 上ベンチ（smart-turn v3.1 ONNX / MaAI VAP）。

### 1.6 完了条件

- エージェント発話中の割り込みで、確定後 ≤300ms 程度で音声が止まる。
- 相槌では止まらない（duck のみ）。誤停止時は自然に再開する。
- 中断後の LLM 履歴が実際に再生された内容と一致する。

### 1.7 実装状況（2026-06-13）

計画: `~/.claude/plans/proud-watching-nebula.md`。フルTier1 + AEC を5フェーズで実装中。

- **Phase 0 完了（コントラクト）**: `barge_in.proto`（BargeInEvent）、`PlaybackControlCommand`（cpal_sink向けflush）、`AgentCancelRequest.heard_text`。Python/Rust生成・round-trip確認。
- **Phase 1 完了（cpal_sink flush+フェード）**: `playback_control`入力でバッファ尾（最大1.27s）を破棄＋15ms線形フェード。`FlushSignal`/`FlushControl`、Rust 10ユニットテスト。
- **Phase 2 完了（検知+統括+配線）**: `barge_in_detector`ノード新設（再生中の継続発話を検知、純粋な信号ノード、7テスト）。`dialogue_engine`が`barge_in`/`playback_state`を購読し、`handle_barge_in`で `PlaybackStop`+`PlaybackControlFlush`+`_cancel_active_agent("barge_in")` を発行（2テスト）。`run_live_hardware_voice_session.sh` に配線（barge_in_detector追加、playback_command→playback_queue、playback_control→cpal_sink、barge_in/playback_state→dialogue_engine）。生成グラフの参照は全解決。全211テスト合格。
  - 安全策: stopは dialogue_engine 自身の `playback_state` 追跡でゲート（完了済みrequestへのstopを出さない＝playback_queueの例外回避）。flush seqはセッション内単調増加、command seqはrequest毎0。
- **Phase 3 完了（履歴トランケーション）**: `dialogue_engine` が TTS リクエスト毎の発話テキストを登録し、バージイン時に「完全再生済みチャンク + 中断チャンクの聞こえた接頭辞（`played_frames`/`tts_sample_rate_hz`×`tts_chars_per_second` で推定、句クランプ）」を `heard_text` として算出。`AgentCancelRequest.heard_text` に載せ、かつ**次ターンのユーザー発話に注記前置**（Codex はサーバ側履歴を切り詰めないため）。`--tts-sample-rate-hz`(48000)/`--tts-chars-per-second`(7.0) 設定。3テスト追加（接頭辞算出・注記前置・無再生時None）。全体 dialogue_engine 18テスト合格。
- **Phase 4 再評価中（AEC）**: `barge_in_aec` ノードは Rust 実装として存在し、`webrtc` と `sonora` の backend 切替を持つ。単体テストでは両 backend の最低限の処理は通る。古い実機検証では pass/fail が揺れていたが、主因は backend そのものより、far reference が `cpal_sink` の実再生タイミングではなく source PCM に由来している点だった。現在は `cpal_sink` が CPAL output callback に書いた PCM を `render_reference` として DORA に出力し、検証グラフとライブ生成グラフの `barge_in_aec far` を `cpal_sink/render_reference` に差し替えている。

修正後の実測では、WebRTC AEC3 wrapper + `FLUENT_DIALOGUE_DORA_AEC_STREAM_DELAY_MS=40` が 3/3 repeatability pass。Sonora + 40ms は 2/3 pass。現時点の第一候補は WebRTC。まだ「ライブ音声対話でのバージイン完了」とは言えず、次は実際のTTS再生中にユーザーが割り込んだとき、再生停止・生成キャンセル・VAD/ASR誤発火抑制が同時に成立するかを確認する。評価メモ: `artifacts/aec_research/selection_after_hardware_eval.md`。

- **Phase 5 未（ライブ最終確認・ユーザー実施）**: `FLUENT_DIALOGUE_DORA_ALLOW_LIVE_CODEX_TURN=1 scripts/run_live_hardware_voice_session.sh` で実マイク+スピーカー運用。エージェント発話に被せて割り込み→≤300msでフェード停止・ターンキャンセル・次応答が聞こえた所まで反映・AECで自声誤発火が消える、を確認。要調整: `--barge-in-speech-frames`/`--min-speech-probability`(誤発火・感度)、AEC の far 整合（cpalバッファが大きいと render が echo より先行しすぎる懸念→必要なら `FLUENT_DIALOGUE_DORA_OUTPUT_QUEUE_CAPACITY_CHUNKS` 縮小か far 遅延バッファ）、`--tts-chars-per-second`(トランケーション精度)。

検証メモ: Phase 0-4 全テスト合格（barge_in_aec 5・cpal_sink 10・rust_audio_boundary 4、Python: vad/dialogue_engine/playback/contracts 214）。実装は numpy/pandas 非依存。最終的な「実環境でエコーが十分消えてバージインが成立するか」は Phase 5 のライブ検証でのみ確定する（sonora の実室内性能と far 時間整合が主リスク）。

---

## 2. ツール実行前ナレーションの音声化 — ロジック精査済み・実機検証未了

### 2.1 期待動作

Codex はツール呼び出し前に「これから〜します」という自然文を出すことが
多い。複数ツールの段階実行中に逐次これが読み上げられれば、無音不安を
避けられる。

### 2.2 ロジック精査の結論（確認済み）: 設計上は機能するはず

イベントの流れ:

1. `codex app-server` の `item/agentMessage/delta` を `codex_app_server` ノードが
   **delta 単位で即時** `agent_text` 出力へ転送（蓄積しない）
   （`nodes/dialogue_engine/codex_app_server/main.py:2485-2489`）。
2. `dialogue_engine` は delta を `<think>` フィルタ → TTS 正規化
   （Markdown 等除去）→ 句読点 `.!?。！？、，,\n` チャンカに通し、
   **句読点が来た時点で `tts_text` をフラッシュ**（ターン完了を待たない）
   （`nodes/dialogue_engine/main.py:402-445`）。
3. `tts_backend` は受信順に HTTP 合成（直列・timeout 30s）、`playback_queue` は
   FIFO で即時再生。**ツール状態とは無関係に進む**。
4. ツールイベント（`item/started`/`item/completed`）は `agent_tool` として
   観測系に流れるのみで、**音声化もブロックもしない**。

したがって「プリアンブル文 → ツール実行開始」の順で Codex が出力する限り、
プリアンブルはツール完了を待たずに合成・再生開始される。読み上げ専用の
developer instructions（短文・句点で閉じる・「詳細は画面に出します」等、
`scripts/run_live_hardware_voice_session.sh:201-216`）もこの前提で設計済み。

### 2.3 残存リスク（検証で潰す対象）

| リスク | 内容 |
| --- | --- |
| 順序レース | `agent_text` と `agent_tool` は別トピックで、DORA キュー次第で前後し得る（音声には影響軽微、ダッシュボード表示順に影響） |
| プリアンブル後の長い無音 | プリアンブル読み上げ終了後、長時間ツール中は再び無音になる。tool_event 起点の進捗発話（「実行中です」等）は未実装 |
| キャンセル時の orphan audio | ターンキャンセル後も合成済み音声は再生され続ける（課題 1 と共通） |
| 承認要求との交錯 | approval プロンプト読み上げとプリアンブルが TTS キューで交錯し得る |
| モデル依存 | そもそも Qwen3-Coder がプリアンブルを書くか、reasoning に書いて delta に出さないかはモデル挙動次第（reasoning delta は破棄される: `codex_app_server/main.py:2069-2071`） |

### 2.4 検証手順

1. **fixture 検証**: `tests/fixtures/test_agent_turn_replay.py` 系の仕組みで
   「テキスト delta（句点含む）→ tool started → （遅延）→ tool completed →
   後続 delta」の合成イベント列を流し、`tts_text` / `synth_audio` /
   `playback_state(playing)` のタイムスタンプが tool completed より**前**に
   出ることをログで確認する。
2. **実機検証**: live セッションでツールを 1 回使う依頼（例: ファイル一覧）を
   行い、`dataflows/out/<id>/log_codex_app_server.txt`・`log_tts_backend.txt`・
   `log_playback_queue.txt` の時系列で同様の前後関係を確認 + 体感確認。
3. モデル挙動の確認: Qwen3-Coder が実際にプリアンブルを agent message として
   出すか（reasoning ではなく）を複数タスクで観測。出さない場合は
   developer instructions に「ツール実行前に一文で宣言する」を追加して再評価。
4. （拡張判断）長時間ツール対策として `agent_tool` started → N 秒経過で
   定型進捗文を TTS する機構の要否を決める。

### 2.5 完了条件

- ツールを伴う実タスクで、ツール完了前にプリアンブル音声が再生開始される
  ことがログと体感の両方で確認できる。
- プリアンブルが出ないケースの頻度と原因（モデル/指示）が把握できている。

### 2.6 検証結果（2026-06-12）

**fixture 検証: PASS。** 検証手順 1 を実施した。

- 新規資材: `tests/fixtures/jsonrpc/codex_app_server_tool_narration_fixture.py`
  （プリアンブル文 → tool started → 4 秒待ち → tool completed → 結び文 →
  turn completed を発行する fixture）、`graphs/tool_narration_fixture_smoke.yml`、
  `scripts/run_tool_narration_smoke.sh`（タイムライン解析と PASS/FAIL 判定込み）。
- 結果: プリアンブルの `playback_state: playing` はツール完了の **3.89 秒前**
  （ツール遅延 4.0 秒設定）。テキスト delta 到着から再生開始まで **114ms**
  （TTS は fixture。実 pyopenjtalk では合成時間が加算される）。
- 補足観察: `agent_tool started` と最初のテキスト delta はブリッジ上ほぼ同時刻
  に記録された（2.3 節の順序レースは観測されるが音声経路には無害）。
- 実モデル観測（同日）: ツール誘発プロンプト
  （`tools/llm_dialogue_eval/prompts_tool_probe_ja.tsv`、結果は
  `artifacts/llm_dialogue_eval/runs/codex_tool_probe_v2_qwen3parser/`）で、
  Qwen3-Coder は **ツール試行の前後に日本語ナレーションを豊富に出す**ことを
  確認（「〜を数えます。」「確認してみます。」等）。完了条件の後半も達成。
- ただしツール実行自体が課題 5（sandbox 不全）で失敗するため、
  「ナレーション → ツール成功 → 結果読み上げ」の一気通貫は課題 5 解決後に
  ライブで最終確認する。また、ツール失敗時はモデルが試行錯誤の長文を
  生成し続ける（39〜55 秒/ターン）ことを観測 — 課題 4 の長さガードが
  この面でも必要。

---

## 3. Nemotron ASR — 認識精度とパーシャル表示

### 3.1 現状（確認済み）

モデル: `nemotron-3.5-asr-streaming-0.6b`（NeMo cache-aware streaming,
GPU/fp32/batch1, att_context (56,3) = 320ms チャンク, ローカル .nemo）。

**「確定文しか出ない」原因はダッシュボードではなく ASR ノード側**:

- 配管自体は 3 種対応済み: `TranscriptDelta` / `TranscriptPartial` /
  `TranscriptFinal` の contract・web bridge デコード・dashboard 描画
  （`turn.userLive` への反映）まで全部存在する。
- しかし backend は「小チャンク逐次推論は仮説が不安定」という理由で
  **意図的に final 中心の出力に倒してある**（`nodes/asr/nemotron_streaming/README.md:88-92`、
  delta は append-only の場合のみ: `backend.py:392-406`）。スモークテストも
  「delta 0 件」を期待値にしている。
- さらに推論は `asr_control` でゲートされる: AsrStart（ターン開始 + 1s
  プリバッファ）から holdback 256ms 遅れで進み、**確定テキストは AsrStop
  （ターン終了 = 750ms 無音後）にターン全体を再転写して生成**
  （`backend.py:267-315` `_transcribe_complete_turn`）。
  実態は「ターン末バッチに近いストリーミング」。

つまり認識結果がダッシュボードに出るのは発話終了の 750ms + 再転写時間後で
あり、発話中のフィードバックはほぼ無い。

### 3.2 認識精度の論点（仮説・要実測）

1. **計測が無い**: まず日本語評価セット（自分の声 + マイク実環境で 30〜50
   発話）で CER を取らないと、改善の効果判定ができない。
2. モデル容量: 0.6B 多言語モデルの日本語精度はそもそも限定的な可能性。
3. 設定: `att-context-right-frames` は精度/遅延トレードオフ
   （許容値 0/1/3/6/13、現在 3）。final が全区間再転写である以上、
   final 精度には効かない可能性もある（partial 品質に効く）— 要実測。
4. 言語指定: live hardware は既定 `ja-JP`（`run_live_hardware_voice_session.sh:647`）
   だが、実行時に env で上書きされていないか毎回ログで確認する価値あり
   （file セッションは英語 fixture 用に `en-US` なので混同注意）。
5. 音響経路: 48k→16k リサンプル、マイクゲイン、距離、AEC 無し（課題 1）。
   ターン頭切れ（VAD 立ち上がり遅れ > 1s プリバッファ）の可能性。
6. GPU 競合: vLLM と同居。推論遅延が holdback と相互作用していないか。

### 3.3 改善レバー

設定レベル（小）:

- `FLUENT_DIALOGUE_DORA_NEMOTRON_ATT_CONTEXT_RIGHT_FRAMES`（精度/遅延）、
  `FLUENT_DIALOGUE_DORA_NEMOTRON_CONTROL_HOLDBACK_FRAMES`（partial の早さ）、
  プリバッファ・無音閾値の調整。

アーキテクチャレベル（中）:

- **パーシャル復活**: 「不安定な仮説」を安定化フィルタ（直近 N ステップで
  共通の確定プレフィクスのみ partial として出す等）で抑えて再有効化する。
  ダッシュボード側は受け口が既にあるため、ASR ノードのみの変更で済む。
- **二段デコード**: 発話中は streaming partial（低遅延・粗い）、AsrStop 後は
  現行の全区間再転写を final として併用（現行構造と相性が良い）。

モデルレベル（大・候補は要評価）:

- 日本語特化/強化モデルへの差し替え評価: ReazonSpeech 系（NeMo ベース日本語）、
  kotoba-whisper / whisper-large-v3-turbo（faster-whisper, 疑似ストリーミング）、
  Nemotron ASR の上位サイズ等。ストリーミング適性・Jetson での RTF・
  ライセンスを含めて比較表を作る。

### 3.4 精査・検証手順

1. 評価ハーネス作成: 既存の `wav_pcm_source` + `asr_nemotron_smoke` 構成を
   流用し、日本語 wav セット → TranscriptFinal を収集して CER 算出。
2. 現行設定でベースライン CER / final 遅延（発話終了→transcript 表示）を実測。
3. att_context / holdback / 言語指定のスイープ。
4. パーシャル安定化の試作 → ダッシュボード `userLive` で体感確認。
5. 代替モデルの同一セット評価。

### 3.5 完了条件

- 日本語 CER とレイテンシのベースラインと改善後の数値が記録されている。
- 発話中にダッシュボードへ逐次テキストが表示される。
- 体感の誤認識が課題 4 の評価を妨げないレベルになる。

### 3.6 実測結果（2026-06-12、合成音声ベースライン）

評価ハーネス `tools/asr_eval/`（README 参照）を作成し、pyopenjtalk 合成の
日本語 35 発話（core 30 + numeric 5、計約 100 秒）で実測した。
結果は `artifacts/asr_eval/runs/*/summary.json`。設定は live 同等
（`ja-JP` / att_context (56,3)、ノード同一の backend を直接駆動）。

| 条件 | core CER | numeric CER | finalize p50/p95 | partial が出た発話 |
| --- | --- | --- | --- | --- |
| クリーン | **1.28%** | 0% | 0.99s / 1.38s | 5/35 |
| SNR20dB・-6dB | 3.85% | 5.5% | 1.26s / 2.03s | 4/35 |
| SNR10dB・-6dB | **12.2%** | 16.4% | 1.17s / 1.41s | 3/35 |

主な所見:

1. **クリーン音声ならモデルの日本語認識はほぼ完璧**（誤り 3 件中 2 件は
   精度→制度・閉めた→占めた の同音異義漢字選択）。数値も漢数字のまま出力され
   表記揺れ問題なし。→ 体感の「認識能力が低い」は**音響経路起因が濃厚**。
2. **ノイズに弱い**: SNR10 で CER が約 10 倍悪化。特に短い命令発話が壊滅
   （「音楽を止めて」→「本作を染めて」、「うん、わかった」→空文字）。
   実マイクの遠距離・環境音・エコーがこのレンジに入っている可能性が高い。
3. **パーシャル枯渇は backend 自体の挙動**: 本ハーネスは logic 層の
   holdback ゲーティングを介さず backend を直接駆動しても 5/35 発話しか
   partial が出ない。原因は NeMo cache-aware デコードが文脈確定まで
   トークンを出さない挙動側にある（発話単位で全か無かの二峰性）。
4. **finalize 約 1 秒**（全区間再転写、RTF 0.36）。無音検出 750ms と合わせて
   発話終了から約 1.8 秒後に transcript が出る。応答性の主要因の一つ。
   ストリーミング推論自体は RTF 0.17 と高速なので、stop 時の再転写を
   「最後のストリーミング仮説の採用 + 必要時のみ再転写」にすれば短縮余地大。

次のアクション（優先順）:

1. ~~実マイク録音セットでの再評価~~ **済**（3.7 節）
2. **マイクデバイスの A/B**（3.7 の結論を受けた最優先アクション）:
   PowerConf S3 vs C920 内蔵マイク等、DSP 加工の少ない入力での比較録音。
3. パーシャル復活: att_context_right を上げた場合の partial 頻度と
   安定化フィルタの試作（3.3 のアーキテクチャレベル施策）。
   実マイクではパーシャル 0/35 のため重要度が上がった。
4. finalize 短縮: 二段デコード化の検討。

### 3.7 実マイク実測結果（2026-06-12、PowerConf S3・35 発話）

`tools/asr_eval/record_set.py` でユーザー本人が収録（ライブと同一マイク
`plughw:CARD=S3,DEV=0`、48kHz mono）。結果:

| 条件 | core CER | 備考 |
| --- | --- | --- |
| 合成クリーン（再掲） | 1.28% | |
| **実マイク gain 1.0** | **13.5%**（尾部切断疑い 16 件除外でも 11.9%） | パーシャル 0/35 |
| 実マイク gain 4.0（live 相当） | 15.2% | クリップの上乗せは +1.7pt のみ |

分析（根拠つき）:

1. **主因はマイク（PowerConf S3）の通話用 DSP と推定**。録音の推定 SNR は
   平均 107dB（発話前がほぼデジタル無音）= デバイス内ノイズゲートが作動して
   おり、ゲート立ち上がりが語頭の低エネルギー音素を破壊している。誤りパターン
   が語頭破壊に集中（「おはようございます」→空、「音声認識」→「性認識」、
   「午後三時」→「ブグを山地」）することと整合。ノイズ過多ではなく
   「会議通話向けに加工された信号が ASR に不適合」という構図。
2. **gain 4.0（live の media_graph 設定）は主因ではない**（+1.7pt）。NeMo の
   特徴量正規化が振幅差を吸収する。ただし無益なクリップ歪みではあるので、
   デバイス選定後に VAD 感度（Silero は振幅依存）と合わせて再調整する
   （`FLUENT_DIALOGUE_DORA_ASR_LINEAR_GAIN`）。単独で先に下げると VAD の発話検出を
   壊す可能性があるため保留。
3. 測定上の注意: 初版 record_set.py は Enter と同時に録音停止していたため
   35 件中 18 件で語尾 200ms 未満の切断が混入（修正済み: 停止前 0.8s 猶予）。
   また「下げて」→「下げてください」等の挿入誤りは読み上げ時の言い回し逸脱の
   可能性がある。これらを除いても CER は約 12% で結論は変わらない。
4. 実マイクではストリーミングパーシャルが 1 件も出ない（合成でも 5/35）。
   ダッシュボードの逐次表示は現状の backend 挙動では成立しない。

補足（2026-06-13 確認）: PowerConf S3 の DSP は Linux からは無効化できない。
ALSA ミキサーは音量/ミュートのみ、USB オーディオクラスにも処理ユニットの
公開なし、生マイク信号への代替経路なし。

Web 調査 + 実機 HID 解析の結論（確度高）:

- **DSP 無効化の公開手段は存在しない。** 加工は S3 が USB/BT で出す唯一の
  音声ストリームに焼き込まれている。レビューでも「DSP ノイズ低減はオフに
  できない」と明言（gadgetexplained 2020）。
- **S3 の設定はモバイル AnkerWork アプリ（Bluetooth 経由）でのみ可能。**
  デスクトップアプリは S3 非対応。実機で見つけた USB HID インターフェース
  （Report ID 3 のベンダーページ）は電話制御用（ミュート同期等）で設定
  チャンネルではない。リバースエンジニアリングの前例もゼロ。
  → HID 経由での DSP オフは見込みなし。
- **唯一のマイク関連設定は Single/Multi-Person モード**（アプリのみ）。
  集音範囲と全/半二重を変えるが DSP バイパスではない。ただし処理挙動は
  変わるため、スマホで切り替えて（設定はデバイスに永続化されると推測）
  A/B する価値はある（低コスト）。
- **本件の語頭破壊と一致する既知事象**: PowerConf 系には「アイドル後に
  音声の先頭数語/数秒を切り落とす idle ゲーティング」が報告されており
  （Rhasspy コミュニティ）、対策は**キャプチャストリームを常時開いたままに
  して deスリープさせない**こと。3.7 の「語頭破壊」と症状が合致するため、
  S3 を使い続ける場合の有力な緩和策（発話間でストリームを閉じない）。
- **二重処理の警告**: Home Assistant の事例では PowerConf 系 + Whisper を
  直結すると約 99% だったが、**デバイス DSP の上にソフト NS/AGC を重ねると
  約 50% に崩壊**。本パイプラインの media_graph `--linear-gain` は単純ゲイン
  なので NS/AGC ではないが、Silero VAD 等で前処理を重ねていないか要確認。

出典: us.ankerwork.com/products/a3302、service.ankerwork.com（ファーム更新
記事）、gadgetexplained.com（PowerConf レビュー）、community.rhasspy.org
（idle ゲーティング/キープアライブ）、home-assistant.io（2023 wakewords、
二重処理での精度崩壊）、github.com/erans/anker-powerconf-c200-linux-tools
（C200 webcam の UVC 拡張ユニット解析。speakerphone の前例ではない）。

### 3.8 マイク A/B 確定結果（2026-06-13、DJI Mic 3 で主因確定）

DJI Mic 3 を Bluetooth（HFP/mSBC, 16kHz mono）で接続し、同一 35 文を
ユーザー本人が収録して評価（`artifacts/asr_eval/runs/dji_bt_v1/`）。

| 条件 | core CER | numeric CER | 完全一致 |
| --- | --- | --- | --- |
| 合成クリーン | 1.28% | 0% | — |
| **DJI Mic 3 (BT/mSBC 16k)** | **6.42%** | 27.4%※ | 17/35 |
| PowerConf S3 実マイク gain1.0 | 13.5% | 23.3% | 15/35 |
| PowerConf S3 実マイク gain4.0 | 15.2% | 21.9% | — |

※numeric は 5 文中 2 文（七時→サ指示、移動したし）が外れて振れた値。
同一単文比較では DJI 6.7%（精度→制度のみ）vs PowerConf 60〜73%。

**結論: 課題 3 の認識精度低下の主因は PowerConf S3 の DSP で確定。**
クリーンなマイクに替えるだけで core CER が 2 倍以上改善し、DJI の誤りの
大半は「降っています→降ってます」「。→?」等の正書法差で実質的な音響誤認識は
わずか。当初想定（HFP 電話品質で不利）を覆し、Bluetooth 経由でも実用十分
だった。

確定した対策方針: **ASR 入力マイクを S3 から分離する。**

- **本番推奨は DJI Mic 3 の USB-C レシーバー(RX)**: 48kHz クリーン、
  GDM/Bluetooth の不安定要素なし、ALSA 直結で DORA と相性が良い。
  Bluetooth は主因確定には十分だったが、本番には以下の弱点がある:
  - SCO リンクが接続直後不安定（初回テストクリップが文字化けした）。
  - GDM の PipeWire 競合回避（`systemctl stop user@122.service`）が
    再起動で揮発する。恒久化するなら gdm ユーザーの pipewire/wireplumber を
    mask する必要がある。
  - HFP は 16kHz mono が上限（RX なら 48kHz）。
- S3 はスピーカー（出力）専用に降格。再生中のエコーは課題 1 Tier 2 の
  パイプライン AEC で処理する構成と整合する（S3 の内蔵 AEC に頼らない）。

ライブ系への適用（2026-06-13 実施・cpal スモークで検証済み）: DJI Mic 3 の
USB-C レシーバー(Rx)を採用。`run_live_hardware_voice_session.sh` の既定を変更:

- `FLUENT_DIALOGUE_DORA_CPAL_INPUT_DEVICE_ID` 既定 `alsa:hw:CARD=S3,DEV=0` →
  **`alsa:plughw:CARD=Rx,DEV=0`**。
- cpal の `capture_channels` 既定を **2**（Rx ネイティブのステレオ）に。
- 出力（cpal_sink）は `alsa:hw:CARD=S3` のまま = S3 はスピーカー専用に降格。
- 入力バックエンドは `cpal` のまま（変更なし）。

設計（関心の分離を厳守）: **Rx のハードウェアは S24_3LE/2ch/48k のみ**対応
（`/proc/asound/card4/stream0`）。cpal 0.18.1 の ALSA は S24_3LE 非対応
（`I24` は 4 バイトの `S24LE` のみ、S24_3LE はソースで明示的にコメントアウト）
のため `hw:` では開けず、`plughw` 経由で開く。plug が必ず何らかの形式変換を
する以上「入力で無変換」は不可能なので、**入力では非可逆な縮約を一切せず、
可逆な f32le で受ける**方針にした:

- 入力層(cpal_capture)は `plughw:CARD=Rx` を **48k/2ch/f32le** で開く。plug の
  S24_3LE→f32 は無損失（24bit は f32 仮数に完全に収まる）で、量子化等の媒体
  判断を含まない＝「デバイスを忠実に読むだけ」。レート・チャンネルも触らない。
- 媒体変換すべて — **16bit 化(f32→s16)、48k→16k リサンプル、2ch→1ch
  ダウンミックス、gain** — は **media_graph(GStreamer audioconvert +
  audioresample + volume)が担う**＝本来の責務。S3+cpal 時代の「cpal で取得 →
  media_graph で変換」と同じ層構造。

このため cpal_capture と共有 `rust_audio_boundary` を f32le 対応に拡張した
（proto は `SAMPLE_FORMAT_F32LE = 2` を既に定義済み。Rust 側の未実装を実装した
だけでコントラクト拡張ではない）。cpal_capture はサンプル型を一般化し、
s16le なら i16、f32le なら f32 ストリームを受ける。

検証: 品質差は無い（16bit でもマイク SNR を遥かに超える）ため目的は層の正しさ。
cpal スモークで f32le 捕捉を確認（`input_device=Wireless Mic Rx`、48k/2ch、
25 チャンク/12000 フレーム/96000 バイト、実音声 nonzero 4318）。
`rust_audio_boundary` 単体テスト 4 passed、cpal_capture 3 passed、
audio_device+media_graph pytest 53 passed。生成された
`graphs/out/live_hardware_voice_session.local.yml` で cpal_capture(plughw:Rx,
48k/2ch/f32le) → media_graph_asr(in 48k/2ch/f32le → out 16k/1ch/s16le,
linear-gain 4.0) → ASR の配線を確認。

注意点:
- カード名 `Rx` は USB 列挙順で変わり得る。固定するなら実機の安定した
  カード名/ID に `FLUENT_DIALOGUE_DORA_CPAL_INPUT_DEVICE_ID` で合わせる。
- `--linear-gain` は cpal 既定の 4.0（S3 で調整した値）のまま。Rx は
  実測ピーク約 -30dBFS と低めなので 4.0 は概ね妥当だが、VAD(Silero は振幅
  依存)と合わせて `FLUENT_DIALOGUE_DORA_ASR_LINEAR_GAIN` で実機調整の余地あり。
- Rx ステレオの 2ch は audioconvert が平均でダウンミックス。将来 R が
  セーフティトラック等なら media_graph で明示的なチャンネル選択に変える
  余地あり（媒体層で扱うべき判断。入力層には持ち込まない）。
- arecord/plughw を直接使う検証時は PipeWire が Rx を占有しないこと。
- 最終確認（マイク前での実セッション + ツール一気通貫=課題5.4）は未実施。

残課題（マイク交換後も有効）:

1. パーシャル枯渇（partial 0/35）は backend 起因で未解決。3.3 のアーキ施策。
2. finalize 約 1 秒（全区間再転写）の短縮。

---

## 4. LLM の日本語対話品質

### 4.1 現状（確認済み）

- モデルは **Qwen3-Coder-30B-A3B**（コーディング/エージェント特化 MoE,
  NVFP4 量子化）を Codex CLI（コーディングエージェント前提のシステム
  プロンプト）経由で使用。
- その上に読み上げ用 developer instructions（一〜二文・前置き禁止・
  Markdown 禁止等）で強く制約している。
- トークン速度は十分（ユーザー所感）。

### 4.2 仮説（優先順）

| 仮説 | 内容 | 切り分け方法 |
| --- | --- | --- |
| H1: ASR 起因 | 誤認識テキストへの応答なので噛み合わない | ASR をバイパスしてテキスト直接入力で評価 |
| H2: モデル特性 | Coder 系は日本語雑談・対話が弱い | 同条件で非 Coder 系（例: Qwen3-30B-A3B-Instruct 系）に差し替え比較 |
| H3: プロンプト | Codex のコーディング向け文脈 + 厳しい読み上げ制約が不自然さを生む | instructions の A/B、制約の緩和テスト |

ユーザー仮説は H1。ただし H2 も濃厚（Coder モデルの選定理由はツール呼び出し
適性であり、対話品質とトレードオフになっている）。H1 と H2 は独立に効くため
両方確認する。

### 4.3 切り分け手順

1. **課題 3 のベースライン CER を先に取得**（ASR 入力品質の定量化）。
2. **ASR バイパス評価**: 既存のテキストターン経路
   （`scripts/run_codex_app_server_live_smoke.sh` /
   `FLUENT_DIALOGUE_DORA_ALLOW_LIVE_CODEX_TURN=1` の live turn smoke）で日本語の
   対話プロンプト 10〜20 件を直接投入し、応答の日本語品質を評価。
   ここで品質が十分なら H1 が主因と確定。
3. 不十分なら **モデル A/B**: `FLUENT_DIALOGUE_DORA_VLLM_MODEL` /
   `FLUENT_DIALOGUE_DORA_VLLM_SERVED_MODEL_NAME` で非 Coder 系に差し替えて同一
   プロンプト比較。制約: ツール呼び出し（hermes parser / responses API）と
   Jetson メモリ（現行 NVFP4 30B 相当）を満たすこと。
4. H3 確認: developer instructions を最小化した状態と現行の比較。
5. ASR 改善（課題 3）後に音声経由で再評価し、期待値に達するか判定。

### 4.4 完了条件

- H1/H2/H3 の寄与が切り分けられ、採用モデル + instructions が決まる。
- 音声経由の対話で「噛み合わない」事例の頻度が許容内になる。

### 4.5 切り分け結果（2026-06-12、ASR バイパス評価）

評価ハーネス `tools/llm_dialogue_eval/`（日本語 15 プロンプト、
codex フルスタック経由 / vLLM 直接の 2 モード）で実測。
結果は `artifacts/llm_dialogue_eval/runs/{codex_v1,vllm_v1}/responses.jsonl`。

**結論: H1（ASR起因）だけではない。H2・H3 がそれぞれ実在する。**

| 観点 | codex 経由 | vLLM 直接（同一 instructions） |
| --- | --- | --- |
| 形式遵守（一〜二文・Markdown禁止） | **違反あり**: d-015 が番号付きリスト 587 字・30 秒、d-003 も Markdown 太字 | **全 15 件遵守**（最長 45 字） |
| 内容の質 | 比較的丁寧で文脈的（d-013 は誤認識語「四両」に確認質問を返せた） | 短いが雑になりがち（d-009 は指示に答えていない） |
| 誠実性 | **虚偽の動作報告**: d-010「音声入出力を無効化しました」（そんな操作はしていない） | **捏造が悪化**: d-011「今日は快晴です。気温は25度前後」（天気を知る術がない） |
| コーディング文脈への脱線 | d-012 で「コードを削除してください」等に脱線、d-008 で禁止された機能一覧を読み上げ | ほぼ無し |
| TTFT / 速度 | 平均 0.51s（十分高速） | 総時間 0.6〜2.5s |

解釈:

- **H3（Codex スタックの影響）= 長文・Markdown 違反の主因。**
  developer instructions は thread/start で送信されている（コード確認済み）
  にもかかわらず、Codex の大きなコーディング向けシステムプロンプト配下では
  形式制約が負ける。同じモデル単体では完全に守れることから、モデルの
  能力不足ではなくプロンプト競合。
- **H2（モデル特性）= 誠実性の欠如は両モードで発生。** 実行していない操作の
  完了報告・知らないことへの捏造は Qwen3-Coder（NVFP4）自体の対話挙動。
  ASR を完璧にしても残る品質問題。
- **H1（ASR起因）も実在するが説明力は部分的**: 誤認識語への応答は
  ケースバイケース（d-013 は聞き返せたが d-011/d-012 は誤認識のまま進行）。
  課題 3 の結果（実マイク CER が高い疑い）と合わせ、誤認識頻度を下げることは
  依然有効。

対策候補（優先順）:

1. **音声サーフェス側の長さガード**（instructions に依存しない安全網）:
   dialogue_engine で読み上げを最初の N 文 / M 文字で打ち切り
   「詳細は画面に出します」を付加する。H3 由来の 30 秒読み上げを構造的に防ぐ。
2. **instructions への誠実性条項の追加**（「していない操作を実行したと
   言わない」「知らないことは分からないと言う」「三文以内」）。
   → 同日 A/B 実施（`codex_v2_honesty`、結果は 4.6 節）。
3. **モデル A/B**: 非 Coder 系（対話向け instruct モデル）への差し替え評価。
   要件: ツール呼び出し（tool parser / responses API）対応 + Jetson メモリ。
   H2 の誠実性問題がモデル起因かを確定できる。
4. ASR 改善（課題 3）後に音声経由で再評価。

### 4.6 誠実性指示の A/B（2026-06-12、`codex_v2_honesty`）

4.5 の対策候補 2 を同日実施。developer instructions 末尾に
「知らないことは分からないと言う」「していない操作を実行したと言わない」
「三文以内・列挙禁止」を追記して codex 経由で再評価した。

- 改善: d-012 が「権限がありません」と正直な回答に（捏造消失）、
  d-011 の天気捏造も消失、d-015 は 587 字リスト → 3 文に。
  平均応答長 104 → 76 字。
- 残存: d-008（能力一覧の読み上げ、禁止事項）と d-009（番号付きリスト）は
  指示を強めても違反。d-010 の虚偽動作報告も形を変えて残存。
- 結論: **instructions の改善は有効だが上限がある**。形式と長さは
  dialogue_engine 側の構造的ガード（対策候補 1）で保証し、誠実性は
  モデル A/B（対策候補 3）で詰めるのが現実的。

---

## 5. Codex ツール実行の不全（新規発見 2026-06-12）

課題 4 の評価中に発見した、独立性の高い不具合。音声対話の「エージェントが
作業できる」価値そのものを塞いでいたため課題として追加する。

### 5.1 事象と原因（特定済み）

ツール誘発プロンプト 3 件でツール呼び出しが一度も成功しなかった。
原因は二層:

1. **vLLM の hermes ツールパーサが Qwen3-Coder の呼び出しを取りこぼす。**
   `artifacts/vllm/eval_session.log` に `hermes_tool_parser.py` の
   JSONDecodeError、および `/v1/responses` への 400
   （`'dict object' has no attribute 'parameters'`）。
   → **対処済み**: vLLM 0.22.1 には専用パーサがあるため
   `scripts/run_qwen3_coder_vllm_server.sh` の既定を `qwen3_coder` に変更した。
2. **パーサ修正後もツール実行が sandbox エラーで全滅。**
   codex の Linux サンドボックスは Landlock 前提だが、この機体の
   tegra カーネルは LSM が `capability,yama,apparmor` のみで
   **Landlock が無効**（`/sys/kernel/security/lsm` 確認済み）。
   live セッション既定も `--sandbox read-only`（script:415-416）のため、
   **ライブ音声対話でもツール実行は常に失敗していた**はず。
   失敗時はモデルが試行錯誤ナレーションを延々と生成する（最長 55 秒/ターン）。

### 5.2 対処方針（要決定）

| 案 | 内容 | トレードオフ |
| --- | --- | --- |
| A. sandbox 無効 + 承認ゲート | `FLUENT_DIALOGUE_DORA_CODEX_SANDBOX=danger-full-access` + `approval_policy` を `untrusted`/`on-request` にして既存のダッシュボード承認フローを通す | 分離なし。音声起点のコマンド実行を承認 UI に依存させる運用 |
| B. カーネルで Landlock を有効化 | tegra カーネルの `CONFIG_SECURITY_LANDLOCK` + `lsm=` ブートパラメータ追加 | カーネル再構築/再起動が必要。本筋だが重い |
| C. コンテナ等の外部分離 | codex をコンテナ/ユーザ分離で包み sandbox は無効 | 構成が増える。ROS2/デバイスアクセスとの整合に注意 |

推奨: 短期 A（承認フローは実装済み・検証済みのため）→ 中期 B。

**決定（2026-06-12）**: カーネル再ビルドは見送り、案 A を採用（ユーザー合意）。
`run_live_hardware_voice_session.sh` の既定を
`sandbox=danger-full-access` / `approval_policy=untrusted` に変更済み
（untrusted = 既知の安全な読み取りコマンドは自動実行、それ以外は
ダッシュボード承認）。env でいつでも上書き可能。

### 5.3 適用結果（2026-06-12）

ツールプローブ（`codex_tool_probe_v3_nosandbox`）で **シェルコマンドの実実行を
確認**（vLLM へのリクエストが 1 ターンに 2 ラウンド = ツール結果を受けて
再生成しており、応答にリポジトリの実ファイル構成が反映された）。

同時に信頼性の問題を 2 件発見:

1. **ツール呼び出し構文の生テキストリーク**: モデルが崩れた形式
   （`<function=exec_command>` 開始 + `</tool_call>` 終了の混在）で呼び出しを
   出すと qwen3_coder パーサも取りこぼし、構文がそのまま agent text に漏れる
   （3 プローブ中 1 件で発生）。**ライブでは TTS がこの構文を読み上げてしまう**。
   → 対策: dialogue_engine の TTS 正規化に tool-call 構文パターンの除去を追加
   （課題 4 対策 1 の「読み上げガード」実装に含める。ダッシュボード側には
   原文が残るので失敗の隠蔽にはならない）。
2. **commandExecution が tool_event に投影されない**: `item/started`/`completed`
   のうち mcpToolCall / dynamicToolCall のみ投影し、commandExecution は意図的に
   破棄している（`codex_app_server/main.py:2090-2094`）。シェルコマンドは
   音声エージェントで最頻のツール種別なのに、ダッシュボードからも
   対話エンジンからも実行が見えない。→ 投影対象に追加すべき
   （将来の「実行中です」進捗発話の前提にもなる）。

### 5.4 完了条件

- ライブ構成で「ファイルを確認して」等の依頼に対し、ツールが実際に成功し、
  プリアンブル → 実行 → 結果読み上げが一気通貫すること（課題 2 の最終確認を
  兼ねる。マイク前での実セッション確認が必要なためユーザー実施）。
- ツール構文リークが読み上げに乗らないこと（ガード実装後に再確認）。

---

## 6. 課題間の依存関係と推奨着手順序

```text
課題3 (ASR 実測・改善)  ──→  課題4 (LLM 切り分けは ASR ベースライン後)
課題2 (検証のみ・低コスト) — 独立、いつでも可
課題1 (バージイン)        — 独立。ただし Tier2 の AEC は課題3 の音響品質にも効く
```

推奨順序と進捗（2026-06-12 更新）:

1. ~~課題 3 の実測~~ **済**（3.6 節。ハーネス: `tools/asr_eval/`）
2. ~~課題 4 の ASR バイパス評価~~ **済**（4.5–4.6 節。ハーネス:
   `tools/llm_dialogue_eval/`）
3. ~~課題 2 の検証~~ **済**（2.6 節。`scripts/run_tool_narration_smoke.sh`）

次にやるべきこと（優先順）:

1. **課題 5 の sandbox 方針決定 + ライブでのツール一気通貫確認**
   （短期案 A なら設定変更のみ。課題 2 の最終確認を兼ねる）。
2. **課題 3: 実マイク録音セットでの CER 再評価**（要ユーザー録音。
   クリーン 1.3% との差で音響経路の寄与が確定する）。
3. **課題 4: dialogue_engine の読み上げ長ガード実装**（構造的な安全網。
   ツール失敗時の長文暴走（課題 5）にも効く）+ モデル A/B。
4. **課題 1 Tier 1 実装**（配線 + 判定 + sink flush + トランケーション）→
   実測を踏まえて Tier 2（AEC → 意味論ターン判定 → 相槌フィルタ）。
   課題 3 のパーシャル復活・finalize 短縮は並行可能。

---

## 7. 参考資料（課題 1 調査の出典）

- LiveKit turns / adaptive interruption / turn-detector model:
  <https://docs.livekit.io/agents/build/turns/>,
  <https://livekit.com/blog/adaptive-interruption-handling>,
  <https://huggingface.co/livekit/turn-detector>
- Pipecat smart-turn v3/v3.1（日本語対応・8M params・BSD-2）:
  <https://huggingface.co/pipecat-ai/smart-turn-v3>,
  <https://www.daily.co/blog/announcing-smart-turn-v3-with-cpu-inference-in-just-12ms/>
- 京大 MaAI / VAP（日本語ターンテイキング・相槌予測, CPU リアルタイム）:
  <https://github.com/MaAI-Kyoto/MaAI>, <https://arxiv.org/abs/2401.04868>
- TEN VAD / Turn Detection: <https://github.com/ten-framework/ten-vad>,
  <https://github.com/TEN-framework/ten-turn-detection>
- OpenAI Realtime の割り込み + truncate パターン:
  <https://platform.openai.com/docs/guides/realtime-conversations>
- NVIDIA NeMo voice agent example（parakeet EOU + 相槌 ignore list, EN）:
  <https://github.com/NVIDIA-NeMo/NeMo/blob/main/examples/voice_agent/README.md>
- フルデュプレックス: Moshi <https://github.com/kyutai-labs/moshi>,
  J-Moshi（日本語, CC BY-NC）<https://github.com/nu-dialogue/j-moshi>,
  NVIDIA PersonaPlex <https://huggingface.co/nvidia/personaplex-7b-v1>
- AEC: PipeWire echo-cancel <https://docs.pipewire.org/page_module_echo_cancel.html>,
  webrtc-audio-processing (Rust) <https://github.com/tonarino/webrtc-audio-processing>,
  sonora（純 Rust AEC3）<https://github.com/dignifiedquire/sonora>
