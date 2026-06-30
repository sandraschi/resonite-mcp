"""Tests for Agent Lab Phase 5 Marble / World Labs fleet tools."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def marble_dirs(tmp_path: Path) -> tuple[Path, Path]:
    marble = tmp_path / "marble"
    fab = tmp_path / "fab"
    marble.mkdir()
    fab.mkdir()
    (marble / "scene.ply").write_text("ply", encoding="utf-8")
    (fab / "overlay.svg").write_text("<svg/>", encoding="utf-8")
    (fab / "path.dxf").write_text("dxf", encoding="utf-8")
    return marble, fab


class TestMarbleStaging:
    @pytest.mark.asyncio
    async def test_list_marble_staging(self, marble_dirs: tuple[Path, Path]):
        from resonite_mcp.tools.fleet_tools import resonite_fleet

        marble, fab = marble_dirs
        result = await resonite_fleet(
            "list_marble_staging",
            marble_dir=str(marble),
            fab_staging_dir=str(fab),
        )
        assert result["success"] is True
        assert len(result["files"]) >= 3

    @pytest.mark.asyncio
    async def test_import_worldlabs_batch(self, marble_dirs: tuple[Path, Path]):
        from resonite_mcp.tools.fleet_tools import resonite_fleet

        marble, _fab = marble_dirs
        with patch(
            "resonite_mcp.tools.integrations.resonite_import_worldlabs_batch",
            new=AsyncMock(return_value={"status": "ok", "imported": 1, "total": 1, "imports": []}),
        ):
            result = await resonite_fleet("import_worldlabs_batch", marble_dir=str(marble))
        assert result["success"] is True
        assert result["data"]["imported"] == 1

    @pytest.mark.asyncio
    async def test_pull_inkscape_fab_offline(self, marble_dirs: tuple[Path, Path], tmp_path: Path):
        from resonite_mcp.tools.fleet_tools import resonite_fleet

        marble, fab = marble_dirs
        ui = tmp_path / "ui"
        ui.mkdir()
        (ui / "icon.svg").write_text("<svg/>", encoding="utf-8")

        with (
            patch(
                "resonite_mcp.tools.fleet_tools.check_http_health",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "resonite_mcp.tools.fleet_tools._import_local_file",
                new=AsyncMock(return_value={"success": True, "path": "mock"}),
            ),
        ):
            result = await resonite_fleet(
                "pull_inkscape_fab",
                input_dir=str(ui),
                marble_dir=str(marble),
                fab_staging_dir=str(fab),
            )
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_run_marble_pipeline(self, marble_dirs: tuple[Path, Path], tmp_path: Path):
        from resonite_mcp.tools.fleet_tools import resonite_fleet

        marble, fab = marble_dirs
        ui = tmp_path / "ui"
        ui.mkdir()
        (ui / "icon.svg").write_text("<svg/>", encoding="utf-8")

        with (
            patch(
                "resonite_mcp.tools.fleet_tools.check_http_health",
                new=AsyncMock(return_value=False),
            ),
            patch(
                "resonite_mcp.tools.fleet_tools._import_local_file",
                new=AsyncMock(return_value={"success": True, "path": "mock"}),
            ),
            patch(
                "resonite_mcp.tools.integrations.resonite_import_worldlabs_batch",
                new=AsyncMock(return_value={"status": "ok", "imported": 1, "total": 1, "imports": []}),
            ),
        ):
            result = await resonite_fleet(
                "run_marble_pipeline",
                input_dir=str(ui),
                marble_dir=str(marble),
                fab_staging_dir=str(fab),
            )
        assert result["success"] is True
        assert len(result["data"]["steps"]) == 2


class TestMarbleUtils:
    def test_list_marble_files(self, marble_dirs: tuple[Path, Path]):
        from resonite_mcp.utils.marble_staging import list_marble_files

        marble, fab = marble_dirs
        listing = list_marble_files(marble, fab)
        assert listing["splats"]
        assert listing["dxf_refs"]
        assert listing["overlays"]
