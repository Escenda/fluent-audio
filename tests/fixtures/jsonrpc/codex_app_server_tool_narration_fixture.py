"""JSON-RPC fixture emitting a pre-tool narration scenario for timing checks.

Scenario per turn (docs/課題/voice-dialogue-quality.md 課題2):

1. agent message delta: preamble sentence(s) closed with punctuation
2. item/started for a tool call
3. sleep ``--tool-delay-seconds`` (simulated long-running tool)
4. item/completed for the tool call
5. agent message delta: closing sentence
6. turn/completed

If the voice pipeline is non-blocking, preamble audio must reach the
playback queue while the fixture is still sleeping in step 3.
"""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated, TypeAlias

from pydantic import BaseModel, Field, TypeAdapter

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from nodes.dialogue_engine.codex_app_server.main import (
    CodexAgentMessageDeltaEnvelope,
    CodexAgentMessageDeltaParams,
    CodexInitializeJsonRpcRequest,
    CodexInitializeJsonRpcResponse,
    CodexInitializeResult,
    CodexInitializedNotification,
    CodexItemCompletedEnvelope,
    CodexItemLifecycleParams,
    CodexItemStartedEnvelope,
    CodexMcpToolCallItem,
    CodexThreadReference,
    CodexThreadStartJsonRpcRequest,
    CodexThreadStartJsonRpcResponse,
    CodexThreadStartResult,
    CodexTurnCompletedEnvelope,
    CodexTurnCompletedParams,
    CodexTurnInterruptJsonRpcRequest,
    CodexTurnInterruptJsonRpcResponse,
    CodexTurnReference,
    CodexTurnStartJsonRpcRequest,
    CodexTurnStartJsonRpcResponse,
    CodexTurnStartResult,
)

FixtureClientRequest: TypeAlias = (
    CodexInitializeJsonRpcRequest
    | CodexThreadStartJsonRpcRequest
    | CodexTurnStartJsonRpcRequest
    | CodexTurnInterruptJsonRpcRequest
)
FixtureClientMessage: TypeAlias = FixtureClientRequest | CodexInitializedNotification
FixtureClientMessageEnvelope: TypeAlias = Annotated[
    FixtureClientMessage,
    Field(discriminator="method"),
]
FIXTURE_CLIENT_MESSAGE_ADAPTER = TypeAdapter(FixtureClientMessageEnvelope)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the tool narration JSON-RPC fixture.")
    parser.add_argument("--preamble-text", default="これからテストツールを実行します。")
    parser.add_argument("--post-text", default="ツールの実行が完了しました。")
    parser.add_argument("--tool-delay-seconds", type=float, default=4.0)
    parser.add_argument("--thread-id", default="thread-tool-narration-1")
    parser.add_argument("--turn-id", default="turn-tool-narration-1")
    parser.add_argument("--item-id", default="agent-message-tool-narration-1")
    parser.add_argument("--tool-item-id", default="tool-call-tool-narration-1")
    parser.add_argument("--expected-turns", type=int, default=1)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    completed_turns = 0
    while completed_turns < args.expected_turns:
        line = sys.stdin.readline()
        if line == "":
            raise RuntimeError("JSON-RPC fixture stdin closed before expected turns")
        request = FIXTURE_CLIENT_MESSAGE_ADAPTER.validate_json(line)
        if isinstance(request, CodexInitializeJsonRpcRequest):
            _write_model(
                CodexInitializeJsonRpcResponse(
                    id=request.id,
                    result=CodexInitializeResult(
                        user_agent="fluent-dialogue-dora-tool-narration-fixture/0.0.0",
                        codex_home="/tmp/fluent-dialogue-dora-fixture-codex-home",
                        platform_family="unix",
                        platform_os="linux",
                    ),
                )
            )
        elif isinstance(request, CodexInitializedNotification):
            continue
        elif isinstance(request, CodexThreadStartJsonRpcRequest):
            _write_model(
                CodexThreadStartJsonRpcResponse(
                    id=request.id,
                    result=CodexThreadStartResult(
                        thread=CodexThreadReference(id=args.thread_id),
                    ),
                )
            )
        elif isinstance(request, CodexTurnStartJsonRpcRequest):
            _write_model(
                CodexTurnStartJsonRpcResponse(
                    id=request.id,
                    result=CodexTurnStartResult(
                        turn=CodexTurnReference(id=args.turn_id, status="inProgress"),
                    ),
                )
            )
            thread_id = request.params.thread_id
            _write_agent_delta(thread_id, args, args.preamble_text)
            _write_tool_lifecycle(thread_id, args, started=True)
            time.sleep(args.tool_delay_seconds)
            _write_tool_lifecycle(thread_id, args, started=False)
            _write_agent_delta(thread_id, args, args.post_text)
            _write_model(
                CodexTurnCompletedEnvelope(
                    method="turn/completed",
                    params=CodexTurnCompletedParams(
                        thread_id=thread_id,
                        turn=CodexTurnReference(id=args.turn_id, status="completed"),
                    ),
                )
            )
            completed_turns += 1
        elif isinstance(request, CodexTurnInterruptJsonRpcRequest):
            _write_model(CodexTurnInterruptJsonRpcResponse(id=request.id))
    return 0


def _write_agent_delta(thread_id: str, args: argparse.Namespace, text: str) -> None:
    _write_model(
        CodexAgentMessageDeltaEnvelope(
            method="item/agentMessage/delta",
            params=CodexAgentMessageDeltaParams(
                delta=text,
                item_id=args.item_id,
                thread_id=thread_id,
                turn_id=args.turn_id,
            ),
        )
    )


def _write_tool_lifecycle(thread_id: str, args: argparse.Namespace, *, started: bool) -> None:
    item = CodexMcpToolCallItem(
        type="mcpToolCall",
        id=args.tool_item_id,
        server="fixture",
        tool="slow_tool",
        status="inProgress" if started else "completed",
    )
    params = CodexItemLifecycleParams(
        thread_id=thread_id,
        turn_id=args.turn_id,
        item=item,
    )
    if started:
        _write_model(CodexItemStartedEnvelope(method="item/started", params=params))
    else:
        _write_model(CodexItemCompletedEnvelope(method="item/completed", params=params))


def _write_model(model: BaseModel) -> None:
    sys.stdout.write(model.model_dump_json(by_alias=True, exclude_none=True) + "\n")
    sys.stdout.flush()


if __name__ == "__main__":
    raise SystemExit(main())
