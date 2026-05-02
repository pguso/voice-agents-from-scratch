"""Return local time string."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class TimeParams(BaseModel):
    fmt: str = "%Y-%m-%d %H:%M:%S"


def time_now(params: TimeParams) -> str:
    return datetime.now().strftime(params.fmt)


if __name__ == "__main__":
    print(time_now(TimeParams()))
