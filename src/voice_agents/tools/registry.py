"""Tool registry with JSON Schema via Pydantic."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, TypeAdapter


def tool_schema(model: type[BaseModel]) -> dict[str, Any]:
    """Return a JSON Schema dict for a Pydantic model."""
    return TypeAdapter(model).json_schema()


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, tuple[type[BaseModel], Callable[..., Any]]] = {}

    def register(self, name: str, params_model: type[BaseModel], fn: Callable[..., Any]) -> None:
        self._tools[name] = (params_model, fn)

    def schema_list(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for name, (model, _) in self._tools.items():
            out.append(
                {
                    "name": name,
                    "parameters": tool_schema(model),
                }
            )
        return out

    def call(self, name: str, arguments: dict[str, Any] | BaseModel) -> Any:
        if name not in self._tools:
            raise KeyError(f"unknown tool: {name}")
        model, fn = self._tools[name]
        if isinstance(arguments, BaseModel):
            args = arguments
        else:
            args = model.model_validate(arguments)
        return fn(args)
