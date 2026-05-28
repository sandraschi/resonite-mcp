"""Agent execution mode guidance based on Resonite presence."""

from __future__ import annotations

from typing import Any


async def describe_execution_mode(*, installed: bool, running: bool) -> dict[str, Any]:
    if running:
        mode = "hands_in"
        summary = "Resonite is running — use ResoniteLink and OSC for live imports."
        steps = [
            "Confirm ResoniteLink enabled (port 4242).",
            "Use resonite_fleet import_staged_assets or import_blender_asset.",
            "Verify slots via resonite_link inspector tools.",
        ]
    elif installed:
        mode = "hands_off_launch"
        summary = "Resonite installed but not running — launch before live imports."
        steps = [
            "Launch Resonite via steam:// or webapp Presence Gate.",
            "Stage assets with inkscape_sim_art stage_resonite_ui first.",
            "Re-run resonite_fleet when process is active.",
        ]
    else:
        mode = "hands_off_install"
        summary = "Resonite not detected — filesystem staging and HTTP fleet calls still work."
        steps = [
            "Install Resonite from Steam (App 2519830).",
            "Prepare UI vectors via inkscape-mcp sim art pipeline.",
            "Import after install using resonite_fleet run_fleet_pipeline.",
        ]

    return {
        "mode": mode,
        "summary": summary,
        "resonite_installed": installed,
        "resonite_running": running,
        "recommended_steps": steps,
        "fleet_staging_default": "D:/Temp/fleet_pipeline/resonite_fleet",
        "inkscape_ui_staging_default": "D:/Temp/fleet_pipeline/inkscape_sim_art/resonite_ui",
    }
