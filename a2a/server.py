#!/usr/bin/env python3
"""
A2A Task Endpoint and Agent Card HTTP Server for mcp-agent-kit.
Zero runtime dependencies (stdlib http.server).
"""

import json
import os
import sys

from mcp_agent_kit.a2a import TaskManager, run_a2a_server

CARD_PATH = os.path.join(os.path.dirname(__file__), "agent.json")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    with open(CARD_PATH, "r", encoding="utf-8") as f:
        agent_card = json.load(f)

    print(f"Starting A2A HTTP Server on port {port}...")
    print(f"Agent Card: http://localhost:{port}/.well-known/agent.json")
    print(f"Tasks API:  http://localhost:{port}/a2a/tasks/send")

    server = run_a2a_server(agent_card=agent_card, port=port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nA2A server shutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
