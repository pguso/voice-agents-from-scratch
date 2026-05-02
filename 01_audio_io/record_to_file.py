"""Record to ``tmp/recorded.wav``."""

from __future__ import annotations

from pathlib import Path

import sys

from voice_agents.audio.audio_input import AudioInputConfig, record_seconds, save_wav

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tmp" / "recorded.wav"

if __name__ == "__main__":
    sec = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0
    print(f"Recording {sec}s to {OUT}…")
    audio, sr = record_seconds(sec, config=AudioInputConfig())
    save_wav(OUT, audio, sr)
    print("Done.")
