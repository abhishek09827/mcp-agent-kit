"""
MCP Error codes and Exception definitions.
Compliant with Stateless MCP 2026-07-28 and JSON-RPC 2.0.
"""

from typing import Any, Dict, List, Optional


# JSON-RPC & MCP Standard Error Codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603

# MCP 2026-07-28 Specific Error Codes
HEADER_MISMATCH = -32020
UNSUPPORTED_PROTOCOL_VERSION = -32022


class MCPError(Exception):
    """Base class for MCP JSON-RPC protocol errors."""

    def __init__(self, code: int, message: str, data: Optional[Any] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.data is not None:
            payload["data"] = self.data
        return payload


class UnsupportedProtocolVersionError(MCPError):
    """Returned when client protocol version is unsupported (-32022)."""

    def __init__(self, requested: str, supported: List[str]):
        super().__init__(
            code=UNSUPPORTED_PROTOCOL_VERSION,
            message="Unsupported protocol version",
            data={
                "requested": requested,
                "supported": supported,
            },
        )
        self.requested = requested
        self.supported = supported


class InvalidParamsError(MCPError):
    """Returned when params are invalid or missing required _meta (-32602)."""

    def __init__(self, message: str = "Invalid params: missing or invalid _meta (must include protocolVersion, clientCapabilities, clientInfo)"):
        super().__init__(code=INVALID_PARAMS, message=message)


class HeaderMismatchError(MCPError):
    """Returned when header or metadata protocol mismatch occurs (-32020)."""

    def __init__(self, message: str = "Header mismatch: request metadata does not match protocol expectations"):
        super().__init__(code=HEADER_MISMATCH, message=message)


class MethodNotFoundError(MCPError):
    """Returned when method is unrecognized (-32601)."""

    def __init__(self, method: str):
        super().__init__(code=METHOD_NOT_FOUND, message=f"Method not found: {method}")


class ParseError(MCPError):
    """Returned when JSON cannot be parsed (-32700)."""

    def __init__(self, detail: str = "Parse error"):
        super().__init__(code=PARSE_ERROR, message=f"Parse error: {detail}")


class InvalidRequestError(MCPError):
    """Returned when request structure is invalid (-32600)."""

    def __init__(self, detail: str = "Invalid request"):
        super().__init__(code=INVALID_REQUEST, message=f"Invalid Request: {detail}")


class InternalError(MCPError):
    """Returned for unhandled server internal errors (-32603)."""

    def __init__(self, detail: str = "Internal error"):
        super().__init__(code=INTERNAL_ERROR, message=f"Internal error: {detail}")
