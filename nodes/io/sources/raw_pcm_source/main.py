"""CLI wrapper for the raw PCM offline source node logic."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from fluent_audio.contracts import AudioChunk, AudioFormat
from fluent_audio.offline import (
    RawPcmReadConfig,
    iter_raw_pcm_chunks,
    write_raw_pcm_chunk_jsonl,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read headerless PCM and emit AudioChunk JSONL.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--sample-rate-hz", required=True, type=int)
    parser.add_argument("--channels", required=True, type=int)
    parser.add_argument("--sample-format", required=True, choices=("s16le", "f32le"))
    parser.add_argument("--chunk-frames", required=True, type=int)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--stream-id", required=True)
    parser.add_argument("--start-seq", type=int, default=0)
    parser.add_argument("--start-sample-index", type=int, default=0)
    parser.add_argument("--chunks-jsonl", type=Path)
    parser.add_argument("--overwrite-jsonl", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = RawPcmReadConfig(
        path=args.input,
        audio_format=AudioFormat(
            sample_rate_hz=args.sample_rate_hz,
            channels=args.channels,
            sample_format=args.sample_format,
        ),
        chunk_frames=args.chunk_frames,
        source_id=args.source_id,
        stream_id=args.stream_id,
        start_seq=args.start_seq,
        start_sample_index=args.start_sample_index,
    )
    chunks = iter_raw_pcm_chunks(config)

    if args.chunks_jsonl is not None:
        write_raw_pcm_chunk_jsonl(
            args.chunks_jsonl,
            chunks,
            overwrite=args.overwrite_jsonl,
        )
        return 0

    for chunk in chunks:
        sys.stdout.write(_metadata_json_line(chunk))
        sys.stdout.write("\n")
    return 0


def _metadata_json_line(chunk: AudioChunk) -> str:
    return json.dumps(
        {
            "source_id": chunk.source_id,
            "stream_id": chunk.stream_id,
            "seq": chunk.seq,
            "sample_index": chunk.sample_index,
            "capture_time_ns": chunk.capture_time_ns,
            "frame_count": chunk.frame_count,
            "format": chunk.format.model_dump(mode="json"),
            "payload_size_bytes": chunk.payload_size_bytes,
        },
        sort_keys=True,
    )


if __name__ == "__main__":
    raise SystemExit(main())
