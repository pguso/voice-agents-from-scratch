"""Dev view: print transcript + mock agent state (extend with your session fields)."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

from voice_agents.agent.session_store import SessionStore


def main() -> None:
    console = Console()
    store = SessionStore(ttl_s=60.0)
    sid = "dev"
    store.update(sid, last_transcript="hello world", state="LISTENING")
    state = store.get(sid)
    console.print(
        Panel(
            f"[bold]last_transcript[/] {state.get('last_transcript')}\n"
            f"[bold]state[/] {state.get('state')}",
            title="echo_mode",
        )
    )


if __name__ == "__main__":
    main()
