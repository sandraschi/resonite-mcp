"""Base plugin class for Resonite MCP server extensions."""

import logging
from abc import ABC, abstractmethod
from typing import Any

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


class BasePlugin(ABC):
    """Base class for Resonite MCP plugins.

    Plugins can extend the Resonite MCP server with custom tools, resources,
    and functionality. Each plugin should inherit from this class and implement
    the required methods.
    """

    def __init__(self, name: str, version: str = "1.0.0", description: str = ""):
        """Initialize the plugin.

        Args:
            name: Plugin name (must be unique)
            version: Plugin version string
            description: Plugin description
        """
        self.name = name
        self.version = version
        self.description = description
        self.enabled = False
        self.logger = logging.getLogger(f"{__name__}.{name}")

    @property
    @abstractmethod
    def plugin_type(self) -> str:
        """Plugin type identifier (e.g., 'osc', 'protoflux', 'inventory')."""
        pass

    @abstractmethod
    async def initialize(self, server: FastMCP) -> bool:
        """Initialize the plugin with the MCP server.

        Args:
            server: FastMCP server instance to register tools with

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    async def shutdown(self) -> bool:
        """Shutdown the plugin and clean up resources.

        Returns:
            True if shutdown successful, False otherwise
        """
        pass

    def get_info(self) -> dict[str, Any]:
        """Get plugin information.

        Returns:
            Dictionary with plugin metadata
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "type": self.plugin_type,
            "enabled": self.enabled,
            "status": "active" if self.enabled else "inactive",
        }

    def log(self, level: str, message: str, *args, **kwargs):
        """Log a message with the plugin's logger.

        Args:
            level: Log level (debug, info, warning, error, critical)
            message: Log message
            *args: Additional arguments for string formatting
            **kwargs: Additional keyword arguments
        """
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(f"[{self.name}] {message}", *args, **kwargs)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.shutdown()
