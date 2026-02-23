"""Resonite MCP Tools Package - Individual tool registration.

This package contains all individual MCP tools for the Resonite MCP server.
Each tool module registers its functions as MCP tools when imported.
"""

# Import all tool modules to register individual tools
from . import avatar, inventory, osc, plugin, session, system, resonite_link, rest_api

__all__ = ["avatar", "inventory", "osc", "plugin", "session", "system", "resonite_link", "rest_api"]
