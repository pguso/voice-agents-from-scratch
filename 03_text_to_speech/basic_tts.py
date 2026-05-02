"""Synthesize speech with Kokoro (same stack as chapter 00)."""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console

from voice_agents.tts.streaming_tts import TTSConfig, pick_voice, synthesize_to_wav

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "models" / "kokoro" / "kokoro-v1.0.onnx"
VOICES = ROOT / "models" / "kokoro" / "voices-v1.0.bin"
OUT = ROOT / "tmp" / "tts_basic.wav"

if __name__ == "__main__":
    console = Console()
    if not MODEL.is_file() or not VOICES.is_file():
        console.print("[red]Download Kokoro models first:[/] uv run python 00_start_here/download_models.py")
        raise SystemExit(1)
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Hello from Kokoro text to speech."
    cfg = TTSConfig(model_path=str(MODEL), voices_path=str(VOICES), voice="af_heart")
    cfg.voice = pick_voice(cfg, cfg.voice)
    synthesize_to_wav(text, OUT, config=cfg)
    console.print(f"Wrote [bold]{OUT}[/]")
