"""Plugin manager for Resonite MCP server."""

import asyncio
import importlib
import inspect
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from fastmcp import FastMCP

from .base_plugin import BasePlugin

logger = logging.getLogger(__name__)


class PluginManager:
    """Manager for loading and coordinating Resonite MCP plugins."""

    def __init__(self, plugins_dir: Optional[str] = None):
        """Initialize the plugin manager.

        Args:
            plugins_dir: Directory to scan for plugins (default: plugins/)
        """
        self.plugins_dir = Path(plugins_dir) if plugins_dir else Path(__file__).parent
        self.loaded_plugins: Dict[str, BasePlugin] = {}
        self.plugin_types: Dict[str, List[str]] = {}
        self.logger = logging.getLogger(f"{__name__}.PluginManager")

    async def discover_plugins(self) -> List[str]:
        """Discover available plugins in the plugins directory.

        Returns:
            List of discovered plugin names
        """
        discovered = []

        # Scan for Python files in plugins directory
        if self.plugins_dir.exists():
            for item in self.plugins_dir.iterdir():
                if item.is_file() and item.suffix == ".py" and not item.name.startswith("__"):
                    plugin_name = item.stem
                    discovered.append(plugin_name)
                    self.logger.debug(f"Discovered plugin: {plugin_name}")

        # Also scan for plugin subdirectories with __init__.py
        for item in self.plugins_dir.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                plugin_name = item.name
                discovered.append(plugin_name)
                self.logger.debug(f"Discovered plugin package: {plugin_name}")

        return discovered

    async def load_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Load a specific plugin by name.

        Args:
            plugin_name: Name of the plugin to load

        Returns:
            Loaded plugin instance or None if loading failed
        """
        if plugin_name in self.loaded_plugins:
            self.logger.warning(f"Plugin {plugin_name} is already loaded")
            return self.loaded_plugins[plugin_name]

        try:
            # Import the plugin module
            module_name = f"resonite_mcp.plugins.{plugin_name}"
            module = importlib.import_module(module_name)

            # Find plugin classes that inherit from BasePlugin
            plugin_classes = []
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and
                    issubclass(obj, BasePlugin) and
                    obj != BasePlugin):
                    plugin_classes.append(obj)

            if not plugin_classes:
                self.logger.error(f"No plugin classes found in {plugin_name}")
                return None

            if len(plugin_classes) > 1:
                self.logger.warning(f"Multiple plugin classes found in {plugin_name}, using first: {plugin_classes[0].__name__}")

            # Instantiate the plugin
            plugin_class = plugin_classes[0]
            plugin_instance = plugin_class()

            self.logger.info(f"Loaded plugin: {plugin_name} ({plugin_instance.plugin_type})")
            return plugin_instance

        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return None

    async def initialize_plugin(self, plugin: BasePlugin, server: FastMCP) -> bool:
        """Initialize a plugin with the MCP server.

        Args:
            plugin: Plugin instance to initialize
            server: FastMCP server instance

        Returns:
            True if initialization successful
        """
        try:
            success = await plugin.initialize(server)
            if success:
                plugin.enabled = True
                self.loaded_plugins[plugin.name] = plugin

                # Track by type
                plugin_type = plugin.plugin_type
                if plugin_type not in self.plugin_types:
                    self.plugin_types[plugin_type] = []
                self.plugin_types[plugin_type].append(plugin.name)

                self.logger.info(f"Initialized plugin: {plugin.name}")
                return True
            else:
                self.logger.error(f"Plugin initialization failed: {plugin.name}")
                return False

        except Exception as e:
            self.logger.error(f"Error initializing plugin {plugin.name}: {e}")
            return False

    async def load_all_plugins(self, server: FastMCP) -> Dict[str, bool]:
        """Load and initialize all available plugins.

        Args:
            server: FastMCP server instance

        Returns:
            Dictionary mapping plugin names to initialization success
        """
        results = {}

        # Discover available plugins
        available_plugins = await self.discover_plugins()
        self.logger.info(f"Discovered {len(available_plugins)} plugins")

        # Load and initialize each plugin
        for plugin_name in available_plugins:
            plugin = await self.load_plugin(plugin_name)
            if plugin:
                success = await self.initialize_plugin(plugin, server)
                results[plugin_name] = success
            else:
                results[plugin_name] = False

        successful = sum(1 for success in results.values() if success)
        self.logger.info(f"Successfully loaded {successful}/{len(results)} plugins")

        return results

    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin.

        Args:
            plugin_name: Name of the plugin to unload

        Returns:
            True if unloading successful
        """
        if plugin_name not in self.loaded_plugins:
            self.logger.warning(f"Plugin {plugin_name} is not loaded")
            return False

        plugin = self.loaded_plugins[plugin_name]

        try:
            success = await plugin.shutdown()
            if success:
                plugin.enabled = False

                # Remove from type tracking
                plugin_type = plugin.plugin_type
                if plugin_type in self.plugin_types and plugin_name in self.plugin_types[plugin_type]:
                    self.plugin_types[plugin_type].remove(plugin_name)

                del self.loaded_plugins[plugin_name]
                self.logger.info(f"Unloaded plugin: {plugin_name}")
                return True
            else:
                self.logger.error(f"Plugin shutdown failed: {plugin_name}")
                return False

        except Exception as e:
            self.logger.error(f"Error unloading plugin {plugin_name}: {e}")
            return False

    async def unload_all_plugins(self) -> Dict[str, bool]:
        """Unload all loaded plugins.

        Returns:
            Dictionary mapping plugin names to unload success
        """
        results = {}

        plugin_names = list(self.loaded_plugins.keys())
        for plugin_name in plugin_names:
            success = await self.unload_plugin(plugin_name)
            results[plugin_name] = success

        self.logger.info(f"Unloaded {sum(results.values())} plugins")
        return results

    def get_plugin_info(self, plugin_name: Optional[str] = None) -> Dict[str, Any]:
        """Get information about loaded plugins.

        Args:
            plugin_name: Specific plugin name, or None for all plugins

        Returns:
            Dictionary with plugin information
        """
        if plugin_name:
            if plugin_name in self.loaded_plugins:
                return self.loaded_plugins[plugin_name].get_info()
            else:
                return {"error": f"Plugin {plugin_name} not found"}
        else:
            return {
                "total_plugins": len(self.loaded_plugins),
                "plugin_types": self.plugin_types,
                "plugins": {name: plugin.get_info() for name, plugin in self.loaded_plugins.items()},
            }

    def get_plugins_by_type(self, plugin_type: str) -> List[str]:
        """Get all plugins of a specific type.

        Args:
            plugin_type: Plugin type to filter by

        Returns:
            List of plugin names of the specified type
        """
        return self.plugin_types.get(plugin_type, [])

    async def reload_plugin(self, plugin_name: str, server: FastMCP) -> bool:
        """Reload a plugin (unload and reload).

        Args:
            plugin_name: Name of the plugin to reload
            server: FastMCP server instance

        Returns:
            True if reload successful
        """
        # Unload first
        unload_success = await self.unload_plugin(plugin_name)
        if not unload_success:
            return False

        # Reload
        plugin = await self.load_plugin(plugin_name)
        if not plugin:
            return False

        # Re-initialize
        return await self.initialize_plugin(plugin, server)
