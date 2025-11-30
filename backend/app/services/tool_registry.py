from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence

import logging

from app.tools.base import ToolDefinition


class ToolNotRegisteredError(ValueError):
    """Raised when the agent requests an unknown tool."""


logger = logging.getLogger(__name__)


@dataclass
class ToolPlan:
    name: str
    rationale: str
    arguments: Dict[str, Any]


@dataclass
class ToolExecutionResult:
    name: str
    rationale: str
    arguments: Dict[str, Any]
    output: Dict[str, Any]


class ToolRegistry:
    """Stores tool metadata and executes mock invocations."""

    def __init__(self, definitions: Sequence[ToolDefinition]):
        self._definitions: Dict[str, ToolDefinition] = {tool.name: tool for tool in definitions}
        logger.info("Registered %d tools", len(self._definitions))

    def list_openai_tools(self) -> List[Dict[str, Any]]:
        logger.debug("Serializing %d tools for OpenAI", len(self._definitions))
        return [tool.to_openai_tool() for tool in self._definitions.values()]

    def get(self, name: str) -> ToolDefinition:
        try:
            return self._definitions[name]
        except KeyError as exc:
            logger.error("Attempted to access unknown tool '%s'", name)
            raise ToolNotRegisteredError(f"Tool '{name}' is not registered") from exc

    def execute(self, name: str, arguments: Any, rationale: str = "") -> ToolExecutionResult:
        tool = self.get(name)
        parsed_args = self._normalize_arguments(arguments)
        logger.info(
            "Agent call -> %s (args: %s)",
            name,
            ",".join(sorted(parsed_args.keys())) or "<no-args>",
        )
        return ToolExecutionResult(
            name=name,
            rationale=rationale,
            arguments=parsed_args,
            output=tool.mock_response,
        )

    def _normalize_arguments(self, arguments: Any) -> Dict[str, Any]:
        if isinstance(arguments, str) and arguments.strip():
            logger.debug("Parsing JSON arguments for tool call")
            return json.loads(arguments)
        if isinstance(arguments, dict):
            return arguments
        return {}

    def names(self) -> Iterable[str]:
        return self._definitions.keys()
