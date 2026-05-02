"""Simple energy-based VAD: print *speech* vs *silence* per block (for debugging)."""

from __future__ import annotations

import sys

import numpy as np
import sounddevice as sd

SR = 16_000
BLOCK = 1024
THRESH = 0.015


def main() -> None:
    print(f"Threshold RMS={THRESH}. Streaming 6s…")

    def cb(indata, frames, t, status):
        m = indata.copy().reshape(-1)
        rms = float(np.sqrt(np.mean(np.square(m)))) if m.size else 0.0
        tag = "SPEECH" if rms >= THRESH else "silence"
        print(f"  {tag:7}  rms={rms:.4f}")

    with sd.InputStream(
        channels=1,
        samplerate=SR,
        blocksize=BLOCK,
        callback=cb,
        dtype="float32",
    ):
        import time

        time.sleep(6)


if __name__ == "__main__":
    main()
