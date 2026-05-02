"""Color-coded stage timings for the blocking voice pipeline."""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
from rich.console import Console
from rich.table import Table

from voice_agents.agent.agent_core import AgentCore
from voice_agents.agent.prompt_engine import PromptEngine
from voice_agents.audio.audio_input import AudioInputConfig, record_seconds
from voice_agents.audio.audio_output import play_float_mono
from voice_agents.stt.streaming_stt import TranscribeConfig, transcribe_samples
from voice_agents.tts.streaming_tts import TTSConfig, pick_voice, synthesize_to_wav

ROOT = Path(__file__).resolve().parents[1]
WHISPER_ROOT = ROOT / "models" / "whisper"
LLM_PATH = ROOT / "models" / "llm" / "qwen2.5-0.5b-instruct-q4_k_m.gguf"
KOKORO_MODEL = ROOT / "models" / "kokoro" / "kokoro-v1.0.onnx"
KOKORO_VOICES = ROOT / "models" / "kokoro" / "voices-v1.0.bin"
OUT = ROOT / "tmp" / "latency_response.wav"


def main() -> None:
    console = Console()
    rows: list[tuple[str, float, str]] = []
    t_wall = time.perf_counter()

    t0 = time.perf_counter()
    audio, sr = record_seconds(3.0, config=AudioInputConfig())
    rows.append(("Mic capture (fixed 3s)", time.perf_counter() - t0, "green"))

    t0 = time.perf_counter()
    stt = TranscribeConfig(download_root=str(WHISPER_ROOT))
    text = transcribe_samples(audio, sr, config=stt)
    rows.append(("STT", time.perf_counter() - t0, "cyan"))

    t0 = time.perf_counter()
    reply = AgentCore(model_path=str(LLM_PATH)).complete(
        text or "hello", engine=PromptEngine(), max_tokens=128
    )
    rows.append(("LLM", time.perf_counter() - t0, "magenta"))

    t0 = time.perf_counter()
    cfg = TTSConfig(str(KOKORO_MODEL), str(KOKORO_VOICES))
    cfg.voice = pick_voice(cfg, "af_heart")
    synthesize_to_wav(reply, OUT, config=cfg)
    rows.append(("TTS (WAV)", time.perf_counter() - t0, "yellow"))

    t0 = time.perf_counter()
    import soundfile as sf

    data, ssr = sf.read(OUT, dtype="float32")
    play_float_mono(np.squeeze(data), int(ssr))
    rows.append(("Playback", time.perf_counter() - t0, "blue"))

    total = time.perf_counter() - t_wall
    tb = Table(title="Latency stages")
    tb.add_column("Stage", style="bold")
    tb.add_column("Seconds", justify="right")
    for name, sec, color in rows:
        tb.add_row(f"[{color}]{name}[/]", f"{sec:.3f}")
    tb.add_row("[bold]Wall total[/]", f"{total:.3f}")
    console.print(tb)


if __name__ == "__main__":
    main()
