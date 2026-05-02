"""Text-only LLM turn (no audio) using the same Qwen chat template as the voice loop."""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console

from voice_agents.agent.agent_core import AgentCore
from voice_agents.agent.prompt_engine import PromptEngine

ROOT = Path(__file__).resolve().parents[1]
LLM = ROOT / "models" / "llm" / "qwen2.5-0.5b-instruct-q4_k_m.gguf"

if __name__ == "__main__":
    console = Console()
    if not LLM.is_file():
        console.print("Run 00_start_here/download_models.py first.")
        raise SystemExit(1)
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is 2+2? Reply in one short sentence."
    agent = AgentCore(model_path=str(LLM))
    engine = PromptEngine()
    out = agent.complete(q, engine=engine, max_tokens=128)
    console.print(out)
