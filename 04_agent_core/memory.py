"""PromptEngine memory lines across multiple turns (still in-process)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt

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
    engine = PromptEngine(system_prompt="You are a concise assistant. Remember facts the user states.")
    console.print("[dim]Type 'quit' to exit.[/]")
    while True:
        user = Prompt.ask("You")
        if user.strip().lower() in {"quit", "exit"}:
            break
        reply = agent.complete(user, engine=engine, max_tokens=256)
        console.print(f"[bold]Assistant[/] {reply}")


if __name__ == "__main__":
    main()
