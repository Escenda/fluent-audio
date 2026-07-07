"""Replay a fixed final transcript as typed DORA transcript events."""
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

from fluent_dialogue_dora.contracts import TranscriptFinal
from fluent_dialogue_dora.dora import (
    encode_transcript_final_for_dora,
    encode_transcript_stream_final_marker_for_dora,
)

DORA_FINAL_MARKER_DRAIN_SECONDS = 0.1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Emit one final transcript and stream marker.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--user-turn-id", required=True)
    parser.add_argument("--stream-id", required=True)
    parser.add_argument("--seq", type=int, default=0)
    parser.add_argument("--text")
    parser.add_argument("--text-file", type=Path)
    parser.add_argument("--start-sample-index", type=int, required=True)
    parser.add_argument("--end-sample-index", type=int, required=True)
    return parser


def resolve_transcript_text(
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
    transcript_text = resolve_transcript_text(
        parser,
        text=args.text,
        text_file=args.text_file,
    )
    transcript = TranscriptFinal(
        session_id=args.session_id,
        user_turn_id=args.user_turn_id,
        stream_id=args.stream_id,
        seq=args.seq,
        text=transcript_text,
        start_sample_index=args.start_sample_index,
        end_sample_index=args.end_sample_index,
    )

    if args.dora:
        from dora import Node

        send_transcript_replay_dora(Node(), transcript)
        return 0

    sys.stdout.write(transcript.model_dump_json())
    sys.stdout.write("\n")
    return 0


def send_transcript_replay_dora(node, transcript: TranscriptFinal) -> int:
    payload, metadata = encode_transcript_final_for_dora(transcript)
    node.send_output("transcript", payload, metadata=metadata.to_dora_metadata())
    final_payload, final_metadata = encode_transcript_stream_final_marker_for_dora(
        session_id=transcript.session_id,
        stream_id=transcript.stream_id,
        seq=transcript.seq + 1,
        sample_index=transcript.end_sample_index,
    )
    node.send_output("transcript", final_payload, metadata=final_metadata.to_dora_metadata())
    time.sleep(DORA_FINAL_MARKER_DRAIN_SECONDS)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
