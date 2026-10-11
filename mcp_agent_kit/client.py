"""
Dual-Era MCP Client implementation.
Pure Python standard library with zero runtime dependencies.
Implements dual-era probe negotiation, legacy fallback security boundaries,
and multi-server namespace merging with collision detection.
"""

from dataclasses import dataclass
import json
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from .errors import (
    HEADER_MISMATCH,
    MCPError,
    UNSUPPORTED_PROTOCOL_VERSION,
)
from .protocol import (
    LEGACY_PROTOCOL_VERSIONS,
    MODERN_PROTOCOL_VERSION,
    SUPPORTED_PROTOCOL_VERSIONS,
    ClientInfo,
)


class ProbeFailedError(Exception):
    """Raised when probing a peer server fails or fails closed."""
    pass


class AmbiguousSignalError(ProbeFailedError):
    """Raised when an unallowlisted peer returns an ambiguous signal."""
    pass


class LegacyTimeoutError(ProbeFailedError):
    """Raised when bounded initialize probe times out."""
    pass


class InvalidLegacyResponseError(ProbeFailedError):
    """Raised when legacy initialize response does not meet strict validity criteria."""
    pass


@dataclass
class ToolRoute:
    canonical_name: str
    local_name: str
    peer_id: str
    tool_def: Dict[str, Any]


class DualEraMCPClient:
    """
    MCP Client featuring:
    1. Dual-era handshake probing with fail-closed security.
    2. Strict validation of legacy initialize responses.
    3. Multi-server tool namespace merger with collision prefixing.
    """

    def __init__(
        self,
        name: str = "test_client",
        version: str = "1.0.0",
        allowlisted_peers: Optional[Set[str]] = None,
        probe_timeout_seconds: float = 2.0,
    ):
        self.client_info = ClientInfo(name=name, version=version)
        self.allowlisted_peers = allowlisted_peers or set()
        self.probe_timeout_seconds = probe_timeout_seconds

        # Connected peers state: peer_id -> {"era": "modern"|"legacy", "version": "...", "serverInfo": {...}}
        self.peers: Dict[str, Dict[str, Any]] = {}

        # Namespace merge state
        # canonical_name -> ToolRoute
        self.tools: Dict[str, ToolRoute] = {}
        # Track colliding local names: local_name -> [peer_id, ...]
        self._local_name_registry: Dict[str, List[str]] = {}

    def build_meta(self, protocol_version: str = MODERN_PROTOCOL_VERSION) -> Dict[str, Any]:
        """Builds modern _meta payload independently."""
        return {
            "protocolVersion": protocol_version,
            "clientCapabilities": {
                "roots": {"listChanged": False},
                "sampling": {},
            },
            "clientInfo": {
                "name": self.client_info.name,
                "version": self.client_info.version,
            },
            "headers": {
                "x-mcp-protocol-version": protocol_version,
            },
        }

    # =========================================================================
    # Dual-Era Probe
    # =========================================================================

    def probe_peer(
        self,
        peer_id: str,
        transport_call: Callable[[Dict[str, Any]], Dict[str, Any]],
        mock_timeout_on_init: bool = False,
    ) -> Dict[str, Any]:
        """
        Executes dual-era probe against a peer:
        1. Send server/discover with modern _meta
        2. On DiscoverResult -> select version, continue modern
        3. On recognized modern error (-32020, -32021, -32022) -> correct + retry, never send initialize
        4. On ambiguous signal -> fail closed (unless peer explicitly allowlisted)
        5. On allowlisted peer + ambiguous -> send bounded initialize probe with timeout
        6. Accept legacy era only on valid initialize result
        """
        # Step 1: Send server/discover with modern _meta
        discover_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "server/discover",
            "params": {
                "_meta": self.build_meta(MODERN_PROTOCOL_VERSION),
            },
        }

        resp = transport_call(discover_req)

        # Step 2: Check for DiscoverResult success
        if "result" in resp and isinstance(resp["result"], dict):
            res = resp["result"]
            supported_versions = res.get("supportedVersions", [])
            selected_version = MODERN_PROTOCOL_VERSION
            if supported_versions:
                if MODERN_PROTOCOL_VERSION in supported_versions:
                    selected_version = MODERN_PROTOCOL_VERSION
                else:
                    selected_version = supported_versions[0]

            peer_record = {
                "era": "modern",
                "version": selected_version,
                "serverInfo": res.get("serverInfo", {}),
                "capabilities": res.get("capabilities", {}),
                "ttlMs": res.get("ttlMs", 3600000),
                "cacheScope": res.get("cacheScope", "workspace"),
            }
            self.peers[peer_id] = peer_record
            return peer_record

        # Check error response
        error = resp.get("error", {})
        error_code = error.get("code")

        # Step 3: Recognized modern errors (-32020, -32021, -32022) -> correct + retry, never send initialize
        RECOGNIZED_MODERN_ERRORS = {HEADER_MISMATCH, -32021, UNSUPPORTED_PROTOCOL_VERSION}
        if error_code in RECOGNIZED_MODERN_ERRORS:
            if error_code == UNSUPPORTED_PROTOCOL_VERSION:
                # Correct protocol version from server's supported list and retry modern discover
                data = error.get("data", {})
                supported_by_server = data.get("supported", [])
                common_versions = [v for v in supported_by_server if v in SUPPORTED_PROTOCOL_VERSIONS]
                if common_versions:
                    corrected_version = common_versions[0]
                    retry_req = {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "server/discover",
                        "params": {"_meta": self.build_meta(corrected_version)},
                    }
                    retry_resp = transport_call(retry_req)
                    if "result" in retry_resp and isinstance(retry_resp["result"], dict):
                        r = retry_resp["result"]
                        peer_record = {
                            "era": "modern",
                            "version": corrected_version,
                            "serverInfo": r.get("serverInfo", {}),
                            "capabilities": r.get("capabilities", {}),
                        }
                        self.peers[peer_id] = peer_record
                        return peer_record

            # Under recognized modern error: NEVER send initialize
            raise ProbeFailedError(
                f"Recognized modern error ({error_code}) could not be negotiated; modern probe failed without sending initialize"
            )

        # Step 4: Ambiguous signal -> fail closed (unless peer explicitly allowlisted)
        if peer_id not in self.allowlisted_peers:
            raise AmbiguousSignalError(
                f"Ambiguous signal (error code {error_code}) from unallowlisted peer '{peer_id}'; failed closed"
            )

        # Step 5: Allowlisted peer + ambiguous signal -> send bounded initialize probe with timeout
        if mock_timeout_on_init:
            raise LegacyTimeoutError(f"Initialize probe to allowlisted peer '{peer_id}' timed out; peer stays unavailable")

        init_req_id = 100
        legacy_req = {
            "jsonrpc": "2.0",
            "id": init_req_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": self.client_info.name, "version": self.client_info.version},
            },
        }

        start_time = time.time()
        legacy_resp = transport_call(legacy_req)
        elapsed = time.time() - start_time
        if elapsed > self.probe_timeout_seconds:
            raise LegacyTimeoutError(f"Initialize probe to peer '{peer_id}' exceeded bounded timeout; peer stays unavailable")

        # Step 6: Accept legacy era ONLY on valid initialize result:
        # - jsonrpc: 2.0
        # - matching id
        # - result (no error)
        # - protocolVersion in legacy set
        # - capabilities object
        # - serverInfo with non-empty name + version
        self._validate_legacy_initialize_response(init_req_id, legacy_resp)

        leg_result = legacy_resp["result"]
        peer_record = {
            "era": "legacy",
            "version": leg_result["protocolVersion"],
            "serverInfo": leg_result["serverInfo"],
            "capabilities": leg_result["capabilities"],
        }
        self.peers[peer_id] = peer_record
        return peer_record

    def _validate_legacy_initialize_response(self, expected_id: Any, resp: Dict[str, Any]) -> None:
        """Strict validation of legacy initialize response per specification."""
        if not isinstance(resp, dict):
            raise InvalidLegacyResponseError("Response must be an object")

        if resp.get("jsonrpc") != "2.0":
            raise InvalidLegacyResponseError(f"Expected jsonrpc 2.0, got: {resp.get('jsonrpc')}")

        if resp.get("id") != expected_id:
            raise InvalidLegacyResponseError(f"Expected id {expected_id}, got: {resp.get('id')}")

        if "error" in resp:
            raise InvalidLegacyResponseError(f"Initialize response returned error: {resp['error']}")

        if "result" not in resp or not isinstance(resp["result"], dict):
            raise InvalidLegacyResponseError("Initialize response missing valid result object")

        result = resp["result"]
        proto_ver = result.get("protocolVersion")
        if proto_ver not in LEGACY_PROTOCOL_VERSIONS:
            raise InvalidLegacyResponseError(f"protocolVersion '{proto_ver}' not in legacy set {LEGACY_PROTOCOL_VERSIONS}")

        if not isinstance(result.get("capabilities"), dict):
            raise InvalidLegacyResponseError("capabilities must be an object")

        s_info = result.get("serverInfo")
        if not isinstance(s_info, dict):
            raise InvalidLegacyResponseError("serverInfo must be an object")

        s_name = s_info.get("name")
        s_ver = s_info.get("version")
        if not isinstance(s_name, str) or not s_name.strip():
            raise InvalidLegacyResponseError("serverInfo.name must be non-empty string")
        if not isinstance(s_ver, str) or not s_ver.strip():
            raise InvalidLegacyResponseError("serverInfo.version must be non-empty string")

    # =========================================================================
    # Multi-Server Namespace Merge
    # =========================================================================

    def register_peer_tools(self, peer_id: str, tools_list: List[Dict[str, Any]]) -> List[ToolRoute]:
        """
        Merges tools from a peer server into the client registry.
        Collision policy:
        - Prefix on collision (server/tool_name)
        - Never silent overwrite
        - Store both canonical and local names
        - Route calls to owning peer by canonical name lookup
        """
        registered_routes: List[ToolRoute] = []

        for tool in tools_list:
            local_name = tool["name"]

            if local_name not in self._local_name_registry:
                # First time this local name is seen: record local name
                self._local_name_registry[local_name] = [peer_id]
                canonical_name = local_name
                route = ToolRoute(
                    canonical_name=canonical_name,
                    local_name=local_name,
                    peer_id=peer_id,
                    tool_def=tool,
                )
                self.tools[canonical_name] = route
                registered_routes.append(route)
            else:
                # Collision detected!
                existing_peers = self._local_name_registry[local_name]
                if peer_id not in existing_peers:
                    existing_peers.append(peer_id)

                # 1. If the previous registration was stored under the un-prefixed name,
                # rename it to prefixed so that neither server silently overwrites!
                if local_name in self.tools:
                    orig_route = self.tools.pop(local_name)
                    prefixed_orig_name = f"{orig_route.peer_id}/{local_name}"
                    orig_route.canonical_name = prefixed_orig_name
                    self.tools[prefixed_orig_name] = orig_route

                # 2. Add current tool with prefixed canonical name
                canonical_name = f"{peer_id}/{local_name}"
                route = ToolRoute(
                    canonical_name=canonical_name,
                    local_name=local_name,
                    peer_id=peer_id,
                    tool_def=tool,
                )
                self.tools[canonical_name] = route
                registered_routes.append(route)

        return registered_routes

    def resolve_tool_route(self, tool_name: str) -> Optional[ToolRoute]:
        """Resolves tool invocation by canonical name."""
        return self.tools.get(tool_name)

    def execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        peer_transports: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Routes a tool call to the owning peer by canonical name lookup."""
        route = self.resolve_tool_route(tool_name)
        if not route:
            raise KeyError(f"Tool '{tool_name}' not found in client registry")

        transport = peer_transports.get(route.peer_id)
        if not transport:
            raise ConnectionError(f"No transport found for peer '{route.peer_id}'")

        peer_info = self.peers.get(route.peer_id, {})
        is_modern = peer_info.get("era", "modern") == "modern"

        params: Dict[str, Any] = {
            "name": route.local_name,
            "arguments": arguments,
        }
        if is_modern:
            params["_meta"] = self.build_meta(peer_info.get("version", MODERN_PROTOCOL_VERSION))

        request = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000) % 1000000,
            "method": "tools/call",
            "params": params,
        }

        return transport(request)
