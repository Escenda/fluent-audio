"""Evaluate Japanese dialogue quality of the voice agent LLM, bypassing ASR.

Two modes isolate where quality is lost (docs/課題/voice-dialogue-quality.md 課題4):

- ``--mode codex``: the full voice stack minus ASR — text turns through
  ``codex app-server`` (same model/provider/developer-instructions wiring as
  the live session). Measures what the voice user would get with perfect ASR.
- ``--mode vllm``: the bare model — direct ``/v1/chat/completions`` against the
  local vLLM server with the same developer instructions as system prompt.
  Differences against codex mode expose the Codex stack's影響 (H3).

Run inside the repo uv environment (vLLM server must be up):

    VLLM_API_KEY=dummy uv run --extra dev --extra dora python \
        tools/llm_dialogue_eval/eval_dialogue.py --mode codex --run-name codex_v1
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

DEFAULT_BASE_URL = "http://127.0.0.1:18080/v1"
DEFAULT_MODEL = "qwen3.6-27b-mtp-pi-tune-nvfp4"
DEFAULT_PROVIDER = "vllm_local"

# scripts/run_live_hardware_voice_session.sh の既定と同一に保つこと。
DEFAULT_DEVELOPER_INSTRUCTIONS = (
    "あなたは音声対話でユーザーに聞こえる返答本文だけを書きます。"
    "返答本文はTTSで即座に読み上げられるため、自然な短い日本語にしてください。"
    "原則として一文か二文で、最初の文で直接答えてください。"
    "最初の文は短くし、必ず句点「。」または疑問符「？」で閉じてください。"
    "最初の文がそのまま先に読み上げられる前提で、前置きや能力紹介を書かないでください。"
    "Markdown、箇条書き、コードブロック、ファイルパス、コマンド例、長い列挙、内部タグ、思考タグ、未加工のツール出力は禁止です。"
    "ファイル作成、ファイル編集、Python、JavaScript、コード、コマンド、ツールの機能一覧は読み上げ本文に出してはいけません。"
    "詳細や一覧が必要な場合は、読み上げ本文では「詳細は画面に出します。」のように短く述べるだけにしてください。"
    "能力紹介、機能一覧、ファイル作成・編集・コード生成などの例示を、ユーザーが明示的に求めていない限り話さないでください。"
    "ユーザーが何ができるか、どんなツールを使えるかを聞いても、CLI、Codex、ファイル操作、コード編集の機能一覧を読み上げないでください。"
    "その場合は、必要に応じて確認や作業を進められることだけを短く伝え、具体的な希望を一つ尋ねてください。"
    "ツール実行や詳しい調査が必要なときも、読み上げ本文では短く状況だけ伝え、詳細は画面やログに出す前提で進めてください。"
    "質問が曖昧な場合は、短い確認質問を一つだけ返してください。"
)


def parse_prompts(path: Path) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t", 2)
        if len(parts) != 3:
            raise ValueError(f"{path}:{line_number}: expected id<TAB>category<TAB>text")
        rows.append((parts[0], parts[1], parts[2]))
    return rows


def build_codex_command(base_url: str, model: str, provider: str) -> list[str]:
    return [
        "codex",
        "app-server",
        "--listen",
        "stdio://",
        "--disable", "apps",
        "--disable", "multi_agent",
        "--disable", "multi_agent_v2",
        "--disable", "image_generation",
        "--disable", "web_search",
        "--disable", "browser_use",
        "--disable", "computer_use",
        "--disable", "standalone_web_search",
        "--disable", "web_search_request",
        "--disable", "web_search_cached",
        "-c", 'web_search="disabled"',
        "-c", "tools.web_search=false",
        "-c", f"model={json.dumps(model)}",
        "-c", f"model_provider={json.dumps(provider)}",
        "-c", f'model_providers.{provider}.name="Local vLLM"',
        "-c", f"model_providers.{provider}.base_url={json.dumps(base_url)}",
        "-c", f'model_providers.{provider}.env_key="VLLM_API_KEY"',
        "-c", f'model_providers.{provider}.wire_api="responses"',
    ]


def run_codex_mode(prompts, args) -> list[dict]:
    from nodes.dialogue_engine.codex_app_server.main import (
        CodexAppServerConfig,
        ProjectedTextDeltaEvent,
        ProjectedToolEvent,
        ProjectedTurnDoneEvent,
        SubprocessCodexJsonRpcTransport,
    )
    from fluent_dialogue_dora.contracts import AgentTurnRequest

    config = CodexAppServerConfig(
        command=tuple(build_codex_command(args.base_url, args.model, args.provider)),
        timeout_seconds=args.timeout_seconds,
        cwd=os.environ.get("FLUENT_DIALOGUE_DORA_CODEX_CWD", "/tmp/fluent-dialogue-dora-codex-empty-cwd"),
        model=args.model,
        model_provider=args.provider,
        developer_instructions=args.developer_instructions,
        sandbox=args.sandbox,
        approval_policy="never",
        approvals_reviewer="user",
    )
    Path(config.cwd).mkdir(parents=True, exist_ok=True)
    results = []
    for index, (prompt_id, category, text) in enumerate(prompts):
        session_id = f"dialogue-eval-{args.run_name}-{prompt_id}"
        request = AgentTurnRequest(
            session_id=session_id,
            user_turn_id=f"user-{prompt_id}",
            assistant_turn_id=f"assistant-{prompt_id}",
            seq=0,
            text=text,
        )
        # プロンプト毎に新規プロセス: 実運用の「セッション開始→ターン」と同型で、
        # 中断ターンの残留通知が次プロンプトを汚染しない。
        transport = SubprocessCodexJsonRpcTransport(config)
        started = time.perf_counter()
        first_delta_s = None
        response_parts: list[str] = []
        tool_events: list[dict] = []
        text_chars_before_first_tool = None
        status = "completed"
        try:
            for event in transport.stream_turn(request):
                if isinstance(event, ProjectedTextDeltaEvent):
                    if first_delta_s is None:
                        first_delta_s = time.perf_counter() - started
                    response_parts.append(event.to_contract().text)
                elif isinstance(event, ProjectedToolEvent):
                    tool = event.to_contract()
                    if tool.event == "started" and text_chars_before_first_tool is None:
                        text_chars_before_first_tool = len("".join(response_parts))
                    tool_events.append(
                        {
                            "at_s": round(time.perf_counter() - started, 3),
                            "tool_name": tool.tool_name,
                            "event": tool.event,
                        }
                    )
                elif isinstance(event, ProjectedTurnDoneEvent):
                    break
        except Exception as error:  # 評価続行のため個別失敗を記録
            status = f"error: {error}"
        finally:
            transport.close()
        total_s = time.perf_counter() - started
        record = {
            "id": prompt_id,
            "category": category,
            "prompt": text,
            "response": "".join(response_parts),
            "status": status,
            "ttft_s": round(first_delta_s, 3) if first_delta_s is not None else None,
            "total_s": round(total_s, 3),
            "tool_events": tool_events,
            "text_chars_before_first_tool": text_chars_before_first_tool,
            "mode": "codex",
        }
        results.append(record)
        print(
            f"[{index + 1}/{len(prompts)}] {prompt_id} status={status[:60]} "
            f"ttft={record['ttft_s']} total={record['total_s']}s\n"
            f"  Q: {text}\n  A: {record['response']!r}",
            flush=True,
        )
    return results


def run_vllm_mode(prompts, args) -> list[dict]:
    results = []
    for index, (prompt_id, category, text) in enumerate(prompts):
        payload = {
            "model": args.model,
            "messages": [
                {"role": "system", "content": args.developer_instructions},
                {"role": "user", "content": text},
            ],
            "max_tokens": 512,
            "temperature": 0.7,
        }
        request = urllib.request.Request(
            f"{args.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.environ.get('VLLM_API_KEY', 'dummy')}",
            },
        )
        started = time.perf_counter()
        status = "completed"
        response_text = ""
        try:
            with urllib.request.urlopen(request, timeout=args.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
            response_text = body["choices"][0]["message"]["content"] or ""
        except Exception as error:
            status = f"error: {error}"
        total_s = time.perf_counter() - started
        record = {
            "id": prompt_id,
            "category": category,
            "prompt": text,
            "response": response_text,
            "status": status,
            "ttft_s": None,
            "total_s": round(total_s, 3),
            "mode": "vllm",
        }
        results.append(record)
        print(
            f"[{index + 1}/{len(prompts)}] {prompt_id} total={record['total_s']}s\n"
            f"  Q: {text}\n  A: {response_text!r}",
            flush=True,
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("codex", "vllm"), required=True)
    parser.add_argument(
        "--prompts", type=Path, default=Path(__file__).resolve().parent / "prompts_ja.tsv"
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--provider", default=DEFAULT_PROVIDER)
    parser.add_argument("--developer-instructions", default=DEFAULT_DEVELOPER_INSTRUCTIONS)
    parser.add_argument(
        "--instructions-suffix",
        default=None,
        help="developer instructions の末尾に追記するテキスト(A/B実験用)",
    )
    parser.add_argument("--timeout-seconds", type=float, default=120.0)
    parser.add_argument(
        "--sandbox",
        default="read-only",
        help="codex sandbox (この機体は landlock 不在のため実行検証は danger-full-access)",
    )
    parser.add_argument("--run-name", required=True)
    parser.add_argument(
        "--output-root", type=Path, default=_REPO_ROOT / "artifacts/llm_dialogue_eval/runs"
    )
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    prompts = parse_prompts(args.prompts)
    if args.limit is not None:
        prompts = prompts[: args.limit]
    if args.instructions_suffix:
        args.developer_instructions = args.developer_instructions + args.instructions_suffix

    if args.mode == "codex":
        results = run_codex_mode(prompts, args)
    else:
        results = run_vllm_mode(prompts, args)

    output_dir = args.output_root / args.run_name
    output_dir.mkdir(parents=True, exist_ok=True)
    results_path = output_dir / "responses.jsonl"
    with results_path.open("w", encoding="utf-8") as results_file:
        for record in results:
            results_file.write(json.dumps(record, ensure_ascii=False) + "\n")

    completed = [r for r in results if r["status"] == "completed"]
    ttfts = [r["ttft_s"] for r in completed if r["ttft_s"] is not None]
    summary = {
        "run_name": args.run_name,
        "mode": args.mode,
        "model": args.model,
        "prompts": len(results),
        "completed": len(completed),
        "ttft_s_mean": round(sum(ttfts) / len(ttfts), 3) if ttfts else None,
        "total_s_mean": (
            round(sum(r["total_s"] for r in completed) / len(completed), 3) if completed else None
        ),
        "response_chars_mean": (
            round(sum(len(r["response"]) for r in completed) / len(completed), 1)
            if completed
            else None
        ),
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\n=== summary ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"wrote {results_path}")


if __name__ == "__main__":
    main()
