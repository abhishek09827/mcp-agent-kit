# mcp-agent-kit

`mcp-agent-kit` is an enterprise-grade scaffolding kit and runtime foundation that enables developers to build, validate, and ship a fully compliant, production-ready Model Context Protocol (MCP) server with Agent-to-Agent (A2A) protocol support and portable Agent Skill (`SKILL.md`) packaging in under 30 minutes. Built entirely with the Python standard library for zero runtime dependencies in the protocol core, it enforces strict stateless MCP specification compliance (version 2026-07-28), deterministic resource listing, schema design validation, dual-era negotiation, and automated tool-to-skill card mapping.

---



https://github.com/user-attachments/assets/17b0c72c-3a48-4e5c-921f-3ddf488e3e2d



## Quick Start (5 Lines)

```bash
pip install mcp-agent-kit
create-mcp-agent my_agent
cd my_agent
python validate.py
python server.py
```

---

## End-to-End Demo Walkthrough (with Real Outputs)

Follow these step-by-step instructions to scaffold, validate, test, and run an MCP agent end-to-end.

### Step 1: Scaffold a New Agent
Run the generator CLI to create a new agent (e.g. `demo_agent`):

```bash
python -m mcp_agent_kit demo_agent --desc "Use when computing numerical metrics and data summaries. Do not use for unstructured text parsing."
```

**Terminal Output:**
```text
Scaffolding MCP agent 'demo_agent' into 'demo_agent'...
✓ Agent 'demo_agent' successfully created in 'demo_agent'.
Next steps:
  cd demo_agent
  python validate.py
```

---

### Step 2: Run Compliance Validation
Navigate into the agent directory and execute `validate.py`:

```bash
cd demo_agent
python validate.py
```

**Terminal Output:**
```text
✓ MCP server/discover responds correctly
✓ tools/list is deterministically ordered
✓ all tool schemas pass design rules
✓ A2A agent.json is valid
✓ SKILL.md portable core is valid
✓ dual-era client probe works against local server
```

---

### Step 3: Run the Dual-Era Probe Client Test
Verify client negotiation and tool execution via `client_test.py`:

```bash
python client_test.py
```

**Terminal Output:**
```text
..
----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

---

### Step 4: Test Stateless MCP 2026-07-28 Server via Stdio
Send raw JSON-RPC requests to `server.py` over stdin. Notice every request independently carries `_meta`:

#### Request A: Discovery (`server/discover`)
**Stdin Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "server/discover",
  "params": {
    "_meta": {
      "protocolVersion": "2026-07-28",
      "clientCapabilities": {},
      "clientInfo": {"name": "demo-client", "version": "1.0.0"}
    }
  }
}
```

**Stdout Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "resultType": "complete",
    "serverInfo": {
      "name": "demo_agent",
      "version": "1.0.0"
    },
    "supportedVersions": [
      "2026-07-28"
    ],
    "capabilities": {
      "tools": {"listChanged": false},
      "resources": {"subscribe": false, "listChanged": false},
      "prompts": {"listChanged": false}
    },
    "ttlMs": 3600000,
    "cacheScope": "workspace"
  }
}
```

#### Request B: Tool Execution (`tools/call`)
**Stdin Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "_meta": {
      "protocolVersion": "2026-07-28",
      "clientCapabilities": {},
      "clientInfo": {"name": "demo-client", "version": "1.0.0"}
    },
    "name": "calculate_metrics",
    "arguments": {
      "metric_type": "mean",
      "values": [12.5, 45.0, 78.5, 92.0]
    }
  }
}
```

**Stdout Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "resultType": "complete",
    "serverInfo": {
      "name": "demo_agent",
      "version": "1.0.0"
    },
    "content": [
      {
        "type": "text",
        "text": "{\"metric\": \"mean\", \"value\": 57.0, \"count\": 4}"
      }
    ],
    "isError": false
  }
}
```

---

### Step 5: Test A2A Agent Card & Task Lifecycle API
Start the HTTP server on port 8000:

```bash
python a2a/server.py 8000
```

#### A. Fetch the Agent Card
```bash
curl -s http://localhost:8000/.well-known/agent.json
```

**HTTP 200 Response:**
```json
{
  "schemaVersion": "1.0",
  "name": "demo_agent",
  "description": "Use when computing numerical metrics and data summaries. Do not use for unstructured text parsing.",
  "url": "http://localhost:8000/a2a",
  "version": "1.0.0",
  "skills": [
    {
      "id": "calculate_metrics",
      "name": "calculate_metrics",
      "description": "Use when analyzing numerical series or computing aggregate metrics. Do not use for unstructured text parsing.",
      "inputModes": ["data", "text"],
      "outputModes": ["data", "text"],
      "parameters": {
        "type": "object",
        "properties": {
          "metric_type": {"type": "string", "enum": ["mean", "sum", "max", "min"]},
          "values": {"type": "array", "items": {"type": "number"}}
        },
        "required": ["values"]
      }
    }
  ],
  "capabilities": {
    "streaming": true,
    "pushNotifications": false
  }
}
```

#### B. Send a Task (`POST /a2a/tasks/send`)
```bash
curl -s -X POST http://localhost:8000/a2a/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "parts": [
          {"type": "text", "text": "Compute quarterly summary metrics"},
          {"type": "data", "data": {"quarter": "Q3", "values": [100, 200, 300]}}
        ]
      }
    ]
  }'
```

**HTTP 200 Response:**
```json
{
  "taskId": "task_e8ca2985820b",
  "status": "completed"
}
```

#### C. Query Task Status and Output Artifact (`GET /a2a/tasks/{id}`)
```bash
curl -s http://localhost:8000/a2a/tasks/task_e8ca2985820b
```

**HTTP 200 Response:**
```json
{
  "taskId": "task_e8ca2985820b",
  "status": "completed",
  "messages": [
    {
      "role": "user",
      "parts": [
        {"type": "text", "text": "Compute quarterly summary metrics"},
        {"type": "data", "data": {"quarter": "Q3", "values": [100, 200, 300]}}
      ]
    }
  ],
  "artifacts": [
    {
      "name": "task_output",
      "type": "data",
      "data": {
        "status": "success",
        "processed_parts": 1
      }
    }
  ],
  "created_at": 1791728650.129,
  "updated_at": 1791728650.130
}
```

---

### Step 6: Run Comprehensive Test Suite
Run the 20-test automated compliance and unit testing suite:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

**Terminal Output:**
```text
test_artifact_returned_on_completion (test_a2a.TestA2A.test_artifact_returned_on_completion) ... ok
test_input_required_pause_and_resume (test_a2a.TestA2A.test_input_required_pause_and_resume) ... ok
test_mcp_tools_to_a2a_skills_mapping (test_a2a.TestA2A.test_mcp_tools_to_a2a_skills_mapping) ... ok
test_task_lifecycle_submitted_to_working_to_completed (test_a2a.TestA2A.test_task_lifecycle_submitted_to_working_to_completed) ... ok
test_allowlisted_peer_timeout_stays_unavailable (test_mcp_client.TestMCPClient.test_allowlisted_peer_timeout_stays_unavailable) ... ok
test_allowlisted_peer_valid_initialize_selects_legacy (test_mcp_client.TestMCPClient.test_allowlisted_peer_valid_initialize_selects_legacy) ... ok
test_ambiguous_signal_fails_closed_without_allowlist (test_mcp_client.TestMCPClient.test_ambiguous_signal_fails_closed_without_allowlist) ... ok
test_collision_produces_prefixed_name_never_silent_overwrite (test_mcp_client.TestMCPClient.test_collision_produces_prefixed_name_never_silent_overwrite) ... ok
test_recognized_modern_errors_never_trigger_initialize (test_mcp_client.TestMCPClient.test_recognized_modern_errors_never_trigger_initialize) ... ok
test_every_request_repeats_meta_independently (test_mcp_server.TestMCPServer.test_every_request_repeats_meta_independently) ... ok
test_list_results_stable_regardless_of_insertion_order (test_mcp_server.TestMCPServer.test_list_results_stable_regardless_of_insertion_order) ... ok
test_server_never_initiates_request (test_mcp_server.TestMCPServer.test_server_never_initiates_request) ... ok
test_stdio_loop (test_mcp_server.TestMCPServer.test_stdio_loop) ... ok
test_tool_call_returns_isError_true_on_executor_failure (test_mcp_server.TestMCPServer.test_tool_call_returns_isError_true_on_executor_failure) ... ok
test_unsupported_protocol_version_error (test_mcp_server.TestMCPServer.test_unsupported_protocol_version_error) ... ok
test_scaffold_creates_complete_working_structure (test_scaffolder.TestScaffolder.test_scaffold_creates_complete_working_structure) ... ok
test_description_length_and_pattern_checks (test_skill.TestSkillPackage.test_description_length_and_pattern_checks) ... ok
test_generate_skill_markdown_creates_compliant_output (test_skill.TestSkillPackage.test_generate_skill_markdown_creates_compliant_output) ... ok
test_skill_name_matches_directory (test_skill.TestSkillPackage.test_skill_name_matches_directory) ... ok
test_unknown_runtime_extensions_rejected_in_portable_core (test_skill.TestSkillPackage.test_unknown_runtime_extensions_rejected_in_portable_core) ... ok

----------------------------------------------------------------------
Ran 20 tests in 0.033s

OK
```

---

## Architecture

```
+=============================================================================+
|                      Host Environment / AI Assistant                        |
|             (Claude Desktop, Claude Code, Anthropic API, Custom Host)       |
+=============================================================================+
        |                                   |                           |
        | [Stateless JSON-RPC]              | [REST / Task Lifecycle]   | [Progressive Disclosure]
        | (stdio transport)                 | (HTTP /a2a)               | (Agent Skill)
        v                                   v                           v
+-----------------------+       +-----------------------+   +-----------------+
|   MCP Server Core     |       |   A2A Task Server     |   |    SKILL.md     |
|   (Stateless 2026)    |       |       (v1.0)          |   | (Portable Core) |
+-----------------------+       +-----------------------+   +-----------------+
| - server/discover     |       | - /.well-known/agent  |   | - Frontmatter   |
| - tools/list & call   |<----->| - tasks/send (Parts)  |   | - Workflows     |
| - resources/list&read | Auto- | - tasks/{id}          |   | - Tool index    |
| - prompts/list & get  | Map   | - Artifacts pipeline  |   |                 |
| - input_required mode |       | - input_required pause|   |                 |
+-----------------------+       +-----------------------+   +-----------------+
        |
        +-----------------------------------+
                                            v
                        +---------------------------------------+
                        |       Compliant Tool Schemas          |
                        | - snake_case names                    |
                        | - "Use when X. Do not use for Y."     |
                        | - readOnlyHint / destructiveHint      |
                        | - Deterministic alphabetical order    |
                        +---------------------------------------+
```

---

## How to Add a New Tool (3 Steps)

### Step 1: Define the function & schema in `tools/`
Create a new file in `tools/` (e.g., `tools/user_ops.py`):

```python
from typing import Any, Dict

def get_user_profile(arguments: Dict[str, Any]) -> Dict[str, Any]:
    user_id = arguments["user_id"]
    return {"user_id": user_id, "status": "active", "tier": "enterprise"}

TOOL_DEFINITION = {
    "name": "get_user_profile",
    "description": "Use when retrieving user profile details by ID. Do not use for updating account settings.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "Unique user ID"}
        },
        "required": ["user_id"]
    },
    "annotations": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    },
    "handler": get_user_profile
}
```

### Step 2: Register the tool in `server.py`
In `server.py`, register the tool definition with the server engine:

```python
from tools.user_ops import TOOL_DEFINITION as USER_TOOL

srv.tools.register(
    name=USER_TOOL["name"],
    description=USER_TOOL["description"],
    input_schema=USER_TOOL["inputSchema"],
    annotations=USER_TOOL["annotations"],
    handler=USER_TOOL["handler"]
)
```

### Step 3: Verify with `validate.py`
```bash
python validate.py
```

---

## How to Install in Claude Desktop

Add your server configuration to your `claude_desktop_config.json`:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "my_agent": {
      "command": "python",
      "args": ["/absolute/path/to/my_agent/server.py"]
    }
  }
}
```

---

## How to Install as Agent Skill in Claude Code

Run this single command to install as a project-level or global Agent Skill:

```bash
mkdir -p ~/.claude/skills && cp SKILL.md ~/.claude/skills/my_agent.md
```

Or for project-level scope in your repository:

```bash
mkdir -p .claude/skills && cp SKILL.md .claude/skills/my_agent.md
```

---

## Validation Engine (`validate.py`)

Run the complete compliance suite with a single command:

```bash
python validate.py
```

### Example Output

```text
✓ MCP server/discover responds correctly
✓ tools/list is deterministically ordered
✓ all tool schemas pass design rules
✓ A2A agent.json is valid
✓ SKILL.md portable core is valid
✓ dual-era client probe works against local server
```

If a tool violates schema rules (e.g. missing annotations or improper description formatting), the validator detects and reports it with granular diagnostics:

```text
✗ notes_delete missing readOnlyHint or destructiveHint (at least one must be true)
```

---

## What `mcp-agent-kit` Implements

### 1. Stateless MCP Specification (2026-07-28)
- **Zero Stateful Coupling**: Every JSON-RPC request must carry a valid `_meta` block (`protocolVersion`, `clientCapabilities`, `clientInfo`) and is validated independently without session reuse.
- **Envelope Contracts**: Every successful response includes `resultType: "complete"` and server identity (`serverInfo`).
- **Input Required Protocol**: Handlers needing interaction yield `resultType: "input_required"`. The server never initiates unsolicited requests to the client.
- **Deterministic Alphabetical Sorting**: All collections (`tools/list`, `resources/list`, `prompts/list`) are deterministically sorted.
- **Stdio Rules**: JSON-RPC is strictly emitted to `stdout` with newline flushing; diagnostics and logs are written exclusively to `stderr`.

### 2. Dual-Era Probe Client & Namespace Merger
- **Probing State Machine**: Starts with modern `server/discover`.
- **Fail-Closed Security**: Recognized modern errors (`-32020`, `-32021`, `-32022`) correct and retry without falling back to initialize. Ambiguous signals fail closed unless explicitly allowlisted.
- **Multi-Server Namespace Merging**: Colliding tool names are prefixed (`server/tool_name`), avoiding silent overwrites while preserving local names.

### 3. A2A Protocol (Agent-to-Agent v1.0)
- Auto-generates `/.well-known/agent.json` from registered tools.
- Task lifecycle management: `submitted` → `working` → `completed` | `failed` | `input_required`.
- Rich message parts (`text`, `file`, `data`) and typed output artifacts upon completion.

### 4. Portable Agent Skill (`SKILL.md`)
- YAML frontmatter with strict portable core validation (`name` matches directory, `description` 20–1024 characters with `"Use when X. Do not use for Y."` pattern).
- Zero unknown runtime extensions.

---

## Architecture Boundaries (What NOT to Build)

- **Authentication**: Zero hardcoded auth in core protocol. To add auth, attach a bearer token validator in `a2a/server.py` or middleware headers in `MCPServer._dispatch`.
- **Database**: Zero database dependencies. In-memory task and state stores are provided with cleanly documented swap points (`TaskManager.task_executor`).
- **Dependencies**: Protocol core uses Python standard library only (`json`, `dataclasses`, `http.server`, `re`, `sys`). Flask is optional: `pip install mcp-agent-kit[a2a]`.

---

## Specification References

- [Model Context Protocol (MCP) Specification 2026-07-28](https://spec.modelcontextprotocol.io)
- [Agent-to-Agent (A2A) Protocol Specification v1.0](https://a2a-protocol.org)
- [Portable Agent Skill Specification](https://docs.anthropic.com/en/docs/agents-and-tools)

---
