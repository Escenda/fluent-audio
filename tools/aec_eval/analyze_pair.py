"""Score an AEC candidate against the captured no-AEC microphone signal."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from nodes.vad.silero.silero import SileroVadConfig, SileroVadSession  # noqa: E402

SAMPLE_RATE_HZ = 16_000
VAD_WINDOW_FRAMES = 512


class RmsMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    reference_playback_dbfs: float
    candidate_playback_dbfs: float
    rms_attenuation_db: float
    baseline_subtracted_echo_reduction_db: float
    reference_vs_far_corr: float
    reference_vs_far_corr_lag_samples: int = Field(ge=0)
    candidate_vs_far_corr: float
    candidate_vs_far_corr_lag_samples: int = Field(ge=0)
    corr_attenuation_db: float
    reference_baseline_dbfs: float
    candidate_baseline_dbfs: float


class VadSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    events: int = Field(ge=0)
    speech_events: int = Field(ge=0)
    speech_seconds: float = Field(ge=0.0)
    turns: int = Field(ge=0)
    max_contiguous_speech_events: int = Field(ge=0)
    max_contiguous_speech_seconds: float = Field(ge=0.0)
    max_detector_speech_frames: int = Field(ge=0)
    max_detector_speech_seconds: float = Field(ge=0.0)
    simulated_barge_in_count: int = Field(ge=0)
    max_speech_probability: float = Field(ge=0.0, le=1.0)


class VadMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    threshold: float = Field(ge=0.0, le=1.0)
    reference: VadSummary
    candidate: VadSummary
    candidate_speech_event_ratio: float = Field(ge=0.0)
    max_allowed_candidate_speech_event_ratio: float = Field(ge=0.0)
    max_allowed_candidate_contiguous_speech_events: int = Field(ge=0)
    barge_in_speech_frames: int = Field(gt=0)
    silence_reset_frames: int = Field(gt=0)


class PassMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    speaker_echo_captured: bool
    rms_attenuation: bool
    echo_reduction: bool
    baseline_vad_triggered: bool
    vad_ratio: bool
    contiguous_vad: bool
    barge_in_detector: bool
    overall: bool


class AecPairReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    candidate_name: str
    reference_near_path: str
    candidate_path: str
    far_stimulus_path: str
    stream_delay_ms: str | None
    stimulus_text: str | None
    stimulus_gain: float | None
    rms: RmsMetrics
    vad: VadMetrics
    passed: PassMetrics


def read_mono_i16(path: Path) -> np.ndarray:
    data = path.read_bytes()
    if len(data) % 2 != 0:
        raise ValueError(f"{path}: s16le byte length must be divisible by 2")
    return np.frombuffer(data, dtype="<i2").astype(np.float32) / np.float32(32768.0)


def read_stimulus_48k_stereo_left_as_16k(path: Path) -> np.ndarray:
    data = path.read_bytes()
    if len(data) % 4 != 0:
        raise ValueError(f"{path}: stereo s16le byte length must be divisible by 4")
    stereo = np.frombuffer(data, dtype="<i2").reshape((-1, 2)).astype(np.float32)
    return stereo[:, 0][::3] / np.float32(32768.0)


def rms(samples: np.ndarray) -> float:
    if samples.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(samples * samples)))


def db(value: float) -> float:
    return 20.0 * math.log10(max(value, 1.0e-12))


def best_corr_level(signal: np.ndarray, reference: np.ndarray, max_lag: int) -> tuple[float, int]:
    best = 0.0
    best_lag = 0
    stride = 8
    lag_step = 32
    reference_strided = reference[::stride]
    reference_energy = float(np.dot(reference_strided, reference_strided))
    if reference_energy == 0.0:
        raise ValueError("far reference is silent; validation is invalid")
    # ponytail: coarse correlation is enough for candidate ranking; use FFT if
    # this becomes lab-grade measurement.
    for lag in range(0, max_lag + 1, lag_step):
        window = signal[lag::stride]
        length = min(window.size, reference_strided.size)
        if length <= 0:
            break
        signal_slice = window[:length]
        reference_slice = reference_strided[:length]
        energy = float(np.dot(signal_slice, signal_slice))
        if energy == 0.0:
            continue
        corr = abs(float(np.dot(signal_slice, reference_slice))) / math.sqrt(
            energy * reference_energy
        )
        if corr > best:
            best = corr
            best_lag = lag
    return best, best_lag


def vad_summary(
    path: Path,
    *,
    threshold: float,
    barge_in_speech_frames: int,
    silence_reset_frames: int,
) -> VadSummary:
    session = SileroVadSession(SileroVadConfig(threshold=threshold))
    results = session.push(read_mono_i16(path))
    results.extend(session.flush())

    speech_events = 0
    speech_frames = 0
    turns = 0
    max_run = 0
    current_run = 0
    previous = False
    detector_speech_frames = 0
    detector_silence_frames = 0
    max_detector_speech_frames = 0
    simulated_barge_in_count = 0
    fired = False
    max_probability = 0.0

    for result in results:
        frame_count = result.window_frames - result.padded_frames
        if frame_count <= 0:
            continue
        max_probability = max(max_probability, result.probability)
        if result.is_speech:
            speech_events += 1
            speech_frames += frame_count
            current_run += 1
            max_run = max(max_run, current_run)
            if not previous:
                turns += 1
            detector_speech_frames += frame_count
            detector_silence_frames = 0
            max_detector_speech_frames = max(max_detector_speech_frames, detector_speech_frames)
            if not fired and detector_speech_frames >= barge_in_speech_frames:
                simulated_barge_in_count = 1
                fired = True
        else:
            current_run = 0
            detector_silence_frames += frame_count
            if detector_silence_frames >= silence_reset_frames:
                detector_speech_frames = 0
        previous = result.is_speech

    return VadSummary(
        events=len(results),
        speech_events=speech_events,
        speech_seconds=speech_frames / SAMPLE_RATE_HZ,
        turns=turns,
        max_contiguous_speech_events=max_run,
        max_contiguous_speech_seconds=max_run * VAD_WINDOW_FRAMES / SAMPLE_RATE_HZ,
        max_detector_speech_frames=max_detector_speech_frames,
        max_detector_speech_seconds=max_detector_speech_frames / SAMPLE_RATE_HZ,
        simulated_barge_in_count=simulated_barge_in_count,
        max_speech_probability=max_probability,
    )


def analyze(args: argparse.Namespace) -> AecPairReport:
    reference = read_mono_i16(args.reference_near)
    candidate = read_mono_i16(args.candidate)
    far = read_stimulus_48k_stereo_left_as_16k(args.far_stimulus)
    length = min(reference.size, candidate.size, far.size)
    if length <= SAMPLE_RATE_HZ:
        raise ValueError("audio is too short to contain baseline and playback windows")
    reference = reference[:length]
    candidate = candidate[:length]
    far = far[:length]

    baseline = slice(0, SAMPLE_RATE_HZ)
    playback = slice(SAMPLE_RATE_HZ, min(5 * SAMPLE_RATE_HZ, length))
    reference_base = rms(reference[baseline])
    reference_play = rms(reference[playback])
    candidate_base = rms(candidate[baseline])
    candidate_play = rms(candidate[playback])
    reference_corr, reference_lag = best_corr_level(
        reference[playback], far[playback], SAMPLE_RATE_HZ // 2
    )
    candidate_corr, candidate_lag = best_corr_level(
        candidate[playback], far[playback], SAMPLE_RATE_HZ // 2
    )
    reference_echo_power = max((reference_play * reference_play) - (reference_base * reference_base), 1.0e-12)
    candidate_echo_power = max((candidate_play * candidate_play) - (candidate_base * candidate_base), 1.0e-12)
    echo_reduction_db = 10.0 * math.log10(candidate_echo_power / reference_echo_power)

    reference_vad = vad_summary(
        args.reference_near,
        threshold=args.vad_threshold,
        barge_in_speech_frames=args.barge_in_speech_frames,
        silence_reset_frames=args.barge_in_silence_reset_frames,
    )
    candidate_vad = vad_summary(
        args.candidate,
        threshold=args.vad_threshold,
        barge_in_speech_frames=args.barge_in_speech_frames,
        silence_reset_frames=args.barge_in_silence_reset_frames,
    )
    ratio = (
        candidate_vad.speech_events / reference_vad.speech_events
        if reference_vad.speech_events
        else 1.0
    )
    passed = PassMetrics(
        speaker_echo_captured=reference_play >= reference_base * 1.5,
        rms_attenuation=(db(candidate_play) - db(reference_play)) <= args.max_rms_attenuation_db,
        echo_reduction=echo_reduction_db <= args.max_echo_reduction_db,
        baseline_vad_triggered=reference_vad.speech_events > 0,
        vad_ratio=ratio <= args.max_vad_speech_ratio,
        contiguous_vad=(
            candidate_vad.max_contiguous_speech_events <= args.max_contiguous_speech_events
        ),
        barge_in_detector=candidate_vad.simulated_barge_in_count == 0,
        overall=False,
    )
    passed = passed.model_copy(
        update={
            "overall": (
                passed.speaker_echo_captured
                and passed.rms_attenuation
                and passed.echo_reduction
                and passed.baseline_vad_triggered
                and passed.vad_ratio
                and passed.contiguous_vad
                and passed.barge_in_detector
            )
        }
    )
    return AecPairReport(
        candidate_name=args.candidate_name,
        reference_near_path=str(args.reference_near),
        candidate_path=str(args.candidate),
        far_stimulus_path=str(args.far_stimulus),
        stream_delay_ms=args.stream_delay_ms,
        stimulus_text=args.stimulus_text,
        stimulus_gain=args.stimulus_gain,
        rms=RmsMetrics(
            reference_playback_dbfs=db(reference_play),
            candidate_playback_dbfs=db(candidate_play),
            rms_attenuation_db=db(candidate_play) - db(reference_play),
            baseline_subtracted_echo_reduction_db=echo_reduction_db,
            reference_vs_far_corr=reference_corr,
            reference_vs_far_corr_lag_samples=reference_lag,
            candidate_vs_far_corr=candidate_corr,
            candidate_vs_far_corr_lag_samples=candidate_lag,
            corr_attenuation_db=db(candidate_corr) - db(reference_corr),
            reference_baseline_dbfs=db(reference_base),
            candidate_baseline_dbfs=db(candidate_base),
        ),
        vad=VadMetrics(
            threshold=args.vad_threshold,
            reference=reference_vad,
            candidate=candidate_vad,
            candidate_speech_event_ratio=ratio,
            max_allowed_candidate_speech_event_ratio=args.max_vad_speech_ratio,
            max_allowed_candidate_contiguous_speech_events=args.max_contiguous_speech_events,
            barge_in_speech_frames=args.barge_in_speech_frames,
            silence_reset_frames=args.barge_in_silence_reset_frames,
        ),
        passed=passed,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-name", required=True)
    parser.add_argument("--reference-near", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--far-stimulus", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--stream-delay-ms", default=None)
    parser.add_argument("--stimulus-text", default=None)
    parser.add_argument("--stimulus-gain", type=float, default=None)
    parser.add_argument("--vad-threshold", type=float, default=0.5)
    parser.add_argument("--max-vad-speech-ratio", type=float, default=0.25)
    parser.add_argument("--max-contiguous-speech-events", type=int, default=9)
    parser.add_argument("--max-rms-attenuation-db", type=float, default=-6.0)
    parser.add_argument("--max-echo-reduction-db", type=float, default=-10.0)
    parser.add_argument("--barge-in-speech-frames", type=int, default=4800)
    parser.add_argument("--barge-in-silence-reset-frames", type=int, default=2048)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = analyze(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(f"candidate={report.candidate_name}")
    print(f"overall_pass={int(report.passed.overall)}")
    print(f"echo_reduction_db={report.rms.baseline_subtracted_echo_reduction_db:.3f}")
    print(f"vad_speech_events={report.vad.candidate.speech_events}")
    print(f"barge_in_detector_fires={report.vad.candidate.simulated_barge_in_count}")
    print(f"report={args.output}")


if __name__ == "__main__":
    main()
