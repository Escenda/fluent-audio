import pytest

from fluent_audio.contracts import VoiceActivityEvent
from fluent_audio.dora import (
    decode_turn_event_from_dora,
    encode_voice_activity_event_for_dora,
    encode_voice_activity_final_marker_for_dora,
    validate_dora_turn_final_marker,
    validate_dora_turn_metadata,
)
from nodes.perception.turn_detector.main import (
    TurnDetectorNodeConfig,
    TurnDetectorNodeError,
    run_turn_detector_events,
)


class FakeDoraNode:
    def __init__(self, events) -> None:
        self._events = events
        self.sent = []

    def __iter__(self):
        return iter(self._events)

    def send_output(self, output_id, data, metadata=None) -> None:
        self.sent.append((output_id, data, metadata))


def _config(*, end_silence_frames: int = 1024) -> TurnDetectorNodeConfig:
    return TurnDetectorNodeConfig(
        input_source_id="silero_vad",
        input_stream_id="activity/main",
        session_id="session-1",
        output_stream_id="turn/main",
        end_silence_frames=end_silence_frames,
    )


def _activity(
    *,
    seq: int,
    sample_index: int,
    frame_count: int = 512,
    state: str,
    probability: float,
    source_id: str = "silero_vad",
    stream_id: str = "activity/main",
) -> VoiceActivityEvent:
    return VoiceActivityEvent(
        source_id=source_id,
        stream_id=stream_id,
        seq=seq,
        sample_index=sample_index,
        frame_count=frame_count,
        state=state,
        speech_probability=probability,
    )


def _dora_activity_event(activity: VoiceActivityEvent):
    payload, metadata = encode_voice_activity_event_for_dora(activity)
    return {
        "type": "INPUT",
        "id": "activity",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _dora_activity_final_event(*, seq: int, sample_index: int):
    payload, metadata = encode_voice_activity_final_marker_for_dora(
        source_id="silero_vad",
        stream_id="activity/main",
        seq=seq,
        sample_index=sample_index,
    )
    return {
        "type": "INPUT",
        "id": "activity",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _decode_turn_outputs(fake_node: FakeDoraNode):
    turn_events = []
    final_marker = None
    for output_id, payload, metadata in fake_node.sent:
        assert output_id == "turn"
        assert metadata is not None
        turn_metadata = validate_dora_turn_metadata(metadata)
        if turn_metadata.final:
            final_marker = validate_dora_turn_final_marker(payload, turn_metadata)
        else:
            turn_events.append(decode_turn_event_from_dora(payload, turn_metadata))
    assert final_marker is not None
    return turn_events, final_marker


def test_turn_detector_node_emits_turn_events_and_final_marker() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_activity_event(
                _activity(seq=0, sample_index=0, state="speech", probability=0.9)
            ),
            _dora_activity_event(
                _activity(seq=1, sample_index=512, state="speech", probability=0.8)
            ),
            _dora_activity_event(
                _activity(seq=2, sample_index=1024, state="silence", probability=0.1)
            ),
            _dora_activity_event(
                _activity(seq=3, sample_index=1536, state="silence", probability=0.1)
            ),
            _dora_activity_final_event(seq=4, sample_index=2048),
        ]
    )

    summary = run_turn_detector_events(fake_node, _config(end_silence_frames=1024))
    turn_events, final_marker = _decode_turn_outputs(fake_node)

    assert summary.activity_events == 4
    assert summary.turn_events == 3
    assert summary.started_events == 1
    assert summary.ended_events == 1
    assert [event.state for event in turn_events] == ["started", "active", "ended"]
    assert [event.seq for event in turn_events] == [0, 1, 2]
    assert [event.sample_index for event in turn_events] == [0, 512, 1024]
    assert final_marker.seq == 3
    assert final_marker.sample_index == 2048


def test_turn_detector_node_accepts_input_closed_completion() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_activity_event(
                _activity(seq=0, sample_index=0, state="speech", probability=0.9)
            ),
            {"type": "INPUT_CLOSED", "id": "activity"},
        ]
    )

    summary = run_turn_detector_events(fake_node, _config())
    turn_events, final_marker = _decode_turn_outputs(fake_node)

    assert summary.turn_events == 2
    assert [event.state for event in turn_events] == ["started", "ended"]
    assert final_marker.sample_index == 512


def test_turn_detector_node_rejects_activity_source_mismatch() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_activity_event(
                _activity(
                    seq=0,
                    sample_index=0,
                    state="speech",
                    probability=0.9,
                    source_id="other",
                )
            )
        ]
    )

    with pytest.raises(TurnDetectorNodeError, match="source mismatch"):
        run_turn_detector_events(fake_node, _config())


def test_turn_detector_node_rejects_activity_stream_mismatch() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_activity_event(
                _activity(
                    seq=0,
                    sample_index=0,
                    state="speech",
                    probability=0.9,
                    stream_id="activity/other",
                )
            )
        ]
    )

    with pytest.raises(TurnDetectorNodeError, match="stream mismatch"):
        run_turn_detector_events(fake_node, _config())


def test_turn_detector_node_rejects_final_before_activity_events() -> None:
    fake_node = FakeDoraNode([_dora_activity_final_event(seq=0, sample_index=0)])

    with pytest.raises(TurnDetectorNodeError, match="before activity events"):
        run_turn_detector_events(fake_node, _config())


def test_turn_detector_node_rejects_missing_completion() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_activity_event(
                _activity(seq=0, sample_index=0, state="speech", probability=0.9)
            )
        ]
    )

    with pytest.raises(TurnDetectorNodeError, match="without completion"):
        run_turn_detector_events(fake_node, _config())
