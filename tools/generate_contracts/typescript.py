"""Generate TypeScript protobuf bindings for fluent-audio contracts."""

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TYPESCRIPT_ROOT = REPO_ROOT / "contracts" / "typescript"
GENERATED_ROOT = TYPESCRIPT_ROOT / "src" / "generated"
PROTO_FILES = (
    "../proto/fluent_audio/v1/audio.proto",
    "../proto/fluent_audio/v1/vad.proto",
    "../proto/fluent_audio/v1/asr.proto",
    "../proto/fluent_audio/v1/dialogue.proto",
    "../proto/fluent_audio/v1/tts.proto",
    "../proto/fluent_audio/v1/session.proto",
    "../proto/fluent_audio/v1/playback.proto",
    "../proto/fluent_audio/v1/diagnostics.proto",
)


def _run(command: tuple[str, ...]) -> None:
    subprocess.run(command, cwd=TYPESCRIPT_ROOT, check=True)


def main() -> None:
    GENERATED_ROOT.mkdir(parents=True, exist_ok=True)
    js_path = GENERATED_ROOT / "fluent_audio_v1.js"
    dts_path = GENERATED_ROOT / "fluent_audio_v1.d.ts"
    if js_path.exists():
        js_path.unlink()
    legacy_cjs_path = GENERATED_ROOT / "fluent_audio_v1.cjs"
    if legacy_cjs_path.exists():
        legacy_cjs_path.unlink()
    if dts_path.exists():
        dts_path.unlink()
    _run(
        (
            "npx",
            "pbjs",
            "-t",
            "static-module",
            "-w",
            "commonjs",
            "-p",
            "../proto",
            "-o",
            str(js_path.relative_to(TYPESCRIPT_ROOT)),
            *PROTO_FILES,
        )
    )
    _run(
        (
            "npx",
            "pbts",
            "-o",
            str(dts_path.relative_to(TYPESCRIPT_ROOT)),
            str(js_path.relative_to(TYPESCRIPT_ROOT)),
        )
    )


if __name__ == "__main__":
    main()
