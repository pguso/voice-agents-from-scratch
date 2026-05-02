"""Measure Kokoro synthesis time vs audio duration (RTF-style)."""

from __future__ import annotations

import time
from pathlib import Path

from kokoro_onnx import Kokoro
from rich.console import Console
from rich.table import Table

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "models" / "kokoro" / "kokoro-v1.0.onnx"
VOICES = ROOT / "models" / "kokoro" / "voices-v1.0.bin"


def main() -> None:
    console = Console()
    if not MODEL.is_file():
        console.print("Download models first.")
        raise SystemExit(1)
    k = Kokoro(str(MODEL), str(VOICES))
    voice = k.get_voices()[0]
    text = "Measure how long synthesis takes compared to spoken length."
    t0 = time.perf_counter()
    audio, sr = k.create(text, voice=voice, speed=1.0)
    synth_s = time.perf_counter() - t0
    dur_s = len(audio) / float(sr)
    rtf = synth_s / dur_s if dur_s > 0 else 0.0
    tb = Table(title="TTS latency (Kokoro)")
    tb.add_column("Metric")
    tb.add_column("Seconds", justify="right")
    tb.add_row("Audio duration", f"{dur_s:.3f}")
    tb.add_row("Synthesis wall time", f"{synth_s:.3f}")
    tb.add_row("RTF (lower is faster)", f"{rtf:.3f}")
    console.print(tb)


if __name__ == "__main__":
    main()
