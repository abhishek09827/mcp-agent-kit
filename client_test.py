#!/usr/bin/env python3
"""
Dual-Era Probe client tests for local MCP agent.
Validates modern negotiation, tools listing, and execution.
"""

import unittest
from mcp_agent_kit.client import DualEraMCPClient
from server import create_server


class TestLocalAgentClient(unittest.TestCase):
    def setUp(self):
        self.server = create_server()
        self.client = DualEraMCPClient(name="local_test_client")

    def transport(self, req):
        res = self.server.handle_request_dict(req)
        return res if res is not None else {}

    def test_modern_probe_success(self):
        peer = self.client.probe_peer("mcp_agent_kit", self.transport)
        self.assertEqual(peer["era"], "modern")
        self.assertEqual(peer["version"], "2026-07-28")
        self.assertIn("tools", peer["capabilities"])

    def test_tools_list_and_execution(self):
        self.client.probe_peer("mcp_agent_kit", self.transport)
        tools_resp = self.server.handle_request_dict({
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/list",
            "params": {"_meta": self.client.build_meta()},
        })
        tools = tools_resp["result"]["tools"]
        self.client.register_peer_tools("mcp_agent_kit", tools)

        # Call calculate_metrics
        res = self.client.execute_tool_call(
            "calculate_metrics",
            {"values": [10.0, 20.0, 30.0], "metric_type": "mean"},
            {"mcp_agent_kit": self.transport},
        )
        self.assertIn("result", res)
        self.assertFalse(res["result"]["isError"])
        content = res["result"]["content"]
        self.assertTrue(len(content) > 0)


if __name__ == "__main__":
    unittest.main()
