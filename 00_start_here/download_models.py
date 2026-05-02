"""Download local model artifacts into ``models/`` (idempotent)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import httpx
from faster_whisper import WhisperModel
from huggingface_hub import hf_hub_download
from rich.console import Console
from rich.progress import BarColumn, DownloadColumn, Progress, TextColumn, TimeRemainingColumn

# Project root = parent of 00_start_here/
ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "models"
WHISPER_DIR = MODELS / "whisper"
LLM_DIR = MODELS / "llm"
KOKORO_DIR = MODELS / "kokoro"

# Kokoro v1.0 (matches kokoro-onnx docs)
KOKORO_ONNX_URL = (
    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
)
KOKORO_VOICES_URL = (
    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
)

# Qwen2.5 0.5B Q4 — small, fits tutorial machines
LLM_REPO = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"
LLM_FILE = "qwen2.5-0.5b-instruct-q4_k_m.gguf"


def _download_url(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return
    console = Console()
    with httpx.Client(follow_redirects=True, timeout=600.0) as client:
        with client.stream("GET", url) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            with Progress(
                TextColumn("[bold blue]{task.fields[filename]}"),
                BarColumn(),
                DownloadColumn(),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("dl", total=total or None, filename=dest.name)
                with open(dest, "wb") as f:
                    for chunk in r.iter_bytes(1024 * 256):
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))


def ensure_whisper(model_size: str = "tiny.en") -> None:
    """Trigger faster-whisper download into ``models/whisper``."""
    WHISPER_DIR.mkdir(parents=True, exist_ok=True)
    # Instantiating downloads converted CTranslate2 weights when missing
    WhisperModel(
        model_size,
        device="cpu",
        compute_type="int8",
        download_root=str(WHISPER_DIR),
    )


def ensure_llm() -> Path:
    LLM_DIR.mkdir(parents=True, exist_ok=True)
    path = hf_hub_download(
        repo_id=LLM_REPO,
        filename=LLM_FILE,
        local_dir=str(LLM_DIR),
    )
    return Path(path)


def ensure_kokoro() -> tuple[Path, Path]:
    KOKORO_DIR.mkdir(parents=True, exist_ok=True)
    onnx_p = KOKORO_DIR / "kokoro-v1.0.onnx"
    voices_p = KOKORO_DIR / "voices-v1.0.bin"
    _download_url(KOKORO_ONNX_URL, onnx_p)
    _download_url(KOKORO_VOICES_URL, voices_p)
    return onnx_p, voices_p


def main() -> None:
    parser = argparse.ArgumentParser(description="Download STT, LLM, and TTS models into models/")
    parser.add_argument(
        "--whisper",
        default="tiny.en",
        help="faster-whisper model id (default: tiny.en)",
    )
    args = parser.parse_args()
    console = Console()
    console.print("[bold]Downloading / verifying models under[/]", MODELS)
    try:
        console.print("… Whisper (faster-whisper):", args.whisper)
        ensure_whisper(args.whisper)
        console.print("… LLM GGUF:", LLM_REPO, LLM_FILE)
        ensure_llm()
        console.print("… Kokoro ONNX + voices")
        ensure_kokoro()
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        raise SystemExit(1) from e
    console.print("[green]All set.[/] Run: uv run python 00_start_here/run_first_voice_agent.py")


if __name__ == "__main__":
    main()
