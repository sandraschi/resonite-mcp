"""Live HTTP fleet chain helpers (inkscape-mcp -> resonite-mcp)."""

from __future__ import annotations

from pathlib import Path

from .fleet_http import DEFAULT_INKSCAPE_URL, DEFAULT_RESONITE_URL, call_http_tool, check_http_health

DEFAULT_LIVE_WORK_DIR = Path("D:/Temp/fleet_pipeline/resonite_e2e_live")


def prepare_live_fixtures(*, work_dir: Path) -> Path:
    """Write sample SVG icons for inkscape sim-art staging on the local machine."""
    pack_in = work_dir / "svg_pack"
    pack_in.mkdir(parents=True, exist_ok=True)
    (pack_in / "icon_live.svg").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect x="8" y="8" width="48" height="48" fill="#6633cc" stroke="#000"/>
</svg>""",
        encoding="utf-8",
    )
    return pack_in


async def run_live_smoke(
    *,
    work_dir: Path | None = None,
    inkscape_url: str = DEFAULT_INKSCAPE_URL,
    resonite_url: str = DEFAULT_RESONITE_URL,
) -> dict[str, object]:
    """Run inkscape stage -> resonite import over HTTP when both servers are up."""
    work = work_dir or DEFAULT_LIVE_WORK_DIR
    steps: list[dict[str, object]] = []

    inkscape_online = await check_http_health(inkscape_url)
    resonite_online = await check_http_health(resonite_url)
    steps.append(
        {
            "name": "live_probe",
            "success": inkscape_online and resonite_online,
            "detail": {
                "inkscape_online": inkscape_online,
                "resonite_online": resonite_online,
                "inkscape_url": inkscape_url,
                "resonite_url": resonite_url,
            },
        }
    )
    if not inkscape_online or not resonite_online:
        return {
            "success": False,
            "mode": "http_live",
            "steps": steps,
            "error": "Both inkscape-mcp and resonite-mcp HTTP must be online for live chain",
        }

    pack_in = prepare_live_fixtures(work_dir=work)
    pack_out = work / "svg_pack_out"
    resonite_ui = work / "resonite_ui"

    batch = await call_http_tool(
        inkscape_url,
        "inkscape_sim_art",
        {
            "operation": "svg_pack_batch",
            "input_dir": str(pack_in),
            "output_dir": str(pack_out),
            "template_id": "ui_icon_64",
            "validate": True,
        },
    )
    steps.append({"name": "live_inkscape_svg_pack_batch", "success": bool(batch.get("success")), "detail": batch})

    stage = await call_http_tool(
        inkscape_url,
        "inkscape_sim_art",
        {
            "operation": "stage_resonite_ui",
            "input_dir": str(pack_out if pack_out.is_dir() else pack_in),
            "staging_dir": str(work),
            "output_path": str(work / "icon_sheet.svg"),
        },
    )
    steps.append({"name": "live_inkscape_stage_resonite_ui", "success": bool(stage.get("success")), "detail": stage})

    mode = await call_http_tool(
        resonite_url,
        "resonite_fleet",
        {"operation": "execution_mode"},
    )
    steps.append({"name": "live_resonite_execution_mode", "success": bool(mode.get("success")), "detail": mode})

    listing = await call_http_tool(
        resonite_url,
        "resonite_fleet",
        {
            "operation": "list_staging",
            "input_dir": str(resonite_ui),
            "staging_dir": str(work / "resonite_fleet"),
        },
    )
    steps.append({"name": "live_resonite_list_staging", "success": bool(listing.get("success")), "detail": listing})

    imported = await call_http_tool(
        resonite_url,
        "resonite_fleet",
        {
            "operation": "import_staged_assets",
            "input_dir": str(resonite_ui),
            "staging_dir": str(work / "resonite_fleet"),
        },
    )
    steps.append({"name": "live_resonite_import_staged", "success": bool(imported.get("success")), "detail": imported})

    pull = await call_http_tool(
        resonite_url,
        "resonite_fleet",
        {
            "operation": "pull_inkscape_ui",
            "input_dir": str(resonite_ui),
            "staging_dir": str(work / "resonite_fleet"),
        },
    )
    steps.append({"name": "live_resonite_pull_inkscape_ui", "success": bool(pull.get("success")), "detail": pull})

    success = all(bool(s.get("success")) for s in steps)
    return {"success": success, "mode": "http_live", "steps": steps}
