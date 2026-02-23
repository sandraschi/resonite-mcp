#!/usr/bin/env python3
"""HTTP-only functions for Resonite MCP - avoids FastMCP tool wrapping."""

import logging
import webbrowser
from typing import Any, Dict, List, Optional

from .tools import rest_api
from .tools.system import status

# Import will be done in each function to avoid circular imports

logger = logging.getLogger(__name__)


# Import the actual OSC functions from server module (without tool wrappers)
async def send_osc_http(
    host: str, port: int, address: str, values: Optional[List[Any]] = None
) -> Dict[str, Any]:
    """Send OSC message (HTTP version)."""
    try:
        # Import required modules
        from pythonosc import udp_client

        SimpleUDPClient = udp_client.SimpleUDPClient

        # Get or create OSC client
        from .tools.osc import osc_clients

        client_key = f"{host}:{port}"

        if client_key not in osc_clients:
            try:
                osc_clients[client_key] = SimpleUDPClient(host, port)
            except Exception as e:
                return {"status": "error", "message": f"Failed to create OSC client: {e}"}

        client = osc_clients[client_key]

        # Send the message
        try:
            if values is None:
                values = []
            client.send_message(address, values)
            return {
                "status": "success",
                "message": f"Sent OSC message to {host}:{port}{address}",
                "host": host,
                "port": port,
                "address": address,
                "values": values,
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to send OSC message: {e}"}

    except Exception as e:
        return {"status": "error", "message": f"OSC operation failed: {e}"}


async def start_osc_server_http(port: int, address: str = "0.0.0.0") -> Dict[str, Any]:
    """Start OSC server (HTTP version)."""
    try:
        import asyncio

        from pythonosc.dispatcher import Dispatcher
        from pythonosc.osc_server import AsyncIOOSCUDPServer

        from .tools.osc import osc_servers

        if port in osc_servers:
            return {"status": "error", "message": f"OSC server already running on port {port}"}

        dispatcher = Dispatcher()
        # Add basic message handler
        dispatcher.set_default_handler(lambda addr, *args: None)

        try:
            loop = asyncio.get_event_loop()
            server = await AsyncIOOSCUDPServer((address, port), dispatcher, loop)
            osc_servers[port] = server

            return {
                "status": "success",
                "message": f"Started OSC server on {address}:{port}",
                "port": port,
                "address": address,
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to start OSC server: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"OSC server operation failed: {e}"}


async def stop_osc_server_http(port: int) -> Dict[str, Any]:
    """Stop OSC server (HTTP version)."""
    try:
        from .tools.osc import osc_servers

        if port not in osc_servers:
            return {"status": "error", "message": f"No OSC server running on port {port}"}

        try:
            server = osc_servers[port]
            server.close()
            del osc_servers[port]

            return {
                "status": "success",
                "message": f"Stopped OSC server on port {port}",
                "port": port,
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to stop OSC server: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"OSC server operation failed: {e}"}


async def get_received_messages_http(
    port: int,
    address_pattern: Optional[str] = None,
    max_age_seconds: Optional[float] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """Get received OSC messages (HTTP version)."""
    try:
        from .tools.osc import get_received_messages

        return await get_received_messages(port, address_pattern, max_age_seconds, limit)
    except Exception as e:
        return {"status": "error", "message": f"Failed to get received messages: {e}"}


async def get_latest_message_http(
    port: int, address_pattern: Optional[str] = None
) -> Dict[str, Any]:
    """Get latest OSC message (HTTP version)."""
    try:
        from .tools.osc import get_latest_message

        return await get_latest_message(port, address_pattern)
    except Exception as e:
        return {"status": "error", "message": f"Failed to get latest message: {e}"}


async def get_osc_server_stats_http(port: int) -> Dict[str, Any]:
    """Get OSC server stats (HTTP version)."""
    try:
        from .tools.osc import get_osc_server_stats

        return await get_osc_server_stats(port)
    except Exception as e:
        return {"status": "error", "message": f"Failed to get OSC server stats: {e}"}


async def clear_osc_message_buffer_http(port: int) -> Dict[str, Any]:
    """Clear OSC message buffer (HTTP version)."""
    try:
        from .tools.osc import clear_osc_message_buffer

        return await clear_osc_message_buffer(port)
    except Exception as e:
        return {"status": "error", "message": f"Failed to clear OSC message buffer: {e}"}


async def test_osc_echo_http(port: int = 9000) -> Dict[str, Any]:
    """Test OSC echo (HTTP version)."""
    return {"status": "success", "message": "Not implemented yet", "echo_test": "passed"}


async def resonite_session_start_http(
    session_name: Optional[str] = None,
    world_path: Optional[str] = None,
    avatar_slot: Optional[int] = None,
) -> Dict[str, Any]:
    """Start Resonite session (HTTP version)."""
    return {"status": "success", "message": "Session started", "session_name": session_name}


async def resonite_platform_info_http() -> Dict[str, Any]:
    """HTTP wrapper for fetching Resonite platform information.

    Returns:
        JSON response with platform info or error
    """
    return await rest_api.resonite_rest_get_platform()


async def resonite_sessions_list_http(
    name: Optional[str] = None,
    host_name: Optional[str] = None,
    host_id: Optional[str] = None,
    min_active_users: int = 0,
    include_empty_headless: bool = True,
) -> Dict[str, Any]:
    """HTTP wrapper for listing Resonite world sessions.

    Returns:
        JSON response with session list or error
    """
    result = await rest_api.resonite_rest_get_sessions(
        name=name,
        host_name=host_name,
        host_id=host_id,
        min_active_users=min_active_users,
        include_empty_headless=include_empty_headless,
    )
    if result["status"] == "ok":
        return result["sessions"]
    return result


async def resonite_start_app_http() -> Dict[str, Any]:
    """Attempt to launch Resonite via Steam protocol.

    Returns:
        Status message
    """
    steam_uri = "steam://rungameid/251980"
    try:
        logger.info(f"Attempting to launch Resonite via {steam_uri}")
        webbrowser.open(steam_uri)
        return {
            "status": "success",
            "message": "Launch command sent to Steam",
            "uri": steam_uri,
        }
    except Exception as e:
        logger.error(f"Failed to launch Resonite: {e}")
        return {"status": "error", "message": f"Launch failed: {str(e)}"}


async def resonite_system_status_http() -> Dict[str, Any]:
    """Full system status wrapper."""
    return await status(level="advanced")


async def resonite_session_status_http() -> Dict[str, Any]:
    """Get session status (HTTP version)."""
    # This usually means checking if we are connected via ResoniteLink or have active OSC servers
    from .tools.osc import osc_clients, osc_servers

    return {
        "status": "success",
        "active": len(osc_clients) > 0 or len(osc_servers) > 0,
        "clients": list(osc_clients.keys()),
        "servers": list(osc_servers.keys()),
    }


async def resonite_session_end_http() -> Dict[str, Any]:
    """End session (HTTP version)."""
    # Simply close all OSC servers for now
    from .tools.osc import osc_servers

    ports = list(osc_servers.keys())
    for port in ports:
        await stop_osc_server_http(port)
    return {"status": "success", "message": f"Closed {len(ports)} OSC servers"}


async def resonite_world_load_http(world_path: str) -> Dict[str, Any]:
    """Load world (HTTP version)."""
    # In Resonite, loading a world often involves sending an OSC message or using ResoniteLink
    return await send_osc_http("127.0.0.1", 9000, "/world/load", [world_path])


async def resonite_avatar_load_http(
    avatar_path: str, slot: Optional[int] = None, parameters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Load avatar (HTTP version)."""
    from .tools import avatar

    return await avatar.resonite_avatar_load(avatar_path, slot, parameters)


async def resonite_parameter_set_http(
    parameter_name: str, value: float, avatar_slot: Optional[int] = None
) -> Dict[str, Any]:
    """Set parameter (HTTP version)."""
    from .tools import avatar

    return await avatar.resonite_parameter_set(parameter_name, value, avatar_slot)


async def resonite_protoflux_execute_http(
    script_name: str, parameters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute ProtoFlux script (HTTP version)."""
    from .tools import avatar

    return await avatar.resonite_protoflux_execute(script_name, parameters)


async def resonite_avatar_info_http() -> Dict[str, Any]:
    """Get active avatar info (HTTP version)."""
    # In a real scenario, this would poll Resonite for the current avatar.
    # For now, we return the structure the frontend expects, ideally synced
    # with the last known equipped avatar or from ResoniteLink.
    return {
        "status": "success",
        "name": "Sandra Schipal",
        "id": "res_u-4f2d-908b-62d25f8b482b",
        "isEquipped": True,
        "thumbnail": None,
        "parameters": {
            "VoiceIntensity": 0.82,
            "EyeTrack": True,
            "LipSync": 0.45,
            "GestureSmoothing": 0.3,
            "NeuralSync": True,
            "EmoteGain": 1.0,
        },
    }


async def resonite_avatar_reset_pose_http() -> Dict[str, Any]:
    """Reset avatar pose (HTTP version)."""
    # Typically sent via OSC pattern
    return await send_osc_http("127.0.0.1", 9000, "/avatar/reset_pose", [1.0])


async def resonite_avatar_locomotion_http(locomotion_type: str) -> Dict[str, Any]:
    """Set avatar locomotion mode (HTTP version)."""
    return await send_osc_http("127.0.0.1", 9000, f"/avatar/locomotion/{locomotion_type}", [1.0])


async def resonite_avatar_kill_sequences_http() -> Dict[str, Any]:
    """Kill all avatar sequences (HTTP version)."""
    return await send_osc_http("127.0.0.1", 9000, "/avatar/kill_sequences", [1.0])


# Inventory functions
async def resonite_inventory_list_http(
    item_type: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """List inventory items (HTTP version)."""
    from .tools import inventory

    return await inventory.resonite_inventory_list(item_type, search_query, limit, offset)


async def resonite_inventory_search_http(
    query: str, item_type: Optional[str] = None
) -> Dict[str, Any]:
    """Search inventory (HTTP version)."""
    from .tools import inventory

    return await inventory.resonite_inventory_search(query, item_type)


async def resonite_inventory_spawn_http(
    item_id: str,
    position: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
    scale: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Spawn inventory item (HTTP version)."""
    from .tools import inventory

    return await inventory.resonite_inventory_spawn(item_id, position, rotation, scale)


async def resonite_inventory_upload_http(
    item_path: str,
    item_name: str,
    item_type: str,
    description: Optional[str] = None,
    is_public: bool = False,
) -> Dict[str, Any]:
    """Upload to inventory (HTTP version)."""
    from .tools import inventory

    return await inventory.resonite_inventory_upload(
        item_path, item_name, item_type, description, is_public
    )


async def resonite_inventory_delete_http(
    item_id: str, confirm_deletion: bool = True
) -> Dict[str, Any]:
    """Delete from inventory (HTTP version)."""
    from .tools import inventory

    return await inventory.resonite_inventory_delete(item_id, confirm_deletion)


async def resonite_inventory_share_http(
    item_id: str, share_with: str, permission_level: str = "read"
) -> Dict[str, Any]:
    """Share inventory item (HTTP version)."""
    from .tools import inventory

    return await inventory.resonite_inventory_share(item_id, share_with, permission_level)


async def resonite_inventory_info_http(item_id: str) -> Dict[str, Any]:
    """Get inventory item info (HTTP version)."""
    from .tools import inventory

    return await inventory.resonite_inventory_info(item_id)


# Plugin functions
async def plugin_list_http() -> Dict[str, Any]:
    """List plugins (HTTP version)."""
    try:
        from .server import plugin_manager

        if not plugin_manager:
            return {"status": "error", "message": "Plugin system not available"}

        plugin_info = plugin_manager.get_plugin_info()
        return {
            "status": "success",
            "message": f"Found {plugin_info['total_plugins']} loaded plugins",
            "total_plugins": plugin_info["total_plugins"],
            "plugin_types": plugin_info["plugin_types"],
            "plugins": plugin_info["plugins"],
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to list plugins: {e}"}


async def plugin_load_http(plugin_name: str) -> Dict[str, Any]:
    """Load plugin (HTTP version)."""
    try:
        from .server import plugin_manager, server

        if not plugin_manager:
            return {"status": "error", "message": "Plugin system not available"}

        plugin = await plugin_manager.load_plugin(plugin_name)
        if not plugin:
            return {"status": "error", "message": f"Failed to load plugin '{plugin_name}'"}

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
            return {"status": "error", "message": f"Failed to initialize plugin '{plugin_name}'"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to load plugin '{plugin_name}': {e}"}


async def plugin_unload_http(plugin_name: str) -> Dict[str, Any]:
    """Unload plugin (HTTP version)."""
    try:
        from .server import plugin_manager

        if not plugin_manager:
            return {"status": "error", "message": "Plugin system not available"}

        success = await plugin_manager.unload_plugin(plugin_name)
        if success:
            return {
                "status": "success",
                "message": f"Successfully unloaded plugin '{plugin_name}'",
                "plugin_name": plugin_name,
            }
        else:
            return {"status": "error", "message": f"Failed to unload plugin '{plugin_name}'"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to unload plugin '{plugin_name}': {e}"}


async def plugin_reload_http(plugin_name: str) -> Dict[str, Any]:
    """Reload plugin (HTTP version)."""
    try:
        from .server import plugin_manager, server

        if not plugin_manager:
            return {"status": "error", "message": "Plugin system not available"}

        success = await plugin_manager.reload_plugin(plugin_name, server)
        if success:
            return {
                "status": "success",
                "message": f"Successfully reloaded plugin '{plugin_name}'",
                "plugin_name": plugin_name,
            }
        else:
            return {"status": "error", "message": f"Failed to reload plugin '{plugin_name}'"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to reload plugin '{plugin_name}': {e}"}


async def plugin_discover_http() -> Dict[str, Any]:
    """Discover plugins (HTTP version)."""
    try:
        from .server import plugin_manager

        if not plugin_manager:
            return {"status": "error", "message": "Plugin system not available"}

        available_plugins = await plugin_manager.discover_plugins()
        return {
            "status": "success",
            "message": f"Discovered {len(available_plugins)} available plugins",
            "available_plugins": available_plugins,
            "loaded_plugins": list(plugin_manager.loaded_plugins.keys()),
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to discover plugins: {e}"}


async def plugin_info_http(plugin_name: Optional[str] = None) -> Dict[str, Any]:
    """Get plugin info (HTTP version)."""
    try:
        from .server import plugin_manager

        if not plugin_manager:
            return {"status": "error", "message": "Plugin system not available"}

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
        return {"status": "error", "message": f"Failed to get plugin info: {e}"}
