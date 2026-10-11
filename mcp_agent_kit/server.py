"""
Stateless MCP 2026-07-28 Server implementation.
Pure Python standard library with zero runtime dependencies.
Supports stdio transport, deterministic listing, input_required results,
and optional --legacy dual-era handshake.
"""

import json
import sys
from typing import Any, Dict, List, Optional, TextIO

from .errors import (
    HeaderMismatchError,
    InternalError,
    InvalidParamsError,
    InvalidRequestError,
    MCPError,
    MethodNotFoundError,
    ParseError,
    UnsupportedProtocolVersionError,
)
from .prompts import PromptRegistry
from .protocol import (
    MODERN_PROTOCOL_VERSION,
    SUPPORTED_PROTOCOL_VERSIONS,
    ServerInfo,
    format_error_response,
    format_legacy_initialize_response,
    format_success_response,
    validate_stateless_request,
)
from .resources import ResourceRegistry
from .tools import ToolRegistry


class MCPServer:
    """
    Stateless MCP Server implementing MCP 2026-07-28.
    Validates _meta independently on every request.
    Never initiates requests to clients.
    """

    def __init__(
        self,
        name: str = "mcp_agent",
        version: str = "1.0.0",
        legacy_mode: bool = False,
        ttl_ms: int = 3600000,
        cache_scope: str = "workspace",
    ):
        self.server_info = ServerInfo(name=name, version=version)
        self.legacy_mode = legacy_mode
        self.ttl_ms = ttl_ms
        self.cache_scope = cache_scope

        self.tools = ToolRegistry()
        self.resources = ResourceRegistry()
        self.prompts = PromptRegistry()

        # Track legacy handshake state if legacy_mode is active
        self._legacy_initialized = False

    def log_diagnostic(self, message: str, stream: Optional[TextIO] = None) -> None:
        """Writes diagnostic logs to stderr exclusively."""
        err_stream = stream or sys.stderr
        err_stream.write(f"[{self.server_info.name}] {message}\n")
        err_stream.flush()

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "tools": {"listChanged": False},
            "resources": {"subscribe": False, "listChanged": False},
            "prompts": {"listChanged": False},
        }

    # =========================================================================
    # Request Dispatcher
    # =========================================================================

    def handle_request_dict(self, req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Dispatches a parsed JSON-RPC request dictionary.
        Returns a response dictionary or None (for notifications).
        """
        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if not isinstance(method, str):
            err = InvalidRequestError("Method must be a string")
            return format_error_response(req_id, err)

        # JSON-RPC Notifications have no ID and should not return a response
        is_notification = req_id is None

        # Handle Legacy Mode initialization separately if enabled
        if self.legacy_mode:
            if method == "initialize":
                return self._handle_legacy_initialize(req_id, params)
            if method == "notifications/initialized":
                self._legacy_initialized = True
                return None
            if self._legacy_initialized and (not isinstance(params, dict) or "_meta" not in params):
                # Dispatched via separate legacy handling path
                return self._dispatch_legacy(req_id, method, params, is_notification)

        # Stateless MCP 2026-07-28 Protocol path:
        # Every request MUST carry _meta and be validated independently
        try:
            meta = validate_stateless_request(params, SUPPORTED_PROTOCOL_VERSIONS)
        except MCPError as exc:
            return format_error_response(req_id, exc)
        except Exception as exc:
            return format_error_response(req_id, InternalError(str(exc)))

        # Route modern stateless methods
        try:
            if method == "server/discover":
                return self._handle_discover(req_id)
            elif method == "tools/list":
                return self._handle_tools_list(req_id)
            elif method == "tools/call":
                return self._handle_tools_call(req_id, params)
            elif method == "resources/list":
                return self._handle_resources_list(req_id)
            elif method == "resources/read":
                return self._handle_resources_read(req_id, params)
            elif method == "prompts/list":
                return self._handle_prompts_list(req_id)
            elif method == "prompts/get":
                return self._handle_prompts_get(req_id, params)
            else:
                return format_error_response(req_id, MethodNotFoundError(method))
        except MCPError as exc:
            return format_error_response(req_id, exc)
        except Exception as exc:
            return format_error_response(req_id, InternalError(str(exc)))

    # =========================================================================
    # Stateless Handlers (2026-07-28)
    # =========================================================================

    def _handle_discover(self, req_id: Any) -> Dict[str, Any]:
        """server/discover -> supportedVersions, capabilities, ttlMs, cacheScope, serverInfo"""
        return format_success_response(
            request_id=req_id,
            result_data={
                "supportedVersions": list(SUPPORTED_PROTOCOL_VERSIONS),
                "capabilities": self.get_capabilities(),
                "ttlMs": self.ttl_ms,
                "cacheScope": self.cache_scope,
            },
            server_info=self.server_info,
            result_type="complete",
        )

    def _handle_tools_list(self, req_id: Any) -> Dict[str, Any]:
        """tools/list -> deterministic ordered list, ttlMs, cacheScope"""
        tool_list = self.tools.list_tools()
        return format_success_response(
            request_id=req_id,
            result_data={
                "tools": tool_list,
                "ttlMs": self.ttl_ms,
                "cacheScope": self.cache_scope,
            },
            server_info=self.server_info,
            result_type="complete",
        )

    def _handle_tools_call(self, req_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """tools/call -> content blocks + isError flag or input_required"""
        tool_name = params.get("name")
        if not tool_name or not isinstance(tool_name, str):
            raise InvalidParamsError("tools/call requires 'name' string parameter")

        arguments = params.get("arguments", {})
        if not isinstance(arguments, dict):
            raise InvalidParamsError("tools/call 'arguments' must be an object")

        result_data, is_error, is_input_required = self.tools.call_tool(tool_name, arguments)

        if is_input_required:
            return format_success_response(
                request_id=req_id,
                result_data=result_data,
                server_info=self.server_info,
                result_type="input_required",
            )

        return format_success_response(
            request_id=req_id,
            result_data=result_data,
            server_info=self.server_info,
            result_type="complete",
        )

    def _handle_resources_list(self, req_id: Any) -> Dict[str, Any]:
        """resources/list -> deterministic ordered list, ttlMs, cacheScope"""
        resources = self.resources.list_resources()
        return format_success_response(
            request_id=req_id,
            result_data={
                "resources": resources,
                "ttlMs": self.ttl_ms,
                "cacheScope": self.cache_scope,
            },
            server_info=self.server_info,
            result_type="complete",
        )

    def _handle_resources_read(self, req_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """resources/read -> typed contents, ttlMs, cacheScope"""
        uri = params.get("uri")
        if not uri or not isinstance(uri, str):
            raise InvalidParamsError("resources/read requires 'uri' string parameter")

        contents = self.resources.read_resource(uri)
        if contents is None:
            raise InvalidParamsError(f"Resource not found: {uri}")

        return format_success_response(
            request_id=req_id,
            result_data={
                "contents": contents,
                "ttlMs": self.ttl_ms,
                "cacheScope": self.cache_scope,
            },
            server_info=self.server_info,
            result_type="complete",
        )

    def _handle_prompts_list(self, req_id: Any) -> Dict[str, Any]:
        """prompts/list -> deterministic ordered list, ttlMs, cacheScope"""
        prompts = self.prompts.list_prompts()
        return format_success_response(
            request_id=req_id,
            result_data={
                "prompts": prompts,
                "ttlMs": self.ttl_ms,
                "cacheScope": self.cache_scope,
            },
            server_info=self.server_info,
            result_type="complete",
        )

    def _handle_prompts_get(self, req_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """prompts/get -> rendered prompt"""
        name = params.get("name")
        if not name or not isinstance(name, str):
            raise InvalidParamsError("prompts/get requires 'name' string parameter")

        arguments = params.get("arguments", {})
        rendered = self.prompts.get_prompt(name, arguments)
        if rendered is None:
            raise InvalidParamsError(f"Prompt not found: {name}")

        return format_success_response(
            request_id=req_id,
            result_data=rendered,
            server_info=self.server_info,
            result_type="complete",
        )

    # =========================================================================
    # Legacy Handlers (2025-11-25 separate code path)
    # =========================================================================

    def _handle_legacy_initialize(self, req_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy 2025-11-25 handshake - never mixed with modern protocol."""
        return format_legacy_initialize_response(
            request_id=req_id,
            server_info=self.server_info,
            capabilities=self.get_capabilities(),
            protocol_version="2025-11-25",
        )

    def _dispatch_legacy(
        self, req_id: Any, method: str, params: Dict[str, Any], is_notification: bool
    ) -> Optional[Dict[str, Any]]:
        """Separate legacy route for initialized legacy peers."""
        if is_notification:
            return None

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self.tools.list_tools()},
            }
        elif method == "tools/call":
            name = params.get("name")
            args = params.get("arguments", {})
            res, is_err, _ = self.tools.call_tool(name, args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": res,
            }
        elif method == "resources/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"resources": self.resources.list_resources()},
            }
        elif method == "prompts/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"prompts": self.prompts.list_prompts()},
            }
        else:
            return format_error_response(req_id, MethodNotFoundError(method))

    # =========================================================================
    # Transport (Stdio)
    # =========================================================================

    def handle_line(self, line: str) -> Optional[str]:
        """Parses a line of JSON-RPC input, processes it, and returns the response line."""
        line = line.strip()
        if not line:
            return None

        try:
            req = json.loads(line)
        except Exception as exc:
            err_resp = format_error_response(None, ParseError(str(exc)))
            return json.dumps(err_resp)

        if not isinstance(req, dict):
            err_resp = format_error_response(None, InvalidRequestError("Request must be an object"))
            return json.dumps(err_resp)

        resp = self.handle_request_dict(req)
        if resp is not None:
            return json.dumps(resp)
        return None

    def run_stdio(self, in_stream: Optional[TextIO] = None, out_stream: Optional[TextIO] = None) -> None:
        """
        Runs the MCP stdio loop according to protocol rules:
        - Only JSON-RPC to stdout
        - Diagnostics to stderr
        - Newline + flush each response
        - Exit cleanly on stdin EOF
        """
        in_s = in_stream or sys.stdin
        out_s = out_stream or sys.stdout

        self.log_diagnostic(f"Starting server in {'legacy' if self.legacy_mode else 'stateless 2026-07-28'} mode")

        while True:
            line = in_s.readline()
            if not line:
                # EOF reached, exit cleanly
                break

            resp_str = self.handle_line(line)
            if resp_str is not None:
                out_s.write(resp_str + "\n")
                out_s.flush()

        self.log_diagnostic("Stdin closed (EOF). Server exiting.")
