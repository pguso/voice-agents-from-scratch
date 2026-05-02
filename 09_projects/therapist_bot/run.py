"""Empathetic short replies — pair with safety filters in production."""

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
        console.print("Download models first.")
        raise SystemExit(1)
    user = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "I'm feeling overwhelmed today."
    eng = PromptEngine(
        system_prompt=(
            "You are a supportive listener. Reflect briefly, avoid medical claims, "
            "and suggest professional help for crises."
        )
    )
    out = AgentCore(model_path=str(LLM)).complete(user, engine=eng, max_tokens=200)
    console.print(out)


if __name__ == "__main__":
    main()
