"""Tests for HTTP tool bridge and live fleet helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def api_client():
    from resonite_mcp.http_server import app

    return TestClient(app)


class TestApiV1Tool:
    def test_health_endpoint(self, api_client: TestClient):
        response = api_client.get("/api/v1/health")
        assert response.status_code == 200
        body = response.json()
        assert body["version"] == "1.0.0"
        assert body["agent_lab_phase"] == 6

    def test_resonite_fleet_list_presets(self, api_client: TestClient):
        response = api_client.post(
            "/api/v1/tool",
            json={"tool": "resonite_fleet", "params": {"operation": "list_presets"}},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "inkscape_url" in body["data"]["data"]

    def test_unknown_tool(self, api_client: TestClient):
        response = api_client.post("/api/v1/tool", json={"tool": "missing_tool", "params": {}})
        assert response.status_code == 404


class TestLiveSmokeHelpers:
    def test_prepare_live_fixtures(self, tmp_path: Path):
        from resonite_mcp.utils.fleet_e2e_live import prepare_live_fixtures

        pack = prepare_live_fixtures(work_dir=tmp_path / "live")
        assert (pack / "icon_live.svg").is_file()

    @pytest.mark.asyncio
    async def test_run_live_smoke_offline_servers(self, tmp_path: Path):
        from resonite_mcp.utils.fleet_e2e_live import run_live_smoke

        with patch(
            "resonite_mcp.utils.fleet_e2e_live.check_http_health",
            new=AsyncMock(return_value=False),
        ):
            report = await run_live_smoke(work_dir=tmp_path / "live")
        assert report["success"] is False
        assert report["mode"] == "http_live"


class TestContactsEndpoint:
    """Test /api/contacts endpoint."""

    def test_get_contacts_success(self, api_client: TestClient):
        """Test successful contacts fetch."""
        mock_contacts = [{"id": "U-sandra", "contactUsername": "sandra"}]
        with patch(
            "resonite_mcp.tools.rest_api.resonite_friends_list",
            new=AsyncMock(return_value={"status": "ok", "friends": mock_contacts, "count": 1}),
        ):
            response = api_client.get("/api/contacts")
            assert response.status_code == 200
            assert response.json() == mock_contacts

    def test_get_contacts_unauthenticated(self, api_client: TestClient):
        """Test contacts fetch when not authenticated."""
        with patch(
            "resonite_mcp.tools.rest_api.resonite_friends_list",
            new=AsyncMock(
                return_value={"status": "error", "detail": "Not authenticated. Call resonite_rest_login first."}
            ),
        ):
            response = api_client.get("/api/contacts")
            assert response.status_code == 401
            assert "Not authenticated" in response.json()["detail"]
