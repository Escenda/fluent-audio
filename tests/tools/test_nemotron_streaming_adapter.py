import numpy as np
import pytest

import tools.asr_eval.nemotron_streaming_adapter as adapter_module
from fluent_dialogue_dora.contracts import AsrCancel, AsrStart, AsrStop, AudioChunk, AudioFormat
from nodes.asr.nemotron_streaming.logic import AsrBackendFinalResult, AsrBackendPushResult
from tools.asr_eval.nemotron_streaming_adapter import NemotronSessionFactory, NemotronStreamingSession


class FakeBackend:
    def __init__(self) -> None:
        self.started: list[tuple[AsrStart, AudioFormat]] = []
        self.chunks: list[AudioChunk] = []
        self.stopped: list[AsrStop] = []
        self.cancelled: list[AsrCancel] = []
        self.target_langs: list[str] = []

    def start(self, control: AsrStart, audio_format: AudioFormat) -> None:
        self.started.append((control, audio_format))

    def push_audio(self, chunk: AudioChunk) -> AsrBackendPushResult:
        self.chunks.append(chunk)
        return AsrBackendPushResult(partial_texts=(f"partial-{chunk.seq}",))

    def stop(self, control: AsrStop) -> AsrBackendFinalResult:
        self.stopped.append(control)
        return AsrBackendFinalResult(text="最終結果")

    def cancel(self, control: AsrCancel) -> None:
        self.cancelled.append(control)

    def set_target_lang(self, target_lang: str) -> None:
        self.target_langs.append(target_lang)


def test_nemotron_session_streams_chunks_and_final() -> None:
    backend = FakeBackend()
    session = NemotronStreamingSession(backend, utterance_id="utt-1")

    session.start()
    partials = session.push_audio(
        np.array([0.0, 0.25, -0.25], dtype=np.float32),
        sample_index=0,
        chunk_index=7,
    )
    final = session.stop(sample_count=3)

    assert backend.started[0][0].user_turn_id == "utt-1"
    assert backend.started[0][1].sample_format == "f32le"
    assert backend.chunks[0].seq == 7
    assert backend.chunks[0].frame_count == 3
    assert backend.chunks[0].payload == np.array([0.0, 0.25, -0.25], dtype="<f4").tobytes()
    assert partials[0].text == "partial-7"
    assert partials[0].sample_index == 3
    assert final.text == "最終結果"
    assert backend.stopped[0].stop_sample_index == 3


def test_nemotron_session_rejects_sample_index_gap() -> None:
    session = NemotronStreamingSession(FakeBackend(), utterance_id="utt-1")
    session.start()
    session.push_audio([0.0], sample_index=0, chunk_index=0)

    with pytest.raises(ValueError, match="sample_index discontinuity"):
        session.push_audio([0.0], sample_index=2, chunk_index=1)


def test_nemotron_session_factory_builds_backend_lazily(monkeypatch) -> None:
    built = []

    def fake_build(settings):
        built.append(settings)
        return FakeBackend()

    monkeypatch.setattr(adapter_module, "build_nemotron_backend", fake_build)

    factory = NemotronSessionFactory(model_name="/tmp/model.nemo")

    assert built == []
    assert isinstance(factory.create("utt-1"), NemotronStreamingSession)
    assert len(built) == 1


def test_nemotron_session_factory_can_preload_backend(monkeypatch) -> None:
    built = []

    def fake_build(settings):
        built.append(settings)
        return FakeBackend()

    monkeypatch.setattr(adapter_module, "build_nemotron_backend", fake_build)

    factory = NemotronSessionFactory(model_name="/tmp/model.nemo")
    factory.load_backend()
    factory.create("utt-1")

    assert len(built) == 1


def test_nemotron_session_factory_switches_target_lang_after_preload(monkeypatch) -> None:
    backend = FakeBackend()

    def fake_build(settings):
        return backend

    monkeypatch.setattr(adapter_module, "build_nemotron_backend", fake_build)

    factory = NemotronSessionFactory(model_name="/tmp/model.nemo", target_lang="ja-JP")
    factory.load_backend()
    factory.set_target_lang("en-US")

    assert backend.target_langs == ["en-US"]
