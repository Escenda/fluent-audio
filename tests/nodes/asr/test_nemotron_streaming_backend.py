from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest
from pydantic import ValidationError

from fluent_audio.contracts import AsrStop
import nodes.asr.nemotron_streaming.backend as backend_module
from nodes.asr.nemotron_streaming.backend import (
    DEFAULT_NEMOTRON_MODEL_NAME,
    NemoCacheAwareStreamingBackend,
    NemotronBackendError,
    NemotronBackendSettings,
    NemotronBackendUnavailableError,
    _native_stream_chunk_sample_count,
    _prepare_nemo_extracted_dir,
    _strip_lang_tag,
    build_nemotron_backend,
)
from nodes.asr.nemotron_streaming.main import (
    NemotronStreamingNodeError,
    _backend_settings_from_args,
    build_parser,
    main,
)

BASE_ARGV = [
    "--dora",
    "--input-audio-source-id",
    "media_graph",
    "--input-audio-stream-id",
    "audio/asr/input",
    "--session-id",
    "session-1",
    "--output-stream-id",
    "transcript/main",
]


def test_backend_settings_preserve_nemotron_defaults() -> None:
    settings = NemotronBackendSettings(backend="nemo")

    assert settings.model_name == DEFAULT_NEMOTRON_MODEL_NAME
    assert settings.model_extracted_dir is None
    assert settings.target_lang == "auto"
    assert settings.strip_lang_tags is True
    assert settings.att_context_size == (56, 3)
    assert settings.chunk_duration_ms == 320
    assert settings.partial_update_interval_ms == 320
    assert settings.partial_agreement_steps == 1
    assert settings.partial_holdback_chars == 0
    assert settings.final_transcript_mode == "retranscribe"
    assert settings.compute_dtype == "float32"
    assert settings.cuda_device is None


def test_backend_settings_reject_unknown_lookahead() -> None:
    with pytest.raises(ValidationError, match="att_context_right_frames"):
        NemotronBackendSettings(backend="nemo", att_context_right_frames=2)


def test_backend_builder_fails_closed_when_nemo_runtime_is_absent(monkeypatch) -> None:
    settings = NemotronBackendSettings(
        backend="nemo",
        model_name="nvidia/nemotron-3.5-asr-streaming-0.6b",
    )
    monkeypatch.setattr(
        backend_module,
        "_missing_runtime_modules",
        lambda: ("nemo.collections.asr.models",),
    )

    with pytest.raises(NemotronBackendUnavailableError, match="not installed"):
        build_nemotron_backend(settings)


def test_backend_builder_constructs_nemo_backend(monkeypatch) -> None:
    class FakeBackend:
        def __init__(self, settings: NemotronBackendSettings) -> None:
            self.settings = settings

    settings = NemotronBackendSettings(
        backend="nemo",
        model_name="/tmp/model.nemo",
    )
    monkeypatch.setattr(backend_module, "NemoCacheAwareStreamingBackend", FakeBackend)

    backend = build_nemotron_backend(settings)

    assert isinstance(backend, FakeBackend)
    assert backend.settings == settings


def test_strip_lang_tag_removes_terminal_language_prompt_tag() -> None:
    assert _strip_lang_tag("Hello world. <en-US>") == "Hello world."
    assert _strip_lang_tag("こんにちは。 <ja-JP>") == "こんにちは。"


def test_cli_requires_explicit_backend() -> None:
    with pytest.raises(SystemExit):
        main(BASE_ARGV)


def test_cli_reports_backend_construction_errors_before_dora_node_creation(monkeypatch) -> None:
    def raise_backend_error(settings: NemotronBackendSettings):
        raise NemotronBackendUnavailableError("runtime missing")

    monkeypatch.setattr(
        "nodes.asr.nemotron_streaming.main.build_nemotron_backend",
        raise_backend_error,
    )

    with pytest.raises(NemotronStreamingNodeError, match="runtime missing"):
        main([*BASE_ARGV, "--backend", "nemo"])


def test_backend_settings_from_cli_can_keep_language_tags() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [*BASE_ARGV, "--backend", "nemo", "--target-lang", "ja-JP", "--keep-lang-tags"]
    )
    settings = _backend_settings_from_args(args)

    assert settings.target_lang == "ja-JP"
    assert settings.strip_lang_tags is False


def test_backend_settings_from_cli_can_set_extracted_model_dir(tmp_path) -> None:
    parser = build_parser()
    extracted_dir = tmp_path / "nemotron-extracted"
    args = parser.parse_args(
        [
            *BASE_ARGV,
            "--backend",
            "nemo",
            "--model-extracted-dir",
            str(extracted_dir),
        ]
    )
    settings = _backend_settings_from_args(args)

    assert settings.model_extracted_dir == extracted_dir


def test_backend_settings_from_cli_can_set_streaming_tuning() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            *BASE_ARGV,
            "--backend",
            "nemo",
            "--att-context-right-frames",
            "13",
            "--partial-agreement-steps",
            "2",
            "--partial-holdback-chars",
            "1",
            "--final-transcript-mode",
            "streaming",
        ]
    )
    settings = _backend_settings_from_args(args)

    assert settings.att_context_right_frames == 13
    assert settings.partial_agreement_steps == 2
    assert settings.partial_holdback_chars == 1
    assert settings.final_transcript_mode == "streaming"


def test_prepare_nemo_extracted_dir_unpacks_empty_cache(tmp_path) -> None:
    nemo_path = tmp_path / "model.nemo"
    nemo_path.write_bytes(b"fake")
    extracted_dir = tmp_path / "extracted"

    class FakeConnector:
        @staticmethod
        def _unpack_nemo_file(path2file: str, out_folder: str) -> None:
            assert path2file == str(nemo_path)
            Path(out_folder, "model_config.yaml").write_text("model: {}\n", encoding="utf-8")
            Path(out_folder, "model_weights.ckpt").write_bytes(b"weights")

    assert _prepare_nemo_extracted_dir(nemo_path, extracted_dir, FakeConnector) == extracted_dir


def test_prepare_nemo_extracted_dir_rejects_incomplete_nonempty_cache(tmp_path) -> None:
    nemo_path = tmp_path / "model.nemo"
    nemo_path.write_bytes(b"fake")
    extracted_dir = tmp_path / "extracted"
    extracted_dir.mkdir()
    (extracted_dir / "model_config.yaml").write_text("model: {}\n", encoding="utf-8")

    class FakeConnector:
        @staticmethod
        def _unpack_nemo_file(path2file: str, out_folder: str) -> None:
            raise AssertionError("should not overwrite incomplete cache")

    with pytest.raises(NemotronBackendError, match="incomplete"):
        _prepare_nemo_extracted_dir(nemo_path, extracted_dir, FakeConnector)


def test_nemo_backend_reuses_previous_pred_out_between_stream_steps() -> None:
    @dataclass(frozen=True)
    class FakeConformerCall:
        previous_pred_out: str | None
        drop_extra_pre_encoded: int

    class FakeInferenceMode:
        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeTorch:
        @staticmethod
        def inference_mode():
            return FakeInferenceMode()

    class FakeEncoder:
        class streaming_cfg:
            drop_extra_pre_encoded = 99

    class FakeHypothesis:
        def __init__(self, text: str) -> None:
            self.text = text

    class FakeModel:
        def __init__(self) -> None:
            self.encoder = FakeEncoder()
            self.calls: list[FakeConformerCall] = []

        def conformer_stream_step(
            self,
            *,
            processed_signal: str,
            processed_signal_length: str,
            cache_last_channel: str,
            cache_last_time: str,
            cache_last_channel_len: str,
            keep_all_outputs: bool,
            previous_hypotheses: str | None,
            previous_pred_out: str | None,
            drop_extra_pre_encoded: int,
            return_transcription: bool,
            return_log_probs: bool,
        ):
            call_index = len(self.calls)
            self.calls.append(
                FakeConformerCall(
                    previous_pred_out=previous_pred_out,
                    drop_extra_pre_encoded=drop_extra_pre_encoded,
                )
            )
            return (
                f"pred-{call_index}",
                [FakeHypothesis(f"text-{call_index}")],
                f"cache-channel-{call_index}",
                f"cache-time-{call_index}",
                f"cache-len-{call_index}",
                f"hyp-{call_index}",
            )

    class FakeStreamingBuffer:
        def __init__(self) -> None:
            self._items = [("audio-0", "len-0"), ("audio-1", "len-1")]
            self._cursor = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self._cursor >= len(self._items):
                raise StopIteration
            item = self._items[self._cursor]
            self._cursor += 1
            return item

        def is_buffer_empty(self) -> bool:
            return self._cursor >= len(self._items)

    settings = NemotronBackendSettings(backend="nemo")
    model = FakeModel()
    backend = NemoCacheAwareStreamingBackend.__new__(NemoCacheAwareStreamingBackend)
    backend._settings = settings
    backend._model = model
    backend._torch = FakeTorch()
    backend._streaming_buffer = FakeStreamingBuffer()
    backend._cache_last_channel = "initial-channel"
    backend._cache_last_time = "initial-time"
    backend._cache_last_channel_len = "initial-len"
    backend._previous_hypotheses = None
    backend._previous_pred_out = None
    backend._partial_filter = backend_module._ReplacementPartialFilter(
        agreement_steps=1,
        holdback_chars=0,
    )
    backend._latest_stream_text = ""
    backend._stream_step_index = 0

    assert backend._consume_available_stream_updates() == ("text-0", "text-1")
    assert model.calls[0].previous_pred_out is None
    assert model.calls[1].previous_pred_out == "pred-0"
    assert model.calls[0].drop_extra_pre_encoded == 0
    assert model.calls[1].drop_extra_pre_encoded == 99


def test_nemo_backend_buffers_raw_audio_until_native_chunk_size() -> None:
    backend = NemoCacheAwareStreamingBackend.__new__(NemoCacheAwareStreamingBackend)
    backend._np = np
    backend._stream_chunk_sample_count = 4
    backend._stream_step_index = 0
    backend._live_samples = np.empty(0, dtype=np.float32)
    appended: list[list[float]] = []

    def append_chunk(samples) -> None:
        appended.append(samples.tolist())

    backend._append_stream_audio_chunk = append_chunk
    backend._consume_available_stream_updates = lambda: (f"partial-{len(appended)}",)

    assert backend._append_stream_audio(np.array([1.0, 2.0], dtype=np.float32)) == ()
    assert appended == []

    assert backend._append_stream_audio(np.array([3.0, 4.0, 5.0], dtype=np.float32)) == (
        "partial-1",
    )
    assert appended == [[1.0, 2.0, 3.0, 4.0]]
    assert backend._live_samples.tolist() == [5.0]


def test_nemo_backend_feeds_prefix_consistent_features_with_edge_holdback() -> None:
    samples_per_frame = 4

    class FakeStreamingBuffer:
        def __init__(self) -> None:
            self.preprocess_lengths: list[int] = []
            self.appended: list[tuple[list[int], int]] = []

        def preprocess_audio(self, audio):
            self.preprocess_lengths.append(len(audio))
            total_frames = len(audio) // samples_per_frame
            processed = np.arange(total_frames, dtype=np.float32).reshape(1, 1, total_frames)
            return processed, total_frames

        def append_processed_signal(self, processed_signal, stream_id=-1):
            frames = processed_signal[0, 0, :].astype(int).tolist()
            self.appended.append((frames, stream_id))
            # Mimic NeMo: the first append (buffer creation) echoes stream_id -1.
            return processed_signal, processed_signal.shape[-1], stream_id

    buffer = FakeStreamingBuffer()
    backend = NemoCacheAwareStreamingBackend.__new__(NemoCacheAwareStreamingBackend)
    backend._np = np
    backend._streaming_buffer = buffer
    backend._streamed_samples = np.empty(0, dtype=np.float32)
    backend._appended_feature_frames = 0
    backend._stream_id = -1

    chunk = np.zeros(8, dtype=np.float32)

    # 2 frames total, both held back as STFT edge frames: nothing appended yet.
    backend._append_stream_audio_chunk(chunk)
    assert buffer.appended == []
    assert backend._stream_id == -1

    # 4 frames total: frames 0-1 become interior and are appended.
    backend._append_stream_audio_chunk(chunk)
    assert buffer.appended == [([0, 1], -1)]
    assert backend._stream_id == 0

    # 6 frames total: only the newly interior frames 2-3 are appended.
    backend._append_stream_audio_chunk(chunk)
    assert buffer.appended == [([0, 1], -1), ([2, 3], 0)]

    # Features are recomputed over the whole turn prefix every step.
    assert buffer.preprocess_lengths == [8, 16, 24]


def test_nemo_backend_streaming_final_mode_uses_latest_stream_text() -> None:
    settings = NemotronBackendSettings(backend="nemo", final_transcript_mode="streaming")
    backend = NemoCacheAwareStreamingBackend.__new__(NemoCacheAwareStreamingBackend)
    backend._settings = settings
    backend._active = True
    backend._pending_frame_count = 16
    backend._latest_stream_text = " streaming final "
    flushed = []

    def flush() -> None:
        flushed.append(True)

    backend._flush_streaming_residual = flush
    backend._reset_active_stream = lambda: None

    result = backend.stop(
        AsrStop(
            action="stop",
            session_id="session-1",
            user_turn_id="turn-1",
            stream_id="audio/asr/input",
            seq=1,
            stop_sample_index=16,
        )
    )

    assert result.text == "streaming final"
    assert flushed == [True]


def test_native_stream_chunk_sample_count_uses_second_streaming_chunk() -> None:
    class FakeStreamingCfg:
        chunk_size = [105, 112]

    class FakeEncoder:
        streaming_cfg = FakeStreamingCfg()

    class FakePreprocessor:
        sample_rate = 16000
        window_stride = 0.01

    class FakeCfg:
        preprocessor = FakePreprocessor()

    class FakeModel:
        encoder = FakeEncoder()
        cfg = FakeCfg()

    assert _native_stream_chunk_sample_count(FakeModel()) == 17920


def test_backend_partial_filter_agrees_and_dedupes_replacement_hypotheses() -> None:
    filter_ = backend_module._ReplacementPartialFilter(
        agreement_steps=2,
        holdback_chars=1,
    )

    assert filter_.update("資料で") is None
    assert filter_.update("資料をま") == "資料"
    assert filter_.update("資料をまとめ") == "資料を"
    assert filter_.update("資料をまとめ") == "資料をまと"
    assert filter_.update("資料をまとめ") is None
