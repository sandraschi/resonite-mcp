#!/usr/bin/env python3
"""Integration tools for cross-server workflows between Resonite and other MCPs.

No mocks. All functions make real HTTP/OSC calls.
"""

import logging
import tempfile
import uuid
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_TEMP_DIR = Path(tempfile.gettempdir()) / "resonite-mcp"


async def _download_to_temp(url: str, suffix: str) -> str:
    """Download a URL to a temp file and return the local path."""
    _TEMP_DIR.mkdir(parents=True, exist_ok=True)
    dest = _TEMP_DIR / f"wl_{uuid.uuid4().hex[:16]}{suffix}"
    if dest.exists():
        return str(dest)
    async with httpx.AsyncClient(timeout=300, follow_redirects=True) as client:
        async with client.stream("GET", url) as resp:
            resp.raise_for_status()
            with open(dest, "wb") as f:
                async for chunk in resp.aiter_bytes(65536):
                    f.write(chunk)
    return str(dest)


async def resonite_import_worldlabs_url(
    splat_url: str,
    mesh_url: str = "",
    world_name: str = "WorldLabs_World",
    target_slot: str = "root",
) -> dict[str, Any]:
    """Import a WorldLabs splat from a URL into Resonite.

    Two import paths:
    1. ResoniteLink WebSocket — if connected, sends importFile command
    2. Direct OSC — sends URL via OSC for Resonite-side ProtoFlux to pick up

    Returns the import result with local file paths.
    """
    results: dict[str, Any] = {
        "world_name": world_name,
        "target_slot": target_slot,
        "files": {},
    }

    # 1. Download the splat file
    try:
        splat_path = await _download_to_temp(splat_url, ".spz")
        results["files"]["splat"] = splat_path
    except Exception as e:
        results["files"]["splat_error"] = str(e)

    # 2. Download the mesh file (optional)
    if mesh_url:
        try:
            mesh_path = await _download_to_temp(mesh_url, ".glb")
            results["files"]["mesh"] = mesh_path
        except Exception as e:
            results["files"]["mesh_error"] = str(e)

    # 3. Try ResoniteLink import
    try:
        from ..resonite_link import ResoniteLinkClient

        client = ResoniteLinkClient()
        for kind, path_key in [("splat", "splat"), ("mesh", "mesh")]:
            path = results.get("files", {}).get(path_key)
            if not path or not Path(path).exists():
                continue
            payload = {
                "type": "importFile",
                "filePath": str(Path(path).resolve()),
                "targetSlotId": target_slot,
                "position": {"x": 0, "y": 0, "z": 0},
            }
            resp = await client._send(payload)
            results[f"rl_import_{kind}"] = resp
    except Exception as e:
        logger.info(f"ResoniteLink not available, falling back to OSC: {e}")
        results["rl_import"] = f"ResoniteLink unavailable: {e}"

    # 4. Always send OSC as well (for Resonite-side receivers)
    try:
        from ..models import OSCMessageInput
        from .osc import send_osc

        msg = OSCMessageInput(
            host="127.0.0.1", port=9000, address="/worldlabs/import",
            values=[splat_url, mesh_url, world_name],
        )
        await send_osc(msg)
        results["osc"] = "sent"
    except Exception as e:
        results["osc"] = f"OSC failed: {e}"

    results["status"] = "ok" if results.get("files", {}).get("splat") else "error"
    return results


async def resonite_import_worldlabs_batch(
    manifest: list[dict[str, Any]],
    *,
    target_slot: str = "root",
) -> dict[str, Any]:
    """Import multiple World Labs / Marble splats from a manifest."""
    imports: list[dict[str, Any]] = []
    ok = 0
    for entry in manifest:
        splat_url = str(entry.get("splat_url") or entry.get("url") or "")
        if not splat_url:
            imports.append({"success": False, "error": "missing splat_url", "entry": entry})
            continue
        result = await resonite_import_worldlabs_url(
            splat_url=splat_url,
            mesh_url=str(entry.get("mesh_url") or ""),
            world_name=str(entry.get("world_name") or entry.get("name") or "Marble_World"),
            target_slot=str(entry.get("target_slot") or target_slot),
        )
        success = result.get("status") == "ok"
        imports.append({"success": success, "entry": entry, "detail": result})
        if success:
            ok += 1
    return {
        "status": "ok" if ok == len(manifest) and manifest else ("partial" if ok else "error"),
        "imported": ok,
        "total": len(manifest),
        "imports": imports,
    }


async def resonite_import_blender(object_name: str, export_format: str = "glb") -> dict[str, Any]:
    """Export an object from Blender and import it into Resonite.

    Calls blender-mcp's tool endpoint at port 10849, downloads the result, and
    imports into Resonite via ResoniteLink.
    """
    results: dict[str, Any] = {"object_name": object_name}

    # 1. Call blender-mcp to export via /tool bridge
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "http://127.0.0.1:10849/tool",
                json={
                    "tool": "blender_export_presets",
                    "params": {
                        "operation": "export_with_preset",
                        "platform": "RESONITE",
                        "target_objects": [object_name],
                        "output_path": f"//{object_name}_resonite.glb",
                    },
                },
            )
            resp.raise_for_status()
            tool_result = resp.json()
            if tool_result.get("success") and tool_result.get("data"):
                export_data = tool_result["data"]
                file_url = (
                    export_data.get("url")
                    or export_data.get("file_path", "")
                    or str(export_data)
                )
            else:
                file_url = ""
            results["blender_export"] = "ok" if file_url else "no_file_path"
    except Exception as e:
        results["blender_export"] = f"Blender MCP not available: {e}"
        return results

    # 2. Download the exported file
    try:
        local_path = await _download_to_temp(file_url, f".{export_format}")
        results["local_path"] = local_path
    except Exception as e:
        results["download_error"] = str(e)
        return results

    # 3. Import via ResoniteLink
    try:
        from ..resonite_link import ResoniteLinkClient

        client = ResoniteLinkClient()
        payload = {
            "type": "importFile",
            "filePath": str(Path(local_path).resolve()),
            "targetSlotId": "root",
            "position": {"x": 0, "y": 0, "z": 0},
        }
        rl_resp = await client._send(payload)
        results["rl_import"] = rl_resp
    except Exception as e:
        results["rl_import"] = f"ResoniteLink unavailable: {e}"

    results["status"] = "ok"
    return results


async def resonite_avatar_unity(
    avatar_model_path: str, unity_package_path: str | None = None,
) -> dict[str, Any]:
    """Sync avatar data between Unity3D and Resonite.

    Downloads the avatar model from Unity3D-mcp and imports via ResoniteLink.
    """
    results: dict[str, Any] = {"avatar_path": avatar_model_path}

    try:
        local_path = await _download_to_temp(avatar_model_path, ".glb")
        results["local_path"] = local_path
    except Exception as e:
        results["download_error"] = str(e)
        return results

    try:
        from ..resonite_link import ResoniteLinkClient

        client = ResoniteLinkClient()
        payload = {
            "type": "importFile",
            "filePath": str(Path(local_path).resolve()),
            "targetSlotId": "root",
            "position": {"x": 0, "y": 0, "z": 0},
        }
        rl_resp = await client._send(payload)
        results["rl_import"] = rl_resp
    except Exception as e:
        results["rl_import"] = f"ResoniteLink unavailable: {e}"

    results["status"] = "ok"
    return results
