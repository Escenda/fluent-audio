"""Generate C++ protobuf bindings for fluent-dialogue-dora contracts."""

import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROTO_ROOT = REPO_ROOT / "contracts" / "proto"
CPP_GENERATED_ROOT = REPO_ROOT / "contracts" / "cpp" / "generated"
PROTO_FILES = (
    PROTO_ROOT / "fluent_dialogue_dora" / "v1" / "audio.proto",
    PROTO_ROOT / "fluent_dialogue_dora" / "v1" / "vad.proto",
    PROTO_ROOT / "fluent_dialogue_dora" / "v1" / "asr.proto",
    PROTO_ROOT / "fluent_dialogue_dora" / "v1" / "dialogue.proto",
    PROTO_ROOT / "fluent_dialogue_dora" / "v1" / "tts.proto",
    PROTO_ROOT / "fluent_dialogue_dora" / "v1" / "session.proto",
    PROTO_ROOT / "fluent_dialogue_dora" / "v1" / "playback.proto",
    PROTO_ROOT / "fluent_dialogue_dora" / "v1" / "barge_in.proto",
    PROTO_ROOT / "fluent_dialogue_dora" / "v1" / "diagnostics.proto",
)


class CppContractGenerationError(RuntimeError):
    """Raised when C++ protobuf generation cannot run in this environment."""


def _remove_generated_files() -> None:
    if not CPP_GENERATED_ROOT.exists():
        return
    for path in CPP_GENERATED_ROOT.rglob("*.pb.cc"):
        path.unlink()
    for path in CPP_GENERATED_ROOT.rglob("*.pb.h"):
        path.unlink()


def _protoc_binary() -> str:
    configured = os.environ.get("FLUENT_DIALOGUE_DORA_PROTOC")
    if configured is not None:
        if configured == "":
            raise CppContractGenerationError("FLUENT_DIALOGUE_DORA_PROTOC must not be empty")
        return configured
    discovered = shutil.which("protoc")
    if discovered is None:
        raise CppContractGenerationError(
            "protoc is required for C++ contract generation. "
            "Install protobuf-compiler or set FLUENT_DIALOGUE_DORA_PROTOC to a protoc binary."
        )
    return discovered


def _strip_trailing_whitespace(path: Path) -> None:
    path.write_text(
        "\n".join(line.rstrip(" \t") for line in path.read_text().splitlines()) + "\n"
    )


def _normalize_generated_files() -> None:
    for path in CPP_GENERATED_ROOT.rglob("*.pb.cc"):
        _strip_trailing_whitespace(path)
    for path in CPP_GENERATED_ROOT.rglob("*.pb.h"):
        _strip_trailing_whitespace(path)


def main() -> None:
    CPP_GENERATED_ROOT.mkdir(parents=True, exist_ok=True)
    _remove_generated_files()
    args = (
        _protoc_binary(),
        f"--proto_path={PROTO_ROOT}",
        f"--cpp_out={CPP_GENERATED_ROOT}",
        *(str(path) for path in PROTO_FILES),
    )
    subprocess.run(args, check=True)
    _normalize_generated_files()


if __name__ == "__main__":
    main()
