"""Download ``Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf`` into ``models/llm/`` for chapter 09.

Uses ``huggingface_hub`` (same stack as ``00_start_here/download_models.py``). Default
weights come from the **bartowski** GGUF repo (no Meta account gating).

Run from the **repository root**:

    uv run python 09_projects/download_llama_8b_instruct_gguf.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import hf_hub_download
from rich.console import Console

ROOT = Path(__file__).resolve().parent.parent
LLM_DIR = ROOT / "models" / "llm"
DEFAULT_REPO = "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF"
DEFAULT_FILE = "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Download Llama 3.1 8B Instruct Q4_K_M GGUF into models/llm/ (chapter 09)."
    )
    ap.add_argument(
        "--repo",
        default=DEFAULT_REPO,
        help=f"Hugging Face repo id (default: {DEFAULT_REPO}).",
    )
    ap.add_argument(
        "--filename",
        default=DEFAULT_FILE,
        help=f"GGUF filename inside the repo (default: {DEFAULT_FILE}).",
    )
    args = ap.parse_args()

    console = Console()
    LLM_DIR.mkdir(parents=True, exist_ok=True)
    console.print(
        f"[bold]Downloading[/] [cyan]{args.filename}[/] from [cyan]{args.repo}[/]\n"
        f"into [cyan]{LLM_DIR}[/] …"
    )
    path = hf_hub_download(
        repo_id=args.repo,
        filename=args.filename,
        local_dir=str(LLM_DIR),
    )
    console.print(f"[green]OK[/]  -  {path}")
    console.print(
        "[dim]Then run e.g. [cyan]uv run python 09_projects/therapist_bot/therapist_bot.py[/][/]"
    )


if __name__ == "__main__":
    main()
