"""Fleet handoff portmanteau for Resonite Agent Lab Phase 1."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any
from typing import Literal

from pydantic import BaseModel
from pydantic import Field

from ..utils.execution_mode import describe_execution_mode
from ..utils.fleet_http import DEFAULT_BLENDER_URL
from ..utils.fleet_http import DEFAULT_GIMP_URL
from ..utils.fleet_http import DEFAULT_INKSCAPE_URL
from ..utils.fleet_http import call_http_tool
from ..utils.fleet_http import check_http_health
from ..utils.fleet_staging import DEFAULT_FLEET_STAGING
from ..utils.fleet_staging import DEFAULT_INKSCAPE_UI_STAGING
from ..utils.fleet_staging import classify_staged_assets
from ..utils.fleet_staging import list_staging_files

logger = logging.getLogger(__name__)

FleetOperation = Literal[
    "list_presets",
    "execution_mode",
    "list_staging",
    "import_staged_assets",
    "pull_inkscape_ui",
    "import_blender_asset",
    "import_gimp_texture",
    "run_fleet_pipeline",
]


class FleetResult(BaseModel):
    success: bool
    operation: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    files: list[str] = Field(default_factory=list)
    execution_time_ms: float = 0.0
    error: str = ""


async def _import_local_file(path: str, *, target_slot: str = "root") -> dict[str, Any]:
    result: dict[str, Any] = {"path": path, "target_slot": target_slot, "success": False}
    src = Path(path)
    if not src.is_file():
        result["error"] = f"File not found: {path}"
        return result

    try:
        from ..resonite_link import ResoniteLinkClient

        client = ResoniteLinkClient()
        payload = {
            "type": "importFile",
            "filePath": str(src.resolve()),
            "targetSlotId": target_slot,
            "position": {"x": 0, "y": 0, "z": 0},
        }
        resp = await client._send(payload)
        result["resonite_link"] = resp
        result["success"] = True
    except Exception as exc:
        logger.info("ResoniteLink import unavailable for %s: %s", path, exc)
        result["resonite_link"] = str(exc)

    try:
        from ..models import OSCMessageInput
        from .osc import send_osc

        osc = await send_osc(
            OSCMessageInput(
                host="127.0.0.1",
                port=9000,
                address="/resonite/fleet/import",
                values=[str(src.resolve()), target_slot],
            )
        )
        result["osc"] = osc
        if osc.get("status") == "success":
            result["success"] = True
    except Exception as exc:
        logger.warning("OSC fleet import failed for %s: %s", path, exc)
        result["osc"] = str(exc)

    if not result.get("success"):
        result["error"] = result.get("error") or "Import failed (ResoniteLink and OSC)"
    return result


async def resonite_fleet(
    operation: FleetOperation,
    *,
    staging_dir: str = "",
    input_dir: str = "",
    object_name: str = "",
    texture_path: str = "",
    target_slot: str = "root",
    inkscape_url: str = "",
    blender_url: str = "",
    gimp_url: str = "",
    skip_inkscape: bool = False,
    skip_blender: bool = True,
    skip_gimp: bool = True,
) -> dict[str, Any]:
    """Cross-fleet asset pipeline into Resonite (inkscape UI, blender GLB, gimp textures)."""
    start = time.time()
    stage = Path(staging_dir) if staging_dir else DEFAULT_FLEET_STAGING
    inkscape_stage = Path(input_dir) if input_dir else DEFAULT_INKSCAPE_UI_STAGING
    iurl = inkscape_url or DEFAULT_INKSCAPE_URL
    burl = blender_url or DEFAULT_BLENDER_URL
    gurl = gimp_url or DEFAULT_GIMP_URL

    try:
        if operation == "list_presets":
            return FleetResult(
                success=True,
                operation=operation,
                message="Fleet preset catalog",
                data={
                    "inkscape_url": iurl,
                    "blender_url": burl,
                    "gimp_url": gurl,
                    "default_staging": str(DEFAULT_FLEET_STAGING),
                    "inkscape_ui_staging": str(DEFAULT_INKSCAPE_UI_STAGING),
                    "supported_ui_suffixes": [".svg", ".png", ".webp"],
                    "supported_model_suffixes": [".glb", ".gltf", ".vrm", ".fbx"],
                    "naming_hint": "Inkscape stage_resonite_ui -> icons/*.svg, sheets/*.svg",
                },
            ).model_dump()

        if operation == "execution_mode":
            from ..server import is_resonite_installed, is_resonite_running

            mode_data = await describe_execution_mode(
                installed=is_resonite_installed(),
                running=is_resonite_running(),
            )
            return FleetResult(
                success=True,
                operation=operation,
                message="Execution mode guidance for agents",
                data=mode_data,
            ).model_dump()

        if operation == "list_staging":
            merged: list[str] = []
            for root in (inkscape_stage, stage):
                listing = list_staging_files(root)
                merged.extend(listing.get("files") or [])
            classified = classify_staged_assets(merged)
            return FleetResult(
                success=True,
                operation=operation,
                message=f"Found {len(merged)} staged file(s)",
                data={"files": merged, "classified": classified, "scan_roots": [str(inkscape_stage), str(stage)]},
                files=merged,
            ).model_dump()

        if operation == "import_staged_assets":
            listing = await resonite_fleet("list_staging", staging_dir=str(stage), input_dir=str(inkscape_stage))
            files = list(listing.get("files") or [])
            ui_files = classify_staged_assets(files)["ui"] + classify_staged_assets(files)["models"]
            if not ui_files:
                return FleetResult(
                    success=False,
                    operation=operation,
                    message="No staged assets to import",
                    error="FileNotFoundError",
                ).model_dump()

            imports: list[dict[str, Any]] = []
            ok = 0
            for path in ui_files:
                item = await _import_local_file(path, target_slot=target_slot)
                imports.append(item)
                if item.get("success"):
                    ok += 1

            success = ok == len(ui_files)
            return FleetResult(
                success=success,
                operation=operation,
                message=f"Imported {ok}/{len(ui_files)} staged asset(s)",
                data={"imports": imports, "imported": ok, "total": len(ui_files)},
                files=[p for p in ui_files if Path(p).is_file()],
                error="" if success else "PartialImport",
            ).model_dump()

        if operation == "pull_inkscape_ui":
            staged_local = list_staging_files(inkscape_stage)
            files = list(staged_local.get("files") or [])
            inkscape_online = await check_http_health(iurl)
            handoff: dict[str, Any] = {"inkscape_reachable": inkscape_online, "local_files_before": len(files)}

            if inkscape_online and not skip_inkscape:
                stage_resp = await call_http_tool(
                    iurl,
                    "inkscape_sim_art",
                    {
                        "operation": "stage_resonite_ui",
                        "input_dir": str(inkscape_stage / ".." / "svg_pack"),
                        "staging_dir": str(inkscape_stage.parent),
                    },
                )
                handoff["inkscape_stage"] = stage_resp
                if stage_resp.get("files"):
                    files = list(stage_resp["files"])

            imported = await resonite_fleet(
                "import_staged_assets",
                staging_dir=str(stage),
                input_dir=str(inkscape_stage),
                target_slot=target_slot,
            )
            return FleetResult(
                success=bool(imported.get("success")),
                operation=operation,
                message="Inkscape UI pull complete" if imported.get("success") else "Inkscape UI pull partial",
                data={"handoff": handoff, "import": imported.get("data")},
                files=list(imported.get("files") or []),
                error="" if imported.get("success") else "PullError",
            ).model_dump()

        if operation == "import_blender_asset":
            if not object_name:
                return FleetResult(
                    success=False,
                    operation=operation,
                    message="object_name required",
                    error="ValueError",
                ).model_dump()
            from .integrations import resonite_import_blender

            result = await resonite_import_blender(object_name)
            success = result.get("status") == "ok"
            return FleetResult(
                success=success,
                operation=operation,
                message="Blender asset import attempted",
                data=result,
                files=[result["local_path"]] if result.get("local_path") else [],
                error="" if success else str(result.get("blender_export") or "BlenderImportError"),
            ).model_dump()

        if operation == "import_gimp_texture":
            if not texture_path:
                return FleetResult(
                    success=False,
                    operation=operation,
                    message="texture_path required",
                    error="ValueError",
                ).model_dump()
            audit = await call_http_tool(
                gurl,
                "gimp_validation_tool",
                {
                    "operation": "audit_texture",
                    "input_path": texture_path,
                    "target_platform": "resonite",
                },
            )
            imported = await _import_local_file(texture_path, target_slot=target_slot)
            success = bool(imported.get("success")) and bool(audit.get("success", True))
            return FleetResult(
                success=success,
                operation=operation,
                message="GIMP texture imported into Resonite pipeline",
                data={"gimp_audit": audit, "import": imported},
                files=[texture_path],
                error="" if success else "GimpTextureError",
            ).model_dump()

        if operation == "run_fleet_pipeline":
            steps: list[dict[str, Any]] = []
            if not skip_inkscape:
                pull = await resonite_fleet(
                    "pull_inkscape_ui",
                    staging_dir=str(stage),
                    input_dir=str(inkscape_stage),
                    inkscape_url=iurl,
                    target_slot=target_slot,
                )
                steps.append({"name": "pull_inkscape_ui", "success": bool(pull.get("success")), "detail": pull})
            else:
                imp = await resonite_fleet(
                    "import_staged_assets",
                    staging_dir=str(stage),
                    input_dir=str(inkscape_stage),
                    target_slot=target_slot,
                )
                steps.append({"name": "import_staged_assets", "success": bool(imp.get("success")), "detail": imp})

            if not skip_blender and object_name:
                blender = await resonite_fleet("import_blender_asset", object_name=object_name)
                steps.append(
                    {"name": "import_blender_asset", "success": bool(blender.get("success")), "detail": blender}
                )

            if not skip_gimp and texture_path:
                gimp = await resonite_fleet(
                    "import_gimp_texture",
                    texture_path=texture_path,
                    target_slot=target_slot,
                    gimp_url=gurl,
                )
                steps.append({"name": "import_gimp_texture", "success": bool(gimp.get("success")), "detail": gimp})

            success = all(bool(s.get("success")) for s in steps) if steps else False
            return FleetResult(
                success=success,
                operation=operation,
                message="Fleet pipeline complete" if success else "Fleet pipeline partial failure",
                data={"steps": steps},
            ).model_dump()

        return FleetResult(
            success=False,
            operation=operation,
            message=f"Unknown operation: {operation}",
            error="ValueError",
        ).model_dump()
    except Exception as exc:
        logger.exception("resonite_fleet failed operation=%s", operation)
        return FleetResult(
            success=False,
            operation=operation,
            message=str(exc),
            error=str(exc),
            execution_time_ms=(time.time() - start) * 1000,
        ).model_dump()


from ..server import server

server.tool()(resonite_fleet)
