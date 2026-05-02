"""Capstone sketch: tutor-style system prompt + one text turn (extend with STT/TTS from ch 05)."""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console

from voice_agents.agent.agent_core import AgentCore
from voice_agents.agent.prompt_engine import PromptEngine

ROOT = Path(__file__).resolve().parents[2]
LLM = ROOT / "models" / "llm" / "qwen2.5-0.5b-instruct-q4_k_m.gguf"


def main() -> None:
    console = Console()
    if not LLM.is_file():
        console.print("Download models first (chapter 00).")
        raise SystemExit(1)
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Explain what a list comprehension is."
    eng = PromptEngine(
        system_prompt="You are a patient tutor. Give a short explanation then one practice question."
    )
    out = AgentCore(model_path=str(LLM)).complete(q, engine=eng, max_tokens=256)
    console.print(out)


if __name__ == "__main__":
    main()
