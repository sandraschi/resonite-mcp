"""ResoniteLink Tools - Individual tool registration.

This module provides high-level tools for interacting with Resonite via the
ResoniteLink WebSocket JSON protocol.
"""

import logging
from typing import Any, Dict

from ..models import (
    ResoniteLinkConnectInput,
    ResoniteLinkSpawnInput,
    ResoniteLinkSetInput,
    ResoniteLinkGetInput,
)
from ..server import server

logger = logging.getLogger(__name__)

# The client will be initialized in server.py and made available via imports
# or we can use a getter from a shared state.
# For simplicity in this architecture, we'll try to get it from the server module's globals.


async def get_client():
    """Helper to get the initialized ResoniteLink client."""
    from .. import server as server_mod

    if (
        not hasattr(server_mod, "resonite_link_client")
        or server_mod.resonite_link_client is None
    ):
        from ..resonite_link import ResoniteLinkClient

        server_mod.resonite_link_client = ResoniteLinkClient()
    return server_mod.resonite_link_client


@server.tool()
async def resonite_link_connect(input_data: ResoniteLinkConnectInput) -> Dict[str, Any]:
    """Connect to the ResoniteLink WebSocket server.

    Resonite must be running with the ResoniteLink mod/plugin enabled.
    Default port is usually 4242.
    """
    client = await get_client()
    client.uri = f"ws://{input_data.host}:{input_data.port}"
    success = await client.connect()

    if success:
        return {
            "status": "success",
            "message": f"Connected to ResoniteLink at {client.uri}",
            "host": input_data.host,
            "port": input_data.port,
        }
    else:
        return {
            "status": "error",
            "message": f"Failed to connect to ResoniteLink at {client.uri}",
            "host": input_data.host,
            "port": input_data.port,
        }


@server.tool()
async def resonite_link_spawn(input_data: ResoniteLinkSpawnInput) -> Dict[str, Any]:
    """Spawn a 3D object in Resonite using a template URL.

    Example template_url: "resonite:///items/ExampleCube.7pb"
    """
    client = await get_client()
    if not client.running:
        return {
            "status": "error",
            "message": "ResoniteLink not connected. Call resonite_link_connect first.",
        }

    success = await client.spawn_object(input_data.template_url, input_data.position)
    return {
        "status": "success" if success else "error",
        "action": "spawn",
        "template_url": input_data.template_url,
    }


@server.tool()
async def resonite_link_set(input_data: ResoniteLinkSetInput) -> Dict[str, Any]:
    """Set a value on a Resonite component field.

    Requires the unique ID of the component and the field name.
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}

    success = await client.set_component_value(
        input_data.component_id, input_data.field, input_data.value
    )
    return {
        "status": "success" if success else "error",
        "component_id": input_data.component_id,
        "field": input_data.field,
        "value": input_data.value,
    }


@server.tool()
async def resonite_link_get(input_data: ResoniteLinkGetInput) -> Dict[str, Any]:
    """Request a value from a Resonite component field.

    The value will be returned asynchronously via updates if subscribed,
    or this command will return the current state if supported by the link.
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}

    success = await client.get_component_value(
        input_data.component_id, input_data.field
    )
    return {
        "status": "success" if success else "error",
        "component_id": input_data.component_id,
        "field": input_data.field,
    }
