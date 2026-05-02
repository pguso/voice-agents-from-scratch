"""Microphone capture using sounddevice."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf


@dataclass
class AudioInputConfig:
    sample_rate: int = 16_000
    channels: int = 1
    dtype: str = "float32"


def record_seconds(
    duration_s: float,
    *,
    config: AudioInputConfig | None = None,
) -> tuple[np.ndarray, int]:
    """Record mono audio for a fixed duration."""
    cfg = config or AudioInputConfig()
    frames = int(cfg.sample_rate * duration_s)
    audio = sd.rec(
        frames,
        samplerate=cfg.sample_rate,
        channels=cfg.channels,
        dtype=cfg.dtype,
    )
    sd.wait()
    return np.squeeze(audio), cfg.sample_rate


def record_until_silence(
    *,
    max_duration_s: float = 30.0,
    silence_threshold: float = 0.02,
    silence_duration_s: float = 0.8,
    chunk_s: float = 0.05,
    config: AudioInputConfig | None = None,
) -> tuple[np.ndarray, int]:
    """Record until RMS stays below threshold for ``silence_duration_s`` or ``max_duration_s``."""
    cfg = config or AudioInputConfig()
    chunk_frames = max(1, int(cfg.sample_rate * chunk_s))
    max_chunks = int(max_duration_s / chunk_s)
    chunks: list[np.ndarray] = []
    silent_chunks = 0
    needed_silent = int(silence_duration_s / chunk_s)

    for _ in range(max_chunks):
        block = sd.rec(
            chunk_frames,
            samplerate=cfg.sample_rate,
            channels=cfg.channels,
            dtype=cfg.dtype,
        )
        sd.wait()
        block = np.squeeze(block)
        chunks.append(block)
        rms = float(np.sqrt(np.mean(np.square(block))))
        if rms < silence_threshold:
            silent_chunks += 1
            if silent_chunks >= needed_silent and len(chunks) > needed_silent:
                # strip trailing silence chunks
                audio = np.concatenate(chunks[: -needed_silent])
                return audio, cfg.sample_rate
        else:
            silent_chunks = 0

    return np.concatenate(chunks), cfg.sample_rate


def save_wav(path: str | Path, samples: np.ndarray, sample_rate: int) -> None:
    """Write mono float/PCM to WAV."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), samples, sample_rate, subtype="FLOAT" if samples.dtype == np.float32 else "PCM_16")
