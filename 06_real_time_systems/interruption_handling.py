"""Barge-in demo: start playback, stop early when *stop* event fires."""

from __future__ import annotations

import threading
import time
from pathlib import Path

import numpy as np
import sounddevice as sd
from rich.console import Console
from rich.prompt import Prompt

ROOT = Path(__file__).resolve().parents[1]
WAV = ROOT / "tmp" / "latency_response.wav"


def play_with_cancel(samples: np.ndarray, sr: int, cancel: threading.Event) -> None:
    """Play sample-by-sample until *cancel* (coarse but educational)."""
    # chunk for efficiency
    chunk = 2048
    i = 0
    n = len(samples)
    while i < n and not cancel.is_set():
        end = min(i + chunk, n)
        sd.play(samples[i:end], sr)
        sd.wait()
        i = end
    if cancel.is_set():
        sd.stop()


def main() -> None:
    console = Console()
    if not WAV.is_file():
        console.print("Run 05_full_voice_loop/debug_latency.py once to create tmp/latency_response.wav")
        raise SystemExit(1)
    import soundfile as sf

    data, sr = sf.read(WAV, dtype="float32")
    x = np.squeeze(data)
    cancel = threading.Event()

    def runner() -> None:
        play_with_cancel(x, int(sr), cancel)

    t = threading.Thread(target=runner, daemon=True)
    t.start()
    time.sleep(0.3)
    if Prompt.ask("Stop playback now?", default=True, show_default=True):
        cancel.set()
    t.join(timeout=5)
    console.print("Done (event-based cancel).")


if __name__ == "__main__":
    main()
