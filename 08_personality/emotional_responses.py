"""Keyword-based tone hint (toy example — real sentiment needs a classifier)."""

from __future__ import annotations

from voice_agents.agent.prompt_engine import PromptEngine


def hint_from_text(user: str) -> str:
    low = user.lower()
    if any(w in low for w in ("sad", "sorry", "worried")):
        return "Respond with empathy and reassurance."
    if any(w in low for w in ("great", "awesome", "thanks")):
        return "Match the user's positive energy briefly."
    return "Stay neutral and helpful."


if __name__ == "__main__":
    user = "I'm worried about the deadline."
    pe = PromptEngine(
        system_prompt="You are a supportive colleague.\n\n" + hint_from_text(user)
    )
    print(pe.system_prompt)
