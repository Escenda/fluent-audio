use std::str::FromStr;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::mpsc::{sync_channel, Receiver, SyncSender, TryRecvError};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

use clap::{Parser, ValueEnum};
use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use cpal::{BufferSize, Device, DeviceId, StreamConfig};
use dora_node_api::dora_core::config::DataId;
use dora_node_api::{into_vec, DoraNode, Event, Metadata};
use fluent_dialogue_dora_contracts::fluent_dialogue_dora::v1::{PlaybackControlCommand, PlaybackControlKind};
use fluent_dialogue_dora_io_boundary::{
    capture_time_ns_for_frame_offset, i16_samples_to_s16le_bytes, protobuf_message_type,
    s16le_bytes_to_i16_samples, AudioBoundaryError, AudioChunk, AudioFormat, AudioMetadata,
    ChannelLayout, DoraAudioMessage, ExpectedAudioStream, SampleFormat, AUDIO_INPUT_ID,
};
use prost::Message;
use thiserror::Error;

/// DORA input id carrying a device-level flush control for the speaker sink.
const PLAYBACK_CONTROL_INPUT_ID: &str = "playback_control";
const PLAYBACK_CONTROL_MESSAGE_TYPE: &str = "fluent_dialogue_dora.v1.PlaybackControlCommand";
const RENDER_REFERENCE_OUTPUT_ID: &str = "render_reference";

#[derive(Debug, Error)]
enum SinkError {
    #[error("choose exactly one of --device-name, --device-id, or --default-output-device")]
    DeviceSelection,
    #[error("failed to parse CPAL device id {id:?}: {source}")]
    DeviceIdParse {
        id: String,
        #[source]
        source: cpal::Error,
    },
    #[error("CPAL output device id {0:?} was not found")]
    DeviceIdNotFound(String),
    #[error("no default CPAL output device is available")]
    NoDefaultDevice,
    #[error("CPAL output device {0:?} was not found")]
    DeviceNotFound(String),
    #[error("multiple CPAL output devices matched {0:?}; use an exact device name")]
    AmbiguousDevice(String),
    #[error("failed to enumerate CPAL output devices: {0}")]
    DeviceEnumeration(#[source] cpal::Error),
    #[error("failed to build CPAL output stream: {0}")]
    BuildStream(#[source] cpal::Error),
    #[error("failed to start CPAL output stream: {0}")]
    PlayStream(#[source] cpal::Error),
    #[error("CPAL output stream error: {0}")]
    Stream(String),
    #[error("startup buffer chunks {startup_buffer_chunks} exceeds queue capacity chunks {queue_capacity_chunks}")]
    StartupBufferExceedsQueue {
        startup_buffer_chunks: usize,
        queue_capacity_chunks: usize,
    },
    #[error("playback underrun occurred; no configured fill policy exists")]
    Underrun,
    #[error("playback did not finish within {0:?}")]
    CompletionTimeout(Duration),
    #[error("unexpected DORA input id {0:?}")]
    UnexpectedInput(String),
    #[error("playback control metadata is invalid: {0}")]
    ControlMetadata(String),
    #[error("playback control protobuf could not decode: {0}")]
    ControlPayload(#[source] prost::DecodeError),
    #[error("playback control stream_id {got:?} does not match sink stream_id {expected:?}")]
    ControlStreamMismatch { expected: String, got: String },
    #[error("playback control kind {0} is unsupported")]
    ControlKind(i32),
    #[error("playback control seq {got} is not strictly greater than previous {previous}")]
    ControlSeqRegressed { previous: u64, got: u64 },
    #[error("render reference source and stream id must be provided together")]
    RenderReferenceSelection,
    #[error("render reference channel overflowed before DORA could forward it")]
    RenderReferenceDropped,
    #[error("upstream node failed: {0}")]
    UpstreamFailed(String),
    #[error("DORA node initialization failed: {0}")]
    DoraInit(#[source] eyre::Report),
    #[error("audio boundary error: {0}")]
    AudioBoundary(#[from] fluent_dialogue_dora_io_boundary::AudioBoundaryError),
    #[error("DORA audio payload could not decode as u8 array: {0}")]
    DoraPayload(#[source] eyre::Report),
    #[error("DORA output failed: {0}")]
    DoraOutput(#[source] eyre::Report),
}

#[derive(Parser, Debug)]
#[command(about = "Receive DORA audio input and play explicit s16le chunks through CPAL.")]
struct Args {
    #[arg(long)]
    device_name: Option<String>,
    #[arg(long)]
    device_id: Option<String>,
    #[arg(long, default_value_t = false)]
    default_output_device: bool,
    #[arg(long)]
    sample_rate_hz: u32,
    #[arg(long)]
    channels: u16,
    #[arg(long, value_parser = ["s16le"])]
    sample_format: String,
    #[arg(long, value_parser = ["interleaved"])]
    channel_layout: String,
    #[arg(long)]
    buffer_size_frames: u32,
    #[arg(long)]
    queue_capacity_chunks: usize,
    #[arg(long)]
    startup_buffer_chunks: usize,
    #[arg(long, value_enum, default_value_t = EmptyQueuePolicy::Error)]
    empty_queue_policy: EmptyQueuePolicy,
    #[arg(long)]
    source_id: String,
    #[arg(long)]
    stream_id: String,
    #[arg(long)]
    completion_timeout_ms: u64,
    #[arg(long)]
    render_reference_source_id: Option<String>,
    #[arg(long)]
    render_reference_stream_id: Option<String>,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, ValueEnum)]
enum EmptyQueuePolicy {
    Error,
    Silence,
}

#[derive(Clone, Debug)]
struct SinkConfig {
    device_name: Option<String>,
    device_id: Option<String>,
    use_default_device: bool,
    format: AudioFormat,
    buffer_size_frames: u32,
    queue_capacity_chunks: usize,
    startup_buffer_chunks: usize,
    empty_queue_policy: EmptyQueuePolicy,
    source_id: String,
    stream_id: String,
    completion_timeout: Duration,
    render_reference: Option<RenderReferenceConfig>,
}

#[derive(Clone, Debug)]
struct RenderReferenceConfig {
    source_id: String,
    stream_id: String,
    format: AudioFormat,
}

impl TryFrom<Args> for SinkConfig {
    type Error = SinkError;

    fn try_from(args: Args) -> Result<Self, Self::Error> {
        let selectors = args.device_name.is_some() as u8
            + args.device_id.is_some() as u8
            + args.default_output_device as u8;
        if selectors != 1 {
            return Err(SinkError::DeviceSelection);
        }
        let format = AudioFormat::new(
            args.sample_rate_hz,
            args.channels,
            args.sample_format.parse::<SampleFormat>()?,
            args.channel_layout.parse::<ChannelLayout>()?,
        )?;
        if args.buffer_size_frames == 0 {
            return Err(SinkError::AudioBoundary(
                fluent_dialogue_dora_io_boundary::AudioBoundaryError::NonPositive {
                    field: "buffer_size_frames",
                    value: u64::from(args.buffer_size_frames),
                },
            ));
        }
        if args.queue_capacity_chunks == 0 {
            return Err(SinkError::AudioBoundary(
                fluent_dialogue_dora_io_boundary::AudioBoundaryError::NonPositive {
                    field: "queue_capacity_chunks",
                    value: args.queue_capacity_chunks as u64,
                },
            ));
        }
        if args.startup_buffer_chunks == 0 {
            return Err(SinkError::AudioBoundary(
                fluent_dialogue_dora_io_boundary::AudioBoundaryError::NonPositive {
                    field: "startup_buffer_chunks",
                    value: args.startup_buffer_chunks as u64,
                },
            ));
        }
        if args.startup_buffer_chunks > args.queue_capacity_chunks {
            return Err(SinkError::StartupBufferExceedsQueue {
                startup_buffer_chunks: args.startup_buffer_chunks,
                queue_capacity_chunks: args.queue_capacity_chunks,
            });
        }
        if args.completion_timeout_ms == 0 {
            return Err(SinkError::AudioBoundary(
                fluent_dialogue_dora_io_boundary::AudioBoundaryError::NonPositive {
                    field: "completion_timeout_ms",
                    value: args.completion_timeout_ms,
                },
            ));
        }
        let render_reference = match (
            args.render_reference_source_id,
            args.render_reference_stream_id,
        ) {
            (Some(source_id), Some(stream_id)) => Some(RenderReferenceConfig {
                source_id,
                stream_id,
                format,
            }),
            (None, None) => None,
            _ => return Err(SinkError::RenderReferenceSelection),
        };
        Ok(Self {
            device_name: args.device_name,
            device_id: args.device_id,
            use_default_device: args.default_output_device,
            format,
            buffer_size_frames: args.buffer_size_frames,
            queue_capacity_chunks: args.queue_capacity_chunks,
            startup_buffer_chunks: args.startup_buffer_chunks,
            empty_queue_policy: args.empty_queue_policy,
            source_id: args.source_id,
            stream_id: args.stream_id,
            completion_timeout: Duration::from_millis(args.completion_timeout_ms),
            render_reference,
        })
    }
}

#[derive(Debug)]
enum PlaybackMessage {
    Chunk(Vec<i16>),
    Final,
    StreamError(String),
}

/// Number of interleaved samples covered by a fade of `fade_out_ms` at the
/// given rate/channel count. Pure for unit testing.
fn fade_length_samples(fade_out_ms: u32, sample_rate_hz: u32, channels: u16) -> usize {
    let frames = (u64::from(fade_out_ms) * u64::from(sample_rate_hz)) / 1000;
    (frames as usize) * usize::from(channels)
}

/// Apply a linear fade ramp to one sample. `remaining`/`total` go from
/// total..0 across the fade; `total == 0` means no fade (pass through). Pure.
fn ramped_sample(raw: i16, remaining: usize, total: usize) -> i16 {
    if total == 0 {
        return raw;
    }
    let ramp = remaining as f32 / total as f32;
    (f32::from(raw) * ramp).round() as i16
}

/// Shared flush state between the DORA event loop and the CPAL callback.
/// The loop bumps `seq` after publishing `fade_samples`; the callback observes
/// a changed `seq`, reads `fade_samples`, fades out, then drops the buffered
/// tail. There is no request id: a flush acts on whatever the sink has buffered.
#[derive(Clone)]
struct FlushSignal {
    seq: Arc<AtomicU64>,
    fade_samples: Arc<AtomicU64>,
}

impl FlushSignal {
    fn new() -> Self {
        Self {
            seq: Arc::new(AtomicU64::new(0)),
            fade_samples: Arc::new(AtomicU64::new(0)),
        }
    }

    fn request_flush(&self, fade_samples: usize) {
        self.fade_samples
            .store(fade_samples as u64, Ordering::SeqCst);
        self.seq.fetch_add(1, Ordering::SeqCst);
    }
}

/// Validates and applies one PlaybackControlCommand against the sink config.
struct FlushControl {
    signal: FlushSignal,
    stream_id: String,
    sample_rate_hz: u32,
    channels: u16,
    last_seq: Option<u64>,
}

impl FlushControl {
    fn apply(&mut self, metadata: &Metadata, payload: &[u8]) -> Result<(), SinkError> {
        let message_type = protobuf_message_type(metadata)
            .map_err(|err| SinkError::ControlMetadata(err.to_string()))?;
        if message_type != PLAYBACK_CONTROL_MESSAGE_TYPE {
            return Err(SinkError::ControlMetadata(format!(
                "expected {PLAYBACK_CONTROL_MESSAGE_TYPE}, got {message_type:?}"
            )));
        }
        let command = PlaybackControlCommand::decode(payload).map_err(SinkError::ControlPayload)?;
        self.validate_command(&command)?;
        self.last_seq = Some(command.seq);
        let fade_samples =
            fade_length_samples(command.fade_out_ms, self.sample_rate_hz, self.channels);
        self.signal.request_flush(fade_samples);
        Ok(())
    }

    /// Validate a decoded control command against the sink stream id and the
    /// monotonic seq contract. Pure (no I/O), so it is unit-testable.
    fn validate_command(&self, command: &PlaybackControlCommand) -> Result<(), SinkError> {
        if command.kind != PlaybackControlKind::Flush as i32 {
            return Err(SinkError::ControlKind(command.kind));
        }
        if command.stream_id != self.stream_id {
            return Err(SinkError::ControlStreamMismatch {
                expected: self.stream_id.clone(),
                got: command.stream_id.clone(),
            });
        }
        if let Some(previous) = self.last_seq {
            if command.seq <= previous {
                return Err(SinkError::ControlSeqRegressed {
                    previous,
                    got: command.seq,
                });
            }
        }
        Ok(())
    }
}

fn main() -> Result<(), SinkError> {
    let config = SinkConfig::try_from(Args::parse())?;
    run(config)
}

fn run(config: SinkConfig) -> Result<(), SinkError> {
    let (mut node, mut events) = DoraNode::init_from_env().map_err(SinkError::DoraInit)?;
    let host = cpal::default_host();
    let device = select_output_device(&host, &config)?;
    eprintln!("cpal_sink: output_device={}", device_name(&device));

    let stream_config = StreamConfig {
        channels: config.format.channels,
        sample_rate: config.format.sample_rate_hz,
        buffer_size: BufferSize::Fixed(config.buffer_size_frames),
    };
    let (sender, receiver) = sync_channel(config.queue_capacity_chunks);
    let underrun = Arc::new(AtomicBool::new(false));
    let done = Arc::new(AtomicBool::new(false));
    let stream_error = Arc::new(AtomicBool::new(false));
    let render_reference_dropped = Arc::new(AtomicBool::new(false));
    let (render_reference_sender, render_reference_receiver) =
        config.render_reference.as_ref().map_or((None, None), |_| {
            let (sender, receiver) = sync_channel(config.queue_capacity_chunks);
            (Some(sender), Some(receiver))
        });
    let flush = FlushSignal::new();
    let stream = build_s16le_output_stream(
        &device,
        stream_config,
        receiver,
        Arc::clone(&underrun),
        Arc::clone(&done),
        Arc::clone(&stream_error),
        sender.clone(),
        config.empty_queue_policy,
        flush.clone(),
        render_reference_sender,
        Arc::clone(&render_reference_dropped),
    )?;
    let mut render_reference = RenderReferenceEmitter::new(
        config.render_reference.clone(),
        render_reference_receiver,
        RENDER_REFERENCE_OUTPUT_ID.to_owned(),
    );

    let mut flush_control = FlushControl {
        signal: flush,
        stream_id: config.stream_id.clone(),
        sample_rate_hz: config.format.sample_rate_hz,
        channels: config.format.channels,
        last_seq: None,
    };
    let mut expected = ExpectedAudioStream::new(
        config.source_id.clone(),
        config.stream_id.clone(),
        config.format,
    );
    let mut chunks_queued = 0_usize;
    let mut final_received = false;
    while let Some(event) = events.recv() {
        handle_dora_event(
            event,
            &sender,
            &mut expected,
            &mut chunks_queued,
            &mut final_received,
            &mut flush_control,
        )?;
        if chunks_queued >= config.startup_buffer_chunks || final_received {
            break;
        }
    }

    stream.play().map_err(SinkError::PlayStream)?;

    if !final_received {
        while !final_received {
            render_reference.drain(&mut node)?;
            if render_reference_dropped.load(Ordering::SeqCst) {
                return Err(SinkError::RenderReferenceDropped);
            }
            if let Some(event) = events.recv_timeout(Duration::from_millis(5)) {
                if is_recv_timeout(&event) {
                    continue;
                }
                handle_dora_event(
                    event,
                    &sender,
                    &mut expected,
                    &mut chunks_queued,
                    &mut final_received,
                    &mut flush_control,
                )?;
            } else {
                break;
            }
            if final_received {
                break;
            }
            if underrun.load(Ordering::SeqCst) {
                return Err(SinkError::Underrun);
            }
            if stream_error.load(Ordering::SeqCst) {
                return Err(SinkError::Stream("unknown CPAL output error".to_owned()));
            }
        }
    }

    wait_for_playback_completion(
        &config,
        &mut node,
        &mut render_reference,
        underrun,
        done,
        stream_error,
        render_reference_dropped,
    )
}

fn handle_dora_event(
    event: Event,
    sender: &SyncSender<PlaybackMessage>,
    expected: &mut ExpectedAudioStream,
    chunks_queued: &mut usize,
    final_received: &mut bool,
    flush_control: &mut FlushControl,
) -> Result<(), SinkError> {
    match event {
        Event::Input { id, metadata, data } => {
            if id == DataId::from(PLAYBACK_CONTROL_INPUT_ID.to_owned()) {
                let payload = into_vec::<u8>(&data).map_err(SinkError::DoraPayload)?;
                return flush_control.apply(&metadata, &payload);
            }
            if id != DataId::from(AUDIO_INPUT_ID.to_owned()) {
                return Err(SinkError::UnexpectedInput(id.to_string()));
            }
            let payload = into_vec::<u8>(&data).map_err(SinkError::DoraPayload)?;
            match DoraAudioMessage::decode(&metadata, &payload)? {
                DoraAudioMessage::Chunk(chunk) => {
                    validate_playback_chunk(expected, &chunk)?;
                    let samples = s16le_bytes_to_i16_samples(&chunk.payload)?;
                    send_playback_message(sender, PlaybackMessage::Chunk(samples))?;
                    *chunks_queued += 1;
                }
                DoraAudioMessage::Final(audio_metadata) => {
                    expected.validate_final_marker(&audio_metadata, 0)?;
                    send_playback_message(sender, PlaybackMessage::Final)?;
                    *final_received = true;
                }
            }
            Ok(())
        }
        Event::InputClosed { id } => {
            // The optional control input closing first is not a playback failure.
            if id == DataId::from(PLAYBACK_CONTROL_INPUT_ID.to_owned()) {
                return Ok(());
            }
            if id != DataId::from(AUDIO_INPUT_ID.to_owned()) {
                return Err(SinkError::UnexpectedInput(id.to_string()));
            }
            Err(SinkError::Stream(
                "DORA audio input closed before explicit protobuf final marker".to_owned(),
            ))
        }
        Event::NodeFailed { error, .. } => Err(SinkError::UpstreamFailed(error)),
        Event::Stop(_) => {
            send_playback_message(sender, PlaybackMessage::Final)?;
            *final_received = true;
            Ok(())
        }
        Event::Error(error) if is_recv_timeout_error(&error) => Ok(()),
        Event::Error(error) => Err(SinkError::Stream(error)),
        Event::Reload { .. } => Ok(()),
        _ => Ok(()),
    }
}

fn validate_playback_chunk(
    expected: &mut ExpectedAudioStream,
    chunk: &AudioChunk,
) -> Result<(), SinkError> {
    match expected.validate_chunk(chunk) {
        Ok(()) => Ok(()),
        Err(AudioBoundaryError::SequenceMismatch {
            expected: expected_seq,
            actual,
        }) if actual > expected_seq => accept_forward_playback_gap(expected, chunk, expected_seq),
        Err(AudioBoundaryError::SampleIndexMismatch {
            expected: expected_sample_index,
            actual,
        }) if actual > expected_sample_index => {
            accept_forward_playback_gap(expected, chunk, expected_sample_index)
        }
        Err(error) => Err(SinkError::AudioBoundary(error)),
    }
}

fn accept_forward_playback_gap(
    expected: &mut ExpectedAudioStream,
    chunk: &AudioChunk,
    expected_position: u64,
) -> Result<(), SinkError> {
    chunk
        .metadata
        .validate_payload_len(chunk.payload.len())
        .map_err(SinkError::AudioBoundary)?;
    if let Some(expected_sample_index) = expected.next_sample_index {
        if chunk.metadata.sample_index < expected_sample_index {
            return Err(SinkError::AudioBoundary(
                AudioBoundaryError::SampleIndexMismatch {
                    expected: expected_sample_index,
                    actual: chunk.metadata.sample_index,
                },
            ));
        }
    }
    eprintln!(
        "cpal_sink: playback chunk gap after {expected_position}; continuing at seq={} sample_index={}",
        chunk.metadata.seq, chunk.metadata.sample_index
    );
    expected.next_seq = Some(chunk.metadata.next_seq());
    expected.next_sample_index = Some(chunk.metadata.next_sample_index());
    Ok(())
}

fn send_playback_message(
    sender: &SyncSender<PlaybackMessage>,
    message: PlaybackMessage,
) -> Result<(), SinkError> {
    match sender.send(message) {
        Ok(()) => Ok(()),
        Err(_) => Err(SinkError::Stream(
            "CPAL output callback channel disconnected".to_owned(),
        )),
    }
}

fn wait_for_playback_completion(
    config: &SinkConfig,
    node: &mut DoraNode,
    render_reference: &mut RenderReferenceEmitter,
    underrun: Arc<AtomicBool>,
    done: Arc<AtomicBool>,
    stream_error: Arc<AtomicBool>,
    render_reference_dropped: Arc<AtomicBool>,
) -> Result<(), SinkError> {
    let deadline = Instant::now() + config.completion_timeout;
    loop {
        render_reference.drain(node)?;
        if render_reference_dropped.load(Ordering::SeqCst) {
            return Err(SinkError::RenderReferenceDropped);
        }
        if underrun.load(Ordering::SeqCst) {
            return Err(SinkError::Underrun);
        }
        if stream_error.load(Ordering::SeqCst) {
            return Err(SinkError::Stream("unknown CPAL output error".to_owned()));
        }
        if done.load(Ordering::SeqCst) {
            render_reference.drain(node)?;
            render_reference.emit_final(node)?;
            return Ok(());
        }
        if Instant::now() >= deadline {
            return Err(SinkError::CompletionTimeout(config.completion_timeout));
        }
        thread::sleep(Duration::from_millis(5));
    }
}

fn is_recv_timeout(event: &Event) -> bool {
    matches!(event, Event::Error(error) if is_recv_timeout_error(error))
}

fn is_recv_timeout_error(error: &str) -> bool {
    error.contains("Receiver timed out")
}

struct RenderReferenceEmitter {
    config: Option<RenderReferenceConfig>,
    receiver: Option<Receiver<Vec<i16>>>,
    output_id: DataId,
    seq: u64,
    sample_index: u64,
    final_sent: bool,
}

impl RenderReferenceEmitter {
    fn new(
        config: Option<RenderReferenceConfig>,
        receiver: Option<Receiver<Vec<i16>>>,
        output_id: String,
    ) -> Self {
        Self {
            config,
            receiver,
            output_id: DataId::from(output_id),
            seq: 0,
            sample_index: 0,
            final_sent: false,
        }
    }

    fn drain(&mut self, node: &mut DoraNode) -> Result<(), SinkError> {
        loop {
            let Some(receiver) = &self.receiver else {
                return Ok(());
            };
            let samples = match receiver.try_recv() {
                Ok(samples) => samples,
                Err(TryRecvError::Empty) => return Ok(()),
                Err(TryRecvError::Disconnected) => return Ok(()),
            };
            self.emit_chunk(node, &samples)?;
        }
    }

    fn emit_chunk(&mut self, node: &mut DoraNode, samples: &[i16]) -> Result<(), SinkError> {
        let Some(config) = &self.config else {
            return Ok(());
        };
        let channels = usize::from(config.format.channels);
        let frame_count = (samples.len() / channels) as u64;
        if frame_count == 0 {
            return Ok(());
        }
        let capture_time_ns =
            capture_time_ns_for_frame_offset(0, self.sample_index, config.format.sample_rate_hz);
        let metadata = AudioMetadata::chunk(
            config.source_id.clone(),
            config.stream_id.clone(),
            self.seq,
            self.sample_index,
            capture_time_ns,
            frame_count,
            config.format,
        )?;
        let chunk = AudioChunk::new(metadata, i16_samples_to_s16le_bytes(samples))?;
        let encoded = chunk.to_dora_payload()?;
        node.send_output_bytes(
            self.output_id.clone(),
            chunk.metadata.to_dora_parameters()?,
            encoded.len(),
            &encoded,
        )
        .map_err(SinkError::DoraOutput)?;
        self.seq = chunk.metadata.next_seq();
        self.sample_index = chunk.metadata.next_sample_index();
        Ok(())
    }

    fn emit_final(&mut self, node: &mut DoraNode) -> Result<(), SinkError> {
        if self.final_sent {
            return Ok(());
        }
        let Some(config) = &self.config else {
            self.final_sent = true;
            return Ok(());
        };
        let capture_time_ns =
            capture_time_ns_for_frame_offset(0, self.sample_index, config.format.sample_rate_hz);
        let metadata = AudioMetadata::final_marker(
            config.source_id.clone(),
            config.stream_id.clone(),
            self.seq,
            self.sample_index,
            capture_time_ns,
            config.format,
        )?;
        let payload = metadata.to_final_dora_payload()?;
        node.send_output_bytes(
            self.output_id.clone(),
            metadata.to_dora_parameters()?,
            payload.len(),
            &payload,
        )
        .map_err(SinkError::DoraOutput)?;
        self.final_sent = true;
        Ok(())
    }
}

fn build_s16le_output_stream(
    device: &Device,
    config: StreamConfig,
    receiver: Receiver<PlaybackMessage>,
    underrun: Arc<AtomicBool>,
    done: Arc<AtomicBool>,
    stream_error: Arc<AtomicBool>,
    sender: SyncSender<PlaybackMessage>,
    empty_queue_policy: EmptyQueuePolicy,
    flush: FlushSignal,
    render_reference_sender: Option<SyncSender<Vec<i16>>>,
    render_reference_dropped: Arc<AtomicBool>,
) -> Result<cpal::Stream, SinkError> {
    let mut current = Vec::<i16>::new();
    let mut current_index = 0_usize;
    let mut final_seen = false;
    // Flush/fade state, all owned by the callback.
    let mut applied_flush_seq = flush.seq.load(Ordering::SeqCst);
    let mut fading = false;
    let mut fade_remaining = 0_usize;
    let mut fade_total = 0_usize;
    let callback_stream_error = Arc::clone(&stream_error);
    device
        .build_output_stream(
            config,
            move |data: &mut [i16], _info: &cpal::OutputCallbackInfo| {
                // Observe a barge-in flush requested since the last callback.
                let requested_seq = flush.seq.load(Ordering::SeqCst);
                if requested_seq != applied_flush_seq {
                    applied_flush_seq = requested_seq;
                    fade_total = flush.fade_samples.load(Ordering::SeqCst) as usize;
                    if fade_total == 0 {
                        // Immediate cut: drop the buffered tail, stay alive in silence.
                        current.clear();
                        current_index = 0;
                        drain_pending(&receiver, &mut final_seen);
                        fading = false;
                    } else {
                        // Fade out across real audio for fade_total samples, then drop.
                        fade_remaining = fade_total;
                        fading = true;
                    }
                }
                for sample in data.iter_mut() {
                    let raw = loop {
                        if current_index < current.len() {
                            let value = current[current_index];
                            current_index += 1;
                            break value;
                        }
                        current.clear();
                        current_index = 0;
                        if final_seen {
                            done.store(true, Ordering::SeqCst);
                            break 0;
                        }
                        match receiver.try_recv() {
                            Ok(PlaybackMessage::Chunk(samples)) => {
                                current = samples;
                            }
                            Ok(PlaybackMessage::Final) => {
                                final_seen = true;
                            }
                            Ok(PlaybackMessage::StreamError(error)) => {
                                callback_stream_error.store(true, Ordering::SeqCst);
                                eprintln!("cpal_sink callback received stream error: {error}");
                                break 0;
                            }
                            Err(TryRecvError::Empty) => {
                                // A flushed sink waiting for the next turn is idle,
                                // not underrunning, so suppress underrun while fading.
                                if empty_queue_policy == EmptyQueuePolicy::Error && !fading {
                                    underrun.store(true, Ordering::SeqCst);
                                }
                                break 0;
                            }
                            Err(TryRecvError::Disconnected) => {
                                callback_stream_error.store(true, Ordering::SeqCst);
                                break 0;
                            }
                        }
                    };
                    if fading {
                        *sample = ramped_sample(raw, fade_remaining, fade_total);
                        fade_remaining = fade_remaining.saturating_sub(1);
                        if fade_remaining == 0 {
                            // Fade complete: discard the rest of the buffered tail.
                            fading = false;
                            current.clear();
                            current_index = 0;
                            drain_pending(&receiver, &mut final_seen);
                        }
                    } else {
                        *sample = raw;
                    }
                }
                if let Some(sender) = &render_reference_sender {
                    if sender.try_send(data.to_vec()).is_err() {
                        render_reference_dropped.store(true, Ordering::SeqCst);
                    }
                }
            },
            move |err| {
                stream_error.store(true, Ordering::SeqCst);
                let _ = sender.try_send(PlaybackMessage::StreamError(err.to_string()));
            },
            None,
        )
        .map_err(SinkError::BuildStream)
}

/// Discard all queued playback chunks (the buffered tail) without blocking.
/// A drained `Final` is still honored so end-of-stream completion is not lost.
fn drain_pending(receiver: &Receiver<PlaybackMessage>, final_seen: &mut bool) {
    while let Ok(message) = receiver.try_recv() {
        if let PlaybackMessage::Final = message {
            *final_seen = true;
        }
    }
}

fn select_output_device(host: &cpal::Host, config: &SinkConfig) -> Result<Device, SinkError> {
    if config.use_default_device {
        return host
            .default_output_device()
            .ok_or(SinkError::NoDefaultDevice);
    }
    if let Some(device_id) = &config.device_id {
        let parsed = DeviceId::from_str(device_id).map_err(|source| SinkError::DeviceIdParse {
            id: device_id.clone(),
            source,
        })?;
        return host
            .device_by_id(&parsed)
            .ok_or_else(|| SinkError::DeviceIdNotFound(device_id.clone()));
    }
    let requested = config
        .device_name
        .as_ref()
        .ok_or(SinkError::DeviceSelection)?;
    let mut matches = Vec::new();
    for device in host
        .output_devices()
        .map_err(SinkError::DeviceEnumeration)?
    {
        if device_name(&device) == *requested {
            matches.push(device);
        }
    }
    match matches.len() {
        0 => Err(SinkError::DeviceNotFound(requested.clone())),
        1 => Ok(matches.remove(0)),
        _ => Err(SinkError::AmbiguousDevice(requested.clone())),
    }
}

fn device_name(device: &Device) -> String {
    device.to_string()
}

#[cfg(test)]
mod tests {
    use super::*;
    use fluent_dialogue_dora_io_boundary::AudioMetadata;

    #[test]
    fn rejects_missing_explicit_device_selection() {
        let args = Args {
            device_name: None,
            device_id: None,
            default_output_device: false,
            sample_rate_hz: 16_000,
            channels: 1,
            sample_format: "s16le".to_owned(),
            channel_layout: "interleaved".to_owned(),
            buffer_size_frames: 160,
            queue_capacity_chunks: 2,
            startup_buffer_chunks: 1,
            empty_queue_policy: EmptyQueuePolicy::Error,
            source_id: "capture".to_owned(),
            stream_id: "audio/capture".to_owned(),
            completion_timeout_ms: 1_000,
            render_reference_source_id: None,
            render_reference_stream_id: None,
        };
        assert!(matches!(
            SinkConfig::try_from(args),
            Err(SinkError::DeviceSelection)
        ));
    }

    #[test]
    fn accepts_default_device_opt_in() {
        let args = Args {
            device_name: None,
            device_id: None,
            default_output_device: true,
            sample_rate_hz: 16_000,
            channels: 1,
            sample_format: "s16le".to_owned(),
            channel_layout: "interleaved".to_owned(),
            buffer_size_frames: 160,
            queue_capacity_chunks: 2,
            startup_buffer_chunks: 1,
            empty_queue_policy: EmptyQueuePolicy::Error,
            source_id: "capture".to_owned(),
            stream_id: "audio/capture".to_owned(),
            completion_timeout_ms: 1_000,
            render_reference_source_id: None,
            render_reference_stream_id: None,
        };
        let config = SinkConfig::try_from(args).expect("config should validate");
        assert!(config.use_default_device);
        assert_eq!(config.format.sample_rate_hz, 16_000);
        assert_eq!(config.empty_queue_policy, EmptyQueuePolicy::Error);
    }

    #[test]
    fn rejects_startup_buffer_larger_than_queue_capacity() {
        let args = Args {
            device_name: None,
            device_id: None,
            default_output_device: true,
            sample_rate_hz: 16_000,
            channels: 1,
            sample_format: "s16le".to_owned(),
            channel_layout: "interleaved".to_owned(),
            buffer_size_frames: 160,
            queue_capacity_chunks: 2,
            startup_buffer_chunks: 3,
            empty_queue_policy: EmptyQueuePolicy::Silence,
            source_id: "capture".to_owned(),
            stream_id: "audio/capture".to_owned(),
            completion_timeout_ms: 1_000,
            render_reference_source_id: None,
            render_reference_stream_id: None,
        };
        assert!(matches!(
            SinkConfig::try_from(args),
            Err(SinkError::StartupBufferExceedsQueue {
                startup_buffer_chunks: 3,
                queue_capacity_chunks: 2,
            })
        ));
    }

    #[test]
    fn fade_length_samples_covers_requested_milliseconds() {
        // 15 ms at 48 kHz stereo = 720 frames * 2 channels.
        assert_eq!(fade_length_samples(15, 48_000, 2), 1_440);
        // 10 ms at 16 kHz mono = 160 frames.
        assert_eq!(fade_length_samples(10, 16_000, 1), 160);
        // Zero fade means an immediate cut.
        assert_eq!(fade_length_samples(0, 48_000, 2), 0);
    }

    #[test]
    fn ramped_sample_fades_linearly_to_zero() {
        let total = 1_000;
        // Full amplitude at the start of the fade.
        assert_eq!(ramped_sample(1_000, total, total), 1_000);
        // Halfway through, roughly half amplitude.
        assert_eq!(ramped_sample(1_000, total / 2, total), 500);
        // Silence at the end of the fade.
        assert_eq!(ramped_sample(1_000, 0, total), 0);
        // total == 0 passes the sample through unchanged (no fade).
        assert_eq!(ramped_sample(-1_234, 0, 0), -1_234);
    }

    fn test_format() -> AudioFormat {
        AudioFormat::new(48_000, 2, SampleFormat::S16Le, ChannelLayout::Interleaved)
            .expect("test format should validate")
    }

    fn playback_chunk(seq: u64, sample_index: u64, frame_count: u64) -> AudioChunk {
        let format = test_format();
        let metadata = AudioMetadata::chunk(
            "media_graph_speaker".to_owned(),
            "speaker/playback".to_owned(),
            seq,
            sample_index,
            0,
            frame_count,
            format,
        )
        .expect("test metadata should validate");
        let payload_len = usize::try_from(frame_count).expect("frame_count should fit")
            * format.frame_size_bytes();
        AudioChunk::new(metadata, vec![0; payload_len]).expect("test chunk should validate")
    }

    #[test]
    fn playback_validation_accepts_forward_gap() {
        let mut expected = ExpectedAudioStream::new(
            "media_graph_speaker".to_owned(),
            "speaker/playback".to_owned(),
            test_format(),
        );
        validate_playback_chunk(&mut expected, &playback_chunk(0, 0, 160))
            .expect("first chunk should validate");
        validate_playback_chunk(&mut expected, &playback_chunk(3, 480, 160))
            .expect("forward playback gap should not kill the speaker sink");
        assert_eq!(expected.next_seq, Some(4));
        assert_eq!(expected.next_sample_index, Some(640));
    }

    #[test]
    fn playback_validation_rejects_duplicate_chunk() {
        let mut expected = ExpectedAudioStream::new(
            "media_graph_speaker".to_owned(),
            "speaker/playback".to_owned(),
            test_format(),
        );
        validate_playback_chunk(&mut expected, &playback_chunk(0, 0, 160))
            .expect("first chunk should validate");
        assert!(matches!(
            validate_playback_chunk(&mut expected, &playback_chunk(0, 0, 160)),
            Err(SinkError::AudioBoundary(
                AudioBoundaryError::SequenceMismatch {
                    expected: 1,
                    actual: 0
                }
            ))
        ));
    }

    #[test]
    fn playback_validation_rejects_rewound_sample_index() {
        let mut expected = ExpectedAudioStream::new(
            "media_graph_speaker".to_owned(),
            "speaker/playback".to_owned(),
            test_format(),
        );
        validate_playback_chunk(&mut expected, &playback_chunk(0, 0, 160))
            .expect("first chunk should validate");
        assert!(matches!(
            validate_playback_chunk(&mut expected, &playback_chunk(3, 80, 160)),
            Err(SinkError::AudioBoundary(
                AudioBoundaryError::SampleIndexMismatch {
                    expected: 160,
                    actual: 80
                }
            ))
        ));
    }

    fn flush_control_with(last_seq: Option<u64>) -> FlushControl {
        FlushControl {
            signal: FlushSignal::new(),
            stream_id: "speaker/cpal".to_owned(),
            sample_rate_hz: 48_000,
            channels: 2,
            last_seq,
        }
    }

    fn flush_command(stream_id: &str, seq: u64) -> PlaybackControlCommand {
        PlaybackControlCommand {
            kind: PlaybackControlKind::Flush as i32,
            stream_id: stream_id.to_owned(),
            seq,
            fade_out_ms: 15,
        }
    }

    #[test]
    fn validate_command_accepts_increasing_seq() {
        let control = flush_control_with(Some(5));
        assert!(control
            .validate_command(&flush_command("speaker/cpal", 6))
            .is_ok());
    }

    #[test]
    fn validate_command_rejects_regressed_seq() {
        let control = flush_control_with(Some(5));
        assert!(matches!(
            control.validate_command(&flush_command("speaker/cpal", 5)),
            Err(SinkError::ControlSeqRegressed {
                previous: 5,
                got: 5
            })
        ));
    }

    #[test]
    fn validate_command_rejects_stream_mismatch() {
        let control = flush_control_with(None);
        assert!(matches!(
            control.validate_command(&flush_command("speaker/other", 0)),
            Err(SinkError::ControlStreamMismatch { .. })
        ));
    }

    #[test]
    fn validate_command_rejects_unsupported_kind() {
        let control = flush_control_with(None);
        let command = PlaybackControlCommand {
            kind: PlaybackControlKind::Unspecified as i32,
            stream_id: "speaker/cpal".to_owned(),
            seq: 0,
            fade_out_ms: 15,
        };
        assert!(matches!(
            control.validate_command(&command),
            Err(SinkError::ControlKind(0))
        ));
    }

    #[test]
    fn accepts_explicit_device_id_selection() {
        let args = Args {
            device_name: None,
            device_id: Some("alsa:hw:CARD=APE,DEV=0".to_owned()),
            default_output_device: false,
            sample_rate_hz: 48_000,
            channels: 2,
            sample_format: "s16le".to_owned(),
            channel_layout: "interleaved".to_owned(),
            buffer_size_frames: 480,
            queue_capacity_chunks: 4,
            startup_buffer_chunks: 1,
            empty_queue_policy: EmptyQueuePolicy::Silence,
            source_id: "capture".to_owned(),
            stream_id: "audio/capture".to_owned(),
            completion_timeout_ms: 1_000,
            render_reference_source_id: None,
            render_reference_stream_id: None,
        };
        let config = SinkConfig::try_from(args).expect("config should validate");
        assert_eq!(config.device_id.as_deref(), Some("alsa:hw:CARD=APE,DEV=0"));
        assert_eq!(config.empty_queue_policy, EmptyQueuePolicy::Silence);
    }

    #[test]
    fn rejects_partial_render_reference_selection() {
        let args = Args {
            device_name: None,
            device_id: Some("alsa:hw:CARD=APE,DEV=0".to_owned()),
            default_output_device: false,
            sample_rate_hz: 48_000,
            channels: 2,
            sample_format: "s16le".to_owned(),
            channel_layout: "interleaved".to_owned(),
            buffer_size_frames: 480,
            queue_capacity_chunks: 4,
            startup_buffer_chunks: 1,
            empty_queue_policy: EmptyQueuePolicy::Silence,
            source_id: "capture".to_owned(),
            stream_id: "audio/capture".to_owned(),
            completion_timeout_ms: 1_000,
            render_reference_source_id: Some("cpal_sink".to_owned()),
            render_reference_stream_id: None,
        };
        assert!(matches!(
            SinkConfig::try_from(args),
            Err(SinkError::RenderReferenceSelection)
        ));
    }

    #[test]
    fn dora_timeout_event_is_not_a_sink_error() {
        assert!(is_recv_timeout(&Event::Error(
            "Timeout event stream error: Receiver timed out".to_owned()
        )));
        assert!(is_recv_timeout_error(
            "Timeout event stream error: Receiver timed out"
        ));
        assert!(!is_recv_timeout(&Event::Error(
            "actual DORA failure".to_owned()
        )));
    }
}
