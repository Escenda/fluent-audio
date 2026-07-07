"""DORA probe for agent runtime output events."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fluent_dialogue_dora.contracts import (
    AgentApprovalRequest,
    AgentTextDelta,
    AgentToolEvent,
    AgentTurnDone,
)
from fluent_dialogue_dora.dora import (
    decode_agent_approval_request_from_dora,
    decode_agent_text_delta_from_dora,
    decode_agent_tool_event_from_dora,
    decode_agent_turn_done_from_dora,
    validate_dora_agent_approval_metadata,
    validate_dora_agent_text_metadata,
    validate_dora_agent_tool_metadata,
    validate_dora_agent_turn_done_metadata,
)


class AgentOutputProbeError(ValueError):
    """Raised when DORA agent output validation fails."""


AGENT_OUTPUT_INPUT_IDS = ("agent_text", "agent_done", "agent_approval", "agent_tool")


class AgentOutputProbeSummary(BaseModel):
    """Validated smoke summary for a DORA agent output stream."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    text_deltas: int = Field(ge=0)
    turn_done: int = Field(ge=0)
    approval_requests: int = Field(ge=0)
    tool_events: int = Field(ge=0)
    done_status: str
    text: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and discard DORA agent outputs.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--user-turn-id", required=True)
    parser.add_argument("--agent-turn-id", required=True)
    parser.add_argument("--expected-min-text-deltas", type=int, default=0)
    parser.add_argument("--expected-approval-requests", type=int, default=0)
    parser.add_argument("--expected-tool-events", type=int, default=0)
    parser.add_argument(
        "--expected-done-status",
        choices=("completed", "cancelled", "failed"),
        default="completed",
    )
    parser.add_argument("--expected-text-contains", default="")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("agent_output_probe requires --dora")

    from dora import Node

    summary = run_agent_output_probe_dora(
        Node(),
        session_id=args.session_id,
        user_turn_id=args.user_turn_id,
        agent_turn_id=args.agent_turn_id,
    )
    validate_summary(
        summary,
        expected_min_text_deltas=args.expected_min_text_deltas,
        expected_approval_requests=args.expected_approval_requests,
        expected_tool_events=args.expected_tool_events,
        expected_done_status=args.expected_done_status,
        expected_text_contains=args.expected_text_contains,
    )
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def run_agent_output_probe_dora(
    node,
    *,
    session_id: str,
    user_turn_id: str,
    agent_turn_id: str,
) -> AgentOutputProbeSummary:
    text_deltas = 0
    turn_done = 0
    approval_requests = 0
    tool_events = 0
    text_parts: list[tuple[int, str]] = []
    done_status = ""
    done_seq: int | None = None
    seen_seqs: dict[int, str] = {}
    non_terminal_seqs: list[tuple[str, int]] = []
    closed_inputs: set[str] = set()

    for event in node:
        if event is None:
            return _build_summary_after_terminal(
                text_deltas=text_deltas,
                turn_done=turn_done,
                approval_requests=approval_requests,
                tool_events=tool_events,
                done_status=done_status,
                done_seq=done_seq,
                non_terminal_seqs=non_terminal_seqs,
                text_parts=text_parts,
            )

        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            return _build_summary_after_terminal(
                text_deltas=text_deltas,
                turn_done=turn_done,
                approval_requests=approval_requests,
                tool_events=tool_events,
                done_status=done_status,
                done_seq=done_seq,
                non_terminal_seqs=non_terminal_seqs,
                text_parts=text_parts,
            )
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id not in AGENT_OUTPUT_INPUT_IDS:
                raise AgentOutputProbeError(f"Unexpected DORA input id: {input_id!r}")
            closed_inputs.add(input_id)
            if all(input_id in closed_inputs for input_id in AGENT_OUTPUT_INPUT_IDS):
                return _build_summary_after_terminal(
                    text_deltas=text_deltas,
                    turn_done=turn_done,
                    approval_requests=approval_requests,
                    tool_events=tool_events,
                    done_status=done_status,
                    done_seq=done_seq,
                    non_terminal_seqs=non_terminal_seqs,
                    text_parts=text_parts,
                )
            continue
        if event_type != "INPUT":
            raise AgentOutputProbeError(f"Unexpected DORA event type: {event_type!r}")

        input_id = _required_event_text(event, "id")
        payload = event.get("value")
        metadata = event.get("metadata")
        if input_id == "agent_text":
            text = _decode_text_delta(payload, metadata)
            _validate_turn_event(
                text,
                session_id=session_id,
                user_turn_id=user_turn_id,
                agent_turn_id=agent_turn_id,
            )
            _record_seq(seen_seqs, "agent_text", text.seq)
            non_terminal_seqs.append(("agent_text", text.seq))
            text_deltas += 1
            text_parts.append((text.seq, text.text))
            continue
        if input_id == "agent_done":
            done = _decode_turn_done(payload, metadata)
            _validate_turn_event(
                done,
                session_id=session_id,
                user_turn_id=user_turn_id,
                agent_turn_id=agent_turn_id,
            )
            _record_seq(seen_seqs, "agent_done", done.seq)
            turn_done += 1
            if turn_done > 1:
                raise AgentOutputProbeError(f"Agent done count mismatch: expected 1, got {turn_done}")
            done_status = done.status
            done_seq = done.seq
            continue
        if input_id == "agent_approval":
            approval = _decode_approval_request(payload, metadata)
            _validate_session_turn(
                approval.session_id,
                approval.user_turn_id,
                session_id=session_id,
                user_turn_id=user_turn_id,
            )
            _record_seq(seen_seqs, "agent_approval", approval.seq)
            non_terminal_seqs.append(("agent_approval", approval.seq))
            approval_requests += 1
            continue
        if input_id == "agent_tool":
            tool = _decode_tool_event(payload, metadata)
            _validate_session_turn(
                tool.session_id,
                tool.user_turn_id,
                session_id=session_id,
                user_turn_id=user_turn_id,
            )
            _record_seq(seen_seqs, "agent_tool", tool.seq)
            non_terminal_seqs.append(("agent_tool", tool.seq))
            tool_events += 1
            continue
        raise AgentOutputProbeError(f"Unexpected DORA input id: {input_id!r}")

    return _build_summary_after_terminal(
        text_deltas=text_deltas,
        turn_done=turn_done,
        approval_requests=approval_requests,
        tool_events=tool_events,
        done_status=done_status,
        done_seq=done_seq,
        non_terminal_seqs=non_terminal_seqs,
        text_parts=text_parts,
    )


def validate_summary(
    summary: AgentOutputProbeSummary,
    *,
    expected_min_text_deltas: int,
    expected_approval_requests: int,
    expected_tool_events: int,
    expected_done_status: str,
    expected_text_contains: str,
) -> None:
    if summary.text_deltas < expected_min_text_deltas:
        raise AgentOutputProbeError(
            "Agent text delta count below expectation: "
            f"expected at least {expected_min_text_deltas}, got {summary.text_deltas}"
        )
    if summary.turn_done != 1:
        raise AgentOutputProbeError(
            f"Agent done count mismatch: expected 1, got {summary.turn_done}"
        )
    if summary.approval_requests != expected_approval_requests:
        raise AgentOutputProbeError(
            "Agent approval count mismatch: "
            f"expected {expected_approval_requests}, got {summary.approval_requests}"
        )
    if summary.tool_events != expected_tool_events:
        raise AgentOutputProbeError(
            f"Agent tool event count mismatch: expected {expected_tool_events}, got {summary.tool_events}"
        )
    if summary.done_status != expected_done_status:
        raise AgentOutputProbeError(
            f"Agent done status mismatch: expected {expected_done_status!r}, got {summary.done_status!r}"
        )
    if expected_text_contains and expected_text_contains not in summary.text:
        raise AgentOutputProbeError(
            "Agent text did not contain expected substring: "
            f"expected {expected_text_contains!r}, got {summary.text!r}"
        )


def _decode_text_delta(payload, metadata) -> AgentTextDelta:
    text_metadata = validate_dora_agent_text_metadata(metadata)
    return decode_agent_text_delta_from_dora(payload, text_metadata)


def _decode_turn_done(payload, metadata) -> AgentTurnDone:
    done_metadata = validate_dora_agent_turn_done_metadata(metadata)
    return decode_agent_turn_done_from_dora(payload, done_metadata)


def _decode_approval_request(payload, metadata) -> AgentApprovalRequest:
    approval_metadata = validate_dora_agent_approval_metadata(metadata)
    return decode_agent_approval_request_from_dora(payload, approval_metadata)


def _decode_tool_event(payload, metadata) -> AgentToolEvent:
    tool_metadata = validate_dora_agent_tool_metadata(metadata)
    return decode_agent_tool_event_from_dora(payload, tool_metadata)


def _validate_turn_event(
    event: AgentTextDelta | AgentTurnDone,
    *,
    session_id: str,
    user_turn_id: str,
    agent_turn_id: str,
) -> None:
    _validate_session_turn(
        event.session_id,
        event.user_turn_id,
        session_id=session_id,
        user_turn_id=user_turn_id,
    )
    if event.agent_turn_id != agent_turn_id:
        raise AgentOutputProbeError(
            f"Agent turn id mismatch: expected {agent_turn_id!r}, got {event.agent_turn_id!r}"
        )


def _validate_session_turn(
    observed_session_id: str,
    observed_user_turn_id: str,
    *,
    session_id: str,
    user_turn_id: str,
) -> None:
    if observed_session_id != session_id:
        raise AgentOutputProbeError(
            f"Agent output session mismatch: expected {session_id!r}, got {observed_session_id!r}"
        )
    if observed_user_turn_id != user_turn_id:
        raise AgentOutputProbeError(
            "Agent output user turn mismatch: "
            f"expected {user_turn_id!r}, got {observed_user_turn_id!r}"
        )


def _build_summary_after_terminal(
    *,
    text_deltas: int,
    turn_done: int,
    approval_requests: int,
    tool_events: int,
    done_status: str,
    done_seq: int | None,
    non_terminal_seqs: list[tuple[str, int]],
    text_parts: list[tuple[int, str]],
) -> AgentOutputProbeSummary:
    if turn_done != 1 or done_seq is None:
        raise AgentOutputProbeError("DORA agent output stream ended without agent_done")
    _validate_terminal_seq(done_seq, non_terminal_seqs)
    return AgentOutputProbeSummary(
        text_deltas=text_deltas,
        turn_done=turn_done,
        approval_requests=approval_requests,
        tool_events=tool_events,
        done_status=done_status,
        text="".join(text for _, text in sorted(text_parts, key=lambda part: part[0])),
    )


def _record_seq(seen_seqs: dict[int, str], input_id: str, seq: int) -> None:
    previous_input = seen_seqs.get(seq)
    if previous_input is not None:
        raise AgentOutputProbeError(
            f"Agent output duplicate seq {seq}: {previous_input!r} and {input_id!r}"
        )
    seen_seqs[seq] = input_id


def _validate_terminal_seq(done_seq: int, non_terminal_seqs: list[tuple[str, int]]) -> None:
    for input_id, seq in non_terminal_seqs:
        if seq >= done_seq:
            raise AgentOutputProbeError(
                "Agent terminal seq must be greater than non-terminal seq: "
                f"agent_done={done_seq}, {input_id}={seq}"
            )


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise AgentOutputProbeError(f"DORA event field {key!r} must be a string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
