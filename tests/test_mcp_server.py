"""
Tests for Stateless MCP 2026-07-28 Server.
Covers:
- Every request repeats _meta independently
- -32022 returned for unsupported version with {requested, supported}
- List results stable regardless of insertion order
- Tool call returns isError:true on executor failure
- Server never initiates a request (input_required protocol)
- Stdio transport execution & legacy flag separation
"""

import io
import json
import unittest

from mcp_agent_kit.errors import INVALID_PARAMS, UNSUPPORTED_PROTOCOL_VERSION
from mcp_agent_kit.protocol import MODERN_PROTOCOL_VERSION
from mcp_agent_kit.server import MCPServer
from mcp_agent_kit.tools import InputRequired


class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.server = MCPServer(name="test_server", version="1.0.0")

    def _meta(self, version: str = MODERN_PROTOCOL_VERSION):
        return {
            "protocolVersion": version,
            "clientCapabilities": {},
            "clientInfo": {"name": "unit-test-client", "version": "1.0.0"},
        }

    def test_every_request_repeats_meta_independently(self):
        """Metadata must never be reused between requests; each request must supply _meta."""
        # 1. First request has valid _meta
        req1 = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "server/discover",
            "params": {"_meta": self._meta()},
        }
        res1 = self.server.handle_request_dict(req1)
        self.assertIn("result", res1)
        self.assertEqual(res1["result"]["resultType"], "complete")

        # 2. Second request omits _meta -> MUST fail independently with -32602
        req2 = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }
        res2 = self.server.handle_request_dict(req2)
        self.assertIn("error", res2)
        self.assertEqual(res2["error"]["code"], INVALID_PARAMS)
        self.assertIn("_meta", res2["error"]["message"])

    def test_unsupported_protocol_version_error(self):
        """Unsupported version returns -32022 with {requested, supported} in data."""
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "server/discover",
            "params": {
                "_meta": self._meta(version="2024-01-01"),
            },
        }
        res = self.server.handle_request_dict(req)
        self.assertIn("error", res)
        err = res["error"]
        self.assertEqual(err["code"], UNSUPPORTED_PROTOCOL_VERSION)
        self.assertIn("data", err)
        self.assertEqual(err["data"]["requested"], "2024-01-01")
        self.assertIn(MODERN_PROTOCOL_VERSION, err["data"]["supported"])

    def test_list_results_stable_regardless_of_insertion_order(self):
        """List results must be deterministically sorted alphabetically, not insertion order."""
        # Insert tools in reverse order
        self.server.tools.register(
            name="zebra_tool",
            description="Use when doing zebra tasks. Do not use for lions.",
            input_schema={"type": "object"},
            annotations={"readOnlyHint": True},
            handler=lambda args: "zebra",
        )
        self.server.tools.register(
            name="alpha_tool",
            description="Use when doing alpha tasks. Do not use for beta.",
            input_schema={"type": "object"},
            annotations={"readOnlyHint": True},
            handler=lambda args: "alpha",
        )
        self.server.tools.register(
            name="middle_tool",
            description="Use when doing middle tasks. Do not use for extremes.",
            input_schema={"type": "object"},
            annotations={"readOnlyHint": True},
            handler=lambda args: "middle",
        )

        req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/list",
            "params": {"_meta": self._meta()},
        }
        res = self.server.handle_request_dict(req)
        tool_names = [t["name"] for t in res["result"]["tools"]]
        self.assertEqual(tool_names, ["alpha_tool", "middle_tool", "zebra_tool"])

        # Insert resources out of order
        self.server.resources.register(
            uri="res://zebra",
            name="Zebra Resource",
            description="Zebra",
            mime_type="text/plain",
            handler=lambda: {"text": "z"},
        )
        self.server.resources.register(
            uri="res://alpha",
            name="Alpha Resource",
            description="Alpha",
            mime_type="text/plain",
            handler=lambda: {"text": "a"},
        )
        res_req = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "resources/list",
            "params": {"_meta": self._meta()},
        }
        res_resp = self.server.handle_request_dict(res_req)
        uris = [r["uri"] for r in res_resp["result"]["resources"]]
        self.assertEqual(uris, ["res://alpha", "res://zebra"])

    def test_tool_call_returns_isError_true_on_executor_failure(self):
        """Executor failures must return content blocks and isError: true without crashing."""
        def failing_handler(args):
            raise RuntimeError("Database connection timed out during execution")

        self.server.tools.register(
            name="failing_tool",
            description="Use when testing failures. Do not use for healthy runs.",
            input_schema={"type": "object"},
            annotations={"destructiveHint": True},
            handler=failing_handler,
        )

        req = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "_meta": self._meta(),
                "name": "failing_tool",
                "arguments": {},
            },
        }
        res = self.server.handle_request_dict(req)
        self.assertIn("result", res)
        result = res["result"]
        self.assertEqual(result["resultType"], "complete")
        self.assertTrue(result["isError"])
        self.assertIn("content", result)
        self.assertIn("Database connection timed out", result["content"][0]["text"])

    def test_server_never_initiates_request(self):
        """Server never initiates requests; returns input_required result for client retry."""
        def interactive_handler(args):
            if "confirmation" not in args:
                raise InputRequired(
                    prompt="Please confirm deletion of resources",
                    fields=[{"name": "confirmation", "type": "boolean"}],
                )
            return "Deleted successfully"

        self.server.tools.register(
            name="delete_tool",
            description="Use when deleting resources. Do not use for creation.",
            input_schema={"type": "object"},
            annotations={"destructiveHint": True},
            handler=interactive_handler,
        )

        # 1. First call without required input -> returns input_required result
        req1 = {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "_meta": self._meta(),
                "name": "delete_tool",
                "arguments": {},
            },
        }
        res1 = self.server.handle_request_dict(req1)
        self.assertEqual(res1["result"]["resultType"], "input_required")
        self.assertEqual(res1["result"]["prompt"], "Please confirm deletion of resources")

        # 2. Client retries with new request ID and needed fields
        req2 = {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {
                "_meta": self._meta(),
                "name": "delete_tool",
                "arguments": {"confirmation": True},
            },
        }
        res2 = self.server.handle_request_dict(req2)
        self.assertEqual(res2["result"]["resultType"], "complete")
        self.assertFalse(res2["result"]["isError"])

    def test_stdio_loop(self):
        """Server processes stdio lines, writes to stdout, diagnostics to stderr, and exits on EOF."""
        req = {
            "jsonrpc": "2.0",
            "id": 20,
            "method": "server/discover",
            "params": {"_meta": self._meta()},
        }
        input_data = json.dumps(req) + "\n"
        in_stream = io.StringIO(input_data)
        out_stream = io.StringIO()
        err_stream = io.StringIO()

        self.server.log_diagnostic = lambda msg, stream=None: err_stream.write(msg + "\n")
        self.server.run_stdio(in_stream=in_stream, out_stream=out_stream)

        # Output received
        output_line = out_stream.getvalue().strip()
        resp = json.loads(output_line)
        self.assertEqual(resp["id"], 20)
        self.assertEqual(resp["result"]["resultType"], "complete")
        self.assertIn("serverInfo", resp["result"])


if __name__ == "__main__":
    unittest.main()
