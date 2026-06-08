"""CLI wrapper for the raw PCM offline sink node logic."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from fluent_audio.contracts import AudioFormat
from fluent_audio.offline import (
    RawPcmWriteConfig,
    iter_raw_pcm_chunk_jsonl,
    write_raw_pcm_chunks,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate AudioChunk JSONL and write raw PCM.")
    parser.add_argument("--chunks-jsonl", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--sample-rate-hz", required=True, type=int)
    parser.add_argument("--channels", required=True, type=int)
    parser.add_argument("--sample-format", required=True, choices=("s16le", "f32le"))
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--stream-id", required=True)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = RawPcmWriteConfig(
        path=args.output,
        expected_format=AudioFormat(
            sample_rate_hz=args.sample_rate_hz,
            channels=args.channels,
            sample_format=args.sample_format,
        ),
        source_id=args.source_id,
        stream_id=args.stream_id,
        overwrite=args.overwrite,
    )
    summary = write_raw_pcm_chunks(config, iter_raw_pcm_chunk_jsonl(args.chunks_jsonl))
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
