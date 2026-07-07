from pathlib import Path

import pytest

from scripts.download_models import (
    DEFAULT_NEMOTRON_REPO_ID,
    DownloadError,
    HfModelInfo,
    HfSibling,
    auth_header,
    default_nemotron_path,
    hf_resolve_url,
    normalize_targets,
    repo_leaf,
    select_nemo_file_from_info,
)


def test_default_nemotron_path_matches_runtime_scripts() -> None:
    assert default_nemotron_path(Path("data/models/fluent_dialogue_dora")) == Path(
        "data/models/fluent_dialogue_dora/"
        "nemotron-3.5-asr-streaming-0.6b/"
        "nemotron-3.5-asr-streaming-0.6b.nemo"
    )


def test_select_nemotron_nemo_file_prefers_expected_name() -> None:
    info = HfModelInfo(
        siblings=(
            HfSibling(rfilename="other.nemo"),
            HfSibling(rfilename="nemotron-3.5-asr-streaming-0.6b.nemo"),
        )
    )

    assert (
        select_nemo_file_from_info(DEFAULT_NEMOTRON_REPO_ID, info)
        == "nemotron-3.5-asr-streaming-0.6b.nemo"
    )


def test_select_nemo_file_rejects_ambiguous_repo() -> None:
    info = HfModelInfo(siblings=(HfSibling(rfilename="a.nemo"), HfSibling(rfilename="b.nemo")))

    with pytest.raises(DownloadError):
        select_nemo_file_from_info("owner/model", info)


def test_hf_helpers_encode_paths_and_token() -> None:
    assert hf_resolve_url("owner/model name", "dir/model file.nemo") == (
        "https://huggingface.co/owner/model%20name/resolve/main/dir/model%20file.nemo"
    )
    assert auth_header("token") == {"Authorization": "Bearer token"}
    assert auth_header(None) == {}


def test_targets_and_repo_leaf() -> None:
    assert normalize_targets(None) == frozenset(("nemotron", "kokoro", "llm"))
    assert normalize_targets(("all",)) == frozenset(("nemotron", "kokoro", "llm"))
    assert normalize_targets(("kokoro", "llm")) == frozenset(("kokoro", "llm"))
    assert repo_leaf("owner/model-name") == "model-name"
