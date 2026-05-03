"""Resolve a Llama 3.x **instruct** GGUF under ``models/llm/`` for chapter 09 capstones.

Filenames are common Hugging Face / bartowski releases. Add your own file name to
``LLAMA_INSTRUCT_FILENAMES`` if you use a different quant or vendor.

To fetch the default file with one command, run from the repo root::

    uv run python 09_projects/download_llama_8b_instruct_gguf.py
"""

from __future__ import annotations

from pathlib import Path

# Tried in order; all expect the Meta Llama 3 instruct chat format (see ``AgentCore.chat_template="llama3"``).
LLAMA_INSTRUCT_FILENAMES = (
    "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    "Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    "Meta-Llama-3-8B-Instruct-Q4_K_M.gguf",
    "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
)


def resolve_llama_instruct_gguf(repo_root: Path) -> Path | None:
    d = repo_root / "models" / "llm"
    for name in LLAMA_INSTRUCT_FILENAMES:
        p = d / name
        if p.is_file():
            return p
    return None
