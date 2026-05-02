"""Lightweight error reporting for mic / STT / TTS stages (no retries)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from rich.console import Console


class Stage(str, Enum):
    MIC = "microphone"
    STT = "stt"
    LLM = "llm"
    TTS = "tts"
    PLAYBACK = "playback"


@dataclass
class FallbackReport:
    stage: Stage
    message: str
    detail: Any = None


def log_failure(console: Console | None, report: FallbackReport) -> None:
    c = console or Console()
    extra = f" — {report.detail!r}" if report.detail is not None else ""
    c.print(f"[red][{report.stage.value}][/] {report.message}{extra}")
