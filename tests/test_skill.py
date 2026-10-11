"""
Tests for SKILL.md portable core generation and validation.
Covers:
- SKILL.md name matches directory
- Description passes length and pattern checks ('Use when X. Do not use for Y.')
- Unknown runtime extensions in portable core rejection
"""

import unittest

from mcp_agent_kit.skill import (
    generate_skill_markdown,
    validate_skill_markdown,
)


class TestSkillPackage(unittest.TestCase):
    def test_skill_name_matches_directory(self):
        """SKILL.md frontmatter name must match directory name."""
        content = """---
name: my_agent
description: Use when running my_agent workflows. Do not use for other tasks.
---

# My Agent
"""
        # Matching dir
        errors = validate_skill_markdown(content, expected_dir_name="my_agent")
        self.assertEqual(len(errors), 0)

        # Mismatched dir
        errs_mismatch = validate_skill_markdown(content, expected_dir_name="completely_different_dir")
        self.assertTrue(any("does not match directory" in e for e in errs_mismatch))

    def test_description_length_and_pattern_checks(self):
        """Description must be 20-1024 chars and match 'Use when X. Do not use for Y.' pattern."""
        # Valid description
        valid_content = """---
name: valid_skill
description: Use when analyzing log files. Do not use for modifying files directly.
---

# Valid Skill
"""
        errs = validate_skill_markdown(valid_content, expected_dir_name="valid_skill")
        self.assertEqual(len(errs), 0)

        # Too short (<20 chars)
        short_content = """---
name: valid_skill
description: Use when X.
---
"""
        short_errs = validate_skill_markdown(short_content, expected_dir_name="valid_skill")
        self.assertTrue(any("between 20 and 1024" in e for e in short_errs))

        # Missing pattern
        no_pattern_content = """---
name: valid_skill
description: This is a sufficiently long description that unfortunately does not follow the required pattern at all.
---
"""
        pattern_errs = validate_skill_markdown(no_pattern_content, expected_dir_name="valid_skill")
        self.assertTrue(any("does not match pattern" in e for e in pattern_errs))

    def test_unknown_runtime_extensions_rejected_in_portable_core(self):
        """Portable core must not contain unknown runtime extensions in frontmatter."""
        content_with_unknown = """---
name: my_skill
description: Use when running workflows. Do not use for external jobs.
customExtensionProperty: true
runtimeConfig:
  timeout: 50
---
"""
        errs = validate_skill_markdown(content_with_unknown, expected_dir_name="my_skill")
        self.assertTrue(any("Unknown runtime extension" in e for e in errs))

    def test_generate_skill_markdown_creates_compliant_output(self):
        """generate_skill_markdown produces frontmatter that passes validation."""
        generated = generate_skill_markdown(
            agent_name="sample_agent",
            description="Use when handling sample actions. Do not use for other agents.",
            tools_list=[
                {
                    "name": "sample_tool",
                    "description": "Use when sampling. Do not use for prod.",
                    "annotations": {"readOnlyHint": True, "destructiveHint": False},
                }
            ],
        )
        errs = validate_skill_markdown(generated, expected_dir_name="sample_agent")
        self.assertEqual(len(errs), 0)


if __name__ == "__main__":
    unittest.main()
