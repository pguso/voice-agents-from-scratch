"""Register tools and invoke by name with JSON-like dict args."""

from __future__ import annotations

import sys
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

from rich.console import Console
from rich.pretty import pprint

from voice_agents.tools.registry import ToolRegistry

from calculator_tool import CalcParams, calculator_eval
from time_tool import TimeParams, time_now
from weather_tool import WeatherParams, weather_current_c
from web_search_tool import SearchParams, web_search_lite


def build_registry() -> ToolRegistry:
    r = ToolRegistry()
    r.register("weather", WeatherParams, lambda m: weather_current_c(m))
    r.register("search", SearchParams, lambda m: web_search_lite(m))
    r.register("calc", CalcParams, lambda m: calculator_eval(m))
    r.register("time", TimeParams, lambda m: time_now(m))
    return r


def main() -> None:
    console = Console()
    reg = build_registry()
    console.print("[bold]Registered tools:[/]")
    pprint(reg.schema_list())

    demo = [
        ("weather", {"latitude": 52.52, "longitude": 13.41}),
        ("calc", {"expression": "21 * 2"}),
        ("time", {"fmt": "%H:%M"}),
    ]
    for name, args in demo:
        out = reg.call(name, args)
        console.print(f"[green]{name}[/] => {out}")


if __name__ == "__main__":
    main()
