"""Print each faster-whisper *segment* as it completes (partial / incremental view)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel
from rich.console import Console

ROOT = Path(__file__).resolve().parents[1]
WHISPER_ROOT = ROOT / "models" / "whisper"

if __name__ == "__main__":
    console = Console()
    wav = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "tmp" / "recorded.wav"
    if not wav.is_file():
        console.print(f"[red]Missing:[/] {wav}")
        raise SystemExit(1)
    model = WhisperModel("tiny.en", download_root=str(WHISPER_ROOT))
    audio, sr = sf.read(wav, dtype="float32")
    audio = np.squeeze(audio)
    segments, _ = model.transcribe(audio, language="en", beam_size=5)
    for seg in segments:
        console.print(f"[green]{seg.start:.2f}–{seg.end:.2f}s[/] {seg.text.strip()}")
