import argparse

from fluent_audio.contracts import TranscriptFinal
from fluent_audio.dora import (
    decode_transcript_final_from_dora,
    validate_dora_transcript_metadata,
    validate_dora_transcript_stream_final_marker,
)
from nodes.asr.transcript_replay.main import (
    resolve_transcript_text,
    send_transcript_replay_dora,
)


class FakeDoraNode:
    def __init__(self) -> None:
        self.sent = []

    def send_output(self, output_id, data, metadata=None) -> None:
        self.sent.append((output_id, data, metadata))


def _transcript() -> TranscriptFinal:
    return TranscriptFinal(
        session_id="session-1",
        user_turn_id="user-turn-1",
        stream_id="asr/main",
        seq=0,
        text="hello",
        start_sample_index=0,
        end_sample_index=16_000,
    )


def test_transcript_replay_emits_final_and_stream_final_marker() -> None:
    fake_node = FakeDoraNode()

    count = send_transcript_replay_dora(fake_node, _transcript())

    assert count == 1
    assert [output_id for output_id, _payload, _metadata in fake_node.sent] == [
        "transcript",
        "transcript",
    ]
    final_payload, final_metadata = fake_node.sent[0][1], fake_node.sent[0][2]
    marker_payload, marker_metadata = fake_node.sent[1][1], fake_node.sent[1][2]
    assert final_metadata is not None
    assert marker_metadata is not None

    decoded_final = decode_transcript_final_from_dora(
        final_payload,
        validate_dora_transcript_metadata(final_metadata),
    )
    decoded_marker = validate_dora_transcript_stream_final_marker(
        marker_payload,
        validate_dora_transcript_metadata(marker_metadata),
    )

    assert decoded_final == _transcript()
    assert decoded_marker.seq == 1
    assert decoded_marker.start_sample_index == 16_000


def test_resolve_transcript_text_from_file(tmp_path) -> None:
    text_file = tmp_path / "transcript.txt"
    text_file.write_text("/no_think Respond exactly.\n", encoding="utf-8")

    resolved = resolve_transcript_text(
        argparse.ArgumentParser(),
        text=None,
        text_file=text_file,
    )

    assert resolved == "/no_think Respond exactly."
