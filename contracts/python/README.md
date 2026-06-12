# Python Contracts

This package exposes generated protobuf bindings.

Generate bindings:

```bash
uv run --with grpcio-tools --with protobuf tools/generate_contracts/python.py
```

Use from Python:

```python
from fluent_audio_contracts.fluent_audio.v1.audio_pb2 import AudioFrame
```
