"""System / user prompt assembly with optional memory context."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PromptEngine:
    system_prompt: str = "You are a helpful, concise voice assistant."
    memory_lines: list[str] = field(default_factory=list)

    def add_memory(self, line: str) -> None:
        self.memory_lines.append(line)
        if len(self.memory_lines) > 20:
            self.memory_lines = self.memory_lines[-20:]

    def build_user_message(self, user_text: str) -> str:
        if not self.memory_lines:
            return user_text
        ctx = "\n".join(self.memory_lines)
        return f"Context from earlier in the conversation:\n{ctx}\n\nUser says:\n{user_text}"
