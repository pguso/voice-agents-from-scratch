# Chapter 07 — Tools

**Goals:** **Pydantic**-typed parameters, **JSON Schema** via `ToolRegistry`, and example tools (weather, search, calc, time).

- `tool_router.py` — builds a registry and demo calls.
- `weather_tool.py`, `web_search_tool.py`, `calculator_tool.py`, `time_tool.py` — example implementations.

Wiring **LLM → tool JSON → execute** is model-specific; small local models need tight prompts. Extend `04_agent_core` with a tool-calling loop as an exercise.

**Next:** [08_personality/](../08_personality/).
