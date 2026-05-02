"""Log pipeline stages (text-only): user → prompt preview → model reply."""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console

from voice_agents.agent.agent_core import AgentCore, qwen25_chat_prompt
from voice_agents.agent.prompt_engine import PromptEngine

ROOT = Path(__file__).resolve().parents[1]
LLM = ROOT / "models" / "llm" / "qwen2.5-0.5b-instruct-q4_k_m.gguf"

if __name__ == "__main__":
    console = Console()
    if not LLM.is_file():
        console.print("Download LLM first.")
        raise SystemExit(1)
    user = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Say hello in two words."
    engine = PromptEngine()
    full_user = engine.build_user_message(user)
    prompt = qwen25_chat_prompt(engine.system_prompt, full_user)
    console.print("[bold]Prompt tail (last 400 chars):[/]")
    console.print(prompt[-400:])
    agent = AgentCore(model_path=str(LLM))
    out = agent.complete(user, engine=engine)
    console.print("[bold]Reply:[/]", out)
