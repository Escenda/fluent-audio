import pytest
from pydantic import ValidationError

import nodes.asr.nemotron_streaming.backend as backend_module
from nodes.asr.nemotron_streaming.backend import (
    DEFAULT_NEMOTRON_MODEL_NAME,
    NemotronBackendSettings,
    NemotronBackendUnavailableError,
    _append_only_delta,
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
    assert settings.target_lang == "auto"
    assert settings.strip_lang_tags is True
    assert settings.att_context_size == (56, 3)
    assert settings.chunk_duration_ms == 320
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


def test_append_only_delta_emits_only_confirmed_suffix() -> None:
    emitted, delta = _append_only_delta(emitted_text="", hypothesis_text="The")
    assert emitted == "The"
    assert delta == "The"

    emitted, delta = _append_only_delta(
        emitted_text=emitted,
        hypothesis_text="The stales",
    )
    assert emitted == "The stales"
    assert delta == " stales"

    emitted, delta = _append_only_delta(
        emitted_text=emitted,
        hypothesis_text="These tales",
    )
    assert emitted == "The stales"
    assert delta is None


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
