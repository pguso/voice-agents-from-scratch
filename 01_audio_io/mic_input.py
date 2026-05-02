"""Record a few seconds from the default mic and print peak level."""

from __future__ import annotations

import numpy as np

from voice_agents.audio.audio_input import AudioInputConfig, record_seconds

if __name__ == "__main__":
    print("Recording 3 seconds…")
    audio, sr = record_seconds(3.0, config=AudioInputConfig(sample_rate=16_000))
    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(np.square(audio))))
    print(f"Sample rate: {sr} Hz, samples: {len(audio)}, peak: {peak:.4f}, RMS: {rms:.4f}")
