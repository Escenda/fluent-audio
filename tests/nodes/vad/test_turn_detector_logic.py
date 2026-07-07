import pytest

from fluent_dialogue_dora.contracts import VoiceActivityEvent, VoiceActivityState
from nodes.vad.turn_detector.logic import (
    TurnDetectorConfig,
    TurnDetectorError,
    TurnDetectorState,
)


def _config(
    *,
    end_silence_frames: int = 3,
    user_turn_id_prefix: str = "user-turn",
) -> TurnDetectorConfig:
    return TurnDetectorConfig(
        session_id="session-1",
        output_stream_id="turns/main",
        end_silence_frames=end_silence_frames,
        user_turn_id_prefix=user_turn_id_prefix,
    )


def _activity(
    *,
    seq: int,
    sample_index: int,
    frame_count: int,
    state: VoiceActivityState,
    speech_probability: float = 1.0,
) -> VoiceActivityEvent:
    return VoiceActivityEvent(
        source_id="vad",
        stream_id="activity/main",
        seq=seq,
        sample_index=sample_index,
        frame_count=frame_count,
        state=state,
        speech_probability=speech_probability,
    )


def test_started_active_ended_sequence_uses_last_speech_end_sample_index() -> None:
    state = TurnDetectorState(_config(end_silence_frames=3))

    started = state.push(_activity(seq=0, sample_index=0, frame_count=10, state="speech"))
    active = state.push(_activity(seq=1, sample_index=10, frame_count=10, state="speech"))
    short_silence = state.push(_activity(seq=2, sample_index=20, frame_count=2, state="silence"))
    ended = state.push(_activity(seq=3, sample_index=22, frame_count=1, state="silence"))

    events = [*started, *active, *short_silence, *ended]

    assert [(event.state, event.seq, event.sample_index) for event in events] == [
        ("started", 0, 0),
        ("active", 1, 10),
        ("ended", 2, 20),
    ]
    assert {event.user_turn_id for event in events} == {"user-turn-000001"}
    assert short_silence == []


def test_silence_only_emits_no_turn_events() -> None:
    state = TurnDetectorState(_config(end_silence_frames=3))

    first = state.push(_activity(seq=0, sample_index=0, frame_count=2, state="silence"))
    second = state.push(_activity(seq=1, sample_index=2, frame_count=3, state="silence"))
    finished = state.finish(final_sample_index=5)

    assert first == []
    assert second == []
    assert finished == []


def test_final_flush_active_turn_emits_ended_at_last_speech_end() -> None:
    state = TurnDetectorState(_config(end_silence_frames=10))

    started = state.push(_activity(seq=0, sample_index=100, frame_count=10, state="speech"))
    short_silence = state.push(_activity(seq=1, sample_index=110, frame_count=5, state="silence"))
    ended = state.finish(final_sample_index=115)

    assert [(event.state, event.seq, event.sample_index) for event in [*started, *ended]] == [
        ("started", 0, 100),
        ("ended", 1, 110),
    ]
    assert short_silence == []


def test_final_flush_accepts_real_end_inside_last_padded_activity_window() -> None:
    state = TurnDetectorState(_config(end_silence_frames=10))

    started = state.push(_activity(seq=0, sample_index=100, frame_count=10, state="speech"))
    ended = state.finish(final_sample_index=106)

    assert [(event.state, event.seq, event.sample_index) for event in [*started, *ended]] == [
        ("started", 0, 100),
        ("ended", 1, 106),
    ]


def test_input_seq_discontinuity_rejects_event() -> None:
    state = TurnDetectorState(_config())

    state.push(_activity(seq=0, sample_index=0, frame_count=10, state="speech"))

    with pytest.raises(TurnDetectorError, match="seq discontinuity"):
        state.push(_activity(seq=2, sample_index=10, frame_count=10, state="speech"))


def test_input_sample_index_discontinuity_rejects_event() -> None:
    state = TurnDetectorState(_config())

    state.push(_activity(seq=0, sample_index=0, frame_count=10, state="speech"))

    with pytest.raises(TurnDetectorError, match="sample_index discontinuity"):
        state.push(_activity(seq=1, sample_index=11, frame_count=10, state="speech"))


def test_output_seq_and_user_turn_id_are_deterministic() -> None:
    state = TurnDetectorState(_config(end_silence_frames=1, user_turn_id_prefix="speaker"))

    first_started = state.push(_activity(seq=0, sample_index=0, frame_count=10, state="speech"))
    first_ended = state.push(_activity(seq=1, sample_index=10, frame_count=1, state="silence"))
    second_started = state.push(_activity(seq=2, sample_index=11, frame_count=5, state="speech"))
    second_active = state.push(_activity(seq=3, sample_index=16, frame_count=5, state="speech"))
    second_ended = state.finish(final_sample_index=21)

    events = [*first_started, *first_ended, *second_started, *second_active, *second_ended]

    assert [event.seq for event in events] == [0, 1, 2, 3, 4]
    assert [event.user_turn_id for event in events] == [
        "speaker-000001",
        "speaker-000001",
        "speaker-000002",
        "speaker-000002",
        "speaker-000002",
    ]
    assert [(event.state, event.sample_index) for event in events] == [
        ("started", 0),
        ("ended", 10),
        ("started", 11),
        ("active", 16),
        ("ended", 21),
    ]
