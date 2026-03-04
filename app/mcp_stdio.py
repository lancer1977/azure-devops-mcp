"""Minimal MCP stdio server implementation for Phase 1.

Implements core MCP methods:
- initialize
- tools/list
- tools/call
"""
import json
import sys
from typing import Any

from .errors import AdoMcpError
from .tool_handlers import call_tool, format_mcp_tool_result, list_tools


SERVER_INFO = {
    "name": "azure-devops-mcp",
    "version": "1.0.0",
}


def _write_message(message: dict[str, Any]) -> None:
    """Write JSON-RPC message to stdout."""
    sys.stdout.write(json.dumps(message) + "\n")
    sys.stdout.flush()


def _handle_request(request: dict[str, Any]) -> dict[str, Any]:
    """Handle one JSON-RPC request and return a response."""
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    try:
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                    },
                    "serverInfo": SERVER_INFO,
                },
            }

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": list_tools(),
                },
            }

        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            result = call_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": format_mcp_tool_result(result),
            }

        if method == "notifications/initialized":
            # Notification: no response expected
            return {}

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}",
            },
        }
    except Exception as exc:
        if isinstance(exc, AdoMcpError):
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": exc.mcp_code,
                    "message": exc.message,
                },
            }
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32000,
                "message": str(exc),
            },
        }


def run_stdio_server() -> None:
    """Run MCP stdio server loop."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            _write_message(
                {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error",
                    },
                }
            )
            continue

        response = _handle_request(request)
        if response:
            _write_message(response)
