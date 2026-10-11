"""
Stateless MCP 2026-07-28 Protocol definitions, validation, and serialization.
Pure Python standard library with zero runtime dependencies.
"""

from dataclasses import dataclass, field
import json
from typing import Any, Dict, List, Optional, Tuple

from .errors import (
    HeaderMismatchError,
    InvalidParamsError,
    MCPError,
    UnsupportedProtocolVersionError,
)

MODERN_PROTOCOL_VERSION = "2026-07-28"
SUPPORTED_PROTOCOL_VERSIONS = [MODERN_PROTOCOL_VERSION]
LEGACY_PROTOCOL_VERSIONS = {"2025-11-25", "2024-11-05"}


@dataclass(frozen=True)
class ClientInfo:
    name: str
    version: str

    @classmethod
    def from_dict(cls, data: Any) -> "ClientInfo":
        if not isinstance(data, dict):
            raise InvalidParamsError("clientInfo must be an object with name and version")
        name = data.get("name")
        version = data.get("version")
        if not isinstance(name, str) or not name.strip():
            raise InvalidParamsError("clientInfo.name must be a non-empty string")
        if not isinstance(version, str) or not version.strip():
            raise InvalidParamsError("clientInfo.version must be a non-empty string")
        return cls(name=name.strip(), version=version.strip())


@dataclass(frozen=True)
class ServerInfo:
    name: str
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, str]:
        return {"name": self.name, "version": self.version}


@dataclass(frozen=True)
class RequestMeta:
    protocolVersion: str
    clientCapabilities: Dict[str, Any]
    clientInfo: ClientInfo
    headers: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, meta_dict: Any, supported_versions: Optional[List[str]] = None) -> "RequestMeta":
        if supported_versions is None:
            supported_versions = SUPPORTED_PROTOCOL_VERSIONS

        if not isinstance(meta_dict, dict):
            raise InvalidParamsError("params._meta must be a JSON object")

        protocol_version = meta_dict.get("protocolVersion")
        if not isinstance(protocol_version, str) or not protocol_version.strip():
            raise InvalidParamsError("params._meta.protocolVersion must be a non-empty string")

        if protocol_version not in supported_versions:
            raise UnsupportedProtocolVersionError(
                requested=protocol_version,
                supported=list(supported_versions),
            )

        client_caps = meta_dict.get("clientCapabilities")
        if not isinstance(client_caps, dict):
            raise InvalidParamsError("params._meta.clientCapabilities must be an object")

        client_info_raw = meta_dict.get("clientInfo")
        client_info = ClientInfo.from_dict(client_info_raw)

        headers = meta_dict.get("headers", {})
        if not isinstance(headers, dict):
            raise HeaderMismatchError("params._meta.headers must be an object")

        # Validate header consistency if protocol header is supplied
        if "x-mcp-protocol-version" in headers:
            hdr_val = str(headers["x-mcp-protocol-version"])
            if hdr_val != protocol_version:
                raise HeaderMismatchError(
                    f"Header mismatch: x-mcp-protocol-version '{hdr_val}' != _meta.protocolVersion '{protocol_version}'"
                )

        return cls(
            protocolVersion=protocol_version,
            clientCapabilities=client_caps,
            clientInfo=client_info,
            headers=headers,
        )


def validate_stateless_request(
    params: Any,
    supported_versions: Optional[List[str]] = None,
) -> RequestMeta:
    """
    Validates that request parameters carry a valid _meta block independently.
    Never reuses metadata from any previous request.
    """
    if not isinstance(params, dict):
        raise InvalidParamsError("Request params must be an object containing _meta")

    if "_meta" not in params:
        raise InvalidParamsError("Missing required '_meta' block in request params")

    return RequestMeta.from_dict(params["_meta"], supported_versions=supported_versions)


def format_success_response(
    request_id: Any,
    result_data: Dict[str, Any],
    server_info: ServerInfo,
    result_type: str = "complete",
) -> Dict[str, Any]:
    """
    Formats an MCP 2026-07-28 compliant JSON-RPC success response.
    Returns resultType: "complete" (or "input_required") + server identity.
    """
    payload = {
        "resultType": result_type,
        "serverInfo": server_info.to_dict(),
    }
    payload.update(result_data)
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": payload,
    }


def format_error_response(request_id: Any, error: MCPError) -> Dict[str, Any]:
    """Formats an MCP compliant JSON-RPC error response."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": error.to_dict(),
    }


def format_legacy_initialize_response(
    request_id: Any,
    server_info: ServerInfo,
    capabilities: Dict[str, Any],
    protocol_version: str = "2025-11-25",
) -> Dict[str, Any]:
    """Formats a legacy MCP initialize response (2025-11-25 era)."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": protocol_version,
            "capabilities": capabilities,
            "serverInfo": server_info.to_dict(),
        },
    }
