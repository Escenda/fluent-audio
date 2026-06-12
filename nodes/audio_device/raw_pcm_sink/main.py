"""CLI wrapper for the raw PCM offline sink node logic."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from fluent_audio.contracts import AudioFormat
from fluent_audio.dora import (
    decode_audio_chunk_from_dora,
    validate_dora_audio_final_marker,
    validate_dora_audio_metadata,
)
from fluent_audio.offline import (
    RawPcmWriteConfig,
    RawPcmWriteSummary,
    iter_raw_pcm_chunk_jsonl,
    write_raw_pcm_chunks,
)


class DoraAudioInputEventError(ValueError):
    """Raised when a DORA event is not valid raw PCM sink input."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate AudioChunk JSONL and write raw PCM.")
    parser.add_argument("--chunks-jsonl", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--sample-rate-hz", required=True, type=int)
    parser.add_argument("--channels", required=True, type=int)
    parser.add_argument("--sample-format", required=True, choices=("s16le", "f32le"))
    parser.add_argument("--channel-layout", required=True, choices=("interleaved",))
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--stream-id", required=True)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dora", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = RawPcmWriteConfig(
        path=args.output,
        expected_format=AudioFormat(
            sample_rate_hz=args.sample_rate_hz,
            channels=args.channels,
            sample_format=args.sample_format,
            channel_layout=args.channel_layout,
        ),
        source_id=args.source_id,
        stream_id=args.stream_id,
        overwrite=args.overwrite,
    )

    if args.dora:
        from dora import Node

        write_raw_pcm_sink_dora(Node(), config)
        return 0

    if args.chunks_jsonl is None:
        parser.error("--chunks-jsonl is required unless --dora is set")

    summary = write_raw_pcm_chunks(config, iter_raw_pcm_chunk_jsonl(args.chunks_jsonl))
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def write_raw_pcm_sink_dora(node, config: RawPcmWriteConfig) -> RawPcmWriteSummary:
    """Write DORA audio input events as headerless raw PCM."""

    return write_raw_pcm_chunks(config, iter_dora_audio_input_chunks(node))


def iter_dora_audio_input_chunks(events):
    for event in events:
        if event is None:
            break

        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            break
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id != "audio":
                raise DoraAudioInputEventError(f"Unexpected DORA input id: {input_id!r}")
            break
        if event_type != "INPUT":
            raise DoraAudioInputEventError(f"Unexpected DORA event type: {event_type!r}")

        input_id = _required_event_text(event, "id")
        if input_id != "audio":
            raise DoraAudioInputEventError(f"Unexpected DORA input id: {input_id!r}")

        payload = event.get("value")
        metadata = validate_dora_audio_metadata(event.get("metadata"))
        if metadata.final:
            validate_dora_audio_final_marker(payload, metadata)
            break

        yield decode_audio_chunk_from_dora(payload, metadata)


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise DoraAudioInputEventError(f"DORA event field {key!r} must be a string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
