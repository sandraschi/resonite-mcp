#!/usr/bin/env python3
"""CLI interface for Resonite MCP server."""

import argparse
import asyncio
import logging

from .server import initialize_server, server


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Resonite MCP Server - Natural language control for Resonite social VR platform"
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the HTTP server to (default: 127.0.0.1)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=10715,
        help="Port to bind the HTTP server to (default: 10715)",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)",
    )

    parser.add_argument(
        "--stdio",
        action="store_true",
        help="Run in stdio mode for MCP protocol (default: HTTP server mode)",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.1.1")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger(__name__)

    # Initialize server (plugins, etc.)
    asyncio.run(initialize_server())

    if args.stdio:
        # Run in MCP stdio mode using FastMCP's run method
        logger.info("Starting Resonite MCP server in stdio mode")
        server.run(transport="stdio")
    else:
        # Run HTTP server mode
        logger.info(f"Starting Resonite MCP server on {args.host}:{args.port}")
        import uvicorn

        # Run FastAPI server
        uvicorn.run(
            "resonite_mcp.http_server:app",
            host=args.host,
            port=args.port,
            reload=True,
            log_level=args.log_level.lower(),
        )


if __name__ == "__main__":
    main()
