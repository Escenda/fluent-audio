from pathlib import Path

from fluent_audio.contracts import AudioFormat, SynthesizedAudioChunk
from fluent_audio.dora import (
    decode_synthesized_audio_chunk_from_dora,
    validate_dora_synthesized_audio_final_marker,
    validate_dora_synthesized_audio_metadata,
)
from nodes.tts.synth_audio_replay.main import (
    SynthAudioReplayConfig,
    iter_synth_audio_chunks,
    send_synth_audio_replay_dora,
)
from fluent_audio.offline import RawPcmReadConfig


class FakeDoraNode:
    def __init__(self) -> None:
        self.sent = []

    def send_output(self, output_id, data, metadata=None) -> None:
        self.sent.append((output_id, data, metadata))


def _audio_format() -> AudioFormat:
    return AudioFormat(sample_rate_hz=16_000, channels=1, sample_format="s16le")


def _config(path: Path) -> SynthAudioReplayConfig:
    return SynthAudioReplayConfig(
        read=RawPcmReadConfig(
            path=path,
            audio_format=_audio_format(),
            chunk_frames=2,
            source_id="tts_replay",
            stream_id="tts/replay/audio",
            start_seq=0,
            start_sample_index=0,
            start_capture_time_ns=0,
        ),
        request_id="tts-1",
        session_id="session-1",
        user_turn_id="user-turn-1",
        assistant_turn_id="assistant-turn-1",
    )


def test_synth_audio_replay_wraps_raw_pcm_chunks_as_synthesized_audio(tmp_path: Path) -> None:
    source = tmp_path / "speech.s16le"
    source.write_bytes(b"\x01\x00\x02\x00\x03\x00\x04\x00")

    chunks = list(iter_synth_audio_chunks(_config(source)))

    assert chunks == [
        SynthesizedAudioChunk(
            request_id="tts-1",
            session_id="session-1",
            user_turn_id="user-turn-1",
            assistant_turn_id="assistant-turn-1",
            seq=0,
            audio=chunks[0].audio,
        ),
        SynthesizedAudioChunk(
            request_id="tts-1",
            session_id="session-1",
            user_turn_id="user-turn-1",
            assistant_turn_id="assistant-turn-1",
            seq=1,
            audio=chunks[1].audio,
        ),
    ]
    assert chunks[0].audio.source_id == "tts_replay"
    assert chunks[0].audio.stream_id == "tts/replay/audio"
    assert chunks[0].audio.frame_count == 2
    assert chunks[0].audio.payload == b"\x01\x00\x02\x00"
    assert chunks[1].audio.sample_index == 2
    assert chunks[1].audio.payload == b"\x03\x00\x04\x00"


def test_synth_audio_replay_dora_emits_chunk_and_final_marker(tmp_path: Path) -> None:
    source = tmp_path / "speech.s16le"
    source.write_bytes(b"\x01\x00\x02\x00\x03\x00\x04\x00")
    fake_node = FakeDoraNode()

    chunks_sent = send_synth_audio_replay_dora(fake_node, _config(source))

    assert chunks_sent == 2
    assert [output_id for output_id, _payload, _metadata in fake_node.sent] == [
        "synth_audio",
        "synth_audio",
        "synth_audio",
    ]
    chunk_payload, chunk_metadata = fake_node.sent[0][1], fake_node.sent[0][2]
    final_payload, final_metadata = fake_node.sent[2][1], fake_node.sent[2][2]
    assert chunk_metadata is not None
    assert final_metadata is not None
    decoded_chunk = decode_synthesized_audio_chunk_from_dora(
        chunk_payload,
        validate_dora_synthesized_audio_metadata(chunk_metadata),
    )
    decoded_final = validate_dora_synthesized_audio_final_marker(
        final_payload,
        final_metadata,
    )

    assert decoded_chunk.request_id == "tts-1"
    assert decoded_chunk.audio.payload == b"\x01\x00\x02\x00"
    assert decoded_final.request_id == "tts-1"
    assert decoded_final.seq == 2
    assert decoded_final.audio_sample_index == 4
