# Rust Contracts

This crate exposes generated protobuf bindings from `contracts/proto`.

Build and test:

```bash
cargo test --manifest-path contracts/rust/Cargo.toml
```

Use from Rust:

```rust
use fluent_dialogue_dora_contracts::fluent_dialogue_dora::v1::AudioFrame;
```
