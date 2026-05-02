"""Text-to-speech: Kokoro ONNX (default) with WAV output."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro


@dataclass
class TTSConfig:
    model_path: str
    voices_path: str
    voice: str = "af_heart"
    speed: float = 1.0
    lang: str = "en-us"


def list_voices(config: TTSConfig) -> list[str]:
    tts = Kokoro(config.model_path, config.voices_path)
    return tts.get_voices()


def pick_voice(config: TTSConfig, preferred: str) -> str:
    names = list_voices(config)
    if preferred in names:
        return preferred
    return names[0] if names else preferred


def synthesize_to_wav(
    text: str,
    out_path: str | Path,
    *,
    config: TTSConfig,
) -> None:
    """Synthesize ``text`` to a mono WAV file at Kokoro's sample rate."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tts = Kokoro(config.model_path, config.voices_path)
    audio, sr = tts.create(
        text,
        voice=config.voice,
        speed=config.speed,
        lang=config.lang,
    )
    sf.write(str(out_path), np.asarray(audio, dtype=np.float32), sr, subtype="FLOAT")
