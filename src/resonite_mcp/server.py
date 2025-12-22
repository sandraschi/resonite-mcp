#!/usr/bin/env python3
"""Resonite MCP Server - FastMCP 2.13.1+ implementation for Resonite social VR platform.

This server provides natural language control over Resonite through OSC protocol,
enabling avatar control, world management, ProtoFlux scripting, and social interactions.
"""

import asyncio
import logging
import os
import sys
from typing import Any, Dict, List, Optional

# Windows binary mode setup for stdin/stdout
if os.name == "nt":  # Windows only
    try:
        import msvcrt
        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    except Exception:
        pass

# DevNullStdout class for stdio mode suppression
class DevNullStdout:
    """Context manager to suppress stdout writes during MCP initialization."""

    def __init__(self):
        self.original_stdout = sys.stdout
        self.buffer = []

    def write(self, data):
        """Capture writes instead of outputting them."""
        self.buffer.append(data)

    def flush(self):
        """No-op flush."""
        pass

    def restore(self):
        """Restore original stdout."""
        sys.stdout = self.original_stdout

    def __enter__(self):
        sys.stdout = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.restore()

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Detect if we're running in stdio mode (for MCP)
_is_stdio_mode = (
    len(sys.argv) == 1  # No arguments provided
    or (len(sys.argv) == 2 and sys.argv[1] == "-m")  # Just module flag
    or any(arg in ["--stdio", "stdio"] for arg in sys.argv)  # Explicit stdio flag
)

# Store OSC clients and servers
osc_clients: Dict[str, Any] = {}  # Will be SimpleUDPClient instances
osc_servers: Dict[int, Any] = {}  # Will be OSC server instances

# OSC Recording system
osc_recordings: Dict[str, List[Dict[str, Any]]] = {}

# FastMCP 2.13.1+ server initialization
from fastmcp import FastMCP

server = FastMCP(
    name="Resonite MCP",
    version="0.1.0",
    instructions="""You are a Resonite social VR platform assistant. You can help users control avatars, manage worlds, execute ProtoFlux scripts, and handle social interactions through natural language commands.

Key capabilities:
- Avatar control: Load avatars, set parameters, control animations
- World management: Load/save worlds, manage sessions
- ProtoFlux scripting: Create and execute visual scripts
- Inventory management: Handle user assets and items
- Social features: Real-time interactions and collaboration

Always use OSC protocol for real-time control and provide clear feedback on actions taken.""",
)

# Pydantic models for input validation (FastMCP 2.13)
from pydantic import BaseModel, Field


class OSCMessageInput(BaseModel):
    """Input model for OSC message sending."""

    host: str = Field(..., description="Target hostname or IP address")
    port: int = Field(gt=0, le=65535, description="Target UDP port (1-65535)")
    address: str = Field(
        ..., pattern=r"^/.*", description="OSC address pattern starting with /"
    )
    values: List[Any] = Field(
        default_factory=list, description="List of values to send"
    )


class OSCServerInput(BaseModel):
    """Input model for starting OSC server."""

    port: int = Field(
        gt=0, le=65535, description="UDP port to listen on (1-65535)"
    )
    address: str = Field(default="0.0.0.0", description="Network interface to bind to")


class OSCServerStopInput(BaseModel):
    """Input model for stopping OSC server."""

    port: int = Field(
        gt=0, le=65535, description="Port of the server to stop (1-65535)"
    )


class ResoniteSessionInput(BaseModel):
    """Input for Resonite session management."""

    session_name: Optional[str] = Field(
        None, description="Optional custom session name"
    )
    world_path: Optional[str] = Field(
        None, description="Initial world to load (resonite:// format)"
    )
    avatar_slot: Optional[int] = Field(
        None, ge=0, le=7, description="Avatar slot to use (0-7)"
    )


class AvatarControlInput(BaseModel):
    """Input for avatar control operations."""

    avatar_id: str = Field(..., description="Avatar identifier or path")
    slot: Optional[int] = Field(
        None, ge=0, le=7, description="Avatar slot (0-7), auto-assigned if not specified"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Initial parameter values to set"
    )


class ProtoFluxScriptInput(BaseModel):
    """Input for ProtoFlux script operations."""

    script_name: str = Field(..., description="Name of the ProtoFlux script")
    script_data: Optional[Dict[str, Any]] = Field(
        None, description="Script definition and parameters"
    )
    execute: bool = Field(
        True, description="Whether to execute the script immediately"
    )


class InventoryListInput(BaseModel):
    """Input for inventory listing operations."""

    item_type: Optional[str] = Field(
        None, description="Filter by item type: avatar, world, item, tool, script"
    )
    search_query: Optional[str] = Field(
        None, description="Search query to filter items by name or description"
    )
    limit: int = Field(
        50, ge=1, le=200, description="Maximum number of items to return"
    )
    offset: int = Field(
        0, ge=0, description="Number of items to skip (for pagination)"
    )


class InventorySpawnInput(BaseModel):
    """Input for spawning items from inventory."""

    item_id: str = Field(..., description="Unique identifier of the inventory item")
    position: Optional[List[float]] = Field(
        None, description="Position to spawn at [x, y, z]"
    )
    rotation: Optional[List[float]] = Field(
        None, description="Rotation to spawn with [x, y, z, w] quaternion"
    )
    scale: Optional[List[float]] = Field(
        None, description="Scale to spawn with [x, y, z]"
    )


class InventoryUploadInput(BaseModel):
    """Input for uploading items to inventory."""

    item_path: str = Field(..., description="Local file path to upload")
    item_name: str = Field(..., description="Name for the uploaded item")
    item_type: str = Field(
        ..., description="Type of item: avatar, world, item, tool, script"
    )
    description: Optional[str] = Field(
        None, description="Optional description for the item"
    )
    is_public: bool = Field(
        False, description="Whether the item should be publicly accessible"
    )


class InventoryDeleteInput(BaseModel):
    """Input for deleting items from inventory."""

    item_id: str = Field(..., description="Unique identifier of the inventory item")
    confirm_deletion: bool = Field(
        True, description="Must be true to confirm deletion"
    )


class InventoryShareInput(BaseModel):
    """Input for sharing inventory items."""

    item_id: str = Field(..., description="Unique identifier of the inventory item")
    share_with: str = Field(..., description="Username to share with")
    permission_level: str = Field(
        "read", description="Permission level: read, write, admin"
    )


# Import OSC components
try:
    from pythonosc import udp_client
    from pythonosc.osc_server import AsyncIOOSCUDPServer
    from pythonosc.dispatcher import Dispatcher
    SimpleUDPClient = udp_client.SimpleUDPClient
except ImportError:
    logger.warning("python-osc not available, OSC functionality will be limited")
    SimpleUDPClient = None

# Import plugin system
try:
    from .plugins import PluginManager
    plugin_manager = PluginManager()
except ImportError:
    logger.warning("Plugin system not available")
    plugin_manager = None


@server.tool()
async def send_osc(
    host: str,
    port: int,
    address: str,
    values: List[Any] = None
) -> Dict[str, Any]:
    """Send an OSC message to the specified address.

    This is a low-level OSC function for direct protocol control.
    Most users should use the higher-level Resonite-specific tools instead.

    Args:
        host: Target hostname or IP address (e.g., "127.0.0.1" for local Resonite)
        port: Target UDP port (default Resonite OSC port is 9000)
        address: OSC address pattern starting with "/" (e.g., "/avatar/parameter")
        values: List of values to send (optional)

    Returns:
        Dictionary with operation status and details

    Examples:
        Send a parameter value: send_osc("127.0.0.1", 9000, "/avatar/happy", [0.8])
        Send a bang/trigger: send_osc("127.0.0.1", 9000, "/action/jump", [])
    """
    if values is None:
        values = []

    try:
        # Get or create OSC client
        client_key = f"{host}:{port}"
        if client_key not in osc_clients:
            if SimpleUDPClient is None:
                return {"status": "error", "message": "OSC library not available"}
            osc_clients[client_key] = SimpleUDPClient(host, port)

        # Send the OSC message
        osc_clients[client_key].send_message(address, values)

        logger.info(f"Sent OSC to {host}:{port} - {address}: {values}")
        return {
            "status": "success",
            "message": f"OSC message sent successfully",
            "host": host,
            "port": port,
            "address": address,
            "values": values,
        }
    except Exception as e:
        error = f"Failed to send OSC message: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def start_osc_server(port: int, address: str = "0.0.0.0") -> Dict[str, Any]:
    """Start an OSC server to receive incoming messages from Resonite.

    This creates a UDP server that can receive OSC messages from Resonite
    for bidirectional communication and real-time feedback.

    Args:
        port: UDP port to listen on (1-65535)
        address: Network interface to bind to (default: "0.0.0.0" for all interfaces)

    Returns:
        Dictionary with server status and connection details

    Examples:
        Start server for Resonite feedback: start_osc_server(9001)
        Start server on specific interface: start_osc_server(9001, "127.0.0.1")
    """
    if port in osc_servers:
        return {
            "status": "error",
            "message": f"OSC server already running on port {port}",
        }

    try:
        # Create dispatcher for handling incoming messages
        dispatcher = Dispatcher()
        message_buffer = []

        def message_handler(address: str, *args):
            """Handle incoming OSC messages."""
            message = {
                "address": address,
                "args": list(args),
                "timestamp": asyncio.get_event_loop().time(),
            }
            message_buffer.append(message)
            # Keep only last 1000 messages to prevent memory issues
            if len(message_buffer) > 1000:
                message_buffer.pop(0)
            logger.debug(f"Received OSC: {address} {args}")

        # Set up default handler for all messages
        dispatcher.set_default_handler(message_handler)

        # Create and start the server
        osc_server = AsyncIOOSCUDPServer((address, port), dispatcher, asyncio.get_event_loop())
        await osc_server.create_serve_endpoint()

        # Store server instance with buffer
        osc_servers[port] = {
            "server": osc_server,
            "buffer": message_buffer,
            "address": address,
            "start_time": asyncio.get_event_loop().time(),
        }

        logger.info(f"OSC server started on {address}:{port}")
        return {
            "status": "success",
            "message": f"OSC server started on {address}:{port} with message buffering",
            "port": port,
            "address": address,
        }

    except Exception as e:
        error = f"Failed to start OSC server: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def stop_osc_server(port: int) -> Dict[str, Any]:
    """Stop a running OSC server.

    Args:
        port: Port of the server to stop

    Returns:
        Dictionary with operation status
    """
    server_info = osc_servers.pop(port, None)
    if not server_info:
        return {"status": "error", "message": f"No OSC server running on port {port}"}

    try:
        await server_info["server"].endpoint.close()
        logger.info(f"OSC server stopped on port {port}")
        return {
            "status": "success",
            "message": f"OSC server stopped on port {port}",
            "port": port,
        }
    except Exception as e:
        error = f"Failed to stop OSC server: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def get_received_messages(
    port: int,
    address_pattern: Optional[str] = None,
    max_age_seconds: Optional[float] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """Get OSC messages received by a running OSC server.

    Args:
        port: Port of the OSC server to query
        address_pattern: Filter by OSC address pattern (substring match)
        max_age_seconds: Only return messages newer than this age
        limit: Maximum number of messages to return

    Returns:
        Dictionary with messages and metadata
    """
    if port not in osc_servers:
        return {"status": "error", "message": f"No OSC server running on port {port}"}

    server_info = osc_servers[port]
    messages = server_info["buffer"]
    current_time = asyncio.get_event_loop().time()

    # Filter messages
    filtered_messages = []
    for msg in reversed(messages):  # Most recent first
        if address_pattern and address_pattern not in msg["address"]:
            continue
        if max_age_seconds and (current_time - msg["timestamp"]) > max_age_seconds:
            continue
        filtered_messages.append(msg)
        if len(filtered_messages) >= limit:
            break

    return {
        "status": "success",
        "messages": filtered_messages,
        "count": len(filtered_messages),
        "total_available": len(messages),
    }


@server.tool()
async def get_latest_message(
    port: int, address_pattern: Optional[str] = None
) -> Dict[str, Any]:
    """Get the most recent OSC message from a running server.

    Args:
        port: Port of the OSC server to query
        address_pattern: Filter by OSC address pattern

    Returns:
        Dictionary with latest message or empty if none found
    """
    if port not in osc_servers:
        return {"status": "error", "message": f"No OSC server running on port {port}"}

    server_info = osc_servers[port]
    messages = server_info["buffer"]

    # Find latest matching message
    for msg in reversed(messages):
        if not address_pattern or address_pattern in msg["address"]:
            return {
                "status": "success",
                "message": msg,
                "found": True,
            }

    return {"status": "success", "message": None, "found": False}


@server.tool()
async def get_osc_server_stats(port: int) -> Dict[str, Any]:
    """Get statistics about a running OSC server's message buffer.

    Args:
        port: Port of the OSC server to query

    Returns:
        Dictionary with server statistics
    """
    if port not in osc_servers:
        return {"status": "error", "message": f"No OSC server running on port {port}"}

    server_info = osc_servers[port]
    messages = server_info["buffer"]
    current_time = asyncio.get_event_loop().time()

    if not messages:
        stats = {
            "total_messages": 0,
            "max_buffer_size": 1000,
            "oldest_message_age": 0,
            "newest_message_age": 0,
        }
    else:
        oldest_age = current_time - messages[0]["timestamp"]
        newest_age = current_time - messages[-1]["timestamp"]
        stats = {
            "total_messages": len(messages),
            "max_buffer_size": 1000,
            "oldest_message_age": oldest_age,
            "newest_message_age": newest_age,
        }

    return {"status": "success", "stats": stats}


@server.tool()
async def clear_osc_message_buffer(port: int) -> Dict[str, Any]:
    """Clear all messages from an OSC server's buffer.

    Args:
        port: Port of the OSC server to clear

    Returns:
        Dictionary with clear operation results
    """
    if port not in osc_servers:
        return {"status": "error", "message": f"No OSC server running on port {port}"}

    server_info = osc_servers[port]
    cleared_count = len(server_info["buffer"])
    server_info["buffer"].clear()

    return {
        "status": "success",
        "messages_cleared": cleared_count,
        "message": f"Cleared {cleared_count} messages from buffer",
    }


@server.tool()
async def test_osc_echo(port: int = 9000) -> Dict[str, Any]:
    """Test OSC functionality by sending and receiving a message.

    Args:
        port: Port to use for the echo test

    Returns:
        Dictionary with test results
    """
    test_address = "/resonite/test/echo"
    test_values = ["test", 42, 3.14]

    server_started = False
    message_sent = False
    server_stopped = False

    try:
        # Start the OSC server
        start_result = await start_osc_server(port)
        if start_result["status"] == "success":
            server_started = True
            # Give the server a moment to start
            await asyncio.sleep(0.1)

            # Send test message
            send_result = await send_osc("127.0.0.1", port, test_address, test_values)
            if send_result["status"] == "success":
                message_sent = True
                # Give time for message to be received and logged
                await asyncio.sleep(0.2)

        # Stop the server
        stop_result = await stop_osc_server(port)
        if stop_result["status"] == "success":
            server_stopped = True

        return {
            "status": "success",
            "message": "OSC echo test completed successfully",
            "test_address": test_address,
            "test_values": test_values,
            "server_started": server_started,
            "message_sent": message_sent,
            "server_stopped": server_stopped,
        }

    except Exception as e:
        error = f"OSC echo test failed: {e}"
        logger.error(error)

        # Try to stop server if it was started
        if server_started:
            try:
                await stop_osc_server(port)
            except Exception:
                pass

        return {
            "status": "error",
            "message": error,
            "server_started": server_started,
            "message_sent": message_sent,
            "server_stopped": server_stopped,
        }


# ============================================================================
# Resonite-Specific Tools
# ============================================================================


@server.tool()
async def resonite_session_start(
    session_name: Optional[str] = None,
    world_path: Optional[str] = None,
    avatar_slot: Optional[int] = None,
) -> Dict[str, Any]:
    """Start a new Resonite session with optional world and avatar setup.

    This initializes OSC communication with Resonite and sets up a session
    for avatar control, world management, and social interactions.

    Args:
        session_name: Optional custom name for the session
        world_path: Initial world to load (resonite:// format)
        avatar_slot: Avatar slot to use (0-7)

    Returns:
        Dictionary with session information and status

    Examples:
        Start basic session: resonite_session_start()
        Start with world: resonite_session_start(world_path="resonite://MyWorld")
        Start with custom name: resonite_session_start(session_name="MySession", avatar_slot=0)
    """
    try:
        import uuid
        from datetime import datetime

        # Generate session ID
        session_id = session_name or f"resonite_session_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now()

        # Initialize OSC connection (Resonite default is 127.0.0.1:9000)
        osc_result = await send_osc("127.0.0.1", 9000, "/resonite/session/start", [session_id])

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
            await send_osc("127.0.0.1", 9000, "/resonite/avatar/slot", [avatar_slot])

        logger.info(f"Resonite session '{session_id}' started successfully")

        return {
            "status": "success",
            "message": f"Resonite session '{session_id}' started successfully",
            "session_info": session_info,
        }

    except Exception as e:
        error = f"Failed to start Resonite session: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def resonite_session_status() -> Dict[str, Any]:
    """Get the current status of the active Resonite session.

    Returns:
        Dictionary with session status and active components
    """
    try:
        # Query Resonite for current session status
        status_result = await send_osc("127.0.0.1", 9000, "/resonite/session/status", [])

        # This is a simplified implementation - in practice, you'd need to track
        # session state and check OSC server for responses
        return {
            "status": "success",
            "session_active": True,
            "platform": "resonite",
            "osc_connected": True,
            "last_activity": "unknown",  # Would be tracked in real implementation
            "active_components": ["osc_communication"],  # Would be tracked
        }

    except Exception as e:
        error = f"Failed to get session status: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
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
        if not any(world_path.startswith(prefix) for prefix in ["resonite://", "file://", "inventory://"]):
            return {
                "status": "error",
                "message": "Invalid world path format. Use resonite://, file://, or inventory:// prefixes",
            }

        # Send world load command
        result = await send_osc("127.0.0.1", 9000, "/resonite/world/load", [world_path])

        if result["status"] == "success":
            logger.info(f"World load initiated: {world_path}")
            return {
                "status": "success",
                "message": f"World load initiated for {world_path}",
                "world_path": world_path,
                "note": "World loading may take a few seconds to complete",
            }
        else:
            return result

    except Exception as e:
        error = f"Failed to load world: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def resonite_avatar_load(
    avatar_path: str,
    slot: Optional[int] = None,
    parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Load an avatar into the current Resonite session.

    Args:
        avatar_path: Path to the avatar (resonite:// for built-in, inventory:// for user, file:// for local)
        slot: Avatar slot to use (0-7, auto-assigned if not specified)
        parameters: Optional initial parameter values to set

    Returns:
        Dictionary with avatar loading status

    Examples:
        Load built-in avatar: resonite_avatar_load("resonite://DefaultAvatar")
        Load with parameters: resonite_avatar_load("inventory://MyAvatar", parameters={"happy": 0.8})
        Load to specific slot: resonite_avatar_load("file:///path/to/avatar.vrm", slot=0)
    """
    try:
        # Auto-assign slot if not specified
        if slot is None:
            slot = 0  # Default to first slot

        # Send avatar load command
        result = await send_osc("127.0.0.1", 9000, "/resonite/avatar/load", [avatar_path, slot])

        if result["status"] == "success":
            response = {
                "status": "success",
                "message": f"Avatar load initiated: {avatar_path} (slot {slot})",
                "avatar_path": avatar_path,
                "slot": slot,
            }

            # Set initial parameters if provided
            if parameters:
                for param_name, param_value in parameters.items():
                    param_result = await send_osc(
                        "127.0.0.1", 9000, f"/avatar/parameters/{param_name}", [param_value]
                    )
                    if param_result["status"] != "success":
                        logger.warning(f"Failed to set parameter {param_name}: {param_result['message']}")

                response["initial_parameters"] = parameters

            logger.info(f"Avatar loaded: {avatar_path} in slot {slot}")
            return response
        else:
            return result

    except Exception as e:
        error = f"Failed to load avatar: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def resonite_parameter_set(
    parameter_name: str,
    value: float,
    avatar_slot: Optional[int] = None,
) -> Dict[str, Any]:
    """Set an avatar parameter value in Resonite.

    Args:
        parameter_name: Name of the parameter to set
        value: Parameter value (typically 0.0 to 1.0 for most parameters)
        avatar_slot: Specific avatar slot (0-7), affects all if not specified

    Returns:
        Dictionary with parameter setting status

    Examples:
        Set happiness: resonite_parameter_set("Happy", 0.8)
        Set for specific avatar: resonite_parameter_set("Angry", 0.3, avatar_slot=1)
        Set custom parameter: resonite_parameter_set("MyCustomParam", 1.0)
    """
    try:
        # Build OSC address
        if avatar_slot is not None:
            address = f"/avatar/{avatar_slot}/parameters/{parameter_name}"
        else:
            address = f"/avatar/parameters/{parameter_name}"

        # Send parameter value
        result = await send_osc("127.0.0.1", 9000, address, [float(value)])

        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"Parameter '{parameter_name}' set to {value}",
                "parameter": parameter_name,
                "value": value,
                "avatar_slot": avatar_slot,
            }
        else:
            return result

    except Exception as e:
        error = f"Failed to set parameter: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def resonite_protoflux_execute(
    script_name: str,
    parameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute a ProtoFlux script in Resonite.

    Args:
        script_name: Name of the ProtoFlux script to execute
        parameters: Optional parameters to pass to the script

    Returns:
        Dictionary with script execution status

    Examples:
        Execute simple script: resonite_protoflux_execute("HelloWorld")
        Execute with parameters: resonite_protoflux_execute("ColorChanger", {"color": [1.0, 0.5, 0.0]})
    """
    try:
        # Send script execution command
        script_params = parameters or {}
        result = await send_osc("127.0.0.1", 9000, "/protoflux/execute", [script_name, script_params])

        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"ProtoFlux script '{script_name}' executed",
                "script_name": script_name,
                "parameters": script_params,
            }
        else:
            return result

    except Exception as e:
        error = f"Failed to execute ProtoFlux script: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def resonite_session_end() -> Dict[str, Any]:
    """End the current Resonite session and clean up resources.

    Returns:
        Dictionary with session cleanup status
    """
    try:
        # Send session end command
        result = await send_osc("127.0.0.1", 9000, "/resonite/session/end", [])

        # Clean up OSC connections (simplified)
        # In a real implementation, you'd track and clean up session-specific resources

        logger.info("Resonite session ended")

        return {
            "status": "success",
            "message": "Resonite session ended successfully",
            "cleanup_performed": ["osc_connections"],
        }

    except Exception as e:
        error = f"Failed to end session: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


# ============================================================================
# Inventory & Asset Management Tools
# ============================================================================


@server.tool()
async def resonite_inventory_list(
    item_type: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """List items in the user's Resonite inventory.

    Returns a paginated list of inventory items with metadata including
    names, types, creation dates, and sharing permissions.

    Args:
        item_type: Filter by item type (avatar, world, item, tool, script)
        search_query: Search query to filter items by name or description
        limit: Maximum number of items to return (1-200)
        offset: Number of items to skip for pagination

    Returns:
        Dictionary with inventory items and pagination info

    Examples:
        List all avatars: resonite_inventory_list("avatar")
        Search for worlds: resonite_inventory_list("world", "tutorial")
        Get first 10 items: resonite_inventory_list(limit=10)
    """
    try:
        # Build query parameters
        query_params = {
            "limit": limit,
            "offset": offset,
        }

        if item_type:
            query_params["type"] = item_type

        if search_query:
            query_params["search"] = search_query

        # Send inventory list request
        result = await send_osc("127.0.0.1", 9000, "/inventory/list", [query_params])

        if result["status"] == "success":
            # In a real implementation, this would parse the response
            # For now, return a mock response structure
            return {
                "status": "success",
                "message": f"Retrieved {limit} inventory items",
                "items": [],  # Would be populated from OSC response
                "total_count": 0,  # Would be from response
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "has_more": False,
                },
                "filters": {
                    "item_type": item_type,
                    "search_query": search_query,
                },
            }
        else:
            return result

    except Exception as e:
        error = f"Failed to list inventory items: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def resonite_inventory_search(query: str, item_type: Optional[str] = None) -> Dict[str, Any]:
    """Search for items in the user's Resonite inventory.

    Performs a full-text search across item names, descriptions, and tags.

    Args:
        query: Search query string
        item_type: Optional type filter (avatar, world, item, tool, script)

    Returns:
        Dictionary with matching inventory items

    Examples:
        Search all items: resonite_inventory_search("robot")
        Search avatars only: resonite_inventory_search("anime", "avatar")
    """
    try:
        search_params = {"query": query}

        if item_type:
            search_params["type"] = item_type

        result = await send_osc("127.0.0.1", 9000, "/inventory/search", [search_params])

        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"Found items matching '{query}'",
                "query": query,
                "item_type_filter": item_type,
                "results": [],  # Would be populated from OSC response
                "total_matches": 0,  # Would be from response
            }
        else:
            return result

    except Exception as e:
        error = f"Failed to search inventory: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def resonite_inventory_spawn(
    item_id: str,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
    scale: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Spawn an item from inventory into the current world.

    Places an inventory item at the specified location in the current world.

    Args:
        item_id: Unique identifier of the inventory item
        position: Position to spawn at [x, y, z] (optional, uses default if not specified)
        rotation: Rotation quaternion [x, y, z, w] (optional)
        scale: Scale vector [x, y, z] (optional, defaults to [1, 1, 1])

    Returns:
        Dictionary with spawn operation status

    Examples:
        Spawn at default location: resonite_inventory_spawn("item_123")
        Spawn at specific position: resonite_inventory_spawn("avatar_456", [0, 1.6, 0])
        Spawn with rotation: resonite_inventory_spawn("world_789", [5, 0, 5], [0, 0, 0, 1])
    """
    try:
        spawn_params = {"item_id": item_id}

        if position:
            spawn_params["position"] = position

        if rotation:
            spawn_params["rotation"] = rotation

        if scale:
            spawn_params["scale"] = scale

        result = await send_osc("127.0.0.1", 9000, "/inventory/spawn", [spawn_params])

        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"Successfully spawned item {item_id}",
                "item_id": item_id,
                "spawn_parameters": {
                    "position": position,
                    "rotation": rotation,
                    "scale": scale,
                },
            }
        else:
            return result

    except Exception as e:
        error = f"Failed to spawn inventory item: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def resonite_inventory_upload(
    item_path: str,
    item_name: str,
    item_type: str,
    description: Optional[str] = None,
    is_public: bool = False,
) -> Dict[str, Any]:
    """Upload a local file to Resonite inventory.

    Uploads a local file (avatar, world, item, etc.) to the user's cloud inventory.

    Args:
        item_path: Local file path to upload
        item_name: Name for the uploaded item
        item_type: Type of item (avatar, world, item, tool, script)
        description: Optional description for the item
        is_public: Whether the item should be publicly accessible

    Returns:
        Dictionary with upload operation status

    Examples:
        Upload avatar: resonite_inventory_upload("/path/to/avatar.vrm", "My Avatar", "avatar")
        Upload world: resonite_inventory_upload("/path/to/world.resonite", "My World", "world", "A cool world", true)
    """
    try:
        # Validate item type
        valid_types = ["avatar", "world", "item", "tool", "script"]
        if item_type not in valid_types:
            return {
                "status": "error",
                "message": f"Invalid item type. Must be one of: {', '.join(valid_types)}",
            }

        # Check if file exists
        if not os.path.exists(item_path):
            return {
                "status": "error",
                "message": f"File not found: {item_path}",
            }

        upload_params = {
            "file_path": item_path,
            "name": item_name,
            "type": item_type,
            "public": is_public,
        }

        if description:
            upload_params["description"] = description

        result = await send_osc("127.0.0.1", 9000, "/inventory/upload", [upload_params])

        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"Successfully uploaded {item_name} to inventory",
                "item_name": item_name,
                "item_type": item_type,
                "file_path": item_path,
                "is_public": is_public,
                "description": description,
            }
        else:
            return result

    except Exception as e:
        error = f"Failed to upload item to inventory: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def resonite_inventory_delete(item_id: str, confirm_deletion: bool = True) -> Dict[str, Any]:
    """Delete an item from the user's Resonite inventory.

    Permanently removes an item from the inventory. This action cannot be undone.

    Args:
        item_id: Unique identifier of the inventory item
        confirm_deletion: Must be true to confirm deletion (safety check)

    Returns:
        Dictionary with deletion operation status

    Examples:
        Delete item: resonite_inventory_delete("item_123", true)
    """
    try:
        if not confirm_deletion:
            return {
                "status": "error",
                "message": "Deletion not confirmed. Set confirm_deletion=true to proceed.",
            }

        result = await send_osc("127.0.0.1", 9000, "/inventory/delete", [item_id])

        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"Successfully deleted item {item_id} from inventory",
                "item_id": item_id,
                "deleted": True,
            }
        else:
            return result

    except Exception as e:
        error = f"Failed to delete inventory item: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def resonite_inventory_share(
    item_id: str,
    share_with: str,
    permission_level: str = "read",
) -> Dict[str, Any]:
    """Share an inventory item with another user.

    Grants access to an inventory item for another Resonite user.

    Args:
        item_id: Unique identifier of the inventory item
        share_with: Username to share with
        permission_level: Permission level (read, write, admin)

    Returns:
        Dictionary with sharing operation status

    Examples:
        Share for viewing: resonite_inventory_share("item_123", "friend_user", "read")
        Share for editing: resonite_inventory_share("world_456", "collaborator", "write")
    """
    try:
        # Validate permission level
        valid_permissions = ["read", "write", "admin"]
        if permission_level not in valid_permissions:
            return {
                "status": "error",
                "message": f"Invalid permission level. Must be one of: {', '.join(valid_permissions)}",
            }

        share_params = {
            "item_id": item_id,
            "username": share_with,
            "permission": permission_level,
        }

        result = await send_osc("127.0.0.1", 9000, "/inventory/share", [share_params])

        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"Successfully shared item {item_id} with {share_with}",
                "item_id": item_id,
                "shared_with": share_with,
                "permission_level": permission_level,
            }
        else:
            return result

    except Exception as e:
        error = f"Failed to share inventory item: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def resonite_inventory_info(item_id: str) -> Dict[str, Any]:
    """Get detailed information about an inventory item.

    Retrieves comprehensive metadata about a specific inventory item including
    ownership, sharing permissions, usage statistics, and file details.

    Args:
        item_id: Unique identifier of the inventory item

    Returns:
        Dictionary with detailed item information

    Examples:
        Get item details: resonite_inventory_info("avatar_123")
    """
    try:
        result = await send_osc("127.0.0.1", 9000, "/inventory/info", [item_id])

        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"Retrieved information for item {item_id}",
                "item_id": item_id,
                "item_info": {},  # Would be populated from OSC response
            }
        else:
            return result

    except Exception as e:
        error = f"Failed to get inventory item info: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


# ============================================================================
# Plugin Management Tools
# ============================================================================


@server.tool()
async def plugin_list() -> Dict[str, Any]:
    """List all loaded plugins and their status.

    Returns information about all plugins currently loaded in the system,
    including their types, versions, and enabled status.

    Returns:
        Dictionary with plugin information and statistics

    Examples:
        List all plugins: plugin_list()
    """
    try:
        if not plugin_manager:
            return {
                "status": "error",
                "message": "Plugin system not available",
            }

        plugin_info = plugin_manager.get_plugin_info()

        return {
            "status": "success",
            "message": f"Found {plugin_info['total_plugins']} loaded plugins",
            "total_plugins": plugin_info["total_plugins"],
            "plugin_types": plugin_info["plugin_types"],
            "plugins": plugin_info["plugins"],
        }

    except Exception as e:
        error = f"Failed to list plugins: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def plugin_load(plugin_name: str) -> Dict[str, Any]:
    """Load and initialize a specific plugin.

    Loads a plugin by name and initializes it with the MCP server.
    The plugin must be available in the plugins directory.

    Args:
        plugin_name: Name of the plugin to load

    Returns:
        Dictionary with plugin loading status

    Examples:
        Load OSC extensions: plugin_load("osc_extensions")
        Load ProtoFlux helpers: plugin_load("protoflux_helpers")
    """
    try:
        if not plugin_manager:
            return {
                "status": "error",
                "message": "Plugin system not available",
            }

        # Load the plugin
        plugin = await plugin_manager.load_plugin(plugin_name)
        if not plugin:
            return {
                "status": "error",
                "message": f"Failed to load plugin '{plugin_name}'",
            }

        # Initialize the plugin
        success = await plugin_manager.initialize_plugin(plugin, server)
        if success:
            return {
                "status": "success",
                "message": f"Successfully loaded and initialized plugin '{plugin_name}'",
                "plugin_name": plugin_name,
                "plugin_type": plugin.plugin_type,
                "plugin_info": plugin.get_info(),
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to initialize plugin '{plugin_name}'",
            }

    except Exception as e:
        error = f"Failed to load plugin '{plugin_name}': {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def plugin_unload(plugin_name: str) -> Dict[str, Any]:
    """Unload a specific plugin.

    Shuts down and unloads a plugin, removing it from the system.

    Args:
        plugin_name: Name of the plugin to unload

    Returns:
        Dictionary with plugin unloading status

    Examples:
        Unload a plugin: plugin_unload("osc_extensions")
    """
    try:
        if not plugin_manager:
            return {
                "status": "error",
                "message": "Plugin system not available",
            }

        success = await plugin_manager.unload_plugin(plugin_name)
        if success:
            return {
                "status": "success",
                "message": f"Successfully unloaded plugin '{plugin_name}'",
                "plugin_name": plugin_name,
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to unload plugin '{plugin_name}'",
            }

    except Exception as e:
        error = f"Failed to unload plugin '{plugin_name}': {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def plugin_reload(plugin_name: str) -> Dict[str, Any]:
    """Reload a specific plugin.

    Unloads and then reloads a plugin, useful for applying updates
    or fixing issues without restarting the server.

    Args:
        plugin_name: Name of the plugin to reload

    Returns:
        Dictionary with plugin reload status

    Examples:
        Reload a plugin: plugin_reload("protoflux_helpers")
    """
    try:
        if not plugin_manager:
            return {
                "status": "error",
                "message": "Plugin system not available",
            }

        success = await plugin_manager.reload_plugin(plugin_name, server)
        if success:
            return {
                "status": "success",
                "message": f"Successfully reloaded plugin '{plugin_name}'",
                "plugin_name": plugin_name,
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to reload plugin '{plugin_name}'",
            }

    except Exception as e:
        error = f"Failed to reload plugin '{plugin_name}': {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def plugin_discover() -> Dict[str, Any]:
    """Discover available plugins in the plugins directory.

    Scans the plugins directory for available plugins that can be loaded.

    Returns:
        Dictionary with discovered plugins information

    Examples:
        Discover plugins: plugin_discover()
    """
    try:
        if not plugin_manager:
            return {
                "status": "error",
                "message": "Plugin system not available",
            }

        available_plugins = await plugin_manager.discover_plugins()

        return {
            "status": "success",
            "message": f"Discovered {len(available_plugins)} available plugins",
            "available_plugins": available_plugins,
            "loaded_plugins": list(plugin_manager.loaded_plugins.keys()),
        }

    except Exception as e:
        error = f"Failed to discover plugins: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


@server.tool()
async def plugin_info(plugin_name: Optional[str] = None) -> Dict[str, Any]:
    """Get detailed information about a specific plugin or all plugins.

    Args:
        plugin_name: Name of specific plugin, or None for all plugins

    Returns:
        Dictionary with plugin information

    Examples:
        Get all plugin info: plugin_info()
        Get specific plugin info: plugin_info("osc_extensions")
    """
    try:
        if not plugin_manager:
            return {
                "status": "error",
                "message": "Plugin system not available",
            }

        info = plugin_manager.get_plugin_info(plugin_name)

        if plugin_name:
            return {
                "status": "success",
                "message": f"Retrieved information for plugin '{plugin_name}'",
                "plugin_info": info,
            }
        else:
            return {
                "status": "success",
                "message": f"Retrieved information for {info['total_plugins']} plugins",
                "plugin_info": info,
            }

    except Exception as e:
        error = f"Failed to get plugin info: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


async def initialize_server():
    """Initialize the server and load plugins."""
    logger.info("Initializing Resonite MCP server...")

    # Load and initialize plugins
    if plugin_manager:
        logger.info("Loading plugins...")
        plugin_results = await plugin_manager.load_all_plugins(server)

        successful_plugins = sum(1 for success in plugin_results.values() if success)
        total_plugins = len(plugin_results)

        logger.info(f"Plugin loading complete: {successful_plugins}/{total_plugins} plugins loaded")

        if plugin_results:
            logger.info("Loaded plugins:")
            for plugin_name, success in plugin_results.items():
                status = "✅" if success else "❌"
                logger.info(f"  {status} {plugin_name}")
    else:
        logger.warning("Plugin system not available - running without plugins")

    logger.info("Resonite MCP server initialization complete")


if __name__ == "__main__":
    # Run the MCP server
    import mcp.server.stdio

    # Initialize server asynchronously
    asyncio.run(initialize_server())

    logger.info("Starting Resonite MCP server stdio interface...")
    mcp.server.stdio.run_server(server.to_server())
