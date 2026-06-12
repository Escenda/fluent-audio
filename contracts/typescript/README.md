# TypeScript Contracts

This npm package exposes generated protobuf bindings from `contracts/proto`.

Install local generator dependencies:

```bash
npm install --prefix contracts/typescript
```

Generate bindings:

```bash
uv run tools/generate_contracts/typescript.py
```

Use from TypeScript:

```ts
import { fluent_audio } from "@fluent-audio/contracts";

const frame = fluent_audio.v1.AudioFrame.create({ sourceId: "mic" });
```
