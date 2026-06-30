"""Resonite MCP Tools Package - Individual tool registration.

This package contains all individual MCP tools for the Resonite MCP server.
Each tool module registers its functions as MCP tools when imported.
"""

# Import all tool modules to register individual tools
from . import (
    avatar,
    fleet_tools,
    inventory,
    osc,
    plugin,
    prefab_cards,
    resonite_link,
    rest_api,
    session,
    system,
    vbot,
    voice_tools,
)

__all__ = [
    "avatar",
    "fleet_tools",
    "inventory",
    "osc",
    "plugin",
    "prefab_cards",
    "resonite_link",
    "rest_api",
    "session",
    "system",
    "vbot",
    "voice_tools",
]
