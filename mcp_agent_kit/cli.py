"""
MCP Agent Kit Scaffolder CLI (create-mcp-agent).
Interactive and automated generator for production-ready MCP agents.
Generates compliant MCP server, A2A agent card, and portable SKILL.md.
"""

import argparse
import os
import re
import sys
from typing import Optional

SNAKE_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def validate_agent_name(name: str) -> bool:
    """Validates snake_case name."""
    return bool(SNAKE_CASE_PATTERN.match(name))


def scaffold_agent(
    target_dir: str,
    name: str,
    description: str,
    base_url: str = "http://localhost:8000",
    include_example_tools: bool = True,
) -> None:
    """Scaffolds complete MCP agent directory structure and files."""
    os.makedirs(target_dir, exist_ok=True)
    tools_dir = os.path.join(target_dir, "tools")
    a2a_dir = os.path.join(target_dir, "a2a")
    os.makedirs(tools_dir, exist_ok=True)
    os.makedirs(a2a_dir, exist_ok=True)

    # Ensure description matches required pattern
    desc = description.strip()
    if not re.search(r"Use when .+\. Do not use for .+\.", desc):
        desc = f"Use when querying or operating {name} agent capabilities. Do not use for unrelated external operations. {desc}".strip()

    # 1. tools/__init__.py
    tools_init_path = os.path.join(tools_dir, "__init__.py")
    with open(tools_init_path, "w", encoding="utf-8") as f:
        f.write('"""Tools package for MCP agent."""\n')

    # 2. tools/example.py
    example_tool_path = os.path.join(tools_dir, "example.py")
    if include_example_tools:
        example_content = '''"""
Example tool demonstrating compliant MCP 2026-07-28 schema design.
Rules enforced:
- snake_case name
- Description matches "Use when X. Do not use for Y." pattern (20-1024 chars)
- No type:any
- Enums for closed-set parameters
- readOnlyHint or destructiveHint set
"""

from typing import Any, Dict


def calculate_metrics(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates summary statistics for provided numeric data series."""
    metric_type = arguments.get("metric_type", "mean")
    values = arguments.get("values", [])

    if not values:
        return {"metric": metric_type, "value": 0.0, "count": 0}

    if metric_type == "mean":
        val = sum(values) / len(values)
    elif metric_type == "sum":
        val = sum(values)
    elif metric_type == "max":
        val = max(values)
    elif metric_type == "min":
        val = min(values)
    else:
        val = sum(values) / len(values)

    return {
        "metric": metric_type,
        "value": float(val),
        "count": len(values),
    }


TOOL_DEFINITION = {
    "name": "calculate_metrics",
    "description": "Use when analyzing numerical series or computing aggregate metrics. Do not use for unstructured text parsing.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "metric_type": {
                "type": "string",
                "enum": ["mean", "sum", "max", "min"],
                "description": "Aggregation function to apply",
                "is_closed_set": True,
            },
            "values": {
                "type": "array",
                "items": {"type": "number"},
                "description": "List of numeric values to aggregate",
            },
        },
        "required": ["values"],
    },
    "annotations": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    "handler": calculate_metrics,
}
'''
        with open(example_tool_path, "w", encoding="utf-8") as f:
            f.write(example_content)

    # 3. server.py
    server_path = os.path.join(target_dir, "server.py")
    server_content = f'''#!/usr/bin/env python3
"""
Stateless MCP 2026-07-28 Server for {name}.
Pure Python standard library with zero runtime dependencies.
"""

import sys
from pathlib import Path

try:
    from mcp_agent_kit.server import MCPServer
except ImportError:
    for parent in Path(__file__).resolve().parents:
        if (parent / "mcp_agent_kit").exists():
            sys.path.insert(0, str(parent))
            break
    from mcp_agent_kit.server import MCPServer

from tools.example import TOOL_DEFINITION


def create_server(legacy_mode: bool = False) -> MCPServer:
    srv = MCPServer(
        name="{name}",
        version="1.0.0",
        legacy_mode=legacy_mode,
        ttl_ms=3600000,
        cache_scope="workspace",
    )

    # Register tools
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
'''
    with open(server_path, "w", encoding="utf-8") as f:
        f.write(server_content)
    os.chmod(server_path, 0o755)

    # 4. a2a/agent.json
    tools_list = []
    if include_example_tools:
        tools_list.append({
            "name": "calculate_metrics",
            "description": "Use when analyzing numerical series or computing aggregate metrics. Do not use for unstructured text parsing.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "metric_type": {"type": "string", "enum": ["mean", "sum", "max", "min"]},
                    "values": {"type": "array", "items": {"type": "number"}},
                },
                "required": ["values"],
            },
            "annotations": {"readOnlyHint": True, "destructiveHint": False},
        })

    from .a2a import generate_agent_card
    agent_card_data = generate_agent_card(
        name=name,
        description=desc,
        base_url=base_url,
        tools_list=tools_list,
        version="1.0.0",
    )
    import json
    agent_json_path = os.path.join(a2a_dir, "agent.json")
    with open(agent_json_path, "w", encoding="utf-8") as f:
        json.dump(agent_card_data, f, indent=2)

    # 5. a2a/server.py
    a2a_server_path = os.path.join(a2a_dir, "server.py")
    a2a_server_content = f'''#!/usr/bin/env python3
"""
A2A Task Endpoint and Agent Card HTTP Server for {name}.
Zero runtime dependencies (stdlib http.server).
"""

import json
import os
import sys
from mcp_agent_kit.a2a import run_a2a_server, TaskManager

CARD_PATH = os.path.join(os.path.dirname(__file__), "agent.json")

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    with open(CARD_PATH, "r", encoding="utf-8") as f:
        agent_card = json.load(f)

    print(f"Starting A2A HTTP Server for {name} on port {{port}}...")
    print(f"Agent Card: http://localhost:{{port}}/.well-known/agent.json")
    print(f"Tasks API:  http://localhost:{{port}}/a2a/tasks/send")
    
    server = run_a2a_server(agent_card=agent_card, port=port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nA2A server shutting down.")
        server.server_close()

if __name__ == "__main__":
    main()
'''
    with open(a2a_server_path, "w", encoding="utf-8") as f:
        f.write(a2a_server_content)
    os.chmod(a2a_server_path, 0o755)

    # 6. SKILL.md
    from .skill import generate_skill_markdown
    skill_content = generate_skill_markdown(
        agent_name=name,
        description=desc,
        tools_list=tools_list,
    )
    skill_path = os.path.join(target_dir, "SKILL.md")
    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(skill_content)

    # 7. validate.py
    validate_path = os.path.join(target_dir, "validate.py")
    validate_content = f'''#!/usr/bin/env python3
"""
Compliance validation script for {name}.
Runs all required MCP, A2A, and SKILL.md checks.
"""

import sys
from pathlib import Path

try:
    from mcp_agent_kit.validator import ComplianceValidator
except ImportError:
    for parent in Path(__file__).resolve().parents:
        if (parent / "mcp_agent_kit").exists():
            sys.path.insert(0, str(parent))
            break
    from mcp_agent_kit.validator import ComplianceValidator

from server import create_server

def main():
    server = create_server()
    validator = ComplianceValidator(root_dir=".")
    success = validator.run_all(server_instance=server)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
'''
    with open(validate_path, "w", encoding="utf-8") as f:
        f.write(validate_content)
    os.chmod(validate_path, 0o755)

    # 8. client_test.py
    client_test_path = os.path.join(target_dir, "client_test.py")
    client_test_content = f'''#!/usr/bin/env python3
"""
Dual-Era probe client test for {name}.
Tests modern discovery, legacy boundary, and tool invocation.
"""

import unittest
import sys
from pathlib import Path

try:
    from mcp_agent_kit.client import DualEraMCPClient
except ImportError:
    for parent in Path(__file__).resolve().parents:
        if (parent / "mcp_agent_kit").exists():
            sys.path.insert(0, str(parent))
            break
    from mcp_agent_kit.client import DualEraMCPClient

from server import create_server


class TestLocalAgentClient(unittest.TestCase):
    def setUp(self):
        self.server = create_server()
        self.client = DualEraMCPClient(name="test_probe_client")

    def transport(self, req):
        res = self.server.handle_request_dict(req)
        return res if res is not None else {{}}

    def test_modern_probe_success(self):
        peer = self.client.probe_peer("{name}", self.transport)
        self.assertEqual(peer["era"], "modern")
        self.assertEqual(peer["version"], "2026-07-28")

    def test_tool_call_execution(self):
        self.client.probe_peer("{name}", self.transport)
        tools_res = self.server.handle_request_dict({{
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/list",
            "params": {{"_meta": self.client.build_meta()}},
        }})
        tools = tools_res["result"]["tools"]
        self.client.register_peer_tools("{name}", tools)

        res = self.client.execute_tool_call(
            "calculate_metrics",
            {{"values": [10, 20, 30], "metric_type": "mean"}},
            {{"{name}": self.transport}},
        )
        self.assertFalse(res["result"]["isError"])


if __name__ == "__main__":
    unittest.main()
'''
    with open(client_test_path, "w", encoding="utf-8") as f:
        f.write(client_test_content)
    os.chmod(client_test_path, 0o755)

    # 9. README.md
    readme_path = os.path.join(target_dir, "README.md")
    readme_content = f'''# {name}

Production-ready MCP server scaffold built with `mcp-agent-kit`.

## Overview
{desc}

## Quick Start
```bash
# 1. Run compliance validation
python validate.py

# 2. Run dual-era client probe tests
python client_test.py

# 3. Start MCP server (stdio transport)
python server.py

# 4. Start A2A Agent Card & Task server
python a2a/server.py 8000
```

## Architecture
```
+-------------------------------------------------------+
|                       Claude / Agent                  |
+---------------------------+---------------------------+
                            |
           MCP Protocol     |     A2A Protocol
          (2026-07-28)      |       (v1.0)
                            v                           
+---------------------------+---------------------------+
|                        {name}                         |
|  - server.py (Stateless MCP Engine)                   |
|  - tools/ (Compliant Tool Schemas)                    |
|  - a2a/ (Task Endpoint & Agent Card)                  |
|  - SKILL.md (Portable Agent Skill)                    |
+-------------------------------------------------------+
```

## Adding a New Tool
1. Create a function and tool definition dictionary in `tools/`.
2. Ensure description matches `"Use when X. Do not use for Y."` pattern with annotations (`readOnlyHint` or `destructiveHint`).
3. Register the tool in `server.py` and run `python validate.py`.

## Claude Desktop Configuration
Add to `claude_desktop_config.json`:
```json
{{
  "mcpServers": {{
    "{name}": {{
      "command": "python",
      "args": ["{os.path.abspath(server_path)}"]
    }}
  }}
}}
```

## Claude Code Agent Skill Installation
```bash
cp SKILL.md ~/.claude/skills/{name}.md
```
'''
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)


def main():
    parser = argparse.ArgumentParser(description="Scaffold a production-ready MCP Agent with A2A & SKILL.md packaging.")
    parser.add_argument("name", nargs="?", help="Agent name (must be snake_case)")
    parser.add_argument("--desc", help="One-line description")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL (default: http://localhost:8000)")
    parser.add_argument("--example-tools", action="store_true", default=True, help="Include example tools")
    parser.add_argument("--output-dir", help="Target directory (defaults to agent name)")

    args = parser.parse_args()

    # Interactive prompt mode if arguments not provided
    name = args.name
    if not name:
        if sys.stdin.isatty():
            while True:
                name_input = input("1. Agent name (snake_case, e.g. my_agent): ").strip()
                if validate_agent_name(name_input):
                    name = name_input
                    break
                print("   Error: Name must be snake_case (lowercase letters, digits, underscores).")
        else:
            name = "my_agent"

    if not validate_agent_name(name):
        print(f"Error: Invalid agent name '{name}'. Must be snake_case (e.g. my_agent).", file=sys.stderr)
        sys.exit(1)

    desc = args.desc
    if not desc:
        if sys.stdin.isatty():
            desc_input = input("2. One-line description: ").strip()
            desc = desc_input or f"Use when querying {name} capabilities. Do not use for unrelated operations."
        else:
            desc = f"Use when querying {name} capabilities. Do not use for unrelated operations."

    base_url = args.url
    if not args.desc and sys.stdin.isatty():
        url_input = input(f"3. Base URL [{base_url}]: ").strip()
        if url_input:
            base_url = url_input

    target_dir = args.output_dir or name
    print(f"Scaffolding MCP agent '{name}' into '{target_dir}'...")
    scaffold_agent(
        target_dir=target_dir,
        name=name,
        description=desc,
        base_url=base_url,
        include_example_tools=args.example_tools,
    )
    print(f"✓ Agent '{name}' successfully created in '{target_dir}'.")
    print("Next steps:")
    print(f"  cd {target_dir}")
    print("  python validate.py")


if __name__ == "__main__":
    main()
