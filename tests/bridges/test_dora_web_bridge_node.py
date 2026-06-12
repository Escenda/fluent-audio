from __future__ import annotations

import json
import re
import threading
import urllib.error
import urllib.request

from bridges.dora_web_bridge.main import DoraWebTopicStore
from bridges.dora_web_bridge.main import build_server
from bridges.dora_web_bridge.main import run_dora_web_bridge_events
from bridges.dora_web_bridge.main import DoraWebBridgeConfig
from bridges.dora_web_bridge.messages import WebApprovalResponseSubmission
from bridges.dora_web_bridge.projection import WebAgentTextDeltaEvent
from bridges.dora_web_bridge.projection import WebTranscriptFinalEvent


class FakeDoraNode:
    def __init__(self, events) -> None:
        self._events = events

    def __iter__(self):
        return iter(self._events)


class CapturingCodexControlClient:
    def __init__(self) -> None:
        self.requests: list[tuple[tuple[str, str, str], WebApprovalResponseSubmission]] = []

    def submit_approval_response(
        self,
        key: tuple[str, str, str],
        submission: WebApprovalResponseSubmission,
    ) -> bytes:
        self.requests.append((key, submission))
        return (
            b'{"response":{"session_id":"session-1","user_turn_id":"turn-1",'
            b'"approval_id":"approval-1","seq":0,"decision":"accept","scope":"turn"}}'
        )


def _transcript_event() -> WebTranscriptFinalEvent:
    return WebTranscriptFinalEvent(
        session_id="session-1",
        user_turn_id="turn-1",
        stream_id="transcript/main",
        seq=0,
        created_at_ns=10,
        text="hello",
        start_sample_index=0,
        end_sample_index=16000,
    )


def _agent_text_event() -> WebAgentTextDeltaEvent:
    return WebAgentTextDeltaEvent(
        session_id="session-1",
        user_turn_id="turn-1",
        agent_turn_id="assistant-turn-1",
        seq=0,
        created_at_ns=11,
        text="world",
    )


def test_topic_store_exposes_latest_and_recent_events_without_domain_projection() -> None:
    store = DoraWebTopicStore(input_ids=("transcript", "agent_text"), recent_limit=4)

    item = store.append(input_id="transcript", event=_transcript_event())
    store.append(input_id="agent_text", event=_agent_text_event())
    topics = store.list_topics()
    global_snapshot = store.global_snapshot(tail_count=None)
    topic_snapshot = store.topic_snapshot("transcript", tail_count=None)
    latest = store.latest("transcript")
    filtered_events = store.wait_for_global_events_after(
        0,
        topics=("agent_text",),
        timeout_seconds=0.001,
    )

    assert item.global_offset == 0
    assert item.topic_offset == 0
    assert item.topic == "transcript"
    assert topics.topics[0].event_count == 1
    assert topics.topics[0].latest_event_type == "transcript_final"
    assert global_snapshot.event_count == 2
    assert global_snapshot.events[0] == item
    assert topic_snapshot.events == (item,)
    assert latest.event == item
    assert [event.input_id for event in filtered_events] == ["agent_text"]


def test_dora_web_bridge_keeps_running_across_non_input_dora_events() -> None:
    store = DoraWebTopicStore(input_ids=("transcript",), recent_limit=4)
    node = FakeDoraNode(
        (
            {"type": "UNKNOWN"},
            {"type": "STOP"},
        )
    )

    summary = run_dora_web_bridge_events(
        node,
        DoraWebBridgeConfig(
            session_id="session-1",
            host="127.0.0.1",
            port=1,
            input_ids=("transcript",),
        ),
        store,
    )

    assert summary.event_count == 0
    assert summary.non_input_events == 1


def test_http_bridge_serves_dashboard_topic_snapshots_logs_and_proxies_approval_response(
    tmp_path,
) -> None:
    store = DoraWebTopicStore(input_ids=("transcript",), recent_limit=4)
    store.append(input_id="transcript", event=_transcript_event())
    control_client = CapturingCodexControlClient()
    runtime_log = tmp_path / "runtime.log"
    runtime_log.write_text(
        "other: hidden\n"
        "dora_web_bridge: first\n"
        "codex_app_server: second\n"
        "dora_web_bridge: third\n",
        encoding="utf-8",
    )
    server = build_server(
        "127.0.0.1",
        0,
        store,
        control_client=control_client,
        runtime_log_path=runtime_log,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        dashboard = _get_text(server.server_port, "/")
        assert 'id="topics"' in dashboard
        assert 'id="initial-data"' in dashboard
        assert "loadTopics" in dashboard
        assert "loadSessions" not in dashboard
        initial_data = _initial_dashboard_data(dashboard)
        assert initial_data["snapshot"]["event_count"] == 1
        assert initial_data["snapshot"]["events"][0]["event"]["text"] == "hello"
        assert initial_data["topics"]["topics"][0]["topic"] == "transcript"

        topics = _get_json(server.server_port, "/api/topics")
        assert topics["topics"][0]["topic"] == "transcript"
        assert topics["topics"][0]["event_count"] == 1

        events = _get_json(server.server_port, "/api/events.json?tail=10")
        assert events["event_count"] == 1
        assert events["events"][0]["event"]["event_type"] == "transcript_final"

        latest = _get_json(server.server_port, "/api/topics/transcript/latest.json")
        assert latest["event"]["event"]["text"] == "hello"

        node_status = _get_json(server.server_port, "/api/node-status.json")
        assert [node["node_id"] for node in node_status["nodes"]][0] == "dora_web_bridge"

        node_log = _get_json(server.server_port, "/api/node-logs/dora_web_bridge.json?tail=2")
        assert node_log["available"] is True
        assert node_log["lines"] == ["dora_web_bridge: first", "dora_web_bridge: third"]

        body = json.dumps({"decision": "accept", "scope": "turn"}).encode("utf-8")
        response = _post_json(
            server.server_port,
            "/api/agent-approvals/session-1/user-turns/turn-1/approval-requests/"
            "approval-1/responses",
            body,
        )
        assert response["response"]["approval_id"] == "approval-1"
        assert control_client.requests == [
            (
                ("session-1", "turn-1", "approval-1"),
                WebApprovalResponseSubmission(decision="accept", scope="turn"),
            )
        ]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2.0)


def _get_json(port: int, path: str):
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        headers={"Accept": "application/json"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=5.0) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_text(port: int, path: str) -> str:
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        headers={"Accept": "text/html"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=5.0) as response:
        return response.read().decode("utf-8")


def _post_json(port: int, path: str, body: bytes):
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=body,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5.0) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise AssertionError(exc.read().decode("utf-8", errors="replace")) from exc


def _initial_dashboard_data(dashboard: str):
    match = re.search(
        r'<script id="initial-data" type="application/json">(.+?)</script>',
        dashboard,
    )
    assert match is not None
    return json.loads(match.group(1))
