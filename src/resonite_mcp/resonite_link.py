"""
ResoniteLink Client for ResoniteMCP.
Implements the new WebSocket JSON protocol for real-time 3D interaction.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable
import websockets

logger = logging.getLogger(__name__)


class ResoniteLinkClient:
    """
    Client for ResoniteLink protocol (Beta 2026).
    Enables reading and writing of world data model elements via WebSockets.
    """

    def __init__(self, host: str = "localhost", port: int = 4242):
        self.uri = f"ws://{host}:{port}"
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.logger = logging.getLogger("resonite_mcp.link")
        self.callbacks: Dict[str, Callable] = {}
        self.running = False
        self._listen_task: Optional[asyncio.Task] = None

    async def connect(self):
        """Connect to the ResoniteLink host."""
        try:
            self.ws = await websockets.connect(self.uri)
            self.running = True
            self._listen_task = asyncio.create_task(self._listen())
            self.logger.info(f"Connected to ResoniteLink at {self.uri}")
            return True
        except Exception as e:
            self.logger.error(f"ResoniteLink Connection Failed: {e}")
            return False

    async def disconnect(self):
        """Disconnect from ResoniteLink."""
        self.running = False
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        if self.ws:
            await self.ws.close()
            self.logger.info("Disconnected from ResoniteLink")

    async def send_command(self, action: str, payload: Dict[str, Any]):
        """Send a JSON command over ResoniteLink."""
        if not self.ws or not self.running:
            self.logger.warning("ResoniteLink not connected. Cannot send command.")
            return False

        message = {"type": "command", "action": action, "data": payload}
        await self.ws.send(json.dumps(message))
        return True

    async def _listen(self):
        """Listen for incoming JSON updates from Resonite."""
        while self.running and self.ws:
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                self.logger.debug(f"Received from ResoniteLink: {data}")

                # Internal routing of updates
                update_type = data.get("type")
                if update_type in self.callbacks:
                    await self.callbacks[update_type](data)

            except websockets.ConnectionClosed:
                self.logger.warning("ResoniteLink connection closed remotely.")
                self.running = False
                break
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in ResoniteLink listener: {e}")

    def on_update(self, update_type: str, callback: Callable):
        """Register a callback for specific update types."""
        self.callbacks[update_type] = callback

    # High-level actions
    async def spawn_object(self, template_url: str, position: Dict[str, float]):
        """Spawn a 3D object in the current world."""
        return await self.send_command(
            "spawn", {"template": template_url, "position": position}
        )

    async def set_component_value(self, component_id: str, field: str, value: Any):
        """Set a specific field on a Resonite component."""
        return await self.send_command(
            "write", {"id": component_id, "field": field, "value": value}
        )

    async def get_component_value(self, component_id: str, field: str):
        """Request a field value from a Resonite component."""
        return await self.send_command("read", {"id": component_id, "field": field})
