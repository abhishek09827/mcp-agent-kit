"""
mcp-agent-kit: Production-ready MCP server scaffold with A2A support and Agent Skill packaging.
"""

from .a2a import generate_agent_card, map_mcp_tools_to_a2a_skills, run_a2a_server, TaskManager
from .client import DualEraMCPClient
from .errors import (
    HEADER_MISMATCH,
    INTERNAL_ERROR,
    INVALID_PARAMS,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    PARSE_ERROR,
    UNSUPPORTED_PROTOCOL_VERSION,
    HeaderMismatchError,
    InternalError,
    InvalidParamsError,
    InvalidRequestError,
    MCPError,
    MethodNotFoundError,
    ParseError,
    UnsupportedProtocolVersionError,
)
from .prompts import PromptRegistry
from .protocol import (
    MODERN_PROTOCOL_VERSION,
    SUPPORTED_PROTOCOL_VERSIONS,
    ClientInfo,
    RequestMeta,
    ServerInfo,
    format_error_response,
    format_legacy_initialize_response,
    format_success_response,
    validate_stateless_request,
)
from .resources import ResourceRegistry
from .server import MCPServer
from .skill import generate_skill_markdown, validate_skill_markdown
from .tools import InputRequired, ToolAnnotations, ToolDefinition, ToolRegistry, validate_tool_schema
from .validator import ComplianceValidator

__version__ = "0.1.0"

__all__ = [
    "MCPServer",
    "DualEraMCPClient",
    "ToolRegistry",
    "ToolAnnotations",
    "ToolDefinition",
    "InputRequired",
    "validate_tool_schema",
    "ResourceRegistry",
    "PromptRegistry",
    "ComplianceValidator",
    "TaskManager",
    "generate_agent_card",
    "map_mcp_tools_to_a2a_skills",
    "run_a2a_server",
    "generate_skill_markdown",
    "validate_skill_markdown",
    "MODERN_PROTOCOL_VERSION",
    "SUPPORTED_PROTOCOL_VERSIONS",
    "RequestMeta",
    "ServerInfo",
    "ClientInfo",
    "MCPError",
    "UnsupportedProtocolVersionError",
    "InvalidParamsError",
    "HeaderMismatchError",
]
