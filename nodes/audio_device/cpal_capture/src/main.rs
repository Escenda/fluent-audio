use std::str::FromStr;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::mpsc::{sync_channel, RecvTimeoutError, SyncSender, TrySendError};
use std::sync::Arc;
use std::time::Duration;

use clap::Parser;
use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use cpal::{BufferSize, Device, DeviceId, StreamConfig};
use dora_node_api::dora_core::config::DataId;
use dora_node_api::DoraNode;
use fluent_dialogue_dora_io_boundary::{
    capture_time_ns_for_frame_offset, f32_samples_to_f32le_bytes, i16_samples_to_s16le_bytes,
    AudioChunk, AudioFormat, AudioMetadata, ChannelLayout, SampleFormat, AUDIO_OUTPUT_ID,
};
use thiserror::Error;

#[derive(Debug, Error)]
enum CaptureError {
    #[error("choose exactly one of --device-name, --device-id, or --default-input-device")]
    DeviceSelection,
    #[error("failed to parse CPAL device id {id:?}: {source}")]
    DeviceIdParse {
        id: String,
        #[source]
        source: cpal::Error,
    },
    #[error("CPAL input device id {0:?} was not found")]
    DeviceIdNotFound(String),
    #[error("no default CPAL input device is available")]
    NoDefaultDevice,
    #[error("CPAL input device {0:?} was not found")]
    DeviceNotFound(String),
    #[error("multiple CPAL input devices matched {0:?}; use an exact device name")]
    AmbiguousDevice(String),
    #[error("failed to enumerate CPAL input devices: {0}")]
    DeviceEnumeration(#[source] cpal::Error),
    #[error("failed to build CPAL input stream: {0}")]
    BuildStream(#[source] cpal::Error),
    #[error("failed to start CPAL input stream: {0}")]
    PlayStream(#[source] cpal::Error),
    #[error("CPAL input stream error: {0}")]
    Stream(String),
    #[error("capture callback queue overflowed; no configured drop policy exists")]
    QueueOverflow,
    #[error("capture timed out before producing a chunk after {0:?}")]
    CaptureTimeout(Duration),
    #[error("DORA node initialization failed: {0}")]
    DoraInit(#[source] eyre::Report),
    #[error("DORA output failed: {0}")]
    DoraOutput(#[source] eyre::Report),
    #[error("audio boundary error: {0}")]
    AudioBoundary(#[from] fluent_dialogue_dora_io_boundary::AudioBoundaryError),
}

#[derive(Parser, Debug)]
#[command(about = "Capture explicit s16le CPAL input chunks and emit DORA audio output.")]
struct Args {
    #[arg(long)]
    device_name: Option<String>,
    #[arg(long)]
    device_id: Option<String>,
    #[arg(long, default_value_t = false)]
    default_input_device: bool,
    #[arg(long)]
    sample_rate_hz: u32,
    #[arg(long)]
    channels: u16,
    #[arg(long, value_parser = ["s16le", "f32le"])]
    sample_format: String,
    #[arg(long, value_parser = ["interleaved"])]
    channel_layout: String,
    #[arg(long)]
    chunk_frames: u32,
    #[arg(long)]
    buffer_size_frames: u32,
    #[arg(long)]
    queue_capacity_chunks: usize,
    #[arg(long)]
    source_id: String,
    #[arg(long)]
    stream_id: String,
    #[arg(long, default_value_t = 0)]
    start_seq: u64,
    #[arg(long, default_value_t = 0)]
    start_sample_index: u64,
    #[arg(long)]
    start_capture_time_ns: u64,
    #[arg(long)]
    max_chunks: Option<u64>,
    #[arg(long)]
    capture_timeout_ms: u64,
}

#[derive(Clone, Debug)]
struct CaptureConfig {
    device_name: Option<String>,
    device_id: Option<String>,
    use_default_device: bool,
    format: AudioFormat,
    chunk_frames: u32,
    buffer_size_frames: u32,
    queue_capacity_chunks: usize,
    source_id: String,
    stream_id: String,
    start_seq: u64,
    start_sample_index: u64,
    start_capture_time_ns: u64,
    max_chunks: Option<u64>,
    capture_timeout: Duration,
}

impl TryFrom<Args> for CaptureConfig {
    type Error = CaptureError;

    fn try_from(args: Args) -> Result<Self, Self::Error> {
        let selectors = args.device_name.is_some() as u8
            + args.device_id.is_some() as u8
            + args.default_input_device as u8;
        if selectors != 1 {
            return Err(CaptureError::DeviceSelection);
        }
        let format = AudioFormat::new(
            args.sample_rate_hz,
            args.channels,
            args.sample_format.parse::<SampleFormat>()?,
            args.channel_layout.parse::<ChannelLayout>()?,
        )?;
        if args.chunk_frames == 0 {
            return Err(CaptureError::AudioBoundary(
                fluent_dialogue_dora_io_boundary::AudioBoundaryError::NonPositive {
                    field: "chunk_frames",
                    value: u64::from(args.chunk_frames),
                },
            ));
        }
        if args.buffer_size_frames == 0 {
            return Err(CaptureError::AudioBoundary(
                fluent_dialogue_dora_io_boundary::AudioBoundaryError::NonPositive {
                    field: "buffer_size_frames",
                    value: u64::from(args.buffer_size_frames),
                },
            ));
        }
        if args.queue_capacity_chunks == 0 {
            return Err(CaptureError::AudioBoundary(
                fluent_dialogue_dora_io_boundary::AudioBoundaryError::NonPositive {
                    field: "queue_capacity_chunks",
                    value: args.queue_capacity_chunks as u64,
                },
            ));
        }
        if args.capture_timeout_ms == 0 {
            return Err(CaptureError::AudioBoundary(
                fluent_dialogue_dora_io_boundary::AudioBoundaryError::NonPositive {
                    field: "capture_timeout_ms",
                    value: args.capture_timeout_ms,
                },
            ));
        }
        Ok(Self {
            device_name: args.device_name,
            device_id: args.device_id,
            use_default_device: args.default_input_device,
            format,
            chunk_frames: args.chunk_frames,
            buffer_size_frames: args.buffer_size_frames,
            queue_capacity_chunks: args.queue_capacity_chunks,
            source_id: args.source_id,
            stream_id: args.stream_id,
            start_seq: args.start_seq,
            start_sample_index: args.start_sample_index,
            start_capture_time_ns: args.start_capture_time_ns,
            max_chunks: args.max_chunks,
            capture_timeout: Duration::from_millis(args.capture_timeout_ms),
        })
    }
}

#[derive(Debug)]
enum CaptureMessage {
    Chunk(Vec<u8>),
    StreamError(String),
}

fn main() -> Result<(), CaptureError> {
    let config = CaptureConfig::try_from(Args::parse())?;
    run(config)
}

fn run(config: CaptureConfig) -> Result<(), CaptureError> {
    let (mut node, _events) = DoraNode::init_from_env().map_err(CaptureError::DoraInit)?;
    let host = cpal::default_host();
    let device = select_input_device(&host, &config)?;
    eprintln!("cpal_capture: input_device={}", device_name(&device));

    let stream_config = StreamConfig {
        channels: config.format.channels,
        sample_rate: config.format.sample_rate_hz,
        buffer_size: BufferSize::Fixed(config.buffer_size_frames),
    };
    let (sender, receiver) = sync_channel(config.queue_capacity_chunks);
    let overflowed = Arc::new(AtomicBool::new(false));
    let stream_error = Arc::new(AtomicBool::new(false));
    let chunk_size_bytes = config.format.frame_size_bytes() * config.chunk_frames as usize;
    // The capture layer only reads the device into the wire-faithful contract format.
    // For s16le it streams i16; for f32le it streams f32 (lossless from 24-bit sources
    // opened through ALSA plug). Rate/channel/bit-depth conversion is the media graph's job.
    let stream = match config.format.sample_format {
        SampleFormat::S16Le => build_input_stream_typed::<i16>(
            &device,
            stream_config,
            chunk_size_bytes,
            i16_samples_to_s16le_bytes,
            sender,
            Arc::clone(&overflowed),
            Arc::clone(&stream_error),
        ),
        SampleFormat::F32Le => build_input_stream_typed::<f32>(
            &device,
            stream_config,
            chunk_size_bytes,
            f32_samples_to_f32le_bytes,
            sender,
            Arc::clone(&overflowed),
            Arc::clone(&stream_error),
        ),
    }?;
    stream.play().map_err(CaptureError::PlayStream)?;

    let output_id = DataId::from(AUDIO_OUTPUT_ID.to_owned());
    let mut seq = config.start_seq;
    let mut sample_index = config.start_sample_index;
    let mut chunks_sent = 0_u64;

    loop {
        if overflowed.load(Ordering::SeqCst) {
            return Err(CaptureError::QueueOverflow);
        }
        if stream_error.load(Ordering::SeqCst) {
            match receiver.recv_timeout(config.capture_timeout) {
                Ok(CaptureMessage::StreamError(error)) => return Err(CaptureError::Stream(error)),
                Ok(CaptureMessage::Chunk(_)) => {}
                Err(_) => return Err(CaptureError::Stream("unknown CPAL input error".to_owned())),
            }
        }
        if let Some(max_chunks) = config.max_chunks {
            if chunks_sent >= max_chunks {
                break;
            }
        }

        let payload = match receiver.recv_timeout(config.capture_timeout) {
            Ok(CaptureMessage::Chunk(payload)) => payload,
            Ok(CaptureMessage::StreamError(error)) => return Err(CaptureError::Stream(error)),
            Err(RecvTimeoutError::Timeout) => {
                return Err(CaptureError::CaptureTimeout(config.capture_timeout));
            }
            Err(RecvTimeoutError::Disconnected) => {
                return Err(CaptureError::Stream(
                    "CPAL input callback channel disconnected".to_owned(),
                ));
            }
        };
        let frame_count = (payload.len() / config.format.frame_size_bytes()) as u64;
        let capture_time_ns = capture_time_ns_for_frame_offset(
            config.start_capture_time_ns,
            sample_index - config.start_sample_index,
            config.format.sample_rate_hz,
        );
        let metadata = AudioMetadata::chunk(
            config.source_id.clone(),
            config.stream_id.clone(),
            seq,
            sample_index,
            capture_time_ns,
            frame_count,
            config.format,
        )?;
        let chunk = AudioChunk::new(metadata, payload)?;
        let encoded_payload = chunk.to_dora_payload()?;
        let parameters = chunk.metadata.to_dora_parameters()?;
        node.send_output_bytes(
            output_id.clone(),
            parameters,
            encoded_payload.len(),
            &encoded_payload,
        )
            .map_err(CaptureError::DoraOutput)?;
        seq = chunk.metadata.next_seq();
        sample_index = chunk.metadata.next_sample_index();
        chunks_sent += 1;
    }

    let final_capture_time_ns = capture_time_ns_for_frame_offset(
        config.start_capture_time_ns,
        sample_index - config.start_sample_index,
        config.format.sample_rate_hz,
    );
    let final_metadata = AudioMetadata::final_marker(
        config.source_id,
        config.stream_id,
        seq,
        sample_index,
        final_capture_time_ns,
        config.format,
    )?;
    let final_payload = final_metadata.to_final_dora_payload()?;
    node.send_output_bytes(
        output_id,
        final_metadata.to_dora_parameters()?,
        final_payload.len(),
        &final_payload,
    )
        .map_err(CaptureError::DoraOutput)?;
    Ok(())
}

fn build_input_stream_typed<T: cpal::SizedSample + 'static>(
    device: &Device,
    config: StreamConfig,
    chunk_size_bytes: usize,
    convert: fn(&[T]) -> Vec<u8>,
    sender: SyncSender<CaptureMessage>,
    overflowed: Arc<AtomicBool>,
    stream_error: Arc<AtomicBool>,
) -> Result<cpal::Stream, CaptureError> {
    let error_sender = sender.clone();
    let mut pending = Vec::<u8>::with_capacity(chunk_size_bytes);
    device
        .build_input_stream(
            config,
            move |data: &[T], _info: &cpal::InputCallbackInfo| {
                if overflowed.load(Ordering::Relaxed) {
                    return;
                }
                pending.extend_from_slice(&convert(data));
                while pending.len() >= chunk_size_bytes {
                    let chunk = pending.drain(..chunk_size_bytes).collect::<Vec<u8>>();
                    match sender.try_send(CaptureMessage::Chunk(chunk)) {
                        Ok(()) => {}
                        Err(TrySendError::Full(_)) => {
                            overflowed.store(true, Ordering::SeqCst);
                            return;
                        }
                        Err(TrySendError::Disconnected(_)) => return,
                    }
                }
            },
            move |err| {
                stream_error.store(true, Ordering::SeqCst);
                let _ = error_sender.try_send(CaptureMessage::StreamError(err.to_string()));
            },
            None,
        )
        .map_err(CaptureError::BuildStream)
}

fn select_input_device(host: &cpal::Host, config: &CaptureConfig) -> Result<Device, CaptureError> {
    if config.use_default_device {
        return host
            .default_input_device()
            .ok_or(CaptureError::NoDefaultDevice);
    }
    if let Some(device_id) = &config.device_id {
        let parsed =
            DeviceId::from_str(device_id).map_err(|source| CaptureError::DeviceIdParse {
                id: device_id.clone(),
                source,
            })?;
        return host
            .device_by_id(&parsed)
            .ok_or_else(|| CaptureError::DeviceIdNotFound(device_id.clone()));
    }
    let requested = config
        .device_name
        .as_ref()
        .ok_or(CaptureError::DeviceSelection)?;
    let mut matches = Vec::new();
    for device in host
        .input_devices()
        .map_err(CaptureError::DeviceEnumeration)?
    {
        if device_name(&device) == *requested {
            matches.push(device);
        }
    }
    match matches.len() {
        0 => Err(CaptureError::DeviceNotFound(requested.clone())),
        1 => Ok(matches.remove(0)),
        _ => Err(CaptureError::AmbiguousDevice(requested.clone())),
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
            default_input_device: false,
            sample_rate_hz: 16_000,
            channels: 1,
            sample_format: "s16le".to_owned(),
            channel_layout: "interleaved".to_owned(),
            chunk_frames: 160,
            buffer_size_frames: 160,
            queue_capacity_chunks: 2,
            source_id: "capture".to_owned(),
            stream_id: "audio/capture".to_owned(),
            start_seq: 0,
            start_sample_index: 0,
            start_capture_time_ns: 0,
            max_chunks: Some(1),
            capture_timeout_ms: 1_000,
        };
        assert!(matches!(
            CaptureConfig::try_from(args),
            Err(CaptureError::DeviceSelection)
        ));
    }

    #[test]
    fn accepts_default_device_opt_in() {
        let args = Args {
            device_name: None,
            device_id: None,
            default_input_device: true,
            sample_rate_hz: 16_000,
            channels: 1,
            sample_format: "s16le".to_owned(),
            channel_layout: "interleaved".to_owned(),
            chunk_frames: 160,
            buffer_size_frames: 160,
            queue_capacity_chunks: 2,
            source_id: "capture".to_owned(),
            stream_id: "audio/capture".to_owned(),
            start_seq: 0,
            start_sample_index: 0,
            start_capture_time_ns: 0,
            max_chunks: Some(1),
            capture_timeout_ms: 1_000,
        };
        let config = CaptureConfig::try_from(args).expect("config should validate");
        assert!(config.use_default_device);
        assert_eq!(config.format.sample_rate_hz, 16_000);
    }

    #[test]
    fn accepts_explicit_device_id_selection() {
        let args = Args {
            device_name: None,
            device_id: Some("alsa:hw:CARD=APE,DEV=0".to_owned()),
            default_input_device: false,
            sample_rate_hz: 48_000,
            channels: 2,
            sample_format: "s16le".to_owned(),
            channel_layout: "interleaved".to_owned(),
            chunk_frames: 480,
            buffer_size_frames: 480,
            queue_capacity_chunks: 4,
            source_id: "capture".to_owned(),
            stream_id: "audio/capture".to_owned(),
            start_seq: 0,
            start_sample_index: 0,
            start_capture_time_ns: 0,
            max_chunks: Some(25),
            capture_timeout_ms: 1_000,
        };
        let config = CaptureConfig::try_from(args).expect("config should validate");
        assert_eq!(config.device_id.as_deref(), Some("alsa:hw:CARD=APE,DEV=0"));
    }
}
