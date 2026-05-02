"""Play a short synthetic tone (or a WAV if you pass a path)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

from voice_agents.audio.audio_output import play_float_mono

SR = 16_000

if __name__ == "__main__":
    if len(sys.argv) > 1:
        p = Path(sys.argv[1])
        data, sr = sf.read(p, always_2d=False)
        play_float_mono(np.asarray(data, dtype=np.float32), int(sr))
    else:
        t = np.linspace(0, 0.3, int(0.3 * SR), dtype=np.float32)
        tone = 0.1 * np.sin(2 * np.pi * 440.0 * t)
        play_float_mono(tone, SR)
        print("Played 440 Hz tone. Pass a .wav path to play a file instead.")
