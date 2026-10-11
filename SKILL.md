---
name: mcp-agent-kit
description: Use when building, testing, or executing MCP tools and workflows. Do not use for unrelated external operations.
---

# Mcp Agent Kit

Production-ready MCP server scaffold with stateless MCP 2026-07-28, A2A Agent Card, and Agent Skill packaging.

## Overview
Use when building, testing, or executing MCP tools and workflows. Do not use for unrelated external operations.

## Available Tools
- **`calculate_metrics`** [readOnly=True, destructive=False]: Use when analyzing numerical series or computing aggregate metrics. Do not use for unstructured text parsing.

## Instructions & Best Practices
1. Inspect available tools with `tools/list` before initiating operations.
2. Provide all required parameters validated against the schema.
3. If an `input_required` state is returned, prompt for additional inputs and resume.
