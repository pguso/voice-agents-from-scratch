"""Multi-turn **voice tutor**: mic → STT → streaming LLM → Kokoro (chapter 05 glue + persona).

Loads **LLM**, **Whisper**, and **Kokoro** up front (mmap + one dummy transcribe + one dummy
``create``) so the learner spends less time waiting after they start talking. Each voice turn
reuses the same **Whisper** instance and the same **PromptEngine** so
``AgentCore.stream_tokens`` keeps **memory** across turns (like ``voice_interviewer``).

Uses a **Llama 3.x instruct** GGUF  -  see ``09_projects/llama_gguf.py``.

- Default: **multi-turn** voice loop until you say **quit** / **exit** / **goodbye** (whole
  transcript, case-insensitive) or **Ctrl+C**.
- ``--text "…"``: one **text** turn only (no mic), then exit  -  for quick tests without audio.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel
from kokoro_onnx import Kokoro
from rich.console import Console

from voice_agents.agent.agent_core import AgentCore
from voice_agents.agent.prompt_engine import PromptEngine
from voice_agents.audio.audio_output import play_float_mono
from voice_agents.audio.audio_input import AudioInputConfig, record_seconds
from voice_agents.stt.streaming_stt import TranscribeConfig, transcribe_samples

_CH09 = Path(__file__).resolve().parent.parent
if str(_CH09) not in sys.path:
    sys.path.insert(0, str(_CH09))
from llama_gguf import resolve_llama_instruct_gguf

ROOT = Path(__file__).resolve().parents[2]
WHISPER_ROOT = ROOT / "models" / "whisper"
KOKORO_MODEL = ROOT / "models" / "kokoro" / "kokoro-v1.0.onnx"
KOKORO_VOICES = ROOT / "models" / "kokoro" / "voices-v1.0.bin"

_SENTENCE_END = re.compile(r"([.!?]\s+)")


def _play_kokoro(k: Kokoro, voice: str, text: str) -> None:
    audio, sr = k.create(text, voice=voice, speed=1.0)
    play_float_mono(audio, int(sr))


def _stream_tutor_to_speakers(
    agent: AgentCore,
    engine: PromptEngine,
    k: Kokoro,
    voice: str,
    user_text: str,
    *,
    console: Console,
) -> None:
    buf = ""
    for piece in agent.stream_tokens(user_text, engine=engine, max_tokens=256):
        buf += piece
        while True:
            m = _SENTENCE_END.search(buf)
            if not m:
                break
            chunk = buf[: m.end()].strip()
            buf = buf[m.end() :]
            if chunk:
                _play_kokoro(k, voice, chunk)
        if len(buf) > 200:
            chunk = buf.strip()
            buf = ""
            if chunk:
                _play_kokoro(k, voice, chunk)
    if buf.strip():
        _play_kokoro(k, voice, buf.strip())


def _preload_everything(
    *,
    console: Console,
    llm_path: Path,
    tcfg: TranscribeConfig,
    audio_cfg: AudioInputConfig,
) -> tuple[AgentCore, PromptEngine, Kokoro, str, WhisperModel]:
    """Load Llama + Whisper + Kokoro once; warm caches so the first real turn is snappier."""
    console.print("[dim]Loading Whisper (tiny.en)…[/]")
    whisper = WhisperModel(
        tcfg.model_size,
        device=tcfg.device,
        compute_type=tcfg.compute_type,
        download_root=tcfg.download_root,
    )
    # Compile / mmap CTranslate2 path once (cheap audio; transcript may be empty).
    warm_audio = np.zeros(int(0.25 * audio_cfg.sample_rate), dtype=np.float32)
    transcribe_samples(
        warm_audio,
        audio_cfg.sample_rate,
        config=tcfg,
        whisper_model=whisper,
    )

    console.print("[dim]Loading Llama (GGUF mmap)…[/]")
    agent = AgentCore(model_path=str(llm_path), chat_template="llama3", n_ctx=8192)
    agent.preload()

    engine = PromptEngine(
        system_prompt=(
            "You are a patient tutor. Give a short explanation then one practice question. "
            "Keep replies under three sentences. Remember what the learner already asked "
            "when they follow up."
        )
    )

    console.print("[dim]Loading Kokoro…[/]")
    k = Kokoro(str(KOKORO_MODEL), str(KOKORO_VOICES))
    voice = "af_heart" if "af_heart" in k.get_voices() else k.get_voices()[0]
    # Warm ONNX session (first ``create`` is slower).
    k.create("Hi.", voice=voice, speed=1.0)

    console.print("[green]Ready  - [/] first recording should feel faster than a cold start.")
    return agent, engine, k, voice, whisper


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Multi-turn voice tutor (preload LLM+STT+TTS; stream LLM → Kokoro)."
    )
    ap.add_argument(
        "--text",
        default=None,
        help="Single text turn (no mic), then exit  -  for tests without audio.",
    )
    ap.add_argument(
        "--seconds",
        type=float,
        default=5.0,
        help="Seconds of mic capture per voice turn (default: 5).",
    )
    args = ap.parse_args()

    console = Console()
    if not all(path.exists() for path in (KOKORO_MODEL, KOKORO_VOICES)):
        console.print("Download Kokoro assets from chapter 00 first.")
        raise SystemExit(1)
    llm_path = resolve_llama_instruct_gguf(ROOT)
    if llm_path is None:
        console.print(
            "[red]No Llama 3.x instruct GGUF under models/llm/.[/] Add one of the filenames in "
            "[cyan]09_projects/llama_gguf.py[/] (e.g. [bold]Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf[/])."
        )
        raise SystemExit(1)

    tcfg = TranscribeConfig(download_root=str(WHISPER_ROOT))
    audio_cfg = AudioInputConfig()

    agent, engine, k, voice, whisper = _preload_everything(
        console=console,
        llm_path=llm_path,
        tcfg=tcfg,
        audio_cfg=audio_cfg,
    )

    if args.text is not None:
        text = args.text.strip()
        if not text:
            raise SystemExit(0)
        console.print("[bold]You:[/]", text)
        console.print("[dim]Streaming reply…[/]")
        _stream_tutor_to_speakers(agent, engine, k, voice, text, console=console)
        return

    console.print(
        "\n[bold]Voice tutor[/]  -  multi-turn. After each reply, we record again.\n"
        "[dim]Say [bold]quit[/], [bold]exit[/], or [bold]goodbye[/] alone to stop. "
        f"Recording [bold]{args.seconds:g}[/] s per turn. Ctrl+C anytime.[/]\n"
    )

    turn = 0
    while True:
        turn += 1
        console.print(f"\n[dim]Turn {turn}  -  recording {args.seconds:g} s… speak now.[/]")
        audio, sr = record_seconds(args.seconds, config=audio_cfg)
        text = transcribe_samples(audio, sr, config=tcfg, whisper_model=whisper).strip()
        console.print("[bold]You:[/]", text or "[dim](no speech detected)[/]")
        if not text:
            console.print("[dim]Try again, or say quit to leave.[/]")
            continue
        low = text.lower()
        if low in {"quit", "exit", "goodbye"}:
            console.print("[dim]Bye![/]")
            break

        console.print("[dim]Tutor (streaming)…[/]")
        _stream_tutor_to_speakers(agent, engine, k, voice, text, console=console)


if __name__ == "__main__":
    main()
