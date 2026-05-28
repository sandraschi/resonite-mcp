"""Tests for Agent Lab Phase 1 fleet handoff and offline E2E smoke."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest


@pytest.fixture
def staged_ui(tmp_path: Path) -> Path:
    root = tmp_path / "resonite_ui" / "icons"
    root.mkdir(parents=True)
    (root / "badge.svg").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <circle cx="32" cy="32" r="20" fill="#00aa88"/>
</svg>""",
        encoding="utf-8",
    )
    return root.parent


class TestFleetPresets:
    @pytest.mark.asyncio
    async def test_list_presets(self):
        from resonite_mcp.tools.fleet_tools import resonite_fleet

        result = await resonite_fleet("list_presets")
        assert result["success"] is True
        assert "inkscape_url" in result["data"]


class TestExecutionMode:
    @pytest.mark.asyncio
    async def test_execution_mode(self):
        from resonite_mcp.tools.fleet_tools import resonite_fleet

        with patch("resonite_mcp.server.is_resonite_installed", return_value=True), patch(
            "resonite_mcp.server.is_resonite_running",
            return_value=True,
        ):
            result = await resonite_fleet("execution_mode")
        assert result["success"] is True
        assert result["data"]["mode"] == "hands_in"


class TestListStaging:
    @pytest.mark.asyncio
    async def test_list_staging(self, staged_ui: Path):
        from resonite_mcp.tools.fleet_tools import resonite_fleet

        result = await resonite_fleet("list_staging", input_dir=str(staged_ui))
        assert result["success"] is True
        assert len(result["files"]) >= 1


class TestImportStaged:
    @pytest.mark.asyncio
    async def test_import_staged_assets(self, staged_ui: Path):
        from resonite_mcp.tools.fleet_tools import resonite_fleet

        with patch(
            "resonite_mcp.tools.fleet_tools._import_local_file",
            new=AsyncMock(return_value={"success": True, "path": "mock"}),
        ):
            result = await resonite_fleet("import_staged_assets", input_dir=str(staged_ui))
        assert result["success"] is True


class TestFleetE2eOffline:
    @pytest.mark.asyncio
    async def test_offline_smoke(self, tmp_path: Path):
        from resonite_mcp.utils.fleet_e2e_offline import run_offline_smoke

        report = await run_offline_smoke(work_dir=tmp_path / "e2e")
        assert report["success"] is True
        assert report["mode"] == "offline"
        assert len(report["steps"]) >= 5
