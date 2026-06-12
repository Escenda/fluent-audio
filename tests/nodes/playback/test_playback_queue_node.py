import pytest

from fluent_audio.contracts import (
    AudioChunk,
    AudioFormat,
    PlaybackClear,
    PlaybackDone,
    PlaybackPause,
    PlaybackResume,
    PlaybackState,
    PlaybackStop,
    SynthesizedAudioChunk,
)
from fluent_audio.dora import (
    DoraAudioFinalMarker,
    decode_audio_chunk_from_dora,
    decode_playback_done_from_dora,
    decode_playback_state_from_dora,
    encode_playback_command_for_dora,
    encode_synthesized_audio_chunk_for_dora,
    encode_synthesized_audio_final_marker_for_dora,
    validate_dora_audio_final_marker,
    validate_dora_audio_metadata,
)
from nodes.playback.playback_queue.main import (
    PlaybackQueueConfig,
    PlaybackQueueError,
    run_playback_queue_events,
)


class FakeDoraNode:
    def __init__(self, events) -> None:
        self._events = events
        self.sent = []

    def __iter__(self):
        return iter(self._events)

    def send_output(self, output_id, data, metadata=None) -> None:
        self.sent.append((output_id, data, metadata))


def _config(max_queued_audio_chunks: int = 8) -> PlaybackQueueConfig:
    return PlaybackQueueConfig(
        max_queued_audio_chunks=max_queued_audio_chunks,
        output_drain_seconds=0.0,
    )


def _input(input_id: str, encoded):
    payload, metadata = encoded
    return {
        "type": "INPUT",
        "id": input_id,
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _audio_format() -> AudioFormat:
    return AudioFormat(sample_rate_hz=16_000, channels=1, sample_format="s16le")


def _audio_chunk(
    seq: int,
    *,
    frame_count: int = 2,
    stream_id: str = "tts/audio",
) -> AudioChunk:
    sample_index = seq * frame_count
    first_sample = seq + 1
    second_sample = seq + 2
    return AudioChunk(
        source_id="tts",
        stream_id=stream_id,
        seq=seq,
        sample_index=sample_index,
        capture_time_ns=sample_index * 1_000,
        frame_count=frame_count,
        format=_audio_format(),
        payload=bytes((first_sample, 0, second_sample, 0)),
    )


def _synth_chunk(
    seq: int,
    *,
    request_id: str = "tts-1",
    assistant_turn_id: str = "assistant-turn-1",
) -> SynthesizedAudioChunk:
    return SynthesizedAudioChunk(
        request_id=request_id,
        session_id="session-1",
        user_turn_id="user-turn-1",
        assistant_turn_id=assistant_turn_id,
        seq=seq,
        audio=_audio_chunk(seq),
    )


def _synth_event(
    seq: int,
    *,
    request_id: str = "tts-1",
    assistant_turn_id: str = "assistant-turn-1",
):
    return _input(
        "synth_audio",
        encode_synthesized_audio_chunk_for_dora(
            _synth_chunk(
                seq,
                request_id=request_id,
                assistant_turn_id=assistant_turn_id,
            )
        ),
    )


def _synth_final_event(
    seq: int,
    *,
    request_id: str = "tts-1",
    assistant_turn_id: str = "assistant-turn-1",
):
    frame_count = 2
    return _input(
        "synth_audio",
        encode_synthesized_audio_final_marker_for_dora(
            request_id=request_id,
            session_id="session-1",
            user_turn_id="user-turn-1",
            assistant_turn_id=assistant_turn_id,
            seq=seq,
            audio_source_id="tts",
            audio_stream_id="tts/audio",
            audio_seq=seq,
            audio_sample_index=seq * frame_count,
            audio_capture_time_ns=seq * frame_count * 1_000,
            audio_format=_audio_format(),
        ),
    )


def _pause_event(seq: int = 0):
    return _input(
        "playback_command",
        encode_playback_command_for_dora(
            PlaybackPause(command="pause", request_id="tts-1", stream_id="speaker/main", seq=seq)
        ),
    )


def _resume_event(seq: int = 1):
    return _input(
        "playback_command",
        encode_playback_command_for_dora(
            PlaybackResume(command="resume", request_id="tts-1", stream_id="speaker/main", seq=seq)
        ),
    )


def _stop_event(seq: int = 0):
    return _input(
        "playback_command",
        encode_playback_command_for_dora(
            PlaybackStop(command="stop", request_id="tts-1", stream_id="speaker/main", seq=seq)
        ),
    )


def _clear_event(seq: int = 0):
    return _input(
        "playback_command",
        encode_playback_command_for_dora(
            PlaybackClear(command="clear", request_id="tts-1", stream_id="speaker/main", seq=seq)
        ),
    )


def _decode_outputs(
    fake_node: FakeDoraNode,
) -> tuple[
    list[AudioChunk],
    list[DoraAudioFinalMarker],
    list[PlaybackState],
    list[PlaybackDone],
    list[str],
]:
    audio_chunks: list[AudioChunk] = []
    audio_finals: list[DoraAudioFinalMarker] = []
    playback_states: list[PlaybackState] = []
    playback_done: list[PlaybackDone] = []
    output_ids: list[str] = []
    for output_id, payload, metadata in fake_node.sent:
        assert metadata is not None
        output_ids.append(output_id)
        if output_id == "audio":
            audio_metadata = validate_dora_audio_metadata(metadata)
            if audio_metadata.final:
                audio_finals.append(validate_dora_audio_final_marker(payload, audio_metadata))
            else:
                audio_chunks.append(decode_audio_chunk_from_dora(payload, audio_metadata))
        elif output_id == "playback_state":
            playback_states.append(decode_playback_state_from_dora(payload, metadata))
        elif output_id == "playback_done":
            playback_done.append(decode_playback_done_from_dora(payload, metadata))
        else:
            raise AssertionError(f"unexpected output id: {output_id}")
    return audio_chunks, audio_finals, playback_states, playback_done, output_ids


def test_playback_queue_emits_audio_state_and_done_for_completed_request() -> None:
    fake_node = FakeDoraNode(
        [
            _synth_event(0),
            _synth_event(1),
            _synth_final_event(2),
            {"type": "STOP"},
        ]
    )

    summary = run_playback_queue_events(fake_node, _config())
    audio_chunks, audio_finals, playback_states, playback_done, output_ids = _decode_outputs(
        fake_node
    )

    assert summary.synthesized_audio_chunks == 2
    assert summary.synthesized_audio_finals == 1
    assert summary.audio_chunks_sent == 2
    assert summary.audio_finals_sent == 1
    assert summary.playback_states == 4
    assert summary.playback_done == 1
    assert [chunk.seq for chunk in audio_chunks] == [0, 1]
    assert [chunk.source_id for chunk in audio_chunks] == ["playback_queue", "playback_queue"]
    assert [chunk.stream_id for chunk in audio_chunks] == ["speaker/main", "speaker/main"]
    assert [chunk.sample_index for chunk in audio_chunks] == [0, 2]
    assert [final.seq for final in audio_finals] == [2]
    assert [final.source_id for final in audio_finals] == ["playback_queue"]
    assert [final.stream_id for final in audio_finals] == ["speaker/main"]
    assert [final.sample_index for final in audio_finals] == [4]
    assert [state.state for state in playback_states] == [
        "queued",
        "playing",
        "playing",
        "completed",
    ]
    assert [state.seq for state in playback_states] == [0, 1, 2, 3]
    assert [state.played_frames for state in playback_states] == [0, 2, 4, 4]
    assert playback_done == [
        PlaybackDone(
            request_id="tts-1",
            session_id="session-1",
            user_turn_id="user-turn-1",
            stream_id="speaker/main",
            status="completed",
            final_sequence=2,
            total_frames=4,
        )
    ]
    assert output_ids == [
        "playback_state",
        "audio",
        "playback_state",
        "audio",
        "playback_state",
        "audio",
        "playback_state",
        "playback_done",
    ]


@pytest.mark.parametrize(
    ("command_event", "expected_state", "expected_status"),
    [
        (_stop_event(), "stopped", "stopped"),
        (_clear_event(), "cancelled", "cancelled"),
    ],
)
def test_playback_queue_stop_and_clear_terminate_active_request(
    command_event,
    expected_state: str,
    expected_status: str,
) -> None:
    fake_node = FakeDoraNode([_synth_event(0), command_event, {"type": "STOP"}])

    summary = run_playback_queue_events(fake_node, _config())
    audio_chunks, audio_finals, playback_states, playback_done, _output_ids = _decode_outputs(
        fake_node
    )

    assert summary.playback_commands == 1
    assert [chunk.seq for chunk in audio_chunks] == [0]
    assert audio_chunks[0].stream_id == "speaker/main"
    assert [final.seq for final in audio_finals] == [1]
    assert [final.sample_index for final in audio_finals] == [2]
    assert playback_states[-1].state == expected_state
    assert playback_states[-1].played_frames == 2
    assert playback_done[0].status == expected_status
    assert playback_done[0].final_sequence == 1
    assert playback_done[0].total_frames == 2


def test_playback_queue_pause_holds_audio_until_resume_without_drop() -> None:
    fake_node = FakeDoraNode(
        [
            _synth_event(0),
            _pause_event(seq=0),
            _synth_event(1),
            _synth_final_event(2),
            _resume_event(seq=1),
            {"type": "STOP"},
        ]
    )

    summary = run_playback_queue_events(fake_node, _config())
    audio_chunks, audio_finals, playback_states, playback_done, output_ids = _decode_outputs(
        fake_node
    )

    assert summary.paused_requests == 1
    assert summary.resumed_requests == 1
    assert [chunk.seq for chunk in audio_chunks] == [0, 1]
    assert [chunk.sample_index for chunk in audio_chunks] == [0, 2]
    assert [final.seq for final in audio_finals] == [2]
    assert [final.sample_index for final in audio_finals] == [4]
    assert [state.state for state in playback_states] == [
        "queued",
        "playing",
        "paused",
        "queued",
        "queued",
        "playing",
        "playing",
        "completed",
    ]
    assert [state.played_frames for state in playback_states] == [0, 2, 2, 2, 2, 2, 4, 4]
    assert playback_done[0].status == "completed"
    assert playback_done[0].total_frames == 4
    assert output_ids.index("audio") < output_ids.index("playback_done")
    assert output_ids.count("audio") == 3


def test_playback_queue_rejects_stop_without_synthesized_audio_final_marker() -> None:
    fake_node = FakeDoraNode([_synth_event(0), {"type": "STOP"}])

    with pytest.raises(PlaybackQueueError, match="active"):
        run_playback_queue_events(fake_node, _config())

    _audio_chunks, _audio_finals, _playback_states, playback_done, _output_ids = _decode_outputs(
        fake_node
    )
    assert playback_done == []


def test_playback_queue_reports_paused_queue_overflow_as_failed_request() -> None:
    fake_node = FakeDoraNode(
        [
            _synth_event(0),
            _pause_event(seq=0),
            _synth_event(1),
            _synth_event(2),
            {"type": "STOP"},
        ]
    )

    summary = run_playback_queue_events(fake_node, _config(max_queued_audio_chunks=1))
    _audio_chunks, _audio_finals, playback_states, playback_done, _output_ids = _decode_outputs(
        fake_node
    )

    assert summary.playback_done == 1
    assert playback_states[-1].state == "failed"
    assert playback_done[0].status == "failed"
    assert playback_done[0].reason == "paused playback queue is full"


def test_playback_queue_keeps_speaker_audio_sequence_contiguous_across_requests() -> None:
    fake_node = FakeDoraNode(
        [
            _synth_event(0, request_id="tts-1", assistant_turn_id="assistant-turn-1"),
            _synth_final_event(1, request_id="tts-1", assistant_turn_id="assistant-turn-1"),
            _synth_event(0, request_id="tts-2", assistant_turn_id="assistant-turn-1"),
            _synth_final_event(1, request_id="tts-2", assistant_turn_id="assistant-turn-1"),
            {"type": "STOP"},
        ]
    )

    summary = run_playback_queue_events(fake_node, _config())
    audio_chunks, audio_finals, _playback_states, playback_done, _output_ids = _decode_outputs(
        fake_node
    )

    assert summary.synthesized_audio_chunks == 2
    assert summary.synthesized_audio_finals == 2
    assert summary.audio_finals_sent == 2
    assert [chunk.seq for chunk in audio_chunks] == [0, 1]
    assert [chunk.sample_index for chunk in audio_chunks] == [0, 2]
    assert [final.seq for final in audio_finals] == [1, 2]
    assert [final.sample_index for final in audio_finals] == [2, 4]
    assert [done.request_id for done in playback_done] == ["tts-1", "tts-2"]


def test_playback_queue_fails_corrupt_request_without_killing_next_request() -> None:
    fake_node = FakeDoraNode(
        [
            _synth_event(0, request_id="tts-1", assistant_turn_id="assistant-turn-1"),
            _synth_event(9, request_id="tts-1", assistant_turn_id="assistant-turn-1"),
            _synth_final_event(10, request_id="tts-1", assistant_turn_id="assistant-turn-1"),
            _synth_event(0, request_id="tts-2", assistant_turn_id="assistant-turn-1"),
            _synth_final_event(1, request_id="tts-2", assistant_turn_id="assistant-turn-1"),
            {"type": "STOP"},
        ]
    )

    summary = run_playback_queue_events(fake_node, _config())
    audio_chunks, audio_finals, playback_states, playback_done, _output_ids = _decode_outputs(
        fake_node
    )

    assert summary.synthesized_audio_chunks == 3
    assert summary.synthesized_audio_finals == 2
    assert [chunk.seq for chunk in audio_chunks] == [0, 1]
    assert [final.seq for final in audio_finals] == [1, 2]
    assert [state.state for state in playback_states].count("failed") == 1
    assert playback_done[0].request_id == "tts-1"
    assert playback_done[0].status == "failed"
    assert playback_done[0].reason is not None
    assert "seq discontinuity" in playback_done[0].reason
    assert playback_done[1].request_id == "tts-2"
    assert playback_done[1].status == "completed"
