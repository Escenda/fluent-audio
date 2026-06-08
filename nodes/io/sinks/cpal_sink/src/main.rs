use std::str::FromStr;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::mpsc::{sync_channel, Receiver, SyncSender, TryRecvError, TrySendError};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

use clap::Parser;
use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use cpal::{BufferSize, Device, DeviceId, StreamConfig};
use dora_node_api::dora_core::config::DataId;
use dora_node_api::{into_vec, DoraNode, Event};
use fluent_audio_io_boundary::{
    s16le_bytes_to_i16_samples, AudioChunk, AudioFormat, AudioMetadata, ChannelLayout,
    ExpectedAudioStream, SampleFormat, AUDIO_INPUT_ID,
};
use thiserror::Error;

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
    #[error("playback queue overflowed; no configured drop policy exists")]
    QueueOverflow,
    #[error("playback underrun occurred; no configured fill policy exists")]
    Underrun,
    #[error("playback did not finish within {0:?}")]
    CompletionTimeout(Duration),
    #[error("unexpected DORA input id {0:?}")]
    UnexpectedInput(String),
    #[error("upstream node failed: {0}")]
    UpstreamFailed(String),
    #[error("DORA node initialization failed: {0}")]
    DoraInit(#[source] eyre::Report),
    #[error("audio boundary error: {0}")]
    AudioBoundary(#[from] fluent_audio_io_boundary::AudioBoundaryError),
    #[error("DORA audio payload could not decode as u8 array: {0}")]
    DoraPayload(#[source] eyre::Report),
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
    #[arg(long)]
    source_id: String,
    #[arg(long)]
    stream_id: String,
    #[arg(long)]
    completion_timeout_ms: u64,
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
    source_id: String,
    stream_id: String,
    completion_timeout: Duration,
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
                fluent_audio_io_boundary::AudioBoundaryError::NonPositive {
                    field: "buffer_size_frames",
                    value: u64::from(args.buffer_size_frames),
                },
            ));
        }
        if args.queue_capacity_chunks == 0 {
            return Err(SinkError::AudioBoundary(
                fluent_audio_io_boundary::AudioBoundaryError::NonPositive {
                    field: "queue_capacity_chunks",
                    value: args.queue_capacity_chunks as u64,
                },
            ));
        }
        if args.startup_buffer_chunks == 0 {
            return Err(SinkError::AudioBoundary(
                fluent_audio_io_boundary::AudioBoundaryError::NonPositive {
                    field: "startup_buffer_chunks",
                    value: args.startup_buffer_chunks as u64,
                },
            ));
        }
        if args.completion_timeout_ms == 0 {
            return Err(SinkError::AudioBoundary(
                fluent_audio_io_boundary::AudioBoundaryError::NonPositive {
                    field: "completion_timeout_ms",
                    value: args.completion_timeout_ms,
                },
            ));
        }
        Ok(Self {
            device_name: args.device_name,
            device_id: args.device_id,
            use_default_device: args.default_output_device,
            format,
            buffer_size_frames: args.buffer_size_frames,
            queue_capacity_chunks: args.queue_capacity_chunks,
            startup_buffer_chunks: args.startup_buffer_chunks,
            source_id: args.source_id,
            stream_id: args.stream_id,
            completion_timeout: Duration::from_millis(args.completion_timeout_ms),
        })
    }
}

#[derive(Debug)]
enum PlaybackMessage {
    Chunk(Vec<i16>),
    Final,
    StreamError(String),
}

fn main() -> Result<(), SinkError> {
    let config = SinkConfig::try_from(Args::parse())?;
    run(config)
}

fn run(config: SinkConfig) -> Result<(), SinkError> {
    let (_node, mut events) = DoraNode::init_from_env().map_err(SinkError::DoraInit)?;
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
    let stream = build_s16le_output_stream(
        &device,
        stream_config,
        receiver,
        Arc::clone(&underrun),
        Arc::clone(&done),
        Arc::clone(&stream_error),
        sender.clone(),
    )?;

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
        )?;
        if chunks_queued >= config.startup_buffer_chunks || final_received {
            break;
        }
    }

    stream.play().map_err(SinkError::PlayStream)?;

    if !final_received {
        while let Some(event) = events.recv() {
            handle_dora_event(
                event,
                &sender,
                &mut expected,
                &mut chunks_queued,
                &mut final_received,
            )?;
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

    wait_for_playback_completion(&config, underrun, done, stream_error)
}

fn handle_dora_event(
    event: Event,
    sender: &SyncSender<PlaybackMessage>,
    expected: &mut ExpectedAudioStream,
    chunks_queued: &mut usize,
    final_received: &mut bool,
) -> Result<(), SinkError> {
    match event {
        Event::Input { id, metadata, data } => {
            if id != DataId::from(AUDIO_INPUT_ID.to_owned()) {
                return Err(SinkError::UnexpectedInput(id.to_string()));
            }
            let audio_metadata = AudioMetadata::from_dora_metadata(&metadata)?;
            let payload = into_vec::<u8>(&data).map_err(SinkError::DoraPayload)?;
            if audio_metadata.final_marker {
                expected.validate_final_marker(&audio_metadata, payload.len())?;
                send_playback_message(sender, PlaybackMessage::Final)?;
                *final_received = true;
                return Ok(());
            }

            let chunk = AudioChunk::new(audio_metadata, payload)?;
            expected.validate_chunk(&chunk)?;
            let samples = s16le_bytes_to_i16_samples(&chunk.payload)?;
            send_playback_message(sender, PlaybackMessage::Chunk(samples))?;
            *chunks_queued += 1;
            Ok(())
        }
        Event::InputClosed { id } => {
            if id != DataId::from(AUDIO_INPUT_ID.to_owned()) {
                return Err(SinkError::UnexpectedInput(id.to_string()));
            }
            send_playback_message(sender, PlaybackMessage::Final)?;
            *final_received = true;
            Ok(())
        }
        Event::NodeFailed { error, .. } => Err(SinkError::UpstreamFailed(error)),
        Event::Stop(_) => {
            send_playback_message(sender, PlaybackMessage::Final)?;
            *final_received = true;
            Ok(())
        }
        Event::Error(error) => Err(SinkError::Stream(error)),
        Event::Reload { .. } => Ok(()),
        _ => Ok(()),
    }
}

fn send_playback_message(
    sender: &SyncSender<PlaybackMessage>,
    message: PlaybackMessage,
) -> Result<(), SinkError> {
    match sender.try_send(message) {
        Ok(()) => Ok(()),
        Err(TrySendError::Full(_)) => Err(SinkError::QueueOverflow),
        Err(TrySendError::Disconnected(_)) => Err(SinkError::Stream(
            "CPAL output callback channel disconnected".to_owned(),
        )),
    }
}

fn wait_for_playback_completion(
    config: &SinkConfig,
    underrun: Arc<AtomicBool>,
    done: Arc<AtomicBool>,
    stream_error: Arc<AtomicBool>,
) -> Result<(), SinkError> {
    let deadline = Instant::now() + config.completion_timeout;
    loop {
        if underrun.load(Ordering::SeqCst) {
            return Err(SinkError::Underrun);
        }
        if stream_error.load(Ordering::SeqCst) {
            return Err(SinkError::Stream("unknown CPAL output error".to_owned()));
        }
        if done.load(Ordering::SeqCst) {
            return Ok(());
        }
        if Instant::now() >= deadline {
            return Err(SinkError::CompletionTimeout(config.completion_timeout));
        }
        thread::sleep(Duration::from_millis(5));
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
) -> Result<cpal::Stream, SinkError> {
    let mut current = Vec::<i16>::new();
    let mut current_index = 0_usize;
    let mut final_seen = false;
    let callback_stream_error = Arc::clone(&stream_error);
    device
        .build_output_stream(
            config,
            move |data: &mut [i16], _info: &cpal::OutputCallbackInfo| {
                for sample in data.iter_mut() {
                    loop {
                        if current_index < current.len() {
                            *sample = current[current_index];
                            current_index += 1;
                            break;
                        }
                        current.clear();
                        current_index = 0;
                        if final_seen {
                            done.store(true, Ordering::SeqCst);
                            *sample = 0;
                            break;
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
                                *sample = 0;
                                break;
                            }
                            Err(TryRecvError::Empty) => {
                                underrun.store(true, Ordering::SeqCst);
                                *sample = 0;
                                break;
                            }
                            Err(TryRecvError::Disconnected) => {
                                callback_stream_error.store(true, Ordering::SeqCst);
                                *sample = 0;
                                break;
                            }
                        }
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
            source_id: "capture".to_owned(),
            stream_id: "audio/capture".to_owned(),
            completion_timeout_ms: 1_000,
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
            source_id: "capture".to_owned(),
            stream_id: "audio/capture".to_owned(),
            completion_timeout_ms: 1_000,
        };
        let config = SinkConfig::try_from(args).expect("config should validate");
        assert!(config.use_default_device);
        assert_eq!(config.format.sample_rate_hz, 16_000);
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
            source_id: "capture".to_owned(),
            stream_id: "audio/capture".to_owned(),
            completion_timeout_ms: 1_000,
        };
        let config = SinkConfig::try_from(args).expect("config should validate");
        assert_eq!(config.device_id.as_deref(), Some("alsa:hw:CARD=APE,DEV=0"));
    }
}
