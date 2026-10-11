"""
Tests for Dual-Era MCP Client.
Covers:
- Recognized modern errors never trigger initialize
- Ambiguous signal fails closed without allowlist
- Allowlisted peer + valid initialize -> legacy era selected
- Allowlisted peer + timeout -> peer stays unavailable
- Multi-server collision produces prefixed name, never silent overwrite
"""

import time
import unittest

from mcp_agent_kit.client import (
    AmbiguousSignalError,
    DualEraMCPClient,
    LegacyTimeoutError,
    ProbeFailedError,
)
from mcp_agent_kit.errors import (
    HEADER_MISMATCH,
    METHOD_NOT_FOUND,
    UNSUPPORTED_PROTOCOL_VERSION,
)


class TestMCPClient(unittest.TestCase):
    def setUp(self):
        self.client = DualEraMCPClient(name="test_runner_client")

    def test_recognized_modern_errors_never_trigger_initialize(self):
        """Recognized modern errors (-32020, -32021, -32022) must never fall back to initialize."""
        initialize_called = False

        def mock_transport(req):
            nonlocal initialize_called
            if req.get("method") == "initialize":
                initialize_called = True
                return {"jsonrpc": "2.0", "id": req["id"], "result": {}}

            # Return recognized modern error (-32022 with no compatible versions)
            return {
                "jsonrpc": "2.0",
                "id": req.get("id"),
                "error": {
                    "code": UNSUPPORTED_PROTOCOL_VERSION,
                    "message": "Unsupported protocol version",
                    "data": {"requested": "2026-07-28", "supported": ["2030-01-01"]},
                },
            }

        with self.assertRaises(ProbeFailedError):
            self.client.probe_peer("modern_peer", mock_transport)

        # Must NOT have sent initialize
        self.assertFalse(initialize_called)

    def test_ambiguous_signal_fails_closed_without_allowlist(self):
        """Unrecognized error or method not found from non-allowlisted peer must fail closed."""
        def mock_transport(req):
            return {
                "jsonrpc": "2.0",
                "id": req.get("id"),
                "error": {
                    "code": METHOD_NOT_FOUND,
                    "message": "Method not found",
                },
            }

        # Peer is NOT in allowlisted_peers
        with self.assertRaises(AmbiguousSignalError):
            self.client.probe_peer("unknown_legacy_server", mock_transport)

        self.assertNotIn("unknown_legacy_server", self.client.peers)

    def test_allowlisted_peer_valid_initialize_selects_legacy(self):
        """Allowlisted peer on ambiguous signal receives initialize and negotiates legacy era."""
        self.client.allowlisted_peers.add("allowlisted_old_server")

        def mock_transport(req):
            if req.get("method") == "server/discover":
                return {
                    "jsonrpc": "2.0",
                    "id": req["id"],
                    "error": {"code": METHOD_NOT_FOUND, "message": "Method not found"},
                }
            if req.get("method") == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": req["id"],
                    "result": {
                        "protocolVersion": "2025-11-25",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "old_server", "version": "0.9.0"},
                    },
                }
            return {}

        peer = self.client.probe_peer("allowlisted_old_server", mock_transport)
        self.assertEqual(peer["era"], "legacy")
        self.assertEqual(peer["version"], "2025-11-25")
        self.assertEqual(peer["serverInfo"]["name"], "old_server")

    def test_allowlisted_peer_timeout_stays_unavailable(self):
        """Allowlisted peer timing out on initialize must stay unavailable."""
        self.client.allowlisted_peers.add("slow_server")

        def mock_transport(req):
            if req.get("method") == "server/discover":
                return {"jsonrpc": "2.0", "id": req["id"], "error": {"code": METHOD_NOT_FOUND}}
            return {}

        with self.assertRaises(LegacyTimeoutError):
            self.client.probe_peer("slow_server", mock_transport, mock_timeout_on_init=True)

        self.assertNotIn("slow_server", self.client.peers)

    def test_collision_produces_prefixed_name_never_silent_overwrite(self):
        """Tool namespace collision prefixes colliding tools and never silently overwrites."""
        tools_server_a = [
            {"name": "fetch_user", "description": "Fetch user from DB A"},
            {"name": "unique_a", "description": "Only in A"},
        ]
        tools_server_b = [
            {"name": "fetch_user", "description": "Fetch user from API B"},
            {"name": "unique_b", "description": "Only in B"},
        ]

        # Register server A
        self.client.register_peer_tools("server_a", tools_server_a)
        # Register server B with colliding 'fetch_user'
        self.client.register_peer_tools("server_b", tools_server_b)

        # 1. Non-colliding tools retain clean canonical names
        self.assertIn("unique_a", self.client.tools)
        self.assertEqual(self.client.tools["unique_a"].peer_id, "server_a")
        self.assertIn("unique_b", self.client.tools)
        self.assertEqual(self.client.tools["unique_b"].peer_id, "server_b")

        # 2. Colliding tool must be prefixed for both; no silent overwrite
        self.assertIn("server_a/fetch_user", self.client.tools)
        self.assertEqual(self.client.tools["server_a/fetch_user"].peer_id, "server_a")

        self.assertIn("server_b/fetch_user", self.client.tools)
        self.assertEqual(self.client.tools["server_b/fetch_user"].peer_id, "server_b")

        # Local names are preserved
        self.assertEqual(self.client.tools["server_a/fetch_user"].local_name, "fetch_user")
        self.assertEqual(self.client.tools["server_b/fetch_user"].local_name, "fetch_user")


if __name__ == "__main__":
    unittest.main()
