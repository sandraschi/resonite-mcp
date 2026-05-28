"""Tests for Agent Lab Phase 6 inventory, voice, and strict fleet E2E."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


class TestInventoryAdapter:
    @pytest.mark.asyncio
    async def test_mock_inventory_mode(self, monkeypatch: pytest.MonkeyPatch):
        from resonite_mcp.utils.inventory_adapter import list_inventory_items

        monkeypatch.setenv("RESONITE_INVENTORY_MODE", "mock")
        result = await list_inventory_items(limit=5)
        assert result["success"] is True
        assert result["mode"] == "mock"
        assert result["count"] >= 1

    @pytest.mark.asyncio
    async def test_inventory_status_fleet_op(self, monkeypatch: pytest.MonkeyPatch):
        from resonite_mcp.tools.fleet_tools import resonite_fleet

        monkeypatch.setenv("RESONITE_INVENTORY_MODE", "mock")
        result = await resonite_fleet("inventory_status")
        assert result["success"] is True
        assert result["data"]["configured_mode"] == "mock"


class TestVoiceTools:
    @pytest.mark.asyncio
    async def test_list_macros(self):
        from resonite_mcp.tools.voice_tools import resonite_voice

        result = await resonite_voice("list_macros")
        assert result["success"] is True
        assert "wave" in result["data"]["macros"]

    @pytest.mark.asyncio
    async def test_parse_command_keyword(self):
        from resonite_mcp.tools.voice_tools import resonite_voice

        result = await resonite_voice("parse_command", command_text="please wave hello")
        assert result["success"] is True
        assert result["data"]["macro_id"] == "wave"

    @pytest.mark.asyncio
    async def test_send_macro_mock_osc(self):
        from resonite_mcp.tools.voice_tools import resonite_voice

        with patch(
            "resonite_mcp.tools.osc.send_osc",
            new=AsyncMock(return_value={"status": "success", "address": "/avatar/gesture/wave"}),
        ):
            result = await resonite_voice("send_macro", macro_id="wave")
        assert result["success"] is True


class TestStrictFleetPipeline:
    @pytest.mark.asyncio
    async def test_run_strict_fleet_pipeline_offline(self, tmp_path: Path):
        from resonite_mcp.tools.fleet_tools import resonite_fleet

        ui = tmp_path / "ui" / "icons"
        ui.mkdir(parents=True)
        (ui / "icon.svg").write_text("<svg/>", encoding="utf-8")
        texture = tmp_path / "tex.png"
        texture.write_bytes(b"\x89PNG\r\n\x1a\n")
        models = tmp_path / "models"
        models.mkdir()
        (models / "a.vrm").write_bytes(b"vrm")
        marble = tmp_path / "marble"
        marble.mkdir()
        (marble / "w.ply").write_text("ply", encoding="utf-8")

        with patch(
            "resonite_mcp.tools.fleet_tools._import_local_file",
            new=AsyncMock(return_value={"success": True, "path": "mock", "osc": {"status": "success"}}),
        ), patch(
            "resonite_mcp.tools.integrations.resonite_import_worldlabs_batch",
            new=AsyncMock(return_value={"status": "ok", "imported": 1, "total": 1, "imports": []}),
        ), patch(
            "resonite_mcp.tools.fleet_tools.call_http_tool",
            new=AsyncMock(return_value={"success": True}),
        ), patch(
            "resonite_mcp.tools.integrations.resonite_import_blender",
            new=AsyncMock(return_value={"status": "ok", "object_name": "Cube"}),
        ), patch(
            "resonite_mcp.server.is_resonite_installed",
            return_value=True,
        ), patch(
            "resonite_mcp.server.is_resonite_running",
            return_value=False,
        ):
            result = await resonite_fleet(
                "run_strict_fleet_pipeline",
                input_dir=str(ui.parent),
                staging_dir=str(tmp_path / "stage"),
                vrm_dir=str(models),
                marble_dir=str(marble),
                texture_path=str(texture),
                object_name="Cube",
                skip_blender=False,
                skip_vrm=False,
                skip_marble=False,
                skip_inkscape=True,
            )
        assert result["success"] is True
        step_names = [s["name"] for s in result["data"]["steps"]]
        assert "inventory_status" in step_names
        assert "voice_parse_command" in step_names


class TestApiV1ToolPhase6:
    @pytest.fixture
    def api_client(self):
        from resonite_mcp.http_server import app

        return TestClient(app)

    def test_health_phase6(self, api_client: TestClient):
        response = api_client.get("/api/v1/health")
        assert response.status_code == 200
        body = response.json()
        assert body["version"] == "1.0.0"
        assert body["agent_lab_phase"] == 6

    def test_resonite_voice_via_api(self, api_client: TestClient):
        response = api_client.post(
            "/api/v1/tool",
            json={"tool": "resonite_voice", "params": {"operation": "list_macros"}},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True


class TestStrictOfflineSmoke:
    @pytest.mark.asyncio
    async def test_strict_offline_smoke(self, tmp_path: Path):
        from resonite_mcp.utils.fleet_e2e_strict import run_strict_offline_smoke

        report = await run_strict_offline_smoke(work_dir=tmp_path / "strict")
        assert report["success"] is True
        assert report["mode"] == "strict_offline"
