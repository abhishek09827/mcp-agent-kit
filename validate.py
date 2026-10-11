#!/usr/bin/env python3
"""
Compliance validation runner for mcp-agent-kit.
Checks:
✓ MCP server/discover responds correctly
✓ tools/list is deterministically ordered
✓ all tool schemas pass design rules
✓ A2A agent.json is valid
✓ SKILL.md portable core is valid
✓ dual-era client probe works against local server
"""

import sys
from pathlib import Path

try:
    from mcp_agent_kit.validator import ComplianceValidator
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from mcp_agent_kit.validator import ComplianceValidator

from server import create_server


def main():
    server = create_server()
    validator = ComplianceValidator(root_dir=".")
    success = validator.run_all(server_instance=server)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
