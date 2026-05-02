"""Async streaming Kokoro synthesis (yields audio chunks)."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import numpy as np
import sounddevice as sd
from kokoro_onnx import SAMPLE_RATE, Kokoro
from rich.console import Console

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "models" / "kokoro" / "kokoro-v1.0.onnx"
VOICES = ROOT / "models" / "kokoro" / "voices-v1.0.bin"


async def play_stream(text: str, voice: str) -> None:
    k = Kokoro(str(MODEL), str(VOICES))
    if voice not in k.get_voices():
        voice = k.get_voices()[0]
    gen = k.create_stream(text, voice=voice, speed=1.0, lang="en-us")
    async for chunk, _sr in gen:
        x = np.asarray(chunk, dtype=np.float32).reshape(-1)
        sd.play(x, SAMPLE_RATE)
        sd.wait()


def main() -> None:
    console = Console()
    if not MODEL.is_file():
        console.print("Run 00_start_here/download_models.py first.")
        raise SystemExit(1)
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "This is streaming text to speech, chunk by chunk."
    voice = "af_heart"
    console.print(f"[dim]Voice {voice}, streaming to speaker…[/]")
    asyncio.run(play_stream(text, voice))


if __name__ == "__main__":
    main()
