use std::collections::BTreeMap;
use std::convert::TryFrom;
use std::str::FromStr;

use dora_node_api::{Metadata, MetadataParameters, Parameter};
use thiserror::Error;

pub const AUDIO_INPUT_ID: &str = "audio";
pub const AUDIO_OUTPUT_ID: &str = "audio";
pub const DORA_AUDIO_METADATA_FIELDS: [&str; 11] = [
    "source_id",
    "stream_id",
    "seq",
    "sample_index",
    "capture_time_ns",
    "frame_count",
    "sample_rate_hz",
    "channels",
    "sample_format",
    "channel_layout",
    "final",
];

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
    #[error("missing DORA audio metadata field {0}")]
    MissingMetadata(&'static str),
    #[error("DORA audio metadata field {field} has wrong type")]
    WrongMetadataType { field: &'static str },
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
        let mut parameters = BTreeMap::new();
        parameters.insert(
            "source_id".to_owned(),
            Parameter::String(self.source_id.clone()),
        );
        parameters.insert(
            "stream_id".to_owned(),
            Parameter::String(self.stream_id.clone()),
        );
        parameters.insert("seq".to_owned(), int_parameter("seq", self.seq)?);
        parameters.insert(
            "sample_index".to_owned(),
            int_parameter("sample_index", self.sample_index)?,
        );
        parameters.insert(
            "capture_time_ns".to_owned(),
            int_parameter("capture_time_ns", self.capture_time_ns)?,
        );
        parameters.insert(
            "frame_count".to_owned(),
            int_parameter("frame_count", self.frame_count)?,
        );
        parameters.insert(
            "sample_rate_hz".to_owned(),
            int_parameter("sample_rate_hz", u64::from(self.format.sample_rate_hz))?,
        );
        parameters.insert(
            "channels".to_owned(),
            int_parameter("channels", u64::from(self.format.channels))?,
        );
        parameters.insert(
            "sample_format".to_owned(),
            Parameter::String(self.format.sample_format.as_str().to_owned()),
        );
        parameters.insert(
            "channel_layout".to_owned(),
            Parameter::String(self.format.channel_layout.as_str().to_owned()),
        );
        parameters.insert("final".to_owned(), Parameter::Bool(self.final_marker));
        Ok(parameters)
    }

    pub fn from_dora_metadata(metadata: &Metadata) -> Result<Self, AudioBoundaryError> {
        Self::from_dora_parameters(&metadata.parameters)
    }

    pub fn from_dora_parameters(
        parameters: &MetadataParameters,
    ) -> Result<Self, AudioBoundaryError> {
        let audio_metadata = Self {
            source_id: required_string(parameters, "source_id")?,
            stream_id: required_string(parameters, "stream_id")?,
            seq: required_u64(parameters, "seq")?,
            sample_index: required_u64(parameters, "sample_index")?,
            capture_time_ns: required_u64(parameters, "capture_time_ns")?,
            frame_count: required_u64(parameters, "frame_count")?,
            format: AudioFormat::new(
                required_u32(parameters, "sample_rate_hz")?,
                required_u16(parameters, "channels")?,
                SampleFormat::from_str(&required_string(parameters, "sample_format")?)?,
                ChannelLayout::from_str(&required_string(parameters, "channel_layout")?)?,
            )?,
            final_marker: required_bool(parameters, "final")?,
        };
        audio_metadata.validate()?;
        Ok(audio_metadata)
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

fn int_parameter(field: &'static str, value: u64) -> Result<Parameter, AudioBoundaryError> {
    let integer =
        i64::try_from(value).map_err(|_| AudioBoundaryError::IntegerOverflow { field, value })?;
    Ok(Parameter::Integer(integer))
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

fn required_bool(
    parameters: &MetadataParameters,
    field: &'static str,
) -> Result<bool, AudioBoundaryError> {
    match required_parameter(parameters, field)? {
        Parameter::Bool(value) => Ok(*value),
        _ => Err(AudioBoundaryError::WrongMetadataType { field }),
    }
}

fn required_i64(
    parameters: &MetadataParameters,
    field: &'static str,
) -> Result<i64, AudioBoundaryError> {
    match required_parameter(parameters, field)? {
        Parameter::Integer(value) => Ok(*value),
        _ => Err(AudioBoundaryError::WrongMetadataType { field }),
    }
}

fn required_u64(
    parameters: &MetadataParameters,
    field: &'static str,
) -> Result<u64, AudioBoundaryError> {
    let value = required_i64(parameters, field)?;
    u64::try_from(value).map_err(|_| AudioBoundaryError::WrongMetadataType { field })
}

fn required_u32(
    parameters: &MetadataParameters,
    field: &'static str,
) -> Result<u32, AudioBoundaryError> {
    let value = required_u64(parameters, field)?;
    u32::try_from(value).map_err(|_| AudioBoundaryError::WrongMetadataType { field })
}

fn required_u16(
    parameters: &MetadataParameters,
    field: &'static str,
) -> Result<u16, AudioBoundaryError> {
    let value = required_u64(parameters, field)?;
    u16::try_from(value).map_err(|_| AudioBoundaryError::WrongMetadataType { field })
}

#[cfg(test)]
mod tests {
    use super::*;
    fn format() -> AudioFormat {
        AudioFormat::new(16_000, 1, SampleFormat::S16Le, ChannelLayout::Interleaved)
            .expect("format should validate")
    }

    #[test]
    fn metadata_roundtrips_through_dora_parameters() {
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

        let parameters = metadata
            .to_dora_parameters()
            .expect("parameters should encode");
        assert_eq!(
            AudioMetadata::from_dora_parameters(&parameters).expect("metadata should decode"),
            metadata
        );
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
