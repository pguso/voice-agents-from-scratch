"""Very small HTML fetch + tag strip — **not** a production search API."""

from __future__ import annotations

import re

import httpx
from pydantic import BaseModel, Field


class SearchParams(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")


def web_search_lite(params: SearchParams) -> str:
    """Return first ~400 chars of DuckDuckGo HTML lite result (fragile)."""
    url = "https://lite.duckduckgo.com/lite/"
    r = httpx.post(
        url,
        data={"q": params.query},
        headers={"User-Agent": "voice-agents-tutorial/0.1"},
        timeout=15.0,
        follow_redirects=True,
    )
    r.raise_for_status()
    text = re.sub(r"<[^>]+>", " ", r.text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:400]


if __name__ == "__main__":
    print(web_search_lite(SearchParams(query="python asyncio")))
