"""VBOT Robotics Tools — OSC-driven virtual robot control in Resonite.

Wraps the vBot OSC receiver spec (docs/VBOT_OSC_RECEIVER.md) as MCP tools.
Sends UDP OSC messages to Resonite on port 9000 for vBot spawn/move/head/stop.

vBot types: yahboom (vBoomy), mechazilla (vMechazilla), bumi (vBumi), godzilla, custom
"""

import logging
from typing import Any

from ..models import OSCMessageInput
from ..server import server
from ..utils.vbot_osc_receiver import (
    DEFAULT_OSC_PORT,
    VBOOMY_SPAWN_ADDRESS,
    list_vbot_types,
    robot_address,
)

logger = logging.getLogger(__name__)


async def _send_vbot_osc(address: str, values: list[Any]) -> dict[str, Any]:
    """Send an OSC message to Resonite for vBot control."""
    from .osc import send_osc as osc_send

    try:
        result = await osc_send(
            OSCMessageInput(
                host="127.0.0.1",
                port=DEFAULT_OSC_PORT,
                address=address,
                values=values,
            )
        )
        return result
    except Exception as e:
        logger.error("vBot OSC send failed (%s): %s", address, e)
        return {"status": "error", "message": str(e)}


@server.tool()
async def resonite_vbot_list_types() -> dict[str, Any]:
    """List available vBot robot types and their OSC contracts.

    Returns types: yahboom (vBoomy), mechazilla (vMechazilla), bumi (vBumi),
    godzilla (kaiju scale), custom. Each type has default scale and drive mode.

    ## Return Format
    {"status": "success", "types": [...], "count": int}
    """
    catalog = list_vbot_types()
    return {
        "status": "success",
        "types": catalog.get("types", []),
        "count": catalog.get("count", 0),
    }


@server.tool()
async def resonite_vbot_spawn(
    robot_type: str = "yahboom",
    robot_id: str = "",
    position_x: float = 0.0,
    position_y: float = 0.0,
    position_z: float = 0.0,
    scale: float = 0.0,
) -> dict[str, Any]:
    """Spawn a vBot in Resonite at the given position and scale.

    The Resonite world must have the vBot OSC receiver ProtoFlux graph
    listening on port 9000 (see docs/VBOT_OSC_RECEIVER.md).

    Args:
        robot_type: yahboom, mechazilla, bumi, godzilla, or custom
        robot_id: Unique robot ID (auto-generated if empty)
        position_x/y/z: Spawn position in 3D world coordinates
        scale: Spawn scale. Use 0 for type default.

    ## Return Format
    {"success": bool, "robot_id": str, "robot_type": str, "position": {...}}
    """
    from ..utils.vbot_osc_receiver import VBOT_ROBOT_TYPES

    type_meta = VBOT_ROBOT_TYPES.get(robot_type, VBOT_ROBOT_TYPES["custom"])
    rid = robot_id or type_meta.get("default_robot_id", f"vbot_{robot_type}_01")
    s = scale if scale > 0 else type_meta.get("default_scale", 1.0)

    result = await _send_vbot_osc(
        VBOOMY_SPAWN_ADDRESS,
        [rid, robot_type, position_x, position_y, position_z, s],
    )
    return {
        "status": result.get("status", "error"),
        "message": f"vBot spawn OSC sent for {rid} ({robot_type})",
        "robot_id": rid,
        "robot_type": robot_type,
        "position": {"x": position_x, "y": position_y, "z": position_z},
        "scale": s,
        "osc_result": result,
    }


@server.tool()
async def resonite_vbot_move(
    robot_id: str,
    linear: float = 0.0,
    angular: float = 0.0,
) -> dict[str, Any]:
    """Send move command to a vBot in Resonite.

    Holonomic drive: linear = forward/backward speed (m/s), angular = yaw rotation (rad/s).

    Args:
        robot_id: The robot ID (e.g. "vbot_yahboom_01")
        linear: Forward velocity in m/s (positive = forward)
        angular: Yaw angular velocity in rad/s (positive = clockwise)

    ## Return Format
    {"success": bool, "robot_id": str, "linear": float, "angular": float}
    """
    result = await _send_vbot_osc(
        robot_address(robot_id, "move"),
        [linear, angular],
    )
    return {
        "status": result.get("status", "error"),
        "message": f"vBot move OSC sent for {robot_id}",
        "robot_id": robot_id,
        "linear": linear,
        "angular": angular,
        "osc_result": result,
    }


@server.tool()
async def resonite_vbot_head(
    robot_id: str,
    yaw_deg: float = 0.0,
    pitch_deg: float = 0.0,
) -> dict[str, Any]:
    """Move the vBot head to the given yaw/pitch angles.

    Args:
        robot_id: The robot ID
        yaw_deg: Yaw angle in degrees
        pitch_deg: Pitch angle in degrees

    ## Return Format
    {"success": bool, "robot_id": str, "yaw_deg": float, "pitch_deg": float}
    """
    result = await _send_vbot_osc(
        robot_address(robot_id, "head"),
        [yaw_deg, pitch_deg],
    )
    return {
        "status": result.get("status", "error"),
        "message": f"vBot head OSC sent for {robot_id}",
        "robot_id": robot_id,
        "yaw_deg": yaw_deg,
        "pitch_deg": pitch_deg,
        "osc_result": result,
    }


@server.tool()
async def resonite_vbot_stop(robot_id: str) -> dict[str, Any]:
    """Stop a vBot — zero all locomotion commands.

    Args:
        robot_id: The robot ID to stop

    ## Return Format
    {"success": bool, "robot_id": str}
    """
    result = await _send_vbot_osc(
        robot_address(robot_id, "stop"),
        [1.0],
    )
    return {
        "status": result.get("status", "error"),
        "message": f"vBot stop OSC sent for {robot_id}",
        "robot_id": robot_id,
        "osc_result": result,
    }
