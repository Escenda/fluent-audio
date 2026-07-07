"""Submit a browser-style approval response through dora_web_bridge REST."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from bridges.dora_web_bridge.messages import (
    DoraWebBridgeTopicSnapshotResponse,
    WebApprovalResponseSubmission,
)
from bridges.dora_web_bridge.projection import WebApprovalRequestEvent
from fluent_dialogue_dora.contracts import AgentApprovalRequest
from fluent_dialogue_dora.dora import (
    decode_agent_approval_request_from_dora,
    validate_dora_agent_approval_metadata,
)


class DoraWebApprovalSubmitterError(ValueError):
    """Raised when the approval submitter cannot safely complete."""


class DoraWebApprovalSubmitterConfig(BaseModel):
    """Runtime configuration for the approval submitter fixture."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    bridge_url: str = Field(min_length=1)
    decision: Literal["accept", "decline", "cancel"]
    scope: Literal["turn", "session"] = "turn"
    reason: str | None = Field(default=None, min_length=1)
    timeout_seconds: float = Field(default=5.0, gt=0.0)
    poll_interval_seconds: float = Field(default=0.05, gt=0.0)


class DoraWebApprovalSubmitterSummary(BaseModel):
    """Summary printed after one approval response is submitted."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    submitted: int = Field(ge=0)
    session_id: str = Field(min_length=1)
    user_turn_id: str = Field(min_length=1)
    approval_id: str = Field(min_length=1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Submit one dora_web_bridge approval response.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--bridge-url", required=True)
    parser.add_argument("--decision", choices=("accept", "decline", "cancel"), required=True)
    parser.add_argument("--scope", choices=("turn", "session"), default="turn")
    parser.add_argument("--reason")
    parser.add_argument("--timeout-seconds", type=float, default=5.0)
    parser.add_argument("--poll-interval-seconds", type=float, default=0.05)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("dora_web_approval_submitter requires --dora")

    from dora import Node

    config = DoraWebApprovalSubmitterConfig(
        bridge_url=args.bridge_url,
        decision=_approval_decision(args.decision),
        scope=_approval_scope(args.scope),
        reason=args.reason,
        timeout_seconds=args.timeout_seconds,
        poll_interval_seconds=args.poll_interval_seconds,
    )
    summary = run_dora_web_approval_submitter(Node(), config)
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def run_dora_web_approval_submitter(
    node,
    config: DoraWebApprovalSubmitterConfig,
) -> DoraWebApprovalSubmitterSummary:
    for event in node:
        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            raise DoraWebApprovalSubmitterError("DORA STOP arrived before approval request")
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id == "agent_approval":
                raise DoraWebApprovalSubmitterError("agent_approval input closed before request")
            continue
        if event_type != "INPUT":
            raise DoraWebApprovalSubmitterError(f"unexpected DORA event type: {event_type}")
        input_id = _required_event_text(event, "id")
        if input_id != "agent_approval":
            raise DoraWebApprovalSubmitterError(f"unexpected DORA input id: {input_id}")
        metadata = validate_dora_agent_approval_metadata(event.get("metadata"))
        request = decode_agent_approval_request_from_dora(event.get("value"), metadata)
        submit_dora_web_approval_response(config, request)
        return DoraWebApprovalSubmitterSummary(
            submitted=1,
            session_id=request.session_id,
            user_turn_id=request.user_turn_id,
            approval_id=request.approval_id,
        )
    raise DoraWebApprovalSubmitterError("DORA event stream ended before approval request")


def submit_dora_web_approval_response(
    config: DoraWebApprovalSubmitterConfig,
    request: AgentApprovalRequest,
) -> None:
    bridge_url = config.bridge_url.rstrip("/")
    if not bridge_url:
        raise DoraWebApprovalSubmitterError("bridge_url must not be empty")

    deadline = time.monotonic() + config.timeout_seconds
    while time.monotonic() < deadline:
        if _bridge_has_approval_request(bridge_url, request, config.timeout_seconds):
            _post_bridge_approval_response(bridge_url, config, request)
            return
        time.sleep(config.poll_interval_seconds)
    raise DoraWebApprovalSubmitterError("Timed out waiting for dora_web_bridge approval topic")


def _bridge_has_approval_request(
    bridge_url: str,
    request: AgentApprovalRequest,
    timeout_seconds: float,
) -> bool:
    url = f"{bridge_url}/api/topics/agent_approval/events.json?tail=200"
    http_request = urllib.request.Request(url, headers={"Accept": "application/json"}, method="GET")
    try:
        with urllib.request.urlopen(http_request, timeout=timeout_seconds) as response:
            status = response.getcode()
            body = response.read()
    except urllib.error.HTTPError as exc:
        if exc.code in (404, 409):
            return False
        body = exc.read().decode("utf-8", errors="replace")
        raise DoraWebApprovalSubmitterError(
            f"dora_web_bridge approval topic failed with HTTP {exc.code}: {body}"
        ) from exc
    except urllib.error.URLError:
        return False
    if status < 200 or status >= 300:
        raise DoraWebApprovalSubmitterError(
            f"dora_web_bridge approval topic returned unexpected HTTP status {status}"
        )
    try:
        snapshot = DoraWebBridgeTopicSnapshotResponse.model_validate_json(body)
    except ValueError as exc:
        raise DoraWebApprovalSubmitterError(
            "dora_web_bridge approval topic returned invalid JSON"
        ) from exc
    for item in snapshot.events:
        event = item.event
        if not isinstance(event, WebApprovalRequestEvent):
            continue
        if (
            event.session_id == request.session_id
            and event.user_turn_id == request.user_turn_id
            and event.approval_id == request.approval_id
        ):
            return True
    return False


def _post_bridge_approval_response(
    bridge_url: str,
    config: DoraWebApprovalSubmitterConfig,
    request: AgentApprovalRequest,
) -> None:
    session_id = urllib.parse.quote(request.session_id, safe="")
    user_turn_id = urllib.parse.quote(request.user_turn_id, safe="")
    approval_id = urllib.parse.quote(request.approval_id, safe="")
    url = (
        f"{bridge_url}/api/agent-approvals/{session_id}/user-turns/{user_turn_id}"
        f"/approval-requests/{approval_id}/responses"
    )
    submission = WebApprovalResponseSubmission(
        decision=config.decision,
        scope=config.scope,
        reason=config.reason,
    )
    http_request = urllib.request.Request(
        url,
        data=submission.model_dump_json().encode("utf-8"),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(http_request, timeout=config.timeout_seconds) as response:
            status = response.getcode()
            response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise DoraWebApprovalSubmitterError(
            f"dora_web_bridge approval POST failed with HTTP {exc.code}: {body}"
        ) from exc
    except urllib.error.URLError as exc:
        raise DoraWebApprovalSubmitterError(
            f"dora_web_bridge approval POST failed: {exc}"
        ) from exc
    if status < 200 or status >= 300:
        raise DoraWebApprovalSubmitterError(
            f"dora_web_bridge approval POST returned unexpected HTTP status {status}"
        )


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise DoraWebApprovalSubmitterError(f"DORA event field {key!r} must be a string")
    return value


def _approval_decision(value: str) -> Literal["accept", "decline", "cancel"]:
    if value == "accept":
        return "accept"
    if value == "decline":
        return "decline"
    if value == "cancel":
        return "cancel"
    raise ValueError("unsupported approval decision")


def _approval_scope(value: str) -> Literal["turn", "session"]:
    if value == "turn":
        return "turn"
    if value == "session":
        return "session"
    raise ValueError("unsupported approval scope")


if __name__ == "__main__":
    raise SystemExit(main())
