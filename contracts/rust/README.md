# Rust Contracts

This crate exposes generated protobuf bindings from `contracts/proto`.

Build and test:

```bash
cargo test --manifest-path contracts/rust/Cargo.toml
```

Use from Rust:

```rust
use fluent_audio_contracts::fluent_audio::v1::AudioFrame;
```
