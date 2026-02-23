"""API routes for ADO MCP."""
import logging

from flask import Blueprint, jsonify, request

from .ado_client import AdoClient
from .config import get_settings
from .tools_manifest import get_tools_manifest

logger = logging.getLogger(__name__)

# Create Blueprint
api_bp = Blueprint("api", __name__)

# Initialize client lazily
_ado_client = None


def get_ado_client() -> AdoClient:
    """Get or create ADO client instance."""
    global _ado_client
    if _ado_client is None:
        settings = get_settings()
        _ado_client = AdoClient(settings)
    return _ado_client


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

    top = data.get("top", 100)

    try:
        client = get_ado_client()
        result = client.wiql(wiql, top=top)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error searching work items: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route("/tool/ado.get_work_item/<int:work_item_id>", methods=["GET"])
def get_work_item(work_item_id):
    """Get a specific work item by ID."""
    fields = request.args.get("fields")

    try:
        client = get_ado_client()
        fields_list = fields.split(",") if fields else None
        result = client.get_work_item(work_item_id, fields=fields_list)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting work item {work_item_id}: {e}")
        return jsonify({"error": str(e)}), 500
