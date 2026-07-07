from pathlib import Path
from xml.etree import ElementTree


REPO_ROOT = Path(__file__).resolve().parents[2]
INTERFACES_DIR = REPO_ROOT / "bridges" / "ros2_bridge" / "fluent_dialogue_dora_interfaces"
MSG_DIR = INTERFACES_DIR / "msg"

EXPECTED_MESSAGE_FILES: tuple[str, ...] = (
    "AgentApprovalRequest.msg",
    "AgentCancelRequest.msg",
    "AgentTextDelta.msg",
    "AgentToolEvent.msg",
    "AgentTurnDone.msg",
    "AsrControl.msg",
    "AudioFrame.msg",
    "DialogueEvent.msg",
    "PlaybackCommand.msg",
    "PlaybackDone.msg",
    "PlaybackState.msg",
    "Transcript.msg",
    "TurnEvent.msg",
    "VoiceActivity.msg",
    "VoiceSessionEvent.msg",
)

EXPECTED_FIELDS: dict[str, tuple[str, ...]] = {
    "AgentApprovalRequest.msg": (
        "std_msgs/Header header",
        "string session_id",
        "string user_turn_id",
        "string approval_id",
        "uint64 seq",
        "string prompt",
        "string action_label",
    ),
    "AgentCancelRequest.msg": (
        "std_msgs/Header header",
        "string session_id",
        "string user_turn_id",
        "uint64 seq",
        "bool reason_present",
        "string reason",
    ),
    "AgentTextDelta.msg": (
        "std_msgs/Header header",
        "string session_id",
        "string user_turn_id",
        "string agent_turn_id",
        "uint64 seq",
        "string text",
    ),
    "AgentToolEvent.msg": (
        "std_msgs/Header header",
        "string session_id",
        "string user_turn_id",
        "string tool_call_id",
        "string tool_name",
        "string event",
        "uint64 seq",
        "string summary",
        "string error_message",
    ),
    "AgentTurnDone.msg": (
        "std_msgs/Header header",
        "string session_id",
        "string user_turn_id",
        "string agent_turn_id",
        "uint64 seq",
        "string status",
        "string message",
    ),
    "AsrControl.msg": (
        "std_msgs/Header header",
        "string action",
        "string session_id",
        "string user_turn_id",
        "string stream_id",
        "uint64 seq",
        "uint64 start_sample_index",
        "uint64 stop_sample_index",
        "string reason",
    ),
    "AudioFrame.msg": (
        "std_msgs/Header header",
        "string source_id",
        "string stream_id",
        "uint64 seq",
        "uint64 sample_index",
        "uint64 capture_time_ns",
        "uint32 frame_count",
        "string encoding",
        "uint32 sample_rate_hz",
        "uint32 channels",
        "uint32 bit_depth",
        "string layout",
        "uint8[] data",
        "bool final",
    ),
    "DialogueEvent.msg": (
        "std_msgs/Header header",
        "string event",
        "string session_id",
        "string user_turn_id",
        "uint64 seq",
        "string text",
        "string request_id",
        "string message",
    ),
    "PlaybackCommand.msg": (
        "std_msgs/Header header",
        "string command",
        "string request_id",
        "string stream_id",
        "uint64 seq",
    ),
    "Transcript.msg": (
        "std_msgs/Header header",
        "string kind",
        "string session_id",
        "string user_turn_id",
        "string stream_id",
        "uint64 seq",
        "string text",
        "uint64 start_sample_index",
        "uint64 end_sample_index",
    ),
    "PlaybackState.msg": (
        "std_msgs/Header header",
        "string request_id",
        "string session_id",
        "string user_turn_id",
        "string stream_id",
        "string state",
        "uint64 seq",
        "uint64 played_frames",
        "string reason",
    ),
    "PlaybackDone.msg": (
        "std_msgs/Header header",
        "string request_id",
        "string session_id",
        "string user_turn_id",
        "string stream_id",
        "string status",
        "bool final_sequence_present",
        "uint64 final_sequence",
        "bool total_frames_present",
        "uint64 total_frames",
        "string reason",
    ),
    "TurnEvent.msg": (
        "std_msgs/Header header",
        "string session_id",
        "string user_turn_id",
        "string stream_id",
        "uint64 seq",
        "uint64 sample_index",
        "string state",
        "bool confidence_present",
        "float32 confidence",
        "bool final",
    ),
    "VoiceActivity.msg": (
        "std_msgs/Header header",
        "string source_id",
        "string stream_id",
        "uint64 seq",
        "uint64 sample_index",
        "uint32 frame_count",
        "string state",
        "float32 speech_probability",
        "bool final",
    ),
    "VoiceSessionEvent.msg": (
        "std_msgs/Header header",
        "string event",
        "string state",
        "uint64 seq",
        "string session_id",
        "string user_turn_id",
        "string assistant_turn_id",
        "string message",
    ),
}


def test_package_metadata_uses_new_interface_package_name() -> None:
    package = ElementTree.parse(INTERFACES_DIR / "package.xml").getroot()

    assert package.findtext("name") == "fluent_dialogue_dora_interfaces"
    assert package.findtext("license") == "Apache-2.0"
    assert package.findtext("export/build_type") == "ament_cmake"


def test_cmake_lists_all_message_files() -> None:
    cmake_text = (INTERFACES_DIR / "CMakeLists.txt").read_text(encoding="utf-8")

    for message_file in EXPECTED_MESSAGE_FILES:
        assert f'"msg/{message_file}"' in cmake_text


def test_message_files_match_declared_contract_subset() -> None:
    actual_message_files = tuple(sorted(path.name for path in MSG_DIR.glob("*.msg")))

    assert actual_message_files == EXPECTED_MESSAGE_FILES
    for message_file, expected_fields in EXPECTED_FIELDS.items():
        assert _field_lines(MSG_DIR / message_file) == expected_fields


def test_ros2_idl_does_not_reintroduce_legacy_integer_turn_ids() -> None:
    legacy_field = "uint32 user_turn_id"
    legacy_package = "fa_interfaces"

    for message_path in MSG_DIR.glob("*.msg"):
        message_text = message_path.read_text(encoding="utf-8")
        assert legacy_field not in message_text
    assert legacy_package not in (INTERFACES_DIR / "CMakeLists.txt").read_text(encoding="utf-8")
    assert legacy_package not in (INTERFACES_DIR / "package.xml").read_text(encoding="utf-8")


def _field_lines(path: Path) -> tuple[str, ...]:
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            lines.append(stripped)
    return tuple(lines)
