"""Energy-based voice activity (RMS) — tune threshold vs Silero VAD in production."""

from __future__ import annotations

import sys

import numpy as np
import sounddevice as sd

SR = 16_000
BLOCK = 512


def rms_vad(block: np.ndarray, thresh: float) -> bool:
    v = block.reshape(-1).astype(np.float32)
    return float(np.sqrt(np.mean(np.square(v)))) >= thresh


def main() -> None:
    thresh = float(sys.argv[1]) if len(sys.argv) > 1 else 0.02
    print(f"RMS threshold={thresh}, 5s capture…")
    speech_blocks = 0
    total = 0

    def cb(indata, frames, t, status):
        nonlocal speech_blocks, total
        total += 1
        if rms_vad(indata, thresh):
            speech_blocks += 1

    with sd.InputStream(
        channels=1,
        samplerate=SR,
        blocksize=BLOCK,
        callback=cb,
        dtype="float32",
    ):
        import time

        time.sleep(5)
    print(f"Speech-ish blocks: {speech_blocks}/{total}")


if __name__ == "__main__":
    main()
