"""Replay headerless PCM as typed synthesized-audio DORA events."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fluent_dialogue_dora.contracts import AudioFormat, SynthesizedAudioChunk
from fluent_dialogue_dora.dora import (
    encode_synthesized_audio_chunk_for_dora,
    encode_synthesized_audio_final_marker_for_dora,
)
from fluent_dialogue_dora.offline import (
    RawPcmReadConfig,
    capture_time_ns_for_frame_offset,
    iter_raw_pcm_chunks,
)

DORA_FINAL_MARKER_DRAIN_SECONDS = 0.1


class SynthAudioReplayPacingConfig(BaseModel):
    """Explicit DORA replay pacing for treating synthesized fixtures as a stream."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    replay_speed: float = Field(gt=0.0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read headerless PCM and emit SynthesizedAudioChunk DORA events."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--sample-rate-hz", required=True, type=int)
    parser.add_argument("--channels", required=True, type=int)
    parser.add_argument("--sample-format", required=True, choices=("s16le", "f32le"))
    parser.add_argument("--channel-layout", required=True, choices=("interleaved",))
    parser.add_argument("--chunk-frames", required=True, type=int)
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--user-turn-id", required=True)
    parser.add_argument("--assistant-turn-id", required=True)
    parser.add_argument("--audio-source-id", required=True)
    parser.add_argument("--audio-stream-id", required=True)
    parser.add_argument("--start-capture-time-ns", required=True, type=int)
    parser.add_argument("--dora", action="store_true")
    parser.add_argument(
        "--replay-speed",
        type=float,
        help="When set with --dora, sleep after each chunk at real-time / replay_speed.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = SynthAudioReplayConfig(
        read=RawPcmReadConfig(
            path=args.input,
            audio_format=AudioFormat(
                sample_rate_hz=args.sample_rate_hz,
                channels=args.channels,
                sample_format=args.sample_format,
                channel_layout=args.channel_layout,
            ),
            chunk_frames=args.chunk_frames,
            source_id=args.audio_source_id,
            stream_id=args.audio_stream_id,
            start_seq=0,
            start_sample_index=0,
            start_capture_time_ns=args.start_capture_time_ns,
        ),
        request_id=args.request_id,
        session_id=args.session_id,
        user_turn_id=args.user_turn_id,
        assistant_turn_id=args.assistant_turn_id,
    )
    if args.dora:
        from dora import Node

        send_synth_audio_replay_dora(
            Node(),
            config,
            pacing_config=_pacing_config_from_args(args),
        )
        return 0

    for chunk in iter_synth_audio_chunks(config):
        sys.stdout.write(chunk.model_dump_json())
        sys.stdout.write("\n")
    return 0


class SynthAudioReplayConfig(BaseModel):
    """Explicit config for replaying a raw PCM file as one synthesized request."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    read: RawPcmReadConfig
    request_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    user_turn_id: str = Field(min_length=1)
    assistant_turn_id: str = Field(min_length=1)


def iter_synth_audio_chunks(config: SynthAudioReplayConfig):
    for audio in iter_raw_pcm_chunks(config.read):
        yield SynthesizedAudioChunk(
            request_id=config.request_id,
            session_id=config.session_id,
            user_turn_id=config.user_turn_id,
            assistant_turn_id=config.assistant_turn_id,
            seq=audio.seq,
            audio=audio,
        )


def send_synth_audio_replay_dora(
    node,
    config: SynthAudioReplayConfig,
    *,
    pacing_config: SynthAudioReplayPacingConfig | None = None,
) -> int:
    chunks_sent = 0
    next_seq = config.read.start_seq
    next_sample_index = config.read.start_sample_index
    final_capture_time_ns = config.read.start_capture_time_ns

    for chunk in iter_synth_audio_chunks(config):
        payload, metadata = encode_synthesized_audio_chunk_for_dora(chunk)
        node.send_output("synth_audio", payload, metadata=metadata.to_dora_metadata())
        chunks_sent += 1
        next_seq = chunk.seq + 1
        next_sample_index = chunk.audio.next_sample_index
        final_capture_time_ns = capture_time_ns_for_frame_offset(
            config.read.start_capture_time_ns,
            next_sample_index - config.read.start_sample_index,
            config.read.audio_format.sample_rate_hz,
        )
        if pacing_config is not None:
            time.sleep(_chunk_replay_sleep_seconds(chunk, pacing_config))

    final_payload, final_metadata = encode_synthesized_audio_final_marker_for_dora(
        request_id=config.request_id,
        session_id=config.session_id,
        user_turn_id=config.user_turn_id,
        assistant_turn_id=config.assistant_turn_id,
        seq=next_seq,
        audio_source_id=config.read.source_id,
        audio_stream_id=config.read.stream_id,
        audio_seq=next_seq,
        audio_sample_index=next_sample_index,
        audio_capture_time_ns=final_capture_time_ns,
        audio_format=config.read.audio_format,
    )
    node.send_output("synth_audio", final_payload, metadata=final_metadata.to_dora_metadata())
    time.sleep(DORA_FINAL_MARKER_DRAIN_SECONDS)
    return chunks_sent


def _pacing_config_from_args(args: argparse.Namespace) -> SynthAudioReplayPacingConfig | None:
    if args.replay_speed is None:
        return None
    return SynthAudioReplayPacingConfig(replay_speed=args.replay_speed)


def _chunk_replay_sleep_seconds(
    chunk: SynthesizedAudioChunk,
    pacing_config: SynthAudioReplayPacingConfig,
) -> float:
    return chunk.audio.frame_count / (
        chunk.audio.format.sample_rate_hz * pacing_config.replay_speed
    )


if __name__ == "__main__":
    raise SystemExit(main())
