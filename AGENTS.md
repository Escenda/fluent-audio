# AGENTS.md

This repository is the standalone `fluent-audio` runtime.

Core rules:

- Do not hide audio, timing, sequence, device, or model failures with implicit fallback.
- Do not keep legacy compatibility paths unless a human explicitly approves the exception.
- Keep DORA process boundaries separate from in-process media graphs.
- Keep `src/fluent_audio` for shared contracts and libraries.
- Keep executable DORA nodes under top-level `nodes/`.
- Keep Rust-heavy node crates directly under `crates/`.
- Validate external payloads at boundaries before passing them inward.
- Do not introduce `Any`, `dict[str, Any]`, or `object` as contract escape hatches.
- Do not claim runtime success without running the representative path.
