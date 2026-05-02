"""Stream from the mic in short blocks and print RMS (no STT)."""

from __future__ import annotations

import sys

import numpy as np
import sounddevice as sd

SR = 16_000
BLOCK = 1024


def main() -> None:
    print("Streaming mic levels (Ctrl+C to stop)…")

    def cb(indata, frames, t, status):
        if status:
            print(status, file=sys.stderr)
        m = indata.copy().reshape(-1)
        rms = float(np.sqrt(np.mean(np.square(m)))) if m.size else 0.0
        bar = "█" * min(40, int(rms * 400))
        print(f"\rRMS: {rms:.4f} {bar:<40}", end="", flush=True)

    with sd.InputStream(
        channels=1,
        samplerate=SR,
        blocksize=BLOCK,
        callback=cb,
        dtype="float32",
    ):
        import time

        time.sleep(8)
    print()


if __name__ == "__main__":
    main()
