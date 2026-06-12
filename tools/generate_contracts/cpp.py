"""Generate C++ protobuf bindings for fluent-audio contracts."""

import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROTO_ROOT = REPO_ROOT / "contracts" / "proto"
CPP_GENERATED_ROOT = REPO_ROOT / "contracts" / "cpp" / "generated"
PROTO_FILES = (
    PROTO_ROOT / "fluent_audio" / "v1" / "audio.proto",
    PROTO_ROOT / "fluent_audio" / "v1" / "vad.proto",
    PROTO_ROOT / "fluent_audio" / "v1" / "asr.proto",
    PROTO_ROOT / "fluent_audio" / "v1" / "dialogue.proto",
    PROTO_ROOT / "fluent_audio" / "v1" / "tts.proto",
    PROTO_ROOT / "fluent_audio" / "v1" / "session.proto",
    PROTO_ROOT / "fluent_audio" / "v1" / "playback.proto",
    PROTO_ROOT / "fluent_audio" / "v1" / "diagnostics.proto",
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
    configured = os.environ.get("FLUENT_AUDIO_PROTOC")
    if configured is not None:
        if configured == "":
            raise CppContractGenerationError("FLUENT_AUDIO_PROTOC must not be empty")
        return configured
    discovered = shutil.which("protoc")
    if discovered is None:
        raise CppContractGenerationError(
            "protoc is required for C++ contract generation. "
            "Install protobuf-compiler or set FLUENT_AUDIO_PROTOC to a protoc binary."
        )
    return discovered


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


if __name__ == "__main__":
    main()
