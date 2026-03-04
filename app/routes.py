"""API routes for ADO MCP."""
import logging

from flask import Blueprint, jsonify, request

from .errors import AdoMcpError, ValidationError
from .tool_handlers import call_tool
from .tools_manifest import get_tools_manifest

logger = logging.getLogger(__name__)

# Create Blueprint
api_bp = Blueprint("api", __name__)


def _error_response(exc: Exception):
    """Map domain errors to consistent HTTP responses."""
    if isinstance(exc, AdoMcpError):
        return jsonify({"error": exc.message}), exc.http_status
    logger.error(f"Unhandled error: {exc}")
    return jsonify({"error": "Internal server error"}), 500


@api_bp.route("/", methods=["GET"])
def root():
    """Root endpoint with server info."""
    return jsonify({
        "name": "Azure DevOps MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "tools": "/tools",
            "search_work_items": "/tool/ado.search_work_items",
            "get_work_item": "/tool/ado.get_work_item/<id>"
        }
    })


@api_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


@api_bp.route("/tools", methods=["GET"])
def tools():
    """Return the tools manifest."""
    return jsonify(get_tools_manifest())


@api_bp.route("/tool/ado.search_work_items", methods=["POST"])
def search_work_items():
    """Search for work items using WIQL query."""
    data = request.get_json() or {}

    wiql = data.get("wiql")
    if not wiql:
        return jsonify({"error": "wiql query is required"}), 400

    try:
        result = call_tool("ado.search_work_items", data)
        return jsonify(result)
    except Exception as e:
        return _error_response(e)


@api_bp.route("/tool/ado.get_work_item/<int:work_item_id>", methods=["GET"])
def get_work_item(work_item_id):
    """Get a specific work item by ID."""
    fields = request.args.get("fields")

    try:
        fields_list = fields.split(",") if fields else None
        result = call_tool(
            "ado.get_work_item",
            {"id": work_item_id, "fields": fields_list},
        )
        return jsonify(result)
    except Exception as e:
        return _error_response(e)


@api_bp.route("/tool/ado.list_repositories", methods=["GET"])
def list_repositories():
    """List repositories in the current project."""
    try:
        result = call_tool("ado.list_repositories", {})
        return jsonify(result)
    except Exception as e:
        return _error_response(e)


@api_bp.route("/tool/ado.list_pull_requests", methods=["GET"])
def list_pull_requests():
    """List pull requests for a repository."""
    repository_id = request.args.get("repository_id")
    if not repository_id:
        return _error_response(ValidationError("repository_id is required"))

    status = request.args.get("status", "active")
    top = request.args.get("top", "50")

    try:
        result = call_tool(
            "ado.list_pull_requests",
            {
                "repository_id": repository_id,
                "status": status,
                "top": int(top),
            },
        )
        return jsonify(result)
    except Exception as e:
        return _error_response(e)


@api_bp.route("/tool/ado.list_builds", methods=["GET"])
def list_builds():
    """List recent builds."""
    top = request.args.get("top", "25")
    status_filter = request.args.get("status_filter")

    try:
        result = call_tool(
            "ado.list_builds",
            {
                "top": int(top),
                "status_filter": status_filter,
            },
        )
        return jsonify(result)
    except Exception as e:
        return _error_response(e)


@api_bp.route("/tool/ado.create_work_item", methods=["POST"])
def create_work_item():
    """Create a work item (guarded)."""
    data = request.get_json() or {}
    try:
        result = call_tool("ado.create_work_item", data)
        return jsonify(result)
    except Exception as e:
        return _error_response(e)


@api_bp.route("/tool/ado.update_work_item", methods=["POST"])
def update_work_item():
    """Update a work item (guarded)."""
    data = request.get_json() or {}
    try:
        result = call_tool("ado.update_work_item", data)
        return jsonify(result)
    except Exception as e:
        return _error_response(e)


@api_bp.route("/tool/ado.add_pr_comment", methods=["POST"])
def add_pr_comment():
    """Add PR comment (guarded)."""
    data = request.get_json() or {}
    try:
        result = call_tool("ado.add_pr_comment", data)
        return jsonify(result)
    except Exception as e:
        return _error_response(e)
