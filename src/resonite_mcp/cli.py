#!/usr/bin/env python3
"""CLI interface for Resonite MCP server."""

import argparse
import asyncio
import logging
import os

from .server import initialize_server, server


def _enable_agentic_mode():
    """Enable CodeMode BM25 agentic discovery (FastMCP 3.2+ experimental)."""
    try:
        from fastmcp.experimental.transforms import CodeMode

        server.add_transforms(CodeMode())
        logging.getLogger(__name__).info("CodeMode agentic discovery enabled")
    except ImportError:
        logging.getLogger(__name__).warning(
            "CodeMode not available (FastMCP >=3.2.0 required)"
        )


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
        default=10979,
        help="Port to bind the HTTP server to (default: 10979)",
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

    parser.add_argument(
        "--agentic",
        action="store_true",
        help="Enable CodeMode BM25 agentic skill discovery (FastMCP 3.2+)",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.8.0")

    args = parser.parse_args()

    from .utils.structured_logging import configure_file_logging
    from .utils.structured_logging import configure_json_logging_if_enabled

    configure_json_logging_if_enabled()
    if os.getenv("RESONITE_MCP_LOG_DIR"):
        configure_file_logging()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger(__name__)

    if args.agentic:
        _enable_agentic_mode()

    if args.stdio:
        logger.info("Starting Resonite MCP server in stdio mode (deferred init)")
        server.run(transport="stdio")
        return

    # HTTP mode: full init before starting server
    asyncio.run(initialize_server())
    logger.info(f"Starting Resonite MCP server on {args.host}:{args.port}")
    import uvicorn

    uvicorn.run(
        "resonite_mcp.http_server:app",
        host=args.host,
        port=args.port,
        reload=True,
        log_level=args.log_level.lower(),
    )


if __name__ == "__main__":
    main()
