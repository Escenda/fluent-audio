#!/usr/bin/env python3
"""Download model artifacts used by local fluent-dialogue-dora runs."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_NEMOTRON_REPO_ID = "nvidia/nemotron-3.5-asr-streaming-0.6b"
DEFAULT_KOKORO_REPO_ID = "hexgrad/Kokoro-82M"
DEFAULT_LLM_REPO_ID = "sakamakismile/Qwen3.6-27B-MTP-pi-tune-NVFP4"
DEFAULT_MODEL_ROOT = Path("data/models/fluent_dialogue_dora")
CHUNK_BYTES = 8 * 1024 * 1024


class HfSibling(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    rfilename: str = Field(min_length=1)


class HfModelInfo(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    siblings: tuple[HfSibling, ...]


class DownloadError(RuntimeError):
    """Raised when a model artifact cannot be fetched safely."""


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    model_root = args.model_root.expanduser()
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    targets = normalize_targets(args.target)
    if "nemotron" in targets:
        output_path = args.output.expanduser() if args.output else default_nemotron_path(model_root)
        filename = args.filename or select_nemo_file(args.nemotron_repo_id, token)
        download(hf_resolve_url(args.nemotron_repo_id, filename), output_path, token=token, force=args.force)
        print(output_path)
    if "kokoro" in targets:
        output_dir = model_root / repo_leaf(args.kokoro_repo_id)
        download_snapshot(args.kokoro_repo_id, output_dir, token=token, force=args.force)
        print(output_dir)
    if "llm" in targets:
        output_dir = model_root / repo_leaf(args.llm_repo_id)
        download_snapshot(args.llm_repo_id, output_dir, token=token, force=args.force)
        print(output_dir)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Download local model weights.")
    parser.add_argument(
        "--target",
        action="append",
        choices=("all", "nemotron", "kokoro", "llm"),
        default=None,
    )
    parser.add_argument("--nemotron-repo-id", default=DEFAULT_NEMOTRON_REPO_ID)
    parser.add_argument("--kokoro-repo-id", default=DEFAULT_KOKORO_REPO_ID)
    parser.add_argument("--llm-repo-id", default=DEFAULT_LLM_REPO_ID)
    parser.add_argument("--repo-id", dest="nemotron_repo_id", help=argparse.SUPPRESS)
    parser.add_argument("--filename", help="Nemotron .nemo repo file to download")
    parser.add_argument("--model-root", type=Path, default=DEFAULT_MODEL_ROOT)
    parser.add_argument("--output", type=Path, help="Nemotron .nemo output path")
    parser.add_argument("--force", action="store_true")
    return parser


def normalize_targets(targets: Sequence[str] | None) -> frozenset[str]:
    selected = set(targets or ("all",))
    if "all" in selected:
        return frozenset(("nemotron", "kokoro", "llm"))
    return frozenset(selected)


def default_nemotron_path(model_root: Path) -> Path:
    model_name = DEFAULT_NEMOTRON_REPO_ID.rsplit("/", 1)[1]
    return model_root / model_name / f"{model_name}.nemo"


def repo_leaf(repo_id: str) -> str:
    leaf = repo_id.rstrip("/").rsplit("/", 1)[-1]
    if not leaf or leaf in (".", ".."):
        raise DownloadError(f"invalid Hugging Face repo id: {repo_id!r}")
    return leaf


def select_nemo_file(repo_id: str, token: str | None) -> str:
    return select_nemo_file_from_info(repo_id, fetch_hf_model_info(repo_id, token))


def select_nemo_file_from_info(repo_id: str, info: HfModelInfo) -> str:
    candidates = sorted(
        sibling.rfilename for sibling in info.siblings if sibling.rfilename.endswith(".nemo")
    )
    if not candidates:
        raise DownloadError(f"Hugging Face repo has no .nemo file: {repo_id}")
    expected_name = repo_id.rsplit("/", 1)[1] + ".nemo"
    if expected_name in candidates:
        return expected_name
    if len(candidates) == 1:
        return candidates[0]
    raise DownloadError("multiple .nemo files found; pass --filename: " + ", ".join(candidates))


def fetch_hf_model_info(repo_id: str, token: str | None) -> HfModelInfo:
    url = "https://huggingface.co/api/models/" + urllib.parse.quote(repo_id, safe="/")
    request = urllib.request.Request(url, headers=auth_header(token))
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read()
    except urllib.error.HTTPError as exc:
        raise DownloadError(hf_error_message(repo_id, exc)) from exc
    return HfModelInfo.model_validate(json.loads(payload))


def hf_resolve_url(repo_id: str, filename: str) -> str:
    return (
        "https://huggingface.co/"
        + urllib.parse.quote(repo_id, safe="/")
        + "/resolve/main/"
        + urllib.parse.quote(filename, safe="/")
    )


def download_snapshot(repo_id: str, output_dir: Path, *, token: str | None, force: bool) -> None:
    info = fetch_hf_model_info(repo_id, token)
    output_dir.mkdir(parents=True, exist_ok=True)
    for sibling in sorted(info.siblings, key=lambda item: item.rfilename):
        filename = sibling.rfilename
        if filename.endswith("/"):
            continue
        download(
            hf_resolve_url(repo_id, filename),
            output_dir / filename,
            token=token,
            force=force,
        )


def download(url: str, output_path: Path, *, token: str | None, force: bool) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and output_path.stat().st_size > 0 and not force:
        print(f"exists: {output_path}", file=sys.stderr)
        return

    part_path = output_path.with_suffix(output_path.suffix + ".part")
    resume_at = 0 if force or not part_path.exists() else part_path.stat().st_size
    headers = auth_header(token)
    if resume_at:
        headers["Range"] = f"bytes={resume_at}-"

    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            status = getattr(response, "status", 200)
            mode = "ab" if resume_at and status == 206 else "wb"
            if mode == "wb":
                resume_at = 0
            written = resume_at
            with part_path.open(mode) as output:
                while True:
                    chunk = response.read(CHUNK_BYTES)
                    if not chunk:
                        break
                    output.write(chunk)
                    written += len(chunk)
                    print(f"downloaded {written / (1024 * 1024):.1f} MiB", file=sys.stderr)
    except urllib.error.HTTPError as exc:
        raise DownloadError(hf_download_error_message(url, exc)) from exc

    if part_path.stat().st_size == 0:
        raise DownloadError(f"download produced an empty file: {part_path}")
    part_path.replace(output_path)


def auth_header(token: str | None) -> dict[str, str]:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def hf_error_message(repo_id: str, exc: urllib.error.HTTPError) -> str:
    if exc.code in (401, 403):
        return f"Hugging Face access denied for {repo_id}; set HF_TOKEN for gated/private models"
    return f"Hugging Face API failed for {repo_id}: HTTP {exc.code}"


def hf_download_error_message(url: str, exc: urllib.error.HTTPError) -> str:
    if exc.code in (401, 403):
        return f"Hugging Face download denied for {url}; set HF_TOKEN for gated/private models"
    return f"Hugging Face download failed for {url}: HTTP {exc.code}"


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DownloadError as exc:
        raise SystemExit(str(exc)) from exc
