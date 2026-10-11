"""
Unified MCP Agent Kit compliance validation runner.
Executes all required compliance checks for:
- MCP server/discover
- tools/list deterministic ordering
- tool schema design rules
- A2A agent.json card
- SKILL.md portable core
- Dual-era client probe
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

from .client import DualEraMCPClient
from .protocol import MODERN_PROTOCOL_VERSION
from .server import MCPServer
from .skill import validate_skill_markdown


class ComplianceValidator:
    """Runs compliance checks on an MCP agent package."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        self.results: List[Tuple[bool, str]] = []

    def run_all(self, server_instance: Optional[MCPServer] = None) -> bool:
        """Runs all checks and prints formatted ✓ / ✗ output."""
        self.results.clear()

        # 1. MCP server/discover responds correctly
        self._check_server_discover(server_instance)

        # 2. tools/list is deterministically ordered
        self._check_tools_ordering(server_instance)

        # 3. all tool schemas pass design rules
        self._check_tool_schemas(server_instance)

        # 4. A2A agent.json is valid
        self._check_a2a_agent_json()

        # 5. SKILL.md portable core is valid
        self._check_skill_md()

        # 6. dual-era client probe works against local server
        self._check_dual_era_probe(server_instance)

        # Print report
        all_passed = True
        for success, message in self.results:
            if success:
                print(f"✓ {message}")
            else:
                all_passed = False
                print(f"✗ {message}")

        return all_passed

    def _check_server_discover(self, server: Optional[MCPServer]) -> None:
        try:
            srv = server or MCPServer()
            req = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "server/discover",
                "params": {
                    "_meta": {
                        "protocolVersion": MODERN_PROTOCOL_VERSION,
                        "clientCapabilities": {},
                        "clientInfo": {"name": "validator", "version": "1.0.0"},
                    }
                },
            }
            resp = srv.handle_request_dict(req)
            if not resp or "result" not in resp:
                self.results.append((False, "MCP server/discover failed: no result returned"))
                return

            res = resp["result"]
            if res.get("resultType") != "complete":
                self.results.append((False, "MCP server/discover resultType is not 'complete'"))
                return

            if "supportedVersions" not in res or MODERN_PROTOCOL_VERSION not in res["supportedVersions"]:
                self.results.append((False, f"MCP server/discover missing supportedVersion '{MODERN_PROTOCOL_VERSION}'"))
                return

            if "serverInfo" not in res or not res["serverInfo"].get("name"):
                self.results.append((False, "MCP server/discover missing serverInfo"))
                return

            self.results.append((True, "MCP server/discover responds correctly"))
        except Exception as exc:
            self.results.append((False, f"MCP server/discover error: {str(exc)}"))

    def _check_tools_ordering(self, server: Optional[MCPServer]) -> None:
        try:
            srv = server or MCPServer()
            # Register deliberately in reverse order to test sorting
            srv.tools.register(
                name="z_test_tool",
                description="Use when testing ordering. Do not use for production.",
                input_schema={"type": "object"},
                annotations={"readOnlyHint": True},
                handler=lambda args: "ok",
            )
            srv.tools.register(
                name="a_test_tool",
                description="Use when testing ordering. Do not use for production.",
                input_schema={"type": "object"},
                annotations={"readOnlyHint": True},
                handler=lambda args: "ok",
            )

            req = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {
                    "_meta": {
                        "protocolVersion": MODERN_PROTOCOL_VERSION,
                        "clientCapabilities": {},
                        "clientInfo": {"name": "validator", "version": "1.0.0"},
                    }
                },
            }
            resp = srv.handle_request_dict(req)
            tool_list = resp["result"]["tools"]
            names = [t["name"] for t in tool_list]
            if names != sorted(names):
                self.results.append((False, f"tools/list is not deterministically ordered: {names}"))
                return

            self.results.append((True, "tools/list is deterministically ordered"))
        except Exception as exc:
            self.results.append((False, f"tools/list check error: {str(exc)}"))

    def _check_tool_schemas(self, server: Optional[MCPServer]) -> None:
        try:
            srv = server or MCPServer()
            validation_errors = srv.tools.validate_all()
            if validation_errors:
                for tool_name, errs in validation_errors.items():
                    for err in errs:
                        self.results.append((False, f"{tool_name} {err}"))
            else:
                self.results.append((True, "all tool schemas pass design rules"))
        except Exception as exc:
            self.results.append((False, f"Tool schema validation error: {str(exc)}"))

    def _check_a2a_agent_json(self) -> None:
        paths = [
            os.path.join(self.root_dir, "a2a", "agent.json"),
            os.path.join(self.root_dir, ".well-known", "agent.json"),
        ]
        found_path = None
        for p in paths:
            if os.path.exists(p):
                found_path = p
                break

        if not found_path:
            self.results.append((False, "A2A agent.json not found in a2a/agent.json or .well-known/agent.json"))
            return

        try:
            with open(found_path, "r", encoding="utf-8") as f:
                card = json.load(f)

            if card.get("schemaVersion") != "1.0":
                self.results.append((False, "A2A agent.json schemaVersion is not '1.0'"))
                return

            if not card.get("name") or not card.get("url"):
                self.results.append((False, "A2A agent.json missing name or url"))
                return

            if "skills" not in card or not isinstance(card["skills"], list):
                self.results.append((False, "A2A agent.json missing skills array"))
                return

            self.results.append((True, "A2A agent.json is valid"))
        except Exception as exc:
            self.results.append((False, f"A2A agent.json invalid JSON: {str(exc)}"))

    def _check_skill_md(self) -> None:
        skill_path = os.path.join(self.root_dir, "SKILL.md")
        if not os.path.exists(skill_path):
            self.results.append((False, "SKILL.md not found at project root"))
            return

        try:
            with open(skill_path, "r", encoding="utf-8") as f:
                content = f.read()

            dir_name = os.path.basename(self.root_dir)
            errs = validate_skill_markdown(content, expected_dir_name=dir_name)
            if errs:
                for err in errs:
                    self.results.append((False, f"SKILL.md portable core error: {err}"))
            else:
                self.results.append((True, "SKILL.md portable core is valid"))
        except Exception as exc:
            self.results.append((False, f"SKILL.md check error: {str(exc)}"))

    def _check_dual_era_probe(self, server: Optional[MCPServer]) -> None:
        try:
            srv = server or MCPServer(name="local_probe_target")
            client = DualEraMCPClient(name="test_validator_client")

            def transport(req: Dict[str, Any]) -> Dict[str, Any]:
                res = srv.handle_request_dict(req)
                return res if res is not None else {}

            peer_record = client.probe_peer("local_probe_target", transport)
            if peer_record.get("era") == "modern":
                self.results.append((True, "dual-era client probe works against local server"))
            else:
                self.results.append((False, f"dual-era probe failed to negotiate modern era: {peer_record}"))
        except Exception as exc:
            self.results.append((False, f"dual-era client probe error: {str(exc)}"))
