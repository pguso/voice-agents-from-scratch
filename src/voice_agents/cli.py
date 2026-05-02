"""Typer + questionary entrypoint: pick a chapter script to run."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import questionary
import typer
from rich.console import Console

app = typer.Typer(add_completion=False)
console = Console()

ROOT = Path(__file__).resolve().parents[2]

_CHAPTERS: list[tuple[str, str]] = [
    ("00 — First voice agent", "00_start_here/run_first_voice_agent.py"),
    ("00 — Download models", "00_start_here/download_models.py"),
    ("01 — Mic (3s record)", "01_audio_io/mic_input.py"),
    ("01 — Play WAV", "01_audio_io/speaker_output.py"),
    ("05 — Blocking voice loop", "05_full_voice_loop/blocking_voice_agent.py"),
    ("05 — Latency debug", "05_full_voice_loop/debug_latency.py"),
    ("10 — WebSocket server", "10_deployment/websocket_server.py"),
]


def _interactive_menu() -> None:
    choice = questionary.select(
        "Which example do you want to run?",
        choices=[c[0] for c in _CHAPTERS],
    ).ask()
    if not choice:
        raise SystemExit(0)
    rel = next(p for t, p in _CHAPTERS if t == choice)
    script = ROOT / rel
    if not script.is_file():
        console.print(f"[red]Missing:[/] {script}")
        raise SystemExit(1)
    console.print(f"[dim]Running {script}…[/]")
    r = subprocess.run([sys.executable, str(script)], cwd=str(ROOT))
    raise SystemExit(r.returncode)


@app.callback(invoke_without_command=True)
def cli(ctx: typer.Context) -> None:
    """Voice agents from scratch — tutorial launcher."""
    if ctx.invoked_subcommand is None:
        _interactive_menu()


@app.command("start")
def start_cmd() -> None:
    """Same as running ``voice-agent`` with no args (interactive menu)."""
    _interactive_menu()


def main() -> None:
    """Console script entry (``voice-agent`` / ``uv run voice-agent``)."""
    app()


if __name__ == "__main__":
    main()
