"""Generate Python protobuf bindings for fluent-audio contracts."""

from pathlib import Path

import grpc_tools
from grpc_tools import protoc

REPO_ROOT = Path(__file__).resolve().parents[2]
PROTO_ROOT = REPO_ROOT / "contracts" / "proto"
PYTHON_PACKAGE_ROOT = REPO_ROOT / "contracts" / "python" / "src" / "fluent_audio_contracts"
GRPC_TOOLS_PROTO_ROOT = Path(grpc_tools.__file__).resolve().parent / "_proto"
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


def _remove_generated_files() -> None:
    generated_root = PYTHON_PACKAGE_ROOT / "fluent_audio" / "v1"
    for path in generated_root.glob("*_pb2.py"):
        path.unlink()
    for path in generated_root.glob("*_pb2.pyi"):
        path.unlink()


def _ensure_init_files() -> None:
    package_paths = (
        PYTHON_PACKAGE_ROOT,
        PYTHON_PACKAGE_ROOT / "fluent_audio",
        PYTHON_PACKAGE_ROOT / "fluent_audio" / "v1",
    )
    for path in package_paths:
        path.mkdir(parents=True, exist_ok=True)
        init_file = path / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""Generated fluent-audio protobuf package."""\n')


def _rewrite_generated_imports() -> None:
    generated_root = PYTHON_PACKAGE_ROOT / "fluent_audio" / "v1"
    for path in tuple(generated_root.glob("*_pb2.py")) + tuple(generated_root.glob("*_pb2.pyi")):
        text = path.read_text()
        text = text.replace(
            "from fluent_audio.v1 import ",
            "from fluent_audio_contracts.fluent_audio.v1 import ",
        )
        path.write_text(text)


def main() -> None:
    _ensure_init_files()
    _remove_generated_files()
    args = [
        "grpc_tools.protoc",
        f"--proto_path={PROTO_ROOT}",
        f"--proto_path={GRPC_TOOLS_PROTO_ROOT}",
        f"--python_out={PYTHON_PACKAGE_ROOT}",
        f"--pyi_out={PYTHON_PACKAGE_ROOT}",
    ]
    args.extend(str(path) for path in PROTO_FILES)
    exit_code = protoc.main(args)
    if exit_code != 0:
        raise SystemExit(exit_code)
    _rewrite_generated_imports()


if __name__ == "__main__":
    main()
