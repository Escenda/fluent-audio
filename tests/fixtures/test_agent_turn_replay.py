from pathlib import Path

from fluent_dialogue_dora.contracts import AgentTurnRequest
from fluent_dialogue_dora.dora import decode_agent_turn_request_from_dora
from tests.fixtures.dora.agent_turn_replay import main, send_agent_turn_request_dora


class CapturingDoraNode:
    def __init__(self) -> None:
        self.outputs = []

    def send_output(self, output_id, payload, metadata) -> None:
        self.outputs.append((output_id, payload, metadata))


def test_agent_turn_replay_emits_typed_dora_request() -> None:
    node = CapturingDoraNode()
    request = AgentTurnRequest(
        session_id="session-1",
        user_turn_id="user-turn-1",
        assistant_turn_id="assistant-turn-1",
        seq=0,
        text="hello",
    )

    send_agent_turn_request_dora(node, request)

    assert len(node.outputs) == 1
    output_id, payload, metadata = node.outputs[0]
    assert output_id == "agent_turn"
    assert decode_agent_turn_request_from_dora(payload, metadata) == request


def test_agent_turn_replay_accepts_text_file(tmp_path: Path, capsys) -> None:
    text_file = tmp_path / "turn.txt"
    text_file.write_text("hello from file\n", encoding="utf-8")

    result = main(
        [
            "--session-id",
            "session-1",
            "--user-turn-id",
            "user-turn-1",
            "--assistant-turn-id",
            "assistant-turn-1",
            "--text-file",
            str(text_file),
        ]
    )

    assert result == 0
    captured = capsys.readouterr()
    assert AgentTurnRequest.model_validate_json(captured.out).text == "hello from file"
