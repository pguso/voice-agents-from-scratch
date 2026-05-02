"""Stream LLM tokens; flush TTS on sentence boundaries (lighter than full duplex)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import sounddevice as sd
from kokoro_onnx import SAMPLE_RATE, Kokoro
from rich.console import Console

from voice_agents.agent.agent_core import AgentCore
from voice_agents.agent.prompt_engine import PromptEngine
from voice_agents.audio.audio_input import AudioInputConfig, record_seconds
from voice_agents.stt.streaming_stt import TranscribeConfig, transcribe_samples

ROOT = Path(__file__).resolve().parents[1]
WHISPER_ROOT = ROOT / "models" / "whisper"
LLM_PATH = ROOT / "models" / "llm" / "qwen2.5-0.5b-instruct-q4_k_m.gguf"
KOKORO_MODEL = ROOT / "models" / "kokoro" / "kokoro-v1.0.onnx"
KOKORO_VOICES = ROOT / "models" / "kokoro" / "voices-v1.0.bin"

_SENTENCE_END = re.compile(r"([.!?]\s+)")


def main() -> None:
    console = Console()
    if not all(p.exists() for p in (LLM_PATH, KOKORO_MODEL, KOKORO_VOICES)):
        console.print("Download models from chapter 00 first.")
        raise SystemExit(1)
    user_q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    if user_q is None:
        console.print("[dim]Recording 5s…[/]")
        audio, sr = record_seconds(5.0, config=AudioInputConfig())
        text = transcribe_samples(audio, sr, config=TranscribeConfig(download_root=str(WHISPER_ROOT)))
    else:
        text = user_q
    console.print("[bold]You:[/]", text)
    if not text.strip():
        raise SystemExit(0)

    agent = AgentCore(model_path=str(LLM_PATH))
    engine = PromptEngine()
    k = Kokoro(str(KOKORO_MODEL), str(KOKORO_VOICES))
    voice = "af_heart" if "af_heart" in k.get_voices() else k.get_voices()[0]

    buf = ""
    for piece in agent.stream_tokens(text, engine=engine, max_tokens=256):
        buf += piece
        if _SENTENCE_END.search(buf) or len(buf) > 200:
            chunk = buf.strip()
            buf = ""
            if not chunk:
                continue
            audio, _sr = k.create(chunk, voice=voice, speed=1.0)
            x = np.asarray(audio, dtype=np.float32).reshape(-1)
            sd.play(x, SAMPLE_RATE)
            sd.wait()
    if buf.strip():
        audio, _sr = k.create(buf.strip(), voice=voice, speed=1.0)
        x = np.asarray(audio, dtype=np.float32).reshape(-1)
        sd.play(x, SAMPLE_RATE)
        sd.wait()


if __name__ == "__main__":
    main()
