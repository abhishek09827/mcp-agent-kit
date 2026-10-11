"""
MCP Tool registry, schema rules validator, and execution engine.
Enforces deterministic sorting, tool annotations, and strict schema rules.
"""

from dataclasses import dataclass, field
import json
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


class InputRequired(Exception):
    """
    Raised by a tool handler when additional user input is required mid-operation.
    The stateless server returns an input_required response, never initiating requests.
    """

    def __init__(self, prompt: str, fields: Optional[List[Dict[str, Any]]] = None, state: Optional[Dict[str, Any]] = None):
        super().__init__(prompt)
        self.prompt = prompt
        self.fields = fields or []
        self.state = state or {}


@dataclass(frozen=True)
class ToolAnnotations:
    """Standard MCP annotations for tool execution hints."""
    readOnlyHint: bool = False
    destructiveHint: bool = False
    idempotentHint: bool = False
    openWorldHint: bool = False

    def to_dict(self) -> Dict[str, bool]:
        return {
            "readOnlyHint": self.readOnlyHint,
            "destructiveHint": self.destructiveHint,
            "idempotentHint": self.idempotentHint,
            "openWorldHint": self.openWorldHint,
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "ToolAnnotations":
        if not data:
            return cls()
        return cls(
            readOnlyHint=bool(data.get("readOnlyHint", False)),
            destructiveHint=bool(data.get("destructiveHint", False)),
            idempotentHint=bool(data.get("idempotentHint", False)),
            openWorldHint=bool(data.get("openWorldHint", False)),
        )


@dataclass
class ToolDefinition:
    name: str
    description: str
    inputSchema: Dict[str, Any]
    annotations: ToolAnnotations
    handler: Callable[[Dict[str, Any]], Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.inputSchema,
            "annotations": self.annotations.to_dict(),
        }


SNAKE_CASE_REGEX = re.compile(r"^[a-z][a-z0-9_]*$")
DESC_PATTERN_REGEX = re.compile(r"^Use when .+\. Do not use for .+\.", re.DOTALL)


def validate_tool_schema(tool: ToolDefinition) -> List[str]:
    """
    Validates a tool against MCP Agent Kit production schema rules:
    - snake_case name
    - description matches 'Use when X. Do not use for Y.' pattern
    - description 20–1024 chars
    - no type:any fields
    - enums for all Literal/closed-set parameters
    - readOnlyHint or destructiveHint must be set
    """
    errors: List[str] = []

    # 1. snake_case name
    if not SNAKE_CASE_REGEX.match(tool.name):
        errors.append(f"Tool '{tool.name}' name must be snake_case (matching ^[a-z][a-z0-9_]*$)")

    # 2. Description length
    desc = tool.description.strip()
    if len(desc) < 20 or len(desc) > 1024:
        errors.append(
            f"Tool '{tool.name}' description length is {len(desc)} chars; must be between 20 and 1024 chars"
        )

    # 3. Description pattern: "Use when X. Do not use for Y."
    if not DESC_PATTERN_REGEX.search(desc):
        errors.append(
            f"Tool '{tool.name}' description does not match required pattern: 'Use when X. Do not use for Y.'"
        )

    # 4. Annotations: readOnlyHint or destructiveHint must be set
    if not tool.annotations.readOnlyHint and not tool.annotations.destructiveHint:
        errors.append(
            f"Tool '{tool.name}' missing readOnlyHint or destructiveHint (at least one must be true)"
        )

    # 5. Schema checks (no type:any, enum checks)
    schema = tool.inputSchema or {}
    _check_schema_properties(tool.name, schema, errors)

    return errors


def _check_schema_properties(tool_name: str, schema: Any, errors: List[str], path: str = "inputSchema") -> None:
    if not isinstance(schema, dict):
        return

    # Check for type: any
    type_val = schema.get("type")
    if type_val == "any" or (isinstance(type_val, list) and "any" in type_val):
        errors.append(f"Tool '{tool_name}' has disallowed 'type: any' at {path}")

    # Check properties
    properties = schema.get("properties")
    if isinstance(properties, dict):
        for prop_name, prop_schema in properties.items():
            prop_path = f"{path}.properties.{prop_name}"
            if isinstance(prop_schema, dict):
                # Check for explicit type: any
                if prop_schema.get("type") == "any":
                    errors.append(f"Tool '{tool_name}' property '{prop_name}' has disallowed 'type: any'")
                # Check closed-set parameters marked as closed_set or literal
                if prop_schema.get("is_closed_set", False) and "enum" not in prop_schema:
                    errors.append(f"Tool '{tool_name}' closed-set parameter '{prop_name}' must define 'enum'")
                _check_schema_properties(tool_name, prop_schema, errors, prop_path)

    # Check items if array
    items = schema.get("items")
    if isinstance(items, dict):
        _check_schema_properties(tool_name, items, errors, f"{path}.items")


class ToolRegistry:
    """Registry maintaining tools with deterministic alphabetical ordering."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        annotations: Union[ToolAnnotations, Dict[str, bool]],
        handler: Callable[[Dict[str, Any]], Any],
    ) -> ToolDefinition:
        if isinstance(annotations, dict):
            annot = ToolAnnotations.from_dict(annotations)
        else:
            annot = annotations

        tool = ToolDefinition(
            name=name,
            description=description,
            inputSchema=input_schema,
            annotations=annot,
            handler=handler,
        )
        self._tools[name] = tool
        return tool

    def get(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """Returns deterministically sorted list (alphabetically by name)."""
        sorted_names = sorted(self._tools.keys())
        return [self._tools[name].to_dict() for name in sorted_names]

    def validate_all(self) -> Dict[str, List[str]]:
        """Validates all registered tools against schema rules."""
        results: Dict[str, List[str]] = {}
        for name, tool in self._tools.items():
            errs = validate_tool_schema(tool)
            if errs:
                results[name] = errs
        return results

    def call_tool(
        self, name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], bool, bool]:
        """
        Executes a registered tool.
        Returns: (result_data, is_error, is_input_required)
        """
        args = arguments or {}
        tool = self._tools.get(name)
        if not tool:
            return (
                {
                    "content": [{"type": "text", "text": f"Tool '{name}' not found"}],
                    "isError": True,
                },
                True,
                False,
            )

        try:
            output = tool.handler(args)
            if isinstance(output, dict) and output.get("resultType") == "input_required":
                return output, False, True

            # Standard output formatting to content blocks
            if isinstance(output, list) and all(isinstance(b, dict) and "type" in b for b in output):
                content_blocks = output
            elif isinstance(output, dict):
                content_blocks = [{"type": "text", "text": json.dumps(output)}]
            else:
                content_blocks = [{"type": "text", "text": str(output)}]

            return (
                {
                    "content": content_blocks,
                    "isError": False,
                },
                False,
                False,
            )
        except InputRequired as ir:
            return (
                {
                    "resultType": "input_required",
                    "prompt": ir.prompt,
                    "fields": ir.fields,
                    "state": ir.state,
                },
                False,
                True,
            )
        except Exception as exc:
            return (
                {
                    "content": [{"type": "text", "text": f"Tool execution failed: {str(exc)}"}],
                    "isError": True,
                },
                True,
                False,
            )
