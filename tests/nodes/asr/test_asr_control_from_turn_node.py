import pytest

from fluent_audio.contracts import AsrCancel, AsrStart, AsrStop, TurnEvent
from fluent_audio.dora import (
    decode_asr_control_from_dora,
    encode_turn_event_for_dora,
    encode_turn_final_marker_for_dora,
    validate_dora_asr_control_final_marker,
    validate_dora_asr_control_metadata,
)
from nodes.asr.asr_control_from_turn.main import (
    AsrControlFromTurnConfig,
    AsrControlFromTurnError,
    run_asr_control_from_turn_events,
)


class FakeDoraNode:
    def __init__(self, events) -> None:
        self._events = events
        self.sent = []

    def __iter__(self):
        return iter(self._events)

    def send_output(self, output_id, data, metadata=None) -> None:
        self.sent.append((output_id, data, metadata))


def _config(*, asr_prebuffer_frames: int = 0) -> AsrControlFromTurnConfig:
    return AsrControlFromTurnConfig(
        input_session_id="session-1",
        input_turn_stream_id="turn/main",
        output_audio_stream_id="audio/asr/input",
        asr_prebuffer_frames=asr_prebuffer_frames,
        output_drain_seconds=0.0,
    )


def _turn(
    *,
    seq: int,
    state: str,
    sample_index: int,
    user_turn_id: str = "user-turn-000001",
) -> TurnEvent:
    return TurnEvent(
        session_id="session-1",
        user_turn_id=user_turn_id,
        stream_id="turn/main",
        seq=seq,
        sample_index=sample_index,
        state=state,
    )


def _dora_turn_event(turn: TurnEvent):
    payload, metadata = encode_turn_event_for_dora(turn)
    return {
        "type": "INPUT",
        "id": "turn",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _dora_turn_final_event(*, seq: int, sample_index: int):
    payload, metadata = encode_turn_final_marker_for_dora(
        session_id="session-1",
        stream_id="turn/main",
        seq=seq,
        sample_index=sample_index,
    )
    return {
        "type": "INPUT",
        "id": "turn",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _decode_controls(fake_node: FakeDoraNode):
    controls = []
    final_marker = None
    for output_id, payload, metadata in fake_node.sent:
        assert output_id == "asr_control"
        asr_metadata = validate_dora_asr_control_metadata(metadata)
        if asr_metadata.final:
            final_marker = validate_dora_asr_control_final_marker(payload, asr_metadata)
            continue
        controls.append(decode_asr_control_from_dora(payload, asr_metadata))
    assert final_marker is not None
    return controls, final_marker


def test_asr_control_from_turn_emits_start_and_stop_with_prebuffer() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_turn_event(_turn(seq=0, state="started", sample_index=2048)),
            _dora_turn_event(_turn(seq=1, state="active", sample_index=4096)),
            _dora_turn_event(_turn(seq=2, state="ended", sample_index=8192)),
            _dora_turn_final_event(seq=3, sample_index=12000),
        ]
    )

    summary = run_asr_control_from_turn_events(
        fake_node,
        _config(asr_prebuffer_frames=512),
    )
    controls, final_marker = _decode_controls(fake_node)

    assert summary.turn_events == 3
    assert summary.start_controls == 1
    assert summary.stop_controls == 1
    assert summary.cancel_controls == 0
    assert summary.final_sample_index == 12000
    assert isinstance(controls[0], AsrStart)
    assert controls[0].seq == 0
    assert controls[0].stream_id == "audio/asr/input"
    assert controls[0].start_sample_index == 1536
    assert isinstance(controls[1], AsrStop)
    assert controls[1].seq == 1
    assert controls[1].stop_sample_index == 8192
    assert final_marker.seq == 2
    assert final_marker.session_id == "session-1"
    assert final_marker.stream_id == "audio/asr/input"


def test_asr_control_from_turn_clamps_prebuffer_to_zero() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_turn_event(_turn(seq=0, state="started", sample_index=128)),
            _dora_turn_event(_turn(seq=1, state="ended", sample_index=1024)),
            _dora_turn_final_event(seq=2, sample_index=2048),
        ]
    )

    run_asr_control_from_turn_events(fake_node, _config(asr_prebuffer_frames=512))
    controls, final_marker = _decode_controls(fake_node)

    assert isinstance(controls[0], AsrStart)
    assert controls[0].start_sample_index == 0
    assert final_marker.seq == 2


def test_asr_control_from_turn_emits_cancel() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_turn_event(_turn(seq=0, state="started", sample_index=2048)),
            _dora_turn_event(_turn(seq=1, state="cancelled", sample_index=4096)),
            _dora_turn_final_event(seq=2, sample_index=4096),
        ]
    )

    summary = run_asr_control_from_turn_events(fake_node, _config())
    controls, final_marker = _decode_controls(fake_node)

    assert summary.cancel_controls == 1
    assert isinstance(controls[1], AsrCancel)
    assert controls[1].seq == 1
    assert controls[1].reason == "turn_cancelled"
    assert final_marker.seq == 2


def test_asr_control_from_turn_rejects_final_while_active() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_turn_event(_turn(seq=0, state="started", sample_index=2048)),
            _dora_turn_final_event(seq=1, sample_index=4096),
        ]
    )

    with pytest.raises(AsrControlFromTurnError, match="active"):
        run_asr_control_from_turn_events(fake_node, _config())


def test_asr_control_from_turn_rejects_turn_seq_gap() -> None:
    fake_node = FakeDoraNode(
        [
            _dora_turn_event(_turn(seq=0, state="started", sample_index=2048)),
            _dora_turn_event(_turn(seq=2, state="ended", sample_index=4096)),
        ]
    )

    with pytest.raises(AsrControlFromTurnError, match="seq discontinuity"):
        run_asr_control_from_turn_events(fake_node, _config())
