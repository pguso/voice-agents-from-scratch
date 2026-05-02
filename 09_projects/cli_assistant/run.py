"""Capstone sketch: CLI-focused assistant (tools exercise — plug chapter 07 registry)."""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt

from voice_agents.agent.agent_core import AgentCore
from voice_agents.agent.prompt_engine import PromptEngine

ROOT = Path(__file__).resolve().parents[2]
LLM = ROOT / "models" / "llm" / "qwen2.5-0.5b-instruct-q4_k_m.gguf"


def main() -> None:
    console = Console()
    if not LLM.is_file():
        console.print("Download models first.")
        raise SystemExit(1)
    agent = AgentCore(model_path=str(LLM))
    engine = PromptEngine(
        system_prompt="You help with shell and Python tasks. Be concise. If unsure, say so."
    )
    console.print("[dim]CLI assistant — type quit to exit[/]")
    while True:
        q = Prompt.ask(">")
        if q.strip().lower() in {"quit", "exit"}:
            break
        r = agent.complete(q, engine=engine, max_tokens=256)
        console.print(r)


if __name__ == "__main__":
    main()
