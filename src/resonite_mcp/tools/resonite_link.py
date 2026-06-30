"""ResoniteLink Tools — Low-level WebSocket protocol control + high-level convenience.

Surfaces the ResoniteLinkClient (WebSocket JSON protocol v0.8.3) as individual
MCP tools for slot/component CRUD, field read/write, and component discovery.
"""

import logging
from typing import Any

from ..models import (
    ResoniteLinkConnectInput,
    ResoniteLinkGetInput,
    ResoniteLinkSetInput,
    ResoniteLinkSpawnInput,
)
from ..server import server

logger = logging.getLogger(__name__)


async def get_client():
    """Helper to get the initialized ResoniteLink client."""
    from .. import server as server_mod

    if not hasattr(server_mod, "resonite_link_client") or server_mod.resonite_link_client is None:
        from ..resonite_link import ResoniteLinkClient

        server_mod.resonite_link_client = ResoniteLinkClient()
    return server_mod.resonite_link_client


# ── Connection ──────────────────────────────────────────────────────────────────


@server.tool()
async def resonite_link_connect(input_data: ResoniteLinkConnectInput) -> dict[str, Any]:
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


# ── Spawn / convenience ────────────────────────────────────────────────────────


@server.tool()
async def resonite_link_spawn(input_data: ResoniteLinkSpawnInput) -> dict[str, Any]:
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


# ── Low-level field access ─────────────────────────────────────────────────────


@server.tool()
async def resonite_link_read_field(ref_id: str) -> dict[str, Any]:
    """Read a field value by its ref ID via ResoniteLink.

    Use resonite_link_reflect() first to discover ref IDs for component fields.

    Args:
        ref_id: The ref ID of the field to read (e.g. 'S-...F-...')

    ## Return Format
    {"success": bool, "ref_id": str, "value": any}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}

    try:
        value = await client.read_field(ref_id)
        return {"status": "success", "ref_id": ref_id, "value": value}
    except Exception as e:
        return {"status": "error", "ref_id": ref_id, "message": str(e)}


@server.tool()
async def resonite_link_write_field(
    ref_id: str,
    value: Any,
    value_type: str = "",
) -> dict[str, Any]:
    """Write a value to a field by its ref ID via ResoniteLink.

    Args:
        ref_id: The ref ID of the field to write
        value: The value to write (number, string, bool, or typed object)
        value_type: Optional C# type hint (e.g. "System.Single", "UnityEngine.Color")

    ## Return Format
    {"success": bool, "ref_id": str, "value": any}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}

    try:
        resp = await client.write_field(ref_id, value, value_type or None)
        return {"status": "success", "ref_id": ref_id, "value": value, "response": resp}
    except Exception as e:
        return {"status": "error", "ref_id": ref_id, "message": str(e)}


# ── Slot / component CRUD ──────────────────────────────────────────────────────


@server.tool()
async def resonite_link_get_node(ref_id: str) -> dict[str, Any]:
    """Get slot or component information by ref ID via ResoniteLink.

    Args:
        ref_id: Ref ID of the slot or component to inspect

    ## Return Format
    {"success": bool, "ref_id": str, "node": {...}}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}

    try:
        node = await client.get_node(ref_id)
        return {"status": "success", "ref_id": ref_id, "node": node}
    except Exception as e:
        return {"status": "error", "ref_id": ref_id, "message": str(e)}


@server.tool()
async def resonite_link_get_children(slot_id: str) -> dict[str, Any]:
    """List direct children of a slot via ResoniteLink.

    Args:
        slot_id: Ref ID of the parent slot

    ## Return Format
    {"success": bool, "slot_id": str, "children": [...], "count": int}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}

    try:
        children = await client.get_children(slot_id)
        return {
            "status": "success",
            "slot_id": slot_id,
            "children": children,
            "count": len(children),
        }
    except Exception as e:
        return {"status": "error", "slot_id": slot_id, "message": str(e)}


@server.tool()
async def resonite_link_add_slot(parent_id: str, name: str = "Slot") -> dict[str, Any]:
    """Create a new empty slot under a parent slot via ResoniteLink.

    Args:
        parent_id: Ref ID of the parent slot
        name: Name for the new slot

    ## Return Format
    {"success": bool, "parent_id": str, "slot_id": str, "name": str}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}

    try:
        slot_id = await client.add_slot(parent_id, name)
        return {
            "status": "success",
            "parent_id": parent_id,
            "slot_id": slot_id,
            "name": name,
        }
    except Exception as e:
        return {"status": "error", "parent_id": parent_id, "message": str(e)}


@server.tool()
async def resonite_link_add_component(
    slot_id: str,
    component_type: str,
) -> dict[str, Any]:
    """Add a component to a slot via ResoniteLink.

    Use resonite_link_reflect() to discover available component types.

    Args:
        slot_id: Ref ID of the target slot
        component_type: Fully qualified C# type (e.g. "FrooxEngine.AudioStreamController")

    ## Return Format
    {"success": bool, "slot_id": str, "component_id": str, "component_type": str}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}

    try:
        comp_id = await client.add_component(slot_id, component_type)
        return {
            "status": "success",
            "slot_id": slot_id,
            "component_id": comp_id,
            "component_type": component_type,
        }
    except Exception as e:
        return {"status": "error", "slot_id": slot_id, "message": str(e)}


@server.tool()
async def resonite_link_destroy_slot(
    slot_id: str,
    preserve_assets: bool = False,
) -> dict[str, Any]:
    """Destroy a slot and its children via ResoniteLink.

    Args:
        slot_id: Ref ID of the slot to destroy
        preserve_assets: If True, keep asset references alive

    ## Return Format
    {"success": bool, "slot_id": str}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}

    try:
        resp = await client.destroy_slot(slot_id, preserve_assets)
        return {"status": "success", "slot_id": slot_id, "response": resp}
    except Exception as e:
        return {"status": "error", "slot_id": slot_id, "message": str(e)}


# ── Component discovery ────────────────────────────────────────────────────────


@server.tool()
async def resonite_link_reflect(
    component_type: str = "",
) -> dict[str, Any]:
    """Discover component types and their fields via ResoniteLink Reflect API (v0.8.3+).

    Without component_type: returns all supported component types.
    With component_type: returns fields/members for that type.

    Args:
        component_type: Optional C# type to inspect (e.g. "FrooxEngine.ValueField`1")

    ## Return Format
    {"success": bool, "types": [...]} or {"success": bool, "component_type": str, "fields": [...]}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}

    try:
        resp = await client.reflect(component_type or None)
        if component_type:
            return {
                "status": "success",
                "component_type": component_type,
                "data": resp,
            }
        else:
            return {"status": "success", "types": resp}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── Batch operations ───────────────────────────────────────────────────────────


@server.tool()
async def resonite_link_batch(
    operations: list[dict[str, Any]],
) -> dict[str, Any]:
    """Execute multiple ResoniteLink operations atomically (v0.8.3+).

    Each operation is a dict with "type" key and its fields:
    - {"type": "ReadField", "refId": "..."}
    - {"type": "WriteField", "refId": "...", "value": ...}
    - {"type": "AddSlot", "refId": "...", "name": "Slot"}
    - {"type": "DestroySlot", "refId": "...", "preserveAssets": false}

    Args:
        operations: List of operation dicts (without top-level "id")

    ## Return Format
    {"success": bool, "results": [...], "count": int}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}

    try:
        results = await client.batch(operations)
        return {
            "status": "success",
            "results": results,
            "count": len(results),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── Legacy high-level helpers ──────────────────────────────────────────────────


@server.tool()
async def resonite_link_set(input_data: ResoniteLinkSetInput) -> dict[str, Any]:
    """Set a value on a Resonite component field.

    Requires the unique ID of the component and the field name.
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}

    success = await client.set_component_value(input_data.component_id, input_data.field, input_data.value)
    return {
        "status": "success" if success else "error",
        "component_id": input_data.component_id,
        "field": input_data.field,
        "value": input_data.value,
    }


@server.tool()
async def resonite_link_get(input_data: ResoniteLinkGetInput) -> dict[str, Any]:
    """Request a value from a Resonite component field.

    The value will be returned asynchronously via updates if subscribed,
    or this command will return the current state if supported by the link.
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}

    success = await client.get_component_value(input_data.component_id, input_data.field)
    return {
        "status": "success" if success else "error",
        "component_id": input_data.component_id,
        "field": input_data.field,
    }
