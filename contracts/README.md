# Contracts

`contracts/proto` is the schema source of truth for messages shared across DORA
nodes, bridges, and external clients.

Language packages are generated from the proto files:

- `contracts/python` provides the `fluent_audio_contracts` Python package.
- `contracts/rust` provides the `fluent-audio-contracts` Rust crate.
- `contracts/cpp` provides generated C++ sources and a CMake target.
- `contracts/typescript` provides the `@fluent-audio/contracts` npm package.

Generated types guarantee transport shape. Runtime nodes still validate the
domain constraints they own at their ingress and execution boundaries.
