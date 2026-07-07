import base64

import pytest

from fluent_dialogue_dora.contracts import AudioFormat, SynthesizedAudioChunk, TtsTextChunk, TtsTextStreamFinal
from fluent_dialogue_dora.dora import (
    decode_synthesized_audio_chunk_from_dora,
    encode_tts_text_chunk_for_dora,
    encode_tts_text_stream_final_marker_for_dora,
    validate_dora_synthesized_audio_final_marker,
    validate_dora_synthesized_audio_metadata,
)
from nodes.tts.tts_backend.main import (
    TtsBackendAudioChunkEvent,
    TtsBackendAudioDoneEvent,
    TtsBackendConfig,
    TtsBackendNodeError,
    TtsBackendPostRequest,
    parse_tts_backend_event_line,
    run_tts_backend_events,
)


class FakeDoraNode:
    def __init__(self, events) -> None:
        self._events = events
        self.sent = []

    def __iter__(self):
        return iter(self._events)

    def send_output(self, output_id, data, metadata=None) -> None:
        self.sent.append((output_id, data, metadata))


class FakeTtsBackendTransport:
    def __init__(self, *, lines: tuple[str, ...]) -> None:
        self._lines = lines
        self.requests: list[TtsBackendPostRequest] = []

    def post_tts_text(self, request: TtsBackendPostRequest) -> tuple[str, ...]:
        self.requests.append(request)
        return self._lines


def _config() -> TtsBackendConfig:
    return TtsBackendConfig(
        endpoint_url="http://tts.local/synthesize",
        default_voice_id="voice-main",
        output_drain_seconds=0.0,
    )


def _text_chunk() -> TtsTextChunk:
    return TtsTextChunk(
        request_id="tts-1",
        session_id="session-1",
        user_turn_id="user-turn-1",
        assistant_turn_id="assistant-turn-1",
        seq=0,
        text="hello",
        is_final=True,
    )


def _input(input_id: str, encoded):
    payload, metadata = encoded
    return {
        "type": "INPUT",
        "id": input_id,
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _tts_text_event(chunk: TtsTextChunk):
    return _input("tts_text", encode_tts_text_chunk_for_dora(chunk))


def _tts_text_stream_final_event():
    return _input(
        "tts_text",
        encode_tts_text_stream_final_marker_for_dora(
            TtsTextStreamFinal(
                session_id="session-1",
                user_turn_id="user-turn-1",
                assistant_turn_id="assistant-turn-1",
                seq=1,
            )
        ),
    )


def _audio_format() -> AudioFormat:
    return AudioFormat(sample_rate_hz=16_000, channels=1, sample_format="s16le")


def _audio_payload() -> bytes:
    return b"\x01\x00\x02\x00\x03\x00\x04\x00"


def _audio_chunk_line(
    *,
    request_id: str = "tts-1",
    seq: int = 0,
    audio_seq: int = 0,
    audio_sample_index: int = 0,
    audio_frame_count: int = 4,
    audio_format: AudioFormat | None = None,
    payload_b64: str | None = None,
) -> str:
    payload = payload_b64
    if payload is None:
        payload = base64.b64encode(_audio_payload()).decode("ascii")
    event_audio_format = audio_format
    if event_audio_format is None:
        event_audio_format = _audio_format()
    return TtsBackendAudioChunkEvent(
        event="audio_chunk",
        request_id=request_id,
        session_id="session-1",
        assistant_turn_id="assistant-turn-1",
        seq=seq,
        audio_source_id="tts_backend",
        audio_stream_id="tts-1/audio",
        audio_seq=audio_seq,
        audio_sample_index=audio_sample_index,
        audio_capture_time_ns=audio_sample_index * 1_000,
        audio_frame_count=audio_frame_count,
        audio_format=event_audio_format,
        payload_b64=payload,
    ).model_dump_json()


def _audio_done_line(
    *,
    request_id: str = "tts-1",
    seq: int = 1,
    audio_seq: int = 1,
    audio_sample_index: int = 4,
    audio_format: AudioFormat | None = None,
) -> str:
    event_audio_format = audio_format
    if event_audio_format is None:
        event_audio_format = _audio_format()
    return TtsBackendAudioDoneEvent(
        event="audio_done",
        request_id=request_id,
        session_id="session-1",
        assistant_turn_id="assistant-turn-1",
        seq=seq,
        audio_source_id="tts_backend",
        audio_stream_id="tts-1/audio",
        audio_seq=audio_seq,
        audio_sample_index=audio_sample_index,
        audio_capture_time_ns=audio_sample_index * 1_000,
        audio_format=event_audio_format,
    ).model_dump_json()


def _decode_outputs(fake_node: FakeDoraNode):
    chunks: list[SynthesizedAudioChunk] = []
    finals = []
    for output_id, payload, metadata in fake_node.sent:
        assert output_id == "synth_audio"
        assert metadata is not None
        synth_metadata = validate_dora_synthesized_audio_metadata(metadata)
        if synth_metadata.final:
            finals.append(validate_dora_synthesized_audio_final_marker(payload, metadata))
        else:
            chunks.append(decode_synthesized_audio_chunk_from_dora(payload, synth_metadata))
    return chunks, finals


def test_tts_backend_projects_validated_audio_stream_to_dora() -> None:
    chunk = _text_chunk()
    transport = FakeTtsBackendTransport(lines=(_audio_chunk_line(), _audio_done_line()))
    fake_node = FakeDoraNode([_tts_text_event(chunk), {"type": "STOP"}])

    summary = run_tts_backend_events(fake_node, _config(), transport)
    chunks, finals = _decode_outputs(fake_node)

    assert transport.requests == [TtsBackendPostRequest(chunk=chunk, voice_id="voice-main")]
    assert summary.tts_text_chunks == 1
    assert summary.tts_text_stream_finals == 0
    assert summary.synthesized_audio_chunks == 1
    assert summary.synthesized_audio_finals == 1
    assert chunks == [
        SynthesizedAudioChunk(
            request_id="tts-1",
            session_id="session-1",
            user_turn_id="user-turn-1",
            assistant_turn_id="assistant-turn-1",
            seq=0,
            audio=chunks[0].audio,
        )
    ]
    assert chunks[0].audio.payload == _audio_payload()
    assert finals[0].request_id == "tts-1"
    assert finals[0].audio_sample_index == 4


def test_tts_backend_accepts_sse_data_lines_and_blank_separators() -> None:
    chunk = _text_chunk()
    transport = FakeTtsBackendTransport(
        lines=(
            "\n",
            f"data: {_audio_chunk_line()}\n",
            "",
            f"data: {_audio_done_line()}\n",
        ),
    )
    fake_node = FakeDoraNode([_tts_text_event(chunk), {"type": "STOP"}])

    summary = run_tts_backend_events(fake_node, _config(), transport)
    chunks, finals = _decode_outputs(fake_node)

    assert summary.synthesized_audio_chunks == 1
    assert summary.synthesized_audio_finals == 1
    assert chunks[0].request_id == "tts-1"
    assert finals[0].request_id == "tts-1"


def test_tts_backend_accepts_text_stream_final_without_http_call() -> None:
    transport = FakeTtsBackendTransport(lines=())
    fake_node = FakeDoraNode([_tts_text_stream_final_event(), {"type": "STOP"}])

    summary = run_tts_backend_events(fake_node, _config(), transport)

    assert summary.tts_text_stream_finals == 1
    assert summary.synthesized_audio_chunks == 0
    assert summary.synthesized_audio_finals == 0
    assert transport.requests == []
    assert fake_node.sent == []


def test_tts_backend_requires_audio_done_for_each_request() -> None:
    transport = FakeTtsBackendTransport(lines=(_audio_chunk_line(),))
    fake_node = FakeDoraNode([_tts_text_event(_text_chunk()), {"type": "STOP"}])

    with pytest.raises(TtsBackendNodeError, match="without exactly one audio_done"):
        run_tts_backend_events(fake_node, _config(), transport)


def test_tts_backend_rejects_mismatched_request_id() -> None:
    transport = FakeTtsBackendTransport(
        lines=(_audio_chunk_line(request_id="other-tts"), _audio_done_line()),
    )
    fake_node = FakeDoraNode([_tts_text_event(_text_chunk()), {"type": "STOP"}])

    with pytest.raises(TtsBackendNodeError, match="request_id"):
        run_tts_backend_events(fake_node, _config(), transport)


def test_tts_backend_rejects_invalid_base64_payload() -> None:
    transport = FakeTtsBackendTransport(
        lines=(_audio_chunk_line(payload_b64="not base64"), _audio_done_line()),
    )
    fake_node = FakeDoraNode([_tts_text_event(_text_chunk()), {"type": "STOP"}])

    with pytest.raises(TtsBackendNodeError, match="payload_b64"):
        run_tts_backend_events(fake_node, _config(), transport)


def test_tts_backend_rejects_payload_format_mismatch() -> None:
    short_payload = base64.b64encode(b"\x00\x00").decode("ascii")
    transport = FakeTtsBackendTransport(
        lines=(_audio_chunk_line(payload_b64=short_payload), _audio_done_line()),
    )
    fake_node = FakeDoraNode([_tts_text_event(_text_chunk()), {"type": "STOP"}])

    with pytest.raises(TtsBackendNodeError, match="did not validate"):
        run_tts_backend_events(fake_node, _config(), transport)


def test_tts_backend_rejects_event_after_audio_done() -> None:
    transport = FakeTtsBackendTransport(
        lines=(
            _audio_done_line(seq=0, audio_seq=0, audio_sample_index=0),
            _audio_chunk_line(seq=1, audio_seq=0, audio_sample_index=0),
        ),
    )
    fake_node = FakeDoraNode([_tts_text_event(_text_chunk()), {"type": "STOP"}])

    with pytest.raises(TtsBackendNodeError, match="after audio_done"):
        run_tts_backend_events(fake_node, _config(), transport)


def test_tts_backend_rejects_audio_sequence_discontinuity() -> None:
    transport = FakeTtsBackendTransport(
        lines=(_audio_chunk_line(audio_seq=1), _audio_done_line()),
    )
    fake_node = FakeDoraNode([_tts_text_event(_text_chunk()), {"type": "STOP"}])

    with pytest.raises(TtsBackendNodeError, match="audio_seq discontinuity"):
        run_tts_backend_events(fake_node, _config(), transport)


def test_tts_backend_rejects_audio_format_change_before_done() -> None:
    transport = FakeTtsBackendTransport(
        lines=(
            _audio_chunk_line(),
            _audio_done_line(
                audio_format=AudioFormat(
                    sample_rate_hz=16_000,
                    channels=1,
                    sample_format="f32le",
                )
            ),
        ),
    )
    fake_node = FakeDoraNode([_tts_text_event(_text_chunk()), {"type": "STOP"}])

    with pytest.raises(TtsBackendNodeError, match="format changed"):
        run_tts_backend_events(fake_node, _config(), transport)


def test_parse_tts_backend_event_line_rejects_invalid_json_and_empty_sse_data() -> None:
    assert parse_tts_backend_event_line("") is None
    assert parse_tts_backend_event_line("  \n") is None

    with pytest.raises(TtsBackendNodeError, match="invalid"):
        parse_tts_backend_event_line('{"event":"audio_chunk"}')

    with pytest.raises(TtsBackendNodeError, match="must not be empty"):
        parse_tts_backend_event_line("data: \n")
