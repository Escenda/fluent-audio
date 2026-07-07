"""DORA live topic bridge for the fluent-dialogue-dora dashboard."""
# ruff: noqa: E402

from __future__ import annotations

import argparse
import http.client
import os
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from collections.abc import Sequence
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Literal, Protocol, assert_never

from pydantic import BaseModel, ConfigDict, Field

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from bridges.dora_web_bridge.decoder import (
    DoraWebBridgeDecodeConfig,
    decode_dora_input_for_web_bridge,
    input_id_from_dora_event,
    required_event_text,
)
from bridges.dora_web_bridge.messages import (
    WEB_BRIDGE_INPUT_IDS,
    ApprovalResponsePathParts,
    DoraWebBridgeGlobalSnapshotResponse,
    DoraWebBridgeLatestResponse,
    DoraWebBridgeTrackFrame,
    DoraWebBridgeTrackSnapshotResponse,
    DoraWebBridgeTopicEvent,
    DoraWebBridgeTopicListResponse,
    DoraWebBridgeTopicSnapshotResponse,
    DoraWebBridgeTopicSummary,
    WebApprovalResponseSubmission,
    WebBridgeInputId,
    WebTrackTopic,
)
from bridges.dora_web_bridge.projection import WebBridgeProjection


NodeRunState = Literal["running", "stopped", "unknown"]

DEFAULT_NODE_LOG_TAIL_COUNT = 160
MAX_NODE_LOG_TAIL_COUNT = 1000
DEFAULT_RECENT_LIMIT = 600
DEFAULT_DASHBOARD_INITIAL_TAIL_COUNT = 500
DEFAULT_SSE_WAIT_SECONDS = 15.0
_DASHBOARD_INITIAL_STATE_PLACEHOLDER = "__FLUENT_DIALOGUE_DORA_INITIAL_STATE__"


class DoraWebBridgeError(ValueError):
    """Raised when the DORA Web bridge boundary is violated."""


class DoraWebBridgeConfig(BaseModel):
    """Runtime configuration for the live topic bridge."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    session_id: str = Field(min_length=1)
    host: str = Field(min_length=1)
    port: int = Field(ge=1, le=65535)
    recent_limit: int = Field(default=DEFAULT_RECENT_LIMIT, ge=1)
    input_ids: tuple[WebBridgeInputId, ...] = WEB_BRIDGE_INPUT_IDS
    runtime_log_path: Path | None = None
    dataflow_path: Path | None = None
    codex_control_url: str | None = Field(default=None, min_length=1)
    keep_http_after_dora_stop: bool = False


class DoraWebBridgeSummary(BaseModel):
    """Validated processing summary for one bridge run."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    event_count: int = Field(ge=0)
    final_markers: int = Field(ge=0)
    closed_inputs: int = Field(ge=0)
    non_input_events: int = Field(ge=0)


class WebNodeStatusItem(BaseModel):
    """Dashboard status for one expected live node."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    node_id: str = Field(min_length=1)
    status: NodeRunState
    process_count: int = Field(ge=0)
    pid: int | None = Field(default=None, gt=0)
    command: str | None = None


class WebNodeStatusResponse(BaseModel):
    """Dashboard response with process-level node health."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    nodes: tuple[WebNodeStatusItem, ...]


class WebNodeLogResponse(BaseModel):
    """Dashboard response with a node-filtered runtime log tail."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    node_id: str = Field(min_length=1)
    available: bool
    line_count: int = Field(ge=0)
    lines: tuple[str, ...]
    message: str | None = None


class WebDashboardInitialState(BaseModel):
    """Initial bounded state embedded into the dashboard HTML."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    snapshot: DoraWebBridgeGlobalSnapshotResponse
    topics: DoraWebBridgeTopicListResponse
    tracks: DoraWebBridgeTrackSnapshotResponse


class RequestBodyBoundaryError(ValueError):
    """Raised when an HTTP request body cannot be read as a typed boundary input."""

    def __init__(self, *, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code


class CodexControlClient(Protocol):
    """Forwards browser control decisions to the Codex control plane."""

    def submit_approval_response(
        self,
        key: ApprovalResponsePathParts,
        submission: WebApprovalResponseSubmission,
    ) -> bytes:
        """Submit one approval response and return the upstream body."""


class HttpCodexControlClient:
    """REST client for the Codex app-server control endpoint."""

    def __init__(self, *, base_url: str, timeout_seconds: float = 5.0) -> None:
        self._base_url = base_url.rstrip("/")
        if not self._base_url:
            raise DoraWebBridgeError("codex control URL must not be empty")
        self._timeout_seconds = timeout_seconds

    def submit_approval_response(
        self,
        key: ApprovalResponsePathParts,
        submission: WebApprovalResponseSubmission,
    ) -> bytes:
        session_id, user_turn_id, approval_id = key
        path = (
            "/api/agent-approvals/"
            + urllib.parse.quote(session_id, safe="")
            + "/user-turns/"
            + urllib.parse.quote(user_turn_id, safe="")
            + "/approval-requests/"
            + urllib.parse.quote(approval_id, safe="")
            + "/responses"
        )
        request = urllib.request.Request(
            self._base_url + path,
            data=submission.model_dump_json().encode("utf-8"),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                status = response.getcode()
                body = response.read()
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise DoraWebBridgeError(
                f"Codex control approval response failed with HTTP {exc.code}: {body}"
            ) from exc
        except (urllib.error.URLError, http.client.HTTPException, OSError) as exc:
            raise DoraWebBridgeError(f"Codex control approval response failed: {exc}") from exc
        if status < 200 or status >= 300:
            raise DoraWebBridgeError(
                f"Codex control approval response returned unexpected HTTP status {status}"
            )
        return body


class DoraWebTopicStore:
    """Bounded live-topic transport store.

    This store intentionally keeps only latest values and recent transport
    buffers. It does not own domain history semantics.
    """

    def __init__(
        self,
        *,
        input_ids: tuple[WebBridgeInputId, ...],
        recent_limit: int,
    ) -> None:
        if not input_ids:
            raise DoraWebBridgeError("dora_web_bridge requires at least one input topic")
        self._input_ids = input_ids
        self._recent_limit = recent_limit
        self._global_events: deque[DoraWebBridgeTopicEvent] = deque(maxlen=recent_limit)
        self._topic_events: dict[str, deque[DoraWebBridgeTopicEvent]] = {
            input_id: deque(maxlen=recent_limit) for input_id in input_ids
        }
        self._latest_by_topic: dict[str, DoraWebBridgeTopicEvent] = {}
        self._latest_by_track: dict[WebTrackTopic, DoraWebBridgeTrackFrame] = {}
        self._topic_counts: dict[str, int] = {input_id: 0 for input_id in input_ids}
        self._event_count = 0
        self._condition = threading.Condition()

    @property
    def event_count(self) -> int:
        with self._condition:
            return self._event_count

    def append(
        self,
        *,
        input_id: WebBridgeInputId,
        event,
    ) -> DoraWebBridgeTopicEvent:
        with self._condition:
            if input_id not in self._topic_events:
                raise DoraWebBridgeError(f"Unexpected bridge input id: {input_id!r}")
            topic_offset = self._topic_counts[input_id]
            item = DoraWebBridgeTopicEvent(
                global_offset=self._event_count,
                topic_offset=topic_offset,
                topic=input_id,
                input_id=input_id,
                event=event,
            )
            self._event_count += 1
            self._topic_counts[input_id] = topic_offset + 1
            self._global_events.append(item)
            self._topic_events[input_id].append(item)
            self._latest_by_topic[input_id] = item
            track_topic = _track_topic_for_event(event)
            self._latest_by_track[track_topic] = DoraWebBridgeTrackFrame(
                topic=track_topic,
                global_offset=item.global_offset,
                event=event,
            )
            self._condition.notify_all()
            return item

    def list_topics(self) -> DoraWebBridgeTopicListResponse:
        with self._condition:
            summaries: list[DoraWebBridgeTopicSummary] = []
            for input_id in self._input_ids:
                latest = self._latest_by_topic.get(input_id)
                summaries.append(
                    DoraWebBridgeTopicSummary(
                        topic=input_id,
                        input_id=input_id,
                        event_count=self._topic_counts[input_id],
                        latest_event_type=latest.event.event_type if latest else None,
                        last_seen_ns=latest.event.created_at_ns if latest else None,
                    )
                )
            return DoraWebBridgeTopicListResponse(topics=tuple(summaries))

    def global_snapshot(self, *, tail_count: int | None) -> DoraWebBridgeGlobalSnapshotResponse:
        with self._condition:
            events = _bounded_tail(tuple(self._global_events), tail_count=tail_count)
            return DoraWebBridgeGlobalSnapshotResponse(
                event_count=self._event_count,
                events=events,
            )

    def track_snapshot(self) -> DoraWebBridgeTrackSnapshotResponse:
        with self._condition:
            tracks = tuple(
                sorted(
                    self._latest_by_track.values(),
                    key=lambda frame: frame.topic,
                )
            )
            return DoraWebBridgeTrackSnapshotResponse(tracks=tracks)

    def topic_snapshot(
        self,
        topic: str,
        *,
        tail_count: int | None,
    ) -> DoraWebBridgeTopicSnapshotResponse:
        input_id = _input_id_from_topic(topic)
        with self._condition:
            if input_id not in self._topic_events:
                raise DoraWebBridgeError(f"Unknown bridge topic: {topic}")
            events = _bounded_tail(tuple(self._topic_events[input_id]), tail_count=tail_count)
            return DoraWebBridgeTopicSnapshotResponse(
                topic=input_id,
                input_id=input_id,
                event_count=self._topic_counts[input_id],
                events=events,
            )

    def latest(self, topic: str) -> DoraWebBridgeLatestResponse:
        input_id = _input_id_from_topic(topic)
        with self._condition:
            if input_id not in self._topic_events:
                raise DoraWebBridgeError(f"Unknown bridge topic: {topic}")
            return DoraWebBridgeLatestResponse(
                topic=input_id,
                input_id=input_id,
                event_count=self._topic_counts[input_id],
                event=self._latest_by_topic.get(input_id),
            )

    def wait_for_global_events_after(
        self,
        offset: int,
        *,
        topics: tuple[WebBridgeInputId, ...] | None,
        timeout_seconds: float,
    ) -> tuple[DoraWebBridgeTopicEvent, ...]:
        with self._condition:
            offset = self._global_stream_offset(offset)
            self._condition.wait_for(
                lambda: any(
                    _event_selected_by_topics(event, topics)
                    for event in self._global_events
                    if event.global_offset >= offset
                ),
                timeout=timeout_seconds,
            )
            return tuple(
                event
                for event in self._global_events
                if event.global_offset >= offset and _event_selected_by_topics(event, topics)
            )

    def wait_for_topic_events_after(
        self,
        topic: str,
        offset: int,
        *,
        timeout_seconds: float,
    ) -> tuple[DoraWebBridgeTopicEvent, ...]:
        input_id = _input_id_from_topic(topic)
        with self._condition:
            if input_id not in self._topic_events:
                raise DoraWebBridgeError(f"Unknown bridge topic: {topic}")
            offset = self._topic_stream_offset(input_id, offset)
            self._condition.wait_for(
                lambda: any(
                    event.topic_offset >= offset for event in self._topic_events[input_id]
                ),
                timeout=timeout_seconds,
            )
            return tuple(
                event for event in self._topic_events[input_id] if event.topic_offset >= offset
            )

    def _global_stream_offset(self, offset: int) -> int:
        if offset < 0:
            raise DoraWebBridgeError("after offset must be non-negative")
        if not self._global_events:
            return offset
        oldest = self._global_events[0].global_offset
        if offset < oldest:
            return oldest
        return offset

    def _topic_stream_offset(self, input_id: WebBridgeInputId, offset: int) -> int:
        if offset < 0:
            raise DoraWebBridgeError("after offset must be non-negative")
        events = self._topic_events[input_id]
        if not events:
            return offset
        oldest = events[0].topic_offset
        if offset < oldest:
            return oldest
        return offset


class NodeStatusMonitor:
    """Reads process-level liveness for the local live voice dataflow."""

    def __init__(self, node_ids: tuple[str, ...], runtime_log_path: Path | None) -> None:
        self._node_ids = node_ids
        self._runtime_log_path = runtime_log_path

    def snapshot(self) -> WebNodeStatusResponse:
        spawned_pids = _latest_spawned_pids(self._runtime_log_path)
        statuses: list[WebNodeStatusItem] = []
        for node_id in self._node_ids:
            pid = spawned_pids.get(node_id)
            if pid is None:
                statuses.append(
                    WebNodeStatusItem(
                        node_id=node_id,
                        status="unknown",
                        process_count=0,
                    )
                )
            elif _pid_is_running(pid):
                command = _command_for_pid(pid)
                statuses.append(
                    WebNodeStatusItem(
                        node_id=node_id,
                        status="running",
                        process_count=1,
                        pid=pid,
                        command=command,
                    )
                )
            else:
                statuses.append(
                    WebNodeStatusItem(
                        node_id=node_id,
                        status="stopped",
                        process_count=0,
                        pid=pid,
                    )
                )
        return WebNodeStatusResponse(nodes=tuple(statuses))


class RuntimeLogReader:
    """Reads node-filtered tails from the shared live runtime log."""

    def __init__(
        self,
        runtime_log_path: Path | None,
        node_ids: tuple[str, ...],
    ) -> None:
        self._runtime_log_path = runtime_log_path
        self._node_ids = frozenset(node_ids)

    def tail(self, node_id: str, *, tail_count: int) -> WebNodeLogResponse:
        if node_id not in self._node_ids:
            raise DoraWebBridgeError(f"Unknown live node id: {node_id}")
        if tail_count > MAX_NODE_LOG_TAIL_COUNT:
            raise DoraWebBridgeError(
                f"node log tail query parameter must be {MAX_NODE_LOG_TAIL_COUNT} or less"
            )
        if self._runtime_log_path is None:
            return WebNodeLogResponse(
                node_id=node_id,
                available=False,
                line_count=0,
                lines=(),
                message="Runtime log path is not configured for this bridge.",
            )
        if not self._runtime_log_path.exists():
            return WebNodeLogResponse(
                node_id=node_id,
                available=False,
                line_count=0,
                lines=(),
                message=f"Runtime log does not exist: {self._runtime_log_path}",
            )
        if not self._runtime_log_path.is_file():
            return WebNodeLogResponse(
                node_id=node_id,
                available=False,
                line_count=0,
                lines=(),
                message=f"Runtime log path is not a file: {self._runtime_log_path}",
            )
        selected_lines: deque[str] = deque(maxlen=tail_count)
        try:
            with self._runtime_log_path.open("r", encoding="utf-8", errors="replace") as log_file:
                for line in log_file:
                    stripped_line = line.rstrip("\n")
                    if _runtime_log_line_matches_node(stripped_line, node_id):
                        selected_lines.append(stripped_line)
        except OSError as exc:
            return WebNodeLogResponse(
                node_id=node_id,
                available=False,
                line_count=0,
                lines=(),
                message=f"Runtime log cannot be read: {exc}",
            )
        lines = tuple(selected_lines)
        return WebNodeLogResponse(
            node_id=node_id,
            available=True,
            line_count=len(lines),
            lines=lines,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bridge live DORA topics to a Web dashboard.")
    parser.add_argument("--dora", action="store_true")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--recent-limit", type=int, default=DEFAULT_RECENT_LIMIT)
    parser.add_argument("--input", action="append", choices=list(WEB_BRIDGE_INPUT_IDS), dest="inputs")
    parser.add_argument("--runtime-log", type=Path)
    parser.add_argument("--dataflow", type=Path)
    parser.add_argument("--codex-control-url")
    parser.add_argument("--keep-http-after-dora-stop", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.dora:
        parser.error("dora_web_bridge requires --dora")
    if args.dataflow is not None and not args.dataflow.is_absolute():
        parser.error("dora_web_bridge requires --dataflow to be an absolute path")

    from dora import Node

    input_ids = tuple(args.inputs or WEB_BRIDGE_INPUT_IDS)
    config = DoraWebBridgeConfig(
        session_id=args.session_id,
        host=args.host,
        port=args.port,
        recent_limit=args.recent_limit,
        input_ids=input_ids,
        runtime_log_path=args.runtime_log,
        dataflow_path=args.dataflow,
        codex_control_url=args.codex_control_url,
        keep_http_after_dora_stop=args.keep_http_after_dora_stop,
    )
    store = DoraWebTopicStore(input_ids=config.input_ids, recent_limit=config.recent_limit)
    control_client = (
        HttpCodexControlClient(base_url=config.codex_control_url)
        if config.codex_control_url is not None
        else None
    )
    server = build_server(
        config.host,
        config.port,
        store,
        control_client=control_client,
        runtime_log_path=config.runtime_log_path,
        dataflow_path=config.dataflow_path,
    )
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    try:
        summary = run_dora_web_bridge_events(Node(), config, store)
        sys.stdout.write(summary.model_dump_json())
        sys.stdout.write("\n")
        sys.stdout.flush()
        if config.keep_http_after_dora_stop:
            _keep_http_server_alive(config)
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=2.0)
    return 0


def run_dora_web_bridge_events(
    node,
    config: DoraWebBridgeConfig,
    store: DoraWebTopicStore,
) -> DoraWebBridgeSummary:
    configured_inputs = set(config.input_ids)
    decode_config = DoraWebBridgeDecodeConfig(session_id=config.session_id)
    final_markers = 0
    non_input_events = 0
    closed_inputs: set[WebBridgeInputId] = set()

    for dora_event in node:
        if dora_event is None:
            return _summary(
                store,
                final_markers=final_markers,
                closed_inputs=closed_inputs,
                non_input_events=non_input_events,
            )
        event_type = required_event_text(dora_event, "type")
        if event_type == "STOP":
            return _summary(
                store,
                final_markers=final_markers,
                closed_inputs=closed_inputs,
                non_input_events=non_input_events,
            )
        if event_type == "INPUT_CLOSED":
            input_id = input_id_from_dora_event(dora_event)
            if input_id not in configured_inputs:
                raise DoraWebBridgeError(f"Unexpected DORA input id: {input_id!r}")
            closed_inputs.add(input_id)
            continue
        if event_type != "INPUT":
            non_input_events += 1
            sys.stderr.write(
                "dora_web_bridge: observed non-input DORA event "
                f"{event_type!r}; keeping dashboard available\n"
            )
            sys.stderr.flush()
            continue

        input_id = input_id_from_dora_event(dora_event)
        if input_id not in configured_inputs:
            raise DoraWebBridgeError(f"Unexpected DORA input id: {input_id!r}")
        decoded = decode_dora_input_for_web_bridge(input_id, dora_event, decode_config)
        if decoded is None:
            final_markers += 1
            continue
        store.append(input_id=input_id, event=decoded)

    return _summary(
        store,
        final_markers=final_markers,
        closed_inputs=closed_inputs,
        non_input_events=non_input_events,
    )


def build_server(
    host: str,
    port: int,
    store: DoraWebTopicStore,
    *,
    control_client: CodexControlClient | None = None,
    runtime_log_path: Path | None = None,
    dataflow_path: Path | None = None,
) -> ThreadingHTTPServer:
    node_ids = _node_ids_from_dataflow(dataflow_path) if dataflow_path is not None else ()
    node_status_monitor = NodeStatusMonitor(node_ids, runtime_log_path)
    runtime_log_reader = RuntimeLogReader(runtime_log_path, node_ids)

    class ReusableHTTPServer(ThreadingHTTPServer):
        allow_reuse_address = True

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed_path = urllib.parse.urlparse(self.path)
            if parsed_path.path == "/health":
                _send_bytes(self, 200, b"ok", content_type="text/plain")
                return
            if parsed_path.path in ("/", "/topics"):
                _send_bytes(
                    self,
                    200,
                    _dashboard_html_with_initial_state(store).encode("utf-8"),
                    content_type="text/html; charset=utf-8",
                )
                return
            if parsed_path.path == "/api/topics":
                _send_model(self, 200, store.list_topics())
                return
            if parsed_path.path == "/api/tracks.json":
                _send_model(self, 200, store.track_snapshot())
                return
            if parsed_path.path == "/api/events.json":
                try:
                    _send_model(
                        self,
                        200,
                        store.global_snapshot(tail_count=_tail_count_from_query(parsed_path.query)),
                    )
                except DoraWebBridgeError as exc:
                    _send_error(self, 400, str(exc))
                return
            if parsed_path.path == "/api/events.sse":
                try:
                    after_offset = _after_offset_from_request(parsed_path.query, self.headers)
                    topics = _topics_from_query(parsed_path.query)
                    _send_global_event_stream(
                        self,
                        store,
                        after_offset=after_offset,
                        topics=topics,
                    )
                except DoraWebBridgeError as exc:
                    _send_error(self, 409, str(exc))
                return
            if parsed_path.path == "/api/node-status.json":
                try:
                    _send_model(self, 200, node_status_monitor.snapshot())
                except DoraWebBridgeError as exc:
                    _send_error(self, 503, str(exc))
                return
            node_id = _node_id_from_log_path(parsed_path.path)
            if node_id is not None:
                try:
                    _send_model(
                        self,
                        200,
                        runtime_log_reader.tail(
                            node_id,
                            tail_count=_node_log_tail_count_from_query(parsed_path.query),
                        ),
                    )
                except DoraWebBridgeError as exc:
                    _send_error(self, 400, str(exc))
                return
            topic = _topic_from_path(parsed_path.path, suffix="/events.json")
            if topic is not None:
                try:
                    _send_model(
                        self,
                        200,
                        store.topic_snapshot(
                            topic,
                            tail_count=_tail_count_from_query(parsed_path.query),
                        ),
                    )
                except DoraWebBridgeError as exc:
                    _send_error(self, 404, str(exc))
                return
            topic = _topic_from_path(parsed_path.path, suffix="/latest.json")
            if topic is not None:
                try:
                    _send_model(self, 200, store.latest(topic))
                except DoraWebBridgeError as exc:
                    _send_error(self, 404, str(exc))
                return
            topic = _topic_from_path(parsed_path.path, suffix="/events.sse")
            if topic is not None:
                try:
                    _send_topic_event_stream(
                        self,
                        store,
                        topic=topic,
                        after_offset=_after_offset_from_request(parsed_path.query, self.headers),
                    )
                except DoraWebBridgeError as exc:
                    _send_error(self, 409, str(exc))
                return
            _send_error(self, 404, "Not found")

        def do_POST(self) -> None:
            parsed_path = urllib.parse.urlparse(self.path)
            approval_key = _approval_response_path_parts(parsed_path.path)
            if approval_key is None:
                _send_error(self, 404, "Not found")
                return
            try:
                request_body = _read_required_request_body(self)
            except RequestBodyBoundaryError as exc:
                _send_error(self, exc.status_code, str(exc))
                return
            try:
                submission = WebApprovalResponseSubmission.model_validate_json(request_body)
            except ValueError:
                _send_error(self, 400, "Invalid approval response submission")
                return
            if control_client is None:
                _send_error(self, 503, "Codex control URL is not configured")
                return
            try:
                response_body = control_client.submit_approval_response(approval_key, submission)
            except DoraWebBridgeError as exc:
                _send_error(self, 503, str(exc))
                return
            _send_bytes(self, 200, response_body, content_type="application/json")

        def log_message(self, format: str, *args: str) -> None:
            return

    return ReusableHTTPServer((host, port), Handler)


def _summary(
    store: DoraWebTopicStore,
    *,
    final_markers: int,
    closed_inputs: set[WebBridgeInputId],
    non_input_events: int,
) -> DoraWebBridgeSummary:
    return DoraWebBridgeSummary(
        event_count=store.event_count,
        final_markers=final_markers,
        closed_inputs=len(closed_inputs),
        non_input_events=non_input_events,
    )


def _keep_http_server_alive(config: DoraWebBridgeConfig) -> None:
    sys.stderr.write(
        "dora_web_bridge: DORA event stream ended; keeping HTTP dashboard "
        f"alive on {config.host}:{config.port}\n"
    )
    sys.stderr.flush()
    while True:
        time.sleep(3600.0)


def _dashboard_html_with_initial_state(store: DoraWebTopicStore) -> str:
    initial_state = WebDashboardInitialState(
        snapshot=store.global_snapshot(tail_count=DEFAULT_DASHBOARD_INITIAL_TAIL_COUNT),
        topics=store.list_topics(),
        tracks=store.track_snapshot(),
    )
    initial_json = initial_state.model_dump_json().replace("</", "<\\/")
    return DORA_WEB_BRIDGE_DASHBOARD_HTML.replace(
        _DASHBOARD_INITIAL_STATE_PLACEHOLDER,
        initial_json,
        1,
    )


def _node_ids_from_dataflow(dataflow_path: Path) -> tuple[str, ...]:
    if not dataflow_path.is_absolute():
        raise DoraWebBridgeError("Dataflow path must be absolute")
    if not dataflow_path.exists():
        raise DoraWebBridgeError(f"Dataflow does not exist: {dataflow_path}")
    if not dataflow_path.is_file():
        raise DoraWebBridgeError(f"Dataflow path is not a file: {dataflow_path}")

    node_ids: list[str] = []
    seen: set[str] = set()
    in_nodes = False
    try:
        lines = dataflow_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise DoraWebBridgeError(f"Dataflow cannot be read: {exc}") from exc
    for line in lines:
        stripped = line.strip()
        if stripped == "nodes:":
            in_nodes = True
            continue
        if not in_nodes or not stripped.startswith("- id:"):
            continue
        node_id = _plain_yaml_value(stripped.removeprefix("- id:").strip())
        if not node_id:
            raise DoraWebBridgeError(f"Dataflow node id must not be empty: {dataflow_path}")
        if node_id in seen:
            raise DoraWebBridgeError(f"Dataflow node id is duplicated: {node_id}")
        seen.add(node_id)
        node_ids.append(node_id)
    if not node_ids:
        raise DoraWebBridgeError(f"Dataflow has no nodes[].id entries: {dataflow_path}")
    return tuple(node_ids)


def _plain_yaml_value(value: str) -> str:
    if len(value) >= 2 and value[0] in ("'", '"') and value[-1] == value[0]:
        return value[1:-1]
    return value


def _latest_spawned_pids(runtime_log_path: Path | None) -> dict[str, int]:
    if runtime_log_path is None or not runtime_log_path.is_file():
        return {}
    pids: dict[str, int] = {}
    try:
        with runtime_log_path.open("r", encoding="utf-8", errors="replace") as log_file:
            for line in log_file:
                parsed = _spawned_pid_from_log_line(line.rstrip("\n"))
                if parsed is not None:
                    node_id, pid = parsed
                    pids[node_id] = pid
    except OSError:
        return {}
    return pids


def _spawned_pid_from_log_line(line: str) -> tuple[str, int] | None:
    marker = ": spawner  spawned node with pid "
    prefix, separator, pid_text = line.partition(marker)
    if separator == "":
        return None
    node_id = prefix.rsplit(maxsplit=1)[-1]
    try:
        pid = int(pid_text.split(maxsplit=1)[0])
    except (IndexError, ValueError):
        return None
    return (node_id, pid)


def _pid_is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _command_for_pid(pid: int) -> str | None:
    cmdline_path = Path("/proc") / str(pid) / "cmdline"
    if not cmdline_path.is_file():
        return None
    try:
        raw = cmdline_path.read_bytes()
    except OSError:
        return None
    command = raw.replace(b"\0", b" ").decode("utf-8", errors="replace").strip()
    return command or None


def _runtime_log_line_matches_node(line: str, node_id: str) -> bool:
    return (
        line.startswith(f"{node_id}:")
        or f" {node_id}:" in line
        or f" node_id={node_id}" in line
        or f"Node `{node_id}`" in line
    )


def _bounded_tail(
    events: tuple[DoraWebBridgeTopicEvent, ...],
    *,
    tail_count: int | None,
) -> tuple[DoraWebBridgeTopicEvent, ...]:
    if tail_count is None:
        return events
    if tail_count == 0:
        return ()
    return events[-tail_count:]


def _track_topic_for_event(event: WebBridgeProjection) -> WebTrackTopic:
    if event.event_type == "session_state":
        return "session/state"
    if event.event_type == "audio_level":
        return "audio/level"
    if event.event_type == "audio_activity":
        return "vad/activity"
    if event.event_type == "turn":
        return "vad/turn"
    if event.event_type == "asr_control":
        return "asr/control"
    if event.event_type in ("transcript_delta", "transcript_partial", "transcript_final"):
        return "asr/transcript"
    if event.event_type == "dialogue_event":
        return "dialogue/event"
    if event.event_type == "agent_text_delta":
        return "agent/text"
    if event.event_type == "agent_turn_done":
        return "agent/done"
    if event.event_type == "approval_request":
        return "agent/approval"
    if event.event_type == "agent_user_input_request":
        return "agent/user-input"
    if event.event_type == "agent_mcp_elicitation_request":
        return "agent/mcp-elicitation"
    if event.event_type == "tool_event":
        return "agent/tool"
    if event.event_type == "tts_text":
        return "tts/text"
    if event.event_type == "barge_in":
        return "barge-in/event"
    if event.event_type == "playback_state":
        return "playback/state"
    if event.event_type == "playback_done":
        return "playback/done"
    assert_never(event)


def _event_selected_by_topics(
    event: DoraWebBridgeTopicEvent,
    topics: tuple[WebBridgeInputId, ...] | None,
) -> bool:
    if topics is None:
        return True
    return event.input_id in topics


def _input_id_from_topic(topic: str) -> WebBridgeInputId:
    decoded = urllib.parse.unquote(topic)
    if decoded in WEB_BRIDGE_INPUT_IDS:
        return decoded
    raise DoraWebBridgeError(f"Unknown bridge topic: {decoded}")


def _topic_from_path(path: str, *, suffix: str) -> str | None:
    prefix = "/api/topics/"
    if not path.startswith(prefix) or not path.endswith(suffix):
        return None
    encoded_topic = path[len(prefix) : -len(suffix)]
    if encoded_topic == "":
        return None
    return urllib.parse.unquote(encoded_topic)


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
    return (session_id, user_turn_id, approval_id)


def _node_id_from_log_path(path: str) -> str | None:
    prefix = "/api/node-logs/"
    suffix = ".json"
    if not path.startswith(prefix) or not path.endswith(suffix):
        return None
    encoded_node_id = path[len(prefix) : -len(suffix)]
    if encoded_node_id == "":
        return None
    return urllib.parse.unquote(encoded_node_id)


def _topics_from_query(query: str) -> tuple[WebBridgeInputId, ...] | None:
    values = tuple(value for key, value in urllib.parse.parse_qsl(query) if key == "topics")
    if len(values) == 0:
        return None
    if len(values) > 1:
        raise DoraWebBridgeError("topics query parameter must appear at most once")
    topic_texts = tuple(topic for topic in values[0].split(",") if topic)
    if not topic_texts:
        raise DoraWebBridgeError("topics query parameter must not be empty")
    return tuple(_input_id_from_topic(topic) for topic in topic_texts)


def _tail_count_from_query(query: str) -> int | None:
    values = tuple(value for key, value in urllib.parse.parse_qsl(query) if key == "tail")
    if len(values) == 0:
        return None
    if len(values) > 1:
        raise DoraWebBridgeError("tail query parameter must appear at most once")
    try:
        tail_count = int(values[0])
    except ValueError as exc:
        raise DoraWebBridgeError("tail query parameter must be an integer") from exc
    if tail_count < 0:
        raise DoraWebBridgeError("tail query parameter must be non-negative")
    return tail_count


def _after_offset_from_query(query: str) -> int:
    values = tuple(value for key, value in urllib.parse.parse_qsl(query) if key == "after")
    if len(values) == 0:
        return 0
    if len(values) > 1:
        raise DoraWebBridgeError("after query parameter must appear at most once")
    try:
        after_offset = int(values[0])
    except ValueError as exc:
        raise DoraWebBridgeError("after query parameter must be an integer") from exc
    if after_offset < 0:
        raise DoraWebBridgeError("after query parameter must be non-negative")
    return after_offset


def _after_offset_from_request(query: str, headers: http.client.HTTPMessage) -> int:
    after_offset = _after_offset_from_query(query)
    last_event_id = headers.get("Last-Event-ID")
    if last_event_id is None:
        return after_offset
    try:
        last_offset = int(last_event_id)
    except ValueError as exc:
        raise DoraWebBridgeError("Last-Event-ID must be an integer") from exc
    if last_offset < 0:
        raise DoraWebBridgeError("Last-Event-ID must be non-negative")
    return max(after_offset, last_offset + 1)


def _node_log_tail_count_from_query(query: str) -> int:
    tail_count = _tail_count_from_query(query)
    if tail_count is None:
        return DEFAULT_NODE_LOG_TAIL_COUNT
    return tail_count


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


def _send_model(
    handler: BaseHTTPRequestHandler,
    status: int,
    model: BaseModel,
) -> None:
    _send_bytes(
        handler,
        status,
        model.model_dump_json().encode("utf-8"),
        content_type="application/json",
    )


def _send_error(handler: BaseHTTPRequestHandler, status: int, message: str) -> None:
    _send_bytes(handler, status, f"{message}\n".encode("utf-8"), content_type="text/plain")


def _send_bytes(
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
    try:
        handler.wfile.write(body)
    except (BrokenPipeError, ConnectionResetError):
        return


def _send_global_event_stream(
    handler: BaseHTTPRequestHandler,
    store: DoraWebTopicStore,
    *,
    after_offset: int,
    topics: tuple[WebBridgeInputId, ...] | None,
) -> None:
    handler.send_response(200)
    handler.send_header("Content-Type", "text/event-stream")
    handler.send_header("Cache-Control", "no-cache")
    handler.send_header("Connection", "keep-alive")
    handler.end_headers()
    next_offset = after_offset
    while True:
        events = store.wait_for_global_events_after(
            next_offset,
            topics=topics,
            timeout_seconds=DEFAULT_SSE_WAIT_SECONDS,
        )
        if not events:
            try:
                handler.wfile.write(b": heartbeat\n\n")
                handler.wfile.flush()
            except BrokenPipeError:
                return
            continue
        for event in events:
            track_topic = _track_topic_for_event(event.event)
            body = (
                f"id: {event.global_offset}\n"
                "event: dora-topic-event\n"
                f"data: {event.model_dump_json()}\n\n"
                f"id: {event.global_offset}\n"
                f"event: {track_topic}\n"
                f"data: {event.event.model_dump_json()}\n\n"
            ).encode("utf-8")
            try:
                handler.wfile.write(body)
                handler.wfile.flush()
            except BrokenPipeError:
                return
            next_offset = event.global_offset + 1


def _send_topic_event_stream(
    handler: BaseHTTPRequestHandler,
    store: DoraWebTopicStore,
    *,
    topic: str,
    after_offset: int,
) -> None:
    handler.send_response(200)
    handler.send_header("Content-Type", "text/event-stream")
    handler.send_header("Cache-Control", "no-cache")
    handler.send_header("Connection", "keep-alive")
    handler.end_headers()
    next_offset = after_offset
    while True:
        events = store.wait_for_topic_events_after(
            topic,
            next_offset,
            timeout_seconds=DEFAULT_SSE_WAIT_SECONDS,
        )
        if not events:
            try:
                handler.wfile.write(b": heartbeat\n\n")
                handler.wfile.flush()
            except BrokenPipeError:
                return
            continue
        for event in events:
            body = (
                f"id: {event.topic_offset}\n"
                "event: dora-topic-event\n"
                f"data: {event.model_dump_json()}\n\n"
            ).encode("utf-8")
            try:
                handler.wfile.write(body)
                handler.wfile.flush()
            except BrokenPipeError:
                return
            next_offset = event.topic_offset + 1


_DASHBOARD_HTML_PATH = Path(__file__).resolve().with_name("dashboard.html")
DORA_WEB_BRIDGE_DASHBOARD_HTML = _DASHBOARD_HTML_PATH.read_text(encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
