"""Resonite MCP Plugin System.

This module provides a plugin system for extending the Resonite MCP server
with custom functionality, similar to VRChat MCP's plugin architecture.
"""

from .plugin_manager import PluginManager
from .base_plugin import BasePlugin

__all__ = ["PluginManager", "BasePlugin"]
