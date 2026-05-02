"""Blocking pipeline (same stages as chapter 00; configurable durations)."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm

from voice_agents.agent.agent_core import AgentCore
from voice_agents.agent.prompt_engine import PromptEngine
from voice_agents.audio.audio_input import AudioInputConfig, record_seconds, save_wav
from voice_agents.audio.audio_output import play_wav_file
from voice_agents.stt.streaming_stt import TranscribeConfig, transcribe_samples
from voice_agents.tts.streaming_tts import TTSConfig, pick_voice, synthesize_to_wav

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"
WHISPER_ROOT = MODELS / "whisper"
LLM_PATH = MODELS / "llm" / "qwen2.5-0.5b-instruct-q4_k_m.gguf"
KOKORO_MODEL = MODELS / "kokoro" / "kokoro-v1.0.onnx"
KOKORO_VOICES = MODELS / "kokoro" / "voices-v1.0.bin"
OUT_WAV = ROOT / "tmp" / "blocking_response.wav"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=5.0, help="Recording length")
    args = ap.parse_args()
    console = Console()
    for p in (LLM_PATH, KOKORO_MODEL, KOKORO_VOICES):
        if not p.exists():
            console.print(f"Missing {p} — run download_models.")
            raise SystemExit(1)
    if not Confirm.ask(f"Record {args.seconds}s?", default=True):
        raise SystemExit(0)
    audio, sr = record_seconds(args.seconds, config=AudioInputConfig())
    save_wav(ROOT / "tmp/blocking_input.wav", audio, sr)
    stt = TranscribeConfig(download_root=str(WHISPER_ROOT))
    text = transcribe_samples(audio, sr, config=stt)
    console.print("[bold]You:[/]", text)
    if not text.strip():
        raise SystemExit(0)
    reply = AgentCore(model_path=str(LLM_PATH)).complete(
        text, engine=PromptEngine(), max_tokens=256
    )
    console.print("[bold]Assistant:[/]", reply)
    cfg = TTSConfig(str(KOKORO_MODEL), str(KOKORO_VOICES), voice="af_heart")
    cfg.voice = pick_voice(cfg, cfg.voice)
    synthesize_to_wav(reply, OUT_WAV, config=cfg)
    play_wav_file(OUT_WAV)


if __name__ == "__main__":
    main()
