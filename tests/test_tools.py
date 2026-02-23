"""Tests for tools manifest and API endpoints."""
import pytest

from app.tools_manifest import get_tools_manifest


class TestToolsManifest:
    """Tests for tools manifest."""

    def test_get_tools_manifest_returns_dict(self):
        """Should return a dictionary."""
        manifest = get_tools_manifest()
        assert isinstance(manifest, dict)

    def test_manifest_has_tools_key(self):
        """Manifest should have 'tools' key."""
        manifest = get_tools_manifest()
        assert "tools" in manifest
        assert isinstance(manifest["tools"], list)

    def test_tools_have_required_keys(self):
        """Each tool should have required keys."""
        manifest = get_tools_manifest()
        required_keys = ["name", "description", "input_schema", "output_schema"]

        for tool in manifest["tools"]:
            for key in required_keys:
                assert key in tool, f"Tool missing '{key}'"

    def test_search_work_items_tool_exists(self):
        """ado.search_work_items tool should exist."""
        manifest = get_tools_manifest()
        tool_names = [t["name"] for t in manifest["tools"]]
        assert "ado.search_work_items" in tool_names

    def test_get_work_item_tool_exists(self):
        """ado.get_work_item tool should exist."""
        manifest = get_tools_manifest()
        tool_names = [t["name"] for t in manifest["tools"]]
        assert "ado.get_work_item" in tool_names

    def test_search_work_items_input_schema(self):
        """search_work_items should have correct input schema."""
        manifest = get_tools_manifest()
        tool = next(t for t in manifest["tools"] if t["name"] == "ado.search_work_items")

        assert "wiql" in tool["input_schema"]["properties"]
        assert "top" in tool["input_schema"]["properties"]
        assert "wiql" in tool["input_schema"]["required"]

    def test_get_work_item_input_schema(self):
        """get_work_item should have correct input schema."""
        manifest = get_tools_manifest()
        tool = next(t for t in manifest["tools"] if t["name"] == "ado.get_work_item")

        assert "id" in tool["input_schema"]["properties"]
        assert "id" in tool["input_schema"]["required"]


class TestAPIEndpoints:
    """Tests for API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from app.main import app
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_health_endpoint(self, client):
        """Health endpoint should return ok."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"

    def test_tools_endpoint(self, client):
        """Tools endpoint should return manifest."""
        response = client.get("/tools")
        assert response.status_code == 200
        data = response.get_json()
        assert "tools" in data
        assert len(data["tools"]) == 2

    def test_search_work_items_missing_wiql(self, client):
        """Missing wiql should return 400."""
        response = client.post("/tool/ado.search_work_items", json={})
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
