import io
import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from fluent_dialogue_dora.contracts import TurnEvent
from tools.asr_eval import streaming_web_harness


@dataclass(frozen=True)
class _FakePartial:
    text: str
    seq: int
    chunk_index: int
    sample_index: int
    elapsed_audio_s: float = 0.0
    push_wall_s: float = 0.0


@dataclass(frozen=True)
class _FakeFinal:
    text: str
    sample_count: int
    stop_wall_s: float = 0.0


class _FakeSession:
    def __init__(self, utt_id: str, samples) -> None:
        self.utt_id = utt_id
        self.samples = samples
        self.started = False

    def start(self) -> None:
        self.started = True

    def push_audio(self, samples, *, sample_index: int, chunk_index: int):
        assert self.started
        return (
            _FakePartial(
                text=f"partial-{self.utt_id}-{chunk_index}",
                seq=chunk_index,
                chunk_index=chunk_index,
                sample_index=sample_index + len(samples),
            ),
        )

    def stop(self, *, sample_count: int):
        return _FakeFinal(text=f"final-{self.utt_id}", sample_count=sample_count)

    def cancel(self, *, reason: str) -> None:
        return None


class _FakeFactory:
    def __init__(self, samples_by_id: dict[str, list[float]]) -> None:
        self._samples_by_id = samples_by_id
        self.target_langs: list[str] = []

    def create(self, utterance_id: str) -> _FakeSession:
        return _FakeSession(utterance_id, self._samples_by_id[utterance_id])

    def set_target_lang(self, target_lang: str) -> None:
        self.target_langs.append(target_lang)


class _LoadableFakeFactory(_FakeFactory):
    def __init__(self, samples_by_id: dict[str, list[float]]) -> None:
        super().__init__(samples_by_id)
        self.loaded = False

    def load_backend(self) -> None:
        self.loaded = True

    def create(self, utterance_id: str) -> _FakeSession:
        assert self.loaded
        return super().create(utterance_id)


class _FakeStreamingTurnDetector:
    def __init__(self, **kwargs) -> None:
        self._sample_index = 0

    def push(self, samples):
        start = self._sample_index
        self._sample_index += len(samples)
        if start == 0:
            return [
                TurnEvent(
                    session_id="asr-eval",
                    user_turn_id="u1-turn-000001",
                    stream_id="turn/main",
                    seq=0,
                    sample_index=0,
                    state="started",
                )
            ]
        if start == 4:
            return [
                TurnEvent(
                    session_id="asr-eval",
                    user_turn_id="u1-turn-000001",
                    stream_id="turn/main",
                    seq=1,
                    sample_index=4,
                    state="ended",
                    confidence=0.9,
                )
            ]
        return []

    def finish(self, final_sample_index: int):
        return []


def _read_events(base_url: str, events: list[tuple[str, dict]]) -> None:
    with urlopen(base_url + "/events", timeout=5.0) as response:
        body = io.TextIOWrapper(response, encoding="utf-8")
        event_name: str | None = None
        data_line: str = ""
        while True:
            line = body.readline()
            if not line:
                return
            if line == "\n":
                if event_name is not None:
                    events.append((event_name, json.loads(data_line)))
                    if event_name in {"done", "error"}:
                        return
                event_name = None
                data_line = ""
                continue
            if line.startswith("event:"):
                event_name = line[6:].strip()
            elif line.startswith("data:"):
                data_line = line[5:].strip()


def _run_server(harness: streaming_web_harness.StreamingWebHarness) -> tuple[object, threading.Thread, int]:
    server = streaming_web_harness._build_httpd("127.0.0.1", 0, harness)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, server.server_address[1]


def _post_run(base_url: str, payload: dict[str, str] | None = None) -> None:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(base_url + "/run", data=data, headers=headers, method="POST")
    with urlopen(request, timeout=5.0):
        pass


def test_reference_char_index_tracks_audio_position() -> None:
    assert streaming_web_harness._reference_char_index(
        "おはようございます。",
        sample_index=0,
        sample_count=16000,
    ) == 0
    assert streaming_web_harness._reference_char_index(
        "おはようございます。",
        sample_index=8000,
        sample_count=16000,
    ) == 5
    assert streaming_web_harness._reference_char_index(
        "おはようございます。",
        sample_index=16000,
        sample_count=16000,
    ) == 10


def test_partial_stabilizer_exposes_repeated_prefix_only() -> None:
    stabilizer = streaming_web_harness.PartialStabilizer()

    assert stabilizer.update("資料で") == ("", "資料で")
    assert stabilizer.update("資料をま") == ("資料", "をま")
    assert stabilizer.update("資料をまとめ") == ("資料をま", "とめ")


def test_partial_stabilizer_agreement_window_and_hold_chars() -> None:
    windowed = streaming_web_harness.PartialStabilizer(agreement_window=3)
    assert windowed.update("資料で") == ("", "資料で")
    assert windowed.update("資料をま") == ("", "資料をま")
    assert windowed.update("資料をまとめ") == ("資料", "をまとめ")

    held = streaming_web_harness.PartialStabilizer(hold_chars=2)
    assert held.update("資料をま") == ("", "資料をま")
    assert held.update("資料をまとめ") == ("資料", "をまとめ")


def test_partial_stabilizer_counts_revisions_and_retreats() -> None:
    stabilizer = streaming_web_harness.PartialStabilizer()
    stabilizer.update("資料をまとめ")
    stabilizer.update("資料をまとめて")
    assert stabilizer.revision_count == 0
    assert stabilizer.stable_retreat_count == 0

    stabilizer.update("試料をまとめて")
    assert stabilizer.revision_count == 1
    assert stabilizer.stable_retreat_count == 1


def test_utterance_partial_tracker_summary() -> None:
    tracker = streaming_web_harness.UtterancePartialTracker()
    tracker.observe_push(0.010)
    tracker.observe_push(0.030)
    tracker.update_partial("こんにち", elapsed_audio_s=0.5)
    tracker.update_partial("こんにちは", elapsed_audio_s=1.0)
    summary = tracker.summary(final_text="こんにちは", stop_wall_s=0.1, audio_duration_s=2.0)

    assert summary["partial_count"] == 2
    assert summary["revision_count"] == 0
    assert summary["stable_retreat_count"] == 0
    assert summary["first_partial_elapsed_audio_s"] == 0.5
    assert round(summary["mean_push_wall_ms"]) == 20
    assert round(summary["max_push_wall_ms"]) == 30
    assert summary["push_rtf"] == (0.010 + 0.030) / 2.0
    assert summary["stop_wall_ms"] == 100.0
    assert summary["final_chars"] == 5
    assert summary["final_matches_last_partial"] is True


def test_confidence_weighted_silence_frames() -> None:
    assert streaming_web_harness._confidence_weighted_silence_frames(22_400, 0.8) == 4_480
    assert (
        streaming_web_harness._confidence_weighted_silence_frames(
            22_400,
            0.98,
            min_silence_frames=7_200,
        )
        == 7_200
    )
    assert streaming_web_harness._confidence_weighted_silence_frames(22_400, 1.2) == 0
    assert streaming_web_harness._confidence_weighted_silence_frames(22_400, -1.0) == 22_400


def test_harness_preloads_asr_before_run(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.jsonl"
    manifest_path.write_text(
        json.dumps({"id": "u1", "group": "g", "text": "hello", "wav": str(tmp_path / "a.wav")})
        + "\n",
        encoding="utf-8",
    )
    factory = _LoadableFakeFactory({"u1": [0.0]})
    harness = streaming_web_harness.StreamingWebHarness(
        manifest_path=manifest_path,
        target_lang="ja-JP",
        session_factory=factory,
    )

    assert harness.status()["asr_ready"] is False
    assert harness.start() is False

    harness.preload_asr_backend()
    deadline = time.monotonic() + 5.0
    while not harness.status()["asr_ready"] and time.monotonic() < deadline:
        time.sleep(0.01)

    assert factory.loaded is True
    assert harness.status()["can_run"] is True


def test_streaming_web_harness_sse_emits_status_partial_final(tmp_path: Path, monkeypatch) -> None:
    manifest_path = tmp_path / "manifest.jsonl"
    wav_a = tmp_path / "a.wav"
    wav_b = tmp_path / "b.wav"
    wav_a.write_bytes(b"")
    wav_b.write_bytes(b"")
    manifest_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "id": "u1",
                        "group": "g",
                        "text": "hello",
                        "wav": str(wav_a),
                    }
                ),
                json.dumps(
                    {
                        "id": "u2",
                        "group": "g",
                        "text": "world",
                        "wav": str(wav_b),
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    samples_by_id = {"u1": [0.0, 0.1, 0.2], "u2": [0.3, 0.4]}
    samples_by_wav = {"a.wav": "u1", "b.wav": "u2"}
    def _fake_load_wav(wav_path, linear_gain=1.0):
        return samples_by_id[samples_by_wav[Path(wav_path).name]]

    monkeypatch.setattr(streaming_web_harness, "load_wav_as_16k_f32", _fake_load_wav)

    harness = streaming_web_harness.StreamingWebHarness(
        manifest_path=manifest_path,
        target_lang="ja-JP",
        chunk_frames=2,
        session_factory=_FakeFactory(samples_by_id),
    )
    server, server_thread, port = _run_server(harness)

    events: list[tuple[str, dict]] = []
    reader_thread = threading.Thread(
        target=_read_events,
        args=(f"http://127.0.0.1:{port}", events),
        daemon=True,
    )
    reader_thread.start()
    deadline = time.monotonic() + 5.0
    while not events and time.monotonic() < deadline:
        time.sleep(0.01)
    _post_run(f"http://127.0.0.1:{port}")
    reader_thread.join(timeout=5.0)
    with urlopen(f"http://127.0.0.1:{port}/status", timeout=5.0) as response:
        status = json.load(io.TextIOWrapper(response, encoding="utf-8"))
    assert status["state"] == "done"
    with urlopen(f"http://127.0.0.1:{port}/history", timeout=5.0) as response:
        history = json.load(io.TextIOWrapper(response, encoding="utf-8"))
    server.shutdown()
    server.server_close()
    server_thread.join(timeout=5.0)

    event_types = [name for name, _ in events]
    assert "status" in event_types
    assert "utterance_start" in event_types
    assert "audio_progress" in event_types
    assert "partial" in event_types
    assert "final" in event_types
    assert "utterance_done" in event_types
    assert "done" in event_types
    partial_payloads = [payload for name, payload in events if name == "partial"]
    assert all("stable_text" in payload for payload in partial_payloads)
    assert any(payload["stable_text"] == "partial-u1-" for payload in partial_payloads)
    metrics_payloads = [payload for name, payload in events if name == "utterance_metrics"]
    assert [payload["id"] for payload in metrics_payloads] == ["u1", "u2"]
    assert metrics_payloads[0]["partial_count"] == 2
    assert metrics_payloads[0]["revision_count"] == 1
    assert metrics_payloads[0]["first_partial_elapsed_audio_s"] > 0.0
    assert any(item["event"] == "audio_progress" for item in history)


def test_streaming_web_harness_selects_probe_case_with_validated_body(
    tmp_path: Path,
    monkeypatch,
) -> None:
    ja_manifest = tmp_path / "ja.jsonl"
    en_manifest = tmp_path / "en.jsonl"
    ja_wav = tmp_path / "ja.wav"
    en_wav = tmp_path / "en.wav"
    ja_wav.write_bytes(b"")
    en_wav.write_bytes(b"")
    ja_manifest.write_text(
        json.dumps({"id": "ja1", "group": "ja", "text": "こんにちは", "wav": str(ja_wav)}) + "\n",
        encoding="utf-8",
    )
    en_manifest.write_text(
        json.dumps({"id": "en1", "group": "en", "text": "hello", "wav": str(en_wav)}) + "\n",
        encoding="utf-8",
    )

    samples_by_id = {"ja1": [0.0], "en1": [0.0, 0.1]}
    samples_by_wav = {"ja.wav": "ja1", "en.wav": "en1"}

    def _fake_load_wav(wav_path, linear_gain=1.0):
        return samples_by_id[samples_by_wav[Path(wav_path).name]]

    monkeypatch.setattr(streaming_web_harness, "load_wav_as_16k_f32", _fake_load_wav)

    factory = _FakeFactory(samples_by_id)
    harness = streaming_web_harness.StreamingWebHarness(
        manifest_path=ja_manifest,
        target_lang="ja-JP",
        case_id="ja",
        case_label="Japanese",
        chunk_frames=2,
        session_factory=factory,
        probe_cases=(
            streaming_web_harness.ProbeCase(
                id="en",
                label="English",
                manifest_path=en_manifest,
                target_lang="en-US",
                limit=1,
            ),
        ),
    )
    server, server_thread, port = _run_server(harness)
    base_url = f"http://127.0.0.1:{port}"

    with urlopen(base_url + "/cases", timeout=5.0) as response:
        cases = json.load(io.TextIOWrapper(response, encoding="utf-8"))
    assert [case["id"] for case in cases] == ["ja", "en"]

    events: list[tuple[str, dict]] = []
    reader_thread = threading.Thread(target=_read_events, args=(base_url, events), daemon=True)
    reader_thread.start()
    deadline = time.monotonic() + 5.0
    while not events and time.monotonic() < deadline:
        time.sleep(0.01)
    _post_run(base_url, {"case_id": "en"})
    reader_thread.join(timeout=5.0)

    with urlopen(base_url + "/status", timeout=5.0) as response:
        status = json.load(io.TextIOWrapper(response, encoding="utf-8"))
    server.shutdown()
    server.server_close()
    server_thread.join(timeout=5.0)

    assert status["case_id"] == "en"
    assert status["target_lang"] == "en-US"
    assert status["manifest"] == str(en_manifest)
    assert factory.target_langs == ["en-US"]
    assert any(payload.get("id") == "en1" for name, payload in events if name == "final")


def test_streaming_web_harness_can_split_entry_with_turn_detector(
    tmp_path: Path,
    monkeypatch,
) -> None:
    manifest_path = tmp_path / "manifest.jsonl"
    wav_path = tmp_path / "a.wav"
    wav_path.write_bytes(b"")
    manifest_path.write_text(
        json.dumps({"id": "u1", "group": "g", "text": "hello world", "wav": str(wav_path)})
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(streaming_web_harness, "load_wav_as_16k_f32", lambda *_args, **_kwargs: [0.0] * 6)
    monkeypatch.setattr(streaming_web_harness, "StreamingTurnDetector", _FakeStreamingTurnDetector)

    harness = streaming_web_harness.StreamingWebHarness(
        manifest_path=manifest_path,
        target_lang="ja-JP",
        case_id="base",
        chunk_frames=2,
        session_factory=_FakeFactory({"u1-turn-000001": [0.0] * 6}),
        probe_cases=(
            streaming_web_harness.ProbeCase(
                id="td",
                label="Turn detected",
                manifest_path=manifest_path,
                target_lang="ja-JP",
                limit=1,
                turn_detection=True,
                smart_turn_model_path=tmp_path / "smart-turn.onnx",
            ),
        ),
    )
    server, server_thread, port = _run_server(harness)
    base_url = f"http://127.0.0.1:{port}"

    events: list[tuple[str, dict]] = []
    reader_thread = threading.Thread(target=_read_events, args=(base_url, events), daemon=True)
    reader_thread.start()
    deadline = time.monotonic() + 5.0
    while not events and time.monotonic() < deadline:
        time.sleep(0.01)
    _post_run(base_url, {"case_id": "td"})
    reader_thread.join(timeout=5.0)

    with urlopen(base_url + "/status", timeout=5.0) as response:
        status = json.load(io.TextIOWrapper(response, encoding="utf-8"))
    server.shutdown()
    server.server_close()
    server_thread.join(timeout=5.0)

    finals = [payload for name, payload in events if name == "final"]
    turns = [payload for name, payload in events if name == "turn"]
    assert status["case_id"] == "td"
    assert status["turn_detection"] is True
    assert [payload["state"] for payload in turns] == ["started", "ended"]
    assert finals[0]["id"] == "u1-turn-000001"
    assert finals[0]["sample_count"] == 6


def test_streaming_web_harness_rejects_unknown_probe_case(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.jsonl"
    wav_path = tmp_path / "a.wav"
    wav_path.write_bytes(b"")
    manifest_path.write_text(
        json.dumps({"id": "u1", "group": "g", "text": "hello", "wav": str(wav_path)}) + "\n",
        encoding="utf-8",
    )
    harness = streaming_web_harness.StreamingWebHarness(
        manifest_path=manifest_path,
        target_lang="ja-JP",
        session_factory=_FakeFactory({"u1": [0.0]}),
    )
    server, server_thread, port = _run_server(harness)

    try:
        _post_run(f"http://127.0.0.1:{port}", {"case_id": "missing"})
    except HTTPError as exc:
        assert exc.code == 400
    else:
        raise AssertionError("unknown case_id should be rejected")
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=5.0)
