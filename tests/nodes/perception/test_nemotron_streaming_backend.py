import pytest
from pydantic import ValidationError

from nodes.perception.nemotron_streaming.backend import (
    DEFAULT_NEMOTRON_MODEL_NAME,
    NemotronBackendSettings,
    NemotronBackendUnavailableError,
    build_nemotron_backend,
)
from nodes.perception.nemotron_streaming.main import (
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


def test_backend_builder_fails_closed_until_nemo_runtime_is_wired() -> None:
    settings = NemotronBackendSettings(
        backend="nemo",
        model_name="nvidia/nemotron-3.5-asr-streaming-0.6b",
    )

    with pytest.raises(NemotronBackendUnavailableError, match="not implemented"):
        build_nemotron_backend(settings)


def test_cli_requires_explicit_backend() -> None:
    with pytest.raises(SystemExit):
        main(BASE_ARGV)


def test_cli_validates_backend_settings_before_dora_node_creation() -> None:
    with pytest.raises(NemotronStreamingNodeError, match="NeMo backend is configured"):
        main([*BASE_ARGV, "--backend", "nemo"])


def test_backend_settings_from_cli_can_keep_language_tags() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [*BASE_ARGV, "--backend", "nemo", "--target-lang", "ja-JP", "--keep-lang-tags"]
    )
    settings = _backend_settings_from_args(args)

    assert settings.target_lang == "ja-JP"
    assert settings.strip_lang_tags is False
