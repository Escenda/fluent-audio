"""Web harness to stream recordings into an ASR session and observe partial/final text.

Endpoints:
- GET /            - Control page.
- GET /events      - Server-Sent Events stream.
- POST /run        - Start processing manifest asynchronously.
- POST /stop       - Request stop.
- GET /status      - JSON status snapshot.
"""

from __future__ import annotations

import argparse
import json
import queue
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import ClassVar, Protocol, Sequence
from urllib.parse import urlparse

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fluent_dialogue_dora.contracts import TurnEvent, VoiceActivityEvent
from tools.asr_eval.eval_nemotron import ASR_SAMPLE_RATE_HZ, load_manifest, load_wav_as_16k_f32

DEFAULT_TURN_END_SILENCE_FRAMES = 22_400
DEFAULT_TURN_MIN_SILENCE_FRAMES = 7_200
TURN_PREROLL_FRAMES = 3_200
MAX_HISTORY_EVENTS = 2_000
DEFAULT_SMART_TURN_MODEL_PATH = (
    _REPO_ROOT / "artifacts/asr_eval/smart_turn/smart-turn-v3.2-cpu.onnx"
)


class StreamingAsrSession(Protocol):
    def start(self) -> None:
        ...

    def push_audio(self, samples: Sequence[float], *, sample_index: int, chunk_index: int) -> tuple:
        ...

    def stop(self, *, sample_count: int):
        ...

    def cancel(self, *, reason: str) -> None:
        ...


try:
    from tools.asr_eval.nemotron_streaming_adapter import (
        StreamingAsrSessionFactory,
        add_nemotron_session_arguments,
        nemotron_session_factory_from_args,
    )
except Exception:  # pragma: no cover - exercised only when adapter is unavailable.
    class StreamingAsrSessionFactory(Protocol):
        def create(self, utterance_id: str) -> StreamingAsrSession:
            ...

    add_nemotron_session_arguments = None
    nemotron_session_factory_from_args = None


PayloadValue = str | int | float | bool | None
JsonValue = PayloadValue | list["JsonValue"] | dict[str, "JsonValue"]
EventPayload = dict[str, PayloadValue]
Event = tuple[str, EventPayload]
HistoryEvent = dict[str, PayloadValue]


_REQUIRED_MANIFEST_FIELDS: tuple[str, ...] = ("id", "group", "text", "wav")


@dataclass(frozen=True)
class ManifestEntry:
    id: str
    group: str
    text: str
    wav: Path


@dataclass(frozen=True)
class ProbeCase:
    id: str
    label: str
    manifest_path: Path
    target_lang: str
    limit: int | None = None
    turn_detection: bool = False
    end_silence_frames: int = DEFAULT_TURN_END_SILENCE_FRAMES
    smart_turn_model_path: Path | None = None

    def summary(self) -> EventPayload:
        return {
            "id": self.id,
            "label": self.label,
            "manifest": str(self.manifest_path),
            "target_lang": self.target_lang,
            "limit": self.limit if self.limit is not None else -1,
            "turn_detection": self.turn_detection,
            "end_silence_frames": self.end_silence_frames,
            "smart_turn_model": str(self.smart_turn_model_path) if self.smart_turn_model_path else "",
        }


class PartialStabilizer:
    """Splits replacement partials into a stable prefix and an unstable tail.

    agreement_window is how many consecutive partials (including the current
    one) must share a prefix before it is shown as stable; 2 keeps the previous
    longest-common-prefix-with-previous behavior. hold_chars keeps the newest
    characters of the agreed prefix in the unstable tail because they are the
    most likely to be rewritten by the next partial.
    """

    def __init__(self, *, agreement_window: int = 2, hold_chars: int = 0) -> None:
        if agreement_window < 2:
            raise ValueError("agreement_window must be >= 2")
        if hold_chars < 0:
            raise ValueError("hold_chars must be >= 0")
        self._agreement_window = agreement_window
        self._hold_chars = hold_chars
        self._recent: deque[str] = deque(maxlen=agreement_window)
        self._previous_text = ""
        self._previous_stable = ""
        self.revision_count = 0
        self.stable_retreat_count = 0

    def update(self, text: str) -> tuple[str, str]:
        if self._recent and not text.startswith(self._previous_text):
            self.revision_count += 1
        self._recent.append(text)
        self._previous_text = text
        if len(self._recent) < self._agreement_window:
            stable = ""
        else:
            stable = self._recent[0]
            for candidate in tuple(self._recent)[1:]:
                stable = _longest_common_prefix(stable, candidate)
        if self._hold_chars:
            stable = stable[: max(0, len(stable) - self._hold_chars)]
        if not stable.startswith(self._previous_stable):
            self.stable_retreat_count += 1
        self._previous_stable = stable
        return stable, text[len(stable) :]


class UtterancePartialTracker:
    """Stabilizes partial text and aggregates per-utterance streaming metrics."""

    def __init__(self, *, agreement_window: int = 2, hold_chars: int = 0) -> None:
        self._stabilizer = PartialStabilizer(
            agreement_window=agreement_window,
            hold_chars=hold_chars,
        )
        self._push_count = 0
        self._total_push_wall_s = 0.0
        self._max_push_wall_s = 0.0
        self._partial_count = 0
        self._first_partial_elapsed_audio_s: float | None = None
        self._last_partial_text = ""

    def observe_push(self, push_wall_s: float) -> None:
        self._push_count += 1
        self._total_push_wall_s += push_wall_s
        self._max_push_wall_s = max(self._max_push_wall_s, push_wall_s)

    def update_partial(self, text: str, *, elapsed_audio_s: float) -> tuple[str, str]:
        self._partial_count += 1
        if self._first_partial_elapsed_audio_s is None:
            self._first_partial_elapsed_audio_s = elapsed_audio_s
        self._last_partial_text = text
        return self._stabilizer.update(text)

    def summary(
        self,
        *,
        final_text: str,
        stop_wall_s: float,
        audio_duration_s: float,
    ) -> EventPayload:
        mean_push_wall_s = (
            self._total_push_wall_s / self._push_count if self._push_count else 0.0
        )
        return {
            "partial_count": self._partial_count,
            "revision_count": self._stabilizer.revision_count,
            "revision_ratio": (
                self._stabilizer.revision_count / self._partial_count
                if self._partial_count
                else 0.0
            ),
            "stable_retreat_count": self._stabilizer.stable_retreat_count,
            "first_partial_elapsed_audio_s": (
                self._first_partial_elapsed_audio_s
                if self._first_partial_elapsed_audio_s is not None
                else -1.0
            ),
            "mean_push_wall_ms": mean_push_wall_s * 1000.0,
            "max_push_wall_ms": self._max_push_wall_s * 1000.0,
            "push_rtf": (
                self._total_push_wall_s / audio_duration_s if audio_duration_s > 0 else -1.0
            ),
            "stop_wall_ms": stop_wall_s * 1000.0,
            "audio_duration_s": audio_duration_s,
            "final_chars": len(final_text),
            "final_matches_last_partial": final_text.strip() == self._last_partial_text.strip(),
        }


class StreamingTurnDetector:
    def __init__(
        self,
        *,
        entry_id: str,
        end_silence_frames: int,
        vad_threshold: float = 0.5,
        smart_turn_model_path: Path | None = None,
    ) -> None:
        from nodes.vad.silero.silero import SileroVadConfig, SileroVadSession
        from nodes.vad.turn_detector.logic import TurnDetectorConfig, TurnDetectorState

        self._vad = SileroVadSession(SileroVadConfig(threshold=vad_threshold))
        self._turn = None if smart_turn_model_path is not None else TurnDetectorState(
            TurnDetectorConfig(
                session_id="asr-eval",
                output_stream_id="turn/main",
                end_silence_frames=end_silence_frames,
                user_turn_id_prefix=f"{entry_id}-turn",
            )
        )
        self._smart_turn = (
            SmartTurnEndpointDetector(smart_turn_model_path)
            if smart_turn_model_path is not None
            else None
        )
        self._entry_id = entry_id
        self._end_silence_frames = end_silence_frames
        self._activity_seq = 0
        self._next_output_seq = 0
        self._next_turn_number = 1
        self._active_turn_id: str | None = None
        self._last_speech_end_sample_index: int | None = None
        self._turn_start_sample_index = 0
        self._silence_frames = 0
        self._samples = None

    def push(self, samples: Sequence[float]) -> list[TurnEvent]:
        import numpy as np

        waveform = np.asarray(samples, dtype=np.float32)
        self._samples = waveform if self._samples is None else np.concatenate((self._samples, waveform))
        events: list[TurnEvent] = []
        for result in self._vad.push(waveform):
            events.extend(self._push_vad_result(result))
        return events

    def finish(self, final_sample_index: int) -> list[TurnEvent]:
        events: list[TurnEvent] = []
        for result in self._vad.flush():
            events.extend(self._push_vad_result(result))
        if self._smart_turn is not None:
            if self._active_turn_id is not None:
                events.append(self._end_active_turn(final_sample_index))
            return events
        if self._turn is not None:
            events.extend(self._turn.finish(final_sample_index))
        return events

    def _push_vad_result(self, result) -> list[TurnEvent]:
        frame_count = int(result.window_frames - result.padded_frames)
        if frame_count <= 0:
            return []
        activity = VoiceActivityEvent(
            source_id="vad",
            stream_id="activity/main",
            seq=self._activity_seq,
            sample_index=int(result.window_start_frame),
            frame_count=frame_count,
            state="speech" if bool(result.is_speech) else "silence",
            speech_probability=float(result.probability),
        )
        self._activity_seq += 1
        if self._smart_turn is None:
            if self._turn is None:
                return []
            return self._turn.push(activity)
        return self._push_smart_turn_activity(activity)

    def _push_smart_turn_activity(self, activity: VoiceActivityEvent) -> list[TurnEvent]:
        if activity.state == "speech":
            self._silence_frames = 0
            self._last_speech_end_sample_index = activity.sample_index + activity.frame_count
            if self._active_turn_id is None:
                self._active_turn_id = self._new_turn_id()
                self._turn_start_sample_index = activity.sample_index
                return [self._build_event(self._active_turn_id, activity.sample_index, "started")]
            return []

        if self._active_turn_id is None:
            return []
        self._silence_frames += activity.frame_count
        if self._samples is None or self._smart_turn is None:
            return []
        end_sample = min(len(self._samples), activity.sample_index + activity.frame_count)
        probability = self._smart_turn.complete_probability(
            self._samples[self._turn_start_sample_index : end_sample]
        )
        required_silence_frames = _confidence_weighted_silence_frames(
            self._end_silence_frames,
            probability,
            min_silence_frames=DEFAULT_TURN_MIN_SILENCE_FRAMES,
        )
        if self._silence_frames < required_silence_frames:
            return []
        return [self._end_active_turn(self._last_speech_end_sample_index or end_sample, confidence=probability)]

    def _end_active_turn(self, sample_index: int, *, confidence: float | None = None) -> TurnEvent:
        if self._active_turn_id is None:
            raise ValueError("cannot end inactive turn")
        event = self._build_event(self._active_turn_id, sample_index, "ended", confidence=confidence)
        self._active_turn_id = None
        self._last_speech_end_sample_index = None
        self._silence_frames = 0
        return event

    def _build_event(
        self,
        user_turn_id: str,
        sample_index: int,
        state: str,
        *,
        confidence: float | None = None,
    ) -> TurnEvent:
        event = TurnEvent(
            session_id="asr-eval",
            user_turn_id=user_turn_id,
            stream_id="turn/main",
            seq=self._next_output_seq,
            sample_index=sample_index,
            state=state,
            confidence=confidence,
        )
        self._next_output_seq += 1
        return event

    def _new_turn_id(self) -> str:
        user_turn_id = f"{self._entry_id}-turn-{self._next_turn_number:06d}"
        self._next_turn_number += 1
        return user_turn_id


class SmartTurnEndpointDetector:
    def __init__(self, model_path: Path) -> None:
        if not model_path.exists():
            raise ValueError(f"Smart Turn model not found: {model_path}")
        import onnxruntime as ort
        from transformers import WhisperFeatureExtractor

        options = ort.SessionOptions()
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        options.inter_op_num_threads = 1
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self._session = ort.InferenceSession(str(model_path), sess_options=options)
        self._feature_extractor = WhisperFeatureExtractor(chunk_length=8)

    def complete_probability(self, samples) -> float:
        import numpy as np

        audio = np.asarray(samples, dtype=np.float32)
        max_frames = 8 * ASR_SAMPLE_RATE_HZ
        if len(audio) > max_frames:
            audio = audio[-max_frames:]
        inputs = self._feature_extractor(
            audio,
            sampling_rate=ASR_SAMPLE_RATE_HZ,
            return_tensors="np",
            padding="max_length",
            max_length=max_frames,
            truncation=True,
            do_normalize=True,
        )
        input_features = inputs.input_features.squeeze(0).astype(np.float32)
        output = self._session.run(None, {"input_features": input_features[None, ...]})
        return float(output[0][0].item())


class StreamingWebHarness:
    def __init__(
        self,
        *,
        manifest_path: Path,
        target_lang: str,
        case_id: str = "current",
        case_label: str | None = None,
        chunk_frames: int = 512,
        limit: int | None = None,
        realtime: bool = False,
        linear_gain: float = 1.0,
        turn_detection: bool = False,
        end_silence_frames: int = DEFAULT_TURN_END_SILENCE_FRAMES,
        smart_turn_model_path: Path | None = None,
        partial_agreement_window: int = 2,
        partial_hold_chars: int = 0,
        session_factory: StreamingAsrSessionFactory,
        probe_cases: Sequence[ProbeCase] = (),
    ) -> None:
        if chunk_frames <= 0:
            raise ValueError("chunk_frames must be positive")
        if partial_agreement_window < 2:
            raise ValueError("partial_agreement_window must be >= 2")
        if partial_hold_chars < 0:
            raise ValueError("partial_hold_chars must be >= 0")
        if not target_lang:
            raise ValueError("target_lang must be non-empty")
        if not case_id:
            raise ValueError("case_id must be non-empty")
        self._manifest_path = manifest_path
        self._target_lang = target_lang
        self._chunk_frames = chunk_frames
        self._limit = limit
        self._realtime = realtime
        self._linear_gain = linear_gain
        self._turn_detection = turn_detection
        self._end_silence_frames = end_silence_frames
        self._smart_turn_model_path = smart_turn_model_path
        self._partial_agreement_window = partial_agreement_window
        self._partial_hold_chars = partial_hold_chars
        self._session_factory = session_factory
        initial_case = ProbeCase(
            id=case_id,
            label=case_label or f"{target_lang} current manifest",
            manifest_path=manifest_path,
            target_lang=target_lang,
            limit=limit,
            turn_detection=turn_detection,
            end_silence_frames=end_silence_frames,
            smart_turn_model_path=smart_turn_model_path,
        )
        self._probe_cases = _merge_probe_cases(initial_case, probe_cases)
        self._case_id = initial_case.id
        self._listeners: set[queue.Queue[Event]] = set()
        self._history: list[HistoryEvent] = []
        self._history_started_at = time.monotonic()
        self._state_lock = threading.Lock()
        self._run_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._run_thread: threading.Thread | None = None
        self._preload_thread: threading.Thread | None = None
        self._state = "idle"
        self._asr_ready = not hasattr(session_factory, "load_backend")
        self._error_message = ""
        self._current_utterance_id: str | None = None
        self._current_utterance_index: int = 0
        self._total_utterances: int = 0

    @property
    def state(self) -> str:
        with self._state_lock:
            return self._state

    def status(self) -> dict[str, str | int | bool]:
        with self._state_lock:
            return self._status_unlocked()

    def case_summaries(self) -> list[EventPayload]:
        with self._state_lock:
            return [case.summary() for case in self._probe_cases.values()]

    def has_case(self, case_id: str) -> bool:
        with self._state_lock:
            return case_id in self._probe_cases

    def register_listener(self) -> queue.Queue[Event]:
        listener: queue.Queue[Event] = queue.Queue()
        with self._state_lock:
            self._listeners.add(listener)
        return listener

    def unregister_listener(self, listener: queue.Queue[Event]) -> None:
        with self._state_lock:
            self._listeners.discard(listener)

    def emit(self, event_name: str, payload: EventPayload) -> None:
        with self._state_lock:
            self._history.append(
                {
                    "t_ms": int((time.monotonic() - self._history_started_at) * 1000),
                    "event": event_name,
                    "payload": json.dumps(payload, ensure_ascii=False),
                }
            )
            self._history = self._history[-MAX_HISTORY_EVENTS:]
            listeners = tuple(self._listeners)
        for listener in listeners:
            listener.put((event_name, payload))

    def history(self) -> list[HistoryEvent]:
        with self._state_lock:
            return list(self._history)

    def set_state(self, state: str) -> None:
        with self._state_lock:
            self._state = state
            current = self._status_unlocked()
        self.emit("status", current)

    def preload_asr_backend(self) -> None:
        loader = getattr(self._session_factory, "load_backend", None)
        if loader is None:
            with self._state_lock:
                self._asr_ready = True
            self.emit("status", self.status())
            return
        with self._state_lock:
            if self._asr_ready or self._preload_thread is not None:
                return
            self._state = "loading_asr_backend"
            current = self._status_unlocked()
        self.emit("status", current)
        self._preload_thread = threading.Thread(
            target=self._preload_asr_backend,
            name="asr-backend-preload",
            daemon=True,
        )
        self._preload_thread.start()

    def start(self, *, case_id: str | None = None) -> bool:
        with self._run_lock:
            if self._run_thread and self._run_thread.is_alive():
                return False
            with self._state_lock:
                if not self._asr_ready or self._state == "loading_asr_backend":
                    return False
                if self._state == "error":
                    return False
                case = self._probe_cases.get(case_id or self._case_id)
                if case is None:
                    self._error_message = f"unknown probe case: {case_id}"
                    return False
            if case_id is not None or case.target_lang != self._target_lang:
                try:
                    self._apply_probe_case(case)
                except Exception as exc:
                    with self._state_lock:
                        self._error_message = f"probe case setup error: {exc}"
                    self.emit("error", {"event": "probe_case", "message": self._error_message})
                    return False
            self._stop_event.clear()
            with self._state_lock:
                self._state = "running"
                self._history = []
                self._history_started_at = time.monotonic()
                self._current_utterance_id = None
                self._current_utterance_index = 0
                self._total_utterances = 0
            self.emit("status", self.status())
            self._run_thread = threading.Thread(
                target=self._run, name="asr-streaming-harness", daemon=True
            )
            self._run_thread.start()
            return True

    def _apply_probe_case(self, case: ProbeCase) -> None:
        if not case.target_lang:
            raise ValueError("probe case target_lang must be non-empty")
        if not case.manifest_path.exists():
            raise ValueError(f"probe case manifest not found: {case.manifest_path}")
        set_target_lang = getattr(self._session_factory, "set_target_lang", None)
        if set_target_lang is not None:
            set_target_lang(case.target_lang)
        with self._state_lock:
            self._case_id = case.id
            self._manifest_path = case.manifest_path
            self._target_lang = case.target_lang
            self._limit = case.limit
            self._turn_detection = case.turn_detection
            self._end_silence_frames = case.end_silence_frames
            self._smart_turn_model_path = case.smart_turn_model_path
            self._error_message = ""

    def _preload_asr_backend(self) -> None:
        loader = getattr(self._session_factory, "load_backend")
        try:
            loader()
        except Exception as exc:
            with self._state_lock:
                self._state = "error"
                self._error_message = f"ASR backend load error: {exc}"
                current = self._status_unlocked()
            self.emit("error", {"event": "asr_backend_load", "message": self._error_message})
            self.emit("status", current)
            return
        with self._state_lock:
            self._asr_ready = True
            self._state = "idle"
            self._error_message = ""
            current = self._status_unlocked()
        self.emit("status", current)

    def _status_unlocked(self) -> dict[str, str | int | bool]:
        running = self._state in {"running", "stopping"}
        return {
            "state": self._state,
            "case_id": self._case_id,
            "manifest": str(self._manifest_path),
            "target_lang": self._target_lang,
            "chunk_frames": self._chunk_frames,
            "limit": self._limit if self._limit is not None else -1,
            "realtime": self._realtime,
            "turn_detection": self._turn_detection,
            "end_silence_frames": self._end_silence_frames,
            "smart_turn_model": str(self._smart_turn_model_path) if self._smart_turn_model_path else "",
            "partial_agreement_window": self._partial_agreement_window,
            "partial_hold_chars": self._partial_hold_chars,
            "current_utterance_id": self._current_utterance_id or "",
            "current_utterance_index": self._current_utterance_index,
            "total_utterances": self._total_utterances,
            "running": running,
            "asr_ready": self._asr_ready,
            "can_run": self._asr_ready and self._state in {"idle", "stopped", "done"},
            "error_message": self._error_message,
        }

    def _new_partial_tracker(self) -> UtterancePartialTracker:
        return UtterancePartialTracker(
            agreement_window=self._partial_agreement_window,
            hold_chars=self._partial_hold_chars,
        )

    def request_stop(self) -> None:
        self._stop_event.set()
        with self._state_lock:
            if self._state == "running":
                self._state = "stopping"
        self.emit("status", self.status())

    def _run(self) -> None:
        error: str | None = None
        cancelled = False
        try:
            entries = _load_manifest_entries(self._manifest_path, self._limit)
            with self._state_lock:
                self._total_utterances = len(entries)
        except Exception as exc:
            error = f"manifest error: {exc}"
            self.set_state("error")
            self.emit("error", {"event": "manifest", "message": error, "state": self.state})
            self.emit("done", {"state": "error"})
            return

        for index, entry in enumerate(entries, 1):
            if self._stop_event.is_set():
                cancelled = True
                break
            with self._state_lock:
                self._current_utterance_id = entry.id
                self._current_utterance_index = index
            self.emit(
                "utterance_start",
                {"id": entry.id, "index": index, "group": entry.group, "text": entry.text},
            )
            if self._turn_detection:
                error, cancelled = self._run_turn_detected_entry(index, entry)
                if cancelled or error is not None:
                    break
                continue
            session: StreamingAsrSession | None = None
            try:
                samples = load_wav_as_16k_f32(entry.wav, linear_gain=self._linear_gain)
                self.emit(
                    "audio_progress",
                    {
                        "id": entry.id,
                        "index": index,
                        "text": entry.text,
                        "chunk_index": 0,
                        "sample_index": 0,
                        "sample_count": int(len(samples)),
                        "elapsed_audio_s": 0.0,
                        "duration_s": float(len(samples) / ASR_SAMPLE_RATE_HZ),
                        "reference_char_index": 0,
                        "reference_char_count": len(entry.text),
                    },
                )
                session = self._session_factory.create(entry.id)
                self.emit("run_phase", {"id": entry.id, "phase": "starting_asr_session"})
                session.start()
                self.emit("run_phase", {"id": entry.id, "phase": "streaming_audio"})
            except Exception as exc:
                error = f"utterance {entry.id} setup error: {exc}"
                if session is not None:
                    try:
                        session.cancel(reason="setup failure")
                    except Exception:
                        pass
                self.emit("error", {"event": "setup", "id": entry.id, "message": error})
                break

            sample_index = 0
            chunk_index = 0
            partial_tracker = self._new_partial_tracker()
            while sample_index < len(samples):
                if self._stop_event.is_set():
                    cancelled = True
                    try:
                        session.cancel(reason="stop requested")
                    except Exception:
                        pass
                    break
                block = samples[sample_index : sample_index + self._chunk_frames]
                next_sample_index = sample_index + len(block)
                sent_chunk_index = chunk_index + 1
                self.emit(
                    "audio_progress",
                    {
                        "id": entry.id,
                        "index": index,
                        "text": entry.text,
                        "chunk_index": sent_chunk_index,
                        "sample_index": next_sample_index,
                        "sample_count": int(len(samples)),
                        "elapsed_audio_s": float(next_sample_index / ASR_SAMPLE_RATE_HZ),
                        "duration_s": float(len(samples) / ASR_SAMPLE_RATE_HZ),
                        "reference_char_index": _reference_char_index(
                            entry.text,
                            sample_index=next_sample_index,
                            sample_count=len(samples),
                        ),
                        "reference_char_count": len(entry.text),
                    },
                )
                started = time.perf_counter()
                try:
                    partials = session.push_audio(
                        block,
                        sample_index=sample_index,
                        chunk_index=chunk_index,
                    )
                except Exception as exc:
                    error = f"utterance {entry.id} push error: {exc}"
                    try:
                        session.cancel(reason="push failure")
                    except Exception:
                        pass
                    break
                push_wall_s = time.perf_counter() - started
                partial_tracker.observe_push(push_wall_s)
                sample_index = next_sample_index
                chunk_index = sent_chunk_index
                for partial in partials:
                    partial_text = str(getattr(partial, "text", ""))
                    stable_text, unstable_text = partial_tracker.update_partial(
                        partial_text,
                        elapsed_audio_s=float(sample_index / ASR_SAMPLE_RATE_HZ),
                    )
                    self.emit(
                        "partial",
                        {
                            "id": entry.id,
                            "seq": int(getattr(partial, "seq", 0)),
                            "text": partial_text,
                            "stable_text": stable_text,
                            "unstable_text": unstable_text,
                            "chunk_index": int(getattr(partial, "chunk_index", chunk_index)),
                            "sample_index": int(getattr(partial, "sample_index", sample_index)),
                            "push_wall_s": float(push_wall_s),
                            "elapsed_audio_s": float(sample_index / ASR_SAMPLE_RATE_HZ),
                            "index": index,
                        },
                    )
                if self._realtime and len(block) > 0:
                    chunk_seconds = len(block) / ASR_SAMPLE_RATE_HZ
                    if chunk_seconds > 0:
                        time.sleep(chunk_seconds)

            if cancelled:
                break
            if error is not None:
                break
            if len(samples) == 0:
                try:
                    final = session.stop(sample_count=0)
                    final_text = str(getattr(final, "text", ""))
                except Exception:
                    final_text = ""
                self.emit("final", {"id": entry.id, "text": final_text, "sample_count": 0})
                self.emit("utterance_done", {"id": entry.id, "status": "empty", "sample_count": 0})
                continue
            try:
                final = session.stop(sample_count=sample_index)
            except Exception as exc:
                error = f"utterance {entry.id} stop error: {exc}"
                try:
                    session.cancel(reason="stop failure")
                except Exception:
                    pass
                break

            final_text = str(getattr(final, "text", ""))
            self.emit(
                "final",
                {
                    "id": entry.id,
                    "text": final_text,
                    "sample_count": int(sample_index),
                },
            )
            self._emit_utterance_metrics(
                utterance_id=entry.id,
                source_id=entry.id,
                index=index,
                tracker=partial_tracker,
                final_text=final_text,
                stop_wall_s=float(getattr(final, "stop_wall_s", 0.0)),
                sample_count=sample_index,
            )
            self.emit("utterance_done", {"id": entry.id, "status": "done", "sample_count": sample_index})

        if cancelled:
            self.set_state("stopped")
            self.emit("done", {"state": "stopped"})
            return
        if error is not None:
            self.emit("error", {"event": "runtime", "message": error, "state": self.state})
            self.set_state("error")
            self.emit("done", {"state": "error"})
            return
        self.set_state("done")
        self.emit("done", {"state": "done"})

    def _run_turn_detected_entry(
        self,
        index: int,
        entry: ManifestEntry,
    ) -> tuple[str | None, bool]:
        import numpy as np

        try:
            samples = np.asarray(
                load_wav_as_16k_f32(entry.wav, linear_gain=self._linear_gain),
                dtype=np.float32,
            )
            detector = StreamingTurnDetector(
                entry_id=entry.id,
                end_silence_frames=self._end_silence_frames,
                smart_turn_model_path=self._smart_turn_model_path,
            )
        except Exception as exc:
            error = f"utterance {entry.id} turn detector setup error: {exc}"
            self.emit("error", {"event": "setup", "id": entry.id, "message": error})
            return error, False

        self.emit(
            "audio_progress",
            {
                "id": entry.id,
                "index": index,
                "text": entry.text,
                "chunk_index": 0,
                "sample_index": 0,
                "sample_count": int(len(samples)),
                "elapsed_audio_s": 0.0,
                "duration_s": float(len(samples) / ASR_SAMPLE_RATE_HZ),
                "reference_char_index": 0,
                "reference_char_count": len(entry.text),
            },
        )

        session: StreamingAsrSession | None = None
        turn_id = ""
        turn_start_sample = 0
        sent_until = 0
        turn_chunk_index = 0
        partial_tracker: UtterancePartialTracker | None = None
        turns_started = 0
        sample_index = 0
        chunk_index = 0

        while sample_index < len(samples):
            if self._stop_event.is_set():
                if session is not None:
                    try:
                        session.cancel(reason="stop requested")
                    except Exception:
                        pass
                return None, True

            block = samples[sample_index : sample_index + self._chunk_frames]
            next_sample_index = sample_index + len(block)
            sent_chunk_index = chunk_index + 1
            self.emit(
                "audio_progress",
                {
                    "id": entry.id,
                    "index": index,
                    "text": entry.text,
                    "chunk_index": sent_chunk_index,
                    "sample_index": int(next_sample_index),
                    "sample_count": int(len(samples)),
                    "elapsed_audio_s": float(next_sample_index / ASR_SAMPLE_RATE_HZ),
                    "duration_s": float(len(samples) / ASR_SAMPLE_RATE_HZ),
                    "reference_char_index": _reference_char_index(
                        entry.text,
                        sample_index=int(next_sample_index),
                        sample_count=len(samples),
                    ),
                    "reference_char_count": len(entry.text),
                },
            )

            try:
                turn_events = detector.push(block)
            except Exception as exc:
                error = f"utterance {entry.id} turn detector push error: {exc}"
                if session is not None:
                    try:
                        session.cancel(reason="turn detector failure")
                    except Exception:
                        pass
                self.emit("error", {"event": "turn_detector", "id": entry.id, "message": error})
                return error, False

            for event in turn_events:
                self._emit_turn_event(entry, index, event)
                if event.state == "started":
                    if session is not None:
                        error = f"utterance {entry.id} started a new turn before ending {turn_id}"
                        self.emit("error", {"event": "turn_detector", "id": entry.id, "message": error})
                        return error, False
                    turn_id = event.user_turn_id
                    turn_start_sample = max(0, event.sample_index - TURN_PREROLL_FRAMES)
                    sent_until = turn_start_sample
                    turn_chunk_index = 0
                    partial_tracker = self._new_partial_tracker()
                    turns_started += 1
                    try:
                        session = self._session_factory.create(turn_id)
                        self.emit("run_phase", {"id": turn_id, "source_id": entry.id, "phase": "starting_asr_session"})
                        session.start()
                        self.emit("run_phase", {"id": turn_id, "source_id": entry.id, "phase": "streaming_audio"})
                    except Exception as exc:
                        error = f"utterance {entry.id} ASR turn setup error: {exc}"
                        self.emit("error", {"event": "setup", "id": turn_id, "message": error})
                        return error, False

            if session is not None:
                if partial_tracker is None:
                    partial_tracker = self._new_partial_tracker()
                sent_until, turn_chunk_index, error = self._push_turn_asr_audio(
                    session,
                    samples,
                    start_sample=sent_until,
                    end_sample=int(next_sample_index),
                    turn_start_sample=turn_start_sample,
                    chunk_index=turn_chunk_index,
                    entry=entry,
                    manifest_index=index,
                    turn_id=turn_id,
                    partial_tracker=partial_tracker,
                )
                if error is not None:
                    return error, False

            for event in turn_events:
                if event.state == "ended" and session is not None and event.user_turn_id == turn_id:
                    try:
                        final = session.stop(sample_count=sent_until - turn_start_sample)
                    except Exception as exc:
                        error = f"utterance {entry.id} ASR turn stop error: {exc}"
                        try:
                            session.cancel(reason="stop failure")
                        except Exception:
                            pass
                        self.emit("error", {"event": "runtime", "id": turn_id, "message": error})
                        return error, False
                    self.emit(
                        "final",
                        {
                            "id": turn_id,
                            "source_id": entry.id,
                            "text": str(getattr(final, "text", "")),
                            "sample_count": int(sent_until - turn_start_sample),
                        },
                    )
                    if partial_tracker is not None:
                        self._emit_utterance_metrics(
                            utterance_id=turn_id,
                            source_id=entry.id,
                            index=index,
                            tracker=partial_tracker,
                            final_text=str(getattr(final, "text", "")),
                            stop_wall_s=float(getattr(final, "stop_wall_s", 0.0)),
                            sample_count=int(sent_until - turn_start_sample),
                        )
                    self.emit(
                        "utterance_done",
                        {
                            "id": turn_id,
                            "source_id": entry.id,
                            "status": "done",
                            "sample_count": int(sent_until - turn_start_sample),
                        },
                    )
                    session = None
                    turn_id = ""
                    partial_tracker = None

            sample_index = int(next_sample_index)
            chunk_index = sent_chunk_index
            if self._realtime and len(block) > 0:
                chunk_seconds = len(block) / ASR_SAMPLE_RATE_HZ
                if chunk_seconds > 0:
                    time.sleep(chunk_seconds)

        try:
            turn_events = detector.finish(len(samples))
        except Exception as exc:
            error = f"utterance {entry.id} turn detector finish error: {exc}"
            if session is not None:
                try:
                    session.cancel(reason="turn detector finish failure")
                except Exception:
                    pass
            self.emit("error", {"event": "turn_detector", "id": entry.id, "message": error})
            return error, False

        for event in turn_events:
            self._emit_turn_event(entry, index, event)
            if event.state == "started":
                turn_id = event.user_turn_id
                turn_start_sample = max(0, event.sample_index - TURN_PREROLL_FRAMES)
                sent_until = turn_start_sample
                turn_chunk_index = 0
                partial_tracker = self._new_partial_tracker()
                turns_started += 1
                session = self._session_factory.create(turn_id)
                session.start()
            if session is not None:
                if partial_tracker is None:
                    partial_tracker = self._new_partial_tracker()
                sent_until, turn_chunk_index, error = self._push_turn_asr_audio(
                    session,
                    samples,
                    start_sample=sent_until,
                    end_sample=len(samples),
                    turn_start_sample=turn_start_sample,
                    chunk_index=turn_chunk_index,
                    entry=entry,
                    manifest_index=index,
                    turn_id=turn_id,
                    partial_tracker=partial_tracker,
                )
                if error is not None:
                    return error, False
            if event.state == "ended" and session is not None and event.user_turn_id == turn_id:
                final = session.stop(sample_count=sent_until - turn_start_sample)
                self.emit(
                    "final",
                    {
                        "id": turn_id,
                        "source_id": entry.id,
                        "text": str(getattr(final, "text", "")),
                        "sample_count": int(sent_until - turn_start_sample),
                    },
                )
                if partial_tracker is not None:
                    self._emit_utterance_metrics(
                        utterance_id=turn_id,
                        source_id=entry.id,
                        index=index,
                        tracker=partial_tracker,
                        final_text=str(getattr(final, "text", "")),
                        stop_wall_s=float(getattr(final, "stop_wall_s", 0.0)),
                        sample_count=int(sent_until - turn_start_sample),
                    )
                self.emit(
                    "utterance_done",
                    {
                        "id": turn_id,
                        "source_id": entry.id,
                        "status": "done",
                        "sample_count": int(sent_until - turn_start_sample),
                    },
                )
                session = None
                turn_id = ""
                partial_tracker = None

        if session is not None:
            final = session.stop(sample_count=sent_until - turn_start_sample)
            self.emit(
                "final",
                {
                    "id": turn_id,
                    "source_id": entry.id,
                    "text": str(getattr(final, "text", "")),
                    "sample_count": int(sent_until - turn_start_sample),
                },
            )
            if partial_tracker is not None:
                self._emit_utterance_metrics(
                    utterance_id=turn_id,
                    source_id=entry.id,
                    index=index,
                    tracker=partial_tracker,
                    final_text=str(getattr(final, "text", "")),
                    stop_wall_s=float(getattr(final, "stop_wall_s", 0.0)),
                    sample_count=int(sent_until - turn_start_sample),
                )
            self.emit(
                "utterance_done",
                {
                    "id": turn_id,
                    "source_id": entry.id,
                    "status": "done",
                    "sample_count": int(sent_until - turn_start_sample),
                },
            )
        if turns_started == 0:
            self.emit("utterance_done", {"id": entry.id, "status": "no_speech", "sample_count": int(len(samples))})
        return None, False

    def _push_turn_asr_audio(
        self,
        session: StreamingAsrSession,
        samples,
        *,
        start_sample: int,
        end_sample: int,
        turn_start_sample: int,
        chunk_index: int,
        entry: ManifestEntry,
        manifest_index: int,
        turn_id: str,
        partial_tracker: UtterancePartialTracker,
    ) -> tuple[int, int, str | None]:
        cursor = start_sample
        current_chunk = chunk_index
        while cursor < end_sample:
            block = samples[cursor : min(cursor + self._chunk_frames, end_sample)]
            started = time.perf_counter()
            try:
                partials = session.push_audio(
                    block,
                    sample_index=cursor - turn_start_sample,
                    chunk_index=current_chunk,
                )
            except Exception as exc:
                error = f"utterance {entry.id} ASR turn push error: {exc}"
                try:
                    session.cancel(reason="push failure")
                except Exception:
                    pass
                self.emit("error", {"event": "runtime", "id": turn_id, "message": error})
                return cursor, current_chunk, error
            push_wall_s = time.perf_counter() - started
            partial_tracker.observe_push(push_wall_s)
            cursor += len(block)
            current_chunk += 1
            for partial in partials:
                partial_text = str(getattr(partial, "text", ""))
                stable_text, unstable_text = partial_tracker.update_partial(
                    partial_text,
                    elapsed_audio_s=float(cursor / ASR_SAMPLE_RATE_HZ),
                )
                self.emit(
                    "partial",
                    {
                        "id": turn_id,
                        "source_id": entry.id,
                        "seq": int(getattr(partial, "seq", 0)),
                        "text": partial_text,
                        "stable_text": stable_text,
                        "unstable_text": unstable_text,
                        "chunk_index": int(getattr(partial, "chunk_index", current_chunk)),
                        "sample_index": int(getattr(partial, "sample_index", cursor - turn_start_sample)),
                        "push_wall_s": float(push_wall_s),
                        "elapsed_audio_s": float(cursor / ASR_SAMPLE_RATE_HZ),
                        "index": manifest_index,
                    },
                )
        return cursor, current_chunk, None

    def _emit_utterance_metrics(
        self,
        *,
        utterance_id: str,
        source_id: str,
        index: int,
        tracker: UtterancePartialTracker,
        final_text: str,
        stop_wall_s: float,
        sample_count: int,
    ) -> None:
        payload: EventPayload = {
            "id": utterance_id,
            "source_id": source_id,
            "index": index,
        }
        payload.update(
            tracker.summary(
                final_text=final_text,
                stop_wall_s=stop_wall_s,
                audio_duration_s=float(sample_count / ASR_SAMPLE_RATE_HZ),
            )
        )
        self.emit("utterance_metrics", payload)

    def _emit_turn_event(self, entry: ManifestEntry, index: int, event: TurnEvent) -> None:
        if event.state == "active":
            return
        self.emit(
            "turn",
            {
                "id": entry.id,
                "index": index,
                "turn_id": event.user_turn_id,
                "state": event.state,
                "sample_index": event.sample_index,
                "elapsed_audio_s": float(event.sample_index / ASR_SAMPLE_RATE_HZ),
                "confidence": float(event.confidence) if event.confidence is not None else -1.0,
            },
        )


def _load_manifest_entries(path: Path, limit: int | None) -> list[ManifestEntry]:
    entries_raw = load_manifest(path)
    if limit is not None:
        if limit <= 0:
            raise ValueError("limit must be positive")
        entries_raw = entries_raw[:limit]
    entries: list[ManifestEntry] = []
    for raw_index, raw in enumerate(entries_raw, 1):
        if not isinstance(raw, dict):
            raise ValueError(f"manifest line {raw_index} is not a JSON object")
        for key in _REQUIRED_MANIFEST_FIELDS:
            if key not in raw:
                raise ValueError(f"manifest line {raw_index} missing field: {key}")
            if not isinstance(raw[key], str):
                raise ValueError(f"manifest line {raw_index} field '{key}' must be a string")
        wav_path = Path(raw["wav"])
        if not wav_path.is_absolute():
            if not wav_path.exists():
                wav_path = path.parent / wav_path
        if not wav_path.exists():
            raise ValueError(f"manifest line {raw_index} wav not found: {wav_path}")
        entries.append(
            ManifestEntry(
                id=str(raw["id"]),
                group=str(raw["group"]),
                text=str(raw["text"]),
                wav=wav_path,
            )
        )
    if not entries:
        raise ValueError(f"{path}: manifest has no valid entries")
    return entries


def _reference_char_index(text: str, *, sample_index: int, sample_count: int) -> int:
    if sample_count <= 0:
        return 0
    return min(len(text), max(0, (len(text) * sample_index) // sample_count))


def _longest_common_prefix(left: str, right: str) -> str:
    end = 0
    for left_char, right_char in zip(left, right):
        if left_char != right_char:
            break
        end += 1
    return left[:end]


def _confidence_weighted_silence_frames(
    max_silence_frames: int,
    confidence: float,
    *,
    min_silence_frames: int = 0,
) -> int:
    bounded_confidence = min(1.0, max(0.0, confidence))
    return max(min_silence_frames, round(max_silence_frames * (1.0 - bounded_confidence)))


def _merge_probe_cases(initial_case: ProbeCase, probe_cases: Sequence[ProbeCase]) -> dict[str, ProbeCase]:
    cases: dict[str, ProbeCase] = {initial_case.id: initial_case}
    for case in probe_cases:
        if not case.id:
            raise ValueError("probe case id must be non-empty")
        if not case.target_lang:
            raise ValueError(f"probe case {case.id} target_lang must be non-empty")
        cases[case.id] = case
    return cases


def _default_extra_probe_cases() -> tuple[ProbeCase, ...]:
    cases: list[ProbeCase] = []
    english_manifest = _REPO_ROOT / "artifacts/asr_eval/en_harvard_probe/manifest.jsonl"
    if english_manifest.exists():
        cases.append(
            ProbeCase(
                id="en",
                label="English Harvard probe",
                manifest_path=english_manifest,
                target_lang="en-US",
                limit=1,
            )
        )
    long_manifest = _REPO_ROOT / "artifacts/asr_eval/ja_long_probe/manifest.jsonl"
    if long_manifest.exists():
        cases.append(
            ProbeCase(
                id="ja_long",
                label="Japanese long probe",
                manifest_path=long_manifest,
                target_lang="ja-JP",
                limit=1,
            )
        )
        if DEFAULT_SMART_TURN_MODEL_PATH.exists():
            cases.append(
                ProbeCase(
                    id="ja_long_smart_turn",
                    label="Japanese long Smart Turn probe",
                    manifest_path=long_manifest,
                    target_lang="ja-JP",
                    limit=1,
                    turn_detection=True,
                    end_silence_frames=DEFAULT_TURN_END_SILENCE_FRAMES,
                    smart_turn_model_path=DEFAULT_SMART_TURN_MODEL_PATH,
                )
            )
    segmented_manifest = _REPO_ROOT / "artifacts/asr_eval/ja_long_segmented_probe/manifest.jsonl"
    if segmented_manifest.exists():
        cases.append(
            ProbeCase(
                id="ja_long_segmented",
                label="Japanese long segmented probe",
                manifest_path=segmented_manifest,
                target_lang="ja-JP",
                limit=5,
            )
        )
    return tuple(cases)


def _render_html() -> bytes:
    return """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Nemotron ASR Probe</title>
    <style>
      :root {
        color-scheme: light;
        --bg: #f6f7f9;
        --panel: #ffffff;
        --ink: #1c2430;
        --muted: #657084;
        --line: #d9dee8;
        --blue: #1f6feb;
        --green: #14804a;
        --red: #c23131;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        background: var(--bg);
        color: var(--ink);
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }
      header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 18px 22px;
        border-bottom: 1px solid var(--line);
        background: var(--panel);
      }
      h1 {
        margin: 0;
        font-size: 20px;
        line-height: 1.2;
      }
      main {
        display: grid;
        grid-template-columns: minmax(280px, 360px) minmax(0, 1fr);
        gap: 16px;
        padding: 16px;
      }
      section, aside {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
      }
      aside { padding: 14px; }
      section { overflow: hidden; }
      .controls {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 14px;
      }
      button, select {
        border: 1px solid var(--line);
        border-radius: 6px;
        background: #fff;
        color: var(--ink);
        cursor: pointer;
        font-size: 14px;
        font-weight: 600;
        min-height: 38px;
        padding: 0 14px;
      }
      select {
        width: 100%;
        font-weight: 600;
        margin-top: 14px;
      }
      button.primary {
        background: var(--blue);
        border-color: var(--blue);
        color: #fff;
      }
      button.danger {
        border-color: #e0b4b4;
        color: var(--red);
      }
      .pill {
        border-radius: 999px;
        background: #edf2ff;
        color: #174ea6;
        display: inline-flex;
        font-size: 13px;
        font-weight: 700;
        padding: 5px 10px;
      }
      .grid {
        display: grid;
        gap: 8px;
        margin-top: 14px;
      }
      .row {
        display: grid;
        grid-template-columns: 112px minmax(0, 1fr);
        gap: 8px;
        align-items: start;
        border-top: 1px solid var(--line);
        padding-top: 8px;
      }
      .label {
        color: var(--muted);
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
      }
      .value {
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-size: 13px;
        overflow-wrap: anywhere;
      }
      .progress {
        height: 8px;
        overflow: hidden;
        border-radius: 999px;
        background: #e9edf4;
        margin-top: 12px;
      }
      .bar {
        width: 0%;
        height: 100%;
        background: var(--blue);
        transition: width 160ms ease;
      }
      .metric-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin-top: 12px;
      }
      .metric {
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 10px;
      }
      .metric strong {
        display: block;
        font-size: 24px;
        line-height: 1;
      }
      .metric span {
        color: var(--muted);
        font-size: 12px;
      }
      .panel-head {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        padding: 14px 16px;
        border-bottom: 1px solid var(--line);
      }
      .panel-head h2 {
        margin: 0;
        font-size: 16px;
      }
      .audio-progress {
        display: grid;
        gap: 8px;
        padding: 12px 16px 0;
      }
      .audio-progress .value {
        color: var(--muted);
      }
      .current {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        padding: 14px 16px;
        border-bottom: 1px solid var(--line);
      }
      .transcript {
        min-height: 96px;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 10px;
      }
      .transcript h3 {
        margin: 0 0 8px;
        color: var(--muted);
        font-size: 12px;
        text-transform: uppercase;
      }
      .transcript div {
        font-size: 16px;
        line-height: 1.5;
        overflow-wrap: anywhere;
      }
      .reference-text {
        font-size: 20px;
        line-height: 1.7;
      }
      .reference-text .played {
        color: var(--ink);
        font-weight: 700;
      }
      .reference-text .current-char {
        background: #fff0b3;
        border-bottom: 3px solid var(--blue);
        color: var(--ink);
        font-weight: 800;
      }
      .reference-text .pending {
        color: #a2aab8;
      }
      .partial-stable {
        color: var(--ink);
        font-weight: 700;
      }
      .partial-tail {
        color: #8b95a5;
      }
      table {
        width: 100%;
        border-collapse: collapse;
      }
      th, td {
        border-bottom: 1px solid var(--line);
        font-size: 13px;
        padding: 9px 10px;
        text-align: left;
        vertical-align: top;
      }
      th {
        color: var(--muted);
        font-size: 12px;
        text-transform: uppercase;
        background: #fafbfc;
      }
      td.payload {
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        overflow-wrap: anywhere;
      }
      @media (max-width: 860px) {
        main, .current { grid-template-columns: 1fr; }
        header { align-items: flex-start; flex-direction: column; }
      }
    </style>
  </head>
  <body>
    <header>
      <h1>Nemotron ASR Streaming Probe</h1>
      <span class="pill" id="state">connecting</span>
    </header>
    <main>
      <aside>
        <label class="label" for="case">probe case</label>
        <select id="case"></select>
        <div class="controls">
          <button id="run" class="primary">Start run</button>
          <button id="replay">Replay last run</button>
          <button id="stop" class="danger">Stop</button>
        </div>
        <div class="progress"><div class="bar" id="progress"></div></div>
        <div class="metric-row">
          <div class="metric"><strong id="partialCount">0</strong><span>partials</span></div>
          <div class="metric"><strong id="finalCount">0</strong><span>finals</span></div>
          <div class="metric"><strong id="errorCount">0</strong><span>errors</span></div>
        </div>
        <div class="metric-row">
          <div class="metric"><strong id="retreatCount">0</strong><span>stable retreats</span></div>
          <div class="metric"><strong id="firstPartial">-</strong><span>1st partial</span></div>
          <div class="metric"><strong id="meanPush">-</strong><span>mean push</span></div>
        </div>
        <div class="grid">
          <div class="row"><div class="label">manifest</div><div class="value" id="manifest">-</div></div>
          <div class="row"><div class="label">language</div><div class="value" id="language">-</div></div>
          <div class="row"><div class="label">utterance</div><div class="value" id="utterance">-</div></div>
          <div class="row"><div class="label">chunk</div><div class="value" id="chunk">-</div></div>
          <div class="row"><div class="label">stabilizer</div><div class="value" id="stabilizer">-</div></div>
          <div class="row"><div class="label">phase</div><div class="value" id="phase">-</div></div>
          <div class="row"><div class="label">mode</div><div class="value" id="mode">-</div></div>
        </div>
      </aside>
      <section>
        <div class="panel-head">
          <h2>Streaming Audio Segment</h2>
          <span class="value" id="currentId">-</span>
        </div>
        <div class="audio-progress">
          <div class="progress"><div class="bar" id="audioProgress"></div></div>
          <div class="value" id="audioProgressText">-</div>
        </div>
        <div class="current">
          <div class="transcript">
            <h3>Dataset playback cursor</h3>
            <div id="reference" class="reference-text">-</div>
            <div class="value" id="referenceCursor">-</div>
          </div>
          <div class="transcript"><h3>Latest partial</h3><div id="partial">-</div></div>
          <div class="transcript"><h3>Final</h3><div id="final">-</div></div>
        </div>
        <table>
          <thead>
            <tr><th>time</th><th>event</th><th>utterance</th><th>payload</th></tr>
          </thead>
          <tbody id="events"></tbody>
        </table>
      </section>
    </main>
    <script>
      const $ = (id) => document.getElementById(id);
      const counts = {partial: 0, final: 0, error: 0, retreat: 0};
      const setText = (id, value) => { $(id).textContent = value || "-"; };
      const applyMetrics = (data) => {
        counts.retreat += Number(data.stable_retreat_count || 0);
        setText("retreatCount", String(counts.retreat));
        setText("firstPartial", `${Number(data.first_partial_elapsed_audio_s || 0).toFixed(2)}s`);
        setText("meanPush", `${Number(data.mean_push_wall_ms || 0).toFixed(0)}ms`);
      };
      const resetMetrics = () => {
        counts.partial = 0;
        counts.final = 0;
        counts.error = 0;
        counts.retreat = 0;
        setText("partialCount", "0");
        setText("finalCount", "0");
        setText("errorCount", "0");
        setText("retreatCount", "0");
        setText("firstPartial", "");
        setText("meanPush", "");
      };
      const loadCases = () => {
        fetch("/cases")
          .then((r) => r.json())
          .then((items) => {
            const select = $("case");
            select.textContent = "";
            for (const item of items) {
              const option = document.createElement("option");
              option.value = item.id;
              const limit = Number(item.limit || -1);
              option.textContent = `${item.label} (${item.target_lang}${limit > 0 ? ", limit " + limit : ""})`;
              select.append(option);
            }
          });
      };
      const renderReferenceProgress = (text, charIndex) => {
        const chars = Array.from(text || "");
        const safeIndex = Math.max(0, Math.min(chars.length, Number(charIndex || 0)));
        const el = $("reference");
        el.textContent = "";
        if (!chars.length) {
          el.textContent = "-";
          setText("referenceCursor", "");
          return;
        }
        const played = document.createElement("span");
        played.className = "played";
        played.textContent = chars.slice(0, safeIndex).join("");
        const current = document.createElement("span");
        current.className = "current-char";
        current.textContent = chars[safeIndex] || "";
        const pending = document.createElement("span");
        pending.className = "pending";
        pending.textContent = chars.slice(safeIndex + (current.textContent ? 1 : 0)).join("");
        el.append(played, current, pending);
        setText("referenceCursor", `${safeIndex} / ${chars.length} chars`);
      };
      const renderPartial = (data) => {
        const raw = String(data.text || "");
        const stable = String(data.stable_text || "");
        const tail = Object.prototype.hasOwnProperty.call(data, "unstable_text")
          ? String(data.unstable_text || "")
          : raw.slice(stable.length);
        const el = $("partial");
        el.textContent = "";
        if (!raw && !stable && !tail) {
          el.textContent = "-";
          return;
        }
        if (stable) {
          const stableEl = document.createElement("span");
          stableEl.className = "partial-stable";
          stableEl.textContent = stable;
          el.append(stableEl);
        }
        if (tail) {
          const tailEl = document.createElement("span");
          tailEl.className = "partial-tail";
          tailEl.textContent = tail;
          el.append(tailEl);
        }
      };
      let replayTimers = [];
      const clearReplayTimers = () => {
        for (const timer of replayTimers) clearTimeout(timer);
        replayTimers = [];
      };
      const addEvent = (name, data) => {
        const row = document.createElement("tr");
        const payload = JSON.stringify(data);
        row.innerHTML = `<td>${new Date().toLocaleTimeString()}</td><td>${name}</td><td>${data.id || data.current_utterance_id || "-"}</td><td class="payload"></td>`;
        row.querySelector(".payload").textContent = payload;
        $("events").prepend(row);
        while ($("events").children.length > 100) $("events").lastElementChild.remove();
      };
      const renderStatus = (data) => {
        setText("state", data.state);
        $("state").style.background = data.running ? "#e6f4ea" : "#edf2ff";
        $("state").style.color = data.running ? "#137333" : "#174ea6";
        setText("manifest", data.manifest);
        setText("language", data.target_lang);
        const total = Number(data.total_utterances || 0);
        const index = Number(data.current_utterance_index || 0);
        setText("utterance", total ? `${index} / ${total}` : "-");
        setText("currentId", data.current_utterance_id);
        setText("chunk", `${data.chunk_frames} frames`);
        setText("stabilizer", `window ${data.partial_agreement_window}, hold ${data.partial_hold_chars}`);
        setText("phase", data.error_message || (data.asr_ready ? data.state : "loading_asr_backend"));
        setText("mode", data.realtime ? "realtime" : "fast");
        $("progress").style.width = total ? `${Math.min(100, (index / total) * 100)}%` : "0%";
        $("run").disabled = !data.can_run;
        $("stop").disabled = !data.running;
        $("case").disabled = data.running;
        if (data.case_id && !$("case").value) $("case").value = data.case_id;
      };
      const es = new EventSource("/events");
      const applyRecordedEvent = (name, data) => {
        if (name === "status") {
          renderStatus(data);
          addEvent("status", data);
          return;
        }
        if (name === "utterance_start") {
          setText("currentId", data.id);
          renderReferenceProgress(data.text, 0);
          setText("partial", "");
          setText("final", "");
          $("audioProgress").style.width = "0%";
          setText("audioProgressText", "0.00s / -");
          addEvent("utterance_start", data);
          return;
        }
        if (name === "audio_progress") {
          const sampleCount = Number(data.sample_count || 0);
          const sampleIndex = Number(data.sample_index || 0);
          const pct = sampleCount ? Math.min(100, (sampleIndex / sampleCount) * 100) : 0;
          setText("currentId", data.id);
          renderReferenceProgress(data.text, data.reference_char_index);
          $("audioProgress").style.width = `${pct}%`;
          setText("audioProgressText", `${Number(data.elapsed_audio_s || 0).toFixed(2)}s / ${Number(data.duration_s || 0).toFixed(2)}s, chunk ${data.chunk_index}`);
          return;
        }
        if (name === "run_phase") {
          setText("phase", data.phase);
          addEvent("run_phase", data);
          return;
        }
        if (name === "partial") {
          counts.partial += 1;
          setText("partialCount", String(counts.partial));
          renderPartial(data);
          addEvent("partial", data);
          return;
        }
        if (name === "final") {
          counts.final += 1;
          setText("finalCount", String(counts.final));
          setText("final", data.text);
          addEvent("final", data);
          return;
        }
        if (name === "utterance_metrics") {
          applyMetrics(data);
        }
        if (name === "error") {
          counts.error += 1;
          setText("errorCount", String(counts.error));
        }
        addEvent(name, data);
      };
      es.addEventListener("status", (e) => {
        const data = JSON.parse(e.data);
        renderStatus(data);
        addEvent("status", data);
      });
      es.addEventListener("utterance_start", (e) => {
        const data = JSON.parse(e.data);
        setText("currentId", data.id);
        renderReferenceProgress(data.text, 0);
        setText("partial", "");
        setText("final", "");
        $("audioProgress").style.width = "0%";
        setText("audioProgressText", "0.00s / -");
        addEvent("utterance_start", data);
      });
      es.addEventListener("audio_progress", (e) => {
        const data = JSON.parse(e.data);
        const sampleCount = Number(data.sample_count || 0);
        const sampleIndex = Number(data.sample_index || 0);
        const pct = sampleCount ? Math.min(100, (sampleIndex / sampleCount) * 100) : 0;
        setText("currentId", data.id);
        renderReferenceProgress(data.text, data.reference_char_index);
        $("audioProgress").style.width = `${pct}%`;
        setText("audioProgressText", `${Number(data.elapsed_audio_s || 0).toFixed(2)}s / ${Number(data.duration_s || 0).toFixed(2)}s, chunk ${data.chunk_index}`);
      });
      es.addEventListener("run_phase", (e) => {
        const data = JSON.parse(e.data);
        setText("phase", data.phase);
        if (data.phase === "loading_asr_backend") {
          setText("audioProgressText", "ASR backend loading; audio has not started streaming yet");
        }
        if (data.phase === "starting_asr_session") {
          setText("audioProgressText", "ASR session starting; audio has not started streaming yet");
        }
        addEvent("run_phase", data);
      });
      es.addEventListener("turn", (e) => addEvent("turn", JSON.parse(e.data)));
      es.addEventListener("partial", (e) => {
        const data = JSON.parse(e.data);
        counts.partial += 1;
        setText("partialCount", String(counts.partial));
        renderPartial(data);
        addEvent("partial", data);
      });
      es.addEventListener("final", (e) => {
        const data = JSON.parse(e.data);
        counts.final += 1;
        setText("finalCount", String(counts.final));
        setText("final", data.text);
        addEvent("final", data);
      });
      es.addEventListener("utterance_done", (e) => addEvent("utterance_done", JSON.parse(e.data)));
      es.addEventListener("utterance_metrics", (e) => {
        const data = JSON.parse(e.data);
        applyMetrics(data);
        addEvent("utterance_metrics", data);
      });
      es.addEventListener("done", (e) => addEvent("done", JSON.parse(e.data)));
      es.addEventListener("error", (e) => {
        const data = JSON.parse(e.data);
        counts.error += 1;
        setText("errorCount", String(counts.error));
        addEvent("error", data);
      });
      document.getElementById("run").onclick = () => {
        if ($("run").disabled) return;
        clearReplayTimers();
        resetMetrics();
        renderReferenceProgress("", 0);
        setText("partial", "");
        setText("final", "");
        setText("phase", "");
        $("audioProgress").style.width = "0%";
        setText("audioProgressText", "");
        $("events").textContent = "";
        fetch("/run", {
          method:"POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({case_id: $("case").value})
        }).then((r) => r.json()).then((x) => addEvent("run", x));
      };
      document.getElementById("stop").onclick = () => {
        fetch("/stop", {method:"POST"}).then((r) => r.json()).then((x) => addEvent("stop", x));
      };
      document.getElementById("replay").onclick = () => {
        clearReplayTimers();
        resetMetrics();
        $("events").textContent = "";
        fetch("/history")
          .then((r) => r.json())
          .then((items) => {
            if (!items.length) {
              addEvent("replay", {message: "no run history"});
              return;
            }
            const first = Number(items[0].t_ms || 0);
            for (const item of items) {
              const delay = Math.max(0, Number(item.t_ms || 0) - first);
              replayTimers.push(setTimeout(() => {
                applyRecordedEvent(String(item.event), JSON.parse(String(item.payload || "{}")));
              }, delay));
            }
          });
      };
      loadCases();
    </script>
  </body>
</html>""".encode("utf-8")


def _sse_bytes(event_name: str, payload: EventPayload) -> bytes:
    body = json.dumps(payload, ensure_ascii=False)
    return f"event: {event_name}\ndata: {body}\n\n".encode("utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a streaming ASR web harness.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--chunk-frames", type=int, default=512)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--realtime", action="store_true")
    parser.add_argument(
        "--linear-gain",
        type=float,
        default=1.0,
        help="live 経路再現用のソフトウェアゲイン(media_graph --linear-gain 相当、飽和あり)",
    )
    parser.add_argument(
        "--partial-agreement-window",
        type=int,
        default=2,
        help="直近 N 個の partial が一致した接頭辞のみ stable_text にする (2 で従来動作)",
    )
    parser.add_argument(
        "--partial-hold-chars",
        type=int,
        default=0,
        help="一致した接頭辞の末尾 K 文字を unstable 側に留める (揺れやすい末尾の抑制)",
    )
    if add_nemotron_session_arguments is not None:
        add_nemotron_session_arguments(parser)
    return parser


def _build_httpd(host: str, port: int, harness: StreamingWebHarness) -> "StreamingHTTPServer":
    if not isinstance(port, int):
        raise TypeError("port must be int")

    class StreamingHTTPServer(ThreadingHTTPServer):
        allow_reuse_address: ClassVar[bool] = True

    class Handler(BaseHTTPRequestHandler):
        server: StreamingHTTPServer
        server_version = "StreamingWebHarness/1.0"
        error_content_type = "application/json"

        def _json(self, payload: JsonValue, status: int = 200) -> None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _events(self) -> None:
            listener = harness.register_listener()
            try:
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.end_headers()
                self.wfile.write(_sse_bytes("status", harness.status()))
                self.wfile.flush()
                while True:
                    event_name, payload = listener.get()
                    self.wfile.write(_sse_bytes(event_name, payload))
                    self.wfile.flush()
                    if event_name in {"done", "error"}:
                        break
            except (BrokenPipeError, ConnectionError):
                return
            finally:
                harness.unregister_listener(listener)

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            if path == "/":
                data = _render_html()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            if path == "/events":
                self._events()
                return
            if path == "/status":
                self._json(harness.status(), 200)
                return
            if path == "/cases":
                self._json(harness.case_summaries(), 200)
                return
            if path == "/history":
                self._json(harness.history(), 200)
                return
            self.send_error(404, "not found")

        def _read_run_case_id(self) -> str | None:
            content_length = self.headers.get("Content-Length")
            if content_length is None:
                return None
            try:
                length = int(content_length)
            except ValueError as exc:
                raise ValueError("Content-Length must be an integer") from exc
            if length < 0 or length > 4096:
                raise ValueError("request body length must be between 0 and 4096 bytes")
            if length == 0:
                return None
            try:
                body = json.loads(self.rfile.read(length).decode("utf-8"))
            except UnicodeDecodeError as exc:
                raise ValueError("request body must be UTF-8 JSON") from exc
            except json.JSONDecodeError as exc:
                raise ValueError(f"request body JSON is invalid: {exc.msg}") from exc
            if not isinstance(body, dict):
                raise ValueError("request body must be a JSON object")
            for key in body:
                if key not in {"case_id", "case"}:
                    raise ValueError(f"unsupported request field: {key}")
            raw_case_id = body.get("case_id", body.get("case"))
            if raw_case_id is None:
                return None
            if not isinstance(raw_case_id, str):
                raise ValueError("case_id must be a string")
            if raw_case_id == "":
                raise ValueError("case_id must be non-empty")
            return raw_case_id

        def do_POST(self) -> None:
            path = urlparse(self.path).path
            if path == "/run":
                try:
                    case_id = self._read_run_case_id()
                except ValueError as exc:
                    self._json({"ok": False, "error": str(exc)}, 400)
                    return
                if case_id is not None and not harness.has_case(case_id):
                    self._json({"ok": False, "error": f"unknown case_id: {case_id}"}, 400)
                    return
                started = harness.start(case_id=case_id)
                if not started:
                    self._json({"ok": False, "status": harness.status(), "state": harness.state}, 409)
                    return
                self._json({"ok": True, "status": harness.status()}, 200)
                return
            if path == "/stop":
                if harness.state not in {"running", "stopping"}:
                    self._json({"ok": False, "status": harness.status(), "state": harness.state}, 200)
                    return
                harness.request_stop()
                self._json({"ok": True, "status": harness.status()}, 200)
                return
            self.send_error(404, "not found")

        def log_message(self, format: str, *args) -> None:
            return

    return StreamingHTTPServer((host, port), Handler)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.limit is not None and args.limit <= 0:
        raise SystemExit("--limit must be positive")
    if args.partial_agreement_window < 2:
        raise SystemExit("--partial-agreement-window must be >= 2")
    if args.partial_hold_chars < 0:
        raise SystemExit("--partial-hold-chars must be >= 0")

    if nemotron_session_factory_from_args is None:
        raise SystemExit("nemotron_streaming_adapter が見つからず、起動できません")
    session_factory = nemotron_session_factory_from_args(args)  # type: ignore[operator]
    harness = StreamingWebHarness(
        manifest_path=args.manifest,
        target_lang=args.target_lang,
        case_id="ja" if args.target_lang.startswith("ja") else "current",
        case_label="Japanese corpus probe" if args.target_lang.startswith("ja") else None,
        chunk_frames=args.chunk_frames,
        limit=args.limit,
        realtime=args.realtime,
        linear_gain=args.linear_gain,
        partial_agreement_window=args.partial_agreement_window,
        partial_hold_chars=args.partial_hold_chars,
        session_factory=session_factory,
        probe_cases=_default_extra_probe_cases(),
    )
    harness.preload_asr_backend()
    httpd = _build_httpd(args.host, args.port, harness)
    print(f"listening on http://{args.host}:{httpd.server_address[1]}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("shutdown requested")
    finally:
        httpd.shutdown()
        httpd.server_close()


if __name__ == "__main__":
    main()
