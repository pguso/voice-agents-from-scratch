"""Chunked transcription: record windows and transcribe each (streaming-style demo)."""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import sounddevice as sd
from rich.console import Console

from voice_agents.stt.streaming_stt import TranscribeConfig, transcribe_samples

ROOT = Path(__file__).resolve().parents[1]
WHISPER_ROOT = ROOT / "models" / "whisper"
SR = 16_000
WINDOW_S = 4.0


def main() -> None:
    console = Console()
    cfg = TranscribeConfig(download_root=str(WHISPER_ROOT))
    frames = int(WINDOW_S * SR)
    console.print(f"[dim]Recording {WINDOW_S}s windows; partial transcripts each chunk. Ctrl+C to stop.[/]")
    buf = np.zeros(frames, dtype=np.float32)
    try:
        while True:
            audio = sd.rec(frames, samplerate=SR, channels=1, dtype="float32")
            sd.wait()
            buf[:] = audio.reshape(-1)
            t0 = time.perf_counter()
            text = transcribe_samples(buf, SR, config=cfg)
            dt = time.perf_counter() - t0
            console.print(f"[cyan]{dt:.2f}s[/] — {text or '(silence)'}")
    except KeyboardInterrupt:
        console.print("\nStopped.")


if __name__ == "__main__":
    main()
