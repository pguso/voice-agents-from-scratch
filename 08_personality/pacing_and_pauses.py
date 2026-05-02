"""Split assistant text into clauses for staggered TTS (pause markers)."""

from __future__ import annotations

import re

_SPLIT = re.compile(r"(?<=[.!?])\s+")


def chunks_for_tts(text: str, max_chars: int = 120) -> list[str]:
    parts = _SPLIT.split(text.strip())
    out: list[str] = []
    buf = ""
    for p in parts:
        if len(buf) + len(p) > max_chars and buf:
            out.append(buf.strip())
            buf = p
        else:
            buf = (buf + " " + p).strip()
    if buf:
        out.append(buf)
    return out


if __name__ == "__main__":
    s = "Hello. This is one thought! And here is another — with care."
    for i, c in enumerate(chunks_for_tts(s)):
        print(f"{i}: {c}")
