"""In-memory session store with TTL."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionStore:
    ttl_s: float = 3600.0
    _sessions: dict[str, dict[str, Any]] = field(default_factory=dict)
    _updated: dict[str, float] = field(default_factory=dict)

    def get(self, session_id: str) -> dict[str, Any]:
        now = time.monotonic()
        ts = self._updated.get(session_id)
        if ts is not None and now - ts > self.ttl_s:
            self._sessions.pop(session_id, None)
            self._updated.pop(session_id, None)
            return {}
        return dict(self._sessions.get(session_id, {}))

    def set(self, session_id: str, data: dict[str, Any]) -> None:
        self._sessions[session_id] = data
        self._updated[session_id] = time.monotonic()

    def update(self, session_id: str, **kwargs: Any) -> None:
        cur = self.get(session_id)
        cur.update(kwargs)
        self.set(session_id, cur)

    def touch(self, session_id: str) -> None:
        if session_id in self._sessions:
            self._updated[session_id] = time.monotonic()

    def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
        self._updated.pop(session_id, None)
