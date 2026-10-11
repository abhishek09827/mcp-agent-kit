"""
Portable Agent Skill (SKILL.md) generator and validator.
Complies with Portable Core validation:
- name matches directory name
- description 20–1024 chars and matches 'Use when X. Do not use for Y.' pattern
- no unknown runtime extensions in portable core frontmatter
"""

import os
import re
from typing import Any, Dict, List, Optional, Tuple

DESC_PATTERN = re.compile(r"Use when .+\. Do not use for .+\.", re.DOTALL)
ALLOWED_PORTABLE_CORE_KEYS = {"name", "description"}


def format_title(snake_name: str) -> str:
    """Formats snake_case or kebab-case name into Title Case."""
    return " ".join(word.capitalize() for word in re.split(r"[_\-]+", snake_name))


def generate_skill_markdown(
    agent_name: str,
    description: str,
    tools_list: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Generates a portable SKILL.md file.
    Ensures description complies with the pattern 'Use when X. Do not use for Y.'
    """
    tools = tools_list or []
    title = format_title(agent_name)

    # Ensure description matches required pattern if not already formatted
    desc = description.strip()
    if not DESC_PATTERN.search(desc):
        desc = f"Use when interacting with {agent_name} services. Do not use for unrelated operations. {desc}".strip()

    # Generate tool documentation list
    tool_sections: List[str] = []
    if tools:
        for t in tools:
            t_name = t.get("name", "unknown")
            t_desc = t.get("description", "")
            hints = t.get("annotations", {})
            hint_str = f" [readOnly={hints.get('readOnlyHint', False)}, destructive={hints.get('destructiveHint', False)}]"
            tool_sections.append(f"- **`{t_name}`**{hint_str}: {t_desc}")
    else:
        tool_sections.append("- (No tools registered yet)")

    tools_doc = "\n".join(tool_sections)

    return f"""---
name: {agent_name}
description: {desc}
---

# {title}

Automated workflows and capabilities powered by the `{agent_name}` MCP server.

## Overview
{desc}

## Available Tools
{tools_doc}

## Instructions & Best Practices
1. Inspect available tools before initiating tool calls.
2. Provide all required parameters validated against the schema.
3. If an `input_required` state is returned, request the needed parameters and resume the workflow.
"""


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str, List[str]]:
    """
    Parses YAML frontmatter from markdown content without third-party dependencies.
    Returns: (frontmatter_dict, markdown_body, errors)
    """
    errors: List[str] = []
    frontmatter: Dict[str, Any] = {}

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        errors.append("SKILL.md must start with '---' frontmatter delimiter")
        return frontmatter, content, errors

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        errors.append("SKILL.md frontmatter is missing closing '---' delimiter")
        return frontmatter, content, errors

    yaml_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1:])

    # Simple YAML key-value parser for portable core
    current_key = None
    for line in yaml_lines:
        line_str = line.strip()
        if not line_str or line_str.startswith("#"):
            continue

        if ":" in line_str:
            key, val = line_str.split(":", 1)
            key = key.strip()
            val = val.strip().strip("\"'")
            frontmatter[key] = val
            current_key = key
        elif current_key and line.startswith("  "):
            # Multi-line continuation
            frontmatter[current_key] += " " + line_str.strip("\"'")

    return frontmatter, body, errors


def validate_skill_file(file_path: str) -> List[str]:
    """Validates a SKILL.md file on disk."""
    if not os.path.exists(file_path):
        return [f"SKILL.md file not found at: {file_path}"]

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    dir_name = os.path.basename(os.path.dirname(os.path.abspath(file_path)))
    return validate_skill_markdown(content, expected_dir_name=dir_name)


def validate_skill_markdown(content: str, expected_dir_name: Optional[str] = None) -> List[str]:
    """
    Validates SKILL.md content against Portable Core rules:
    - name matches directory name
    - description 20–1024 chars
    - description matches 'Use when X. Do not use for Y.' pattern
    - no unknown runtime extensions in portable core
    """
    frontmatter, _, parse_errors = parse_frontmatter(content)
    if parse_errors:
        return parse_errors

    errors: List[str] = []

    # 1. No unknown runtime extensions in portable core
    for key in frontmatter.keys():
        if key not in ALLOWED_PORTABLE_CORE_KEYS:
            errors.append(f"Unknown runtime extension in portable core: '{key}'")

    # 2. Name validation
    name = frontmatter.get("name")
    if not name or not isinstance(name, str):
        errors.append("Frontmatter missing required 'name' field")
    else:
        name = name.strip()
        if expected_dir_name:
            # Normalize comparisons for snake_case and kebab-case directory names
            norm_name = name.replace("-", "_").lower()
            norm_dir = expected_dir_name.replace("-", "_").lower()
            if norm_name != norm_dir:
                errors.append(
                    f"SKILL.md name '{name}' does not match directory name '{expected_dir_name}'"
                )

    # 3. Description validation
    desc = frontmatter.get("description")
    if not desc or not isinstance(desc, str):
        errors.append("Frontmatter missing required 'description' field")
    else:
        desc = desc.strip()
        if len(desc) < 20 or len(desc) > 1024:
            errors.append(f"Description length is {len(desc)} chars; must be between 20 and 1024 chars")
        if not DESC_PATTERN.search(desc):
            errors.append("Description does not match pattern: 'Use when X. Do not use for Y.'")

    return errors
