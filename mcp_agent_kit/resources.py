"""
MCP Resource registry and handler.
Enforces deterministic sorting (by URI) and typed content reads.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ResourceDefinition:
    uri: str
    name: str
    description: str
    mimeType: str
    handler: Callable[[], Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mimeType,
        }


class ResourceRegistry:
    """Resource registry with deterministic URI ordering."""

    def __init__(self):
        self._resources: Dict[str, ResourceDefinition] = {}

    def register(
        self,
        uri: str,
        name: str,
        description: str,
        mime_type: str,
        handler: Callable[[], Dict[str, Any]],
    ) -> ResourceDefinition:
        res = ResourceDefinition(
            uri=uri,
            name=name,
            description=description,
            mimeType=mime_type,
            handler=handler,
        )
        self._resources[uri] = res
        return res

    def list_resources(self) -> List[Dict[str, Any]]:
        """Returns deterministically sorted list (alphabetically by URI)."""
        sorted_uris = sorted(self._resources.keys())
        return [self._resources[u].to_dict() for u in sorted_uris]

    def read_resource(self, uri: str) -> Optional[List[Dict[str, Any]]]:
        """Reads a resource and returns typed contents list."""
        res = self._resources.get(uri)
        if not res:
            return None
        content = res.handler()
        if isinstance(content, list):
            return content
        if "uri" not in content:
            content["uri"] = uri
        if "mimeType" not in content:
            content["mimeType"] = res.mimeType
        return [content]
