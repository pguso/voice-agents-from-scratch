"""Minimal REPL: stdin → LLM → stdout (debug the brain without audio)."""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console

from voice_agents.agent.agent_core import AgentCore
from voice_agents.agent.prompt_engine import PromptEngine

ROOT = Path(__file__).resolve().parents[1]
LLM = ROOT / "models" / "llm" / "qwen2.5-0.5b-instruct-q4_k_m.gguf"


def main() -> None:
    console = Console()
    if not LLM.is_file():
        console.print("Download LLM first.")
        raise SystemExit(1)
    agent = AgentCore(model_path=str(LLM))
    engine = PromptEngine()
    if not sys.stdin.isatty():
        text = sys.stdin.read().strip()
        print(agent.complete(text, engine=engine))
        return
    console.print("[dim]REPL — empty line to quit[/]")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            break
        print(agent.complete(line, engine=engine))


if __name__ == "__main__":
    main()
