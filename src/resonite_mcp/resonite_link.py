"""
ResoniteLink Client for ResoniteMCP.

Implements the official ResoniteLink WebSocket JSON protocol (v0.8.3, Feb 2026).
Protocol reference: https://github.com/Yellow-Dog-Man/ResoniteLink

MESSAGE FORMAT (official spec):
  Outbound (client → Resonite):
    { "type": "<MessageType>", "id": "<msg-id>", ...fields }

  Inbound (Resonite → client):
    { "type": "<ResponseType>", "id": "<msg-id>", ...fields }

Key message types:
  ReadField    - read a field value by ref ID
  WriteField   - write a value to a field by ref ID
  AddSlot      - add a child slot, returns new slot ID
  AddComponent - add component to slot, returns component ID
  DestroySlot  - destroy a slot and its children
  GetNode      - get slot/component info by ref ID
  GetChildren  - list children of a slot
  Reflect      - enumerate supported components/members (v0.8.3+)
  Batch        - batch multiple operations atomically (v0.8.3+)

TODO: If Resonite publishes a local REST/HTTP API, update _call_resonite_rest()
      below and flip USE_REST_API = True. Endpoint base likely http://localhost:PORT.
      Remove this TODO when REST API details are confirmed.
"""

import asyncio
import json
import logging
import uuid
from typing import Any, Callable, Dict, List, Optional

import websockets
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger(__name__)

# Set True and fill REST_BASE_URL when official REST API is confirmed
USE_REST_API = False
REST_BASE_URL = "http://localhost:4242"  # placeholder


class ResoniteLinkError(Exception):
    """Raised when ResoniteLink returns an error response."""


class ResoniteLinkClient:
    """
    Client for the official ResoniteLink WebSocket protocol (0.8.x).

    Enable ResoniteLink in Resonite:
      - Graphical client: Sessions → Enable ResoniteLink
      - Headless config: add "enableResoniteLink": true
      - Default port: 4242 (configurable via forceResoniteLinkPort)

    Port note: some third-party tools use port 29551 — this client
    defaults to the official 4242.
    """

    DEFAULT_PORT = 4242
    RESPONSE_TIMEOUT = 10.0  # seconds

    def __init__(self, host: str = "localhost", port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.uri = f"ws://{host}:{port}"
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        self._listen_task: Optional[asyncio.Task] = None
        # Pending requests: msg_id → asyncio.Future
        self._pending: Dict[str, asyncio.Future] = {}
        # Event callbacks by type
        self._callbacks: Dict[str, Callable] = {}
        # Session metadata received on connect
        self.session_info: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    async def connect(self) -> bool:
        """Connect to ResoniteLink and await session handshake."""
        try:
            self.ws = await websockets.connect(self.uri, ping_interval=20, ping_timeout=10)
            self.running = True
            self._listen_task = asyncio.create_task(self._listen())
            logger.info("Connected to ResoniteLink at %s", self.uri)

            # ResoniteLink sends a SessionData message on connect (v0.8+)
            # Give it a moment to arrive
            await asyncio.sleep(0.2)
            return True
        except Exception as exc:
            logger.error("ResoniteLink connection failed: %s", exc)
            self.running = False
            return False

    async def disconnect(self):
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

    # ------------------------------------------------------------------
    # Low-level send / receive
    # ------------------------------------------------------------------

    async def _send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message and await the correlated response by id.
        Raises ResoniteLinkError on error responses or timeout.
        """
        if not self.connected:
            raise ResoniteLinkError("Not connected to ResoniteLink")

        msg_id = payload.setdefault("id", str(uuid.uuid4()))
        loop = asyncio.get_event_loop()
        fut: asyncio.Future = loop.create_future()
        self._pending[msg_id] = fut

        try:
            await self.ws.send(json.dumps(payload))
            response = await asyncio.wait_for(fut, timeout=self.RESPONSE_TIMEOUT)
        except asyncio.TimeoutError:
            self._pending.pop(msg_id, None)
            raise ResoniteLinkError(f"Timeout waiting for response to id={msg_id}")
        finally:
            self._pending.pop(msg_id, None)

        if response.get("type") == "Error":
            raise ResoniteLinkError(response.get("message", "Unknown ResoniteLink error"))

        return response

    async def _send_no_wait(self, payload: Dict[str, Any]) -> bool:
        """Fire-and-forget send (for commands with no expected response)."""
        if not self.connected:
            return False
        try:
            await self.ws.send(json.dumps(payload))
            return True
        except Exception as exc:
            logger.error("ResoniteLink send failed: %s", exc)
            return False

    async def _listen(self):
        """Background task: dispatch inbound messages."""
        while self.running and self.ws:
            try:
                raw = await self.ws.recv()
                data = json.loads(raw)
                msg_id = data.get("id")

                # Resolve pending futures
                if msg_id and msg_id in self._pending:
                    fut = self._pending[msg_id]
                    if not fut.done():
                        fut.set_result(data)
                    continue

                # Handle unsolicited messages (SessionData, updates, etc.)
                msg_type = data.get("type", "")
                if msg_type == "SessionData":
                    self.session_info = data
                    logger.info("ResoniteLink session: %s", data)

                if msg_type in self._callbacks:
                    cb = self._callbacks[msg_type]
                    try:
                        if asyncio.iscoroutinefunction(cb):
                            await cb(data)
                        else:
                            cb(data)
                    except Exception as exc:
                        logger.error("Callback error for %s: %s", msg_type, exc)

            except ConnectionClosed:
                logger.warning("ResoniteLink connection closed remotely")
                self.running = False
                break
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("ResoniteLink listener error: %s", exc)

    def on(self, msg_type: str, callback: Callable):
        """Register a callback for unsolicited message types."""
        self._callbacks[msg_type] = callback

    # ------------------------------------------------------------------
    # Data Model API  (official ResoniteLink 0.8.x messages)
    # ------------------------------------------------------------------

    async def get_session_info(self) -> Dict[str, Any]:
        """Return cached session info (populated on connect)."""
        return self.session_info

    async def read_field(self, ref_id: str) -> Any:
        """Read a field value by its ref ID."""
        resp = await self._send({"type": "ReadField", "refId": ref_id})
        return resp.get("value")

    async def write_field(self, ref_id: str, value: Any, value_type: str = None) -> Dict[str, Any]:
        """
        Write a value to a field by its ref ID.

        value_type: optional C# type string e.g. "System.Single", "UnityEngine.Color"
        """
        payload: Dict[str, Any] = {"type": "WriteField", "refId": ref_id, "value": value}
        if value_type:
            payload["valueType"] = value_type
        return await self._send(payload)

    async def get_node(self, ref_id: str) -> Dict[str, Any]:
        """Get node (slot/component) info by ref ID."""
        return await self._send({"type": "GetNode", "refId": ref_id})

    async def get_children(self, slot_id: str) -> List[Dict[str, Any]]:
        """List direct children of a slot."""
        resp = await self._send({"type": "GetChildren", "refId": slot_id})
        return resp.get("children", [])

    async def add_slot(self, parent_id: str, name: str = "Slot") -> str:
        """
        Add a child slot under parent_id.
        Returns the ref ID of the new slot.
        """
        resp = await self._send({"type": "AddSlot", "refId": parent_id, "name": name})
        return resp.get("refId", "")

    async def add_component(self, slot_id: str, component_type: str) -> str:
        """
        Add a component to a slot.
        Returns the ref ID of the new component.
        component_type: fully qualified C# type e.g. "FrooxEngine.AudioStreamController"
        """
        resp = await self._send({"type": "AddComponent", "refId": slot_id, "componentType": component_type})
        return resp.get("refId", "")

    async def destroy_slot(self, slot_id: str, preserve_assets: bool = False) -> Dict[str, Any]:
        """Destroy a slot and its children."""
        return await self._send({
            "type": "DestroySlot",
            "refId": slot_id,
            "preserveAssets": preserve_assets
        })

    async def reflect(self, component_type: str = None) -> Dict[str, Any]:
        """
        Reflection API (v0.8.3+).
        If component_type given, returns members for that type.
        If None, returns list of all supported types.
        """
        payload: Dict[str, Any] = {"type": "Reflect"}
        if component_type:
            payload["componentType"] = component_type
        return await self._send(payload)

    async def batch(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Batch multiple operations atomically (v0.8.3+).
        Each operation is a normal message dict (without top-level id).
        Returns list of per-operation responses.
        """
        resp = await self._send({"type": "Batch", "operations": operations})
        return resp.get("results", [])

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    async def spawn_object(self, parent_id: str, name: str = "Object") -> str:
        """Create a named slot under parent. Returns new slot ref ID."""
        return await self.add_slot(parent_id, name)

    async def teleport_avatar(self, position: Dict[str, float]) -> Dict[str, Any]:
        """
        Teleport via DynamicVariableSpace or similar.

        In practice, teleport is best done through a ProtoFlux logix node
        exposed as a DynamicVariable<float3> in the world.
        This writes to that variable if you know its ref ID.
        See ProtoFlux setup guide in the webapp /protoflux page.
        """
        # User must provide ref_id of the teleport target position field
        # This is a placeholder — wire up the actual ref ID from your world
        logger.warning(
            "teleport_avatar: provide the ref_id of your ProtoFlux position variable. "
            "See /protoflux setup guide in the webapp."
        )
        return {"status": "not_configured", "hint": "Set up ProtoFlux teleport node in world"}

    async def set_component_value(self, ref_id: str, field: str, value: Any) -> Dict[str, Any]:
        """
        Legacy helper: write_field by ref_id.
        Note: In ResoniteLink 0.8.x, field access requires knowing the field's
        own refId, not (component_id + field_name). Use reflect() to discover refIds.
        """
        return await self.write_field(ref_id, value)

    async def get_component_value(self, ref_id: str, field: str = None) -> Any:
        """Legacy helper: read_field by ref_id."""
        return await self.read_field(ref_id)
