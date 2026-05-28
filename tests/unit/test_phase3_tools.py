"""Tests for Agent Lab Phase 3 VRM/avatar fleet tools."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def staged_vrm(tmp_path: Path) -> Path:
    models = tmp_path / "models"
    models.mkdir(parents=True)
    (models / "avatar_stub.vrm").write_bytes(b"VRM1.0 stub")
    return models


class TestListVrmStaging:
    @pytest.mark.asyncio
    async def test_list_vrm_staging(self, staged_vrm: Path):
        from resonite_mcp.tools.fleet_tools import resonite_fleet

        result = await resonite_fleet("list_vrm_staging", vrm_dir=str(staged_vrm))
        assert result["success"] is True
        assert len(result["files"]) >= 1
        assert any(p.endswith(".vrm") for p in result["files"])


class TestImportVrmBatch:
    @pytest.mark.asyncio
    async def test_import_vrm_batch(self, staged_vrm: Path):
        from resonite_mcp.tools.fleet_tools import resonite_fleet

        with patch(
            "resonite_mcp.tools.fleet_tools._import_local_file",
            new=AsyncMock(return_value={"success": True, "path": "mock"}),
        ):
            result = await resonite_fleet("import_vrm_batch", vrm_dir=str(staged_vrm))
        assert result["success"] is True
        assert result["data"]["imported"] >= 1


class TestProtofluxPresets:
    @pytest.mark.asyncio
    async def test_list_protoflux_presets(self):
        from resonite_mcp.tools.fleet_tools import resonite_fleet

        result = await resonite_fleet("list_protoflux_presets")
        assert result["success"] is True
        assert result["data"]["count"] >= 1

    @pytest.mark.asyncio
    async def test_get_protoflux_preset(self):
        from resonite_mcp.tools.fleet_tools import resonite_fleet

        result = await resonite_fleet(
            "list_protoflux_presets",
            protoflux_preset="vrm_blink",
        )
        assert result["success"] is True
        assert result["data"]["preset"]["id"] == "vrm_blink"


class TestPullAvatarVrm:
    @pytest.mark.asyncio
    async def test_pull_avatar_vrm_offline(self, staged_vrm: Path, tmp_path: Path):
        from resonite_mcp.tools.fleet_tools import resonite_fleet

        avatar_dir = tmp_path / "avatar_store"
        avatar_dir.mkdir()
        (avatar_dir / "local.vrm").write_bytes(b"VRM1.0 local")

        with patch(
            "resonite_mcp.tools.fleet_tools.DEFAULT_AVATAR_VRM_DIR",
            avatar_dir,
        ), patch(
            "resonite_mcp.tools.fleet_tools.check_avatar_http_health",
            new=AsyncMock(return_value=False),
        ), patch(
            "resonite_mcp.tools.fleet_tools._import_local_file",
            new=AsyncMock(return_value={"success": True, "path": "mock"}),
        ):
            result = await resonite_fleet(
                "pull_avatar_vrm",
                vrm_dir=str(staged_vrm),
            )
        assert result["success"] is True


class TestApiV1ToolPhase3:
    @pytest.fixture
    def api_client(self):
        from resonite_mcp.http_server import app

        return TestClient(app)

    def test_health_phase3(self, api_client: TestClient):
        response = api_client.get("/api/v1/health")
        assert response.status_code == 200
        body = response.json()
        assert body["version"] == "0.8.0"
        assert body["agent_lab_phase"] == 4

    def test_list_vrm_staging_via_api(self, api_client: TestClient, tmp_path: Path):
        models = tmp_path / "models"
        models.mkdir()
        (models / "x.vrm").write_bytes(b"stub")

        response = api_client.post(
            "/api/v1/tool",
            json={
                "tool": "resonite_fleet",
                "params": {"operation": "list_vrm_staging", "vrm_dir": str(models)},
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True


class TestOfflineVrmSmoke:
    @pytest.mark.asyncio
    async def test_offline_smoke_includes_vrm(self, tmp_path: Path):
        from resonite_mcp.utils.fleet_e2e_offline import run_offline_smoke

        report = await run_offline_smoke(work_dir=tmp_path / "e2e")
        assert report["success"] is True
        step_names = [str(s.get("name")) for s in report["steps"]]
        assert "offline_list_vrm_staging" in step_names
        assert "offline_import_vrm_batch" in step_names
