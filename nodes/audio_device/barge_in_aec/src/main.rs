//! Acoustic echo cancellation node for barge-in.
//!
//! Removes the agent's own TTS (played out the speaker) from the microphone
//! signal so the VAD/ASR — and therefore the barge-in detector — react to the
//! user, not to the agent's echo. Echo cancellation is delegated to a selected
//! AEC backend.
//!
//! Two DORA audio inputs:
//!   - `near`: microphone, 16 kHz mono s16le (from media_graph_asr).
//!   - `far` : playback reference, integer-multiple sample rate, s16le/f32le,
//!             downmixed/resampled to 16 kHz mono inside this node.
//! One DORA audio output `audio`: echo-cancelled near, 16 kHz mono s16le.

use std::collections::VecDeque;

use clap::{Parser, ValueEnum};
use dora_node_api::dora_core::config::DataId;
use dora_node_api::{into_vec, DoraNode, Event};
use fluent_dialogue_dora_io_boundary::{
    capture_time_ns_for_frame_offset, i16_samples_to_s16le_bytes, AudioChunk, AudioFormat,
    AudioMetadata, ChannelLayout, DoraAudioMessage, SampleFormat,
};
use sonora::config::EchoCanceller as SonoraEchoCanceller;
use sonora::{
    AudioProcessing as SonoraAudioProcessing, Config as SonoraConfig,
    StreamConfig as SonoraStreamConfig,
};
use thiserror::Error;
use webrtc_audio_processing::Processor;
use webrtc_audio_processing_config::{
    Config as WebRtcConfig, EchoCanceller as WebRtcEchoCanceller,
};

const NEAR_INPUT_ID: &str = "near";
const FAR_INPUT_ID: &str = "far";
const AUDIO_OUTPUT_ID: &str = "audio";
const AEC_SAMPLE_RATE_HZ: u32 = 16_000;
// sonora/WebRTC APM operates on 10 ms frames: 160 samples at 16 kHz mono.
const FRAME_SAMPLES: usize = (AEC_SAMPLE_RATE_HZ as usize) / 100;

#[derive(Debug, Error)]
enum AecError {
    #[error("unexpected DORA input id {0:?}")]
    UnexpectedInput(String),
    #[error("near audio must be 16 kHz mono s16le, got {0:?}")]
    NearFormat(AudioFormat),
    #[error("far audio sample rate {got} is not an integer multiple of {AEC_SAMPLE_RATE_HZ}")]
    FarRate { got: u32 },
    #[error("far audio must have at least one channel, got {0}")]
    FarChannels(u16),
    #[error("upstream node failed: {0}")]
    UpstreamFailed(String),
    #[error("CPAL/DORA stream error: {0}")]
    Stream(String),
    #[error("Sonora AEC requires an explicit --stream-delay-ms value")]
    SonoraRequiresStreamDelay,
    #[error("DORA node initialization failed: {0}")]
    DoraInit(#[source] eyre::Report),
    #[error("DORA payload could not decode as u8 array: {0}")]
    DoraPayload(#[source] eyre::Report),
    #[error("DORA output failed: {0}")]
    DoraOutput(#[source] eyre::Report),
    #[error("audio boundary error: {0}")]
    AudioBoundary(#[from] fluent_dialogue_dora_io_boundary::AudioBoundaryError),
}

#[derive(Parser, Debug)]
#[command(about = "Acoustic echo cancellation for barge-in (near = mic, far = playback).")]
struct Args {
    #[arg(long)]
    output_source_id: String,
    #[arg(long)]
    output_stream_id: String,
    #[arg(long, default_value_t = 0)]
    start_seq: u64,
    #[arg(long, default_value_t = 0)]
    start_sample_index: u64,
    #[arg(long, default_value_t = 0)]
    start_capture_time_ns: u64,
    /// Cap on far reference backlog (in 16 kHz samples) to bound memory and the
    /// render/capture skew if playback is queued far ahead of the mic.
    #[arg(long, default_value_t = 32_000)]
    far_buffer_max_samples: usize,
    /// Playback-to-capture delay in milliseconds. When omitted, WebRTC APM
    /// estimates the delay from the render and capture streams.
    #[arg(long)]
    stream_delay_ms: Option<u16>,
    #[arg(long, value_enum, default_value = "webrtc")]
    backend: AecBackendKind,
}

#[derive(Clone, Copy, Debug, ValueEnum)]
enum AecBackendKind {
    Webrtc,
    Sonora,
}

enum EchoCancellerBackend {
    Webrtc(WebRtcAecBackend),
    Sonora(SonoraAecBackend),
}

impl EchoCancellerBackend {
    fn new(kind: AecBackendKind, stream_delay_ms: Option<u16>) -> Result<Self, AecError> {
        match kind {
            AecBackendKind::Webrtc => Ok(Self::Webrtc(WebRtcAecBackend::new(stream_delay_ms)?)),
            AecBackendKind::Sonora => Ok(Self::Sonora(SonoraAecBackend::new(stream_delay_ms)?)),
        }
    }

    fn process_frame(
        &mut self,
        far_frame: &[i16],
        near_frame: &[i16],
    ) -> Result<Vec<i16>, AecError> {
        match self {
            Self::Webrtc(backend) => backend.process_frame(far_frame, near_frame),
            Self::Sonora(backend) => backend.process_frame(far_frame, near_frame),
        }
    }
}

struct WebRtcAecBackend {
    processor: Processor,
}

impl WebRtcAecBackend {
    fn new(stream_delay_ms: Option<u16>) -> Result<Self, AecError> {
        let processor = Processor::new(AEC_SAMPLE_RATE_HZ)
            .map_err(|err| AecError::Stream(format!("webrtc init failed: {err:?}")))?;
        processor.set_config(WebRtcConfig {
            echo_canceller: Some(WebRtcEchoCanceller::Full { stream_delay_ms }),
            ..Default::default()
        });
        Ok(Self { processor })
    }

    fn process_frame(
        &mut self,
        far_frame: &[i16],
        near_frame: &[i16],
    ) -> Result<Vec<i16>, AecError> {
        let mut render = vec![i16_frame_to_f32(far_frame)];
        self.processor
            .process_render_frame(&mut render)
            .map_err(|err| AecError::Stream(format!("webrtc render failed: {err:?}")))?;

        let mut capture = vec![i16_frame_to_f32(near_frame)];
        self.processor
            .process_capture_frame(&mut capture)
            .map_err(|err| AecError::Stream(format!("webrtc capture failed: {err:?}")))?;
        Ok(f32_frame_to_i16(&capture[0]))
    }
}

struct SonoraAecBackend {
    processor: SonoraAudioProcessing,
}

impl SonoraAecBackend {
    fn new(stream_delay_ms: Option<u16>) -> Result<Self, AecError> {
        let delay_ms = stream_delay_ms.ok_or(AecError::SonoraRequiresStreamDelay)?;
        let stream_config = SonoraStreamConfig::new(AEC_SAMPLE_RATE_HZ, 1);
        let mut processor = SonoraAudioProcessing::builder()
            .config(SonoraConfig {
                echo_canceller: Some(SonoraEchoCanceller::default()),
                ..Default::default()
            })
            .capture_config(stream_config)
            .render_config(stream_config)
            .build();
        processor
            .set_stream_delay_ms(i32::from(delay_ms))
            .map_err(|err| AecError::Stream(format!("sonora delay failed: {err:?}")))?;
        Ok(Self { processor })
    }

    fn process_frame(
        &mut self,
        far_frame: &[i16],
        near_frame: &[i16],
    ) -> Result<Vec<i16>, AecError> {
        let mut render_out = vec![0_i16; far_frame.len()];
        self.processor
            .process_render_i16(far_frame, &mut render_out)
            .map_err(|err| AecError::Stream(format!("sonora render failed: {err:?}")))?;

        let mut capture_out = vec![0_i16; near_frame.len()];
        self.processor
            .process_capture_i16(near_frame, &mut capture_out)
            .map_err(|err| AecError::Stream(format!("sonora capture failed: {err:?}")))?;
        Ok(capture_out)
    }
}

fn i16_frame_to_f32(frame: &[i16]) -> Vec<f32> {
    frame
        .iter()
        .map(|&sample| f32::from(sample) / 32768.0)
        .collect()
}

fn f32_frame_to_i16(frame: &[f32]) -> Vec<i16> {
    frame
        .iter()
        .map(|&sample| (sample.clamp(-1.0, 1.0) * 32767.0).round() as i16)
        .collect()
}

fn main() -> Result<(), AecError> {
    let args = Args::parse();
    let (mut node, mut events) = DoraNode::init_from_env().map_err(AecError::DoraInit)?;
    let output_format = AudioFormat::new(
        AEC_SAMPLE_RATE_HZ,
        1,
        SampleFormat::S16Le,
        ChannelLayout::Interleaved,
    )?;

    let mut aec = EchoCancellerBackend::new(args.backend, args.stream_delay_ms)?;
    let mut near: VecDeque<i16> = VecDeque::new();
    let mut far: VecDeque<i16> = VecDeque::new();
    let far_delay_samples = args
        .stream_delay_ms
        .map(|ms| (usize::from(ms) * AEC_SAMPLE_RATE_HZ as usize) / 1000)
        .unwrap_or(0);
    let mut far_decimator = FarDecimator::new();
    let mut far_delay = FarDelayLine::new(far_delay_samples);

    let output_id = DataId::from(AUDIO_OUTPUT_ID.to_owned());
    let mut seq = args.start_seq;
    let mut sample_index = args.start_sample_index;

    while let Some(event) = events.recv() {
        match event {
            Event::Input { id, metadata, data } => {
                let payload = into_vec::<u8>(&data).map_err(AecError::DoraPayload)?;
                let input = id.to_string();
                if input == NEAR_INPUT_ID {
                    if let DoraAudioMessage::Chunk(chunk) =
                        DoraAudioMessage::decode(&metadata, &payload)?
                    {
                        push_near(&chunk, &mut near)?;
                    }
                } else if input == FAR_INPUT_ID {
                    if let DoraAudioMessage::Chunk(chunk) =
                        DoraAudioMessage::decode(&metadata, &payload)?
                    {
                        push_far(
                            &chunk,
                            &mut far,
                            &mut far_decimator,
                            &mut far_delay,
                            args.far_buffer_max_samples,
                        )?;
                    }
                } else {
                    return Err(AecError::UnexpectedInput(input));
                }

                // Drive processing off the near (microphone) clock: for each
                // ready 10 ms near frame, consume a matching far frame (silence
                // if none) so the canceller stays time-aligned with the mic.
                while near.len() >= FRAME_SAMPLES {
                    let near_frame: Vec<i16> = near.drain(..FRAME_SAMPLES).collect();
                    let far_frame = take_far_frame(&mut far);
                    let cleaned = aec.process_frame(&far_frame, &near_frame)?;
                    emit_frame(
                        &mut node,
                        &output_id,
                        &args,
                        output_format,
                        &mut seq,
                        &mut sample_index,
                        &cleaned,
                    )?;
                }
            }
            Event::InputClosed { id } => {
                let input = id.to_string();
                if input != NEAR_INPUT_ID && input != FAR_INPUT_ID {
                    return Err(AecError::UnexpectedInput(input));
                }
                if input == NEAR_INPUT_ID {
                    emit_final(
                        &mut node,
                        &output_id,
                        &args,
                        output_format,
                        seq,
                        sample_index,
                    )?;
                    return Ok(());
                }
            }
            Event::NodeFailed { error, .. } => return Err(AecError::UpstreamFailed(error)),
            Event::Stop(_) => {
                emit_final(
                    &mut node,
                    &output_id,
                    &args,
                    output_format,
                    seq,
                    sample_index,
                )?;
                return Ok(());
            }
            Event::Error(error) => return Err(AecError::Stream(error)),
            _ => {}
        }
    }

    emit_final(
        &mut node,
        &output_id,
        &args,
        output_format,
        seq,
        sample_index,
    )?;
    Ok(())
}

fn push_near(chunk: &AudioChunk, near: &mut VecDeque<i16>) -> Result<(), AecError> {
    let format = chunk.metadata.format;
    if format.sample_rate_hz != AEC_SAMPLE_RATE_HZ
        || format.channels != 1
        || format.sample_format != SampleFormat::S16Le
    {
        return Err(AecError::NearFormat(format));
    }
    near.extend(s16le_bytes_to_i16(&chunk.payload));
    Ok(())
}

fn push_far(
    chunk: &AudioChunk,
    far: &mut VecDeque<i16>,
    decimator: &mut FarDecimator,
    delay: &mut FarDelayLine,
    max_samples: usize,
) -> Result<(), AecError> {
    let format = chunk.metadata.format;
    if format.channels == 0 {
        return Err(AecError::FarChannels(format.channels));
    }
    if format.sample_rate_hz % AEC_SAMPLE_RATE_HZ != 0 {
        return Err(AecError::FarRate {
            got: format.sample_rate_hz,
        });
    }
    let decimation = (format.sample_rate_hz / AEC_SAMPLE_RATE_HZ) as usize;
    let interleaved_i16: Vec<i16> = match format.sample_format {
        SampleFormat::F32Le => f32le_bytes_to_i16(&chunk.payload),
        SampleFormat::S16Le => s16le_bytes_to_i16(&chunk.payload),
    };
    let samples_i16 = downmix_interleaved_to_mono(&interleaved_i16, format.channels as usize);
    let mut decimated = VecDeque::new();
    decimator.push(&samples_i16, decimation, &mut decimated);
    delay.push(decimated, far);
    // Bound the backlog: if playback is queued far ahead of the mic, drop the
    // oldest reference rather than grow unbounded.
    while far.len() > max_samples {
        far.pop_front();
    }
    Ok(())
}

fn downmix_interleaved_to_mono(samples: &[i16], channels: usize) -> Vec<i16> {
    if channels == 1 {
        return samples.to_vec();
    }
    samples
        .chunks_exact(channels)
        .map(|frame| {
            let sum: i32 = frame.iter().map(|&sample| i32::from(sample)).sum();
            (sum / channels as i32) as i16
        })
        .collect()
}

struct FarDelayLine {
    delayed: VecDeque<i16>,
}

impl FarDelayLine {
    fn new(delay_samples: usize) -> Self {
        Self {
            delayed: VecDeque::from(vec![0; delay_samples]),
        }
    }

    fn push(&mut self, samples: VecDeque<i16>, out: &mut VecDeque<i16>) {
        for sample in samples {
            self.delayed.push_back(sample);
            if let Some(delayed) = self.delayed.pop_front() {
                out.push_back(delayed);
            }
        }
    }
}

/// Averaging decimator that keeps phase continuity across chunk boundaries.
struct FarDecimator {
    accumulator: i32,
    count: usize,
}

impl FarDecimator {
    fn new() -> Self {
        Self {
            accumulator: 0,
            count: 0,
        }
    }

    fn push(&mut self, samples: &[i16], decimation: usize, out: &mut VecDeque<i16>) {
        if decimation <= 1 {
            out.extend(samples.iter().copied());
            return;
        }
        for &sample in samples {
            self.accumulator += i32::from(sample);
            self.count += 1;
            if self.count == decimation {
                out.push_back((self.accumulator / decimation as i32) as i16);
                self.accumulator = 0;
                self.count = 0;
            }
        }
    }
}

fn take_far_frame(far: &mut VecDeque<i16>) -> Vec<i16> {
    let mut frame = Vec::with_capacity(FRAME_SAMPLES);
    while frame.len() < FRAME_SAMPLES {
        match far.pop_front() {
            Some(sample) => frame.push(sample),
            None => frame.push(0), // silence: no echo to cancel right now
        }
    }
    frame
}

#[allow(clippy::too_many_arguments)]
fn emit_frame(
    node: &mut DoraNode,
    output_id: &DataId,
    args: &Args,
    format: AudioFormat,
    seq: &mut u64,
    sample_index: &mut u64,
    cleaned: &[i16],
) -> Result<(), AecError> {
    let capture_time_ns = capture_time_ns_for_frame_offset(
        args.start_capture_time_ns,
        *sample_index - args.start_sample_index,
        AEC_SAMPLE_RATE_HZ,
    );
    let metadata = AudioMetadata::chunk(
        args.output_source_id.clone(),
        args.output_stream_id.clone(),
        *seq,
        *sample_index,
        capture_time_ns,
        cleaned.len() as u64,
        format,
    )?;
    let chunk = AudioChunk::new(metadata, i16_samples_to_s16le_bytes(cleaned))?;
    let encoded = chunk.to_dora_payload()?;
    node.send_output_bytes(
        output_id.clone(),
        chunk.metadata.to_dora_parameters()?,
        encoded.len(),
        &encoded,
    )
    .map_err(AecError::DoraOutput)?;
    *seq = chunk.metadata.next_seq();
    *sample_index = chunk.metadata.next_sample_index();
    Ok(())
}

fn emit_final(
    node: &mut DoraNode,
    output_id: &DataId,
    args: &Args,
    format: AudioFormat,
    seq: u64,
    sample_index: u64,
) -> Result<(), AecError> {
    let capture_time_ns = capture_time_ns_for_frame_offset(
        args.start_capture_time_ns,
        sample_index - args.start_sample_index,
        AEC_SAMPLE_RATE_HZ,
    );
    let metadata = AudioMetadata::final_marker(
        args.output_source_id.clone(),
        args.output_stream_id.clone(),
        seq,
        sample_index,
        capture_time_ns,
        format,
    )?;
    let payload = metadata.to_final_dora_payload()?;
    node.send_output_bytes(
        output_id.clone(),
        metadata.to_dora_parameters()?,
        payload.len(),
        &payload,
    )
    .map_err(AecError::DoraOutput)?;
    Ok(())
}

fn s16le_bytes_to_i16(bytes: &[u8]) -> Vec<i16> {
    bytes
        .chunks_exact(2)
        .map(|b| i16::from_le_bytes([b[0], b[1]]))
        .collect()
}

fn f32le_bytes_to_i16(bytes: &[u8]) -> Vec<i16> {
    bytes
        .chunks_exact(4)
        .map(|b| {
            let value = f32::from_le_bytes([b[0], b[1], b[2], b[3]]);
            (value.clamp(-1.0, 1.0) * 32767.0).round() as i16
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::VecDeque;

    #[test]
    fn far_decimator_averages_by_three_across_boundaries() {
        let mut decimator = FarDecimator::new();
        let mut out = VecDeque::new();
        // 48 kHz -> 16 kHz is decimation by 3.
        decimator.push(&[3, 3, 3, 9, 9], 3, &mut out);
        decimator.push(&[9], 3, &mut out);
        assert_eq!(out.into_iter().collect::<Vec<_>>(), vec![3, 9]);
    }

    #[test]
    fn take_far_frame_pads_with_silence_when_empty() {
        let mut far: VecDeque<i16> = VecDeque::from(vec![1, 2, 3]);
        let frame = take_far_frame(&mut far);
        assert_eq!(frame.len(), FRAME_SAMPLES);
        assert_eq!(&frame[..3], &[1, 2, 3]);
        assert!(frame[3..].iter().all(|&s| s == 0));
    }

    #[test]
    fn f32le_decode_clamps_and_scales() {
        let bytes: Vec<u8> = [0.0_f32, 1.0, -1.0, 2.0]
            .iter()
            .flat_map(|v| v.to_le_bytes())
            .collect();
        assert_eq!(f32le_bytes_to_i16(&bytes), vec![0, 32767, -32767, 32767]);
    }

    #[test]
    fn far_downmixes_stereo_before_decimation() {
        let mut decimator = FarDecimator::new();
        let mut far = VecDeque::new();
        let format =
            AudioFormat::new(48_000, 2, SampleFormat::S16Le, ChannelLayout::Interleaved).unwrap();
        let samples = [10_i16, 30, 20, 40, 30, 50];
        let chunk = AudioChunk::new(
            AudioMetadata::chunk("far".to_owned(), "speaker".to_owned(), 0, 0, 0, 3, format)
                .unwrap(),
            i16_samples_to_s16le_bytes(&samples),
        )
        .unwrap();

        let mut delay = FarDelayLine::new(0);
        push_far(&chunk, &mut far, &mut decimator, &mut delay, 32_000).unwrap();

        assert_eq!(far.into_iter().collect::<Vec<_>>(), vec![30]);
    }

    #[test]
    fn far_delay_line_delays_decimated_reference() {
        let mut delay = FarDelayLine::new(3);
        let mut out = VecDeque::new();

        delay.push(VecDeque::from(vec![10, 20]), &mut out);
        assert_eq!(out.into_iter().collect::<Vec<_>>(), vec![0, 0]);

        let mut out = VecDeque::new();
        delay.push(VecDeque::from(vec![30, 40]), &mut out);
        assert_eq!(out.into_iter().collect::<Vec<_>>(), vec![0, 10]);
    }

    #[test]
    fn aec_backend_passes_silence_through_as_silence() {
        let mut aec = EchoCancellerBackend::new(AecBackendKind::Webrtc, None).unwrap();
        let silence = vec![0_i16; FRAME_SAMPLES];
        let cleaned = aec.process_frame(&silence, &silence).unwrap();
        assert_eq!(cleaned.len(), FRAME_SAMPLES);
        assert!(cleaned.iter().all(|&s| s == 0));
    }

    #[test]
    fn sonora_backend_requires_explicit_stream_delay() {
        let error = match EchoCancellerBackend::new(AecBackendKind::Sonora, None) {
            Ok(_) => panic!("sonora backend accepted missing stream delay"),
            Err(error) => error,
        };
        assert!(matches!(error, AecError::SonoraRequiresStreamDelay));
    }

    #[test]
    fn sonora_backend_passes_silence_through_as_silence() {
        let mut aec = EchoCancellerBackend::new(AecBackendKind::Sonora, Some(80)).unwrap();
        let silence = vec![0_i16; FRAME_SAMPLES];
        let cleaned = aec.process_frame(&silence, &silence).unwrap();
        assert_eq!(cleaned.len(), FRAME_SAMPLES);
        assert!(cleaned.iter().all(|&s| s == 0));
    }

    fn rms(frame: &[i16]) -> f64 {
        let sum: f64 = frame.iter().map(|&s| f64::from(s) * f64::from(s)).sum();
        (sum / frame.len() as f64).sqrt()
    }

    #[test]
    fn aec_backend_attenuates_echo_after_convergence() {
        // The mic hears exactly the played reference (pure echo, no near speech).
        // After the adaptive filter converges, the output should be much quieter.
        let mut aec = EchoCancellerBackend::new(AecBackendKind::Webrtc, None).unwrap();
        let mut phase = 0.0_f64;
        let mut make_frame = || {
            let frame: Vec<i16> = (0..FRAME_SAMPLES)
                .map(|_| {
                    phase += 2.0 * std::f64::consts::PI * 440.0 / f64::from(AEC_SAMPLE_RATE_HZ);
                    (phase.sin() * 8000.0) as i16
                })
                .collect();
            frame
        };

        let input_rms = rms(&make_frame());
        let mut last_rms = input_rms;
        // ~2 s of audio for the canceller to adapt to the (identity) echo path.
        for _ in 0..200 {
            let echo = make_frame();
            let cleaned = aec.process_frame(&echo, &echo).unwrap();
            last_rms = rms(&cleaned);
        }
        // Converged output should be meaningfully attenuated vs the echo input.
        assert!(
            last_rms < input_rms * 0.5,
            "echo not attenuated: input_rms={input_rms:.1}, last_rms={last_rms:.1}"
        );
    }
}
