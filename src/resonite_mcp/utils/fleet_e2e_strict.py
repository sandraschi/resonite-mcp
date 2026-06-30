"""Strict offline fleet E2E: inkscape -> gimp -> blender -> resonite + marble + voice."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch


async def run_strict_offline_smoke(*, work_dir: Path) -> dict[str, object]:
    """Run the full Agent Lab chain with HTTP peers mocked offline."""
    from resonite_mcp.tools.fleet_tools import resonite_fleet

    steps: list[dict[str, object]] = []
    ui_in = work_dir / "inkscape_ui" / "icons"
    ui_in.mkdir(parents=True, exist_ok=True)
    (ui_in / "icon_home.svg").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect x="8" y="8" width="48" height="48" fill="#3366cc" stroke="#000"/>
</svg>""",
        encoding="utf-8",
    )
    texture = work_dir / "albedo.png"
    texture.write_bytes(b"\x89PNG\r\n\x1a\n")
    vrm_models = work_dir / "models"
    vrm_models.mkdir(parents=True, exist_ok=True)
    (vrm_models / "fleet_avatar.vrm").write_bytes(b"VRM1.0 offline stub")

    marble_dir = work_dir / "marble"
    marble_dir.mkdir(parents=True, exist_ok=True)
    (marble_dir / "world_stub.ply").write_text("ply stub", encoding="utf-8")

    fab_dir = work_dir / "fab_art"
    fab_dir.mkdir(parents=True, exist_ok=True)
    (fab_dir / "overlay.svg").write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><circle cx="16" cy="16" r="12"/></svg>""",
        encoding="utf-8",
    )
    (fab_dir / "robot.dxf").write_text("0\nSECTION\n2\nHEADER\n0\nEOF\n", encoding="utf-8")

    mock_import = AsyncMock(return_value={"success": True, "path": "mock", "osc": {"status": "success"}})

    with (
        patch("resonite_mcp.tools.fleet_tools._import_local_file", new=mock_import),
        patch(
            "resonite_mcp.tools.integrations.resonite_import_worldlabs_batch",
            new=AsyncMock(return_value={"status": "ok", "imported": 1, "total": 1, "imports": []}),
        ),
        patch(
            "resonite_mcp.tools.integrations.resonite_import_blender",
            new=AsyncMock(return_value={"status": "ok", "object_name": "Cube"}),
        ),
        patch(
            "resonite_mcp.tools.fleet_tools.call_http_tool",
            new=AsyncMock(return_value={"success": True}),
        ),
        patch(
            "resonite_mcp.tools.fleet_tools.check_http_health",
            new=AsyncMock(return_value=False),
        ),
        patch(
            "resonite_mcp.server.is_resonite_installed",
            return_value=True,
        ),
        patch(
            "resonite_mcp.server.is_resonite_running",
            return_value=False,
        ),
    ):
        strict = await resonite_fleet(
            "run_strict_fleet_pipeline",
            input_dir=str(ui_in.parent),
            staging_dir=str(work_dir / "resonite_stage"),
            vrm_dir=str(vrm_models),
            marble_dir=str(marble_dir),
            fab_staging_dir=str(fab_dir),
            texture_path=str(texture),
            object_name="Cube",
            skip_blender=False,
            skip_vrm=False,
            skip_marble=False,
            skip_inkscape=True,
        )
        steps.append(
            {"name": "strict_run_fleet_pipeline", "success": bool(strict.get("success")), "detail": strict},
        )

    return {
        "success": all(bool(s.get("success")) for s in steps),
        "mode": "strict_offline",
        "steps": steps,
    }
