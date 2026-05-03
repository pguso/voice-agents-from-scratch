"""Print Modal deploy instructions (used by ``voice-agent`` chapter 10 menu)."""

from __future__ import annotations


def main() -> None:
    print(
        "Chapter 10 — Modal deployment\n\n"
        "  1. uv sync --extra deploy\n"
        "  2. uv run modal setup          # if not already authenticated\n"
        "  3. uv run modal deploy 10_deployment/modal_app.py\n\n"
        "Full guide: 10_deployment/README.md\n"
        "Code walkthrough: 10_deployment/modal_chapter/CODE.md\n"
    )


if __name__ == "__main__":
    main()
