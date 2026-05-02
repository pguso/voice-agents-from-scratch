"""Illustrates editing system prompts and memory without changing model weights."""

from __future__ import annotations

from voice_agents.agent.prompt_engine import PromptEngine


def main() -> None:
    pe = PromptEngine(system_prompt="Answer like a pirate.")
    pe.add_memory("User said they like sailing.")
    msg = pe.build_user_message("Suggest a weekend hobby.")
    print("Built user message preview:\n---")
    print(msg)
    print("---")


if __name__ == "__main__":
    main()
