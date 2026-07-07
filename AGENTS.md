# AGENTS.md

This repository is the standalone `fluent-dialogue-dora` runtime.

Core rules:

- Do not hide audio, timing, sequence, device, or model failures with implicit fallback.
- Do not keep legacy compatibility paths unless a human explicitly approves the exception.
- Keep DORA process boundaries separate from in-process media graphs.
- Keep `contracts/proto` as the schema source of truth for generated contracts.
- Keep `contracts/python` for generated Python protobuf bindings.
- Keep `src/fluent_dialogue_dora` for runtime helpers that are not generated contract code.
- Keep executable DORA nodes under top-level `nodes/`.
- Keep Rust-heavy node implementation inside the owning node directory under `nodes/`.
- Do not reintroduce top-level `crates/` unless a human explicitly approves the exception.
- Validate external payloads at boundaries before passing them inward.
- Do not introduce `Any`, `dict[str, Any]`, or `object` as contract escape hatches.
- Do not claim runtime success without running the representative path.
