# Contracts Implementation Review

Status: resolved by commit `b62bb9c` (`Implement fluent audio contracts`).

This document is kept as audit history for earlier implementation candidates that were not green.

Review target: current uncommitted `src/fluent_audio/contracts/` implementation candidate.

## Verdict

Do not mark `contracts` green yet.

The current candidate passes its own tests, but it does not satisfy [contracts-implementation-task.md](contracts-implementation-task.md). The gap is not style; it changes the public runtime contract that downstream nodes will depend on.

Verified commands:

```bash
uv run --extra dev python -m pytest tests/contracts
uv run --extra dev python -m ruff check .
```

Both passed for the current candidate, but the test set is narrower than the required contract.

## Blocking Gaps

### AudioChunk shape does not match the required contract

Required by the task:

- `seq`
- `capture_time_ns`
- supported sample formats `s16le` and `f32le`

Current candidate:

- uses `sequence`
- has no `capture_time_ns`
- uses `pcm_s16le` and `pcm_f32le`

This must be corrected before `raw_pcm_source` or `raw_pcm_sink` is implemented. Otherwise IO nodes will encode the wrong public payload shape.

### Required interaction and synthesis contracts are missing

Required by the task:

- `DialogueInput`
- `DialogueEvent`
- `AgentTextDelta`
- `AgentApprovalRequest`
- `AgentToolEvent`
- `AgentCancelRequest`
- `TtsTextChunk`
- `SynthesizedAudioChunk`
- `PlaybackState`

Current candidate implements ASR controls, session events, VAD, and playback commands, but not these required payloads.

### Required activity / turn names are missing

Required by the task:

- `VoiceActivityState`
- `VoiceActivityEvent`
- `TurnState`
- `TurnEvent`

Current candidate has `VoiceActivity` and `VoiceSessionEvent`, but those do not cover the required turn-boundary contracts.

### Tests do not cover required fields

The current tests pass, but they do not assert:

- `capture_time_ns` exists and is non-negative
- the public field is `seq`
- `s16le` / `f32le` are the accepted sample format values
- dialogue event models validate explicit variants
- TTS text chunk and synthesized audio models validate payloads
- playback state validates explicit state/correlation fields

## Correction Request

Send this back to the implementation subagent:

```text
Your contracts implementation passes its own tests, but it is not green.

Please correct it against docs/architecture/contracts-implementation-task.md:

1. Change AudioChunk public field from sequence to seq.
2. Add capture_time_ns to AudioChunk and validate it is non-negative.
3. Use the required public sample format values s16le and f32le.
4. Add VoiceActivityState, VoiceActivityEvent, TurnState, and TurnEvent.
5. Add DialogueInput, DialogueEvent, AgentTextDelta, AgentApprovalRequest, AgentToolEvent, and AgentCancelRequest.
6. Add TtsTextChunk, SynthesizedAudioChunk, and PlaybackState.
7. Add tests that fail without the required fields/classes above.
8. Keep build-plan contracts Yellow until the full required test set passes.

Do not implement raw_pcm_source/sink yet.
Do not change nodes/ or graphs/.
Do not introduce Any, dict[str, Any], or object.
```

## Resolution

Commit `b62bb9c` added the required contract modules and updated [build-plan.md](build-plan.md) so `contracts` is Green.

Verified after the commit:

```bash
uv run --extra dev python -c "import fluent_audio; print(fluent_audio.__file__)"
uv run --extra dev python -m pytest tests/contracts
uv run --extra dev python -m ruff check .
grep -R "Any\\|dict\\[str\\|object\\|type: ignore" -n src/fluent_audio tests/contracts || true
grep -R '"sequence"\\|sequence=' -n src/fluent_audio/contracts tests/contracts || true
```

Results:

- package import passed
- `tests/contracts`: 41 passed
- ruff passed
- no `Any`, `dict[str, Any]`, `object`, or `type: ignore` matches
- no old `"sequence"` / `sequence=` contract payload fields remain; `final_sequence` remains only as the explicit playback terminal field
