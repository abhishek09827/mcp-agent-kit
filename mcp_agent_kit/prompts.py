"""
MCP Prompt registry and renderer.
Enforces deterministic sorting (by name) and rendered prompt formatting.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass
class PromptArgument:
    name: str
    description: str
    required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "required": self.required,
        }


@dataclass
class PromptDefinition:
    name: str
    description: str
    arguments: List[PromptArgument]
    renderer: Callable[[Dict[str, Any]], Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "arguments": [arg.to_dict() for arg in self.arguments],
        }


class PromptRegistry:
    """Prompt registry with deterministic name ordering."""

    def __init__(self):
        self._prompts: Dict[str, PromptDefinition] = {}

    def register(
        self,
        name: str,
        description: str,
        arguments: Optional[List[Dict[str, Any]]] = None,
        renderer: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ) -> PromptDefinition:
        arg_objs = []
        if arguments:
            for a in arguments:
                arg_objs.append(
                    PromptArgument(
                        name=a["name"],
                        description=a.get("description", ""),
                        required=a.get("required", True),
                    )
                )

        if renderer is None:
            renderer = lambda args: {
                "description": description,
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": f"Prompt: {name}\nArguments: {args}",
                        },
                    }
                ],
            }

        prompt = PromptDefinition(
            name=name,
            description=description,
            arguments=arg_objs,
            renderer=renderer,
        )
        self._prompts[name] = prompt
        return prompt

    def list_prompts(self) -> List[Dict[str, Any]]:
        """Returns deterministically sorted list (alphabetically by name)."""
        sorted_names = sorted(self._prompts.keys())
        return [self._prompts[n].to_dict() for n in sorted_names]

    def get_prompt(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Renders prompt messages."""
        p = self._prompts.get(name)
        if not p:
            return None
        return p.renderer(arguments or {})
