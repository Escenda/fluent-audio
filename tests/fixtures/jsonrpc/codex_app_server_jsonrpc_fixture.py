"""Line-oriented JSON-RPC fixture for codex_app_server DORA smokes."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated, TypeAlias

from pydantic import BaseModel, Field, TypeAdapter

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from nodes.dialogue_engine.codex_app_server.main import (
    CodexAdditionalFileSystemPermissions,
    CodexAdditionalNetworkPermissions,
    CodexApprovalJsonRpcResponse,
    CodexAgentMessageDeltaEnvelope,
    CodexAgentMessageDeltaParams,
    CodexCommandApprovalParams,
    CodexCommandApprovalRequestEnvelope,
    CodexPermissionProfile,
    CodexPermissionsApprovalJsonRpcResponse,
    CodexPermissionsApprovalParams,
    CodexPermissionsApprovalRequestEnvelope,
    CodexInitializeJsonRpcRequest,
    CodexInitializeJsonRpcResponse,
    CodexInitializeResult,
    CodexInitializedNotification,
    CodexServerRequestResolvedEnvelope,
    CodexServerRequestResolvedParams,
    CodexThreadReference,
    CodexThreadStartJsonRpcRequest,
    CodexThreadStartJsonRpcResponse,
    CodexThreadStartResult,
    CodexTurnCompletedEnvelope,
    CodexTurnCompletedParams,
    CodexTurnInterruptJsonRpcRequest,
    CodexTurnInterruptJsonRpcResponse,
    CodexTurnReference,
    CodexTurnStartJsonRpcRequest,
    CodexTurnStartJsonRpcResponse,
    CodexTurnStartResult,
)

FixtureClientRequest: TypeAlias = (
    CodexInitializeJsonRpcRequest
    | CodexThreadStartJsonRpcRequest
    | CodexTurnStartJsonRpcRequest
    | CodexTurnInterruptJsonRpcRequest
)
FixtureClientMessage: TypeAlias = FixtureClientRequest | CodexInitializedNotification
FixtureClientMessageEnvelope: TypeAlias = Annotated[
    FixtureClientMessage,
    Field(discriminator="method"),
]
FIXTURE_CLIENT_MESSAGE_ADAPTER = TypeAdapter(FixtureClientMessageEnvelope)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a Codex JSON-RPC fixture.")
    parser.add_argument("--text", required=True)
    parser.add_argument("--thread-id", default="thread-fixture-1")
    parser.add_argument("--turn-id", default="turn-fixture-1")
    parser.add_argument("--item-id", default="agent-message-fixture-1")
    parser.add_argument("--expected-turns", type=int, default=1)
    parser.add_argument("--approval-request-id", default="approval-request-fixture-1")
    parser.add_argument("--approval-kind", choices=("command", "permissions"), default="command")
    parser.add_argument("--approval-command")
    parser.add_argument("--approval-reason")
    parser.add_argument("--permission-write", action="append")
    parser.add_argument("--permission-network", action="store_true")
    parser.add_argument(
        "--expected-approval-decision",
        choices=("accept", "acceptForSession", "decline", "cancel"),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    completed_turns = 0
    while completed_turns < args.expected_turns:
        line = sys.stdin.readline()
        if line == "":
            raise RuntimeError("JSON-RPC fixture stdin closed before expected turns")
        request = FIXTURE_CLIENT_MESSAGE_ADAPTER.validate_json(line)
        if isinstance(request, CodexInitializeJsonRpcRequest):
            _write_initialize_response(request.id)
        elif isinstance(request, CodexInitializedNotification):
            continue
        elif isinstance(request, CodexThreadStartJsonRpcRequest):
            _write_thread_start_response(request.id, thread_id=args.thread_id)
        elif isinstance(request, CodexTurnStartJsonRpcRequest):
            _write_turn_start_response(request.id, turn_id=args.turn_id)
            if args.approval_kind == "permissions":
                _write_permissions_approval_request(
                    request_id=args.approval_request_id,
                    thread_id=request.params.thread_id,
                    turn_id=args.turn_id,
                    item_id="permissions-fixture-1",
                    cwd="/tmp/fluent-dialogue-dora-permissions-fixture",
                    permissions=_build_permission_profile(
                        write_paths=tuple(args.permission_write or ()),
                        network_enabled=args.permission_network,
                    ),
                    reason=args.approval_reason,
                )
                response_line = sys.stdin.readline()
                if response_line == "":
                    raise RuntimeError("JSON-RPC fixture stdin closed before permission response")
                response = CodexPermissionsApprovalJsonRpcResponse.model_validate_json(response_line)
                if response.id != args.approval_request_id:
                    raise RuntimeError("permission response id did not match fixture request id")
                if not response.result.permissions.model_dump(exclude_none=True):
                    raise RuntimeError("permission response did not grant requested permissions")
                _write_server_request_resolved(
                    thread_id=request.params.thread_id,
                    request_id=args.approval_request_id,
                )
            elif args.approval_command is not None or args.approval_reason is not None:
                _write_command_approval_request(
                    request_id=args.approval_request_id,
                    thread_id=request.params.thread_id,
                    turn_id=args.turn_id,
                    item_id="command-fixture-1",
                    command=args.approval_command,
                    reason=args.approval_reason,
                )
                response_line = sys.stdin.readline()
                if response_line == "":
                    raise RuntimeError("JSON-RPC fixture stdin closed before approval response")
                response = CodexApprovalJsonRpcResponse.model_validate_json(response_line)
                if response.id != args.approval_request_id:
                    raise RuntimeError("approval response id did not match fixture request id")
                if args.expected_approval_decision is not None:
                    if response.result.decision != args.expected_approval_decision:
                        raise RuntimeError("approval response decision did not match expectation")
                _write_server_request_resolved(
                    thread_id=request.params.thread_id,
                    request_id=args.approval_request_id,
                )
            _write_agent_delta(
                thread_id=request.params.thread_id,
                turn_id=args.turn_id,
                item_id=args.item_id,
                text=args.text,
            )
            _write_turn_completed(
                thread_id=request.params.thread_id,
                turn_id=args.turn_id,
            )
            completed_turns += 1
        elif isinstance(request, CodexTurnInterruptJsonRpcRequest):
            _write_turn_interrupt_response(request.id)
    return 0


def _write_initialize_response(request_id: str) -> None:
    response = CodexInitializeJsonRpcResponse(
        id=request_id,
        result=CodexInitializeResult(
            user_agent="fluent-dialogue-dora-fixture/0.0.0",
            codex_home="/tmp/fluent-dialogue-dora-fixture-codex-home",
            platform_family="unix",
            platform_os="linux",
        ),
    )
    _write_model(response)


def _write_thread_start_response(request_id: str, *, thread_id: str) -> None:
    response = CodexThreadStartJsonRpcResponse(
        id=request_id,
        result=CodexThreadStartResult(
            thread=CodexThreadReference(id=thread_id),
        ),
    )
    _write_model(response)


def _write_turn_start_response(request_id: str, *, turn_id: str) -> None:
    response = CodexTurnStartJsonRpcResponse(
        id=request_id,
        result=CodexTurnStartResult(
            turn=CodexTurnReference(id=turn_id, status="inProgress"),
        ),
    )
    _write_model(response)


def _write_turn_interrupt_response(request_id: str) -> None:
    _write_model(CodexTurnInterruptJsonRpcResponse(id=request_id))


def _write_command_approval_request(
    *,
    request_id: str,
    thread_id: str,
    turn_id: str,
    item_id: str,
    command: str | None,
    reason: str | None,
) -> None:
    _write_model(
        CodexCommandApprovalRequestEnvelope(
            id=request_id,
            method="item/commandExecution/requestApproval",
            params=CodexCommandApprovalParams(
                thread_id=thread_id,
                turn_id=turn_id,
                item_id=item_id,
                command=command,
                reason=reason,
            ),
        )
    )


def _write_permissions_approval_request(
    *,
    request_id: str,
    thread_id: str,
    turn_id: str,
    item_id: str,
    cwd: str,
    permissions: CodexPermissionProfile,
    reason: str | None,
) -> None:
    _write_model(
        CodexPermissionsApprovalRequestEnvelope(
            id=request_id,
            method="item/permissions/requestApproval",
            params=CodexPermissionsApprovalParams(
                thread_id=thread_id,
                turn_id=turn_id,
                item_id=item_id,
                cwd=cwd,
                permissions=permissions,
                started_at_ms=1,
                reason=reason,
            ),
        )
    )


def _build_permission_profile(
    *,
    write_paths: tuple[str, ...],
    network_enabled: bool,
) -> CodexPermissionProfile:
    file_system = (
        CodexAdditionalFileSystemPermissions(write=write_paths)
        if write_paths
        else None
    )
    network = (
        CodexAdditionalNetworkPermissions(enabled=True)
        if network_enabled
        else None
    )
    return CodexPermissionProfile(file_system=file_system, network=network)


def _write_server_request_resolved(*, thread_id: str, request_id: str) -> None:
    _write_model(
        CodexServerRequestResolvedEnvelope(
            method="serverRequest/resolved",
            params=CodexServerRequestResolvedParams(
                thread_id=thread_id,
                request_id=request_id,
            ),
        )
    )


def _write_agent_delta(
    *,
    thread_id: str,
    turn_id: str,
    item_id: str,
    text: str,
) -> None:
    notification = CodexAgentMessageDeltaEnvelope(
        method="item/agentMessage/delta",
        params=CodexAgentMessageDeltaParams(
            thread_id=thread_id,
            turn_id=turn_id,
            item_id=item_id,
            delta=text,
        ),
    )
    _write_model(notification)


def _write_turn_completed(*, thread_id: str, turn_id: str) -> None:
    notification = CodexTurnCompletedEnvelope(
        method="turn/completed",
        params=CodexTurnCompletedParams(
            thread_id=thread_id,
            turn=CodexTurnReference(id=turn_id, status="completed"),
        ),
    )
    _write_model(notification)


def _write_model(model: BaseModel) -> None:
    sys.stdout.write(model.model_dump_json(by_alias=True, exclude_none=True))
    sys.stdout.write("\n")
    sys.stdout.flush()


if __name__ == "__main__":
    raise SystemExit(main())
