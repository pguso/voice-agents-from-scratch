"""Transcribe a WAV file once (non-streaming)."""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console

from voice_agents.stt.streaming_stt import TranscribeConfig, transcribe_file

ROOT = Path(__file__).resolve().parents[1]
WHISPER_ROOT = ROOT / "models" / "whisper"

if __name__ == "__main__":
    console = Console()
    wav = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "tmp" / "recorded.wav"
    if not wav.is_file():
        console.print(f"[red]Missing WAV:[/] {wav} — run 01_audio_io/record_to_file.py first.")
        raise SystemExit(1)
    cfg = TranscribeConfig(download_root=str(WHISPER_ROOT))
    text = transcribe_file(wav, config=cfg)
    console.print("[bold]Transcript:[/]", text)
