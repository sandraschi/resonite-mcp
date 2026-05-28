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
from ..utils.fleet_http import DEFAULT_AVATAR_URL
from ..utils.fleet_http import DEFAULT_BLENDER_URL
from ..utils.fleet_http import DEFAULT_GIMP_URL
from ..utils.fleet_http import DEFAULT_INKSCAPE_URL
from ..utils.fleet_http import call_avatar_tool
from ..utils.fleet_http import call_http_tool
from ..utils.fleet_http import check_avatar_http_health
from ..utils.fleet_http import check_http_health
from ..utils.fleet_staging import DEFAULT_AVATAR_VRM_DIR
from ..utils.fleet_staging import DEFAULT_FLEET_STAGING
from ..utils.fleet_staging import DEFAULT_INKSCAPE_UI_STAGING
from ..utils.fleet_staging import DEFAULT_VRM_STAGING
from ..utils.fleet_staging import classify_staged_assets
from ..utils.fleet_staging import list_staging_files
from ..utils.fleet_staging import list_vrm_files
from ..utils.fleet_staging import stage_file
from ..utils.protoflux_avatar_presets import get_protoflux_preset
from ..utils.protoflux_avatar_presets import list_protoflux_presets

logger = logging.getLogger(__name__)

FleetOperation = Literal[
    "list_presets",
    "execution_mode",
    "list_staging",
    "import_staged_assets",
    "pull_inkscape_ui",
    "import_blender_asset",
    "import_gimp_texture",
    "list_vrm_staging",
    "import_vrm_batch",
    "pull_blender_vrm",
    "pull_avatar_vrm",
    "list_protoflux_presets",
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


def _resolve_vrm_roots(vrm_dir: Path, stage: Path) -> list[Path]:
    roots: list[Path] = []
    for candidate in (vrm_dir, stage / "models"):
        if candidate.is_dir() and candidate not in roots:
            roots.append(candidate)
    if vrm_dir.resolve() == DEFAULT_VRM_STAGING.resolve():
        for candidate in (DEFAULT_VRM_STAGING, DEFAULT_AVATAR_VRM_DIR):
            if candidate.is_dir() and candidate not in roots:
                roots.append(candidate)
    return roots


async def _pull_blender_vrm_export(
    *,
    object_name: str,
    blender_url: str,
    vrm_stage: Path,
    export_format: str,
) -> dict[str, Any]:
    handoff: dict[str, Any] = {"object_name": object_name, "export_format": export_format}
    output_name = f"{object_name}_resonite"
    if export_format.lower() == "vrm":
        export_op = "export_vrm"
        ext = ".vrm"
    else:
        export_op = "export_glb"
        ext = ".glb"

    export_resp = await call_http_tool(
        blender_url,
        "blender_export",
        {
            "operation": export_op,
            "output_path": f"//{output_name}{ext}",
            "object_names": [object_name],
        },
    )
    handoff["blender_export"] = export_resp

    export_path = ""
    if isinstance(export_resp, dict):
        export_path = str(
            export_resp.get("output_path")
            or export_resp.get("file_path")
            or export_resp.get("path")
            or ""
        )

    if export_path and Path(export_path).is_file():
        staged = await stage_file(source_path=export_path, staging_dir=vrm_stage, subdir="blender")
        handoff["stage"] = staged
        handoff["success"] = bool(staged.get("success"))
        handoff["files"] = [staged["staged_path"]] if staged.get("staged_path") else []
        return handoff

    handoff["success"] = bool(export_resp.get("success"))
    handoff["files"] = []
    if not handoff["success"]:
        handoff["error"] = str(export_resp.get("error") or "Blender export did not produce a local file")
    return handoff


async def resonite_fleet(
    operation: FleetOperation,
    *,
    staging_dir: str = "",
    input_dir: str = "",
    vrm_dir: str = "",
    object_name: str = "",
    texture_path: str = "",
    target_slot: str = "root",
    inkscape_url: str = "",
    blender_url: str = "",
    gimp_url: str = "",
    avatar_url: str = "",
    protoflux_preset: str = "",
    export_format: str = "vrm",
    skip_inkscape: bool = False,
    skip_blender: bool = True,
    skip_gimp: bool = True,
    skip_vrm: bool = True,
) -> dict[str, Any]:
    """Cross-fleet asset pipeline into Resonite (inkscape UI, blender GLB, gimp textures)."""
    start = time.time()
    stage = Path(staging_dir) if staging_dir else DEFAULT_FLEET_STAGING
    inkscape_stage = Path(input_dir) if input_dir else DEFAULT_INKSCAPE_UI_STAGING
    vrm_stage = Path(vrm_dir) if vrm_dir else DEFAULT_VRM_STAGING
    iurl = inkscape_url or DEFAULT_INKSCAPE_URL
    burl = blender_url or DEFAULT_BLENDER_URL
    gurl = gimp_url or DEFAULT_GIMP_URL
    aurl = avatar_url or DEFAULT_AVATAR_URL

    try:
        if operation == "list_presets":
            pf = list_protoflux_presets()
            return FleetResult(
                success=True,
                operation=operation,
                message="Fleet preset catalog",
                data={
                    "inkscape_url": iurl,
                    "blender_url": burl,
                    "gimp_url": gurl,
                    "avatar_url": aurl,
                    "default_staging": str(DEFAULT_FLEET_STAGING),
                    "inkscape_ui_staging": str(DEFAULT_INKSCAPE_UI_STAGING),
                    "vrm_staging": str(DEFAULT_VRM_STAGING),
                    "avatar_vrm_dir": str(DEFAULT_AVATAR_VRM_DIR),
                    "supported_ui_suffixes": [".svg", ".png", ".webp"],
                    "supported_model_suffixes": [".glb", ".gltf", ".vrm", ".fbx"],
                    "supported_vrm_suffixes": [".vrm", ".glb", ".gltf"],
                    "protoflux_presets": pf.get("presets") or [],
                    "naming_hint": "Inkscape stage_resonite_ui -> icons/*.svg; VRM -> models/*.vrm",
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

        if operation == "list_vrm_staging":
            roots = _resolve_vrm_roots(vrm_stage, stage)
            files = list_vrm_files(*roots)
            classified = classify_staged_assets(files)
            return FleetResult(
                success=True,
                operation=operation,
                message=f"Found {len(files)} VRM/model file(s)",
                data={
                    "files": files,
                    "vrm_files": [p for p in files if Path(p).suffix.lower() == ".vrm"],
                    "classified": classified,
                    "scan_roots": [str(r) for r in roots],
                },
                files=files,
            ).model_dump()

        if operation == "import_vrm_batch":
            listing = await resonite_fleet(
                "list_vrm_staging",
                staging_dir=str(stage),
                vrm_dir=str(vrm_stage),
            )
            files = list(listing.get("files") or [])
            if not files:
                return FleetResult(
                    success=False,
                    operation=operation,
                    message="No VRM/model files to import",
                    error="FileNotFoundError",
                ).model_dump()

            imports: list[dict[str, Any]] = []
            ok = 0
            for path in files:
                item = await _import_local_file(path, target_slot=target_slot)
                imports.append(item)
                if item.get("success"):
                    ok += 1

            success = ok == len(files)
            return FleetResult(
                success=success,
                operation=operation,
                message=f"Imported {ok}/{len(files)} VRM/model file(s)",
                data={"imports": imports, "imported": ok, "total": len(files)},
                files=files,
                error="" if success else "PartialImport",
            ).model_dump()

        if operation == "pull_blender_vrm":
            if not object_name:
                return FleetResult(
                    success=False,
                    operation=operation,
                    message="object_name required",
                    error="ValueError",
                ).model_dump()
            vrm_stage.mkdir(parents=True, exist_ok=True)
            handoff = await _pull_blender_vrm_export(
                object_name=object_name,
                blender_url=burl,
                vrm_stage=vrm_stage,
                export_format=export_format,
            )
            success = bool(handoff.get("success"))
            return FleetResult(
                success=success,
                operation=operation,
                message="Blender VRM export staged" if success else "Blender VRM export incomplete",
                data=handoff,
                files=list(handoff.get("files") or []),
                error="" if success else str(handoff.get("error") or "BlenderVrmError"),
            ).model_dump()

        if operation == "pull_avatar_vrm":
            roots = _resolve_vrm_roots(vrm_stage, stage)
            avatar_online = await check_avatar_http_health(aurl)
            handoff: dict[str, Any] = {"avatar_reachable": avatar_online, "local_files_before": len(list_vrm_files(*roots))}

            if avatar_online:
                avatar_list = await call_avatar_tool(
                    aurl,
                    "avatar_manager",
                    {"operation": "list"},
                )
                handoff["avatar_list"] = avatar_list

            staged_files: list[str] = []
            for path in list_vrm_files(DEFAULT_AVATAR_VRM_DIR):
                staged = await stage_file(source_path=path, staging_dir=vrm_stage, subdir="avatar")
                if staged.get("success") and staged.get("staged_path"):
                    staged_files.append(str(staged["staged_path"]))

            imported = await resonite_fleet(
                "import_vrm_batch",
                staging_dir=str(stage),
                vrm_dir=str(vrm_stage),
                target_slot=target_slot,
            )
            success = bool(imported.get("success")) or bool(staged_files)
            return FleetResult(
                success=success,
                operation=operation,
                message="Avatar VRM pull complete" if success else "Avatar VRM pull partial",
                data={"handoff": handoff, "staged": staged_files, "import": imported.get("data")},
                files=list(imported.get("files") or staged_files),
                error="" if success else "AvatarPullError",
            ).model_dump()

        if operation == "list_protoflux_presets":
            if protoflux_preset:
                preset = get_protoflux_preset(protoflux_preset)
                if not preset:
                    return FleetResult(
                        success=False,
                        operation=operation,
                        message=f"Unknown preset: {protoflux_preset}",
                        error="ValueError",
                    ).model_dump()
                return FleetResult(
                    success=True,
                    operation=operation,
                    message=f"ProtoFlux preset {protoflux_preset}",
                    data={"preset": preset},
                ).model_dump()

            catalog = list_protoflux_presets()
            return FleetResult(
                success=True,
                operation=operation,
                message="ProtoFlux avatar preset catalog",
                data=catalog,
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

            if not skip_vrm:
                if object_name:
                    blender_vrm = await resonite_fleet(
                        "pull_blender_vrm",
                        object_name=object_name,
                        blender_url=burl,
                        vrm_dir=str(vrm_stage),
                        export_format=export_format,
                    )
                    steps.append(
                        {
                            "name": "pull_blender_vrm",
                            "success": bool(blender_vrm.get("success")),
                            "detail": blender_vrm,
                        }
                    )
                vrm_import = await resonite_fleet(
                    "import_vrm_batch",
                    staging_dir=str(stage),
                    vrm_dir=str(vrm_stage),
                    target_slot=target_slot,
                )
                steps.append(
                    {"name": "import_vrm_batch", "success": bool(vrm_import.get("success")), "detail": vrm_import}
                )

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
