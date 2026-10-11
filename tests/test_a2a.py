"""
Tests for A2A Protocol and Task Lifecycle.
Covers:
- Task lifecycle: submitted -> working -> completed
- input_required pause and resume
- Artifact returned on completion
- Tool to A2A skill automatic mapping
"""

import unittest

from mcp_agent_kit.a2a import (
    TaskManager,
    generate_agent_card,
    map_mcp_tools_to_a2a_skills,
)


class TestA2A(unittest.TestCase):
    def setUp(self):
        self.task_manager = TaskManager()

    def test_task_lifecycle_submitted_to_working_to_completed(self):
        """Lifecycle transitions correctly through submitted -> working -> completed."""
        task = self.task_manager.create_or_resume_task({
            "messages": [
                {
                    "role": "user",
                    "parts": [{"type": "text", "text": "Execute analysis task"}],
                }
            ]
        })

        self.assertEqual(task.status, "completed")
        self.assertTrue(len(task.artifacts) > 0)
        self.assertEqual(task.artifacts[0]["name"], "task_output")

    def test_input_required_pause_and_resume(self):
        """Task pauses on input_required state and resumes to completed when input is provided."""
        # 1. Initial request triggers input_required
        task1 = self.task_manager.create_or_resume_task({
            "messages": [
                {
                    "role": "user",
                    "parts": [{"type": "text", "text": "require_input from user for credentials"}],
                }
            ]
        })

        self.assertEqual(task1.status, "input_required")
        task_id = task1.taskId

        # Task can be queried in intermediate state
        queried = self.task_manager.get_task(task_id)
        self.assertIsNotNone(queried)
        self.assertEqual(queried.status, "input_required")

        # 2. Resuming task with required input payload
        resumed = self.task_manager.create_or_resume_task({
            "taskId": task_id,
            "messages": [
                {
                    "role": "user",
                    "parts": [{"type": "text", "text": "Provided credentials token: ABC-123"}],
                }
            ],
        })

        self.assertEqual(resumed.taskId, task_id)
        self.assertEqual(resumed.status, "completed")
        self.assertTrue(len(resumed.artifacts) > 0)

    def test_artifact_returned_on_completion(self):
        """Artifacts are typed and returned upon completion."""
        task = self.task_manager.create_or_resume_task({
            "messages": [
                {
                    "role": "user",
                    "parts": [
                        {"type": "data", "data": {"operation": "generate_report"}},
                        {"type": "text", "text": "Run report"},
                    ],
                }
            ]
        })
        self.assertEqual(task.status, "completed")
        artifact = task.artifacts[0]
        self.assertEqual(artifact["type"], "data")
        self.assertIn("status", artifact["data"])

    def test_mcp_tools_to_a2a_skills_mapping(self):
        """MCP tools automatically map to A2A skills with inputModes and outputModes."""
        tools = [
            {
                "name": "search_database",
                "description": "Use when searching. Do not use for writing.",
                "inputSchema": {"type": "object", "properties": {"q": {"type": "string"}}},
            }
        ]
        skills = map_mcp_tools_to_a2a_skills(tools)
        self.assertEqual(len(skills), 1)
        skill = skills[0]
        self.assertEqual(skill["id"], "search_database")
        self.assertEqual(skill["inputModes"], ["data", "text"])
        self.assertEqual(skill["outputModes"], ["data", "text"])
        self.assertEqual(skill["parameters"], tools[0]["inputSchema"])

        card = generate_agent_card(
            name="test_agent",
            description="Use when testing. Do not use for prod.",
            base_url="http://localhost:8000",
            tools_list=tools,
        )
        self.assertEqual(card["schemaVersion"], "1.0")
        self.assertEqual(card["url"], "http://localhost:8000/a2a")
        self.assertEqual(len(card["skills"]), 1)


if __name__ == "__main__":
    unittest.main()
