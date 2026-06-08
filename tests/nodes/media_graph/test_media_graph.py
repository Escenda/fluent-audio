import pytest
from pydantic import ValidationError

from fluent_audio.contracts import AudioChunk, AudioFormat, require_contiguous_audio_chunks
from fluent_audio.dora import (
    decode_audio_chunk_from_dora,
    encode_audio_chunk_for_dora,
    encode_audio_final_marker_for_dora,
    validate_dora_audio_metadata,
)
from nodes.media_graph.main import (
    GStreamerMediaGraph,
    MediaGraphConfig,
    MediaGraphConfigError,
    MediaGraphInputError,
    build_audio_caps,
    build_pipeline_description,
    run_media_graph_events,
    sample_format_to_gst,
)


class FakeDoraOutputNode:
    def __init__(self) -> None:
        self.sent = []

    def send_output(self, output_id, data, metadata=None) -> None:
        self.sent.append((output_id, data, metadata))


def _audio_format(
    *,
    sample_rate_hz: int = 16_000,
    channels: int = 1,
    sample_format: str = "s16le",
) -> AudioFormat:
    return AudioFormat(
        sample_rate_hz=sample_rate_hz,
        channels=channels,
        sample_format=sample_format,
        channel_layout="interleaved",
    )


def _config(
    *,
    input_format: AudioFormat | None = None,
    output_format: AudioFormat | None = None,
    enable_tap: bool = False,
) -> MediaGraphConfig:
    return MediaGraphConfig(
        input_source_id="offline_file",
        input_stream_id="audio/offline/source",
        input_format=input_format or _audio_format(),
        output_source_id="media_graph",
        output_stream_id="audio/media_graph/main",
        output_format=output_format or _audio_format(),
        output_start_seq=0,
        output_start_sample_index=0,
        output_start_capture_time_ns=0,
        enable_tap=enable_tap,
        tap_source_id="media_graph_tap" if enable_tap else None,
        tap_stream_id="audio/media_graph/tap" if enable_tap else None,
        tap_start_seq=0,
        tap_start_sample_index=0,
        tap_start_capture_time_ns=0,
    )


def _chunk(
    *,
    seq: int,
    sample_index: int,
    frame_count: int = 2,
    audio_format: AudioFormat | None = None,
    payload: bytes | None = None,
) -> AudioChunk:
    resolved_format = audio_format or _audio_format()
    return AudioChunk(
        source_id="offline_file",
        stream_id="audio/offline/source",
        seq=seq,
        sample_index=sample_index,
        capture_time_ns=(sample_index * 1_000_000_000) // resolved_format.sample_rate_hz,
        frame_count=frame_count,
        format=resolved_format,
        payload=payload
        if payload is not None
        else b"\x00" * (frame_count * resolved_format.frame_size_bytes),
    )


def _dora_input_event(chunk: AudioChunk):
    payload, metadata = encode_audio_chunk_for_dora(chunk)
    return {
        "type": "INPUT",
        "id": "audio",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _dora_final_event(
    *,
    seq: int,
    sample_index: int,
    audio_format: AudioFormat | None = None,
):
    resolved_format = audio_format or _audio_format()
    payload, metadata = encode_audio_final_marker_for_dora(
        source_id="offline_file",
        stream_id="audio/offline/source",
        seq=seq,
        sample_index=sample_index,
        capture_time_ns=(sample_index * 1_000_000_000) // resolved_format.sample_rate_hz,
        audio_format=resolved_format,
    )
    return {
        "type": "INPUT",
        "id": "audio",
        "value": payload,
        "metadata": metadata.to_dora_metadata(),
    }


def _output_chunks(fake_node: FakeDoraOutputNode, output_id: str) -> list[AudioChunk]:
    chunks: list[AudioChunk] = []
    for sent_output_id, payload, metadata in fake_node.sent:
        if sent_output_id != output_id:
            continue
        audio_metadata = validate_dora_audio_metadata(metadata)
        if not audio_metadata.final:
            chunks.append(decode_audio_chunk_from_dora(payload, audio_metadata))
    return chunks


def _final_count(fake_node: FakeDoraOutputNode, output_id: str) -> int:
    final_count = 0
    for sent_output_id, _payload, metadata in fake_node.sent:
        if sent_output_id == output_id and validate_dora_audio_metadata(metadata).final:
            final_count += 1
    return final_count


def _final_metadata(fake_node: FakeDoraOutputNode, output_id: str):
    final_markers = [
        validate_dora_audio_metadata(metadata)
        for sent_output_id, _payload, metadata in fake_node.sent
        if sent_output_id == output_id and validate_dora_audio_metadata(metadata).final
    ]
    assert len(final_markers) == 1
    return final_markers[0]


def _sent_output_ids(fake_node: FakeDoraOutputNode, output_id: str) -> list[str]:
    return [
        sent_output_id
        for sent_output_id, _payload, _metadata in fake_node.sent
        if sent_output_id == output_id
    ]


def test_build_audio_caps_uses_explicit_gstreamer_mapping() -> None:
    assert build_audio_caps(_audio_format(sample_format="s16le")) == (
        "audio/x-raw,format=S16LE,rate=16000,channels=1,layout=interleaved"
    )
    assert build_audio_caps(
        _audio_format(sample_rate_hz=48_000, channels=2, sample_format="f32le")
    ) == ("audio/x-raw,format=F32LE,rate=48000,channels=2,layout=interleaved")


def test_sample_format_mapping_rejects_unknown_format() -> None:
    try:
        sample_format_to_gst("u8")
    except MediaGraphConfigError as exc:
        assert "Unsupported GStreamer sample format" in str(exc)
    else:
        raise AssertionError("sample_format_to_gst accepted an unsupported format")


def test_tap_config_requires_explicit_tap_ids() -> None:
    with pytest.raises(ValidationError, match="tap_source_id is required"):
        MediaGraphConfig(
            input_source_id="offline_file",
            input_stream_id="audio/offline/source",
            input_format=_audio_format(),
            output_source_id="media_graph",
            output_stream_id="audio/media_graph/main",
            output_format=_audio_format(),
            output_start_seq=0,
            output_start_sample_index=0,
            output_start_capture_time_ns=0,
            enable_tap=True,
        )


def test_pipeline_description_contains_bounded_tee_queues_only_when_tap_enabled() -> None:
    single_branch_description = build_pipeline_description(_config(enable_tap=False))
    tap_description = build_pipeline_description(_config(enable_tap=True))

    assert "tee name=audio_tee" not in single_branch_description
    assert "tee name=audio_tee" in tap_description
    assert "appsink name=tap_audio_sink" in tap_description
    assert (
        "queue name=audio_queue max-size-buffers=8 max-size-bytes=0 max-size-time=0"
        in tap_description
    )
    assert (
        "queue name=tap_audio_queue max-size-buffers=8 max-size-bytes=0 max-size-time=0"
        in tap_description
    )


def test_gstreamer_graph_sets_appsrc_and_capsfilter_caps() -> None:
    graph = GStreamerMediaGraph(_config())
    try:
        expected_input_caps = build_audio_caps(_audio_format())
        expected_output_caps = build_audio_caps(_audio_format())

        expected_input = graph.Gst.Caps.from_string(expected_input_caps)
        expected_output = graph.Gst.Caps.from_string(expected_output_caps)

        assert graph.appsrc.get_property("caps").is_equal(expected_input)
        assert graph._required_element("input_caps").get_property("caps").is_equal(expected_input)
        assert graph._required_element("output_caps").get_property("caps").is_equal(expected_output)
    finally:
        graph.close()


def test_passthrough_preserves_payload_and_emits_valid_tap_branch() -> None:
    first = _chunk(seq=0, sample_index=0, payload=b"abcd")
    second = _chunk(seq=1, sample_index=2, payload=b"efgh")
    fake_node = FakeDoraOutputNode()

    summary = run_media_graph_events(
        [
            _dora_input_event(first),
            _dora_input_event(second),
            _dora_final_event(seq=2, sample_index=4),
        ],
        fake_node,
        _config(enable_tap=True),
    )

    main_chunks = _output_chunks(fake_node, "audio")
    tap_chunks = _output_chunks(fake_node, "tap_audio")

    assert b"".join(chunk.payload for chunk in main_chunks) == b"abcdefgh"
    assert b"".join(chunk.payload for chunk in tap_chunks) == b"abcdefgh"
    assert [chunk.source_id for chunk in main_chunks] == ["media_graph", "media_graph"]
    assert [chunk.stream_id for chunk in tap_chunks] == [
        "audio/media_graph/tap",
        "audio/media_graph/tap",
    ]
    assert [chunk.seq for chunk in main_chunks] == [0, 1]
    assert [chunk.sample_index for chunk in main_chunks] == [0, 2]
    assert _final_count(fake_node, "audio") == 1
    assert _final_count(fake_node, "tap_audio") == 1
    assert summary.input_chunks == 2
    assert summary.main_output_chunks == 2
    assert summary.tap_output_chunks == 2


def test_resample_emits_output_format_and_contiguous_metadata() -> None:
    input_format = _audio_format(sample_rate_hz=48_000, channels=2)
    output_format = _audio_format(sample_rate_hz=16_000, channels=2)
    payload = b"\x00" * (480 * input_format.frame_size_bytes)
    fake_node = FakeDoraOutputNode()

    run_media_graph_events(
        [
            _dora_input_event(
                _chunk(
                    seq=0,
                    sample_index=0,
                    frame_count=480,
                    audio_format=input_format,
                    payload=payload,
                )
            ),
            _dora_final_event(seq=1, sample_index=480, audio_format=input_format),
        ],
        fake_node,
        _config(input_format=input_format, output_format=output_format),
    )

    main_chunks = _output_chunks(fake_node, "audio")

    assert main_chunks
    assert all(chunk.format == output_format for chunk in main_chunks)
    assert all(
        chunk.payload_size_bytes % output_format.frame_size_bytes == 0 for chunk in main_chunks
    )
    for previous, current in zip(main_chunks, main_chunks[1:]):
        require_contiguous_audio_chunks(previous, current)


def test_resample_final_marker_is_sent_after_eos_drain() -> None:
    input_format = _audio_format(sample_rate_hz=48_000, channels=2)
    output_format = _audio_format(sample_rate_hz=16_000, channels=2)
    payload = b"\x00" * (480 * input_format.frame_size_bytes)
    fake_node = FakeDoraOutputNode()

    run_media_graph_events(
        [
            _dora_input_event(
                _chunk(
                    seq=0,
                    sample_index=0,
                    frame_count=480,
                    audio_format=input_format,
                    payload=payload,
                )
            ),
            _dora_final_event(seq=1, sample_index=480, audio_format=input_format),
        ],
        fake_node,
        _config(input_format=input_format, output_format=output_format),
    )

    main_chunks = _output_chunks(fake_node, "audio")
    final_metadata = _final_metadata(fake_node, "audio")
    total_output_frames = sum(chunk.frame_count for chunk in main_chunks)

    assert _sent_output_ids(fake_node, "audio")[-1] == "audio"
    assert validate_dora_audio_metadata(fake_node.sent[-1][2]).final
    assert total_output_frames == 160
    assert final_metadata.seq == len(main_chunks)
    assert final_metadata.sample_index == total_output_frames
    assert final_metadata.capture_time_ns == (total_output_frames * 1_000_000_000) // 16_000


def test_finish_sends_final_only_after_post_eos_drain_cycle_is_empty() -> None:
    input_format = _audio_format(sample_rate_hz=48_000, channels=2)
    output_format = _audio_format(sample_rate_hz=16_000, channels=2)
    payload = b"\x00" * (480 * input_format.frame_size_bytes)
    fake_node = FakeDoraOutputNode()
    graph = GStreamerMediaGraph(_config(input_format=input_format, output_format=output_format))

    try:
        graph.push_chunk(
            _chunk(
                seq=0,
                sample_index=0,
                frame_count=480,
                audio_format=input_format,
                payload=payload,
            ),
            fake_node,
        )
        assert _final_count(fake_node, "audio") == 0

        graph.finish(fake_node)

        main_chunks = _output_chunks(fake_node, "audio")
        total_output_frames = sum(chunk.frame_count for chunk in main_chunks)
        final_metadata = _final_metadata(fake_node, "audio")

        assert main_chunks
        assert validate_dora_audio_metadata(fake_node.sent[-1][2]).final
        assert total_output_frames == 160
        assert final_metadata.sample_index == total_output_frames
        assert graph.drain_available(fake_node)
        assert _final_count(fake_node, "audio") == 1
    finally:
        graph.close()


def test_rejects_input_format_mismatch() -> None:
    input_format = _audio_format(sample_rate_hz=48_000)

    with pytest.raises(MediaGraphInputError, match="input format mismatch"):
        run_media_graph_events(
            [
                _dora_input_event(
                    _chunk(seq=0, sample_index=0, audio_format=input_format, payload=b"\x00" * 4)
                ),
                _dora_final_event(seq=1, sample_index=2, audio_format=input_format),
            ],
            FakeDoraOutputNode(),
            _config(),
        )


def test_input_closed_after_explicit_final_is_success() -> None:
    fake_node = FakeDoraOutputNode()

    summary = run_media_graph_events(
        [
            _dora_input_event(_chunk(seq=0, sample_index=0, payload=b"abcd")),
            _dora_final_event(seq=1, sample_index=2),
            {"type": "INPUT_CLOSED", "id": "audio"},
        ],
        fake_node,
        _config(),
    )

    assert summary.input_chunks == 1
    assert _final_count(fake_node, "audio") == 1


def test_rejects_input_closed_without_explicit_final() -> None:
    with pytest.raises(MediaGraphInputError, match="input closed before explicit final marker"):
        run_media_graph_events(
            [
                _dora_input_event(_chunk(seq=0, sample_index=0, payload=b"abcd")),
                {"type": "INPUT_CLOSED", "id": "audio"},
            ],
            FakeDoraOutputNode(),
            _config(),
        )
