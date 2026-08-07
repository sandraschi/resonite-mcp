"""Plugin Management Tools - Portmanteau for Resonite MCP plugin operations."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _get_plugin_manager():
    """Get the real PluginManager instance if available."""
    try:
        from ..server import plugin_manager

        return plugin_manager
    except (ImportError, AttributeError):
        return None


async def plugin_list() -> dict[str, Any]:
    """List all available and loaded plugins.

    Returns:
        Dictionary with plugin information

    Examples:
        List all plugins: plugin_list()
    """
    try:
        pm = _get_plugin_manager()
        if pm:
            loaded = list(pm.loaded_plugins.keys())
            discovered = [p.get("name", str(p)) for p in (pm.discovered_plugins or [])]
            return {
                "status": "success",
                "plugins": {
                    "loaded_plugins": loaded,
                    "discovered_plugins": discovered,
                    "total_loaded": len(loaded),
                    "total_discovered": len(discovered),
                },
            }
        return {
            "status": "success",
            "plugins": {
                "loaded_plugins": [],
                "discovered_plugins": [],
                "total_loaded": 0,
                "total_discovered": 0,
                "note": "PluginManager not available — plugin system not initialized.",
            },
        }
    except Exception as e:
        logger.error(f"Failed to list plugins: {e}")
        return {"status": "error", "message": f"Failed to list plugins: {e!s}"}


async def plugin_load(plugin_name: str) -> dict[str, Any]:
    """Load a plugin into the running server.

    Args:
        plugin_name: Name of the plugin to load

    Returns:
        Dictionary with plugin loading status

    Examples:
        Load OSC extensions: plugin_load("osc_extensions")
    """
    try:
        pm = _get_plugin_manager()
        if not pm:
            return {
                "status": "error",
                "message": "PluginManager not available — cannot load plugins.",
                "plugin_name": plugin_name,
            }
        result = await pm.load_plugin(plugin_name)
        if result:
            try:
                from ..server import server as mcp_server

                await pm.initialize_plugin(result, mcp_server)
            except Exception:
                logger.debug("Plugin init skipped for %s", result)
        return {
            "status": "success" if result else "error",
            "message": (
                f"Plugin '{plugin_name}' loaded" if result else f"Plugin '{plugin_name}' not found or failed to load"
            ),
            "plugin_name": plugin_name,
            "loaded": result,
        }
    except Exception as e:
        logger.error(f"Failed to load plugin {plugin_name}: {e}")
        return {
            "status": "error",
            "message": f"Failed to load plugin: {e!s}",
            "plugin_name": plugin_name,
        }


async def plugin_unload(plugin_name: str) -> dict[str, Any]:
    """Unload a plugin from the running server.

    Args:
        plugin_name: Name of the plugin to unload

    Returns:
        Dictionary with plugin unloading status

    Examples:
        Unload OSC extensions: plugin_unload("osc_extensions")
    """
    try:
        pm = _get_plugin_manager()
        if not pm:
            return {
                "status": "error",
                "message": "PluginManager not available — cannot unload plugins.",
                "plugin_name": plugin_name,
            }
        if plugin_name not in pm.loaded_plugins:
            return {
                "status": "error",
                "message": f"Plugin '{plugin_name}' is not loaded.",
                "plugin_name": plugin_name,
            }
        await pm.unload_plugin(plugin_name)
        return {
            "status": "success",
            "message": f"Plugin '{plugin_name}' unloaded.",
            "plugin_name": plugin_name,
        }
    except Exception as e:
        logger.error(f"Failed to unload plugin {plugin_name}: {e}")
        return {
            "status": "error",
            "message": f"Failed to unload plugin: {e!s}",
            "plugin_name": plugin_name,
        }


async def plugin_reload(plugin_name: str) -> dict[str, Any]:
    """Reload a plugin in the running server.

    This unloads and then reloads the plugin, useful for applying configuration changes.

    Args:
        plugin_name: Name of the plugin to reload

    Returns:
        Dictionary with plugin reload status

    Examples:
        Reload ProtoFlux helpers: plugin_reload("protoflux_helpers")
    """
    pm = _get_plugin_manager()
    if not pm:
        return {
            "status": "error",
            "message": "PluginManager not available — cannot reload plugins.",
            "plugin_name": plugin_name,
        }
    unload_result = await plugin_unload(plugin_name)
    if unload_result["status"] != "success":
        return unload_result
    return await plugin_load(plugin_name)


async def plugin_discover() -> dict[str, Any]:
    """Discover available plugins in the system.

    Scans plugin directories and returns information about all discoverable plugins.

    Returns:
        Dictionary with discovered plugin information

    Examples:
        Discover plugins: plugin_discover()
    """
    try:
        pm = _get_plugin_manager()
        if pm:
            await pm.discover_plugins()
            discovered = [
                {
                    "name": p.get("name", str(p)),
                    "path": p.get("path", ""),
                    "type": p.get("type", "unknown"),
                    "status": "loaded" if p.get("name") in pm.loaded_plugins else "available",
                }
                for p in (pm.discovered_plugins or [])
            ]
            return {
                "status": "success",
                "message": f"Discovered {len(discovered)} plugins",
                "discovery": {
                    "discovered_plugins": discovered,
                    "total_discovered": len(discovered),
                    "loaded_count": len(pm.loaded_plugins),
                },
            }
        return {
            "status": "error",
            "message": "PluginManager not available — plugin discovery not possible.",
        }
    except Exception as e:
        logger.error(f"Failed to discover plugins: {e}")
        return {"status": "error", "message": f"Failed to discover plugins: {e!s}"}


async def plugin_info(plugin_name: str | None = None) -> dict[str, Any]:
    """Get detailed information about a specific plugin or all plugins.

    Args:
        plugin_name: Name of specific plugin to get info for (optional)

    Returns:
        Dictionary with detailed plugin information

    Examples:
        Get info for specific plugin: plugin_info("osc_extensions")
        Get info for all plugins: plugin_info()
    """
    pm = _get_plugin_manager()
    if not pm:
        return {
            "status": "error",
            "message": "PluginManager not available.",
        }
    if plugin_name:
        loaded = plugin_name in pm.loaded_plugins
        discovered = any(p.get("name") == plugin_name for p in (pm.discovered_plugins or []))
        return {
            "status": "success",
            "plugin": {
                "name": plugin_name,
                "loaded": loaded,
                "discovered": discovered,
            },
        }
    return {
        "status": "success",
        "plugins_summary": {
            "total_loaded": len(pm.loaded_plugins),
            "total_discovered": len(pm.discovered_plugins or []),
            "loaded_names": list(pm.loaded_plugins.keys()),
        },
    }


# Import server for tool registration
from ..server import server

server.tool()(plugin_list)
server.tool()(plugin_load)
server.tool()(plugin_unload)
server.tool()(plugin_reload)
server.tool()(plugin_discover)
server.tool()(plugin_info)
