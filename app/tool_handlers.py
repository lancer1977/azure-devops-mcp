"""Shared tool handlers used by both REST and MCP transports."""
import json
from typing import Any, Optional

from .ado_client import AdoClient
from .config import get_settings
from .errors import ValidationError
from .tools_manifest import get_tools_manifest

# Lazily initialized ADO client
_ado_client: Optional[AdoClient] = None


def get_ado_client() -> AdoClient:
    """Get or create ADO client instance."""
    global _ado_client
    if _ado_client is None:
        settings = get_settings()
        _ado_client = AdoClient(settings)
    return _ado_client


def list_tools() -> list[dict[str, Any]]:
    """Return tools in MCP-compatible shape."""
    manifest = get_tools_manifest()
    tools = []
    for tool in manifest.get("tools", []):
        tools.append(
            {
                "name": tool["name"],
                "description": tool["description"],
                "inputSchema": tool["input_schema"],
            }
        )
    return tools


def call_tool(tool_name: str, arguments: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Execute a tool by name and return JSON-serializable result."""
    arguments = arguments or {}
    client = get_ado_client()

    if tool_name == "ado.search_work_items":
        wiql = arguments.get("wiql")
        if not wiql:
            raise ValidationError("wiql query is required")
        top = arguments.get("top", 100)
        if not isinstance(top, int) or top < 1 or top > 1000:
            raise ValidationError("top must be an integer between 1 and 1000")
        return client.wiql(wiql, top=top)

    if tool_name == "ado.get_work_item":
        work_item_id = arguments.get("id")
        if work_item_id is None:
            raise ValidationError("id is required")
        fields = arguments.get("fields")
        if fields is not None and not isinstance(fields, list):
            raise ValidationError("fields must be an array of strings")
        return client.get_work_item(int(work_item_id), fields=fields)

    if tool_name == "ado.list_repositories":
        return client.list_repositories()

    if tool_name == "ado.list_pull_requests":
        repository_id = arguments.get("repository_id")
        if not repository_id:
            raise ValidationError("repository_id is required")
        status = arguments.get("status", "active")
        top = arguments.get("top", 50)
        if status not in {"active", "abandoned", "completed", "all"}:
            raise ValidationError("status must be one of: active, abandoned, completed, all")
        if not isinstance(top, int) or top < 1 or top > 1000:
            raise ValidationError("top must be an integer between 1 and 1000")
        return client.list_pull_requests(
            repository_id=str(repository_id),
            status=str(status),
            top=int(top),
        )

    if tool_name == "ado.list_builds":
        top = int(arguments.get("top", 25))
        if top < 1 or top > 1000:
            raise ValidationError("top must be an integer between 1 and 1000")
        status_filter = arguments.get("status_filter")
        return client.list_builds(top=top, status_filter=status_filter)

    if tool_name == "ado.create_work_item":
        settings = get_settings()
        if not settings.ado_allow_writes:
            raise ValidationError("Write operations are disabled. Set ADO_ALLOW_WRITES=true to enable.")

        work_item_type = arguments.get("work_item_type")
        fields = arguments.get("fields")
        if not work_item_type:
            raise ValidationError("work_item_type is required")
        if not isinstance(fields, dict) or not fields:
            raise ValidationError("fields must be a non-empty object")

        allowed_types = {t.strip() for t in settings.ado_allowed_work_item_types.split(",") if t.strip()}
        if allowed_types and work_item_type not in allowed_types:
            raise ValidationError(
                f"work_item_type '{work_item_type}' is not allowed. Allowed: {sorted(allowed_types)}"
            )

        return client.create_work_item(work_item_type=work_item_type, fields=fields)

    if tool_name == "ado.update_work_item":
        settings = get_settings()
        if not settings.ado_allow_writes:
            raise ValidationError("Write operations are disabled. Set ADO_ALLOW_WRITES=true to enable.")

        work_item_id = arguments.get("id")
        fields = arguments.get("fields")
        if work_item_id is None:
            raise ValidationError("id is required")
        if not isinstance(fields, dict) or not fields:
            raise ValidationError("fields must be a non-empty object")

        return client.update_work_item(work_item_id=int(work_item_id), fields=fields)

    if tool_name == "ado.add_pr_comment":
        settings = get_settings()
        if not settings.ado_allow_writes:
            raise ValidationError("Write operations are disabled. Set ADO_ALLOW_WRITES=true to enable.")

        repository_id = arguments.get("repository_id")
        pull_request_id = arguments.get("pull_request_id")
        content = arguments.get("content")
        if not repository_id:
            raise ValidationError("repository_id is required")
        if pull_request_id is None:
            raise ValidationError("pull_request_id is required")
        if not content:
            raise ValidationError("content is required")
        if len(str(content)) > 4000:
            raise ValidationError("content must be 4000 characters or fewer")

        return client.add_pull_request_comment(
            repository_id=str(repository_id),
            pull_request_id=int(pull_request_id),
            content=str(content),
        )

    raise ValidationError(f"Unknown tool: {tool_name}")


def format_mcp_tool_result(data: dict[str, Any]) -> dict[str, Any]:
    """Format a tool result according to MCP content blocks."""
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(data),
            }
        ]
    }
