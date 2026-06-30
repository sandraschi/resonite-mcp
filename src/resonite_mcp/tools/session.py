"""Session Management Tools - Portmanteau for Resonite session and world operations.

This module provides comprehensive session management functionality for Resonite,
including session initialization, world loading, and session lifecycle management.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from ..models import OSCMessageInput, ResoniteSessionInput
from ..server import server
from .osc import osc_clients, osc_servers, send_osc

logger = logging.getLogger(__name__)


async def resonite_session_start(input_data: ResoniteSessionInput) -> dict[str, Any]:
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
        osc_input = OSCMessageInput(host="127.0.0.1", port=9000, address="/resonite/session/start", values=[session_id])
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
            "message": f"Failed to start Resonite session: {e!s}",
        }


server.tool()(resonite_session_start)


async def resonite_session_status() -> dict[str, Any]:
    """Get the current status of the active Resonite session.

    Returns:
        Dictionary with session status and active components

    Examples:
        Check session status: resonite_session_status()
    """
    try:
        from ..server import is_resonite_running, resonite_link_client

        res_running = is_resonite_running()
        link_connected = resonite_link_client.running if resonite_link_client else False
        osc_active = len(osc_servers) > 0

        session_status = {
            "resonite_running": res_running,
            "osc_servers_active": osc_active,
            "osc_ports": list(osc_servers.keys()),
            "resonite_link_connected": link_connected,
            "mcp_server": "healthy",
        }

        if not res_running:
            session_status["note"] = (
                "Resonite.exe is not detected as running. "
                "Start Resonite and enable OSC input before using session tools."
            )

        return {"status": "success", "session_status": session_status}

    except Exception as e:
        logger.error(f"Failed to get session status: {e}")
        return {"status": "error", "message": f"Failed to get session status: {e!s}"}


server.tool()(resonite_session_status)


async def resonite_world_load(world_path: str) -> dict[str, Any]:
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

        from ..server import is_resonite_running

        if not is_resonite_running():
            return {
                "status": "error",
                "message": "Resonite is not running. Start Resonite first, then retry.",
                "world_path": world_path,
            }

        # Send OSC command to load the world
        osc_input = OSCMessageInput(host="127.0.0.1", port=9000, address="/resonite/world/load", values=[world_path])
        osc_result = await send_osc(osc_input)

        world_info = {
            "world_path": world_path,
            "world_name": world_path.split("/")[-1],
            "osc_status": osc_result["status"],
            "world_type": "public" if world_path.startswith("resonite://") else "private",
        }

        logger.info(f"World load command sent: {world_path} (OSC={osc_result['status']})")
        return {
            "status": osc_result["status"],
            "message": f"World load command sent for '{world_info['world_name']}': {osc_result['message']}",
            "world": world_info,
        }

    except Exception as e:
        logger.error(f"Failed to load world {world_path}: {e}")
        return {
            "status": "error",
            "message": f"Failed to load world: {e!s}",
            "world_path": world_path,
        }


server.tool()(resonite_world_load)


async def resonite_session_end() -> dict[str, Any]:
    """End the current Resonite session and clean up resources.

    Returns:
        Dictionary with session cleanup status

    Examples:
        End session: resonite_session_end()
    """
    try:
        from ..server import resonite_link_client

        cleaned = []
        errors = []

        # Close OSC servers
        for port, srv in list(osc_servers.items()):
            try:
                srv.shutdown()
                del osc_servers[port]
                cleaned.append(f"osc_server:{port}")
            except Exception as e:
                errors.append(f"osc_server:{port}:{e}")

        # Clear OSC client cache
        osc_clients.clear()
        cleaned.append("osc_clients")

        # Disconnect ResoniteLink
        if resonite_link_client and resonite_link_client.running:
            try:
                await resonite_link_client.disconnect()
                cleaned.append("resonite_link")
            except Exception as e:
                errors.append(f"resonite_link:{e}")

        logger.info(f"Resonite session ended: cleaned={cleaned}, errors={len(errors)}")
        return {
            "status": "success" if not errors else "partial",
            "message": f"Session cleanup: {len(cleaned)} resources closed, {len(errors)} errors",
            "cleanup": {"cleaned": cleaned, "errors": errors},
        }

    except Exception as e:
        logger.error(f"Failed to end session: {e}")
        return {"status": "error", "message": f"Failed to end session: {e!s}"}


server.tool()(resonite_session_end)
