"""
Tests for create-mcp-agent scaffolder CLI and end-to-end generation.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from mcp_agent_kit.cli import scaffold_agent
from mcp_agent_kit.validator import ComplianceValidator


class TestScaffolder(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_mcp_scaffold_")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_scaffold_creates_complete_working_structure(self):
        """Scaffolding generates all required files and passes compliance validation."""
        target_agent = os.path.join(self.test_dir, "my_scaffolded_agent")
        scaffold_agent(
            target_dir=target_agent,
            name="my_scaffolded_agent",
            description="Use when handling my_scaffolded_agent tasks. Do not use for other tasks.",
            base_url="http://localhost:8000",
            include_example_tools=True,
        )

        expected_files = [
            "server.py",
            "tools/__init__.py",
            "tools/example.py",
            "a2a/server.py",
            "a2a/agent.json",
            "client_test.py",
            "SKILL.md",
            "validate.py",
            "README.md",
        ]

        for rel_file in expected_files:
            file_path = os.path.join(target_agent, rel_file)
            self.assertTrue(os.path.exists(file_path), f"Missing generated file: {rel_file}")

        # Run ComplianceValidator in the scaffolded directory
        validator = ComplianceValidator(root_dir=target_agent)
        # Import generated server
        sys.path.insert(0, target_agent)
        try:
            import server as agent_server_module
            srv = agent_server_module.create_server()
            success = validator.run_all(server_instance=srv)
            self.assertTrue(success, "Generated agent failed compliance validation")
        finally:
            if target_agent in sys.path:
                sys.path.remove(target_agent)


if __name__ == "__main__":
    unittest.main()
