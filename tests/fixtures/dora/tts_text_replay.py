"""Replay one TTS text chunk and stream final marker as DORA events."""
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

from fluent_dialogue_dora.contracts import TtsTextChunk, TtsTextStreamFinal
from fluent_dialogue_dora.dora import (
    encode_tts_text_chunk_for_dora,
    encode_tts_text_stream_final_marker_for_dora,
)

DORA_OUTPUT_DRAIN_SECONDS = 0.5
DORA_BETWEEN_OUTPUT_SECONDS = 0.05


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Emit one TTS text chunk and final marker.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--user-turn-id", required=True)
    parser.add_argument("--assistant-turn-id", required=True)
    parser.add_argument("--seq", type=int, default=0)
    parser.add_argument("--text", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    chunk = TtsTextChunk(
        request_id=args.request_id,
        session_id=args.session_id,
        user_turn_id=args.user_turn_id,
        assistant_turn_id=args.assistant_turn_id,
        seq=args.seq,
        text=args.text,
        is_final=True,
    )
    marker = TtsTextStreamFinal(
        session_id=args.session_id,
        user_turn_id=args.user_turn_id,
        assistant_turn_id=args.assistant_turn_id,
        seq=args.seq + 1,
    )

    if args.dora:
        from dora import Node

        send_tts_text_replay_dora(Node(), chunk, marker)
        return 0

    sys.stdout.write(chunk.model_dump_json())
    sys.stdout.write("\n")
    sys.stdout.write(marker.model_dump_json())
    sys.stdout.write("\n")
    return 0


def send_tts_text_replay_dora(node, chunk: TtsTextChunk, marker: TtsTextStreamFinal) -> None:
    payload, metadata = encode_tts_text_chunk_for_dora(chunk)
    node.send_output("tts_text", payload, metadata=metadata.to_dora_metadata())
    time.sleep(DORA_BETWEEN_OUTPUT_SECONDS)
    final_payload, final_metadata = encode_tts_text_stream_final_marker_for_dora(marker)
    node.send_output("tts_text", final_payload, metadata=final_metadata.to_dora_metadata())
    time.sleep(DORA_OUTPUT_DRAIN_SECONDS)


if __name__ == "__main__":
    raise SystemExit(main())
