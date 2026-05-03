"""Supportive-listener REPL with a **toy** keyword hint mutating system text each turn.

**Not** therapy, crisis support, or medical advice  -  a teaching sketch only.

Uses a **Llama 3.x instruct** GGUF (``AgentCore.chat_template="llama3"``); see
``09_projects/llama_gguf.py`` for accepted filenames.

The ``hint_from_text`` function matches
``08_personality/emotional_responses/emotional_responses.py`` (copy here so you see
per-turn ``engine.system_prompt = ...`` without import path tricks).
"""

from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt

from voice_agents.agent.agent_core import AgentCore
from voice_agents.agent.prompt_engine import PromptEngine

_CH09 = Path(__file__).resolve().parent.parent
if str(_CH09) not in sys.path:
    sys.path.insert(0, str(_CH09))
from llama_gguf import resolve_llama_instruct_gguf
from stream_util import stream_reply_to_console

ROOT = Path(__file__).resolve().parents[2]

# Base boundaries (see also full emotional_responses demo in chapter 08)
BASE_PERSONA = (
    "You are a supportive listener. Reflect briefly, avoid medical claims, "
    "and suggest professional help if a crisis is mentioned."
)


def hint_from_text(user: str) -> str:
    # Copied from 08_personality/emotional_responses/emotional_responses.py
    low = user.lower()
    if any(w in low for w in ("sad", "sorry", "worried")):
        return "Respond with empathy and reassurance."
    if any(w in low for w in ("great", "awesome", "thanks")):
        return "Match the user's positive energy briefly."
    return "Stay neutral and helpful."


def main() -> None:
    console = Console()
    llm_path = resolve_llama_instruct_gguf(ROOT)
    if llm_path is None:
        console.print(
            "[red]No Llama 3.x instruct GGUF under models/llm/.[/] See [cyan]09_projects/llama_gguf.py[/]."
        )
        raise SystemExit(1)

    agent = AgentCore(model_path=str(llm_path), chat_template="llama3", n_ctx=8192)
    engine = PromptEngine(system_prompt=BASE_PERSONA)
    console.print(
        "[dim]Listener sketch  -  not a substitute for real support. "
        "Empty line, [bold]quit[/], or [bold]exit[/] to stop. "
        "Watch the [dim](hint -> …)[/] line each turn; assistant streams.[/]"
    )
    while True:
        user = Prompt.ask("You")
        if not user.strip() or user.strip().lower() in {"quit", "exit"}:
            break
        hint = hint_from_text(user)
        engine.system_prompt = f"{BASE_PERSONA}\n\n{hint}"
        console.print(f"[dim](hint -> {hint})[/]")
        stream_reply_to_console(
            agent,
            user,
            engine=engine,
            console=console,
            max_tokens=180,
            temperature=0.5,
            bold_label="Assistant",
        )


if __name__ == "__main__":
    main()
