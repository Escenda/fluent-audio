import pytest

from fluent_dialogue_dora.contracts import (
    AgentMcpElicitationRequest,
    AgentTextDelta,
    AgentTurnDone,
    AgentTurnRequest,
    AgentUserInputQuestion,
    AgentUserInputRequest,
    BargeInEvent,
    DialogueEvent,
    DialogueInput,
    PlaybackState,
    TranscriptFinal,
    TtsTextChunk,
    TtsTextStreamFinal,
    VoiceSessionEvent,
)
from fluent_dialogue_dora.dora import (
    decode_agent_cancel_request_from_dora,
    decode_agent_turn_request_from_dora,
    decode_dialogue_event_from_dora,
    decode_playback_command_from_dora,
    decode_playback_control_command_from_dora,
    decode_tts_text_chunk_from_dora,
    decode_voice_session_event_from_dora,
    encode_agent_runtime_event_for_dora,
    encode_barge_in_event_for_dora,
    encode_dialogue_input_for_dora,
    encode_playback_state_for_dora,
    encode_transcript_final_for_dora,
    encode_transcript_stream_final_marker_for_dora,
    validate_dora_agent_cancel_metadata,
    validate_dora_agent_turn_request_metadata,
    validate_dora_dialogue_event_metadata,
    validate_dora_playback_command_metadata,
    validate_dora_playback_control_metadata,
    validate_dora_tts_text_metadata,
    validate_dora_tts_text_stream_final_marker,
    validate_dora_voice_session_metadata,
)
from nodes.dialogue_engine.main import (
    DialogueEngineConfig,
    DialogueEngineError,
    run_dialogue_engine_events,
)


class FakeDoraNode:
    def __init__(self, events) -> None:
        self._events = events
        self.sent = []

    def __iter__(self):
        return iter(self._events)

    def send_output(self, output_id, data, metadata=None) -> None:
        self.sent.append((output_id, data, metadata))


def _config() -> DialogueEngineConfig:
    return DialogueEngineConfig(
        session_id="session-1",
        transcript_stream_id="transcript/main",
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


def _transcript_final(text: str = "hello", *, user_turn_id: str = "user-turn-1") -> TranscriptFinal:
    return TranscriptFinal(
        session_id="session-1",
        user_turn_id=user_turn_id,
        stream_id="transcript/main",
        seq=0,
        text=text,
        start_sample_index=0,
        end_sample_index=1600,
    )


def _transcript_final_event(text: str = "hello", *, user_turn_id: str = "user-turn-1"):
    return _input(
        "transcript",
        encode_transcript_final_for_dora(_transcript_final(text, user_turn_id=user_turn_id)),
    )


def _transcript_stream_final_event():
    return _input(
        "transcript",
        encode_transcript_stream_final_marker_for_dora(
            session_id="session-1",
            stream_id="transcript/main",
            seq=1,
            sample_index=1600,
        ),
    )


def _agent_text(
    text: str,
    *,
    seq: int = 0,
    user_turn_id: str = "user-turn-1",
    agent_turn_id: str = "assistant-turn-000000",
):
    return _input(
        "agent_event",
        encode_agent_runtime_event_for_dora(
            AgentTextDelta(
                session_id="session-1",
                user_turn_id=user_turn_id,
                agent_turn_id=agent_turn_id,
                seq=seq,
                text=text,
            )
        ),
    )


def _agent_user_input_request():
    return _input(
        "agent_event",
        encode_agent_runtime_event_for_dora(
            AgentUserInputRequest(
                session_id="session-1",
                user_turn_id="user-turn-1",
                request_id="input-1",
                seq=1,
                questions=(
                    AgentUserInputQuestion(
                        id="q1",
                        header="Confirm",
                        question="Continue?",
                    ),
                ),
            )
        ),
    )


def _agent_mcp_elicitation_request():
    return _input(
        "agent_event",
        encode_agent_runtime_event_for_dora(
            AgentMcpElicitationRequest(
                session_id="session-1",
                user_turn_id="user-turn-1",
                request_id="mcp-1",
                seq=2,
                server_name="robot",
                mode="url",
                message="Open robot console?",
                url="https://example.invalid",
                elicitation_id="elicit-1",
            )
        ),
    )


def _agent_done(
    status: str = "completed",
    *,
    user_turn_id: str = "user-turn-1",
    agent_turn_id: str = "assistant-turn-000000",
    message: str | None = None,
):
    if status == "cancelled" and message is None:
        message = "cancelled"
    return _input(
        "agent_event",
        encode_agent_runtime_event_for_dora(
            AgentTurnDone(
                session_id="session-1",
                user_turn_id=user_turn_id,
                agent_turn_id=agent_turn_id,
                seq=10,
                status=status,
                message=message,
            )
        ),
    )


def _dialogue_cancel():
    return _input(
        "dialogue_input",
        encode_dialogue_input_for_dora(
            DialogueInput(
                input_type="cancel",
                session_id="session-1",
                user_turn_id="user-turn-1",
                seq=0,
            )
        ),
    )


def _decode_outputs(fake_node: FakeDoraNode):
    agent_turns: list[AgentTurnRequest] = []
    session_events: list[VoiceSessionEvent] = []
    dialogue_events: list[DialogueEvent] = []
    tts_chunks: list[TtsTextChunk] = []
    tts_stream_finals: list[TtsTextStreamFinal] = []
    agent_cancels = []
    for output_id, payload, metadata in fake_node.sent:
        assert metadata is not None
        if output_id == "agent_turn":
            turn_metadata = validate_dora_agent_turn_request_metadata(metadata)
            agent_turns.append(decode_agent_turn_request_from_dora(payload, turn_metadata))
        elif output_id == "session":
            session_metadata = validate_dora_voice_session_metadata(metadata)
            session_events.append(decode_voice_session_event_from_dora(payload, session_metadata))
        elif output_id == "dialogue":
            dialogue_metadata = validate_dora_dialogue_event_metadata(metadata)
            dialogue_events.append(decode_dialogue_event_from_dora(payload, dialogue_metadata))
        elif output_id == "tts_text":
            tts_metadata = validate_dora_tts_text_metadata(metadata)
            if tts_metadata.kind == "stream_final":
                tts_stream_finals.append(
                    validate_dora_tts_text_stream_final_marker(payload, tts_metadata)
                )
            else:
                tts_chunks.append(decode_tts_text_chunk_from_dora(payload, tts_metadata))
        elif output_id == "agent_cancel":
            cancel_metadata = validate_dora_agent_cancel_metadata(metadata)
            agent_cancels.append(decode_agent_cancel_request_from_dora(payload, cancel_metadata))
        else:
            raise AssertionError(f"unexpected output id: {output_id}")
    return (
        agent_turns,
        session_events,
        dialogue_events,
        tts_chunks,
        tts_stream_finals,
        agent_cancels,
    )


def test_dialogue_engine_turns_transcript_and_agent_stream_into_tts_chunks() -> None:
    fake_node = FakeDoraNode(
        [
            _transcript_final_event("what is the weather"),
            _agent_text("Hello. Next", seq=0),
            _agent_done(),
            _transcript_stream_final_event(),
            {"type": "STOP"},
        ]
    )

    summary = run_dialogue_engine_events(fake_node, _config())
    (
        agent_turns,
        session_events,
        dialogue_events,
        tts_chunks,
        tts_stream_finals,
        agent_cancels,
    ) = _decode_outputs(fake_node)

    assert summary.transcript_finals == 1
    assert summary.agent_turn_requests == 1
    assert summary.agent_text_deltas == 1
    assert summary.agent_turn_done == 1
    assert summary.tts_text_chunks == 2
    assert summary.tts_text_stream_finals == 1
    assert agent_cancels == []
    assert agent_turns == [
        AgentTurnRequest(
            session_id="session-1",
            user_turn_id="user-turn-1",
            assistant_turn_id="assistant-turn-000000",
            seq=0,
            text="what is the weather",
        )
    ]
    assert [event.event for event in session_events] == [
        "user_turn_finalized",
        "assistant_turn_started",
        "assistant_turn_completed",
    ]
    assert [event.event for event in dialogue_events] == [
        "agent_text",
        "tts_text",
        "tts_text",
    ]
    assert [(chunk.text, chunk.is_final) for chunk in tts_chunks] == [
        ("Hello.", False),
        ("Next", True),
    ]
    assert tts_stream_finals == [
        TtsTextStreamFinal(
            session_id="session-1",
            user_turn_id="user-turn-1",
            assistant_turn_id="assistant-turn-000000",
            seq=2,
        )
    ]


def test_dialogue_engine_chunks_when_punctuation_arrives_as_separate_delta() -> None:
    fake_node = FakeDoraNode(
        [
            _transcript_final_event("返答して"),
            _agent_text("できます", seq=0),
            _agent_text("。", seq=1),
            _agent_text("次です", seq=2),
            _agent_done(),
            _transcript_stream_final_event(),
            {"type": "STOP"},
        ]
    )

    summary = run_dialogue_engine_events(fake_node, _config())
    (
        _agent_turns,
        _session_events,
        dialogue_events,
        tts_chunks,
        _tts_stream_finals,
        _agent_cancels,
    ) = _decode_outputs(fake_node)

    assert summary.tts_text_chunks == 2
    assert [event.event for event in dialogue_events] == [
        "agent_text",
        "agent_text",
        "tts_text",
        "agent_text",
        "tts_text",
    ]
    assert [(chunk.text, chunk.is_final) for chunk in tts_chunks] == [
        ("できます。", False),
        ("次です", True),
    ]


def test_dialogue_engine_drops_stale_agent_delta_after_new_user_turn() -> None:
    fake_node = FakeDoraNode(
        [
            _transcript_final_event("最初"),
            _agent_text("古い返答です。", seq=0),
            _transcript_final_event("次の発話", user_turn_id="user-turn-2"),
            _agent_text(
                "これは遅れて届いた古い差分です。",
                seq=1,
                user_turn_id="user-turn-1",
                agent_turn_id="assistant-turn-000000",
            ),
            _agent_text(
                "新しい返答です。",
                seq=0,
                user_turn_id="user-turn-2",
                agent_turn_id="assistant-turn-000001",
            ),
            _agent_done(user_turn_id="user-turn-2", agent_turn_id="assistant-turn-000001"),
            _transcript_stream_final_event(),
            {"type": "STOP"},
        ]
    )

    summary = run_dialogue_engine_events(fake_node, _config())
    (
        agent_turns,
        _session_events,
        dialogue_events,
        _tts_chunks,
        _tts_stream_finals,
        agent_cancels,
    ) = _decode_outputs(fake_node)

    assert summary.transcript_finals == 2
    assert summary.agent_turn_requests == 2
    assert [turn.user_turn_id for turn in agent_turns] == ["user-turn-1", "user-turn-2"]
    assert [cancel.user_turn_id for cancel in agent_cancels] == ["user-turn-1"]
    assert all("遅れて届いた古い差分" not in (event.text or "") for event in dialogue_events)


def test_dialogue_engine_drops_punctuation_only_tts_chunks() -> None:
    fake_node = FakeDoraNode(
        [
            _transcript_final_event("返答して"),
            _agent_text("、", seq=0),
            _agent_text("できます", seq=1),
            _agent_text("。", seq=2),
            _agent_done(),
            _transcript_stream_final_event(),
            {"type": "STOP"},
        ]
    )

    summary = run_dialogue_engine_events(fake_node, _config())
    (
        _agent_turns,
        _session_events,
        dialogue_events,
        tts_chunks,
        _tts_stream_finals,
        _agent_cancels,
    ) = _decode_outputs(fake_node)

    assert summary.tts_text_chunks == 1
    assert [event.event for event in dialogue_events] == [
        "agent_text",
        "agent_text",
        "agent_text",
        "tts_text",
    ]
    assert [(chunk.text, chunk.is_final) for chunk in tts_chunks] == [
        ("できます。", False),
    ]


def test_dialogue_engine_turns_agent_user_input_and_mcp_requests_into_spoken_prompts() -> None:
    fake_node = FakeDoraNode(
        [
            _transcript_final_event("start operation"),
            _agent_user_input_request(),
            _agent_mcp_elicitation_request(),
            _agent_done(),
            _transcript_stream_final_event(),
            {"type": "STOP"},
        ]
    )

    summary = run_dialogue_engine_events(fake_node, _config())
    (
        _agent_turns,
        _session_events,
        dialogue_events,
        tts_chunks,
        _tts_stream_finals,
        _agent_cancels,
    ) = _decode_outputs(fake_node)

    assert summary.user_input_requests == 1
    assert summary.mcp_elicitation_requests == 1
    assert [event.event for event in dialogue_events] == [
        "user_input_requested",
        "tts_text",
        "mcp_elicitation_requested",
        "tts_text",
    ]
    assert [event.request_id for event in dialogue_events] == [
        "input-1",
        "tts-000000",
        "mcp-1",
        "tts-000001",
    ]
    assert [(chunk.text, chunk.is_final) for chunk in tts_chunks] == [
        ("Continue?", False),
        ("Open robot console?", False),
    ]


def test_dialogue_engine_filters_literal_think_blocks_before_tts() -> None:
    fake_node = FakeDoraNode(
        [
            _transcript_final_event("what is next"),
            _agent_text("<think>\n\n</think>\n\nHello.", seq=0),
            _agent_done(),
            _transcript_stream_final_event(),
            {"type": "STOP"},
        ]
    )

    summary = run_dialogue_engine_events(fake_node, _config())
    (
        _agent_turns,
        _session_events,
        dialogue_events,
        tts_chunks,
        tts_stream_finals,
        _agent_cancels,
    ) = _decode_outputs(fake_node)

    assert summary.agent_text_deltas == 1
    assert summary.tts_text_chunks == 1
    assert summary.tts_text_stream_finals == 1
    assert [event.event for event in dialogue_events] == [
        "agent_text",
        "tts_text",
    ]
    assert dialogue_events[0].text == "<think>\n\n</think>\n\nHello."
    assert [(chunk.text, chunk.is_final) for chunk in tts_chunks] == [("Hello.", False)]
    assert tts_stream_finals[0].seq == 1


def test_dialogue_engine_filters_split_literal_think_blocks_before_tts() -> None:
    fake_node = FakeDoraNode(
        [
            _transcript_final_event("what is next"),
            _agent_text("<thi", seq=0),
            _agent_text("nk>hidden reasoning", seq=1),
            _agent_text("</think>Visible", seq=2),
            _agent_done(),
            _transcript_stream_final_event(),
            {"type": "STOP"},
        ]
    )

    summary = run_dialogue_engine_events(fake_node, _config())
    (
        _agent_turns,
        _session_events,
        dialogue_events,
        tts_chunks,
        tts_stream_finals,
        _agent_cancels,
    ) = _decode_outputs(fake_node)

    assert summary.agent_text_deltas == 3
    assert summary.tts_text_chunks == 1
    assert summary.tts_text_stream_finals == 1
    assert [event.event for event in dialogue_events] == [
        "agent_text",
        "agent_text",
        "agent_text",
        "tts_text",
    ]
    assert [(chunk.text, chunk.is_final) for chunk in tts_chunks] == [("Visible", True)]
    assert tts_stream_finals[0].seq == 1


def test_dialogue_engine_normalizes_agent_markdown_before_tts() -> None:
    fake_node = FakeDoraNode(
        [
            _transcript_final_event("what changed"),
            _agent_text(
                "```python\nprint('unsafe')\n```\n"
                "- ファイルの作成・編集（PythonやJavascriptなど）- コードの変更。",
                seq=0,
            ),
            _agent_done(),
            _transcript_stream_final_event(),
            {"type": "STOP"},
        ]
    )

    summary = run_dialogue_engine_events(fake_node, _config())
    (
        _agent_turns,
        _session_events,
        _dialogue_events,
        tts_chunks,
        _tts_stream_finals,
        _agent_cancels,
    ) = _decode_outputs(fake_node)

    spoken = " ".join(chunk.text for chunk in tts_chunks)
    assert summary.tts_text_chunks == 2
    assert "```" not in spoken
    assert "print(" not in spoken
    assert not any(chunk.text.startswith("-") for chunk in tts_chunks)
    assert tts_chunks[0].text == "コードの詳細は画面に表示します。"


def test_dialogue_engine_summarizes_code_and_file_capability_lists_for_tts() -> None:
    fake_node = FakeDoraNode(
        [
            _transcript_final_event("何ができる？"),
            _agent_text(
                "- ファイルの作成・編集（PythonやJavaScriptなど）\n"
                "- コードの変更やコマンド実行\n"
                "- ツール呼び出し",
                seq=0,
            ),
            _agent_done(),
            _transcript_stream_final_event(),
            {"type": "STOP"},
        ]
    )

    summary = run_dialogue_engine_events(fake_node, _config())
    (
        _agent_turns,
        _session_events,
        _dialogue_events,
        tts_chunks,
        _tts_stream_finals,
        _agent_cancels,
    ) = _decode_outputs(fake_node)

    assert summary.tts_text_chunks == 1
    assert [(chunk.text, chunk.is_final) for chunk in tts_chunks] == [
        ("詳細は画面に表示します。", False),
    ]


def test_dialogue_engine_cancel_input_emits_agent_cancel_and_allows_stop() -> None:
    fake_node = FakeDoraNode(
        [
            _transcript_final_event(),
            _dialogue_cancel(),
            _transcript_stream_final_event(),
            {"type": "STOP"},
        ]
    )

    summary = run_dialogue_engine_events(fake_node, _config())
    (
        _agent_turns,
        session_events,
        dialogue_events,
        _tts_chunks,
        _tts_stream_finals,
        agent_cancels,
    ) = _decode_outputs(fake_node)

    assert summary.cancel_requests == 1
    assert len(agent_cancels) == 1
    assert agent_cancels[0].reason == "voice_cancel"
    assert session_events[-1].state == "interrupted"
    assert dialogue_events[-1].event == "cancelled"


def test_dialogue_engine_barge_in_starts_new_turn_and_accepts_old_cancel_ack() -> None:
    second_turn = TranscriptFinal(
        session_id="session-1",
        user_turn_id="user-turn-2",
        stream_id="transcript/main",
        seq=1,
        text="second question",
        start_sample_index=2000,
        end_sample_index=3200,
    )
    fake_node = FakeDoraNode(
        [
            _transcript_final_event("first question"),
            _input("transcript", encode_transcript_final_for_dora(second_turn)),
            _agent_done(
                "cancelled",
                user_turn_id="user-turn-1",
                agent_turn_id="assistant-turn-000000",
            ),
            _agent_text(
                "Fresh answer.",
                user_turn_id="user-turn-2",
                agent_turn_id="assistant-turn-000001",
            ),
            _agent_done(
                user_turn_id="user-turn-2",
                agent_turn_id="assistant-turn-000001",
            ),
            _transcript_stream_final_event(),
            {"type": "STOP"},
        ]
    )

    summary = run_dialogue_engine_events(fake_node, _config())
    (
        agent_turns,
        session_events,
        dialogue_events,
        tts_chunks,
        tts_stream_finals,
        agent_cancels,
    ) = _decode_outputs(fake_node)

    assert summary.agent_turn_requests == 2
    assert summary.cancel_requests == 1
    assert summary.agent_turn_done == 2
    assert summary.tts_text_stream_finals == 1
    assert [turn.user_turn_id for turn in agent_turns] == ["user-turn-1", "user-turn-2"]
    assert agent_turns[1].assistant_turn_id == "assistant-turn-000001"
    assert agent_cancels[0].user_turn_id == "user-turn-1"
    assert [event.event for event in session_events] == [
        "user_turn_finalized",
        "state_changed",
        "user_turn_finalized",
        "assistant_turn_started",
        "assistant_turn_completed",
    ]
    assert [event.event for event in dialogue_events] == [
        "cancelled",
        "agent_text",
        "tts_text",
    ]
    assert [(chunk.text, chunk.is_final) for chunk in tts_chunks] == [
        ("Fresh answer.", False),
    ]
    assert tts_stream_finals == [
        TtsTextStreamFinal(
            session_id="session-1",
            user_turn_id="user-turn-2",
            assistant_turn_id="assistant-turn-000001",
            seq=1,
        )
    ]


def test_dialogue_engine_rejects_non_cancelled_status_for_cancelled_turn() -> None:
    second_turn = TranscriptFinal(
        session_id="session-1",
        user_turn_id="user-turn-2",
        stream_id="transcript/main",
        seq=1,
        text="second question",
        start_sample_index=2000,
        end_sample_index=3200,
    )
    fake_node = FakeDoraNode(
        [
            _transcript_final_event("first question"),
            _input("transcript", encode_transcript_final_for_dora(second_turn)),
            _agent_done(
                "completed",
                user_turn_id="user-turn-1",
                agent_turn_id="assistant-turn-000000",
            ),
        ]
    )

    with pytest.raises(DialogueEngineError, match="non-cancelled status"):
        run_dialogue_engine_events(fake_node, _config())


def test_dialogue_engine_rejects_stop_while_agent_turn_is_active() -> None:
    fake_node = FakeDoraNode(
        [
            _transcript_final_event(),
            _transcript_stream_final_event(),
            {"type": "STOP"},
        ]
    )

    with pytest.raises(DialogueEngineError, match="agent turn is active"):
        run_dialogue_engine_events(fake_node, _config())


def _playback_state_event(*, request_id: str, state: str, seq: int, played_frames: int):
    return _input(
        "playback_state",
        encode_playback_state_for_dora(
            PlaybackState(
                request_id=request_id,
                session_id="session-1",
                user_turn_id="user-turn-1",
                stream_id="speaker/main",
                state=state,
                seq=seq,
                played_frames=played_frames,
            )
        ),
    )


def _barge_in_event(*, request_id: str, played_frames: int):
    return _input(
        "barge_in",
        encode_barge_in_event_for_dora(
            BargeInEvent(
                session_id="session-1",
                source_id="barge_in_detector",
                stream_id="barge_in/main",
                seq=0,
                playback_request_id=request_id,
                playback_stream_id="speaker/main",
                played_frames=played_frames,
                detected_sample_index=8000,
                speech_probability=0.95,
            )
        ),
    )


def _playback_outputs(fake_node):
    commands = []
    controls = []
    for output_id, data, metadata in fake_node.sent:
        if output_id == "playback_command":
            commands.append(
                decode_playback_command_from_dora(
                    data, validate_dora_playback_command_metadata(metadata)
                )
            )
        elif output_id == "playback_control":
            controls.append(
                decode_playback_control_command_from_dora(
                    data, validate_dora_playback_control_metadata(metadata)
                )
            )
    return commands, controls


def _agent_cancels(fake_node):
    cancels = []
    for output_id, data, metadata in fake_node.sent:
        if output_id == "agent_cancel":
            cancels.append(
                decode_agent_cancel_request_from_dora(
                    data, validate_dora_agent_cancel_metadata(metadata)
                )
            )
    return cancels


def test_dialogue_engine_barge_in_stops_playback_and_cancels_turn() -> None:
    fake_node = FakeDoraNode(
        [
            _transcript_final_event(),
            _agent_text("これはとても長い返答の途中です。"),
            _playback_state_event(
                request_id="tts-000000", state="playing", seq=0, played_frames=8000
            ),
            _barge_in_event(request_id="tts-000000", played_frames=8000),
            _transcript_stream_final_event(),
            {"type": "STOP"},
        ]
    )

    summary = run_dialogue_engine_events(fake_node, _config())
    commands, controls = _playback_outputs(fake_node)
    cancels = _agent_cancels(fake_node)

    assert len(commands) == 1
    assert commands[0].command == "stop"
    assert commands[0].request_id == "tts-000000"
    assert commands[0].stream_id == "speaker/main"
    assert commands[0].seq == 0
    assert len(controls) == 1
    assert controls[0].kind == "flush"
    assert controls[0].stream_id == "speaker/cpal"
    assert controls[0].fade_out_ms == 15
    assert len(cancels) == 1
    assert cancels[0].reason == "barge_in"
    assert summary.cancel_requests == 1


def test_dialogue_engine_ignores_transcript_during_playback_without_barge_in() -> None:
    fake_node = FakeDoraNode(
        [
            _transcript_final_event(text="こんにちは"),
            _agent_text("これは読み上げ中の返答です。"),
            _playback_state_event(
                request_id="tts-000000", state="playing", seq=0, played_frames=12000
            ),
            _transcript_final_event(text="これは読み上げ中の返答です", user_turn_id="echo-turn"),
            _agent_done(),
            _playback_state_event(
                request_id="tts-000000", state="completed", seq=1, played_frames=24000
            ),
            _transcript_stream_final_event(),
            {"type": "STOP"},
        ]
    )

    summary = run_dialogue_engine_events(fake_node, _config())
    turns = _agent_turns(fake_node)

    assert summary.transcript_finals == 2
    assert summary.agent_turn_requests == 1
    assert len(turns) == 1
    assert turns[0].text == "こんにちは"


def test_dialogue_engine_barge_in_after_playback_done_only_cancels() -> None:
    # If playback already completed, there is nothing to stop; barge-in must not
    # emit a stop for a finished request (playback_queue would reject it).
    fake_node = FakeDoraNode(
        [
            _transcript_final_event(),
            _agent_text("短い返答です。"),
            _playback_state_event(
                request_id="tts-000000", state="playing", seq=0, played_frames=4000
            ),
            _playback_state_event(
                request_id="tts-000000", state="completed", seq=1, played_frames=4000
            ),
            _barge_in_event(request_id="tts-000000", played_frames=4000),
            _transcript_stream_final_event(),
            {"type": "STOP"},
        ]
    )

    run_dialogue_engine_events(fake_node, _config())
    commands, controls = _playback_outputs(fake_node)

    assert commands == []
    assert controls == []


def _agent_turns(fake_node):
    turns = []
    for output_id, data, metadata in fake_node.sent:
        if output_id == "agent_turn":
            turns.append(
                decode_agent_turn_request_from_dora(
                    data, validate_dora_agent_turn_request_metadata(metadata)
                )
            )
    return turns


def test_dialogue_engine_barge_in_computes_heard_text_across_chunks() -> None:
    # Two spoken chunks; the second is interrupted partway. heard_text should be
    # the fully-played first chunk plus the heard prefix of the second.
    fake_node = FakeDoraNode(
        [
            _transcript_final_event(),
            _agent_text("最初の文。次の文。"),
            _playback_state_event(
                request_id="tts-000001", state="playing", seq=0, played_frames=13715
            ),
            _barge_in_event(request_id="tts-000001", played_frames=13715),
            _transcript_stream_final_event(),
            {"type": "STOP"},
        ]
    )
    run_dialogue_engine_events(fake_node, _config())
    cancels = _agent_cancels(fake_node)
    assert len(cancels) == 1
    # 13715 frames / 48000 Hz * 7.0 cps ~= 2 chars of the second chunk.
    assert cancels[0].heard_text == "最初の文。次の"


def test_dialogue_engine_barge_in_prepends_heard_note_to_next_turn() -> None:
    fake_node = FakeDoraNode(
        [
            _transcript_final_event(text="こんにちは"),
            _agent_text("どういたしまして。"),
            _playback_state_event(
                request_id="tts-000000", state="playing", seq=0, played_frames=20000
            ),
            _barge_in_event(request_id="tts-000000", played_frames=20000),
            _transcript_final_event(text="ちょっと待って", user_turn_id="user-turn-2"),
            _agent_done(user_turn_id="user-turn-2", agent_turn_id="assistant-turn-000001"),
            _transcript_stream_final_event(),
            {"type": "STOP"},
        ]
    )
    run_dialogue_engine_events(fake_node, _config())
    turns = _agent_turns(fake_node)
    assert len(turns) == 2
    assert turns[0].text == "こんにちは"
    # The interrupted reply's heard prefix is delivered as a note on turn 2.
    assert "ちょっと待って" in turns[1].text
    assert "遮られました" in turns[1].text
    assert turns[1].text != "ちょっと待って"


def test_dialogue_engine_barge_in_before_audio_has_no_heard_note() -> None:
    # Barge-in with zero played frames: nothing heard, so no note and heard_text None.
    fake_node = FakeDoraNode(
        [
            _transcript_final_event(text="こんにちは"),
            _agent_text("どういたしまして。"),
            _playback_state_event(
                request_id="tts-000000", state="playing", seq=0, played_frames=0
            ),
            _barge_in_event(request_id="tts-000000", played_frames=0),
            _transcript_final_event(text="やっぱりいいです", user_turn_id="user-turn-2"),
            _agent_done(user_turn_id="user-turn-2", agent_turn_id="assistant-turn-000001"),
            _transcript_stream_final_event(),
            {"type": "STOP"},
        ]
    )
    run_dialogue_engine_events(fake_node, _config())
    cancels = _agent_cancels(fake_node)
    turns = _agent_turns(fake_node)
    assert cancels[0].heard_text is None
    assert turns[1].text == "やっぱりいいです"
