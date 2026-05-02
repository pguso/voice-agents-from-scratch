"""Speak once → transcribe → LLM reply → Kokoro TTS → play (blocking pipeline)."""

from __future__ import annotations

import time
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm

from voice_agents.agent.agent_core import AgentCore
from voice_agents.agent.prompt_engine import PromptEngine
from voice_agents.audio.audio_input import AudioInputConfig, record_seconds, save_wav
from voice_agents.audio.audio_output import play_wav_file
from voice_agents.stt.streaming_stt import TranscribeConfig, transcribe_samples
from voice_agents.tts.streaming_tts import TTSConfig, pick_voice, synthesize_to_wav

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"
WHISPER_ROOT = MODELS / "whisper"
LLM_PATH = MODELS / "llm" / "LFM2.5-350M-Q6_K.gguf"
#"qwen2.5-0.5b-instruct-q4_k_m.gguf"
KOKORO_MODEL = MODELS / "kokoro" / "kokoro-v1.0.onnx"
KOKORO_VOICES = MODELS / "kokoro" / "voices-v1.0.bin"
TMP_WAV = ROOT / "tmp" / "user_utterance.wav"
OUT_WAV = ROOT / "tmp" / "response.wav"


def main() -> None:
    console = Console()
    for p in (LLM_PATH, KOKORO_MODEL, KOKORO_VOICES):
        if not p.exists():
            console.print(
                f"[red]Missing model file:[/] {p}\n"
                "Run: [bold]uv run python 00_start_here/download_models.py[/]"
            )
            raise SystemExit(1)

    engine = PromptEngine()
    agent = AgentCore(model_path=str(LLM_PATH), n_ctx=4096, verbose=False)
    console.print("[dim]Loading language model (llama.cpp)…[/]")
    agent.preload()

    if not Confirm.ask("Record ~5s of speech when you are ready", default=True):
        raise SystemExit(0)

    console.print("[dim]Recording 5 seconds… speak now.[/]")
    audio, sr = record_seconds(5.0, config=AudioInputConfig(sample_rate=16_000))
    # Start of pipeline latency: recording has finished; mic buffer is in hand.
    t_after_recording = time.perf_counter()
    TMP_WAV.parent.mkdir(parents=True, exist_ok=True)
    save_wav(TMP_WAV, audio, sr)

    stt_cfg = TranscribeConfig(
        model_size="tiny.en",
        download_root=str(WHISPER_ROOT),
        language="en",
    )
    text = transcribe_samples(audio, sr, config=stt_cfg)
    console.print("[bold]You said:[/]", text or "[dim](empty)[/]")
    if not text.strip():
        console.print("[yellow]No speech detected; exiting.[/]")
        raise SystemExit(0)

    reply = agent.complete(text, engine=engine, max_tokens=256, temperature=0.7)
    console.print("[bold]Assistant:[/]", reply)

    tts_cfg = TTSConfig(
        model_path=str(KOKORO_MODEL),
        voices_path=str(KOKORO_VOICES),
        voice="af_heart",
        speed=1.0,
    )
    tts_cfg.voice = pick_voice(tts_cfg, tts_cfg.voice)
    synthesize_to_wav(reply, OUT_WAV, config=tts_cfg)

    t_assistant_speaking: list[float | None] = [None]

    def mark_assistant_audio_start() -> None:
        t_assistant_speaking[0] = time.perf_counter()

    console.print("[dim]Playing response…[/]")
    play_wav_file(OUT_WAV, on_playback_start=mark_assistant_audio_start)

    t_start = t_assistant_speaking[0]
    if t_start is None:
        raise RuntimeError("playback start time not recorded")
    latency_s = t_start - t_after_recording
    latency_ms = latency_s * 1000.0

    console.print()
    console.print(
        "[bold]Latency (recording finished → assistant audio started):[/] "
        f"{latency_s:.2f} s ({latency_ms:.0f} ms)"
    )
    console.print(
        "[dim]In live conversation, comfortable gaps between turns are often about "
        "200–700 ms; responding inside ~250 ms can feel very snappy, while waits "
        "over ~1 s tend to feel sluggish. This script runs STT, an LLM, and TTS "
        "sequentially, so end-to-end time is usually much longer than human "
        "turn-taking alone — production voice stacks overlap stages and stream "
        "audio to approach conversational pacing.[/]"
    )


if __name__ == "__main__":
    main()
