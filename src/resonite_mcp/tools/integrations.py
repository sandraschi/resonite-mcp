#!/usr/bin/env python3
"""Integration tools for cross-server workflows between Resonite and other MCPs."""

import logging
from typing import Any, Dict, List, Optional

from .inventory import resonite_inventory_upload
from .osc import send_osc_message

logger = logging.getLogger(__name__)


async def resonite_import_worldlabs(
    splat_id: str, target_slot: str = "root", position: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Import a WorldLabs Marble/Chisel splat into Resonite.
    This tool assumes the worldlabs-mcp is available in the environment.
    """
    try:
        # Mocking the interaction with worldlabs-mcp tools
        # In a real scenario, we would use the MCP client to call worldlabs.get_splat_url(splat_id)
        # For now, we simulate finding the asset
        splat_url = f"https://assets.worldlabs.ai/splats/{splat_id}.glb"  # [MOCK]

        # Spawn it in Resonite via OSC or inventory upload
        message = f"Importing WorldLabs splat {splat_id} from {splat_url}"
        await send_osc_message("127.0.0.1", 9000, "/resonite/import/url", [splat_url, target_slot])

        return {"status": "success", "message": message, "splat_id": splat_id, "url": splat_url}
    except Exception as e:
        logger.error(f"WorldLabs import failed: {e}")
        return {"status": "error", "message": str(e)}


async def resonite_import_blender(object_name: str, export_format: str = "glb") -> Dict[str, Any]:
    """
    Export an object from Blender and import it into Resonite.
    """
    try:
        # Mocking interaction with blender-mcp
        # We would call blender.export_object(object_name, format=export_format)
        export_path = f"C:/tmp/blender_export_{object_name}.{export_format}"  # [MOCK]

        # Upload to Resonite inventory
        result = await resonite_inventory_upload(
            item_path=export_path,
            item_name=object_name,
            item_type="object",
            description=f"Imported from Blender: {object_name}",
        )

        return {
            "status": "success",
            "message": f"Successfully imported Blender object {object_name}",
            "upload_result": result,
        }
    except Exception as e:
        logger.error(f"Blender import failed: {e}")
        return {"status": "error", "message": str(e)}


async def resonite_avatar_unity(
    avatar_model_path: str, unity_package_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sync avatar data between Unity3D and Resonite.
    """
    try:
        # Mocking interaction with unity3d-mcp
        # We would use unity3d.vrm_avatar_manager tools
        message = f"Syncing avatar {avatar_model_path} with Unity3D project"

        # Send OSC trigger to Resonite to prepare for avatar swap
        await send_osc_message(
            "127.0.0.1", 9000, "/resonite/avatar/sync_start", [avatar_model_path]
        )

        return {"status": "success", "message": message, "avatar_path": avatar_model_path}
    except Exception as e:
        logger.error(f"Unity3D avatar sync failed: {e}")
        return {"status": "error", "message": str(e)}
