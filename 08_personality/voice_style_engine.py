"""Map simple style tags to system prompt suffixes."""

from __future__ import annotations

from voice_agents.agent.prompt_engine import PromptEngine

STYLES: dict[str, str] = {
    "kind": "Be warm and encouraging.",
    "concise": "Use at most two short sentences.",
    "teacher": "Explain briefly, then give one concrete example.",
}


def engine_with_style(base_system: str, style: str) -> PromptEngine:
    extra = STYLES.get(style, "")
    return PromptEngine(system_prompt=f"{base_system}\n\n{extra}".strip())


if __name__ == "__main__":
    e = engine_with_style("You are a helpful assistant.", "concise")
    print(e.build_user_message("What is asyncio?"))
