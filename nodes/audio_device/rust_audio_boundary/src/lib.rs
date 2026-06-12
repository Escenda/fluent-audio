use std::convert::TryFrom;
use std::str::FromStr;

use dora_node_api::{Metadata, MetadataParameters, Parameter};
use fluent_audio_contracts::fluent_audio::v1::{
    AudioFormat as PbAudioFormat, AudioFrame, AudioStreamFinal,
    ChannelLayout as PbChannelLayout, SampleFormat as PbSampleFormat,
};
use prost::Message;
use thiserror::Error;

pub const AUDIO_INPUT_ID: &str = "audio";
pub const AUDIO_OUTPUT_ID: &str = "audio";
pub const PROTOBUF_CODEC_KEY: &str = "fluent_audio_codec";
pub const PROTOBUF_SCHEMA_VERSION_KEY: &str = "fluent_audio_schema_version";
pub const PROTOBUF_MESSAGE_TYPE_KEY: &str = "fluent_audio_message_type";
pub const PROTOBUF_CODEC: &str = "protobuf";
pub const PROTOBUF_SCHEMA_VERSION: &str = "fluent_audio.v1";
pub const AUDIO_FRAME_MESSAGE_TYPE: &str = "fluent_audio.v1.AudioFrame";
pub const AUDIO_STREAM_FINAL_MESSAGE_TYPE: &str = "fluent_audio.v1.AudioStreamFinal";

#[derive(Debug, Error)]
pub enum AudioBoundaryError {
    #[error("{field} must be positive, got {value}")]
    NonPositive { field: &'static str, value: u64 },
    #[error("{field} is too large for DORA integer metadata: {value}")]
    IntegerOverflow { field: &'static str, value: u64 },
    #[error("unsupported sample format {0:?}; supported sample format is s16le")]
    UnsupportedSampleFormat(String),
    #[error("unsupported channel layout {0:?}; supported channel layout is interleaved")]
    UnsupportedChannelLayout(String),
    #[error("missing DORA protobuf metadata field {0}")]
    MissingMetadata(&'static str),
    #[error("DORA protobuf metadata field {field} has wrong type")]
    WrongMetadataType { field: &'static str },
    #[error("DORA protobuf metadata field {field} expected {expected:?}, got {actual:?}")]
    MetadataValueMismatch {
        field: &'static str,
        expected: &'static str,
        actual: String,
    },
    #[error("DORA protobuf message type mismatch: expected {expected:?}, got {actual:?}")]
    MessageTypeMismatch {
        expected: &'static str,
        actual: String,
    },
    #[error("DORA protobuf payload could not decode as {message_type}: {source}")]
    ProtobufDecode {
        message_type: &'static str,
        #[source]
        source: prost::DecodeError,
    },
    #[error("AudioFrame protobuf is missing required format")]
    MissingAudioFrameFormat,
    #[error("AudioStreamFinal protobuf is missing required format")]
    MissingAudioFinalFormat,
    #[error("unsupported protobuf sample format {0}")]
    UnsupportedProtobufSampleFormat(i32),
    #[error("unsupported protobuf channel layout {0}")]
    UnsupportedProtobufChannelLayout(i32),
    #[error("DORA audio final marker must have frame_count=0")]
    FinalFrameCount,
    #[error("DORA audio chunk metadata must have frame_count > 0")]
    NonFinalFrameCount,
    #[error(
        "audio payload length mismatch: frame_count={frame_count}, frame_size_bytes={frame_size_bytes}, payload_len={payload_len}"
    )]
    PayloadLength {
        frame_count: u64,
        frame_size_bytes: usize,
        payload_len: usize,
    },
    #[error("audio chunk sequence mismatch: expected seq {expected}, got {actual}")]
    SequenceMismatch { expected: u64, actual: u64 },
    #[error("audio chunk sample_index mismatch: expected sample_index {expected}, got {actual}")]
    SampleIndexMismatch { expected: u64, actual: u64 },
    #[error("audio source mismatch: expected {expected:?}, got {actual:?}")]
    SourceMismatch { expected: String, actual: String },
    #[error("audio stream mismatch: expected {expected:?}, got {actual:?}")]
    StreamMismatch { expected: String, actual: String },
    #[error("audio format mismatch: expected {expected:?}, got {actual:?}")]
    FormatMismatch {
        expected: AudioFormat,
        actual: AudioFormat,
    },
    #[error("byte payload length must be even for s16le, got {0}")]
    OddS16PayloadLength(usize),
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum SampleFormat {
    S16Le,
}

impl SampleFormat {
    pub fn as_str(self) -> &'static str {
        match self {
            SampleFormat::S16Le => "s16le",
        }
    }

    pub fn bytes_per_sample(self) -> usize {
        match self {
            SampleFormat::S16Le => 2,
        }
    }

    pub fn to_proto(self) -> i32 {
        match self {
            SampleFormat::S16Le => PbSampleFormat::S16le as i32,
        }
    }

    pub fn from_proto(value: i32) -> Result<Self, AudioBoundaryError> {
        match PbSampleFormat::try_from(value) {
            Ok(PbSampleFormat::S16le) => Ok(SampleFormat::S16Le),
            Ok(_) | Err(_) => Err(AudioBoundaryError::UnsupportedProtobufSampleFormat(value)),
        }
    }
}

impl FromStr for SampleFormat {
    type Err = AudioBoundaryError;

    fn from_str(value: &str) -> Result<Self, Self::Err> {
        match value {
            "s16le" => Ok(SampleFormat::S16Le),
            other => Err(AudioBoundaryError::UnsupportedSampleFormat(
                other.to_owned(),
            )),
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum ChannelLayout {
    Interleaved,
}

impl ChannelLayout {
    pub fn as_str(self) -> &'static str {
        match self {
            ChannelLayout::Interleaved => "interleaved",
        }
    }

    pub fn to_proto(self) -> i32 {
        match self {
            ChannelLayout::Interleaved => PbChannelLayout::Interleaved as i32,
        }
    }

    pub fn from_proto(value: i32) -> Result<Self, AudioBoundaryError> {
        match PbChannelLayout::try_from(value) {
            Ok(PbChannelLayout::Interleaved) => Ok(ChannelLayout::Interleaved),
            Ok(_) | Err(_) => Err(AudioBoundaryError::UnsupportedProtobufChannelLayout(value)),
        }
    }
}

impl FromStr for ChannelLayout {
    type Err = AudioBoundaryError;

    fn from_str(value: &str) -> Result<Self, Self::Err> {
        match value {
            "interleaved" => Ok(ChannelLayout::Interleaved),
            other => Err(AudioBoundaryError::UnsupportedChannelLayout(
                other.to_owned(),
            )),
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct AudioFormat {
    pub sample_rate_hz: u32,
    pub channels: u16,
    pub sample_format: SampleFormat,
    pub channel_layout: ChannelLayout,
}

impl AudioFormat {
    pub fn new(
        sample_rate_hz: u32,
        channels: u16,
        sample_format: SampleFormat,
        channel_layout: ChannelLayout,
    ) -> Result<Self, AudioBoundaryError> {
        if sample_rate_hz == 0 {
            return Err(AudioBoundaryError::NonPositive {
                field: "sample_rate_hz",
                value: u64::from(sample_rate_hz),
            });
        }
        if channels == 0 {
            return Err(AudioBoundaryError::NonPositive {
                field: "channels",
                value: u64::from(channels),
            });
        }
        Ok(Self {
            sample_rate_hz,
            channels,
            sample_format,
            channel_layout,
        })
    }

    pub fn frame_size_bytes(self) -> usize {
        self.sample_format.bytes_per_sample() * usize::from(self.channels)
    }

    pub fn to_proto(self) -> PbAudioFormat {
        PbAudioFormat {
            sample_rate_hz: self.sample_rate_hz,
            channels: u32::from(self.channels),
            sample_format: self.sample_format.to_proto(),
            channel_layout: self.channel_layout.to_proto(),
        }
    }

    pub fn from_proto(format: PbAudioFormat) -> Result<Self, AudioBoundaryError> {
        let channels =
            u16::try_from(format.channels).map_err(|_| AudioBoundaryError::IntegerOverflow {
                field: "channels",
                value: u64::from(format.channels),
            })?;
        AudioFormat::new(
            format.sample_rate_hz,
            channels,
            SampleFormat::from_proto(format.sample_format)?,
            ChannelLayout::from_proto(format.channel_layout)?,
        )
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct AudioMetadata {
    pub source_id: String,
    pub stream_id: String,
    pub seq: u64,
    pub sample_index: u64,
    pub capture_time_ns: u64,
    pub frame_count: u64,
    pub format: AudioFormat,
    pub final_marker: bool,
}

impl AudioMetadata {
    pub fn chunk(
        source_id: String,
        stream_id: String,
        seq: u64,
        sample_index: u64,
        capture_time_ns: u64,
        frame_count: u64,
        format: AudioFormat,
    ) -> Result<Self, AudioBoundaryError> {
        let metadata = Self {
            source_id,
            stream_id,
            seq,
            sample_index,
            capture_time_ns,
            frame_count,
            format,
            final_marker: false,
        };
        metadata.validate()?;
        Ok(metadata)
    }

    pub fn final_marker(
        source_id: String,
        stream_id: String,
        seq: u64,
        sample_index: u64,
        capture_time_ns: u64,
        format: AudioFormat,
    ) -> Result<Self, AudioBoundaryError> {
        let metadata = Self {
            source_id,
            stream_id,
            seq,
            sample_index,
            capture_time_ns,
            frame_count: 0,
            format,
            final_marker: true,
        };
        metadata.validate()?;
        Ok(metadata)
    }

    pub fn validate(&self) -> Result<(), AudioBoundaryError> {
        if self.final_marker {
            if self.frame_count != 0 {
                return Err(AudioBoundaryError::FinalFrameCount);
            }
        } else if self.frame_count == 0 {
            return Err(AudioBoundaryError::NonFinalFrameCount);
        }
        Ok(())
    }

    pub fn next_seq(&self) -> u64 {
        self.seq + 1
    }

    pub fn next_sample_index(&self) -> u64 {
        self.sample_index + self.frame_count
    }

    pub fn validate_payload_len(&self, payload_len: usize) -> Result<(), AudioBoundaryError> {
        let expected = usize::try_from(self.frame_count)
            .ok()
            .and_then(|frames| frames.checked_mul(self.format.frame_size_bytes()));
        if expected != Some(payload_len) {
            return Err(AudioBoundaryError::PayloadLength {
                frame_count: self.frame_count,
                frame_size_bytes: self.format.frame_size_bytes(),
                payload_len,
            });
        }
        Ok(())
    }

    pub fn to_dora_parameters(&self) -> Result<MetadataParameters, AudioBoundaryError> {
        self.validate()?;
        let message_type = if self.final_marker {
            AUDIO_STREAM_FINAL_MESSAGE_TYPE
        } else {
            AUDIO_FRAME_MESSAGE_TYPE
        };
        protobuf_metadata_parameters(message_type)
    }

    pub fn to_final_dora_payload(&self) -> Result<Vec<u8>, AudioBoundaryError> {
        self.validate()?;
        if !self.final_marker {
            return Err(AudioBoundaryError::NonFinalFrameCount);
        }
        let final_message = AudioStreamFinal {
            source_id: self.source_id.clone(),
            stream_id: self.stream_id.clone(),
            seq: self.seq,
            sample_index: self.sample_index,
            capture_time_ns: self.capture_time_ns,
            format: Some(self.format.to_proto()),
        };
        Ok(final_message.encode_to_vec())
    }

    pub fn from_audio_frame(frame: AudioFrame) -> Result<Self, AudioBoundaryError> {
        let frame_count = u64::from(frame.frame_count);
        let format = AudioFormat::from_proto(
            frame.format.ok_or(AudioBoundaryError::MissingAudioFrameFormat)?,
        )?;
        Self::chunk(
            frame.source_id,
            frame.stream_id,
            frame.seq,
            frame.sample_index,
            frame.capture_time_ns,
            frame_count,
            format,
        )
    }

    pub fn from_audio_stream_final(
        final_message: AudioStreamFinal,
    ) -> Result<Self, AudioBoundaryError> {
        let format = AudioFormat::from_proto(
            final_message
                .format
                .ok_or(AudioBoundaryError::MissingAudioFinalFormat)?,
        )?;
        Self::final_marker(
            final_message.source_id,
            final_message.stream_id,
            final_message.seq,
            final_message.sample_index,
            final_message.capture_time_ns,
            format,
        )
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum DoraAudioMessage {
    Chunk(AudioChunk),
    Final(AudioMetadata),
}

impl DoraAudioMessage {
    pub fn decode(metadata: &Metadata, payload: &[u8]) -> Result<Self, AudioBoundaryError> {
        Self::decode_from_parameters(&metadata.parameters, payload)
    }

    pub fn decode_from_parameters(
        parameters: &MetadataParameters,
        payload: &[u8],
    ) -> Result<Self, AudioBoundaryError> {
        match protobuf_message_type_from_parameters(parameters)? {
            AUDIO_FRAME_MESSAGE_TYPE => {
                let frame = AudioFrame::decode(payload).map_err(|source| {
                    AudioBoundaryError::ProtobufDecode {
                        message_type: AUDIO_FRAME_MESSAGE_TYPE,
                        source,
                    }
                })?;
                Ok(DoraAudioMessage::Chunk(AudioChunk::from_audio_frame(frame)?))
            }
            AUDIO_STREAM_FINAL_MESSAGE_TYPE => {
                let final_message = AudioStreamFinal::decode(payload).map_err(|source| {
                    AudioBoundaryError::ProtobufDecode {
                        message_type: AUDIO_STREAM_FINAL_MESSAGE_TYPE,
                        source,
                    }
                })?;
                Ok(DoraAudioMessage::Final(
                    AudioMetadata::from_audio_stream_final(final_message)?,
                ))
            }
            other => Err(AudioBoundaryError::MessageTypeMismatch {
                expected: AUDIO_FRAME_MESSAGE_TYPE,
                actual: other.to_owned(),
            }),
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct AudioChunk {
    pub metadata: AudioMetadata,
    pub payload: Vec<u8>,
}

impl AudioChunk {
    pub fn new(metadata: AudioMetadata, payload: Vec<u8>) -> Result<Self, AudioBoundaryError> {
        metadata.validate_payload_len(payload.len())?;
        Ok(Self { metadata, payload })
    }

    pub fn from_audio_frame(frame: AudioFrame) -> Result<Self, AudioBoundaryError> {
        let payload = frame.payload.clone();
        let metadata = AudioMetadata::from_audio_frame(frame)?;
        Self::new(metadata, payload)
    }

    pub fn to_dora_payload(&self) -> Result<Vec<u8>, AudioBoundaryError> {
        self.metadata.validate_payload_len(self.payload.len())?;
        let frame_count = u32::try_from(self.metadata.frame_count).map_err(|_| {
            AudioBoundaryError::IntegerOverflow {
                field: "frame_count",
                value: self.metadata.frame_count,
            }
        })?;
        let frame = AudioFrame {
            source_id: self.metadata.source_id.clone(),
            stream_id: self.metadata.stream_id.clone(),
            seq: self.metadata.seq,
            sample_index: self.metadata.sample_index,
            capture_time_ns: self.metadata.capture_time_ns,
            frame_count,
            format: Some(self.metadata.format.to_proto()),
            payload: self.payload.clone(),
        };
        Ok(frame.encode_to_vec())
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct ExpectedAudioStream {
    pub source_id: String,
    pub stream_id: String,
    pub format: AudioFormat,
    pub next_seq: Option<u64>,
    pub next_sample_index: Option<u64>,
}

impl ExpectedAudioStream {
    pub fn new(source_id: String, stream_id: String, format: AudioFormat) -> Self {
        Self {
            source_id,
            stream_id,
            format,
            next_seq: None,
            next_sample_index: None,
        }
    }

    pub fn validate_chunk(&mut self, chunk: &AudioChunk) -> Result<(), AudioBoundaryError> {
        self.validate_metadata(&chunk.metadata)?;
        chunk.metadata.validate_payload_len(chunk.payload.len())?;
        self.next_seq = Some(chunk.metadata.next_seq());
        self.next_sample_index = Some(chunk.metadata.next_sample_index());
        Ok(())
    }

    pub fn validate_final_marker(
        &mut self,
        metadata: &AudioMetadata,
        payload_len: usize,
    ) -> Result<(), AudioBoundaryError> {
        self.validate_metadata(metadata)?;
        if payload_len != 0 {
            return Err(AudioBoundaryError::PayloadLength {
                frame_count: metadata.frame_count,
                frame_size_bytes: metadata.format.frame_size_bytes(),
                payload_len,
            });
        }
        Ok(())
    }

    fn validate_metadata(&self, metadata: &AudioMetadata) -> Result<(), AudioBoundaryError> {
        if metadata.source_id != self.source_id {
            return Err(AudioBoundaryError::SourceMismatch {
                expected: self.source_id.clone(),
                actual: metadata.source_id.clone(),
            });
        }
        if metadata.stream_id != self.stream_id {
            return Err(AudioBoundaryError::StreamMismatch {
                expected: self.stream_id.clone(),
                actual: metadata.stream_id.clone(),
            });
        }
        if metadata.format != self.format {
            return Err(AudioBoundaryError::FormatMismatch {
                expected: self.format,
                actual: metadata.format,
            });
        }
        if let Some(expected) = self.next_seq {
            if metadata.seq != expected {
                return Err(AudioBoundaryError::SequenceMismatch {
                    expected,
                    actual: metadata.seq,
                });
            }
        }
        if let Some(expected) = self.next_sample_index {
            if metadata.sample_index != expected {
                return Err(AudioBoundaryError::SampleIndexMismatch {
                    expected,
                    actual: metadata.sample_index,
                });
            }
        }
        Ok(())
    }
}

pub fn capture_time_ns_for_frame_offset(
    start_capture_time_ns: u64,
    frame_offset: u64,
    sample_rate_hz: u32,
) -> u64 {
    start_capture_time_ns + (frame_offset * 1_000_000_000) / u64::from(sample_rate_hz)
}

pub fn i16_samples_to_s16le_bytes(samples: &[i16]) -> Vec<u8> {
    let mut bytes = Vec::with_capacity(samples.len() * 2);
    for sample in samples {
        bytes.extend_from_slice(&sample.to_le_bytes());
    }
    bytes
}

pub fn s16le_bytes_to_i16_samples(bytes: &[u8]) -> Result<Vec<i16>, AudioBoundaryError> {
    if !bytes.len().is_multiple_of(2) {
        return Err(AudioBoundaryError::OddS16PayloadLength(bytes.len()));
    }
    Ok(bytes
        .chunks_exact(2)
        .map(|chunk| i16::from_le_bytes([chunk[0], chunk[1]]))
        .collect())
}

pub fn protobuf_metadata_parameters(
    message_type: &'static str,
) -> Result<MetadataParameters, AudioBoundaryError> {
    let mut parameters = MetadataParameters::new();
    parameters.insert(
        PROTOBUF_CODEC_KEY.to_owned(),
        Parameter::String(PROTOBUF_CODEC.to_owned()),
    );
    parameters.insert(
        PROTOBUF_SCHEMA_VERSION_KEY.to_owned(),
        Parameter::String(PROTOBUF_SCHEMA_VERSION.to_owned()),
    );
    parameters.insert(
        PROTOBUF_MESSAGE_TYPE_KEY.to_owned(),
        Parameter::String(message_type.to_owned()),
    );
    Ok(parameters)
}

pub fn protobuf_message_type(metadata: &Metadata) -> Result<&str, AudioBoundaryError> {
    protobuf_message_type_from_parameters(&metadata.parameters)
}

pub fn protobuf_message_type_from_parameters(
    parameters: &MetadataParameters,
) -> Result<&str, AudioBoundaryError> {
    let codec = required_string(parameters, PROTOBUF_CODEC_KEY)?;
    if codec != PROTOBUF_CODEC {
        return Err(AudioBoundaryError::MetadataValueMismatch {
            field: PROTOBUF_CODEC_KEY,
            expected: PROTOBUF_CODEC,
            actual: codec,
        });
    }
    let schema_version = required_string(parameters, PROTOBUF_SCHEMA_VERSION_KEY)?;
    if schema_version != PROTOBUF_SCHEMA_VERSION {
        return Err(AudioBoundaryError::MetadataValueMismatch {
            field: PROTOBUF_SCHEMA_VERSION_KEY,
            expected: PROTOBUF_SCHEMA_VERSION,
            actual: schema_version,
        });
    }
    required_string_ref(parameters, PROTOBUF_MESSAGE_TYPE_KEY)
}

fn required_parameter<'a>(
    parameters: &'a MetadataParameters,
    field: &'static str,
) -> Result<&'a Parameter, AudioBoundaryError> {
    parameters
        .get(field)
        .ok_or(AudioBoundaryError::MissingMetadata(field))
}

fn required_string(
    parameters: &MetadataParameters,
    field: &'static str,
) -> Result<String, AudioBoundaryError> {
    match required_parameter(parameters, field)? {
        Parameter::String(value) => Ok(value.clone()),
        _ => Err(AudioBoundaryError::WrongMetadataType { field }),
    }
}

fn required_string_ref<'a>(
    parameters: &'a MetadataParameters,
    field: &'static str,
) -> Result<&'a str, AudioBoundaryError> {
    match required_parameter(parameters, field)? {
        Parameter::String(value) => Ok(value.as_str()),
        _ => Err(AudioBoundaryError::WrongMetadataType { field }),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn format() -> AudioFormat {
        AudioFormat::new(16_000, 1, SampleFormat::S16Le, ChannelLayout::Interleaved)
            .expect("format should validate")
    }

    #[test]
    fn audio_frame_roundtrips_through_dora_protobuf_payload() {
        let metadata = AudioMetadata::chunk(
            "capture".to_owned(),
            "audio/test".to_owned(),
            7,
            320,
            20_000_000,
            160,
            format(),
        )
        .expect("metadata should validate");
        let chunk = AudioChunk::new(metadata, vec![0; 320]).expect("chunk should validate");

        let parameters = chunk
            .metadata
            .to_dora_parameters()
            .expect("parameters should encode");
        assert_eq!(
            protobuf_message_type_from_parameters(&parameters).expect("message type"),
            AUDIO_FRAME_MESSAGE_TYPE
        );
        let decoded =
            DoraAudioMessage::decode_from_parameters(&parameters, &chunk.to_dora_payload().unwrap())
                .expect("protobuf payload should decode");
        assert_eq!(decoded, DoraAudioMessage::Chunk(chunk));
    }

    #[test]
    fn audio_final_marker_roundtrips_through_dora_protobuf_payload() {
        let metadata = AudioMetadata::final_marker(
            "capture".to_owned(),
            "audio/test".to_owned(),
            7,
            320,
            20_000_000,
            format(),
        )
        .expect("metadata should validate");

        let parameters = metadata
            .to_dora_parameters()
            .expect("parameters should encode");
        assert_eq!(
            protobuf_message_type_from_parameters(&parameters).expect("message type"),
            AUDIO_STREAM_FINAL_MESSAGE_TYPE
        );
        let decoded = DoraAudioMessage::decode_from_parameters(
            &parameters,
            &metadata.to_final_dora_payload().unwrap(),
        )
        .expect("protobuf final marker should decode");
        assert_eq!(decoded, DoraAudioMessage::Final(metadata));
    }

    #[test]
    fn contiguous_stream_rejects_sequence_gap() {
        let mut expected =
            ExpectedAudioStream::new("capture".to_owned(), "audio/test".to_owned(), format());
        let first = AudioChunk::new(
            AudioMetadata::chunk(
                "capture".to_owned(),
                "audio/test".to_owned(),
                0,
                0,
                0,
                2,
                format(),
            )
            .expect("metadata should validate"),
            vec![0, 0, 1, 0],
        )
        .expect("payload should validate");
        expected
            .validate_chunk(&first)
            .expect("first chunk should validate");

        let second = AudioChunk::new(
            AudioMetadata::chunk(
                "capture".to_owned(),
                "audio/test".to_owned(),
                2,
                2,
                125_000,
                2,
                format(),
            )
            .expect("metadata should validate"),
            vec![0, 0, 1, 0],
        )
        .expect("payload should validate");

        assert!(matches!(
            expected.validate_chunk(&second),
            Err(AudioBoundaryError::SequenceMismatch {
                expected: 1,
                actual: 2
            })
        ));
    }

    #[test]
    fn s16le_conversion_preserves_little_endian_samples() {
        let bytes = i16_samples_to_s16le_bytes(&[-2, 0, 258]);
        assert_eq!(bytes, vec![254, 255, 0, 0, 2, 1]);
        assert_eq!(
            s16le_bytes_to_i16_samples(&bytes).expect("bytes should decode"),
            vec![-2, 0, 258]
        );
    }
}
