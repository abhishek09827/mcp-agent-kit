"""
A2A (Agent-to-Agent) Protocol implementation.
Includes Agent Card generation (/.well-known/agent.json),
tool-to-skill automated mapping, and /a2a task lifecycle endpoint.
Standard library only (with optional Flask adapter).
"""

from dataclasses import dataclass, field
import http.server
import json
import re
import threading
import time
from typing import Any, Callable, Dict, List, Optional
import urllib.parse
import uuid


@dataclass
class MessagePart:
    type: str  # text, file, data
    content: Any

    def to_dict(self) -> Dict[str, Any]:
        if self.type == "text":
            return {"type": "text", "text": str(self.content)}
        elif self.type == "file":
            if isinstance(self.content, dict):
                return {"type": "file", **self.content}
            return {"type": "file", "uri": str(self.content)}
        elif self.type == "data":
            return {"type": "data", "data": self.content}
        return {"type": self.type, "content": self.content}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MessagePart":
        part_type = data.get("type", "text")
        if part_type == "text":
            return cls(type="text", content=data.get("text", ""))
        elif part_type == "file":
            return cls(type="file", content=data)
        elif part_type == "data":
            return cls(type="data", content=data.get("data", {}))
        return cls(type=part_type, content=data)


@dataclass
class Artifact:
    name: str
    type: str  # text, file, data
    data: Any

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "data": self.data,
        }


@dataclass
class A2ATask:
    taskId: str
    status: str  # submitted -> working -> completed | failed | input_required
    messages: List[Dict[str, Any]] = field(default_factory=list)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        res: Dict[str, Any] = {
            "taskId": self.taskId,
            "status": self.status,
            "messages": self.messages,
            "artifacts": self.artifacts,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.error:
            res["error"] = self.error
        return res


def map_mcp_tools_to_a2a_skills(tools_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Maps MCP tools list automatically to A2A skills with matching inputModes and outputModes.
    """
    skills: List[Dict[str, Any]] = []
    for tool in tools_list:
        skills.append(
            {
                "id": tool.get("name", ""),
                "name": tool.get("name", ""),
                "description": tool.get("description", ""),
                "inputModes": ["data", "text"],
                "outputModes": ["data", "text"],
                "parameters": tool.get("inputSchema", {}),
            }
        )
    return skills


def generate_agent_card(
    name: str,
    description: str,
    base_url: str = "http://localhost:8000",
    tools_list: Optional[List[Dict[str, Any]]] = None,
    version: str = "1.0.0",
) -> Dict[str, Any]:
    """
    Generates A2A Agent Card compliant with schemaVersion 1.0.
    """
    tools = tools_list or []
    skills = map_mcp_tools_to_a2a_skills(tools)
    clean_url = base_url.rstrip("/")
    return {
        "schemaVersion": "1.0",
        "name": name,
        "description": description,
        "url": f"{clean_url}/a2a",
        "version": version,
        "skills": skills,
        "capabilities": {
            "streaming": True,
            "pushNotifications": False,
        },
    }


class TaskManager:
    """Manages A2A task lifecycle: submitted -> working -> completed | failed | input_required."""

    def __init__(self, task_executor: Optional[Callable[[A2ATask], None]] = None):
        self._tasks: Dict[str, A2ATask] = {}
        self._lock = threading.Lock()
        self.task_executor = task_executor or self._default_executor

    def create_or_resume_task(self, data: Dict[str, Any]) -> A2ATask:
        with self._lock:
            task_id = data.get("taskId")
            if task_id and task_id in self._tasks:
                task = self._tasks[task_id]
                # Resume input_required task
                if task.status == "input_required":
                    task.status = "working"
                    task.updated_at = time.time()
                    if "messages" in data:
                        task.messages.extend(data["messages"])
                    self.task_executor(task)
                    return task

            new_id = task_id or f"task_{uuid.uuid4().hex[:12]}"
            task = A2ATask(
                taskId=new_id,
                status="submitted",
                messages=data.get("messages", []),
            )
            self._tasks[new_id] = task

        # Execute transition: submitted -> working -> completed/input_required
        self.task_executor(task)
        return task

    def get_task(self, task_id: str) -> Optional[A2ATask]:
        with self._lock:
            return self._tasks.get(task_id)

    def _default_executor(self, task: A2ATask) -> None:
        """Default task state transition simulator."""
        task.status = "working"
        task.updated_at = time.time()

        # Check if the latest message part requests input_required
        if task.messages:
            latest_msg = task.messages[-1]
            parts = latest_msg.get("parts", [])
            for p in parts:
                text_content = p.get("text", "")
                if "require_input" in text_content or p.get("require_input"):
                    task.status = "input_required"
                    return

        # Complete task and produce typed artifact
        task.status = "completed"
        task.artifacts.append(
            Artifact(
                name="task_output",
                type="data",
                data={"status": "success", "processed_parts": len(task.messages)},
            ).to_dict()
        )
        task.updated_at = time.time()


class A2AHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """Stdlib HTTP request handler for A2A endpoints."""

    def __init__(self, *args, agent_card: Dict[str, Any], task_manager: TaskManager, **kwargs):
        self.agent_card = agent_card
        self.task_manager = task_manager
        super().__init__(*args, **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        # Avoid cluttering stdout
        pass

    def _send_json(self, status_code: int, data: Any) -> None:
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Agent Card endpoints
        if path in ("/.well-known/agent.json", "/a2a/agent.json", "/agent.json"):
            self._send_json(200, self.agent_card)
            return

        # GET tasks/{id}
        match = re.match(r"^(?:/a2a)?/tasks/([^/]+)$", path)
        if match:
            task_id = match.group(1)
            task = self.task_manager.get_task(task_id)
            if not task:
                self._send_json(404, {"error": f"Task '{task_id}' not found"})
                return
            self._send_json(200, task.to_dict())
            return

        self._send_json(404, {"error": f"Endpoint not found: {path}"})

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/a2a/tasks/send", "/tasks/send"):
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
                data = json.loads(body)
            except Exception as exc:
                self._send_json(400, {"error": f"Invalid JSON payload: {str(exc)}"})
                return

            task = self.task_manager.create_or_resume_task(data)
            self._send_json(200, {"taskId": task.taskId, "status": task.status})
            return

        self._send_json(404, {"error": f"Endpoint not found: {path}"})


def run_a2a_server(
    agent_card: Dict[str, Any],
    port: int = 8000,
    host: str = "0.0.0.0",
    task_manager: Optional[TaskManager] = None,
) -> http.server.HTTPServer:
    """Runs A2A server on stdlib http.server with zero runtime dependencies."""
    tm = task_manager or TaskManager()

    def handler_factory(*args, **kwargs):
        return A2AHTTPRequestHandler(*args, agent_card=agent_card, task_manager=tm, **kwargs)

    server = http.server.HTTPServer((host, port), handler_factory)
    return server
