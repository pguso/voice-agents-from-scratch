"""Stream ``AgentCore.stream_tokens`` to the Rich console; return full reply string.

``AgentCore`` still appends **User** / **Assistant** lines to ``engine.memory_lines`` after
the stream finishes (same as ``complete``).
"""

from __future__ import annotations

from rich.console import Console

from voice_agents.agent.agent_core import AgentCore
from voice_agents.agent.prompt_engine import PromptEngine


def stream_reply_to_console(
    agent: AgentCore,
    user_text: str,
    *,
    engine: PromptEngine,
    console: Console,
    max_tokens: int = 256,
    temperature: float = 0.7,
    dim_lead: str | None = None,
    bold_label: str | None = None,
) -> str:
    """Print tokens as they arrive; return the full stripped assistant text."""
    if dim_lead:
        console.print(dim_lead)
    if bold_label:
        console.print(f"[bold]{bold_label}[/] ", end="")
    parts: list[str] = []
    for piece in agent.stream_tokens(
        user_text,
        engine=engine,
        max_tokens=max_tokens,
        temperature=temperature,
    ):
        parts.append(piece)
        console.print(piece, end="")
    console.print()
    return "".join(parts).strip()
