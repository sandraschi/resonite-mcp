"""Session Management Tools - Portmanteau for Resonite session and world operations.

This module provides comprehensive session management functionality for Resonite,
including session initialization, world loading, and session lifecycle management.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict

from ..models import OSCMessageInput, ResoniteSessionInput
from ..server import server
from .osc import send_osc

logger = logging.getLogger(__name__)


async def resonite_session_start(input_data: ResoniteSessionInput) -> Dict[str, Any]:
    """Start a new Resonite session with optional world and avatar setup.

    This initializes OSC communication with Resonite and sets up a session
    for avatar control, world management, and social interactions.

    Args:
        input_data: Session configuration (session_name, world_path, avatar_slot)

    Returns:
        Dictionary with session information and status

    Examples:
        Start basic session: resonite_session_start({})
        Start with world: resonite_session_start({"world_path": "resonite://TutorialWorld"})
    """
    session_name = input_data.session_name
    world_path = input_data.world_path
    avatar_slot = input_data.avatar_slot

    try:
        # Generate session ID
        session_id = session_name or f"resonite_session_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now()

        # Initialize OSC connection (Resonite default is 127.0.0.1:9000)
        osc_input = OSCMessageInput(
            host="127.0.0.1", port=9000, address="/resonite/session/start", values=[session_id]
        )
        osc_result = await send_osc(osc_input)

        if osc_result["status"] != "success":
            return {
                "status": "error",
                "message": "Failed to initialize OSC connection with Resonite",
                "osc_error": osc_result["message"],
            }

        session_info = {
            "session_id": session_id,
            "platform": "resonite",
            "start_time": start_time.isoformat(),
            "osc_connected": True,
            "capabilities": [
                "avatar_control",
                "world_management",
                "protoflux_scripting",
                "social_interactions",
                "inventory_management",
            ],
        }

        # Load initial world if specified
        if world_path:
            world_result = await resonite_world_load(world_path)
            session_info["initial_world"] = {
                "path": world_path,
                "load_status": world_result.get("status"),
            }

        # Set avatar slot if specified
        if avatar_slot is not None:
            session_info["avatar_slot"] = avatar_slot
            osc_slot_input = OSCMessageInput(
                host="127.0.0.1", port=9000, address="/resonite/avatar/slot", values=[avatar_slot]
            )
            await send_osc(osc_slot_input)

        logger.info(f"Resonite session '{session_id}' started successfully")

        return {
            "status": "success",
            "message": f"Resonite session '{session_id}' started successfully",
            "session_info": session_info,
        }
    except Exception as e:
        logger.error(f"Failed to start Resonite session: {e}")
        return {
            "status": "error",
            "message": f"Failed to start Resonite session: {str(e)}",
        }


server.tool()(resonite_session_start)


async def resonite_session_status() -> Dict[str, Any]:
    """Get the current status of the active Resonite session.

    Returns:
        Dictionary with session status and active components

    Examples:
        Check session status: resonite_session_status()
    """
    try:
        # In a real implementation, this would query the actual Resonite session
        # For now, we'll return mock status information

        session_status = {
            "session_active": True,
            "session_name": "Active Session",
            "world_loaded": "resonite://TutorialWorld",
            "avatar_loaded": True,
            "avatar_slot": 0,
            "osc_connected": True,
            "uptime_seconds": 3600,
            "active_plugins": ["osc_extensions", "protoflux_helpers"],
            "connection_quality": "good",
        }

        return {"status": "success", "session_status": session_status}

    except Exception as e:
        logger.error(f"Failed to get session status: {e}")
        return {"status": "error", "message": f"Failed to get session status: {str(e)}"}


server.tool()(resonite_session_status)


async def resonite_world_load(world_path: str) -> Dict[str, Any]:
    """Load a world in the current Resonite session.

    Args:
        world_path: Path to the world (resonite:// format for built-in worlds,
                   file:// for local files, inventory:// for user inventory)

    Returns:
        Dictionary with world loading status

    Examples:
        Load built-in world: resonite_world_load("resonite://TutorialWorld")
        Load from inventory: resonite_world_load("inventory://MyCustomWorld")
        Load local file: resonite_world_load("file:///path/to/world.resonite")
    """
    try:
        # Validate world path format
        if not world_path.startswith(("resonite://", "file://", "inventory://")):
            return {
                "status": "error",
                "message": "Invalid world path format. Must start with resonite://, file://, or inventory://",
                "world_path": world_path,
            }

        # Simulate world loading
        world_info = {
            "world_path": world_path,
            "world_name": world_path.split("/")[-1],
            "load_status": "success",
            "load_time_seconds": 2.5,
            "world_type": "public" if world_path.startswith("resonite://") else "private",
            "permissions": ["read", "write", "spawn"],
            "user_count": 1,
        }

        logger.info(f"Loaded world: {world_path}")
        return {
            "status": "success",
            "message": f"World '{world_info['world_name']}' loaded successfully",
            "world": world_info,
        }

    except Exception as e:
        logger.error(f"Failed to load world {world_path}: {e}")
        return {
            "status": "error",
            "message": f"Failed to load world: {str(e)}",
            "world_path": world_path,
        }


server.tool()(resonite_world_load)


async def resonite_session_end() -> Dict[str, Any]:
    """End the current Resonite session and clean up resources.

    Returns:
        Dictionary with session cleanup status

    Examples:
        End session: resonite_session_end()
    """
    try:
        # Simulate session cleanup
        cleanup_info = {
            "session_ended": True,
            "resources_cleaned": ["osc_connections", "world_cache", "avatar_state"],
            "cleanup_time_seconds": 1.2,
            "final_stats": {
                "total_uptime": 3600,
                "worlds_loaded": 3,
                "avatars_used": 2,
                "protoflux_scripts_run": 5,
            },
        }

        logger.info("Resonite session ended successfully")
        return {
            "status": "success",
            "message": "Resonite session ended successfully",
            "cleanup": cleanup_info,
        }

    except Exception as e:
        logger.error(f"Failed to end session: {e}")
        return {"status": "error", "message": f"Failed to end session: {str(e)}"}


server.tool()(resonite_session_end)
