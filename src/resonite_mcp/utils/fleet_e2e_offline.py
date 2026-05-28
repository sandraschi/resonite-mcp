"""In-process Phase 1 fleet smoke (no live Resonite or HTTP services required)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock
from unittest.mock import patch


async def run_offline_smoke(*, work_dir: Path) -> dict[str, object]:
    """Run fleet staging, import, and execution_mode checks locally."""
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

    mock_import = AsyncMock(return_value={"success": True, "path": "mock", "osc": {"status": "success"}})

    with patch("resonite_mcp.tools.fleet_tools._import_local_file", new=mock_import), patch(
        "resonite_mcp.server.is_resonite_installed",
        return_value=True,
    ), patch(
        "resonite_mcp.server.is_resonite_running",
        return_value=False,
    ), patch(
        "resonite_mcp.utils.fleet_http.check_http_health",
        new=AsyncMock(return_value=False),
    ):
        presets = await resonite_fleet("list_presets")
        steps.append({"name": "offline_list_presets", "success": bool(presets.get("success")), "detail": presets})

        mode = await resonite_fleet("execution_mode")
        steps.append({"name": "offline_execution_mode", "success": bool(mode.get("success")), "detail": mode})

        listing = await resonite_fleet("list_staging", input_dir=str(ui_in.parent))
        steps.append({"name": "offline_list_staging", "success": bool(listing.get("success")), "detail": listing})

        imported = await resonite_fleet("import_staged_assets", input_dir=str(ui_in.parent))
        steps.append({"name": "offline_import_staged", "success": bool(imported.get("success")), "detail": imported})

        vrm_list = await resonite_fleet("list_vrm_staging", vrm_dir=str(vrm_models))
        steps.append({"name": "offline_list_vrm_staging", "success": bool(vrm_list.get("success")), "detail": vrm_list})

        vrm_import = await resonite_fleet("import_vrm_batch", vrm_dir=str(vrm_models))
        steps.append({"name": "offline_import_vrm_batch", "success": bool(vrm_import.get("success")), "detail": vrm_import})

        pf_presets = await resonite_fleet("list_protoflux_presets")
        steps.append({"name": "offline_protoflux_presets", "success": bool(pf_presets.get("success")), "detail": pf_presets})

        pipeline = await resonite_fleet(
            "run_fleet_pipeline",
            input_dir=str(ui_in.parent),
            staging_dir=str(work_dir / "resonite_stage"),
            skip_blender=True,
            skip_gimp=True,
        )
        steps.append({"name": "offline_run_fleet_pipeline", "success": bool(pipeline.get("success")), "detail": pipeline})

    return {
        "success": all(bool(s.get("success")) for s in steps),
        "mode": "offline",
        "steps": steps,
    }
