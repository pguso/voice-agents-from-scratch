"""Speech-to-text using faster-whisper (local)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel


@dataclass
class TranscribeConfig:
    model_size: str = "tiny.en"
    device: str = "auto"
    compute_type: str = "int8"
    download_root: str | None = None
    language: str = "en"


def _get_model(cfg: TranscribeConfig) -> WhisperModel:
    return WhisperModel(
        cfg.model_size,
        device=cfg.device,
        compute_type=cfg.compute_type,
        download_root=cfg.download_root,
    )


def transcribe_file(
    wav_path: str | Path,
    *,
    config: TranscribeConfig | None = None,
) -> str:
    """Transcribe a WAV (or other soundfile-supported) path to text."""
    cfg = config or TranscribeConfig()
    model = _get_model(cfg)
    segments, _ = model.transcribe(
        str(wav_path),
        language=cfg.language,
        beam_size=5,
    )
    parts: list[str] = []
    for seg in segments:
        parts.append(seg.text.strip())
    return " ".join(p for p in parts if p).strip()


def transcribe_samples(
    samples: np.ndarray,
    sample_rate: int,
    *,
    config: TranscribeConfig | None = None,
) -> str:
    """Transcribe in-memory mono float32 samples at ``sample_rate`` Hz."""
    cfg = config or TranscribeConfig()
    model = _get_model(cfg)
    audio = np.asarray(samples, dtype=np.float32).squeeze()
    segments, _ = model.transcribe(
        audio,
        language=cfg.language,
        beam_size=5,
    )
    parts: list[str] = []
    for seg in segments:
        parts.append(seg.text.strip())
    return " ".join(p for p in parts if p).strip()
