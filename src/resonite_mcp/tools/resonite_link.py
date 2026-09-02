"""ResoniteLink Tools - real-protocol WebSocket control (target 0.13.1).

Surfaces the ResoniteLinkClient as MCP tools: LAN session discovery,
slot/component CRUD, member read/write, sync method calls, reflection,
and batching. Wire format verified against upstream 0.13.1.
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


# ── Discovery & connection ─────────────────────────────────────────────────────


@server.tool()
async def resonite_link_discover(timeout_seconds: float = 12.0) -> dict[str, Any]:
    """Discover ResoniteLink sessions announced on the local network (UDP 12512).

    Resonite (0.12.0+ protocol) broadcasts active ResoniteLink sessions every
    ~10 seconds. Use this instead of guessing the port; then connect with
    resonite_link_connect using the discovered linkPort.

    Args:
        timeout_seconds: How long to listen (default 12s catches one announce cycle)

    ## Return Format
    {"status": str, "sessions": [{"sessionName", "sessionID", "linkPort", "host"}], "count": int}
    """
    from ..resonite_link import discover_sessions

    try:
        sessions = await discover_sessions(timeout=timeout_seconds)
        return {"status": "success", "sessions": sessions, "count": len(sessions)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@server.tool()
async def resonite_link_connect(input_data: ResoniteLinkConnectInput) -> dict[str, Any]:
    """Connect to the ResoniteLink WebSocket server.

    ResoniteLink is built into Resonite (no mod needed); the session HOST must
    enable it: Dashboard -> Session -> Settings -> Enable ResoniteLink.
    Default port 4242, but prefer resonite_link_discover to find the real port.

    ## Return Format
    {"status": str, "message": str, "session_info": {resoniteVersion, resoniteLinkVersion, uniqueSessionId}}
    """
    client = await get_client()
    client.host = input_data.host
    client.port = input_data.port
    client.uri = f"ws://{input_data.host}:{input_data.port}"
    success = await client.connect()

    if success:
        return {
            "status": "success",
            "message": f"Connected to ResoniteLink at {client.uri}",
            "session_info": client.session_info,
            "host": input_data.host,
            "port": input_data.port,
        }
    return {
        "status": "error",
        "message": (
            f"Failed to connect to ResoniteLink at {client.uri}. "
            "Is Resonite running and ResoniteLink enabled for the session? "
            "Try resonite_link_discover to find active sessions."
        ),
        "host": input_data.host,
        "port": input_data.port,
    }


# ── Slots ──────────────────────────────────────────────────────────────────────


@server.tool()
async def resonite_link_get_slot(
    slot_id: str = "Root",
    include_component_data: bool = False,
    depth: int = 0,
) -> dict[str, Any]:
    """Fetch slot data from the connected world's scene hierarchy.

    Args:
        slot_id: Slot ID ("Root" for the world root)
        include_component_data: Include full component members (bulkier)
        depth: 0 = only this slot, 1 = with children, -1 = entire subtree

    ## Return Format
    {"status": str, "slot_id": str, "data": {...}}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}
    try:
        resp = await client.get_slot(slot_id, include_component_data, depth)
        return {"status": "success", "slot_id": slot_id, "data": resp}
    except Exception as e:
        return {"status": "error", "slot_id": slot_id, "message": str(e)}


@server.tool()
async def resonite_link_get_node(ref_id: str) -> dict[str, Any]:
    """Get slot or component information by ID (tries slot first, then component).

    ## Return Format
    {"status": str, "ref_id": str, "node": {...}}
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
    """List direct children of a slot ("Root" for top level).

    ## Return Format
    {"status": str, "slot_id": str, "children": [...], "count": int}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}
    try:
        children = await client.get_children(slot_id)
        return {"status": "success", "slot_id": slot_id, "children": children, "count": len(children)}
    except Exception as e:
        return {"status": "error", "slot_id": slot_id, "message": str(e)}


@server.tool()
async def resonite_link_add_slot(
    name: str = "Slot",
    parent_id: str = "Root",
    pos_x: float = 0.0,
    pos_y: float = 0.0,
    pos_z: float = 0.0,
    slot_id: str = "",
) -> dict[str, Any]:
    """Create a new slot in the connected world.

    Args:
        name: Name for the new slot
        parent_id: Parent slot ID (default "Root")
        pos_x/pos_y/pos_z: Local position
        slot_id: Optional client-chosen ID (avoid the "Reso_" prefix)

    ## Return Format
    {"status": str, "parent_id": str, "slot_id": str, "name": str}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}
    try:
        new_id = await client.add_slot(
            name=name,
            parent_id=parent_id,
            position={"x": pos_x, "y": pos_y, "z": pos_z},
            slot_id=slot_id or None,
        )
        return {"status": "success", "parent_id": parent_id, "slot_id": new_id, "name": name}
    except Exception as e:
        return {"status": "error", "parent_id": parent_id, "message": str(e)}


@server.tool()
async def resonite_link_destroy_slot(slot_id: str, preserve_assets: bool = False) -> dict[str, Any]:
    """Remove a slot and its children (removeSlot).

    Note: preserve_assets is accepted for compatibility but the protocol has
    no such option; it is ignored with a warning.

    ## Return Format
    {"status": str, "slot_id": str}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}
    try:
        resp = await client.destroy_slot(slot_id, preserve_assets)
        return {"status": "success", "slot_id": slot_id, "response": resp}
    except Exception as e:
        return {"status": "error", "slot_id": slot_id, "message": str(e)}


# ── Components ─────────────────────────────────────────────────────────────────


@server.tool()
async def resonite_link_add_component(
    slot_id: str,
    component_type: str,
    members: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Attach a component to a slot, optionally initializing members.

    component_type uses Resonite syntax, e.g. "[FrooxEngine]FrooxEngine.Grabbable".
    members example: {"Scalable": true}. Use resonite_link_reflect to discover types.

    ## Return Format
    {"status": str, "slot_id": str, "component_id": str, "component_type": str}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}
    try:
        comp_id = await client.add_component(slot_id, component_type, members=members)
        return {
            "status": "success",
            "slot_id": slot_id,
            "component_id": comp_id,
            "component_type": component_type,
        }
    except Exception as e:
        return {"status": "error", "slot_id": slot_id, "message": str(e)}


@server.tool()
async def resonite_link_read_field(ref_id: str) -> dict[str, Any]:
    """Read a component's data (type + all members) by component ID.

    Note: ResoniteLink reads whole components, not individual field refs.
    Member values are in data.members, matching Resonite inspector names.

    ## Return Format
    {"status": str, "ref_id": str, "value": {...}}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}
    try:
        value = await client.get_component(ref_id)
        return {"status": "success", "ref_id": ref_id, "value": value}
    except Exception as e:
        return {"status": "error", "ref_id": ref_id, "message": str(e)}


@server.tool()
async def resonite_link_write_field(
    component_id: str,
    member: str,
    value: Any,
    value_type: str = "",
) -> dict[str, Any]:
    """Write one member on a component (updateComponent).

    Args:
        component_id: The component's ID
        member: Member name exactly as shown in the Resonite inspector
        value: The value (bool/int/float/string auto-encoded; dicts with x/y/z -> float3)
        value_type: Optional explicit protocol type ("float3", "colorX", "reference", ...)

    ## Return Format
    {"status": str, "component_id": str, "member": str}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}
    try:
        await client.set_component_value(component_id, member, value, value_type or None)
        return {"status": "success", "component_id": component_id, "member": member, "value": value}
    except Exception as e:
        return {"status": "error", "component_id": component_id, "member": member, "message": str(e)}


# ── Sync methods (0.11.0+) ─────────────────────────────────────────────────────


@server.tool()
async def resonite_link_call_method(
    target_id: str,
    method_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call a sync method on a component/object (callSyncMethod, protocol 0.11.0+).

    Args:
        target_id: ID of the object to call the method on
        method_name: Method name
        arguments: {argName: value} - primitives auto-encoded

    ## Return Format
    {"status": str, "target_id": str, "method": str, "result": {...}}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}
    try:
        result = await client.call_sync_method(target_id, method_name, arguments)
        return {"status": "success", "target_id": target_id, "method": method_name, "result": result}
    except Exception as e:
        return {"status": "error", "target_id": target_id, "method": method_name, "message": str(e)}


# ── Reflection ─────────────────────────────────────────────────────────────────


@server.tool()
async def resonite_link_reflect(component_type: str = "") -> dict[str, Any]:
    """Discover component types or member definitions.

    Without component_type: getComponentTypeList (all available types).
    With component_type: getComponentDefinition (member definitions; note that
    member types are type REFERENCES since protocol 0.9.0 - resolve them via
    the typeDefinition messages if needed).

    ## Return Format
    {"status": str, "types": {...}} or {"status": str, "component_type": str, "data": {...}}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}
    try:
        resp = await client.reflect(component_type or None)
        if component_type:
            return {"status": "success", "component_type": component_type, "data": resp}
        return {"status": "success", "types": resp}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── Batch ──────────────────────────────────────────────────────────────────────


@server.tool()
async def resonite_link_batch(operations: list[dict[str, Any]]) -> dict[str, Any]:
    """Execute multiple data-model operations atomically (dataModelOperationBatch).

    Each operation is a real protocol message with "$type", e.g.:
    - {"$type": "addSlot", "data": {"name": {"$type": "string", "value": "X"}}}
    - {"$type": "updateComponent", "data": {"id": "...", "members": {...}}}
    - {"$type": "removeSlot", "slotId": "..."}
    - {"$type": "callSyncMethod", "targetID": "...", "methodName": "...", "arguments": {}}

    ## Return Format
    {"status": str, "response": {...}}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}
    try:
        resp = await client.batch(operations)
        return {"status": "success", "response": resp}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── Asset import (wrapped 2026-07-18 from the Phase 0 spike) ───────────────────


@server.tool()
async def resonite_link_import_mesh_json(
    vertices: list[dict[str, Any]],
    submeshes: list[dict[str, Any]],
    bones: list[dict[str, Any]] | None = None,
    blendshapes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Import a mesh asset from JSON vertex/submesh data (importMeshJSON).

    Live-verified 2026-07-18. Returns an asset URL, not an entity ID - wire
    it into a StaticMesh component's URL member (type "Uri") to render it,
    or use resonite_link_spawn_mesh to do the whole chain in one call.

    vertices: [{"position": {"x","y","z"}}, ...] (each may also carry
        "normal"/"tangent"/"color"/"uvs"/"boneWeights").
    submeshes: [{"$type": "triangles", "triangles": [{"vertex0Index",
        "vertex1Index","vertex2Index"}, ...]}] (or "points"/"trianglesFlat").
    bones/blendshapes: optional, for skinned meshes - schema supports it but
        NOT live-tested yet (avatar-import spike is future work).

    ## Return Format
    {"status": str, "asset_url": str} or {"status": "error", "message": str}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}
    try:
        asset_url = await client.import_mesh_json(vertices, submeshes, bones=bones, blendshapes=blendshapes)
        return {"status": "success", "asset_url": asset_url}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@server.tool()
async def resonite_link_import_texture(file_path: str) -> dict[str, Any]:
    """Import a texture from a file path on the RESONITE HOST machine (importTexture2DFile).

    NOTE: file_path is resolved on the machine running Resonite, not the
    machine running this MCP server - matters if they differ. Wire shape is
    confirmed against the upstream C# source but has NOT been live-tested
    against a running session yet; treat results with appropriate caution
    until it has been run once for real.

    ## Return Format
    {"status": str, "asset_url": str} or {"status": "error", "message": str}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}
    try:
        asset_url = await client.import_texture_file(file_path)
        return {"status": "success", "asset_url": asset_url}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@server.tool()
async def resonite_link_spawn_mesh(
    vertices: list[dict[str, Any]],
    submeshes: list[dict[str, Any]],
    name: str = "Mesh",
    pos_x: float = 0.0,
    pos_y: float = 0.0,
    pos_z: float = 0.0,
    color_r: float | None = None,
    color_g: float | None = None,
    color_b: float | None = None,
    color_a: float = 1.0,
) -> dict[str, Any]:
    """Import a JSON mesh and wire the full render chain in one call.

    Convenience wrapper live-verified 2026-07-18 (as three separate manual
    steps that night; now one call): importMeshJSON -> addSlot -> StaticMesh
    -> MeshRenderer -> (if color given) PBS_Metallic wired into Materials.

    color_r/g/b: pass all three (0-1 floats) to also paint the mesh, e.g.
        orange = (1.0, 0.45, 0.05). Omit any one to skip material creation.

    ## Return Format
    {"status": str, "slot_id": str, "asset_url": str, "static_mesh_id": str,
     "renderer_id": str, "material_id": str (only if color given)}
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}
    color = None
    if color_r is not None and color_g is not None and color_b is not None:
        color = {"r": color_r, "g": color_g, "b": color_b, "a": color_a}
    try:
        result = await client.spawn_mesh(
            vertices,
            submeshes,
            position={"x": pos_x, "y": pos_y, "z": pos_z},
            name=name,
            color=color,
        )
        return {"status": "success", **result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── High-level helpers ─────────────────────────────────────────────────────────


@server.tool()
async def resonite_link_spawn(input_data: ResoniteLinkSpawnInput) -> dict[str, Any]:
    """Create a named, positioned slot in the world.

    NOTE: ResoniteLink has no template-URL spawning. If template_url is a
    resonite:// or file path, this returns not_implemented with guidance;
    otherwise it is used as the slot name.
    """
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected. Call resonite_link_connect first."}

    template = input_data.template_url or "Object"
    if "://" in template or template.lower().endswith((".vrm", ".glb", ".gltf", ".fbx")):
        return {
            "status": "not_implemented",
            "message": (
                "ResoniteLink (0.13.1) has no template/file spawning. Build content with "
                "resonite_link_add_slot + resonite_link_add_component, or import assets in-game."
            ),
            "template_url": template,
        }
    try:
        pos = input_data.position if isinstance(input_data.position, dict) else None
        slot_id = await client.spawn_object(name=template, position=pos)
        return {"status": "success", "action": "spawn", "slot_id": slot_id, "name": template}
    except Exception as e:
        return {"status": "error", "message": str(e), "template_url": template}


@server.tool()
async def resonite_link_set(input_data: ResoniteLinkSetInput) -> dict[str, Any]:
    """Set a member value on a Resonite component (component_id + member name)."""
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}
    try:
        await client.set_component_value(input_data.component_id, input_data.field, input_data.value)
        return {
            "status": "success",
            "component_id": input_data.component_id,
            "field": input_data.field,
            "value": input_data.value,
        }
    except Exception as e:
        return {
            "status": "error",
            "component_id": input_data.component_id,
            "field": input_data.field,
            "message": str(e),
        }


@server.tool()
async def resonite_link_get(input_data: ResoniteLinkGetInput) -> dict[str, Any]:
    """Read a member value from a Resonite component (component_id + member name)."""
    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}
    try:
        value = await client.get_component_value(input_data.component_id, input_data.field)
        return {
            "status": "success",
            "component_id": input_data.component_id,
            "field": input_data.field,
            "value": value,
        }
    except Exception as e:
        return {
            "status": "error",
            "component_id": input_data.component_id,
            "field": input_data.field,
            "message": str(e),
        }


# ── Animation ────────────────────────────────────────────────────────────────
# Backported 2026-09-02 from overte-mcp's overte_entity_animate, itself backported from
# norirobotics-mcp's Resonite wave-demo script (scripts/spawn_nori_a3.py) - same closed-form
# math, now available as a reusable tool instead of a one-off script.


def _quat_mul(a: tuple, b: tuple) -> tuple:
    """Hamilton product a*b, both (x,y,z,w) - matches ResoniteLink's floatQ convention
    (proven by test_bone_rotation.py / test_nod_head_bone.py's live head-bone rotation)."""
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    )


def _axis_angle_quat(axis: tuple, angle: float) -> tuple:
    import math

    half = angle / 2.0
    s = math.sin(half)
    return (axis[0] * s, axis[1] * s, axis[2] * s, math.cos(half))


def _bounce_height(t: float, amplitude: float, damping: float, speed: float) -> float:
    """A real bounce, not a sine wave - see overte-mcp's http_server.py for the derivation
    and numerical verification (peaks decay geometrically, settles instead of looping
    forever). t=0 starts on the ground with upward velocity, rises to `amplitude`, falls,
    and each landing's velocity *= sqrt(damping)."""
    import math

    g = 9.8 * max(speed, 0.05)
    v = math.sqrt(2 * g * amplitude) if amplitude > 0 else 0.0
    remaining = t
    while v > 1e-4:
        duration = 2 * v / g
        if remaining <= duration:
            return max(v * remaining - 0.5 * g * remaining * remaining, 0.0)
        remaining -= duration
        v *= math.sqrt(max(min(damping, 1.0), 0.0))
    return 0.0


@server.tool()
async def resonite_link_animate(
    slot_id: str,
    mode: str = "spin",
    axis_x: float = 0.0,
    axis_y: float = 1.0,
    axis_z: float = 0.0,
    speed: float = 1.0,
    amplitude: float = 0.1,
    damping: float = 0.6,
    duration_s: float = 5.0,
    tick_hz: float = 10.0,
) -> dict[str, Any]:
    """Loop-animate a slot in place: 'spin' (continuous rotation), 'bob' (smooth sinusoidal
    vertical oscillation), or 'bounce' (real drop-and-rebound physics with energy loss per
    landing, not a sine wave). Server-driven - repeated updateSlot calls over the ResoniteLink
    WebSocket, not a baked animation clip. Blocks for duration_s while it runs.

    speed: 'spin' radians/second, 'bob' oscillations/second, 'bounce' overall pace (scales
        effective gravity). amplitude: 'bob'/'bounce' peak height above rest, in meters.
        damping: 'bounce' only, energy retained per bounce (0-1).

    ## Return Format
    {"status": str, "slot_id": str, "mode": str, "ticks": int}

    ## Examples
    resonite_link_animate(slot_id="nori_left_wrist_roll_link", mode="spin", speed=1.5, duration_s=6)
    resonite_link_animate(slot_id="test_ball", mode="bounce", amplitude=0.3, damping=0.6, duration_s=6)
    """
    import asyncio
    import time

    if mode not in ("spin", "bob", "bounce"):
        return {"status": "error", "message": "mode must be 'spin', 'bob', or 'bounce'"}

    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}

    try:
        start_data = await client.get_slot(slot_id, include_component_data=False, depth=0)
        slot_data = start_data.get("data", start_data)
        rest_rot = slot_data.get("rotation", {}).get("value") or {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
        rest_rot_t = (rest_rot["x"], rest_rot["y"], rest_rot["z"], rest_rot["w"])
        rest_pos = slot_data.get("position", {}).get("value") or {"x": 0.0, "y": 0.0, "z": 0.0}
    except Exception as e:
        return {"status": "error", "message": f"Could not read slot {slot_id!r}: {e}"}

    axis = (axis_x, axis_y, axis_z)
    start = time.monotonic()
    tick_interval = 1.0 / max(tick_hz, 0.1)
    ticks = 0
    try:
        while (t := time.monotonic() - start) < duration_s:
            if mode == "spin":
                delta = _axis_angle_quat(axis, speed * t)
                x, y, z, w = _quat_mul(rest_rot_t, delta)
                update = {"id": slot_id, "rotation": {"$type": "floatQ", "value": {"x": x, "y": y, "z": z, "w": w}}}
            else:
                import math

                offset = (
                    amplitude * math.sin(2 * math.pi * speed * t)
                    if mode == "bob"
                    else _bounce_height(t, amplitude, damping, speed)
                )
                update = {
                    "id": slot_id,
                    "position": {
                        "$type": "float3",
                        "value": {"x": rest_pos["x"], "y": rest_pos["y"] + offset, "z": rest_pos["z"]},
                    },
                }
            await client.update_slot(update)
            ticks += 1
            await asyncio.sleep(tick_interval)
    except Exception as e:
        return {"status": "error", "message": f"Update failed mid-animation: {e}", "ticks": ticks}

    return {"status": "success", "slot_id": slot_id, "mode": mode, "ticks": ticks}
