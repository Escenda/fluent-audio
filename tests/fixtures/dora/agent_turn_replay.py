"""Replay one typed AgentTurnRequest as a DORA source."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Sequence
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fluent_dialogue_dora.contracts import AgentTurnRequest
from fluent_dialogue_dora.dora import encode_agent_turn_request_for_dora

DORA_OUTPUT_DRAIN_SECONDS = 0.5


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Emit one agent turn request.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--user-turn-id", required=True)
    parser.add_argument("--assistant-turn-id", required=True)
    parser.add_argument("--seq", type=int, default=0)
    parser.add_argument("--text")
    parser.add_argument("--text-file", type=Path)
    return parser


def resolve_turn_text(
    parser: argparse.ArgumentParser,
    *,
    text: str | None,
    text_file: Path | None,
) -> str:
    if (text is None) == (text_file is None):
        parser.error("specify exactly one of --text or --text-file")
    if text_file is not None:
        try:
            resolved = text_file.read_text(encoding="utf-8")
        except OSError as exc:
            parser.error(f"failed to read --text-file: {text_file}: {exc}")
        resolved = resolved.rstrip("\n")
        if resolved == "":
            parser.error("--text-file must not be empty")
        return resolved
    if text is None:
        parser.error("--text is required when --text-file is not set")
    return text


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    turn_text = resolve_turn_text(parser, text=args.text, text_file=args.text_file)
    request = AgentTurnRequest(
        session_id=args.session_id,
        user_turn_id=args.user_turn_id,
        assistant_turn_id=args.assistant_turn_id,
        seq=args.seq,
        text=turn_text,
    )

    if args.dora:
        from dora import Node

        send_agent_turn_request_dora(Node(), request)
        return 0

    sys.stdout.write(request.model_dump_json())
    sys.stdout.write("\n")
    return 0


def send_agent_turn_request_dora(node, request: AgentTurnRequest) -> None:
    payload, metadata = encode_agent_turn_request_for_dora(request)
    node.send_output("agent_turn", payload, metadata=metadata.to_dora_metadata())
    time.sleep(DORA_OUTPUT_DRAIN_SECONDS)


if __name__ == "__main__":
    raise SystemExit(main())
