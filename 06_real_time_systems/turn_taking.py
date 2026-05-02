"""Finite-state view of *listening* vs *speaking* (educational, no audio)."""

from __future__ import annotations

from enum import Enum, auto

from rich.console import Console


class TurnState(Enum):
    LISTENING = auto()
    THINKING = auto()
    SPEAKING = auto()


def main() -> None:
    console = Console()
    s = TurnState.LISTENING
    console.print(f"Start state: {s.name}")
    for ev in ("speech_end", "reply_ready", "playback_end"):
        if s == TurnState.LISTENING and ev == "speech_end":
            s = TurnState.THINKING
        elif s == TurnState.THINKING and ev == "reply_ready":
            s = TurnState.SPEAKING
        elif s == TurnState.SPEAKING and ev == "playback_end":
            s = TurnState.LISTENING
        console.print(f"After {ev}: {s.name}")


if __name__ == "__main__":
    main()
