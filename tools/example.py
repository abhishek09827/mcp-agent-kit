"""
Example tool demonstrating compliant MCP 2026-07-28 schema design.
Rules enforced:
- snake_case name
- Description matches "Use when X. Do not use for Y." pattern (20-1024 chars)
- No type:any
- Enums for all closed-set parameters
- readOnlyHint or destructiveHint set
"""

from typing import Any, Dict


def calculate_metrics(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates summary statistics for provided numeric data series."""
    metric_type = arguments.get("metric_type", "mean")
    values = arguments.get("values", [])

    if not values:
        return {"metric": metric_type, "value": 0.0, "count": 0}

    if metric_type == "mean":
        val = sum(values) / len(values)
    elif metric_type == "sum":
        val = sum(values)
    elif metric_type == "max":
        val = max(values)
    elif metric_type == "min":
        val = min(values)
    else:
        val = sum(values) / len(values)

    return {
        "metric": metric_type,
        "value": float(val),
        "count": len(values),
    }


TOOL_DEFINITION = {
    "name": "calculate_metrics",
    "description": "Use when analyzing numerical series or computing aggregate metrics. Do not use for unstructured text parsing.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "metric_type": {
                "type": "string",
                "enum": ["mean", "sum", "max", "min"],
                "description": "Aggregation function to apply",
                "is_closed_set": True,
            },
            "values": {
                "type": "array",
                "items": {"type": "number"},
                "description": "List of numeric values to aggregate",
            },
        },
        "required": ["values"],
    },
    "annotations": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    "handler": calculate_metrics,
}
