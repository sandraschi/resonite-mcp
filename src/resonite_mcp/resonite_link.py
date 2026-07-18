"""
ResoniteLink Client for ResoniteMCP.

Implements the official ResoniteLink WebSocket JSON protocol as of upstream
release 0.13.1 (2026-03-11). Wire format verified against the reference C#
implementation (Yellow-Dog-Man/ResoniteLink, Message.cs / Response.cs) and
docs/docs/websocket/{slots,components}.md.

HISTORY NOTE (honesty): versions of this file before 2026-07-11 implemented a
fictional wire format (ReadField/WriteField/GetNode/Reflect/Batch with "type"
and "id" keys) that never existed upstream and could not have talked to real
Resonite. This rewrite replaces it with the real protocol.

WIRE FORMAT (real, verified):
  Outbound (client -> Resonite):
    { "$type": "<messageType>", "messageId": "<id>", ...fields }
  Inbound (Resonite -> client):
    { "$type": "<responseType>", "sourceMessageId": "<id>",
      "success": bool, "errorInfo": str|null, ...payload }

Message types ($type, camelCase):
  requestSessionData
  getSlot / addSlot / updateSlot / removeSlot
  getComponent / addComponent / updateComponent / removeComponent
  callSyncMethod / callStaticSyncMethod                       (0.11.0+)
  getComponentTypeList / getComponentDefinition /
  getTypeDefinition / getEnumDefinition / getSyncObjectDefinition /
  getGenericTypeDefinition
  dataModelOperationBatch
  importTexture2DFile / importMeshJSON / importAudioClipFile / ... (assets)

Response types: response, batchResponse, newEntityId, slotData,
  componentData, assetData, sessionData, methodResult,
  typeDefinitionData, enumDefinitionData, componentDefinitionData,
  syncObjectDefinitionData, componentTypeList

Values are typed wrappers:  {"$type": "float3", "value": {"x":0,"y":1,"z":0}}
References:                 {"$type": "reference", "targetId": "Root"}
Root slot has the special ID "Root". Resonite-allocated IDs are prefixed
"Reso_"; client-allocated IDs must avoid that prefix. IDs are NOT persistent
across world save/load.

Session discovery (0.12.0+): Resonite announces ResoniteLink sessions via UDP
broadcast on port 12512 every ~10s as JSON datagrams
{ "sessionName": str, "sessionID": str, "linkPort": int }.
Use discover_sessions() instead of assuming port 4242.

NOT available in the real protocol (do not fake): generic model/file import
(VRM/GLB/FBX). Only texture / mesh-JSON / raw-mesh / audio / cubemap imports
exist. import_file() raises with guidance.
"""

import asyncio
import json
import logging
import socket
import time
import uuid
from collections.abc import Callable
from typing import Any

import websockets
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger(__name__)

PROTOCOL_TARGET = "0.13.1"
DISCOVERY_PORT = 12512
DISCOVERY_ANNOUNCE_INTERVAL = 10.0  # upstream ANNOUNCE_INTERVAL


class ResoniteLinkError(Exception):
    """Raised when ResoniteLink returns an error response or a call is invalid."""


# ---------------------------------------------------------------------------
# Value encoding helpers
# ---------------------------------------------------------------------------


def rl_value(type_name: str, value: Any) -> dict[str, Any]:
    """Wrap a raw value in the protocol's typed-value envelope.

    Example: rl_value("float3", {"x": 0, "y": 1.5, "z": 10})
    """
    return {"$type": type_name, "value": value}


def rl_ref(target_id: str) -> dict[str, Any]:
    """Build a reference value pointing at a slot/component/member ID."""
    return {"$type": "reference", "targetId": target_id}


def rl_list(elements: list[Any]) -> dict[str, Any]:
    """Wrap a list of values in the protocol's list-member envelope.

    Verified live 2026-07-18 against MeshRenderer.Materials (a list of
    component references): elements=[rl_ref(material_id)].
    """
    return {"$type": "list", "elements": elements}


def rl_auto(value: Any) -> dict[str, Any]:
    """Best-effort encode a Python primitive into a typed value.

    bool -> bool, int -> int, float -> float, str -> string.
    dicts with x/y/z(/w) keys -> float3/float4. Already-typed dicts
    (containing "$type") pass through unchanged. Anything else raises,
    because guessing Resonite types silently is worse than failing.
    """
    if isinstance(value, dict):
        if "$type" in value:
            return value
        keys = set(value.keys())
        if keys == {"x", "y", "z"}:
            return rl_value("float3", value)
        if keys == {"x", "y", "z", "w"}:
            return rl_value("float4", value)
        raise ResoniteLinkError(
            f"Cannot auto-encode dict with keys {sorted(keys)}; wrap it with rl_value('<type>', ...)"
        )
    if isinstance(value, bool):
        return rl_value("bool", value)
    if isinstance(value, int):
        return rl_value("int", value)
    if isinstance(value, float):
        return rl_value("float", value)
    if isinstance(value, str):
        return rl_value("string", value)
    raise ResoniteLinkError(f"Cannot auto-encode value of type {type(value).__name__}; use rl_value()")


def _encode_members(members: dict[str, Any]) -> dict[str, Any]:
    """Encode a {memberName: value} dict, auto-wrapping raw primitives."""
    return {name: rl_auto(val) for name, val in members.items()}


# ---------------------------------------------------------------------------
# LAN session discovery (protocol 0.12.0+)
# ---------------------------------------------------------------------------


class _DiscoveryProtocol(asyncio.DatagramProtocol):
    def __init__(self) -> None:
        self.sessions: dict[str, dict[str, Any]] = {}

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        try:
            info = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return
        session_id = info.get("sessionID")
        if not session_id:
            return
        info["host"] = addr[0]
        info["lastSeen"] = time.time()
        self.sessions[session_id] = info


async def discover_sessions(timeout: float = 12.0) -> list[dict[str, Any]]:
    """Discover ResoniteLink sessions announced on the local network.

    Resonite broadcasts session announcements on UDP port 12512 every ~10s,
    so the default 12s window is enough to catch at least one announcement
    from every active session. Returns a list of dicts:
      {"sessionName": str, "sessionID": str, "linkPort": int, "host": str}
    """
    loop = asyncio.get_running_loop()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", DISCOVERY_PORT))
    sock.setblocking(False)
    transport, protocol = await loop.create_datagram_endpoint(_DiscoveryProtocol, sock=sock)
    try:
        await asyncio.sleep(timeout)
    finally:
        transport.close()
    return list(protocol.sessions.values())


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class ResoniteLinkClient:
    """
    Client for the official ResoniteLink WebSocket protocol (target 0.13.1).

    Enable ResoniteLink in Resonite (host only):
      - Graphical client: Dashboard -> Session -> Settings -> Enable ResoniteLink
      - Headless config: "enableResoniteLink": true (optional "forceResoniteLinkPort")
      - Headless console: enableResoniteLink <port>   (0 = random)

    Prefer discover_sessions() over assuming a port; the port shown in the
    Resonite UI (or announced via UDP 12512) is authoritative.
    """

    DEFAULT_PORT = 4242
    RESPONSE_TIMEOUT = 10.0  # seconds

    def __init__(self, host: str = "localhost", port: int = DEFAULT_PORT) -> None:
        self.host = host
        self.port = port
        self.uri = f"ws://{host}:{port}"
        self.ws: Any = None
        self.running = False
        self._listen_task: asyncio.Task[None] | None = None
        self._pending: dict[str, asyncio.Future[dict[str, Any]]] = {}
        self._callbacks: dict[str, Callable[[dict[str, Any]], Any]] = {}
        # sessionData response (resoniteVersion, resoniteLinkVersion, uniqueSessionId)
        self.session_info: dict[str, Any] = {}

    # -- Connection management ------------------------------------------------

    async def connect(self) -> bool:
        """Connect to ResoniteLink and fetch session data."""
        try:
            self.ws = await websockets.connect(self.uri, ping_interval=20, ping_timeout=10)
            self.running = True
            self._listen_task = asyncio.create_task(self._listen())
            logger.info("Connected to ResoniteLink at %s", self.uri)
            try:
                self.session_info = await self.request_session_data()
                logger.info(
                    "ResoniteLink session: Resonite %s, protocol %s",
                    self.session_info.get("resoniteVersion"),
                    self.session_info.get("resoniteLinkVersion"),
                )
            except ResoniteLinkError as exc:
                logger.warning("Connected, but requestSessionData failed: %s", exc)
            return True
        except Exception as exc:
            logger.error("ResoniteLink connection failed: %s", exc)
            self.running = False
            return False

    async def disconnect(self) -> None:
        """Gracefully disconnect."""
        self.running = False
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        if self.ws:
            await self.ws.close()
        logger.info("Disconnected from ResoniteLink")

    @property
    def connected(self) -> bool:
        return self.running and self.ws is not None

    # -- Low-level send / receive ----------------------------------------------

    async def _send(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Send a message and await the response correlated by messageId.

        Raises ResoniteLinkError on failed responses (success=false) or timeout.
        Legacy note: payloads using the pre-2026-07 fictional {"type": ..., "id": ...}
        shape are rejected with guidance instead of being sent.
        """
        if not self.connected:
            raise ResoniteLinkError("Not connected to ResoniteLink")
        if "$type" not in payload:
            legacy = payload.get("type")
            raise ResoniteLinkError(
                "Message is missing '$type'. "
                + (
                    f"'{legacy}' looks like the pre-0.13 fictional format; "
                    "see resonite_link.py docstring for the real message types."
                    if legacy
                    else "Use the real ResoniteLink message types (e.g. 'getSlot')."
                )
            )

        msg_id = payload.setdefault("messageId", str(uuid.uuid4()))
        loop = asyncio.get_running_loop()
        fut: asyncio.Future[dict[str, Any]] = loop.create_future()
        self._pending[msg_id] = fut

        try:
            await self.ws.send(json.dumps(payload))
            response = await asyncio.wait_for(fut, timeout=self.RESPONSE_TIMEOUT)
        except TimeoutError:
            raise ResoniteLinkError(
                f"Timeout waiting for response to messageId={msg_id} ($type={payload.get('$type')})"
            ) from None
        finally:
            self._pending.pop(msg_id, None)

        if response.get("success") is False:
            raise ResoniteLinkError(response.get("errorInfo") or "Unknown ResoniteLink error")
        return response

    async def _listen(self) -> None:
        """Background task: dispatch inbound messages."""
        while self.running and self.ws:
            try:
                raw = await self.ws.recv()
                data = json.loads(raw)

                source_id = data.get("sourceMessageId")
                if source_id and source_id in self._pending:
                    fut = self._pending[source_id]
                    if not fut.done():
                        fut.set_result(data)
                    continue

                # Unsolicited messages: dispatch by $type
                msg_type = data.get("$type", "")
                cb = self._callbacks.get(msg_type)
                if cb is not None:
                    try:
                        result = cb(data)
                        if asyncio.iscoroutine(result):
                            await result
                    except Exception as exc:
                        logger.error("Callback error for %s: %s", msg_type, exc)
                else:
                    logger.debug("Unhandled ResoniteLink message: %s", msg_type)

            except ConnectionClosed:
                logger.warning("ResoniteLink connection closed remotely")
                self.running = False
                break
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("ResoniteLink listener error: %s", exc)

    def on(self, msg_type: str, callback: Callable[[dict[str, Any]], Any]) -> None:
        """Register a callback for unsolicited message $types."""
        self._callbacks[msg_type] = callback

    # -- Session ---------------------------------------------------------------

    async def request_session_data(self) -> dict[str, Any]:
        """Request session metadata (Resonite version, protocol version, session id)."""
        return await self._send({"$type": "requestSessionData"})

    async def get_session_info(self) -> dict[str, Any]:
        """Return cached session info (populated on connect)."""
        return self.session_info

    # -- Slots -------------------------------------------------------------------

    async def get_slot(
        self,
        slot_id: str = "Root",
        include_component_data: bool = False,
        depth: int = 0,
    ) -> dict[str, Any]:
        """Fetch slot data. depth=0 only this slot, -1 the full subtree."""
        return await self._send(
            {
                "$type": "getSlot",
                "slotId": slot_id,
                "includeComponentData": include_component_data,
                "depth": depth,
            }
        )

    async def add_slot(
        self,
        name: str = "Slot",
        parent_id: str | None = None,
        position: dict[str, float] | None = None,
        rotation: dict[str, float] | None = None,
        scale: dict[str, float] | None = None,
        slot_id: str | None = None,
        extra_data: dict[str, Any] | None = None,
    ) -> str:
        """Create a slot. Returns its ID (client-supplied or Resonite-allocated)."""
        data: dict[str, Any] = dict(extra_data or {})
        data["name"] = rl_value("string", name)
        if slot_id:
            data["id"] = slot_id
        if parent_id:
            data["parent"] = rl_ref(parent_id)
        if position:
            data["position"] = rl_value("float3", position)
        if rotation:
            data["rotation"] = rl_value("floatQ", rotation)
        if scale:
            data["scale"] = rl_value("float3", scale)
        resp = await self._send({"$type": "addSlot", "data": data})
        return str(slot_id or resp.get("entityId") or "")

    async def update_slot(self, data: dict[str, Any]) -> dict[str, Any]:
        """Update a slot. data MUST contain 'id'; include only fields to change."""
        if "id" not in data:
            raise ResoniteLinkError("update_slot: data['id'] is mandatory")
        return await self._send({"$type": "updateSlot", "data": data})

    async def remove_slot(self, slot_id: str) -> dict[str, Any]:
        """Remove a slot (and its children)."""
        return await self._send({"$type": "removeSlot", "slotId": slot_id})

    # -- Components ---------------------------------------------------------------

    async def get_component(self, component_id: str) -> dict[str, Any]:
        """Fetch component data (type + members) by component ID."""
        return await self._send({"$type": "getComponent", "componentId": component_id})

    async def add_component(
        self,
        container_slot_id: str,
        component_type: str,
        members: dict[str, Any] | None = None,
        component_id: str | None = None,
    ) -> str:
        """Attach a component to a slot. Returns the component ID.

        component_type uses Resonite syntax, e.g. "[FrooxEngine]FrooxEngine.Grabbable".
        members values are auto-encoded ({"Scalable": True} -> bool wrapper);
        pass rl_value(...)/rl_ref(...) wrappers for anything non-primitive.
        """
        data: dict[str, Any] = {"componentType": component_type}
        if component_id:
            data["id"] = component_id
        if members:
            data["members"] = _encode_members(members)
        resp = await self._send(
            {"$type": "addComponent", "containerSlotId": container_slot_id, "data": data}
        )
        return str(component_id or resp.get("entityId") or "")

    async def update_component(self, component_id: str, members: dict[str, Any]) -> dict[str, Any]:
        """Update members on an existing component."""
        return await self._send(
            {
                "$type": "updateComponent",
                "data": {"id": component_id, "members": _encode_members(members)},
            }
        )

    async def remove_component(self, component_id: str) -> dict[str, Any]:
        """Remove a component by ID."""
        return await self._send({"$type": "removeComponent", "componentId": component_id})

    # -- Sync methods (protocol 0.11.0+) -----------------------------------------

    async def call_sync_method(
        self,
        target_id: str,
        method_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call a sync method on a component/object. Returns the methodResult response."""
        return await self._send(
            {
                "$type": "callSyncMethod",
                "targetID": target_id,
                "methodName": method_name,
                "arguments": _encode_members(arguments or {}),
            }
        )

    async def call_static_sync_method(
        self,
        target_type: str,
        method_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call a static sync method on a type."""
        return await self._send(
            {
                "$type": "callStaticSyncMethod",
                "targetType": target_type,
                "methodName": method_name,
                "arguments": _encode_members(arguments or {}),
            }
        )

    # -- Reflection -----------------------------------------------------------------

    async def get_component_type_list(self, category_path: str | None = None) -> dict[str, Any]:
        """List available component types (optionally within a category path)."""
        payload: dict[str, Any] = {"$type": "getComponentTypeList"}
        if category_path:
            payload["categoryPath"] = category_path
        return await self._send(payload)

    async def get_component_definition(
        self, component_type: str, flattened: bool = True
    ) -> dict[str, Any]:
        """Get member definitions for a component type.

        Note (0.9.0 breaking change upstream): member definitions reference
        types by type-reference, not inline definitions. Resolve referenced
        types via get_type_definition() when needed.
        """
        return await self._send(
            {
                "$type": "getComponentDefinition",
                "componentType": component_type,
                "flattened": flattened,
            }
        )

    async def get_type_definition(self, type_name: str) -> dict[str, Any]:
        """Get the definition of a data type."""
        return await self._send({"$type": "getTypeDefinition", "type": type_name})

    async def get_enum_definition(self, type_name: str) -> dict[str, Any]:
        """Get the values of an enum type."""
        return await self._send({"$type": "getEnumDefinition", "type": type_name})

    # -- Batching -----------------------------------------------------------------

    async def batch(self, operations: list[dict[str, Any]]) -> dict[str, Any]:
        """Execute multiple data-model operations without engine updates in between.

        Each operation must be a real message dict with its own "$type"
        (data-model operations only: slot/component CRUD, sync method calls).
        Returns the batchResponse (per-operation results included).
        """
        for op in operations:
            if "$type" not in op:
                raise ResoniteLinkError(
                    f"batch: every operation needs '$type' (got keys {sorted(op.keys())})"
                )
        return await self._send({"$type": "dataModelOperationBatch", "operations": operations})

    # -- Asset import (mesh / texture) -----------------------------------------------
    # Wrapped 2026-07-18 from the raw _send() calls used in the Phase 0 spike
    # (see mcp-central-docs/projects/RESONITE_PHASE0_HANDOFF.md). importMeshJSON
    # and the render-chain shapes (StaticMesh/MeshRenderer/PBS_Metallic/Materials
    # list) are live-verified against a running session. import_texture_file's
    # wire shape is confirmed against the upstream C# source
    # (Models/Assets/Texture2D/ImportTexture2DFile.cs — a plain one-field
    # message, no binary payload) but has NOT been live-tested; treat it as
    # "shape correct, unproven" until run once against a real session.

    async def import_mesh_json(
        self,
        vertices: list[dict[str, Any]],
        submeshes: list[dict[str, Any]],
        bones: list[dict[str, Any]] | None = None,
        blendshapes: list[dict[str, Any]] | None = None,
    ) -> str:
        """Import a mesh asset from JSON-described vertex/submesh data.

        Live-verified 2026-07-18 (hand-built unit cube, 8 vertices / 12
        triangles). Recommended only for smaller meshes per upstream docs
        (ImportMeshJSON.cs) — for large meshes, ImportMeshRawData is more
        efficient but requires a binary WebSocket payload the client does not
        yet send; see import_mesh_raw().

        vertices: list of {"position": {"x","y","z"}}, each optionally also
            carrying "normal"/"tangent"/"color"/"uvs"/"boneWeights".
        submeshes: list of {"$type": "triangles"|"points"|"trianglesFlat",
            "triangles": [{"vertex0Index","vertex1Index","vertex2Index"}, ...]}
            (or "points": [...] for the points variant).
        bones / blendshapes: optional, for skinned/avatar-style meshes. The
            schema supports both (per ImportMeshJSON.cs) but this path has
            NOT been live-tested — treat as unproven until run once.

        Returns the imported asset's URL (e.g. "local://.../xyz.meshx"),
        NOT an entity/component ID. Wire it into a StaticMesh component's
        URL member (typed "Uri") to render it — see spawn_mesh() for the
        full chain, or do it manually:
            static_mesh_id = await client.add_component(slot_id,
                "[FrooxEngine]FrooxEngine.StaticMesh",
                {"URL": rl_value("Uri", asset_url)})
        """
        payload: dict[str, Any] = {
            "$type": "importMeshJSON",
            "vertices": vertices,
            "submeshes": submeshes,
        }
        if bones is not None:
            payload["bones"] = bones
        if blendshapes is not None:
            payload["blendshapes"] = blendshapes
        resp = await self._send(payload)
        asset_url = resp.get("assetURL")
        if not asset_url:
            raise ResoniteLinkError(f"importMeshJSON succeeded but no assetURL in response: {resp}")
        return str(asset_url)

    async def import_mesh_raw(self, *args: Any, **kwargs: Any) -> str:
        """NOT IMPLEMENTED: ImportMeshRawData needs a binary payload frame.

        Per upstream (ImportMeshRawData.cs / BinaryPayloadMessage.cs), this
        message type carries its vertex/normal/tangent/color/UV/bone-weight
        buffers as a SEPARATE binary WebSocket frame sent immediately after
        the JSON metadata frame, with buffer offsets computed the same way
        FrooxEngine computes them server-side. This client's _send() only
        ever sends JSON text frames; adding binary-frame support plus a
        Python buffer packer (struct/numpy, mirroring ComputeBufferOffsets)
        is real work that has not been done or tested. Do not fake it.

        Use import_mesh_json() instead (verified, JSON-only, works fine for
        the mesh sizes this project needs so far). Revisit this only if a
        generated-home mesh is large enough that JSON overhead actually
        matters (unlikely before Phase 2's decimation budget of ~150k tris
        is hit repeatedly).
        """
        raise ResoniteLinkError(
            "import_mesh_raw is not implemented: ImportMeshRawData requires a "
            "binary WebSocket payload frame (see ImportMeshRawData.cs upstream) "
            "that this client does not send. Use import_mesh_json() instead."
        )

    async def import_texture_file(self, file_path: str) -> str:
        """Import a texture asset from a file path on the RESONITE HOST machine
        (not the machine running this client — matters if they differ).

        Wire shape confirmed against upstream ImportTexture2DFile.cs (single
        "filePath" field, plain Message, no binary payload) but NOT yet
        live-tested against a running session. Run once and update this
        docstring (and RESONITELINK_GUIDE.md's capability table) before
        relying on it for real asset pipelines.
        """
        resp = await self._send({"$type": "importTexture2DFile", "filePath": file_path})
        asset_url = resp.get("assetURL")
        if not asset_url:
            raise ResoniteLinkError(f"importTexture2DFile succeeded but no assetURL in response: {resp}")
        return str(asset_url)

    async def spawn_mesh(
        self,
        vertices: list[dict[str, Any]],
        submeshes: list[dict[str, Any]],
        position: dict[str, float] | None = None,
        name: str = "Mesh",
        color: dict[str, float] | None = None,
    ) -> dict[str, str]:
        """Convenience: import a JSON mesh and wire the full render chain.

        Does in one call what the Phase 0 spike did as three separate
        scripts (phase0_mesh_test.py + phase0_mesh_render.py +
        phase0_material.py, 2026-07-18) — every step below is individually
        live-verified; this is a straight composition, not new behaviour:
          1. importMeshJSON -> assetURL
          2. addSlot at `position`, named `name`
          3. StaticMesh(URL: Uri = assetURL) on that slot
          4. MeshRenderer(Mesh: reference = static mesh component)
          5. if `color` given: PBS_Metallic(AlbedoColor: colorX = color),
             wired into MeshRenderer.Materials via the list-member encoding

        color: {"r","g","b","a"} 0-1 floats, e.g. orange =
            {"r": 1.0, "g": 0.45, "b": 0.05, "a": 1.0}.

        Returns {"slot_id", "asset_url", "static_mesh_id", "renderer_id"}
        plus "material_id" if `color` was given.
        """
        asset_url = await self.import_mesh_json(vertices, submeshes)
        slot_id = await self.add_slot(name=name, position=position)
        static_mesh_id = await self.add_component(
            slot_id, "[FrooxEngine]FrooxEngine.StaticMesh", {"URL": rl_value("Uri", asset_url)}
        )
        renderer_id = await self.add_component(
            slot_id, "[FrooxEngine]FrooxEngine.MeshRenderer", {"Mesh": rl_ref(static_mesh_id)}
        )
        result = {
            "slot_id": slot_id,
            "asset_url": asset_url,
            "static_mesh_id": static_mesh_id,
            "renderer_id": renderer_id,
        }
        if color is not None:
            material_id = await self.add_component(
                slot_id,
                "[FrooxEngine]FrooxEngine.PBS_Metallic",
                {"AlbedoColor": rl_value("colorX", color)},
            )
            await self.update_component(renderer_id, {"Materials": rl_list([rl_ref(material_id)])})
            result["material_id"] = material_id
        return result

    # -- Legacy compatibility surface (pre-2026-07 fictional API) -------------------
    # These keep old call sites working by mapping onto real protocol messages.
    # New code should use the canonical methods above.

    async def get_node(self, ref_id: str) -> dict[str, Any]:
        """Legacy: fetch a slot (with component data); falls back to component lookup."""
        try:
            return await self.get_slot(ref_id, include_component_data=True, depth=0)
        except ResoniteLinkError:
            return await self.get_component(ref_id)

    async def get_children(self, slot_id: str) -> list[dict[str, Any]]:
        """Legacy: list direct children of a slot via getSlot(depth=1)."""
        resp = await self.get_slot(slot_id, include_component_data=False, depth=1)
        data = resp.get("data") or {}
        children = data.get("children") or resp.get("children") or []
        return list(children)

    async def destroy_slot(self, slot_id: str, preserve_assets: bool = False) -> dict[str, Any]:
        """Legacy: removeSlot. preserve_assets does not exist in the protocol."""
        if preserve_assets:
            logger.warning("destroy_slot: preserve_assets is not supported by ResoniteLink; ignoring")
        return await self.remove_slot(slot_id)

    async def reflect(self, component_type: str | None = None) -> dict[str, Any]:
        """Legacy: component type list, or member definitions for one type."""
        if component_type:
            return await self.get_component_definition(component_type)
        return await self.get_component_type_list()

    async def read_field(self, ref_id: str) -> Any:
        """Legacy: the protocol has no per-field reads. Returns the component's
        full data (members included) for the given component ID."""
        return await self.get_component(ref_id)

    async def write_field(self, ref_id: str, value: Any, value_type: str | None = None) -> dict[str, Any]:
        """Legacy: not representable. The protocol writes component MEMBERS, not
        bare field refs. Raises with guidance."""
        raise ResoniteLinkError(
            "writeField does not exist in ResoniteLink. Use "
            "update_component(component_id, members={'MemberName': value}) or "
            "set_component_value(component_id, field, value)."
        )

    async def set_component_value(
        self, component_id: str, field: str, value: Any, value_type: str | None = None
    ) -> dict[str, Any]:
        """Set a single member on a component (updateComponent)."""
        encoded = rl_value(value_type, value) if value_type else rl_auto(value)
        return await self.update_component(component_id, {field: encoded})

    async def get_component_value(self, component_id: str, field: str | None = None) -> Any:
        """Read a component; if field given, return just that member's value."""
        resp = await self.get_component(component_id)
        if not field:
            return resp
        members = (resp.get("data") or {}).get("members") or resp.get("members") or {}
        member = members.get(field)
        if member is None:
            raise ResoniteLinkError(f"Component {component_id} has no member '{field}'")
        return member.get("value", member) if isinstance(member, dict) else member

    async def spawn_object(
        self,
        name: str = "Object",
        position: dict[str, float] | None = None,
        parent_id: str | None = None,
    ) -> str:
        """Legacy: create a named (optionally positioned) slot. Returns its ID.

        Template-URL spawning does not exist in ResoniteLink; build content
        with add_slot/add_component or import assets via the asset messages.
        """
        return await self.add_slot(name=name, parent_id=parent_id, position=position)

    async def import_audio_clip_file(self, file_path: str) -> str:
        """Import an audio asset from a file path on the RESONITE HOST machine
        (not the machine running this client — matters if they differ).

        Wire shape assumed by analogy with import_texture_file()/
        ImportTexture2DFile.cs (both are plain single-field file-import
        messages per the docstring's message-type list) — NOT yet
        confirmed against ImportAudioClipFile.cs upstream source, and not
        live-tested until this session. Update this docstring once proven.
        """
        resp = await self._send({"$type": "importAudioClipFile", "filePath": file_path})
        asset_url = resp.get("assetURL")
        if not asset_url:
            raise ResoniteLinkError(f"importAudioClipFile succeeded but no assetURL in response: {resp}")
        return str(asset_url)

    async def spawn_audio(
        self,
        file_path: str,
        position: dict[str, float] | None = None,
        name: str = "Audio",
        slot_id: str | None = None,
        loop: bool = False,
        volume: float = 1.0,
        spatialize: bool = True,
    ) -> dict[str, str]:
        """Convenience: import an audio file and wire the full playback chain.

        Mirrors spawn_mesh()'s composition pattern:
          1. importAudioClipFile -> assetURL
          2. addSlot at `position` (or reuse `slot_id` if given, e.g. to
             attach speech to an existing avatar slot like Nekomimi-chan's)
          3. StaticAudioClip(URL: Uri = assetURL) on that slot
          4. AudioClipPlayer(Clip: reference = static clip component)
          5. AudioOutput(Source: reference = the AudioClipPlayer,
             Spatialize, Volume) so it's actually audible, positionally

        Component member names confirmed live 2026-07-18 (not guessed —
        learned from the earlier UV_Coordinate lesson: reflection first,
        not brute-force guessing): AudioClipPlayer.Clip is a reference to
        IAssetProvider<AudioClip>; AudioClipPlayer.playback is a nested
        SyncPlayback/IPlayable object with sub-fields {"play", "loop",
        "position", "speed"} — read back live via getComponent() before
        being used here, not assumed. Playback is triggered automatically
        by this method (play=True). Wiring itself is proven (spawn +
        trigger both return success with no errors); **actual audibility
        still needs a human to confirm** — no automated way to verify
        sound reaches a listener's ears from here.

        Returns {"slot_id", "asset_url", "clip_id", "player_id", "output_id"}.
        """
        asset_url = await self.import_audio_clip_file(file_path)
        if slot_id is None:
            slot_id = await self.add_slot(name=name, position=position)
        clip_id = await self.add_component(
            slot_id, "[FrooxEngine]FrooxEngine.StaticAudioClip", {"URL": rl_value("Uri", asset_url)}
        )
        player_id = await self.add_component(
            slot_id, "[FrooxEngine]FrooxEngine.AudioClipPlayer", {"Clip": rl_ref(clip_id)}
        )
        output_id = await self.add_component(
            slot_id,
            "[FrooxEngine]FrooxEngine.AudioOutput",
            {"Source": rl_ref(player_id), "Volume": volume, "Spatialize": spatialize},
        )
        # Trigger playback. "playback" is a nested SyncPlayback/IPlayable
        # object, not a plain bool — live-confirmed shape 2026-07-18:
        # {"play": bool, "loop": bool, "position": float, "speed": float}.
        await self.update_component(
            player_id,
            {"playback": rl_value("playback", {"play": True, "loop": loop, "position": 0.0, "speed": 1.0})},
        )
        return {
            "slot_id": slot_id,
            "asset_url": asset_url,
            "clip_id": clip_id,
            "player_id": player_id,
            "output_id": output_id,
        }

    async def import_file(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """NOT IMPLEMENTED upstream: ResoniteLink has no generic file import.

        Only importTexture2DFile / importMeshJSON / importMeshRawData /
        importAudioClipFile / cubemap variants exist. VRM/GLB model import via
        ResoniteLink is not currently possible; use in-game import or the OSC
        pipeline instead.
        """
        raise ResoniteLinkError(
            "importFile does not exist in ResoniteLink (verified against 0.13.1). "
            "Generic model import (VRM/GLB/FBX) is not supported by the protocol; "
            "only texture/mesh-JSON/audio imports exist."
        )
