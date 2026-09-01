"""
Every skill in skills/ inherits from BaseSkill and implements:
  - name        : unique identifier, e.g. "open_app"
  - description : plain-English explanation the LLM uses to decide when to call this
  - parameters  : JSON-schema-like dict describing what args run() expects
  - run(**kwargs) -> str : does the action, returns a short result message

This file has NO project-specific logic. It's just the contract.
New skill = new file in skills/ + one line in skills/__init__.py registry.
"""

from abc import ABC, abstractmethod


class BaseSkill(ABC):
    name: str = "base_skill"
    description: str = "Override this."
    parameters: dict = {}

    @abstractmethod
    def run(self, **kwargs) -> str:
        """Execute the skill. Must return a short string result to speak/show."""
        raise NotImplementedError

    def to_tool_schema(self) -> dict:
        """Format this skill as an OpenAI/Ollama-style function-calling tool definition."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": list(self.parameters.keys()),
                },
            },
        }
