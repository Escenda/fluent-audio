"""DORA boundary for the Codex JSON-RPC app-server protocol.

The node keeps the voice dataflow contract small: DORA emits finalized text
turns and cancellation requests, while Codex app-server owns model streaming,
MCP/tool execution, approval requests, and turn lifecycle.
"""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import queue
import subprocess
import sys
import threading
import time
import urllib.parse
from collections.abc import Iterable, Sequence
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Annotated, Literal, Protocol, TextIO, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fluent_audio.contracts import (
    AgentApprovalRequest,
    AgentApprovalResponse,
    AgentApprovalScope,
    AgentCancelRequest,
    AgentMcpElicitationRequest,
    AgentMcpElicitationResponse,
    AgentTextDelta,
    AgentToolEvent,
    AgentTurnDone,
    AgentTurnRequest,
    AgentUserInputOption,
    AgentUserInputQuestion,
    AgentUserInputRequest,
    AgentUserInputResponse,
    JsonValue,
)
from fluent_audio.dora import (
    decode_agent_cancel_request_from_dora,
    decode_agent_mcp_elicitation_response_from_dora,
    decode_agent_turn_request_from_dora,
    decode_agent_user_input_response_from_dora,
    encode_agent_approval_request_for_dora,
    encode_agent_mcp_elicitation_request_for_dora,
    encode_agent_runtime_event_for_dora,
    encode_agent_text_delta_for_dora,
    encode_agent_tool_event_for_dora,
    encode_agent_turn_done_for_dora,
    encode_agent_user_input_request_for_dora,
    validate_dora_agent_cancel_metadata,
    validate_dora_agent_mcp_elicitation_response_metadata,
    validate_dora_agent_turn_request_metadata,
    validate_dora_agent_user_input_response_metadata,
)

ApprovalPolicy: TypeAlias = Literal["untrusted", "on-failure", "on-request", "never"]
ApprovalsReviewer: TypeAlias = Literal["user", "auto_review"]
CodexSandboxMode: TypeAlias = Literal["read-only", "workspace-write", "danger-full-access"]
CodexApprovalDecision: TypeAlias = Literal[
    "accept",
    "acceptForSession",
    "decline",
    "cancel",
]
CodexTurnStatus: TypeAlias = Literal["completed", "interrupted", "failed", "inProgress"]
CodexToolCallStatus: TypeAlias = Literal["inProgress", "completed", "failed"]
ProjectedTurnDoneStatus: TypeAlias = Literal["completed", "cancelled", "failed"]
ProjectedToolEventKind: TypeAlias = Literal["started", "completed", "failed"]
PendingApprovalKind: TypeAlias = Literal["command", "file_change", "permissions"]
McpElicitationMode: TypeAlias = Literal["form", "url"]
McpElicitationAction: TypeAlias = Literal["accept", "decline", "cancel"]
CodexJsonRpcRequestId: TypeAlias = str | int
CodexAppServerCommandFileLine: TypeAlias = Annotated[str, Field(min_length=1)]
CODEX_APP_SERVER_COMMAND_JSON_ADAPTER = TypeAdapter(tuple[str, ...])
CODEX_APP_SERVER_COMMAND_FILE_ADAPTER = TypeAdapter(tuple[CodexAppServerCommandFileLine, ...])


class CodexPathFileSystemPath(BaseModel):
    """Codex permission profile filesystem path with an absolute path."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    type: Literal["path"] = "path"
    path: str = Field(min_length=1)


class CodexGlobPatternFileSystemPath(BaseModel):
    """Codex permission profile filesystem path with a glob pattern."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    type: Literal["glob_pattern"] = "glob_pattern"
    pattern: str = Field(min_length=1)


class CodexSpecialFileSystemPathValue(BaseModel):
    """Codex permission profile special filesystem path value."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    kind: Literal["root", "minimal", "project_roots", "tmpdir", "slash_tmp", "unknown"]
    path: str | None = Field(default=None, min_length=1)
    subpath: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_variant_payload(self) -> "CodexSpecialFileSystemPathValue":
        if self.kind == "unknown" and self.path is None:
            raise ValueError("unknown special filesystem path requires path")
        if self.kind != "unknown" and self.path is not None:
            raise ValueError("path is only valid for unknown special filesystem paths")
        if self.subpath is not None and self.kind not in ("project_roots", "unknown"):
            raise ValueError("subpath is only valid for project_roots or unknown special paths")
        return self


class CodexSpecialFileSystemPath(BaseModel):
    """Codex permission profile filesystem path with a special value."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    type: Literal["special"] = "special"
    value: CodexSpecialFileSystemPathValue


CodexFileSystemPath: TypeAlias = (
    CodexPathFileSystemPath
    | CodexGlobPatternFileSystemPath
    | CodexSpecialFileSystemPath
)
CodexFileSystemAccessMode: TypeAlias = Literal["read", "write", "deny"]


class CodexFileSystemSandboxEntry(BaseModel):
    """One Codex permission profile filesystem access entry."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    access: CodexFileSystemAccessMode
    path: CodexFileSystemPath


class CodexAdditionalFileSystemPermissions(BaseModel):
    """Filesystem subset of a Codex permission profile request/grant."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    entries: tuple[CodexFileSystemSandboxEntry, ...] | None = None
    glob_scan_max_depth: int | None = Field(default=None, ge=1, alias="globScanMaxDepth")
    read: tuple[str, ...] | None = None
    write: tuple[str, ...] | None = None


class CodexAdditionalNetworkPermissions(BaseModel):
    """Network subset of a Codex permission profile request/grant."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    enabled: bool | None = None


class CodexPermissionProfile(BaseModel):
    """Codex permission profile subset used by permissions/requestApproval."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    file_system: CodexAdditionalFileSystemPermissions | None = Field(
        default=None,
        alias="fileSystem",
    )
    network: CodexAdditionalNetworkPermissions | None = None


class CodexAppServerNodeError(ValueError):
    """Raised when the Codex app-server boundary cannot be validated."""


class RequestBodyBoundaryError(ValueError):
    """Raised when an HTTP request body cannot be read as typed boundary input."""

    def __init__(self, *, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code


class CodexAppServerConfig(BaseModel):
    """Runtime configuration for the Codex app-server DORA boundary."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    command: tuple[str, ...] = ("codex", "app-server", "--listen", "stdio://")
    timeout_seconds: float = Field(default=30.0, gt=0.0)
    approval_response_timeout_seconds: float = Field(default=300.0, gt=0.0)
    poll_dora_control_during_approval: bool = False
    cwd: str | None = None
    model: str | None = None
    model_provider: str | None = Field(default=None, alias="modelProvider")
    base_instructions: str | None = Field(default=None, alias="baseInstructions")
    developer_instructions: str | None = Field(default=None, alias="developerInstructions")
    sandbox: CodexSandboxMode | None = None
    approval_policy: ApprovalPolicy | None = Field(default="on-request", alias="approvalPolicy")
    approvals_reviewer: ApprovalsReviewer | None = Field(default="user", alias="approvalsReviewer")
    client_name: str = Field(default="fluent-audio", min_length=1)
    client_version: str = Field(default="0.0.0", min_length=1)

    @model_validator(mode="after")
    def validate_command(self) -> "CodexAppServerConfig":
        if len(self.command) == 0:
            raise ValueError("command must not be empty")
        for part in self.command:
            if part.strip() == "":
                raise ValueError("command parts must not be empty")
        return self


class CodexThreadStartParams(BaseModel):
    """Subset of Codex thread/start params needed by the voice surface."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    ephemeral: bool = True
    cwd: str | None = None
    model: str | None = None
    model_provider: str | None = Field(default=None, alias="modelProvider")
    base_instructions: str | None = Field(default=None, alias="baseInstructions")
    developer_instructions: str | None = Field(default=None, alias="developerInstructions")
    sandbox: CodexSandboxMode | None = None
    approval_policy: ApprovalPolicy | None = Field(default="on-request", alias="approvalPolicy")
    approvals_reviewer: ApprovalsReviewer | None = Field(default="user", alias="approvalsReviewer")


class CodexClientInfo(BaseModel):
    """Client identity sent during Codex app-server initialize."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    title: str | None = None


class CodexInitializeCapabilities(BaseModel):
    """Client capabilities negotiated during initialize."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    experimental_api: bool = Field(default=False, alias="experimentalApi")
    opt_out_notification_methods: tuple[str, ...] = Field(
        default=("thread/started", "turn/started"),
        alias="optOutNotificationMethods",
    )
    request_attestation: bool = Field(default=False, alias="requestAttestation")


class CodexInitializeParams(BaseModel):
    """Codex initialize params."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    client_info: CodexClientInfo = Field(alias="clientInfo")
    capabilities: CodexInitializeCapabilities = Field(default_factory=CodexInitializeCapabilities)


class CodexInitializeJsonRpcRequest(BaseModel):
    """JSON-RPC request for initialize."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: str = Field(min_length=1)
    method: Literal["initialize"] = "initialize"
    params: CodexInitializeParams


class CodexInitializedNotification(BaseModel):
    """Client notification sent after initialize succeeds."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    method: Literal["initialized"] = "initialized"


class CodexInitializeResult(BaseModel):
    """initialize result subset used to validate live app-server readiness."""

    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    user_agent: str = Field(alias="userAgent", min_length=1)
    codex_home: str = Field(alias="codexHome", min_length=1)
    platform_family: str = Field(alias="platformFamily", min_length=1)
    platform_os: str = Field(alias="platformOs", min_length=1)


class CodexInitializeJsonRpcResponse(BaseModel):
    """Successful JSON-RPC response to initialize."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    id: str = Field(min_length=1)
    result: CodexInitializeResult


class CodexTextUserInput(BaseModel):
    """Plain text user input for turn/start."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    type: Literal["text"] = "text"
    text: str = Field(min_length=1)


class CodexTurnStartParams(BaseModel):
    """Subset of Codex turn/start params used by speech transcripts."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    thread_id: str = Field(alias="threadId", min_length=1)
    input: tuple[CodexTextUserInput, ...] = Field(min_length=1)
    client_user_message_id: str | None = Field(default=None, alias="clientUserMessageId")


class CodexTurnInterruptParams(BaseModel):
    """Codex turn/interrupt params."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    thread_id: str = Field(alias="threadId", min_length=1)
    turn_id: str = Field(alias="turnId", min_length=1)


class CodexThreadStartJsonRpcRequest(BaseModel):
    """JSON-RPC request for thread/start."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: str = Field(min_length=1)
    method: Literal["thread/start"] = "thread/start"
    params: CodexThreadStartParams


class CodexTurnStartJsonRpcRequest(BaseModel):
    """JSON-RPC request for turn/start."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: str = Field(min_length=1)
    method: Literal["turn/start"] = "turn/start"
    params: CodexTurnStartParams


class CodexTurnInterruptJsonRpcRequest(BaseModel):
    """JSON-RPC request for turn/interrupt."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: str = Field(min_length=1)
    method: Literal["turn/interrupt"] = "turn/interrupt"
    params: CodexTurnInterruptParams


class CodexThreadReference(BaseModel):
    """Small validated thread view used by this node."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    id: str = Field(min_length=1)


class CodexTurnError(BaseModel):
    """Small validated Codex turn error view."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    message: str = Field(min_length=1)
    additional_details: str | None = Field(default=None, alias="additionalDetails")


class CodexTurnReference(BaseModel):
    """Small validated turn view used by this node."""

    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    id: str = Field(min_length=1)
    status: CodexTurnStatus
    error: CodexTurnError | None = None


class CodexThreadStartResult(BaseModel):
    """thread/start result subset."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    thread: CodexThreadReference


class CodexTurnStartResult(BaseModel):
    """turn/start result subset."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    turn: CodexTurnReference


class CodexTurnInterruptResult(BaseModel):
    """turn/interrupt result subset."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)


class CodexThreadStartJsonRpcResponse(BaseModel):
    """Successful JSON-RPC response to thread/start."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    id: str = Field(min_length=1)
    result: CodexThreadStartResult


class CodexTurnStartJsonRpcResponse(BaseModel):
    """Successful JSON-RPC response to turn/start."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    id: str = Field(min_length=1)
    result: CodexTurnStartResult


class CodexTurnInterruptJsonRpcResponse(BaseModel):
    """Successful JSON-RPC response to turn/interrupt."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    id: str = Field(min_length=1)
    result: CodexTurnInterruptResult = Field(default_factory=CodexTurnInterruptResult)


class CodexApprovalJsonRpcResult(BaseModel):
    """Client response body for command/file approval requests."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    decision: CodexApprovalDecision


class CodexApprovalJsonRpcResponse(BaseModel):
    """JSON-RPC client response to a Codex command/file approval request."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: CodexJsonRpcRequestId
    result: CodexApprovalJsonRpcResult


class CodexPermissionsApprovalJsonRpcResult(BaseModel):
    """Client response body for Codex permissions approval requests."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    permissions: CodexPermissionProfile
    scope: AgentApprovalScope = "turn"
    strict_auto_review: bool | None = Field(default=None, alias="strictAutoReview")


class CodexPermissionsApprovalJsonRpcResponse(BaseModel):
    """JSON-RPC client response to a Codex permissions approval request."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: CodexJsonRpcRequestId
    result: CodexPermissionsApprovalJsonRpcResult


class CodexToolUserInputAnswerResult(BaseModel):
    """One Codex tool user-input answer value."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    answers: tuple[str, ...] = Field(min_length=1)


class CodexToolUserInputJsonRpcResult(BaseModel):
    """Client response body for item/tool/requestUserInput."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    answers: dict[str, CodexToolUserInputAnswerResult] = Field(min_length=1)


class CodexToolUserInputJsonRpcResponse(BaseModel):
    """JSON-RPC client response to a Codex tool user-input request."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: CodexJsonRpcRequestId
    result: CodexToolUserInputJsonRpcResult


class CodexMcpElicitationJsonRpcResult(BaseModel):
    """Client response body for mcpServer/elicitation/request."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    action: McpElicitationAction
    content: JsonValue | None
    meta: JsonValue | None = Field(alias="_meta")


class CodexMcpElicitationJsonRpcResponse(BaseModel):
    """JSON-RPC client response to an MCP elicitation request."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: CodexJsonRpcRequestId
    result: CodexMcpElicitationJsonRpcResult


CodexServerRequestJsonRpcClientResponse: TypeAlias = (
    CodexApprovalJsonRpcResponse
    | CodexPermissionsApprovalJsonRpcResponse
    | CodexToolUserInputJsonRpcResponse
    | CodexMcpElicitationJsonRpcResponse
)


class CodexJsonRpcErrorBody(BaseModel):
    """JSON-RPC error body."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    code: int
    message: str = Field(min_length=1)


class CodexJsonRpcErrorResponse(BaseModel):
    """JSON-RPC error response."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    id: str = Field(min_length=1)
    error: CodexJsonRpcErrorBody


class CodexConfigWarningParams(BaseModel):
    """Codex config warning notification params."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    summary: str = Field(min_length=1)
    details: str | None = None


class CodexConfigWarningEnvelope(BaseModel):
    """Codex config warning notification."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    method: Literal["configWarning"]
    params: CodexConfigWarningParams


class CodexWarningParams(BaseModel):
    """Codex generic warning notification params."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    message: str = Field(min_length=1)


class CodexWarningEnvelope(BaseModel):
    """Codex generic warning notification."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    method: Literal["warning"]
    params: CodexWarningParams


class CodexDeprecationNoticeEnvelope(BaseModel):
    """Codex deprecation notice notification.

    This is an app-server lifecycle notice, not a turn-stream event. The payload
    is intentionally ignored because fluent-audio only needs to keep the JSON-RPC
    stream aligned.
    """

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    method: Literal["deprecationNotice"]


class CodexRemoteControlStatusParams(BaseModel):
    """Codex remote-control status notification params."""

    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    status: str = Field(min_length=1)
    server_name: str | None = Field(default=None, alias="serverName")
    installation_id: str | None = Field(default=None, alias="installationId")
    environment_id: str | None = Field(default=None, alias="environmentId")


class CodexRemoteControlStatusChangedEnvelope(BaseModel):
    """Codex remote-control status notification."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    method: Literal["remoteControl/status/changed"]
    params: CodexRemoteControlStatusParams


class CodexMcpStartupStatusUpdatedEnvelope(BaseModel):
    """Codex MCP server startup status notification.

    This method is an app-server lifecycle notification, not a turn-stream event.
    The payload is intentionally not projected into the fluent-audio contract.
    """

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    method: Literal["mcpServer/startupStatus/updated"]


class CodexThreadStatusChangedEnvelope(BaseModel):
    """Codex thread lifecycle status notification."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    method: Literal["thread/status/changed"]


class CodexThreadTokenUsageUpdatedEnvelope(BaseModel):
    """Codex token usage telemetry notification."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    method: Literal["thread/tokenUsage/updated"]


class CodexAccountRateLimitsUpdatedEnvelope(BaseModel):
    """Codex account rate-limit telemetry notification."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    method: Literal["account/rateLimits/updated"]


class CodexAgentMessageDeltaParams(BaseModel):
    """Codex item/agentMessage/delta params."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    delta: str = Field(min_length=1)
    item_id: str = Field(alias="itemId", min_length=1)
    thread_id: str = Field(alias="threadId", min_length=1)
    turn_id: str = Field(alias="turnId", min_length=1)


class CodexAgentMessageDeltaEnvelope(BaseModel):
    """Codex agent text delta notification."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    method: Literal["item/agentMessage/delta"]
    params: CodexAgentMessageDeltaParams


class CodexReasoningTextDeltaParams(BaseModel):
    """Codex reasoning text delta params."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    delta: str = Field(min_length=1)
    item_id: str = Field(alias="itemId", min_length=1)
    thread_id: str = Field(alias="threadId", min_length=1)
    turn_id: str = Field(alias="turnId", min_length=1)
    content_index: int = Field(alias="contentIndex", ge=0)


class CodexReasoningTextDeltaEnvelope(BaseModel):
    """Codex reasoning delta notification that is not projected as agent speech."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    method: Literal["item/reasoning/textDelta"]
    params: CodexReasoningTextDeltaParams


class CodexTurnCompletedParams(BaseModel):
    """Codex turn/completed params."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    thread_id: str = Field(alias="threadId", min_length=1)
    turn: CodexTurnReference


class CodexTurnCompletedEnvelope(BaseModel):
    """Codex terminal turn notification."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    method: Literal["turn/completed"]
    params: CodexTurnCompletedParams


class CodexErrorNotificationParams(BaseModel):
    """Codex turn error notification."""

    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    error: CodexTurnError
    thread_id: str = Field(alias="threadId", min_length=1)
    turn_id: str = Field(alias="turnId", min_length=1)
    will_retry: bool = Field(alias="willRetry")


class CodexErrorNotificationEnvelope(BaseModel):
    """Codex error notification."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    method: Literal["error"]
    params: CodexErrorNotificationParams


class CodexMcpToolCallItem(BaseModel):
    """Subset of a Codex MCP tool-call thread item."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    type: Literal["mcpToolCall"]
    id: str = Field(min_length=1)
    server: str = Field(min_length=1)
    tool: str = Field(min_length=1)
    status: CodexToolCallStatus

    def tool_name(self) -> str:
        return f"{self.server}.{self.tool}"


class CodexDynamicToolCallItem(BaseModel):
    """Subset of a Codex dynamic tool-call thread item."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    type: Literal["dynamicToolCall"]
    id: str = Field(min_length=1)
    namespace: str | None = None
    tool: str = Field(min_length=1)
    status: CodexToolCallStatus

    def tool_name(self) -> str:
        if self.namespace is None:
            return self.tool
        return f"{self.namespace}.{self.tool}"


class CodexCommandExecutionItem(BaseModel):
    """Subset of a Codex command execution item."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    type: Literal["commandExecution"]
    id: str = Field(min_length=1)
    status: str = Field(min_length=1)


class CodexFileChangeItem(BaseModel):
    """Subset of a Codex file-change item."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    type: Literal["fileChange"]
    id: str = Field(min_length=1)
    status: str = Field(min_length=1)


class CodexMessageLifecycleItem(BaseModel):
    """Codex message item lifecycle notification that is not projected as a tool."""

    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    type: Literal["userMessage", "agentMessage", "reasoning"]


CodexToolCallItem: TypeAlias = CodexMcpToolCallItem | CodexDynamicToolCallItem
CodexLifecycleItem: TypeAlias = (
    CodexMcpToolCallItem
    | CodexDynamicToolCallItem
    | CodexCommandExecutionItem
    | CodexFileChangeItem
    | CodexMessageLifecycleItem
)
CodexLifecycleItemEnvelope: TypeAlias = Annotated[
    CodexLifecycleItem,
    Field(discriminator="type"),
]


class CodexItemLifecycleParams(BaseModel):
    """Subset of item lifecycle params needed for tool projection."""

    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    thread_id: str = Field(alias="threadId", min_length=1)
    turn_id: str = Field(alias="turnId", min_length=1)
    item: CodexLifecycleItemEnvelope


class CodexItemStartedEnvelope(BaseModel):
    """Codex item/started notification for tool calls."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    method: Literal["item/started"]
    params: CodexItemLifecycleParams


class CodexItemCompletedEnvelope(BaseModel):
    """Codex item/completed notification for tool calls."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    method: Literal["item/completed"]
    params: CodexItemLifecycleParams


class CodexCommandApprovalParams(BaseModel):
    """Subset of command approval request params."""

    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    item_id: str = Field(alias="itemId", min_length=1)
    thread_id: str = Field(alias="threadId", min_length=1)
    turn_id: str = Field(alias="turnId", min_length=1)
    approval_id: str | None = Field(default=None, alias="approvalId")
    command: str | None = None
    reason: str | None = None


class CodexCommandApprovalRequestEnvelope(BaseModel):
    """Server request emitted when Codex asks for command approval."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: CodexJsonRpcRequestId
    method: Literal["item/commandExecution/requestApproval"]
    params: CodexCommandApprovalParams


class CodexFileChangeApprovalParams(BaseModel):
    """Subset of file-change approval request params."""

    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    item_id: str = Field(alias="itemId", min_length=1)
    thread_id: str = Field(alias="threadId", min_length=1)
    turn_id: str = Field(alias="turnId", min_length=1)
    grant_root: str | None = Field(default=None, alias="grantRoot")
    reason: str | None = None


class CodexFileChangeApprovalRequestEnvelope(BaseModel):
    """Server request emitted when Codex asks for file-change approval."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: CodexJsonRpcRequestId
    method: Literal["item/fileChange/requestApproval"]
    params: CodexFileChangeApprovalParams


class CodexPermissionsApprovalParams(BaseModel):
    """Subset of permissions approval request params."""

    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    item_id: str = Field(alias="itemId", min_length=1)
    thread_id: str = Field(alias="threadId", min_length=1)
    turn_id: str = Field(alias="turnId", min_length=1)
    cwd: str = Field(min_length=1)
    permissions: CodexPermissionProfile
    started_at_ms: int = Field(alias="startedAtMs", ge=0)
    environment_id: str | None = Field(default=None, alias="environmentId")
    reason: str | None = None


class CodexPermissionsApprovalRequestEnvelope(BaseModel):
    """Server request emitted when Codex asks for permissions approval."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: CodexJsonRpcRequestId
    method: Literal["item/permissions/requestApproval"]
    params: CodexPermissionsApprovalParams


class CodexToolRequestOption(BaseModel):
    """One Codex tool user-input selectable option."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    label: str = Field(min_length=1)
    description: str = Field(min_length=1)

    def to_contract(self) -> AgentUserInputOption:
        return AgentUserInputOption(
            label=self.label,
            description=self.description,
        )


class CodexToolRequestQuestion(BaseModel):
    """One Codex tool user-input question."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    id: str = Field(min_length=1)
    header: str = Field(min_length=1)
    question: str = Field(min_length=1)
    is_other: bool = Field(alias="isOther")
    is_secret: bool = Field(alias="isSecret")
    options: tuple[CodexToolRequestOption, ...] | None = Field(default=None, min_length=1)

    def to_contract(self) -> AgentUserInputQuestion:
        return AgentUserInputQuestion(
            id=self.id,
            header=self.header,
            question=self.question,
            is_other=self.is_other,
            is_secret=self.is_secret,
            options=tuple(option.to_contract() for option in self.options)
            if self.options is not None
            else None,
        )


class CodexToolUserInputParams(BaseModel):
    """Subset of tool user-input request params."""

    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    item_id: str = Field(alias="itemId", min_length=1)
    thread_id: str = Field(alias="threadId", min_length=1)
    turn_id: str = Field(alias="turnId", min_length=1)
    questions: tuple[CodexToolRequestQuestion, ...] = Field(min_length=1)


class CodexToolUserInputRequestEnvelope(BaseModel):
    """Server request emitted when a Codex tool asks the user a question."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: CodexJsonRpcRequestId
    method: Literal["item/tool/requestUserInput"]
    params: CodexToolUserInputParams


class CodexMcpElicitationBaseParams(BaseModel):
    """Common MCP elicitation request params."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    server_name: str = Field(alias="serverName", min_length=1)
    thread_id: str = Field(alias="threadId", min_length=1)
    turn_id: str | None = Field(default=None, alias="turnId")
    meta: JsonValue | None = Field(default=None, alias="_meta")
    message: str = Field(min_length=1)


class CodexMcpFormElicitationParams(CodexMcpElicitationBaseParams):
    """MCP form-mode elicitation request params."""

    mode: Literal["form"]
    requested_schema: JsonValue = Field(alias="requestedSchema")

    @model_validator(mode="after")
    def validate_requested_schema(self) -> "CodexMcpFormElicitationParams":
        if self.requested_schema is None:
            raise ValueError("MCP form elicitation requires requestedSchema")
        return self


class CodexMcpUrlElicitationParams(CodexMcpElicitationBaseParams):
    """MCP url-mode elicitation request params."""

    mode: Literal["url"]
    elicitation_id: str = Field(alias="elicitationId", min_length=1)
    url: str = Field(min_length=1)


CodexMcpElicitationParams: TypeAlias = Annotated[
    CodexMcpFormElicitationParams | CodexMcpUrlElicitationParams,
    Field(discriminator="mode"),
]


class CodexMcpElicitationRequestEnvelope(BaseModel):
    """Server request emitted when an MCP server asks for elicitation."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    id: CodexJsonRpcRequestId
    method: Literal["mcpServer/elicitation/request"]
    params: CodexMcpElicitationParams


class CodexServerRequestResolvedParams(BaseModel):
    """Server request resolution notification params."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        populate_by_name=True,
    )

    thread_id: str = Field(alias="threadId", min_length=1)
    request_id: CodexJsonRpcRequestId = Field(alias="requestId")


class CodexServerRequestResolvedEnvelope(BaseModel):
    """Notification emitted after a server-initiated request is resolved."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    method: Literal["serverRequest/resolved"]
    params: CodexServerRequestResolvedParams


CodexServerMessage: TypeAlias = (
    CodexAgentMessageDeltaEnvelope
    | CodexReasoningTextDeltaEnvelope
    | CodexTurnCompletedEnvelope
    | CodexErrorNotificationEnvelope
    | CodexItemStartedEnvelope
    | CodexItemCompletedEnvelope
    | CodexCommandApprovalRequestEnvelope
    | CodexFileChangeApprovalRequestEnvelope
    | CodexPermissionsApprovalRequestEnvelope
    | CodexToolUserInputRequestEnvelope
    | CodexMcpElicitationRequestEnvelope
    | CodexServerRequestResolvedEnvelope
)
CodexServerMessageEnvelope: TypeAlias = Annotated[CodexServerMessage, Field(discriminator="method")]
CODEX_SERVER_MESSAGE_ADAPTER = TypeAdapter(CodexServerMessageEnvelope)

CodexIgnorableNotification: TypeAlias = (
    CodexConfigWarningEnvelope
    | CodexWarningEnvelope
    | CodexDeprecationNoticeEnvelope
    | CodexRemoteControlStatusChangedEnvelope
    | CodexMcpStartupStatusUpdatedEnvelope
    | CodexThreadStatusChangedEnvelope
    | CodexThreadTokenUsageUpdatedEnvelope
    | CodexAccountRateLimitsUpdatedEnvelope
)
CodexIgnorableNotificationEnvelope: TypeAlias = Annotated[
    CodexIgnorableNotification,
    Field(discriminator="method"),
]
CODEX_IGNORABLE_NOTIFICATION_ADAPTER = TypeAdapter(CodexIgnorableNotificationEnvelope)


class ProjectedTextDeltaEvent(BaseModel):
    """Validated text delta projected from Codex to DORA."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event: Literal["text_delta"] = "text_delta"
    session_id: str = Field(min_length=1)
    user_turn_id: str = Field(min_length=1)
    agent_turn_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    text: str = Field(min_length=1)

    def to_contract(self) -> AgentTextDelta:
        return AgentTextDelta(
            session_id=self.session_id,
            user_turn_id=self.user_turn_id,
            agent_turn_id=self.agent_turn_id,
            seq=self.seq,
            text=self.text,
        )


class ProjectedTurnDoneEvent(BaseModel):
    """Validated terminal turn event projected from Codex to DORA."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event: Literal["turn_done"] = "turn_done"
    session_id: str = Field(min_length=1)
    user_turn_id: str = Field(min_length=1)
    agent_turn_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    status: ProjectedTurnDoneStatus
    message: str | None = None

    def to_contract(self) -> AgentTurnDone:
        return AgentTurnDone(
            session_id=self.session_id,
            user_turn_id=self.user_turn_id,
            agent_turn_id=self.agent_turn_id,
            seq=self.seq,
            status=self.status,
            message=self.message,
        )


class ProjectedApprovalRequestEvent(BaseModel):
    """Validated approval request projected from Codex to DORA."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event: Literal["approval_request"] = "approval_request"
    session_id: str = Field(min_length=1)
    user_turn_id: str = Field(min_length=1)
    approval_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    prompt: str = Field(min_length=1)
    action_label: str = Field(min_length=1)

    def to_contract(self) -> AgentApprovalRequest:
        return AgentApprovalRequest(
            session_id=self.session_id,
            user_turn_id=self.user_turn_id,
            approval_id=self.approval_id,
            seq=self.seq,
            prompt=self.prompt,
            action_label=self.action_label,
        )


class ProjectedUserInputRequestEvent(BaseModel):
    """Validated user-input request projected from Codex to DORA."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event: Literal["user_input_request"] = "user_input_request"
    session_id: str = Field(min_length=1)
    user_turn_id: str = Field(min_length=1)
    request_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    questions: tuple[AgentUserInputQuestion, ...] = Field(min_length=1)

    def to_contract(self) -> AgentUserInputRequest:
        return AgentUserInputRequest(
            session_id=self.session_id,
            user_turn_id=self.user_turn_id,
            request_id=self.request_id,
            seq=self.seq,
            questions=self.questions,
        )


class ProjectedMcpElicitationRequestEvent(BaseModel):
    """Validated MCP elicitation request projected from Codex to DORA."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event: Literal["mcp_elicitation_request"] = "mcp_elicitation_request"
    session_id: str = Field(min_length=1)
    user_turn_id: str = Field(min_length=1)
    request_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    server_name: str = Field(min_length=1)
    mode: McpElicitationMode
    message: str = Field(min_length=1)
    url: str | None = None
    elicitation_id: str | None = None
    requested_schema: JsonValue | None = None
    meta: JsonValue | None = None

    def to_contract(self) -> AgentMcpElicitationRequest:
        return AgentMcpElicitationRequest(
            session_id=self.session_id,
            user_turn_id=self.user_turn_id,
            request_id=self.request_id,
            seq=self.seq,
            server_name=self.server_name,
            mode=self.mode,
            message=self.message,
            url=self.url,
            elicitation_id=self.elicitation_id,
            requested_schema=self.requested_schema,
            meta=self.meta,
        )


class ProjectedToolEvent(BaseModel):
    """Validated tool lifecycle event projected from Codex to DORA."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event: Literal["tool_event"] = "tool_event"
    session_id: str = Field(min_length=1)
    user_turn_id: str = Field(min_length=1)
    tool_call_id: str = Field(min_length=1)
    tool_name: str = Field(min_length=1)
    tool_event: ProjectedToolEventKind
    seq: int = Field(ge=0)
    summary: str | None = None
    error_message: str | None = None

    def to_contract(self) -> AgentToolEvent:
        return AgentToolEvent(
            session_id=self.session_id,
            user_turn_id=self.user_turn_id,
            tool_call_id=self.tool_call_id,
            tool_name=self.tool_name,
            event=self.tool_event,
            seq=self.seq,
            summary=self.summary,
            error_message=self.error_message,
        )


ProjectedAppServerEvent: TypeAlias = (
    ProjectedTextDeltaEvent
    | ProjectedTurnDoneEvent
    | ProjectedApprovalRequestEvent
    | ProjectedUserInputRequestEvent
    | ProjectedMcpElicitationRequestEvent
    | ProjectedToolEvent
)
AgentApprovalControlEvent: TypeAlias = AgentApprovalResponse | AgentCancelRequest
AgentUserInputControlEvent: TypeAlias = AgentUserInputResponse | AgentCancelRequest
AgentMcpElicitationControlEvent: TypeAlias = AgentMcpElicitationResponse | AgentCancelRequest
ApprovalResponsePathParts: TypeAlias = tuple[str, str, str]


class CodexAppServerTurnStreamSummary(BaseModel):
    """Counters for one app-server turn response stream."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    text_deltas: int = Field(ge=0)
    turn_done: int = Field(ge=0)
    approval_requests: int = Field(ge=0)
    approval_responses: int = Field(ge=0)
    user_input_requests: int = Field(ge=0)
    user_input_responses: int = Field(ge=0)
    mcp_elicitation_requests: int = Field(ge=0)
    mcp_elicitation_responses: int = Field(ge=0)
    cancel_requests: int = Field(ge=0)
    tool_events: int = Field(ge=0)


class CodexAppServerSummary(BaseModel):
    """Validated counters for one DORA node run."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    turn_requests: int = Field(ge=0)
    cancel_requests: int = Field(ge=0)
    text_deltas: int = Field(ge=0)
    turn_done: int = Field(ge=0)
    approval_requests: int = Field(ge=0)
    approval_responses: int = Field(ge=0)
    user_input_requests: int = Field(ge=0)
    user_input_responses: int = Field(ge=0)
    mcp_elicitation_requests: int = Field(ge=0)
    mcp_elicitation_responses: int = Field(ge=0)
    tool_events: int = Field(ge=0)


class CodexApprovalResponseSubmission(BaseModel):
    """Browser/API payload submitted for one pending Codex approval request."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    decision: Literal["accept", "decline", "cancel"]
    scope: AgentApprovalScope = "turn"
    reason: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_decision_scope(self) -> "CodexApprovalResponseSubmission":
        if self.decision != "accept" and self.scope != "turn":
            raise ValueError("scope=session is only valid for accept")
        return self


class CodexControlAccepted(BaseModel):
    """Response returned after one control-plane decision is accepted."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    response: AgentApprovalResponse


class CodexControlQueue:
    """REST control-plane queue owned by the Codex app-server node."""

    def __init__(self) -> None:
        self._condition = threading.Condition()
        self._pending_approval_keys: set[ApprovalResponsePathParts] = set()
        self._answered_approval_keys: set[ApprovalResponsePathParts] = set()
        self._approval_responses: dict[ApprovalResponsePathParts, AgentApprovalResponse] = {}
        self._next_approval_response_seq = 0

    def mark_pending_approval(self, approval: "ProjectedApprovalRequestEvent") -> None:
        key = _approval_response_key(
            approval.session_id,
            approval.user_turn_id,
            approval.approval_id,
        )
        with self._condition:
            if key in self._pending_approval_keys:
                raise CodexAppServerNodeError("duplicate pending approval request")
            if key in self._answered_approval_keys:
                raise CodexAppServerNodeError("approval request was already answered")
            self._pending_approval_keys.add(key)

    def submit_approval_response(
        self,
        key: ApprovalResponsePathParts,
        submission: CodexApprovalResponseSubmission,
    ) -> CodexControlAccepted:
        with self._condition:
            if key not in self._pending_approval_keys:
                raise CodexAppServerNodeError(
                    "approval response does not match a pending Codex request"
                )
            if key in self._answered_approval_keys:
                raise CodexAppServerNodeError("approval request already has a response")
            session_id, user_turn_id, approval_id = key
            response = AgentApprovalResponse(
                session_id=session_id,
                user_turn_id=user_turn_id,
                approval_id=approval_id,
                seq=self._next_approval_response_seq,
                decision=submission.decision,
                scope=submission.scope,
                reason=submission.reason,
            )
            self._next_approval_response_seq += 1
            self._approval_responses[key] = response
            self._answered_approval_keys.add(key)
            self._condition.notify_all()
            return CodexControlAccepted(response=response)

    def wait_for_approval_response(
        self,
        approval: "ProjectedApprovalRequestEvent",
        *,
        timeout_seconds: float,
    ) -> AgentApprovalResponse | None:
        key = _approval_response_key(
            approval.session_id,
            approval.user_turn_id,
            approval.approval_id,
        )
        with self._condition:
            self._condition.wait_for(
                lambda: key in self._approval_responses,
                timeout=timeout_seconds,
            )
            response = self._approval_responses.pop(key, None)
            if response is None:
                return None
            self._pending_approval_keys.discard(key)
            return response

    def cancel_pending_approval(self, approval: "ProjectedApprovalRequestEvent") -> None:
        key = _approval_response_key(
            approval.session_id,
            approval.user_turn_id,
            approval.approval_id,
        )
        with self._condition:
            self._pending_approval_keys.discard(key)


class CodexThreadState(BaseModel):
    """Local mapping from a DORA voice session to a Codex thread."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: str = Field(min_length=1)
    thread_id: str = Field(min_length=1)


class CodexActiveTurn(BaseModel):
    """Local mapping from a DORA voice session to an active Codex turn."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: str = Field(min_length=1)
    thread_id: str = Field(min_length=1)
    turn_id: str = Field(min_length=1)


class PendingCodexUserInputRequest(BaseModel):
    """Pending Codex user-input request awaiting a DORA response."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: str = Field(min_length=1)
    user_turn_id: str = Field(min_length=1)
    request_id: str = Field(min_length=1)
    codex_request_id: CodexJsonRpcRequestId
    question_ids: tuple[str, ...] = Field(min_length=1)


class PendingCodexMcpElicitationRequest(BaseModel):
    """Pending Codex MCP elicitation request awaiting a DORA response."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: str = Field(min_length=1)
    user_turn_id: str = Field(min_length=1)
    request_id: str = Field(min_length=1)
    codex_request_id: CodexJsonRpcRequestId
    mode: McpElicitationMode


class PendingCodexApproval(BaseModel):
    """Pending Codex server request awaiting a DORA approval response."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: str = Field(min_length=1)
    user_turn_id: str = Field(min_length=1)
    approval_id: str = Field(min_length=1)
    request_id: CodexJsonRpcRequestId
    kind: PendingApprovalKind
    requested_permissions: CodexPermissionProfile | None = None

    @model_validator(mode="after")
    def validate_variant_payload(self) -> "PendingCodexApproval":
        if self.kind == "permissions" and self.requested_permissions is None:
            raise ValueError("permissions approvals require requested_permissions")
        if self.kind != "permissions" and self.requested_permissions is not None:
            raise ValueError("requested_permissions is only valid for permissions approvals")
        return self


class TurnProjectionState(BaseModel):
    """State used while projecting one Codex turn to DORA events."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    next_seq: int = Field(default=0, ge=0)

    def advance(self) -> "TurnProjectionState":
        return TurnProjectionState(next_seq=self.next_seq + 1)


def _read_text_stream_lines(
    stream: TextIO,
    destination: queue.Queue[str | None],
) -> None:
    try:
        for line in stream:
            destination.put(line)
    finally:
        destination.put(None)


class CodexAppServerTransport(Protocol):
    """Codex app-server boundary used by the node runtime and tests."""

    def stream_turn(self, request: AgentTurnRequest) -> Iterable[ProjectedAppServerEvent]:
        """Start one Codex turn and return projected DORA-facing events."""

    def respond_approval(self, response: AgentApprovalResponse) -> None:
        """Resolve one pending Codex approval request."""

    def respond_user_input(self, response: AgentUserInputResponse) -> None:
        """Resolve one pending Codex tool user-input request."""

    def respond_mcp_elicitation(self, response: AgentMcpElicitationResponse) -> None:
        """Resolve one pending Codex MCP elicitation request."""

    def interrupt_turn(self, request: AgentCancelRequest) -> None:
        """Interrupt the currently active Codex turn for the session."""


class SubprocessCodexJsonRpcTransport:
    """Line-oriented stdio JSON-RPC transport for `codex app-server`."""

    def __init__(self, config: CodexAppServerConfig) -> None:
        self._config = config
        self._request_seq = 0
        self._thread_by_session: dict[str, CodexThreadState] = {}
        self._active_turn_by_session: dict[str, CodexActiveTurn] = {}
        self._pending_approval_by_id: dict[str, PendingCodexApproval] = {}
        self._pending_user_input_by_id: dict[str, PendingCodexUserInputRequest] = {}
        self._pending_mcp_elicitation_by_id: dict[str, PendingCodexMcpElicitationRequest] = {}
        self._pending_messages: list[CodexServerMessage] = []
        self._process = subprocess.Popen(
            config.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=config.cwd,
        )
        stdout = self._process.stdout
        if stdout is None:
            raise CodexAppServerNodeError("Codex app-server stdout is not available")
        stderr = self._process.stderr
        if stderr is None:
            raise CodexAppServerNodeError("Codex app-server stderr is not available")
        self._stdout_lines: queue.Queue[str | None] = queue.Queue()
        self._stderr_lines: queue.Queue[str | None] = queue.Queue()
        self._stdout_reader = threading.Thread(
            target=_read_text_stream_lines,
            args=(stdout, self._stdout_lines),
            daemon=True,
        )
        self._stderr_reader = threading.Thread(
            target=_read_text_stream_lines,
            args=(stderr, self._stderr_lines),
            daemon=True,
        )
        self._stdout_reader.start()
        self._stderr_reader.start()
        self._initialize()

    def close(self) -> None:
        if self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait(timeout=2.0)
        self._stdout_reader.join(timeout=0.2)
        self._stderr_reader.join(timeout=0.2)

    def ensure_thread_started(self, session_id: str) -> CodexThreadState:
        """Start or reuse a Codex thread without starting a model turn."""

        return self._ensure_thread(session_id)

    def stream_turn(self, request: AgentTurnRequest) -> Iterable[ProjectedAppServerEvent]:
        thread = self._ensure_thread(request.session_id)
        turn_response = self._send_turn_start(thread, request)
        active_turn = CodexActiveTurn(
            session_id=request.session_id,
            thread_id=thread.thread_id,
            turn_id=turn_response.result.turn.id,
        )
        self._active_turn_by_session[request.session_id] = active_turn
        try:
            yield from self._read_projected_turn_events(request, active_turn)
        finally:
            stored_active_turn = self._active_turn_by_session.get(request.session_id)
            if stored_active_turn == active_turn:
                del self._active_turn_by_session[request.session_id]

    def respond_approval(self, response: AgentApprovalResponse) -> None:
        pending = self._pending_approval_by_id.get(response.approval_id)
        if pending is None:
            raise CodexAppServerNodeError("approval response did not match a pending Codex request")
        if pending.session_id != response.session_id:
            raise CodexAppServerNodeError("approval response session_id did not match pending request")
        if pending.user_turn_id != response.user_turn_id:
            raise CodexAppServerNodeError(
                "approval response user_turn_id did not match pending request"
            )
        self._write_model(_build_codex_approval_response(pending, response))
        del self._pending_approval_by_id[response.approval_id]

    def respond_user_input(self, response: AgentUserInputResponse) -> None:
        pending = self._pending_user_input_by_id.get(response.request_id)
        if pending is None:
            raise CodexAppServerNodeError(
                "user-input response did not match a pending Codex request"
            )
        _validate_user_input_response_matches_pending(response, pending)
        self._write_model(_build_codex_user_input_response(pending, response))
        del self._pending_user_input_by_id[response.request_id]

    def respond_mcp_elicitation(self, response: AgentMcpElicitationResponse) -> None:
        pending = self._pending_mcp_elicitation_by_id.get(response.request_id)
        if pending is None:
            raise CodexAppServerNodeError(
                "MCP elicitation response did not match a pending Codex request"
            )
        _validate_mcp_elicitation_response_matches_pending(response, pending)
        self._write_model(_build_codex_mcp_elicitation_response(pending, response))
        del self._pending_mcp_elicitation_by_id[response.request_id]

    def interrupt_turn(self, request: AgentCancelRequest) -> None:
        active_turn = self._active_turn_by_session.get(request.session_id)
        if active_turn is None:
            raise CodexAppServerNodeError("cannot interrupt Codex turn before turn/start")
        request_id = self._next_request_id("turn-interrupt")
        params = CodexTurnInterruptParams(
            thread_id=active_turn.thread_id,
            turn_id=active_turn.turn_id,
        )
        self._write_model(
            CodexTurnInterruptJsonRpcRequest(id=request_id, params=params),
        )
        _ = self._read_turn_interrupt_response(request_id)
        del self._active_turn_by_session[request.session_id]

    def _initialize(self) -> None:
        request_id = self._next_request_id("initialize")
        self._write_model(
            CodexInitializeJsonRpcRequest(
                id=request_id,
                params=CodexInitializeParams(
                    client_info=CodexClientInfo(
                        name=self._config.client_name,
                        version=self._config.client_version,
                    )
                ),
            )
        )
        _ = self._read_initialize_response(request_id)
        self._write_model(CodexInitializedNotification())

    def _ensure_thread(self, session_id: str) -> CodexThreadState:
        existing = self._thread_by_session.get(session_id)
        if existing is not None:
            return existing

        request_id = self._next_request_id("thread-start")
        params = CodexThreadStartParams(
            ephemeral=True,
            cwd=self._config.cwd,
            model=self._config.model,
            model_provider=self._config.model_provider,
            base_instructions=self._config.base_instructions,
            developer_instructions=self._config.developer_instructions,
            sandbox=self._config.sandbox,
            approval_policy=self._config.approval_policy,
            approvals_reviewer=self._config.approvals_reviewer,
        )
        self._write_model(CodexThreadStartJsonRpcRequest(id=request_id, params=params))
        response = self._read_thread_start_response(request_id)
        thread = CodexThreadState(
            session_id=session_id,
            thread_id=response.result.thread.id,
        )
        self._thread_by_session[session_id] = thread
        return thread

    def _read_initialize_response(self, request_id: str) -> CodexInitializeJsonRpcResponse:
        while True:
            line = self._read_line()
            try:
                response = CodexInitializeJsonRpcResponse.model_validate_json(line)
            except ValueError:
                self._handle_non_response_line(line, request_id)
                continue
            self._validate_response_id(response.id, request_id)
            return response

    def _send_turn_start(
        self,
        thread: CodexThreadState,
        request: AgentTurnRequest,
    ) -> CodexTurnStartJsonRpcResponse:
        request_id = self._next_request_id("turn-start")
        params = CodexTurnStartParams(
            thread_id=thread.thread_id,
            input=(CodexTextUserInput(text=request.text),),
            client_user_message_id=request.user_turn_id,
        )
        self._write_model(CodexTurnStartJsonRpcRequest(id=request_id, params=params))
        response = self._read_turn_start_response(request_id)
        if response.result.turn.status not in ("inProgress", "completed"):
            raise CodexAppServerNodeError(
                f"turn/start returned unexpected status {response.result.turn.status!r}"
            )
        return response

    def _read_projected_turn_events(
        self,
        turn: AgentTurnRequest,
        active_turn: CodexActiveTurn,
    ) -> Iterable[ProjectedAppServerEvent]:
        projection = TurnProjectionState()
        while True:
            message = self._read_next_server_message()
            event = project_codex_server_message(
                turn,
                active_turn,
                message,
                seq=projection.next_seq,
            )
            if event is None:
                continue
            self._track_pending_server_request(turn, message, event)
            projection = projection.advance()
            yield event
            if isinstance(event, ProjectedTurnDoneEvent):
                return

    def _track_pending_server_request(
        self,
        turn: AgentTurnRequest,
        message: CodexServerMessage,
        event: ProjectedAppServerEvent,
    ) -> None:
        if isinstance(event, ProjectedApprovalRequestEvent):
            self._track_pending_approval(turn, message, event)
            return
        if isinstance(event, ProjectedUserInputRequestEvent):
            self._track_pending_user_input(turn, message, event)
            return
        if isinstance(event, ProjectedMcpElicitationRequestEvent):
            self._track_pending_mcp_elicitation(turn, message, event)

    def _track_pending_approval(
        self,
        turn: AgentTurnRequest,
        message: CodexServerMessage,
        event: ProjectedApprovalRequestEvent,
    ) -> None:
        requested_permissions: CodexPermissionProfile | None = None
        if isinstance(message, CodexCommandApprovalRequestEnvelope):
            kind: PendingApprovalKind = "command"
        elif isinstance(message, CodexFileChangeApprovalRequestEnvelope):
            kind = "file_change"
        elif isinstance(message, CodexPermissionsApprovalRequestEnvelope):
            kind = "permissions"
            requested_permissions = message.params.permissions
        else:
            raise CodexAppServerNodeError("approval event was produced from unsupported request kind")
        if event.approval_id in self._pending_approval_by_id:
            raise CodexAppServerNodeError("duplicate pending approval_id from Codex")
        self._pending_approval_by_id[event.approval_id] = PendingCodexApproval(
            session_id=turn.session_id,
            user_turn_id=turn.user_turn_id,
            approval_id=event.approval_id,
            request_id=message.id,
            kind=kind,
            requested_permissions=requested_permissions,
        )

    def _track_pending_user_input(
        self,
        turn: AgentTurnRequest,
        message: CodexServerMessage,
        event: ProjectedUserInputRequestEvent,
    ) -> None:
        if not isinstance(message, CodexToolUserInputRequestEnvelope):
            raise CodexAppServerNodeError(
                "user-input event was produced from unsupported request kind"
            )
        if event.request_id in self._pending_user_input_by_id:
            raise CodexAppServerNodeError("duplicate pending user-input request_id from Codex")
        self._pending_user_input_by_id[event.request_id] = PendingCodexUserInputRequest(
            session_id=turn.session_id,
            user_turn_id=turn.user_turn_id,
            request_id=event.request_id,
            codex_request_id=message.id,
            question_ids=tuple(question.id for question in event.questions),
        )

    def _track_pending_mcp_elicitation(
        self,
        turn: AgentTurnRequest,
        message: CodexServerMessage,
        event: ProjectedMcpElicitationRequestEvent,
    ) -> None:
        if not isinstance(message, CodexMcpElicitationRequestEnvelope):
            raise CodexAppServerNodeError(
                "MCP elicitation event was produced from unsupported request kind"
            )
        if event.request_id in self._pending_mcp_elicitation_by_id:
            raise CodexAppServerNodeError("duplicate pending MCP elicitation request_id from Codex")
        self._pending_mcp_elicitation_by_id[event.request_id] = (
            PendingCodexMcpElicitationRequest(
                session_id=turn.session_id,
                user_turn_id=turn.user_turn_id,
                request_id=event.request_id,
                codex_request_id=message.id,
                mode=event.mode,
            )
        )

    def _read_thread_start_response(self, request_id: str) -> CodexThreadStartJsonRpcResponse:
        while True:
            line = self._read_line()
            try:
                response = CodexThreadStartJsonRpcResponse.model_validate_json(line)
            except ValueError:
                self._handle_non_response_line(line, request_id)
                continue
            self._validate_response_id(response.id, request_id)
            return response

    def _read_turn_start_response(self, request_id: str) -> CodexTurnStartJsonRpcResponse:
        while True:
            line = self._read_line()
            try:
                response = CodexTurnStartJsonRpcResponse.model_validate_json(line)
            except ValueError:
                self._handle_non_response_line(line, request_id)
                continue
            self._validate_response_id(response.id, request_id)
            return response

    def _read_turn_interrupt_response(
        self,
        request_id: str,
    ) -> CodexTurnInterruptJsonRpcResponse:
        while True:
            line = self._read_line()
            try:
                response = CodexTurnInterruptJsonRpcResponse.model_validate_json(line)
            except ValueError:
                self._handle_non_response_line(line, request_id)
                continue
            self._validate_response_id(response.id, request_id)
            return response

    def _handle_non_response_line(self, line: str, request_id: str) -> None:
        try:
            error_response = CodexJsonRpcErrorResponse.model_validate_json(line)
        except ValueError:
            if parse_codex_ignorable_notification_line(line) is not None:
                return
            message = parse_codex_server_message_line(line)
            if message is None:
                return
            self._pending_messages.append(message)
            return
        self._validate_response_id(error_response.id, request_id)
        raise CodexAppServerNodeError(
            f"Codex JSON-RPC error {error_response.error.code}: "
            f"{error_response.error.message}"
        )

    def _read_next_server_message(self) -> CodexServerMessage:
        if self._pending_messages:
            return self._pending_messages.pop(0)
        while True:
            line = self._read_line()
            if parse_codex_ignorable_notification_line(line) is not None:
                continue
            message = parse_codex_server_message_line(line)
            if message is not None:
                return message

    def _read_line(self) -> str:
        try:
            line = self._stdout_lines.get(timeout=self._config.timeout_seconds)
        except queue.Empty:
            stderr_output = self._read_stderr_tail()
            if self._process.poll() is not None:
                raise CodexAppServerNodeError(
                    "Codex app-server exited before producing a complete response: "
                    f"{stderr_output}"
                )
            if stderr_output:
                raise CodexAppServerNodeError(
                    "timed out waiting for Codex app-server output; stderr: "
                    f"{stderr_output}"
                )
            raise CodexAppServerNodeError("timed out waiting for Codex app-server output")
        if line is None:
            stderr_output = self._read_stderr_tail()
            raise CodexAppServerNodeError(
                f"Codex app-server exited before producing a complete response: {stderr_output}"
            )
        return line

    def _read_stderr_tail(self) -> str:
        lines: list[str] = []
        while True:
            try:
                line = self._stderr_lines.get_nowait()
            except queue.Empty:
                break
            if line is not None:
                stripped = line.rstrip()
                if stripped:
                    lines.append(stripped)
        return "\n".join(lines[-20:])

    def _write_model(self, message: BaseModel) -> None:
        stdin = self._process.stdin
        if stdin is None:
            raise CodexAppServerNodeError("Codex app-server stdin is not available")
        exclude_none = not isinstance(message, CodexMcpElicitationJsonRpcResponse)
        stdin.write(message.model_dump_json(by_alias=True, exclude_none=exclude_none))
        stdin.write("\n")
        stdin.flush()

    def _next_request_id(self, prefix: str) -> str:
        self._request_seq += 1
        return f"fluent-audio/{prefix}/{self._request_seq}"

    def _validate_response_id(self, response_id: str, request_id: str) -> None:
        if response_id != request_id:
            raise CodexAppServerNodeError(
                f"Codex JSON-RPC response id {response_id!r} did not match {request_id!r}"
            )


def parse_codex_server_message_line(line: str) -> CodexServerMessage | None:
    """Parse one Codex JSON-RPC server notification/request line."""

    stripped = line.strip()
    if stripped == "":
        return None
    try:
        return CODEX_SERVER_MESSAGE_ADAPTER.validate_json(stripped)
    except ValueError as exc:
        raise CodexAppServerNodeError("Codex server message line is invalid") from exc


def parse_codex_ignorable_notification_line(line: str) -> CodexIgnorableNotification | None:
    """Parse one Codex notification that is not part of a turn stream."""

    stripped = line.strip()
    if stripped == "":
        return None
    try:
        return CODEX_IGNORABLE_NOTIFICATION_ADAPTER.validate_json(stripped)
    except ValueError:
        return None


def project_codex_server_message(
    turn: AgentTurnRequest,
    active_turn: CodexActiveTurn,
    message: CodexServerMessage,
    *,
    seq: int,
) -> ProjectedAppServerEvent | None:
    """Project one Codex server message into the existing DORA agent contract."""

    if isinstance(message, CodexAgentMessageDeltaEnvelope):
        _validate_message_turn(active_turn, message.params.thread_id, message.params.turn_id)
        return ProjectedTextDeltaEvent(
            session_id=turn.session_id,
            user_turn_id=turn.user_turn_id,
            agent_turn_id=turn.assistant_turn_id,
            seq=seq,
            text=message.params.delta,
        )
    if isinstance(message, CodexReasoningTextDeltaEnvelope):
        _validate_message_turn(active_turn, message.params.thread_id, message.params.turn_id)
        return None
    if isinstance(message, CodexTurnCompletedEnvelope):
        _validate_message_turn(active_turn, message.params.thread_id, message.params.turn.id)
        return ProjectedTurnDoneEvent(
            session_id=turn.session_id,
            user_turn_id=turn.user_turn_id,
            agent_turn_id=turn.assistant_turn_id,
            seq=seq,
            status=_project_turn_status(message.params.turn),
            message=_project_turn_message(message.params.turn),
        )
    if isinstance(message, CodexErrorNotificationEnvelope):
        _validate_message_turn(active_turn, message.params.thread_id, message.params.turn_id)
        retry_state = "retrying" if message.params.will_retry else "terminal"
        raise CodexAppServerNodeError(
            f"Codex emitted {retry_state} turn error: {message.params.error.message}"
        )
    if isinstance(message, CodexItemStartedEnvelope | CodexItemCompletedEnvelope):
        _validate_message_turn(active_turn, message.params.thread_id, message.params.turn_id)
        if isinstance(
            message.params.item,
            CodexCommandExecutionItem | CodexFileChangeItem | CodexMessageLifecycleItem,
        ):
            return None
        return _project_tool_event(turn, message.params.item, seq)
    if isinstance(message, CodexCommandApprovalRequestEnvelope):
        _validate_message_turn(active_turn, message.params.thread_id, message.params.turn_id)
        return _project_command_approval(turn, message, seq)
    if isinstance(message, CodexFileChangeApprovalRequestEnvelope):
        _validate_message_turn(active_turn, message.params.thread_id, message.params.turn_id)
        return _project_file_change_approval(turn, message, seq)
    if isinstance(message, CodexPermissionsApprovalRequestEnvelope):
        _validate_message_turn(active_turn, message.params.thread_id, message.params.turn_id)
        return _project_permissions_approval(turn, message, seq)
    if isinstance(message, CodexToolUserInputRequestEnvelope):
        _validate_message_turn(active_turn, message.params.thread_id, message.params.turn_id)
        return _project_user_input_request(turn, message, seq)
    if isinstance(message, CodexMcpElicitationRequestEnvelope):
        if message.params.turn_id is None:
            raise CodexAppServerNodeError("MCP elicitation without turnId cannot be routed")
        _validate_message_turn(active_turn, message.params.thread_id, message.params.turn_id)
        return _project_mcp_elicitation_request(turn, message, seq)
    if isinstance(message, CodexServerRequestResolvedEnvelope):
        if message.params.thread_id != active_turn.thread_id:
            raise CodexAppServerNodeError("resolved server request threadId did not match active thread")
        return None
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Codex app-server DORA boundary.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--approval-response-timeout-seconds", type=float, default=300.0)
    parser.add_argument("--poll-dora-control-during-approval", action="store_true")
    parser.add_argument("--cwd")
    parser.add_argument("--model")
    parser.add_argument("--model-provider")
    parser.add_argument("--base-instructions")
    parser.add_argument("--base-instructions-file", type=Path)
    parser.add_argument("--developer-instructions")
    parser.add_argument("--developer-instructions-file", type=Path)
    parser.add_argument(
        "--sandbox",
        choices=("read-only", "workspace-write", "danger-full-access"),
    )
    parser.add_argument(
        "--approval-policy",
        choices=("untrusted", "on-failure", "on-request", "never"),
        default="on-request",
    )
    parser.add_argument(
        "--approvals-reviewer",
        choices=("user", "auto_review"),
        default="user",
    )
    parser.add_argument(
        "--app-server-command",
        nargs=argparse.REMAINDER,
        help="Command used for the JSON-RPC stdio app-server. Defaults to Codex.",
    )
    parser.add_argument(
        "--app-server-command-json",
        help="JSON array command used for the JSON-RPC stdio app-server.",
    )
    parser.add_argument(
        "--app-server-command-file",
        type=Path,
        help="Path to a UTF-8 file containing one app-server command argument per line.",
    )
    parser.add_argument("--control-host", default="127.0.0.1")
    parser.add_argument("--control-port", type=int)
    return parser


def resolve_app_server_command(
    *,
    command_remainder: Sequence[str],
    command_json: str | None,
    command_file: Path | None,
) -> tuple[str, ...]:
    specified_sources = sum(
        (
            bool(command_remainder),
            command_json is not None,
            command_file is not None,
        )
    )
    if specified_sources > 1:
        raise CodexAppServerNodeError(
            "Specify only one of --app-server-command, --app-server-command-json, "
            "or --app-server-command-file"
        )
    if command_file is not None:
        return _read_app_server_command_file(command_file)
    if command_json is not None:
        return _parse_app_server_command_json(command_json)
    if command_remainder:
        return tuple(command_remainder)
    return ("codex", "app-server", "--listen", "stdio://")


def _parse_app_server_command_json(command_json: str) -> tuple[str, ...]:
    try:
        command = CODEX_APP_SERVER_COMMAND_JSON_ADAPTER.validate_json(command_json)
    except ValueError as exc:
        raise CodexAppServerNodeError("--app-server-command-json must be a JSON string array") from exc
    if not command:
        raise CodexAppServerNodeError("--app-server-command-json must not be empty")
    return command


def _read_app_server_command_file(path: Path) -> tuple[str, ...]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise CodexAppServerNodeError(f"failed to read app-server command file: {path}") from exc
    stripped_lines = tuple(line.strip() for line in lines)
    command_lines = tuple(line for line in stripped_lines if line and not line.startswith("#"))
    try:
        command = CODEX_APP_SERVER_COMMAND_FILE_ADAPTER.validate_python(command_lines)
    except ValueError as exc:
        raise CodexAppServerNodeError("app-server command file must contain non-empty strings") from exc
    if not command:
        raise CodexAppServerNodeError("app-server command file must not be empty")
    return command


def resolve_instruction_text(
    *,
    inline_text: str | None,
    text_file: Path | None,
    label: str,
) -> str | None:
    if inline_text is not None and text_file is not None:
        raise CodexAppServerNodeError(f"Specify only one of --{label} or --{label}-file")
    if text_file is None:
        return inline_text
    try:
        resolved = text_file.read_text(encoding="utf-8")
    except OSError as exc:
        raise CodexAppServerNodeError(f"failed to read --{label}-file: {text_file}") from exc
    if resolved == "":
        raise CodexAppServerNodeError(f"--{label}-file must not be empty")
    return resolved


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("codex_app_server requires --dora")

    from dora import Node

    try:
        command = resolve_app_server_command(
            command_remainder=tuple(args.app_server_command or ()),
            command_json=args.app_server_command_json,
            command_file=args.app_server_command_file,
        )
    except CodexAppServerNodeError as exc:
        parser.error(str(exc))
    try:
        base_instructions = resolve_instruction_text(
            inline_text=args.base_instructions,
            text_file=args.base_instructions_file,
            label="base-instructions",
        )
        developer_instructions = resolve_instruction_text(
            inline_text=args.developer_instructions,
            text_file=args.developer_instructions_file,
            label="developer-instructions",
        )
    except CodexAppServerNodeError as exc:
        parser.error(str(exc))
    config = CodexAppServerConfig(
        command=command,
        timeout_seconds=args.timeout_seconds,
        approval_response_timeout_seconds=args.approval_response_timeout_seconds,
        poll_dora_control_during_approval=args.poll_dora_control_during_approval,
        cwd=args.cwd,
        model=args.model,
        model_provider=args.model_provider,
        base_instructions=base_instructions,
        developer_instructions=developer_instructions,
        sandbox=args.sandbox,
        approval_policy=args.approval_policy,
        approvals_reviewer=args.approvals_reviewer,
    )
    transport = SubprocessCodexJsonRpcTransport(config)
    control_queue = CodexControlQueue()
    control_server: ThreadingHTTPServer | None = None
    control_thread: threading.Thread | None = None
    if args.control_port is not None:
        control_server = build_codex_control_server(
            args.control_host,
            args.control_port,
            control_queue,
        )
        control_thread = threading.Thread(target=control_server.serve_forever, daemon=True)
        control_thread.start()
    try:
        summary = run_codex_app_server_events(
            Node(),
            transport,
            control_queue=control_queue,
            approval_response_timeout_seconds=config.approval_response_timeout_seconds,
            poll_dora_control_during_approval=config.poll_dora_control_during_approval,
        )
    finally:
        if control_server is not None:
            control_server.shutdown()
            control_server.server_close()
        if control_thread is not None:
            control_thread.join(timeout=2.0)
        transport.close()
    sys.stdout.write(summary.model_dump_json())
    sys.stdout.write("\n")
    return 0


def build_codex_control_server(
    host: str,
    port: int,
    control_queue: CodexControlQueue,
) -> ThreadingHTTPServer:
    """Build the REST control endpoint owned by the Codex node."""

    class ReusableHTTPServer(ThreadingHTTPServer):
        allow_reuse_address = True

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if urllib.parse.urlparse(self.path).path == "/health":
                _send_http_bytes(self, 200, b"ok", content_type="text/plain")
                return
            _send_http_error(self, 404, "Not found")

        def do_POST(self) -> None:
            parsed_path = urllib.parse.urlparse(self.path)
            approval_key = _approval_response_path_parts(parsed_path.path)
            if approval_key is None:
                _send_http_error(self, 404, "Not found")
                return
            try:
                request_body = _read_required_request_body(self)
            except RequestBodyBoundaryError as exc:
                _send_http_error(self, exc.status_code, str(exc))
                return
            try:
                submission = CodexApprovalResponseSubmission.model_validate_json(request_body)
            except ValueError:
                _send_http_error(self, 400, "Invalid approval response submission")
                return
            try:
                accepted = control_queue.submit_approval_response(approval_key, submission)
            except CodexAppServerNodeError as exc:
                _send_http_error(self, 409, str(exc))
                return
            _send_http_model(self, 200, accepted)

        def log_message(self, format: str, *args: str) -> None:
            return

    return ReusableHTTPServer((host, port), Handler)


def run_codex_app_server_events(
    node,
    transport: CodexAppServerTransport,
    *,
    control_queue: CodexControlQueue | None = None,
    approval_response_timeout_seconds: float = 300.0,
    poll_dora_control_during_approval: bool = False,
) -> CodexAppServerSummary:
    if control_queue is None:
        control_queue = CodexControlQueue()
    turn_requests = 0
    cancel_requests = 0
    text_deltas = 0
    turn_done = 0
    approval_requests = 0
    approval_responses = 0
    user_input_requests = 0
    user_input_responses = 0
    mcp_elicitation_requests = 0
    mcp_elicitation_responses = 0
    tool_events = 0

    for event in node:
        if event is None:
            raise CodexAppServerNodeError("DORA event stream ended before STOP")
        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            return CodexAppServerSummary(
                turn_requests=turn_requests,
                cancel_requests=cancel_requests,
                text_deltas=text_deltas,
                turn_done=turn_done,
                approval_requests=approval_requests,
                approval_responses=approval_responses,
                user_input_requests=user_input_requests,
                user_input_responses=user_input_responses,
                mcp_elicitation_requests=mcp_elicitation_requests,
                mcp_elicitation_responses=mcp_elicitation_responses,
                tool_events=tool_events,
            )
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id == "agent_turn":
                return CodexAppServerSummary(
                    turn_requests=turn_requests,
                    cancel_requests=cancel_requests,
                    text_deltas=text_deltas,
                    turn_done=turn_done,
                    approval_requests=approval_requests,
                    approval_responses=approval_responses,
                    user_input_requests=user_input_requests,
                    user_input_responses=user_input_responses,
                    mcp_elicitation_requests=mcp_elicitation_requests,
                    mcp_elicitation_responses=mcp_elicitation_responses,
                    tool_events=tool_events,
                )
            if input_id not in (
                "agent_cancel",
                "agent_user_input_response",
                "agent_mcp_elicitation_response",
            ):
                raise CodexAppServerNodeError(f"Unexpected DORA input id: {input_id!r}")
            continue
        if event_type != "INPUT":
            raise CodexAppServerNodeError(f"Unexpected DORA event type: {event_type!r}")

        input_id = _required_event_text(event, "id")
        if input_id == "agent_turn":
            turn = _decode_agent_turn_event(event)
            stream_summary = _stream_turn_and_send_outputs(
                node,
                transport,
                control_queue,
                turn,
                approval_response_timeout_seconds=approval_response_timeout_seconds,
                poll_dora_control_during_approval=poll_dora_control_during_approval,
            )
            turn_requests += 1
            cancel_requests += stream_summary.cancel_requests
            text_deltas += stream_summary.text_deltas
            turn_done += stream_summary.turn_done
            approval_requests += stream_summary.approval_requests
            approval_responses += stream_summary.approval_responses
            user_input_requests += stream_summary.user_input_requests
            user_input_responses += stream_summary.user_input_responses
            mcp_elicitation_requests += stream_summary.mcp_elicitation_requests
            mcp_elicitation_responses += stream_summary.mcp_elicitation_responses
            tool_events += stream_summary.tool_events
        elif input_id == "agent_cancel":
            cancel = _decode_agent_cancel_event(event)
            transport.interrupt_turn(cancel)
            cancel_requests += 1
        elif input_id == "agent_user_input_response":
            raise CodexAppServerNodeError(
                "user-input response arrived without a pending user-input request"
            )
        elif input_id == "agent_mcp_elicitation_response":
            raise CodexAppServerNodeError(
                "MCP elicitation response arrived without a pending MCP elicitation request"
            )
        else:
            raise CodexAppServerNodeError(f"Unexpected DORA input id: {input_id!r}")

    raise CodexAppServerNodeError("DORA event stream ended before STOP")


def _stream_turn_and_send_outputs(
    node,
    transport: CodexAppServerTransport,
    control_queue: CodexControlQueue,
    turn: AgentTurnRequest,
    *,
    approval_response_timeout_seconds: float,
    poll_dora_control_during_approval: bool,
) -> CodexAppServerTurnStreamSummary:
    text_deltas = 0
    turn_done = 0
    approval_requests = 0
    approval_responses = 0
    user_input_requests = 0
    user_input_responses = 0
    mcp_elicitation_requests = 0
    mcp_elicitation_responses = 0
    cancel_requests = 0
    tool_events = 0

    for app_server_event in transport.stream_turn(turn):
        if turn_done:
            raise CodexAppServerNodeError("Codex emitted event after turn_done")
        if isinstance(app_server_event, ProjectedTextDeltaEvent):
            _send_agent_text(node, app_server_event.to_contract())
            text_deltas += 1
        elif isinstance(app_server_event, ProjectedTurnDoneEvent):
            _send_agent_done(node, app_server_event.to_contract())
            turn_done += 1
        elif isinstance(app_server_event, ProjectedApprovalRequestEvent):
            control_queue.mark_pending_approval(app_server_event)
            try:
                _send_agent_approval(node, app_server_event.to_contract())
                control_event = _wait_for_approval_control_event(
                    node,
                    control_queue,
                    app_server_event,
                    timeout_seconds=approval_response_timeout_seconds,
                    poll_dora_control=poll_dora_control_during_approval,
                )
            finally:
                control_queue.cancel_pending_approval(app_server_event)
            if isinstance(control_event, AgentApprovalResponse):
                transport.respond_approval(control_event)
                approval_responses += 1
            elif isinstance(control_event, AgentCancelRequest):
                transport.interrupt_turn(control_event)
                cancel_requests += 1
            else:
                raise CodexAppServerNodeError("unsupported approval control event")
            approval_requests += 1
        elif isinstance(app_server_event, ProjectedUserInputRequestEvent):
            _send_agent_user_input_request(node, app_server_event.to_contract())
            control_event = _wait_for_user_input_control_event(
                node,
                app_server_event,
                timeout_seconds=approval_response_timeout_seconds,
            )
            if isinstance(control_event, AgentUserInputResponse):
                transport.respond_user_input(control_event)
                user_input_responses += 1
            elif isinstance(control_event, AgentCancelRequest):
                transport.interrupt_turn(control_event)
                cancel_requests += 1
            else:
                raise CodexAppServerNodeError("unsupported user-input control event")
            user_input_requests += 1
        elif isinstance(app_server_event, ProjectedMcpElicitationRequestEvent):
            _send_agent_mcp_elicitation_request(node, app_server_event.to_contract())
            control_event = _wait_for_mcp_elicitation_control_event(
                node,
                app_server_event,
                timeout_seconds=approval_response_timeout_seconds,
            )
            if isinstance(control_event, AgentMcpElicitationResponse):
                transport.respond_mcp_elicitation(control_event)
                mcp_elicitation_responses += 1
            elif isinstance(control_event, AgentCancelRequest):
                transport.interrupt_turn(control_event)
                cancel_requests += 1
            else:
                raise CodexAppServerNodeError("unsupported MCP elicitation control event")
            mcp_elicitation_requests += 1
        elif isinstance(app_server_event, ProjectedToolEvent):
            _send_agent_tool(node, app_server_event.to_contract())
            tool_events += 1

    if turn_done != 1:
        raise CodexAppServerNodeError("Codex turn stream ended without exactly one turn_done")
    return CodexAppServerTurnStreamSummary(
        text_deltas=text_deltas,
        turn_done=turn_done,
        approval_requests=approval_requests,
        approval_responses=approval_responses,
        user_input_requests=user_input_requests,
        user_input_responses=user_input_responses,
        mcp_elicitation_requests=mcp_elicitation_requests,
        mcp_elicitation_responses=mcp_elicitation_responses,
        cancel_requests=cancel_requests,
        tool_events=tool_events,
    )


def _project_turn_status(turn: CodexTurnReference) -> ProjectedTurnDoneStatus:
    if turn.status == "completed":
        return "completed"
    if turn.status == "interrupted":
        return "cancelled"
    if turn.status == "failed":
        return "failed"
    raise CodexAppServerNodeError("turn/completed carried inProgress status")


def _project_turn_message(turn: CodexTurnReference) -> str | None:
    if turn.error is None:
        return None
    return turn.error.message


def _to_codex_approval_decision(response: AgentApprovalResponse) -> CodexApprovalDecision:
    if response.decision == "accept":
        if response.scope == "session":
            return "acceptForSession"
        return "accept"
    if response.decision == "decline":
        return "decline"
    if response.decision == "cancel":
        return "cancel"
    raise CodexAppServerNodeError(f"unsupported approval decision: {response.decision!r}")


def _build_codex_approval_response(
    pending: PendingCodexApproval,
    response: AgentApprovalResponse,
) -> CodexServerRequestJsonRpcClientResponse:
    if pending.kind == "permissions":
        if pending.requested_permissions is None:
            raise CodexAppServerNodeError("permissions approval was missing requested permissions")
        granted_permissions = (
            pending.requested_permissions
            if response.decision == "accept"
            else CodexPermissionProfile()
        )
        grant_scope: AgentApprovalScope = response.scope if response.decision == "accept" else "turn"
        return CodexPermissionsApprovalJsonRpcResponse(
            id=pending.request_id,
            result=CodexPermissionsApprovalJsonRpcResult(
                permissions=granted_permissions,
                scope=grant_scope,
            ),
        )
    decision = _to_codex_approval_decision(response)
    return CodexApprovalJsonRpcResponse(
        id=pending.request_id,
        result=CodexApprovalJsonRpcResult(decision=decision),
    )


def _build_codex_user_input_response(
    pending: PendingCodexUserInputRequest,
    response: AgentUserInputResponse,
) -> CodexToolUserInputJsonRpcResponse:
    answered_question_ids = tuple(answer.question_id for answer in response.answers)
    if set(answered_question_ids) != set(pending.question_ids):
        raise CodexAppServerNodeError("user-input response question ids did not match request")
    return CodexToolUserInputJsonRpcResponse(
        id=pending.codex_request_id,
        result=CodexToolUserInputJsonRpcResult(
            answers={
                answer.question_id: CodexToolUserInputAnswerResult(answers=answer.answers)
                for answer in response.answers
            }
        ),
    )


def _build_codex_mcp_elicitation_response(
    pending: PendingCodexMcpElicitationRequest,
    response: AgentMcpElicitationResponse,
) -> CodexMcpElicitationJsonRpcResponse:
    if pending.mode == "form" and response.action == "accept" and response.content is None:
        raise CodexAppServerNodeError("accepted form MCP elicitation requires content")
    return CodexMcpElicitationJsonRpcResponse(
        id=pending.codex_request_id,
        result=CodexMcpElicitationJsonRpcResult(
            action=response.action,
            content=response.content,
            meta=response.meta,
        ),
    )


def _validate_user_input_response_matches_pending(
    response: AgentUserInputResponse,
    pending: PendingCodexUserInputRequest,
) -> None:
    if pending.session_id != response.session_id:
        raise CodexAppServerNodeError("user-input response session_id did not match pending request")
    if pending.user_turn_id != response.user_turn_id:
        raise CodexAppServerNodeError(
            "user-input response user_turn_id did not match pending request"
        )
    if pending.request_id != response.request_id:
        raise CodexAppServerNodeError("user-input response request_id did not match pending request")


def _validate_mcp_elicitation_response_matches_pending(
    response: AgentMcpElicitationResponse,
    pending: PendingCodexMcpElicitationRequest,
) -> None:
    if pending.session_id != response.session_id:
        raise CodexAppServerNodeError(
            "MCP elicitation response session_id did not match pending request"
        )
    if pending.user_turn_id != response.user_turn_id:
        raise CodexAppServerNodeError(
            "MCP elicitation response user_turn_id did not match pending request"
        )
    if pending.request_id != response.request_id:
        raise CodexAppServerNodeError(
            "MCP elicitation response request_id did not match pending request"
        )


def _project_user_input_request(
    turn: AgentTurnRequest,
    message: CodexToolUserInputRequestEnvelope,
    seq: int,
) -> ProjectedUserInputRequestEvent:
    return ProjectedUserInputRequestEvent(
        session_id=turn.session_id,
        user_turn_id=turn.user_turn_id,
        request_id=_jsonrpc_id_to_contract_id(message.id),
        seq=seq,
        questions=tuple(question.to_contract() for question in message.params.questions),
    )


def _project_mcp_elicitation_request(
    turn: AgentTurnRequest,
    message: CodexMcpElicitationRequestEnvelope,
    seq: int,
) -> ProjectedMcpElicitationRequestEvent:
    params = message.params
    if isinstance(params, CodexMcpUrlElicitationParams):
        return ProjectedMcpElicitationRequestEvent(
            session_id=turn.session_id,
            user_turn_id=turn.user_turn_id,
            request_id=_jsonrpc_id_to_contract_id(message.id),
            seq=seq,
            server_name=params.server_name,
            mode="url",
            message=params.message,
            url=params.url,
            elicitation_id=params.elicitation_id,
            meta=params.meta,
        )
    return ProjectedMcpElicitationRequestEvent(
        session_id=turn.session_id,
        user_turn_id=turn.user_turn_id,
        request_id=_jsonrpc_id_to_contract_id(message.id),
        seq=seq,
        server_name=params.server_name,
        mode="form",
        message=params.message,
        requested_schema=params.requested_schema,
        meta=params.meta,
    )


def _project_tool_event(
    turn: AgentTurnRequest,
    item: CodexToolCallItem,
    seq: int,
) -> ProjectedToolEvent:
    event = _project_tool_status(item.status)
    return ProjectedToolEvent(
        session_id=turn.session_id,
        user_turn_id=turn.user_turn_id,
        tool_call_id=item.id,
        tool_name=item.tool_name(),
        tool_event=event,
        seq=seq,
        summary=item.status,
    )


def _project_tool_status(status: CodexToolCallStatus) -> ProjectedToolEventKind:
    if status == "inProgress":
        return "started"
    if status == "completed":
        return "completed"
    if status == "failed":
        return "failed"
    raise CodexAppServerNodeError(f"unsupported Codex tool status: {status!r}")


def _jsonrpc_id_to_contract_id(request_id: CodexJsonRpcRequestId) -> str:
    return str(request_id)


def _approval_contract_id(
    request_id: CodexJsonRpcRequestId,
    approval_id: str | None,
) -> str:
    if approval_id is not None:
        return approval_id
    return _jsonrpc_id_to_contract_id(request_id)


def _project_command_approval(
    turn: AgentTurnRequest,
    message: CodexCommandApprovalRequestEnvelope,
    seq: int,
) -> ProjectedApprovalRequestEvent:
    prompt = _first_present_text(
        message.params.reason,
        message.params.command,
        "Command execution approval requested",
    )
    action_label = _first_present_text(message.params.command, "command_execution")
    return ProjectedApprovalRequestEvent(
        session_id=turn.session_id,
        user_turn_id=turn.user_turn_id,
        approval_id=_approval_contract_id(message.id, message.params.approval_id),
        seq=seq,
        prompt=prompt,
        action_label=action_label,
    )


def _project_file_change_approval(
    turn: AgentTurnRequest,
    message: CodexFileChangeApprovalRequestEnvelope,
    seq: int,
) -> ProjectedApprovalRequestEvent:
    prompt = _first_present_text(
        message.params.reason,
        message.params.grant_root,
        "File change approval requested",
    )
    action_label = _first_present_text(message.params.grant_root, "file_change")
    return ProjectedApprovalRequestEvent(
        session_id=turn.session_id,
        user_turn_id=turn.user_turn_id,
        approval_id=_jsonrpc_id_to_contract_id(message.id),
        seq=seq,
        prompt=prompt,
        action_label=action_label,
    )


def _project_permissions_approval(
    turn: AgentTurnRequest,
    message: CodexPermissionsApprovalRequestEnvelope,
    seq: int,
) -> ProjectedApprovalRequestEvent:
    prompt = _first_present_text(
        message.params.reason,
        f"Grant requested permissions for {message.params.cwd}?",
    )
    return ProjectedApprovalRequestEvent(
        session_id=turn.session_id,
        user_turn_id=turn.user_turn_id,
        approval_id=_jsonrpc_id_to_contract_id(message.id),
        seq=seq,
        prompt=prompt,
        action_label=_summarize_permission_profile(message.params.permissions),
    )


def _summarize_permission_profile(profile: CodexPermissionProfile) -> str:
    labels: list[str] = []
    if profile.file_system is not None:
        file_system = profile.file_system
        if file_system.entries:
            labels.append(f"filesystem entries:{len(file_system.entries)}")
        if file_system.read:
            labels.append(f"filesystem read:{len(file_system.read)}")
        if file_system.write:
            labels.append(f"filesystem write:{len(file_system.write)}")
    if profile.network is not None and profile.network.enabled is not None:
        labels.append(f"network:{str(profile.network.enabled).lower()}")
    if labels:
        return ", ".join(labels)
    return "permissions.request"


def _first_present_text(*candidates: str | None) -> str:
    for candidate in candidates:
        if candidate is not None and candidate.strip() != "":
            return candidate
    raise CodexAppServerNodeError("at least one non-empty text candidate is required")


def _validate_message_turn(
    active_turn: CodexActiveTurn,
    thread_id: str,
    turn_id: str,
) -> None:
    if thread_id != active_turn.thread_id:
        raise CodexAppServerNodeError("Codex message threadId did not match active thread")
    if turn_id != active_turn.turn_id:
        raise CodexAppServerNodeError("Codex message turnId did not match active turn")


def _decode_agent_turn_event(event) -> AgentTurnRequest:
    metadata = validate_dora_agent_turn_request_metadata(event.get("metadata"))
    return decode_agent_turn_request_from_dora(event.get("value"), metadata)


def _decode_agent_cancel_event(event) -> AgentCancelRequest:
    metadata = validate_dora_agent_cancel_metadata(event.get("metadata"))
    return decode_agent_cancel_request_from_dora(event.get("value"), metadata)


def _decode_agent_user_input_response_event(event) -> AgentUserInputResponse:
    metadata = validate_dora_agent_user_input_response_metadata(event.get("metadata"))
    return decode_agent_user_input_response_from_dora(event.get("value"), metadata)


def _decode_agent_mcp_elicitation_response_event(event) -> AgentMcpElicitationResponse:
    metadata = validate_dora_agent_mcp_elicitation_response_metadata(event.get("metadata"))
    return decode_agent_mcp_elicitation_response_from_dora(event.get("value"), metadata)


def _approval_response_key(
    session_id: str,
    user_turn_id: str,
    approval_id: str,
) -> ApprovalResponsePathParts:
    return (session_id, user_turn_id, approval_id)


def _approval_response_path_parts(path: str) -> ApprovalResponsePathParts | None:
    segments = path.split("/")
    if len(segments) != 9:
        return None
    if (
        segments[0] != ""
        or segments[1] != "api"
        or segments[2] != "agent-approvals"
        or segments[4] != "user-turns"
        or segments[6] != "approval-requests"
        or segments[8] != "responses"
    ):
        return None
    session_id = urllib.parse.unquote(segments[3])
    user_turn_id = urllib.parse.unquote(segments[5])
    approval_id = urllib.parse.unquote(segments[7])
    if session_id == "" or user_turn_id == "" or approval_id == "":
        return None
    return _approval_response_key(session_id, user_turn_id, approval_id)


def _read_required_request_body(handler: BaseHTTPRequestHandler) -> bytes:
    content_length = handler.headers.get("Content-Length")
    if content_length is None:
        raise RequestBodyBoundaryError(status_code=411, message="Content-Length is required")
    try:
        body_length = int(content_length)
    except ValueError as exc:
        raise RequestBodyBoundaryError(
            status_code=400,
            message="Content-Length must be an integer",
        ) from exc
    if body_length < 0:
        raise RequestBodyBoundaryError(
            status_code=400,
            message="Content-Length must be non-negative",
        )
    return handler.rfile.read(body_length)


def _send_http_model(
    handler: BaseHTTPRequestHandler,
    status: int,
    model: BaseModel,
) -> None:
    _send_http_bytes(
        handler,
        status,
        model.model_dump_json().encode("utf-8"),
        content_type="application/json",
    )


def _send_http_error(handler: BaseHTTPRequestHandler, status: int, message: str) -> None:
    _send_http_bytes(handler, status, f"{message}\n".encode("utf-8"), content_type="text/plain")


def _send_http_bytes(
    handler: BaseHTTPRequestHandler,
    status: int,
    body: bytes,
    *,
    content_type: str,
) -> None:
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _wait_for_approval_control_event(
    node,
    control_queue: CodexControlQueue,
    approval: ProjectedApprovalRequestEvent,
    *,
    timeout_seconds: float,
    poll_dora_control: bool,
) -> AgentApprovalControlEvent:
    deadline = time.monotonic() + timeout_seconds
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0.0:
            raise CodexAppServerNodeError("timed out waiting for approval response")
        response = control_queue.wait_for_approval_response(
            approval,
            timeout_seconds=min(0.05, remaining),
        )
        if response is not None:
            _validate_approval_response_matches_request(response, approval)
            return response
        if not poll_dora_control:
            continue

        remaining = deadline - time.monotonic()
        if remaining <= 0.0:
            raise CodexAppServerNodeError("timed out waiting for approval response")
        event = _next_dora_event(node, min(0.05, remaining))
        if event is None:
            continue
        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            raise CodexAppServerNodeError("DORA STOP arrived before approval response")
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id in ("agent_cancel",):
                raise CodexAppServerNodeError(
                    f"DORA input {input_id!r} closed before approval was resolved"
                )
            continue
        if event_type != "INPUT":
            raise CodexAppServerNodeError(f"Unexpected DORA event type: {event_type!r}")

        input_id = _required_event_text(event, "id")
        if input_id == "agent_cancel":
            return _decode_agent_cancel_event(event)
        raise CodexAppServerNodeError(
            f"Unexpected DORA input id while waiting for approval: {input_id!r}"
        )


def _wait_for_user_input_control_event(
    node,
    request: ProjectedUserInputRequestEvent,
    *,
    timeout_seconds: float,
) -> AgentUserInputControlEvent:
    while True:
        event = _next_dora_event(node, timeout_seconds)
        if event is None:
            raise CodexAppServerNodeError("timed out waiting for user-input response")
        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            raise CodexAppServerNodeError("DORA STOP arrived before user-input response")
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id in ("agent_user_input_response", "agent_cancel"):
                raise CodexAppServerNodeError(
                    f"DORA input {input_id!r} closed before user-input was resolved"
                )
            continue
        if event_type != "INPUT":
            raise CodexAppServerNodeError(f"Unexpected DORA event type: {event_type!r}")

        input_id = _required_event_text(event, "id")
        if input_id == "agent_user_input_response":
            response = _decode_agent_user_input_response_event(event)
            _validate_user_input_response_matches_request(response, request)
            return response
        if input_id == "agent_cancel":
            return _decode_agent_cancel_event(event)
        raise CodexAppServerNodeError(
            f"Unexpected DORA input id while waiting for user-input: {input_id!r}"
        )


def _wait_for_mcp_elicitation_control_event(
    node,
    request: ProjectedMcpElicitationRequestEvent,
    *,
    timeout_seconds: float,
) -> AgentMcpElicitationControlEvent:
    while True:
        event = _next_dora_event(node, timeout_seconds)
        if event is None:
            raise CodexAppServerNodeError("timed out waiting for MCP elicitation response")
        event_type = _required_event_text(event, "type")
        if event_type == "STOP":
            raise CodexAppServerNodeError("DORA STOP arrived before MCP elicitation response")
        if event_type == "INPUT_CLOSED":
            input_id = _required_event_text(event, "id")
            if input_id in ("agent_mcp_elicitation_response", "agent_cancel"):
                raise CodexAppServerNodeError(
                    f"DORA input {input_id!r} closed before MCP elicitation was resolved"
                )
            continue
        if event_type != "INPUT":
            raise CodexAppServerNodeError(f"Unexpected DORA event type: {event_type!r}")

        input_id = _required_event_text(event, "id")
        if input_id == "agent_mcp_elicitation_response":
            response = _decode_agent_mcp_elicitation_response_event(event)
            _validate_mcp_elicitation_response_matches_request(response, request)
            return response
        if input_id == "agent_cancel":
            return _decode_agent_cancel_event(event)
        raise CodexAppServerNodeError(
            f"Unexpected DORA input id while waiting for MCP elicitation: {input_id!r}"
        )


def _validate_approval_response_matches_request(
    response: AgentApprovalResponse,
    approval: ProjectedApprovalRequestEvent,
) -> None:
    if response.session_id != approval.session_id:
        raise CodexAppServerNodeError("approval response session_id did not match request")
    if response.user_turn_id != approval.user_turn_id:
        raise CodexAppServerNodeError("approval response user_turn_id did not match request")
    if response.approval_id != approval.approval_id:
        raise CodexAppServerNodeError("approval response approval_id did not match request")


def _validate_user_input_response_matches_request(
    response: AgentUserInputResponse,
    request: ProjectedUserInputRequestEvent,
) -> None:
    if response.session_id != request.session_id:
        raise CodexAppServerNodeError("user-input response session_id did not match request")
    if response.user_turn_id != request.user_turn_id:
        raise CodexAppServerNodeError("user-input response user_turn_id did not match request")
    if response.request_id != request.request_id:
        raise CodexAppServerNodeError("user-input response request_id did not match request")


def _validate_mcp_elicitation_response_matches_request(
    response: AgentMcpElicitationResponse,
    request: ProjectedMcpElicitationRequestEvent,
) -> None:
    if response.session_id != request.session_id:
        raise CodexAppServerNodeError("MCP elicitation response session_id did not match request")
    if response.user_turn_id != request.user_turn_id:
        raise CodexAppServerNodeError("MCP elicitation response user_turn_id did not match request")
    if response.request_id != request.request_id:
        raise CodexAppServerNodeError("MCP elicitation response request_id did not match request")


def _next_dora_event(node, timeout_seconds: float):
    next_method = getattr(node, "next", None)
    if callable(next_method):
        return next_method(timeout_seconds)
    return next(node)


def _send_agent_text(node, event: AgentTextDelta) -> None:
    _send_agent_runtime_event(node, event)
    payload, metadata = encode_agent_text_delta_for_dora(event)
    node.send_output("agent_text", payload, metadata=metadata.to_dora_metadata())


def _send_agent_done(node, event: AgentTurnDone) -> None:
    _send_agent_runtime_event(node, event)
    payload, metadata = encode_agent_turn_done_for_dora(event)
    node.send_output("agent_done", payload, metadata=metadata.to_dora_metadata())


def _send_agent_approval(node, event: AgentApprovalRequest) -> None:
    _send_agent_runtime_event(node, event)
    payload, metadata = encode_agent_approval_request_for_dora(event)
    node.send_output("agent_approval", payload, metadata=metadata.to_dora_metadata())


def _send_agent_user_input_request(node, event: AgentUserInputRequest) -> None:
    _send_agent_runtime_event(node, event)
    payload, metadata = encode_agent_user_input_request_for_dora(event)
    node.send_output("agent_user_input", payload, metadata=metadata.to_dora_metadata())


def _send_agent_mcp_elicitation_request(node, event: AgentMcpElicitationRequest) -> None:
    _send_agent_runtime_event(node, event)
    payload, metadata = encode_agent_mcp_elicitation_request_for_dora(event)
    node.send_output("agent_mcp_elicitation", payload, metadata=metadata.to_dora_metadata())


def _send_agent_tool(node, event: AgentToolEvent) -> None:
    _send_agent_runtime_event(node, event)
    payload, metadata = encode_agent_tool_event_for_dora(event)
    node.send_output("agent_tool", payload, metadata=metadata.to_dora_metadata())


def _send_agent_runtime_event(
    node,
    event: (
        AgentTextDelta
        | AgentTurnDone
        | AgentApprovalRequest
        | AgentUserInputRequest
        | AgentMcpElicitationRequest
        | AgentToolEvent
    ),
) -> None:
    payload, metadata = encode_agent_runtime_event_for_dora(event)
    node.send_output("agent_event", payload, metadata=metadata.to_dora_metadata())


def _required_event_text(event, key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str):
        raise CodexAppServerNodeError(f"DORA event field {key!r} must be a string")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
