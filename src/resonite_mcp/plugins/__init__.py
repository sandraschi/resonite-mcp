"""Resonite MCP Plugin System.

This module provides a plugin system for extending the Resonite MCP server
with custom functionality, similar to VRChat MCP's plugin architecture.
"""

from .base_plugin import BasePlugin
from .plugin_manager import PluginManager

__all__ = ["BasePlugin", "PluginManager"]
