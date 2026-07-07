# C++ Contracts

This package contains C++ protobuf bindings generated from `contracts/proto`.

Generate bindings:

```bash
uv run --with grpcio-tools --with protobuf tools/generate_contracts/cpp.py
```

Consume with CMake:

```cmake
add_subdirectory(contracts/cpp)
target_link_libraries(your_target PRIVATE fluent_dialogue_dora_contracts)
```
