"""Sketch of full-duplex: while speaking, a mic monitor thread could trigger *cancel*."""

from __future__ import annotations

import threading
import time

from rich.console import Console


def main() -> None:
    console = Console()
    cancel = threading.Event()

    def monitor() -> None:
        # placeholder: would run VAD / STT partials on mic stream
        time.sleep(0.5)
        console.print("[dim]Monitor: user started speaking → cancel TTS[/]")
        cancel.set()

    threading.Thread(target=monitor, daemon=True).start()
    for i in range(5):
        if cancel.is_set():
            console.print("Stopped early.")
            return
        console.print(f"TTS chunk {i}")
        time.sleep(0.4)
    console.print("Finished without interrupt.")


if __name__ == "__main__":
    main()
