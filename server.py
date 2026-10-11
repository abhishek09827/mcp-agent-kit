#!/usr/bin/env python3
"""
Stateless MCP 2026-07-28 Server for mcp-agent-kit.
Zero runtime dependencies (stdlib only).
"""

import sys
from pathlib import Path

try:
    from mcp_agent_kit.server import MCPServer
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from mcp_agent_kit.server import MCPServer

from tools.example import TOOL_DEFINITION


def create_server(legacy_mode: bool = False) -> MCPServer:
    srv = MCPServer(
        name="mcp_agent_kit",
        version="1.0.0",
        legacy_mode=legacy_mode,
        ttl_ms=3600000,
        cache_scope="workspace",
    )

    # Register default example tool
    srv.tools.register(
        name=TOOL_DEFINITION["name"],
        description=TOOL_DEFINITION["description"],
        input_schema=TOOL_DEFINITION["inputSchema"],
        annotations=TOOL_DEFINITION["annotations"],
        handler=TOOL_DEFINITION["handler"],
    )

    return srv


def main():
    legacy_mode = "--legacy" in sys.argv
    srv = create_server(legacy_mode=legacy_mode)
    srv.run_stdio()


if __name__ == "__main__":
    main()
