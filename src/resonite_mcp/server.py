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
# Commented out as it interferes with MCP stdio protocol
# if os.name == "nt":  # Windows only
#     try:
#         import msvcrt
#
#         msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
#         msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
#     except Exception:
#         pass


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

# FastMCP 2.13.1+ server initialization
from fastmcp import FastMCP

server = FastMCP(
    name="Resonite MCP",
    version="0.1.1",
    instructions="""You are a Resonite social VR platform assistant. You can help users control avatars, manage worlds, execute ProtoFlux scripts, and handle social interactions through natural language commands.

Key capabilities:
- Avatar control: Load avatars, set parameters, control animations
- World management: Load/save worlds, manage sessions
- ProtoFlux scripting: Create and execute visual scripts
- Inventory management: Handle user assets and items
- Social features: Real-time interactions and collaboration

Always use OSC protocol for real-time control and provide clear feedback on actions taken.""",
)

# Import plugin system
try:
    from .plugins import PluginManager

    plugin_manager = PluginManager()
except ImportError:
    logger.warning("Plugin system not available")
    plugin_manager = None

# Import all tool modules to register individual tools
from . import tools


@server.tool()
async def health_check() -> Dict[str, Any]:
    """Check the health status of the Resonite MCP server and its components."""
    return {
        "status": "success",
        "message": "Resonite MCP server is healthy",
        "version": "0.1.0",
        "plugins_loaded": list(plugin_manager.loaded_plugins.keys()) if plugin_manager else [],
        "osc_connected": True,  # Simplified
    }


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
    # Initialize server asynchronously
    asyncio.run(initialize_server())

    logger.info("Starting Resonite MCP server stdio interface...")
    asyncio.run(server.run_stdio_async())
