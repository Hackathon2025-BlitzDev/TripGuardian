from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class ToolDefinition:
    """Represents a single tool exposed to the agent."""

    name: str
    description: str
    input_schema: Dict[str, Any]
    mock_response: Dict[str, Any]

    def to_openai_tool(self) -> Dict[str, Any]:
        """Serialize the tool into the format expected by OpenAI tool-calling."""

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }
