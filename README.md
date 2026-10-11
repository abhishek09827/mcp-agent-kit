# mcp-agent-kit

`mcp-agent-kit` is an enterprise-grade scaffolding kit and runtime foundation that enables developers to build, validate, and ship a fully compliant, production-ready Model Context Protocol (MCP) server with Agent-to-Agent (A2A) protocol support and portable Agent Skill (`SKILL.md`) packaging in under 30 minutes. Built entirely with the Python standard library for zero runtime dependencies in the protocol core, it enforces strict stateless MCP specification compliance (version 2026-07-28), deterministic resource listing, schema design validation, dual-era negotiation, and automated tool-to-skill card mapping.

---

## Quick Start (5 Lines)

```bash
pip install mcp-agent-kit
create-mcp-agent my_agent
cd my_agent
python validate.py
python server.py
```

*(You can also run directly without installation via `python -m mcp_agent_kit my_agent` or clone this repository as a GitHub template).*

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

## License

MIT © [Abhishek Kaushik](https://github.com/abhishekk09827)
