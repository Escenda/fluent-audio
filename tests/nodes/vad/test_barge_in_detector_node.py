from fluent_dialogue_dora.contracts import PlaybackState, VoiceActivityEvent
from fluent_dialogue_dora.dora import (
    decode_barge_in_event_from_dora,
    encode_playback_state_for_dora,
    encode_voice_activity_event_for_dora,
    validate_dora_barge_in_metadata,
)
from nodes.vad.barge_in_detector.main import (
    BargeInDetectorNodeConfig,
    run_barge_in_detector_events,
)


class FakeDoraNode:
    def __init__(self, events) -> None:
        self._events = events
        self.sent = []

    def __iter__(self):
        return iter(self._events)

    def send_output(self, output_id, data, metadata=None) -> None:
        self.sent.append((output_id, data, metadata))


def _config(*, barge_in_speech_frames: int = 1024) -> BargeInDetectorNodeConfig:
    return BargeInDetectorNodeConfig(
        session_id="session-1",
        source_id="barge_in_detector",
        output_stream_id="barge_in/main",
        barge_in_speech_frames=barge_in_speech_frames,
        silence_reset_frames=1024,
        min_speech_probability=0.5,
    )


def _playback_state(*, request_id: str, state: str, seq: int, played_frames: int):
    payload, metadata = encode_playback_state_for_dora(
        PlaybackState(
            request_id=request_id,
            session_id="session-1",
            user_turn_id="user-1",
            stream_id="speaker/main",
            state=state,
            seq=seq,
            played_frames=played_frames,
        )
    )
    return {
        "type": "INPUT",
        "id": "playback_state",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _activity(*, seq: int, sample_index: int, state: str, probability: float, frame_count: int = 512):
    payload, metadata = encode_voice_activity_event_for_dora(
        VoiceActivityEvent(
            source_id="silero_vad",
            stream_id="activity/main",
            seq=seq,
            sample_index=sample_index,
            frame_count=frame_count,
            state=state,
            speech_probability=probability,
        )
    )
    return {
        "type": "INPUT",
        "id": "activity",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _stop():
    return {"type": "STOP"}


def _barge_in_outputs(node):
    out = []
    for output_id, data, metadata in node.sent:
        meta = validate_dora_barge_in_metadata(metadata)
        if meta.message_type.endswith("BargeInEvent"):
            out.append(decode_barge_in_event_from_dora(data, metadata))
    return out


def test_sustained_speech_while_playing_fires_once():
    events = [
        _playback_state(request_id="tts-000000", state="playing", seq=0, played_frames=8000),
        _activity(seq=0, sample_index=0, state="speech", probability=0.9),
        _activity(seq=1, sample_index=512, state="speech", probability=0.9),
        # threshold 1024 crossed after two 512-frame speech events
        _activity(seq=2, sample_index=1024, state="speech", probability=0.9),
        _stop(),
    ]
    node = FakeDoraNode(events)
    summary = run_barge_in_detector_events(node, _config())
    barge_ins = _barge_in_outputs(node)
    assert len(barge_ins) == 1
    assert summary.barge_in_events == 1
    event = barge_ins[0]
    assert event.playback_request_id == "tts-000000"
    assert event.playback_stream_id == "speaker/main"
    assert event.played_frames == 8000


def test_speech_without_playback_does_not_fire():
    events = [
        _activity(seq=0, sample_index=0, state="speech", probability=0.9),
        _activity(seq=1, sample_index=512, state="speech", probability=0.9),
        _activity(seq=2, sample_index=1024, state="speech", probability=0.9),
        _stop(),
    ]
    node = FakeDoraNode(events)
    run_barge_in_detector_events(node, _config())
    assert _barge_in_outputs(node) == []


def test_short_speech_below_threshold_does_not_fire():
    events = [
        _playback_state(request_id="tts-000000", state="playing", seq=0, played_frames=100),
        _activity(seq=0, sample_index=0, state="speech", probability=0.9),
        _stop(),
    ]
    node = FakeDoraNode(events)
    run_barge_in_detector_events(node, _config(barge_in_speech_frames=2048))
    assert _barge_in_outputs(node) == []


def test_low_probability_speech_does_not_count():
    events = [
        _playback_state(request_id="tts-000000", state="playing", seq=0, played_frames=100),
        _activity(seq=0, sample_index=0, state="speech", probability=0.2),
        _activity(seq=1, sample_index=512, state="speech", probability=0.2),
        _activity(seq=2, sample_index=1024, state="speech", probability=0.2),
        _stop(),
    ]
    node = FakeDoraNode(events)
    run_barge_in_detector_events(node, _config())
    assert _barge_in_outputs(node) == []


def test_disarm_after_playback_stops():
    events = [
        _playback_state(request_id="tts-000000", state="playing", seq=0, played_frames=100),
        _playback_state(request_id="tts-000000", state="completed", seq=1, played_frames=200),
        _activity(seq=0, sample_index=0, state="speech", probability=0.9),
        _activity(seq=1, sample_index=512, state="speech", probability=0.9),
        _activity(seq=2, sample_index=1024, state="speech", probability=0.9),
        _stop(),
    ]
    node = FakeDoraNode(events)
    run_barge_in_detector_events(node, _config())
    assert _barge_in_outputs(node) == []


def test_silence_resets_speech_run():
    events = [
        _playback_state(request_id="tts-000000", state="playing", seq=0, played_frames=100),
        _activity(seq=0, sample_index=0, state="speech", probability=0.9),
        _activity(seq=1, sample_index=512, state="silence", probability=0.1, frame_count=1024),
        # run was reset by 1024 frames of silence; a single speech event is below threshold
        _activity(seq=2, sample_index=1536, state="speech", probability=0.9),
        _stop(),
    ]
    node = FakeDoraNode(events)
    run_barge_in_detector_events(node, _config())
    assert _barge_in_outputs(node) == []


def test_new_request_rearms_after_fire():
    events = [
        _playback_state(request_id="tts-000000", state="playing", seq=0, played_frames=100),
        _activity(seq=0, sample_index=0, state="speech", probability=0.9),
        _activity(seq=1, sample_index=512, state="speech", probability=0.9),
        # fires for tts-000000
        _playback_state(request_id="tts-000001", state="playing", seq=2, played_frames=4000),
        _activity(seq=2, sample_index=1024, state="speech", probability=0.9),
        _activity(seq=3, sample_index=1536, state="speech", probability=0.9),
        # fires for tts-000001
        _stop(),
    ]
    node = FakeDoraNode(events)
    run_barge_in_detector_events(node, _config())
    barge_ins = _barge_in_outputs(node)
    assert [b.playback_request_id for b in barge_ins] == ["tts-000000", "tts-000001"]
    assert barge_ins[1].played_frames == 4000
