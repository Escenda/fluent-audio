"""DORA node for the voice dialogue surface.

The dialogue engine is the voice-facing surface around the agent runtime. It
does not own model calls, tool registries, or MCP execution. It validates
transcript and agent events, emits agent turn requests, chunks agent text for
TTS, and publishes session/dialogue observability events.
"""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import re
import sys
import time
from collections.abc import Sequence
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pydantic import BaseModel, ConfigDict, Field

from fluent_dialogue_dora.contracts import (
    AgentApprovalRequest,
    AgentCancelRequest,
    AgentMcpElicitationRequest,
    AgentTextDelta,
    AgentToolEvent,
    AgentTurnDone,
    AgentTurnRequest,
    AgentUserInputRequest,
    BargeInEvent,
    DialogueEvent,
    DialogueInput,
    PlaybackControlFlush,
    PlaybackDone,
    PlaybackState,
    PlaybackStop,
    TranscriptFinal,
    TtsTextChunk,
    TtsTextStreamFinal,
    TurnIds,
    VoiceSessionEvent,
)
from fluent_dialogue_dora.dora import (
    PlaybackCommandEvent,
    decode_agent_runtime_event_from_dora,
    decode_barge_in_event_from_dora,
    decode_dialogue_input_from_dora,
    decode_playback_done_from_dora,
    decode_playback_state_from_dora,
    decode_transcript_final_from_dora,
    encode_agent_cancel_request_for_dora,
    encode_agent_turn_request_for_dora,
    encode_dialogue_event_for_dora,
    encode_playback_command_for_dora,
    encode_playback_control_command_for_dora,
    encode_tts_text_chunk_for_dora,
    encode_tts_text_stream_final_marker_for_dora,
    encode_voice_session_event_for_dora,
    validate_dora_agent_runtime_event_metadata,
    validate_dora_barge_in_metadata,
    validate_dora_dialogue_input_metadata,
    validate_dora_playback_done_metadata,
    validate_dora_playback_state_metadata,
    validate_dora_transcript_metadata,
    validate_dora_transcript_stream_final_marker,
)
from fluent_dialogue_dora_contracts.fluent_dialogue_dora.v1 import dialogue_pb2 as dialogue_pb

DEFAULT_DORA_OUTPUT_DRAIN_SECONDS = 0.2
DEFAULT_ASSISTANT_TURN_PREFIX = "assistant-turn-"
DEFAULT_TTS_REQUEST_PREFIX = "tts-"
DEFAULT_CHUNK_DELIMITERS = ".!?。！？、，,\n"
DEFAULT_PLAYBACK_CONTROL_STREAM_ID = "speaker/cpal"
DEFAULT_PLAYBACK_FADE_OUT_MS = 15
# pyopenjtalk synthesizes at 48 kHz; PlaybackState.played_frames are TTS-rate
# mono frames, so frames / rate gives the seconds the user actually heard.
DEFAULT_TTS_SAMPLE_RATE_HZ = 48000
# Rough Japanese speaking rate for mapping heard seconds to a heard character
# count. Only needs to be good enough that Codex does not assume the un-played
# remainder was heard.
DEFAULT_TTS_CHARS_PER_SECOND = 7.0
HEARD_PREFIX_NOTE_TEMPLATE = (
    "（注: 前の返答は読み上げの途中でユーザーに遮られました。"
    "ユーザーが実際に聞いたのはおおよそ「{heard}」までです。）\n"
)
_FENCED_CODE_PATTERN = re.compile(r"```[\s\S]*?```")
_INLINE_CODE_PATTERN = re.compile(r"`([^`\n]+)`")
_MARKDOWN_LINE_PREFIX_PATTERN = re.compile(r"(?m)^\s{0,3}(?:#{1,6}\s+|[-*+]\s+|\d+[.)]\s+)")
_MARKDOWN_LINE_PREFIX_AT_START_PATTERN = re.compile(
    r"^\s{0,3}(?:#{1,6}\s+|[-*+]\s+|\d+[.)]\s+)"
)
_TTS_UNSAFE_LIST_HINT_PATTERN = re.compile(
    r"(ファイル|コード|Python|Javascript|JavaScript|TypeScript|コマンド|CLI|ツール|作成|編集)"
)
_WHITESPACE_PATTERN = re.compile(r"[ \t]+")
_UNSPOKEN_LEADING_CHARS = " \t\r\n-–—_/\\|"
_SCREEN_DETAIL_TTS_TEXT = "詳細は画面に表示します。"


class DialogueEngineError(ValueError):
    """Raised when dialogue input streams violate the voice surface contract."""


class DialogueEngineConfig(BaseModel):
    """Runtime configuration for one dialogue engine node."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: str = Field(min_length=1)
    transcript_stream_id: str = Field(min_length=1)
    assistant_turn_prefix: str = Field(
        default=DEFAULT_ASSISTANT_TURN_PREFIX,
        min_length=1,
    )
    tts_request_prefix: str = Field(default=DEFAULT_TTS_REQUEST_PREFIX, min_length=1)
    chunk_delimiters: str = Field(default=DEFAULT_CHUNK_DELIMITERS, min_length=1)
    # Device stream id of the speaker sink, target of barge-in flush commands.
    playback_control_stream_id: str = Field(
        default=DEFAULT_PLAYBACK_CONTROL_STREAM_ID, min_length=1
    )
    playback_fade_out_ms: int = Field(default=DEFAULT_PLAYBACK_FADE_OUT_MS, ge=0)
    tts_sample_rate_hz: int = Field(default=DEFAULT_TTS_SAMPLE_RATE_HZ, gt=0)
    tts_chars_per_second: float = Field(default=DEFAULT_TTS_CHARS_PER_SECOND, gt=0.0)
    output_drain_seconds: float = Field(
        default=DEFAULT_DORA_OUTPUT_DRAIN_SECONDS,
        ge=0.0,
    )


class DialogueEngineSummary(BaseModel):
    """Validated counters for one dialogue engine run."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    transcript_finals: int = Field(ge=0)
    agent_turn_requests: int = Field(ge=0)
    agent_text_deltas: int = Field(ge=0)
    agent_turn_done: int = Field(ge=0)
    tts_text_chunks: int = Field(ge=0)
    tts_text_stream_finals: int = Field(ge=0)
    dialogue_events: int = Field(ge=0)
    session_events: int = Field(ge=0)
    cancel_requests: int = Field(ge=0)
    approval_requests: int = Field(ge=0)
    user_input_requests: int = Field(ge=0)
    mcp_elicitation_requests: int = Field(ge=0)
    tool_events: int = Field(ge=0)
    playback_done: int = Field(ge=0)
    transcript_stream_final_seen: bool


class DialogueEngineOutput(BaseModel):
    """Events produced by one dialogue engine state transition."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    agent_turn_requests: tuple[AgentTurnRequest, ...] = ()
    agent_cancel_requests: tuple[AgentCancelRequest, ...] = ()
    session_events: tuple[VoiceSessionEvent, ...] = ()
    dialogue_events: tuple[DialogueEvent, ...] = ()
    tts_text_chunks: tuple[TtsTextChunk, ...] = ()
    tts_text_stream_finals: tuple[TtsTextStreamFinal, ...] = ()
    playback_commands: tuple[PlaybackCommandEvent, ...] = ()
    playback_controls: tuple[PlaybackControlFlush, ...] = ()


class ActiveAgentTurn(BaseModel):
    """Currently active assistant turn tracked by the voice surface."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: str = Field(min_length=1)
    user_turn_id: str = Field(min_length=1)
    assistant_turn_id: str = Field(min_length=1)
    assistant_started: bool = False


class CancelledAgentTurn(BaseModel):
    """Assistant turn whose cancel request has already left this voice surface."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: str = Field(min_length=1)
    user_turn_id: str = Field(min_length=1)
    assistant_turn_id: str = Field(min_length=1)


class TtsRequestRecord(BaseModel):
    """Spoken text emitted for one TTS request, used to reconstruct, on barge-in,
    the prefix the user actually heard."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    assistant_turn_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    text: str = Field(min_length=1)


class LiteralThinkBlockFilter:
    """Removes literal model think blocks before text reaches TTS."""

    _OPEN_TAG = "<think>"
    _CLOSE_TAG = "</think>"

    def __init__(self) -> None:
        self._pending = ""
        self._inside_think_block = False

    def push(self, text: str) -> str:
        if not text:
            raise DialogueEngineError("agent text delta must not be empty")
        self._pending += text
        chunks: list[str] = []
        while self._pending:
            if self._inside_think_block:
                close_index = self._pending.find(self._CLOSE_TAG)
                if close_index == -1:
                    self._pending = self._possible_tag_prefix_suffix(
                        self._pending,
                        self._CLOSE_TAG,
                    )
                    break
                self._pending = self._pending[close_index + len(self._CLOSE_TAG) :]
                self._inside_think_block = False
                continue

            open_index = self._pending.find(self._OPEN_TAG)
            if open_index == -1:
                safe_end = len(self._pending) - len(
                    self._possible_tag_prefix_suffix(self._pending, self._OPEN_TAG),
                )
                if safe_end > 0:
                    chunks.append(self._pending[:safe_end])
                    self._pending = self._pending[safe_end:]
                break

            chunks.append(self._pending[:open_index])
            self._pending = self._pending[open_index + len(self._OPEN_TAG) :]
            self._inside_think_block = True
        return "".join(chunks)

    def finish(self) -> str:
        if self._inside_think_block:
            self._pending = ""
            self._inside_think_block = False
            return ""
        text = self._pending
        self._pending = ""
        return text

    def clear(self) -> None:
        self._pending = ""
        self._inside_think_block = False

    def _possible_tag_prefix_suffix(self, text: str, tag: str) -> str:
        max_length = min(len(text), len(tag) - 1)
        for length in range(max_length, 0, -1):
            suffix = text[-length:]
            if tag.startswith(suffix):
                return suffix
        return ""


class PunctuationChunker:
    """Buffers agent text and releases sentence-ish chunks for TTS."""

    def __init__(self, delimiters: str) -> None:
        if not delimiters:
            raise DialogueEngineError("chunk delimiters must not be empty")
        self._delimiters = frozenset(delimiters)
        self._buffer = ""

    @property
    def has_buffered_text(self) -> bool:
        return bool(self._buffer.strip())

    def push(self, text: str) -> tuple[str, ...]:
        if not text:
            raise DialogueEngineError("agent text delta must not be empty")
        self._buffer += text
        chunks: list[str] = []
        while True:
            split_index = self._first_delimiter_index(self._buffer)
            if split_index is None:
                return tuple(chunks)
            chunk = self._buffer[: split_index + 1].strip()
            self._buffer = self._buffer[split_index + 1 :]
            if _has_tts_speakable_char(chunk):
                chunks.append(chunk)

    def finish(self) -> str | None:
        text = self._buffer.strip()
        self._buffer = ""
        if _has_tts_speakable_char(text):
            return text
        return None

    def clear(self) -> None:
        self._buffer = ""

    def _first_delimiter_index(self, text: str) -> int | None:
        indexes = [index for index, char in enumerate(text) if char in self._delimiters]
        if not indexes:
            return None
        return indexes[0]


def _tts_speech_text(text: str) -> str:
    """Convert agent display text into text that is safe to hand to TTS."""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = _FENCED_CODE_PATTERN.sub("コードの詳細は画面に表示します。", normalized)
    normalized = _INLINE_CODE_PATTERN.sub(r"\1", normalized)
    if _should_speak_screen_detail_summary(normalized):
        return _SCREEN_DETAIL_TTS_TEXT
    normalized = _MARKDOWN_LINE_PREFIX_PATTERN.sub("", normalized)
    for marker in ("```", "**", "__", "~~"):
        normalized = normalized.replace(marker, "")
    lines = []
    for line in normalized.split("\n"):
        clean = line.strip().lstrip(_UNSPOKEN_LEADING_CHARS)
        if clean:
            lines.append(clean)
    spoken = " ".join(lines)
    spoken = _WHITESPACE_PATTERN.sub(" ", spoken)
    return spoken.strip().lstrip(_UNSPOKEN_LEADING_CHARS)


def _should_speak_screen_detail_summary(text: str) -> bool:
    unsafe_list_lines = 0
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if not _MARKDOWN_LINE_PREFIX_AT_START_PATTERN.match(stripped):
            continue
        if _TTS_UNSAFE_LIST_HINT_PATTERN.search(stripped):
            unsafe_list_lines += 1
    return unsafe_list_lines >= 2


def _has_tts_speakable_char(text: str) -> bool:
    return any(char.isalnum() for char in text)


def _required_tts_speech_text(text: str, source: str) -> str:
    spoken = _tts_speech_text(text)
    if not spoken:
        raise DialogueEngineError(f"{source} became empty after TTS speech normalization")
    return spoken


class DialogueEngineRuntime:
    """State machine for the voice dialogue surface."""

    def __init__(self, config: DialogueEngineConfig) -> None:
        self._config = config
        self._tts_text_filter = LiteralThinkBlockFilter()
        self._chunker = PunctuationChunker(config.chunk_delimiters)
        self._active_agent_turn: ActiveAgentTurn | None = None
        self._cancelled_agent_turns: list[CancelledAgentTurn] = []
        self._next_agent_turn_seq = 0
        self._next_agent_cancel_seq = 0
        self._next_session_seq = 0
        self._next_dialogue_seq = 0
        self._next_tts_seq = 0
        # Latest non-terminal playback request, learned from playback_state. Used
        # to gate barge-in stop commands so we never stop an already-finished
        # request (playback_queue would reject that).
        self._active_playback_request_id: str | None = None
        self._barge_in_transcript_allowed = False
        # cpal_sink validates flush seq as strictly increasing for the session.
        self._next_flush_seq = 0
        # Spoken text per TTS request for the current assistant turn, so a
        # barge-in can compute the heard prefix. Cleared when a new turn starts.
        self._tts_requests: dict[str, TtsRequestRecord] = {}
        # Heard prefix awaiting delivery as a note on the next user turn.
        self._pending_heard_prefix: str | None = None

    @property
    def idle(self) -> bool:
        return self._active_agent_turn is None and not self._chunker.has_buffered_text

    def handle_transcript_final(self, transcript: TranscriptFinal) -> DialogueEngineOutput:
        self._validate_transcript(transcript)
        if self._active_playback_request_id is not None and not self._barge_in_transcript_allowed:
            # ponytail: playback echo guard. If this becomes too strict, replace
            # it with an explicit ASR segment provenance flag from the AEC path.
            return DialogueEngineOutput()
        self._barge_in_transcript_allowed = False
        outputs: list[DialogueEngineOutput] = []
        if self._active_agent_turn is not None:
            outputs.append(self._cancel_active_agent("new_user_turn"))

        # A new turn begins; previous-turn TTS records are no longer needed.
        self._tts_requests = {}
        turn_text = self._apply_pending_heard_prefix(transcript.text)

        assistant_turn_id = self._next_assistant_turn_id()
        active = ActiveAgentTurn(
            session_id=transcript.session_id,
            user_turn_id=transcript.user_turn_id,
            assistant_turn_id=assistant_turn_id,
        )
        self._active_agent_turn = active
        agent_turn = AgentTurnRequest(
            session_id=transcript.session_id,
            user_turn_id=transcript.user_turn_id,
            assistant_turn_id=assistant_turn_id,
            seq=self._next_agent_turn_seq,
            text=turn_text,
        )
        self._next_agent_turn_seq += 1
        current = DialogueEngineOutput(
            agent_turn_requests=(agent_turn,),
            session_events=(
                self._session_event(
                    "user_turn_finalized",
                    "thinking",
                    active,
                ),
            ),
        )
        outputs.append(current)
        return _merge_outputs(tuple(outputs))

    def handle_dialogue_input(self, dialogue_input: DialogueInput) -> DialogueEngineOutput:
        if dialogue_input.session_id != self._config.session_id:
            raise DialogueEngineError("dialogue input session mismatch")
        if dialogue_input.input_type == "cancel":
            return self._cancel_active_agent("voice_cancel")
        if dialogue_input.input_type == "playback_done":
            if dialogue_input.request_id is None:
                raise DialogueEngineError("playback_done dialogue input requires request_id")
            return DialogueEngineOutput(
                session_events=(
                    self._session_event_for_turn(
                        "state_changed",
                        "listening",
                        dialogue_input.user_turn_id,
                        None,
                        f"playback_done:{dialogue_input.request_id}",
                    ),
                ),
            )
        raise DialogueEngineError(
            "transcript_final dialogue input is not accepted on dialogue_input"
        )

    def handle_playback_done(self, done: PlaybackDone) -> DialogueEngineOutput:
        if self._active_playback_request_id == done.request_id:
            self._active_playback_request_id = None
        return DialogueEngineOutput(
            session_events=(
                self._session_event_for_turn(
                    "state_changed",
                    "listening",
                    done.user_turn_id,
                    self._active_assistant_turn_id_or_none(),
                    f"playback_done:{done.status}",
                ),
            ),
        )

    def handle_playback_state(self, state: PlaybackState) -> DialogueEngineOutput:
        """Track the active playback request so barge-in can stop it safely."""

        if state.state in ("queued", "playing", "paused"):
            self._active_playback_request_id = state.request_id
            self._barge_in_transcript_allowed = False
        elif self._active_playback_request_id == state.request_id:
            # stopped / completed / cancelled / failed: nothing left to stop.
            self._active_playback_request_id = None
            self._barge_in_transcript_allowed = False
        return DialogueEngineOutput()

    def handle_barge_in(self, event: BargeInEvent) -> DialogueEngineOutput:
        """Stop playback, drop the device buffer, and cancel the active turn."""

        outputs: list[DialogueEngineOutput] = []
        heard_text: str | None = None
        if self._active_playback_request_id == event.playback_request_id:
            heard_text = self._compute_heard_text(
                event.playback_request_id, event.played_frames
            )
            stop = PlaybackStop(
                command="stop",
                request_id=event.playback_request_id,
                stream_id=event.playback_stream_id,
                seq=0,
            )
            flush = PlaybackControlFlush(
                kind="flush",
                stream_id=self._config.playback_control_stream_id,
                seq=self._next_flush_seq,
                fade_out_ms=self._config.playback_fade_out_ms,
            )
            self._next_flush_seq += 1
            self._active_playback_request_id = None
            self._barge_in_transcript_allowed = True
            outputs.append(
                DialogueEngineOutput(
                    playback_commands=(stop,),
                    playback_controls=(flush,),
                )
            )
            # Deliver the heard prefix as a note on the next user turn so Codex's
            # context reflects only what the user actually heard.
            if heard_text is not None:
                self._pending_heard_prefix = heard_text
        # Cancel the agent turn that was being interrupted (no-op if none active).
        outputs.append(self._cancel_active_agent("barge_in", heard_text=heard_text))
        return _merge_outputs(tuple(outputs))

    def handle_agent_text_delta(self, delta: AgentTextDelta) -> DialogueEngineOutput:
        active = self._active_agent_or_stale(
            delta.session_id, delta.user_turn_id, delta.agent_turn_id
        )
        if active is None:
            return DialogueEngineOutput()
        session_events: list[VoiceSessionEvent] = []
        if not active.assistant_started:
            active = active.model_copy(update={"assistant_started": True})
            self._active_agent_turn = active
            session_events.append(
                self._session_event(
                    "assistant_turn_started",
                    "speaking",
                    active,
                )
            )

        dialogue_events = [
            self._dialogue_event(
                "agent_text",
                active,
                text=delta.text,
            )
        ]
        filtered_text = self._tts_text_filter.push(delta.text)
        spoken_text = _tts_speech_text(filtered_text) if filtered_text else ""
        tts_chunks = (
            [
                self._tts_chunk(active, chunk, is_final=False)
                for chunk in self._chunker.push(spoken_text)
            ]
            if spoken_text
            else []
        )
        dialogue_events.extend(
            self._dialogue_event("tts_text", active, text=chunk.text, request_id=chunk.request_id)
            for chunk in tts_chunks
        )
        return DialogueEngineOutput(
            session_events=tuple(session_events),
            dialogue_events=tuple(dialogue_events),
            tts_text_chunks=tuple(tts_chunks),
        )

    def handle_agent_approval_request(
        self,
        approval: AgentApprovalRequest,
    ) -> DialogueEngineOutput:
        self._validate_agent_session(approval.session_id)
        assistant_turn_id = self._active_assistant_turn_id_or_none()
        if assistant_turn_id is None:
            self._log_stale_agent_event(
                "no active agent turn",
                user_turn_id=approval.user_turn_id,
                assistant_turn_id="<unknown>",
            )
            return DialogueEngineOutput()
        active = self._active_agent_or_stale(
            approval.session_id,
            approval.user_turn_id,
            assistant_turn_id,
        )
        if active is None:
            return DialogueEngineOutput()
        tts_text = _required_tts_speech_text(approval.prompt, "approval prompt")
        tts_chunk = self._tts_chunk(active, tts_text, is_final=False)
        return DialogueEngineOutput(
            dialogue_events=(
                self._dialogue_event(
                    "approval_requested",
                    active,
                    request_id=approval.approval_id,
                ),
                self._dialogue_event(
                    "tts_text",
                    active,
                    text=tts_chunk.text,
                    request_id=tts_chunk.request_id,
                ),
            ),
            tts_text_chunks=(tts_chunk,),
        )

    def handle_agent_user_input_request(
        self,
        request: AgentUserInputRequest,
    ) -> DialogueEngineOutput:
        self._validate_agent_session(request.session_id)
        assistant_turn_id = self._active_assistant_turn_id_or_none()
        if assistant_turn_id is None:
            self._log_stale_agent_event(
                "no active agent turn",
                user_turn_id=request.user_turn_id,
                assistant_turn_id="<unknown>",
            )
            return DialogueEngineOutput()
        active = self._active_agent_or_stale(
            request.session_id,
            request.user_turn_id,
            assistant_turn_id,
        )
        if active is None:
            return DialogueEngineOutput()
        tts_text = _required_tts_speech_text(
            _spoken_user_input_request(request),
            "user input prompt",
        )
        tts_chunk = self._tts_chunk(active, tts_text, is_final=False)
        return DialogueEngineOutput(
            dialogue_events=(
                self._dialogue_event(
                    "user_input_requested",
                    active,
                    request_id=request.request_id,
                ),
                self._dialogue_event(
                    "tts_text",
                    active,
                    text=tts_chunk.text,
                    request_id=tts_chunk.request_id,
                ),
            ),
            tts_text_chunks=(tts_chunk,),
        )

    def handle_agent_mcp_elicitation_request(
        self,
        request: AgentMcpElicitationRequest,
    ) -> DialogueEngineOutput:
        self._validate_agent_session(request.session_id)
        assistant_turn_id = self._active_assistant_turn_id_or_none()
        if assistant_turn_id is None:
            self._log_stale_agent_event(
                "no active agent turn",
                user_turn_id=request.user_turn_id,
                assistant_turn_id="<unknown>",
            )
            return DialogueEngineOutput()
        active = self._active_agent_or_stale(
            request.session_id,
            request.user_turn_id,
            assistant_turn_id,
        )
        if active is None:
            return DialogueEngineOutput()
        tts_text = _required_tts_speech_text(request.message, "MCP elicitation prompt")
        tts_chunk = self._tts_chunk(active, tts_text, is_final=False)
        return DialogueEngineOutput(
            dialogue_events=(
                self._dialogue_event(
                    "mcp_elicitation_requested",
                    active,
                    request_id=request.request_id,
                ),
                self._dialogue_event(
                    "tts_text",
                    active,
                    text=tts_chunk.text,
                    request_id=tts_chunk.request_id,
                ),
            ),
            tts_text_chunks=(tts_chunk,),
        )

    def handle_agent_tool_event(self, tool: AgentToolEvent) -> DialogueEngineOutput:
        self._validate_agent_session(tool.session_id)
        assistant_turn_id = self._active_assistant_turn_id_or_none()
        if assistant_turn_id is None:
            self._log_stale_agent_event(
                "no active agent turn",
                user_turn_id=tool.user_turn_id,
                assistant_turn_id="<unknown>",
            )
            return DialogueEngineOutput()
        active = self._active_agent_or_stale(
            tool.session_id,
            tool.user_turn_id,
            assistant_turn_id,
        )
        if active is None:
            return DialogueEngineOutput()
        return DialogueEngineOutput(
            dialogue_events=(
                self._dialogue_event(
                    "tool_event",
                    active,
                    request_id=tool.tool_call_id,
                ),
            ),
        )

    def handle_agent_turn_done(self, done: AgentTurnDone) -> DialogueEngineOutput:
        if self._is_cancelled_turn_done(done):
            return DialogueEngineOutput()
        active = self._active_agent_or_stale(
            done.session_id,
            done.user_turn_id,
            done.agent_turn_id,
        )
        if active is None:
            return DialogueEngineOutput()
        self._active_agent_turn = None
        if done.status == "failed":
            self._tts_text_filter.clear()
            self._chunker.clear()
            message = done.message
            if message is None:
                raise DialogueEngineError("failed agent turn requires message")
            return DialogueEngineOutput(
                session_events=(self._session_event("error", "error", active, message),),
                dialogue_events=(self._dialogue_event("error", active, message=message),),
            )
        if done.status == "cancelled":
            self._tts_text_filter.clear()
            self._chunker.clear()
            return DialogueEngineOutput(
                session_events=(
                    self._session_event("state_changed", "interrupted", active, done.message),
                ),
                dialogue_events=(self._dialogue_event("cancelled", active),),
            )

        filtered_tail = self._tts_text_filter.finish()
        spoken_tail = _tts_speech_text(filtered_tail) if filtered_tail else ""
        tail_chunks = (
            [
                self._tts_chunk(active, chunk, is_final=False)
                for chunk in self._chunker.push(spoken_tail)
            ]
            if spoken_tail
            else []
        )
        final_text = self._chunker.finish()
        tts_chunks: tuple[TtsTextChunk, ...]
        dialogue_events: tuple[DialogueEvent, ...]
        final_chunks: list[TtsTextChunk] = tail_chunks
        if final_text is not None:
            final_chunks.append(self._tts_chunk(active, final_text, is_final=True))
        tts_chunks = tuple(final_chunks)
        dialogue_events = tuple(
            self._dialogue_event(
                "tts_text",
                active,
                text=chunk.text,
                request_id=chunk.request_id,
            )
            for chunk in tts_chunks
        )
        stream_final = self._tts_text_stream_final(active)
        return DialogueEngineOutput(
            session_events=(self._session_event("assistant_turn_completed", "listening", active),),
            dialogue_events=dialogue_events,
            tts_text_chunks=tts_chunks,
            tts_text_stream_finals=(stream_final,),
        )

    def _validate_transcript(self, transcript: TranscriptFinal) -> None:
        if transcript.session_id != self._config.session_id:
            raise DialogueEngineError("transcript session mismatch")
        if transcript.stream_id != self._config.transcript_stream_id:
            raise DialogueEngineError("transcript stream mismatch")

    def _cancel_active_agent(
        self, reason: str, *, heard_text: str | None = None
    ) -> DialogueEngineOutput:
        active = self._active_agent_turn
        if active is None:
            return DialogueEngineOutput()
        self._tts_text_filter.clear()
        self._chunker.clear()
        self._active_agent_turn = None
        self._cancelled_agent_turns.append(
            CancelledAgentTurn(
                session_id=active.session_id,
                user_turn_id=active.user_turn_id,
                assistant_turn_id=active.assistant_turn_id,
            )
        )
        cancel = AgentCancelRequest(
            session_id=active.session_id,
            user_turn_id=active.user_turn_id,
            seq=self._next_agent_cancel_seq,
            reason=reason,
            heard_text=heard_text,
        )
        self._next_agent_cancel_seq += 1
        return DialogueEngineOutput(
            agent_cancel_requests=(cancel,),
            session_events=(self._session_event("state_changed", "interrupted", active, reason),),
            dialogue_events=(self._dialogue_event("cancelled", active),),
        )

    def _active_agent_or_stale(
        self,
        session_id: str,
        user_turn_id: str,
        assistant_turn_id: str,
    ) -> ActiveAgentTurn | None:
        self._validate_agent_session(session_id)
        active = self._active_agent_turn
        if active is None:
            self._log_stale_agent_event(
                "no active agent turn",
                user_turn_id=user_turn_id,
                assistant_turn_id=assistant_turn_id,
            )
            return None
        if active.user_turn_id != user_turn_id or active.assistant_turn_id != assistant_turn_id:
            self._log_stale_agent_event(
                "active agent turn changed",
                user_turn_id=user_turn_id,
                assistant_turn_id=assistant_turn_id,
            )
            return None
        return active

    def _validate_agent_session(self, session_id: str) -> None:
        if session_id != self._config.session_id:
            raise DialogueEngineError("agent event session mismatch")

    def _log_stale_agent_event(
        self,
        reason: str,
        *,
        user_turn_id: str,
        assistant_turn_id: str,
    ) -> None:
        sys.stderr.write(
            "dialogue_engine: dropping stale agent event "
            f"reason={reason} user_turn_id={user_turn_id} "
            f"assistant_turn_id={assistant_turn_id}\n"
        )
        sys.stderr.flush()

    def _is_cancelled_turn_done(self, done: AgentTurnDone) -> bool:
        for index, turn in enumerate(self._cancelled_agent_turns):
            if (
                turn.session_id == done.session_id
                and turn.user_turn_id == done.user_turn_id
                and turn.assistant_turn_id == done.agent_turn_id
            ):
                if done.status != "cancelled":
                    raise DialogueEngineError("cancelled agent turn returned non-cancelled status")
                del self._cancelled_agent_turns[index]
                return True
        return False

    def _next_assistant_turn_id(self) -> str:
        return f"{self._config.assistant_turn_prefix}{self._next_agent_turn_seq:06d}"

    def _tts_chunk(self, active: ActiveAgentTurn, text: str, *, is_final: bool) -> TtsTextChunk:
        request_id = f"{self._config.tts_request_prefix}{self._next_tts_seq:06d}"
        chunk = TtsTextChunk(
            request_id=request_id,
            session_id=active.session_id,
            user_turn_id=active.user_turn_id,
            assistant_turn_id=active.assistant_turn_id,
            seq=self._next_tts_seq,
            text=text,
            is_final=is_final,
        )
        self._tts_requests[request_id] = TtsRequestRecord(
            assistant_turn_id=active.assistant_turn_id,
            seq=self._next_tts_seq,
            text=text,
        )
        self._next_tts_seq += 1
        return chunk

    def _compute_heard_text(self, request_id: str, played_frames: int) -> str | None:
        """Reconstruct what the user heard: fully-played earlier chunks of the
        same turn plus the heard prefix of the interrupted chunk (time-estimated)."""

        record = self._tts_requests.get(request_id)
        if record is None:
            return None
        earlier = sorted(
            (
                other
                for other in self._tts_requests.values()
                if other.assistant_turn_id == record.assistant_turn_id
                and other.seq < record.seq
            ),
            key=lambda other: other.seq,
        )
        heard = "".join(other.text for other in earlier)
        heard_seconds = played_frames / self._config.tts_sample_rate_hz
        heard_chars = round(heard_seconds * self._config.tts_chars_per_second)
        heard_chars = max(0, min(heard_chars, len(record.text)))
        heard += record.text[:heard_chars]
        heard = heard.strip()
        return heard or None

    def _apply_pending_heard_prefix(self, text: str) -> str:
        """Prepend a barge-in note (if any) so the next turn's context tells the
        agent how much of its interrupted reply the user actually heard."""

        heard = self._pending_heard_prefix
        self._pending_heard_prefix = None
        if heard is None:
            return text
        return HEARD_PREFIX_NOTE_TEMPLATE.format(heard=heard) + text

    def _tts_text_stream_final(self, active: ActiveAgentTurn) -> TtsTextStreamFinal:
        marker = TtsTextStreamFinal(
            session_id=active.session_id,
            user_turn_id=active.user_turn_id,
            assistant_turn_id=active.assistant_turn_id,
            seq=self._next_tts_seq,
        )
        self._next_tts_seq += 1
        return marker

    def _session_event(
        self,
        event: str,
        state: str,
        active: ActiveAgentTurn,
        message: str | None = None,
    ) -> VoiceSessionEvent:
        session_event = VoiceSessionEvent(
            event=event,
            state=state,
            seq=self._next_session_seq,
            turn_ids=TurnIds(
                session_id=active.session_id,
                user_turn_id=active.user_turn_id,
                assistant_turn_id=active.assistant_turn_id,
            ),
            message=message,
        )
        self._next_session_seq += 1
        return session_event

    def _session_event_for_turn(
        self,
        event: str,
        state: str,
        user_turn_id: str,
        assistant_turn_id: str | None,
        message: str,
    ) -> VoiceSessionEvent:
        session_event = VoiceSessionEvent(
            event=event,
            state=state,
            seq=self._next_session_seq,
            turn_ids=TurnIds(
                session_id=self._config.session_id,
                user_turn_id=user_turn_id,
                assistant_turn_id=assistant_turn_id,
            ),
            message=message,
        )
        self._next_session_seq += 1
        return session_event

    def _dialogue_event(
        self,
        event: str,
        active: ActiveAgentTurn,
        *,
        text: str | None = None,
        request_id: str | None = None,
        message: str | None = None,
    ) -> DialogueEvent:
        dialogue_event = DialogueEvent(
            event=event,
            session_id=active.session_id,
            user_turn_id=active.user_turn_id,
            seq=self._next_dialogue_seq,
            text=text,
            request_id=request_id,
            message=message,
        )
        self._next_dialogue_seq += 1
        return dialogue_event

    def _active_assistant_turn_id_or_none(self) -> str | None:
        if self._active_agent_turn is None:
            return None
        return self._active_agent_turn.assistant_turn_id


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the fluent-dialogue-dora dialogue engine.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--transcript-stream-id", required=True)
    parser.add_argument("--assistant-turn-prefix", default=DEFAULT_ASSISTANT_TURN_PREFIX)
    parser.add_argument("--tts-request-prefix", default=DEFAULT_TTS_REQUEST_PREFIX)
    parser.add_argument("--chunk-delimiters", default=DEFAULT_CHUNK_DELIMITERS)
    parser.add_argument(
        "--playback-control-stream-id",
        default=DEFAULT_PLAYBACK_CONTROL_STREAM_ID,
    )
    parser.add_argument(
        "--playback-fade-out-ms",
        type=int,
        default=DEFAULT_PLAYBACK_FADE_OUT_MS,
    )
    parser.add_argument(
        "--tts-sample-rate-hz",
        type=int,
        default=DEFAULT_TTS_SAMPLE_RATE_HZ,
    )
    parser.add_argument(
        "--tts-chars-per-second",
        type=float,
        default=DEFAULT_TTS_CHARS_PER_SECOND,
    )
    parser.add_argument(
        "--output-drain-seconds",
        type=float,
        default=DEFAULT_DORA_OUTPUT_DRAIN_SECONDS,
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("dialogue_engine requires --dora")

    from dora import Node

    config = DialogueEngineConfig(
        session_id=args.session_id,
        transcript_stream_id=args.transcript_stream_id,
        assistant_turn_prefix=args.assistant_turn_prefix,
        tts_request_prefix=args.tts_request_prefix,
        chunk_delimiters=args.chunk_delimiters,
        playback_control_stream_id=args.playback_control_stream_id,
        playback_fade_out_ms=args.playback_fade_out_ms,
        tts_sample_rate_hz=args.tts_sample_rate_hz,
        tts_chars_per_second=args.tts_chars_per_second,
        output_drain_seconds=args.output_drain_seconds,
    )
    summary = run_dialogue_engine_events(Node(), config)
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def run_dialogue_engine_events(
    node,
    config: DialogueEngineConfig,
) -> DialogueEngineSummary:
    runtime = DialogueEngineRuntime(config)
    transcript_finals = 0
    agent_turn_requests = 0
    agent_text_deltas = 0
    agent_turn_done = 0
    tts_text_chunks = 0
    tts_text_stream_finals = 0
    dialogue_events = 0
    session_events = 0
    cancel_requests = 0
    approval_requests = 0
    user_input_requests = 0
    mcp_elicitation_requests = 0
    tool_events = 0
    playback_done = 0
    transcript_stream_final_seen = False
    transcript_input_closed = False

    for event in node:
        if event is None:
            raise DialogueEngineError("DORA event stream ended before STOP")
        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            if not transcript_stream_final_seen:
                raise DialogueEngineError("DORA STOP arrived before transcript stream final marker")
            if not runtime.idle:
                raise DialogueEngineError("DORA STOP arrived while an agent turn is active")
            _drain_dora_output_send(config.output_drain_seconds)
            return DialogueEngineSummary(
                transcript_finals=transcript_finals,
                agent_turn_requests=agent_turn_requests,
                agent_text_deltas=agent_text_deltas,
                agent_turn_done=agent_turn_done,
                tts_text_chunks=tts_text_chunks,
                tts_text_stream_finals=tts_text_stream_finals,
                dialogue_events=dialogue_events,
                session_events=session_events,
                cancel_requests=cancel_requests,
                approval_requests=approval_requests,
                user_input_requests=user_input_requests,
                mcp_elicitation_requests=mcp_elicitation_requests,
                tool_events=tool_events,
                playback_done=playback_done,
                transcript_stream_final_seen=transcript_stream_final_seen,
            )
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id == "transcript":
                transcript_input_closed = True
                if _should_finish_after_input_closed(
                    transcript_stream_final_seen=transcript_stream_final_seen,
                    transcript_input_closed=transcript_input_closed,
                    runtime=runtime,
                    tts_text_chunks=tts_text_chunks,
                    playback_done=playback_done,
                ):
                    _drain_dora_output_send(config.output_drain_seconds)
                    return DialogueEngineSummary(
                        transcript_finals=transcript_finals,
                        agent_turn_requests=agent_turn_requests,
                        agent_text_deltas=agent_text_deltas,
                        agent_turn_done=agent_turn_done,
                        tts_text_chunks=tts_text_chunks,
                        tts_text_stream_finals=tts_text_stream_finals,
                        dialogue_events=dialogue_events,
                        session_events=session_events,
                        cancel_requests=cancel_requests,
                        approval_requests=approval_requests,
                        user_input_requests=user_input_requests,
                        mcp_elicitation_requests=mcp_elicitation_requests,
                        tool_events=tool_events,
                        playback_done=playback_done,
                        transcript_stream_final_seen=transcript_stream_final_seen,
                    )
            elif input_id not in (
                "dialogue_input",
                "agent_event",
                "playback_done",
                "playback_state",
                "barge_in",
            ):
                raise DialogueEngineError(f"Unexpected DORA input id: {input_id!r}")
            continue
        if event_type != "INPUT":
            continue

        input_id = _required_event_text(event, "id")
        outputs = _handle_input_event(runtime, input_id, event, config)
        _send_outputs(node, outputs)

        agent_turn_requests += len(outputs.agent_turn_requests)
        cancel_requests += len(outputs.agent_cancel_requests)
        session_events += len(outputs.session_events)
        dialogue_events += len(outputs.dialogue_events)
        tts_text_chunks += len(outputs.tts_text_chunks)
        tts_text_stream_finals += len(outputs.tts_text_stream_finals)
        if input_id == "transcript":
            metadata = validate_dora_transcript_metadata(event.get("metadata"))
            if metadata.kind == "stream_final":
                transcript_stream_final_seen = True
            elif metadata.kind == "final":
                transcript_finals += 1
        elif input_id == "agent_event":
            agent_event_metadata = validate_dora_agent_runtime_event_metadata(event.get("metadata"))
            if agent_event_metadata.message_type == dialogue_pb.AgentTextDelta.DESCRIPTOR.full_name:
                agent_text_deltas += 1
            elif (
                agent_event_metadata.message_type == dialogue_pb.AgentTurnDone.DESCRIPTOR.full_name
            ):
                agent_turn_done += 1
            elif (
                agent_event_metadata.message_type
                == dialogue_pb.AgentApprovalRequest.DESCRIPTOR.full_name
            ):
                approval_requests += 1
            elif (
                agent_event_metadata.message_type
                == dialogue_pb.AgentUserInputRequest.DESCRIPTOR.full_name
            ):
                user_input_requests += 1
            elif (
                agent_event_metadata.message_type
                == dialogue_pb.AgentMcpElicitationRequest.DESCRIPTOR.full_name
            ):
                mcp_elicitation_requests += 1
            elif (
                agent_event_metadata.message_type == dialogue_pb.AgentToolEvent.DESCRIPTOR.full_name
            ):
                tool_events += 1
        elif input_id == "playback_done":
            playback_done += 1

        if _should_finish_after_input_closed(
            transcript_stream_final_seen=transcript_stream_final_seen,
            transcript_input_closed=transcript_input_closed,
            runtime=runtime,
            tts_text_chunks=tts_text_chunks,
            playback_done=playback_done,
        ):
            _drain_dora_output_send(config.output_drain_seconds)
            return DialogueEngineSummary(
                transcript_finals=transcript_finals,
                agent_turn_requests=agent_turn_requests,
                agent_text_deltas=agent_text_deltas,
                agent_turn_done=agent_turn_done,
                tts_text_chunks=tts_text_chunks,
                tts_text_stream_finals=tts_text_stream_finals,
                dialogue_events=dialogue_events,
                session_events=session_events,
                cancel_requests=cancel_requests,
                approval_requests=approval_requests,
                user_input_requests=user_input_requests,
                mcp_elicitation_requests=mcp_elicitation_requests,
                tool_events=tool_events,
                playback_done=playback_done,
                transcript_stream_final_seen=transcript_stream_final_seen,
            )

    raise DialogueEngineError("DORA event stream ended before STOP")


def _should_finish_after_input_closed(
    *,
    transcript_stream_final_seen: bool,
    transcript_input_closed: bool,
    runtime: DialogueEngineRuntime,
    tts_text_chunks: int,
    playback_done: int,
) -> bool:
    return (
        transcript_stream_final_seen
        and transcript_input_closed
        and runtime.idle
        and playback_done >= tts_text_chunks
    )


def _handle_input_event(
    runtime: DialogueEngineRuntime,
    input_id: str,
    event,
    config: DialogueEngineConfig,
) -> DialogueEngineOutput:
    payload = event.get("value")
    metadata = event.get("metadata")
    if input_id == "transcript":
        transcript_metadata = validate_dora_transcript_metadata(metadata)
        if transcript_metadata.kind == "stream_final":
            stream_final = validate_dora_transcript_stream_final_marker(
                payload,
                transcript_metadata,
            )
            if stream_final.session_id != config.session_id:
                raise DialogueEngineError("transcript stream final session mismatch")
            if stream_final.stream_id != config.transcript_stream_id:
                raise DialogueEngineError("transcript stream final stream mismatch")
            return DialogueEngineOutput()
        if transcript_metadata.kind == "final":
            transcript = decode_transcript_final_from_dora(payload, transcript_metadata)
            return runtime.handle_transcript_final(transcript)
        return DialogueEngineOutput()
    if input_id == "dialogue_input":
        dialogue_metadata = validate_dora_dialogue_input_metadata(metadata)
        return runtime.handle_dialogue_input(
            decode_dialogue_input_from_dora(payload, dialogue_metadata)
        )
    if input_id == "agent_event":
        agent_event = decode_agent_runtime_event_from_dora(payload, metadata)
        if isinstance(agent_event, AgentTextDelta):
            return runtime.handle_agent_text_delta(agent_event)
        if isinstance(agent_event, AgentTurnDone):
            return runtime.handle_agent_turn_done(agent_event)
        if isinstance(agent_event, AgentApprovalRequest):
            return runtime.handle_agent_approval_request(agent_event)
        if isinstance(agent_event, AgentUserInputRequest):
            return runtime.handle_agent_user_input_request(agent_event)
        if isinstance(agent_event, AgentMcpElicitationRequest):
            return runtime.handle_agent_mcp_elicitation_request(agent_event)
        if isinstance(agent_event, AgentToolEvent):
            return runtime.handle_agent_tool_event(agent_event)
    if input_id == "playback_done":
        playback_metadata = validate_dora_playback_done_metadata(metadata)
        return runtime.handle_playback_done(
            decode_playback_done_from_dora(payload, playback_metadata)
        )
    if input_id == "playback_state":
        state_metadata = validate_dora_playback_state_metadata(metadata)
        return runtime.handle_playback_state(
            decode_playback_state_from_dora(payload, state_metadata)
        )
    if input_id == "barge_in":
        barge_in_metadata = validate_dora_barge_in_metadata(metadata)
        return runtime.handle_barge_in(
            decode_barge_in_event_from_dora(payload, barge_in_metadata)
        )
    raise DialogueEngineError(f"Unexpected DORA input id: {input_id!r}")


def _send_outputs(node, outputs: DialogueEngineOutput) -> None:
    for event in outputs.agent_turn_requests:
        payload, metadata = encode_agent_turn_request_for_dora(event)
        node.send_output("agent_turn", payload, metadata=metadata.to_dora_metadata())
    for event in outputs.agent_cancel_requests:
        payload, metadata = encode_agent_cancel_request_for_dora(event)
        node.send_output("agent_cancel", payload, metadata=metadata.to_dora_metadata())
    for event in outputs.session_events:
        payload, metadata = encode_voice_session_event_for_dora(event)
        node.send_output("session", payload, metadata=metadata.to_dora_metadata())
    for event in outputs.dialogue_events:
        payload, metadata = encode_dialogue_event_for_dora(event)
        node.send_output("dialogue", payload, metadata=metadata.to_dora_metadata())
    for event in outputs.tts_text_chunks:
        payload, metadata = encode_tts_text_chunk_for_dora(event)
        node.send_output("tts_text", payload, metadata=metadata.to_dora_metadata())
    for event in outputs.tts_text_stream_finals:
        payload, metadata = encode_tts_text_stream_final_marker_for_dora(event)
        node.send_output("tts_text", payload, metadata=metadata.to_dora_metadata())
    for command in outputs.playback_commands:
        payload, metadata = encode_playback_command_for_dora(command)
        node.send_output("playback_command", payload, metadata=metadata.to_dora_metadata())
    for control in outputs.playback_controls:
        payload, metadata = encode_playback_control_command_for_dora(control)
        node.send_output("playback_control", payload, metadata=metadata.to_dora_metadata())


def _spoken_user_input_request(request: AgentUserInputRequest) -> str:
    questions = tuple(question.question for question in request.questions)
    return " ".join(questions)


def _merge_outputs(outputs: tuple[DialogueEngineOutput, ...]) -> DialogueEngineOutput:
    agent_turn_requests: list[AgentTurnRequest] = []
    agent_cancel_requests: list[AgentCancelRequest] = []
    session_events: list[VoiceSessionEvent] = []
    dialogue_events: list[DialogueEvent] = []
    tts_text_chunks: list[TtsTextChunk] = []
    tts_text_stream_finals: list[TtsTextStreamFinal] = []
    playback_commands: list[PlaybackCommandEvent] = []
    playback_controls: list[PlaybackControlFlush] = []
    for output in outputs:
        agent_turn_requests.extend(output.agent_turn_requests)
        agent_cancel_requests.extend(output.agent_cancel_requests)
        session_events.extend(output.session_events)
        dialogue_events.extend(output.dialogue_events)
        tts_text_chunks.extend(output.tts_text_chunks)
        tts_text_stream_finals.extend(output.tts_text_stream_finals)
        playback_commands.extend(output.playback_commands)
        playback_controls.extend(output.playback_controls)
    return DialogueEngineOutput(
        agent_turn_requests=tuple(agent_turn_requests),
        agent_cancel_requests=tuple(agent_cancel_requests),
        session_events=tuple(session_events),
        dialogue_events=tuple(dialogue_events),
        tts_text_chunks=tuple(tts_text_chunks),
        tts_text_stream_finals=tuple(tts_text_stream_finals),
        playback_commands=tuple(playback_commands),
        playback_controls=tuple(playback_controls),
    )


def _drain_dora_output_send(output_drain_seconds: float) -> None:
    time.sleep(output_drain_seconds)


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise DialogueEngineError(f"DORA event field {key!r} must be a string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
