"""Resonite MCP Server - Natural language control for Resonite social VR platform.

This MCP server provides comprehensive integration with Resonite, allowing users to:
- Control avatars and their parameters
- Manage worlds and sessions
- Execute ProtoFlux scripts
- Handle inventory and assets
- Perform real-time social interactions

The server supports both MCP stdio protocol for Claude Desktop integration
and FastAPI HTTP interface for web-based control.
"""

__version__ = "0.2.0"
__author__ = "Sandra Schipal"
__email__ = "sandra@example.com"

from .server import server

__all__ = ["server", "__version__", "__author__", "__email__"]
