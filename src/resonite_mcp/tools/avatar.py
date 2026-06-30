"""Avatar Control Tools - Portmanteau for Resonite avatar and ProtoFlux operations.

This module provides comprehensive avatar control functionality for Resonite,
including avatar loading, parameter manipulation, and ProtoFlux script execution.
"""

import logging
from typing import Any

from ..models import AvatarControlInput, OSCMessageInput, ProtoFluxScriptInput
from ..server import server
from .osc import send_osc

logger = logging.getLogger(__name__)


async def resonite_avatar_load(input_data: AvatarControlInput) -> dict[str, Any]:
    """Load an avatar into the current Resonite session.

    Args:
        input_data: Avatar loading configuration (avatar_id, slot, parameters)

    Returns:
        Dictionary with avatar loading status
    """
    avatar_path = input_data.avatar_id
    slot = input_data.slot if input_data.slot is not None else 0
    parameters = input_data.parameters

    try:
        # Send avatar load command via OSC
        osc_input = OSCMessageInput(
            host="127.0.0.1", port=9000, address="/resonite/avatar/load", values=[avatar_path, slot]
        )
        result = await send_osc(osc_input)

        if result["status"] == "success":
            response = {
                "status": "success",
                "message": f"Avatar load initiated: {avatar_path} (slot {slot})",
            }

            # Set initial parameters if provided
            if parameters:
                for param_name, param_value in parameters.items():
                    await resonite_parameter_set(param_name, param_value, slot)

            return response
        else:
            return result

    except Exception as e:
        error = f"Failed to load avatar {avatar_path}: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


server.tool()(resonite_avatar_load)


async def resonite_parameter_set(parameter_name: str, value: float, avatar_slot: int | None = None) -> dict[str, Any]:
    """Set an avatar parameter value in Resonite.

    Args:
        parameter_name: Name of the parameter to set
        value: Parameter value (typically 0.0 to 1.0)
        avatar_slot: Specific avatar slot (0-7), affects all if not specified
    """
    try:
        address = f"/avatar/parameters/{parameter_name}"
        if avatar_slot is not None:
            address = f"/avatar/{avatar_slot}/parameters/{parameter_name}"

        osc_input = OSCMessageInput(host="127.0.0.1", port=9000, address=address, values=[float(value)])
        result = await send_osc(osc_input)

        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"Parameter '{parameter_name}' set to {value}",
            }
        return result
    except Exception as e:
        error = f"Failed to set parameter: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


server.tool()(resonite_parameter_set)


async def resonite_protoflux_execute(input_data: ProtoFluxScriptInput) -> dict[str, Any]:
    """Execute a ProtoFlux script in Resonite.

    Args:
        input_data: Script configuration (script_name, script_data, execute)
    """
    script_name = input_data.script_name
    parameters = input_data.script_data or {}

    try:
        osc_input = OSCMessageInput(
            host="127.0.0.1",
            port=9000,
            address="/protoflux/execute",
            values=[script_name, parameters],
        )
        result = await send_osc(osc_input)

        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"ProtoFlux script '{script_name}' executed",
            }
        return result
    except Exception as e:
        error = f"Failed to execute ProtoFlux script: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


server.tool()(resonite_protoflux_execute)
