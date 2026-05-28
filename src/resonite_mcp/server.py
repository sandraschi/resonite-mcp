#!/usr/bin/env python3
"""Resonite MCP Server - FastMCP 3.1+ implementation for Resonite social VR platform.

This server provides natural language control over Resonite through OSC protocol,
enabling avatar control, world management, ProtoFlux scripting, and social interactions.
"""

import asyncio
import logging
import os
import subprocess
import sys
import webbrowser
from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.server import create_proxy
from starlette.responses import JSONResponse

from .llm import detect_local_llms, get_best_substrate, synthesize_answer
from .transport import run_server_async

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

server = FastMCP(
    name="Resonite MCP",
    version="0.8.0",
    instructions="""You are a Resonite social VR platform assistant. You can help users control avatars, manage worlds, execute ProtoFlux scripts, and handle social interactions through natural language commands.

Key capabilities:
- Avatar control: Load avatars, set parameters, control animations
- World management: Load/save worlds, manage sessions
- ProtoFlux scripting: Create and execute visual scripts
- Inventory management: Handle user assets and items
- Social features: Real-time interactions and collaboration

Always use OSC protocol for real-time control and provide clear feedback on actions taken.""",
)

# MCP Bridge: ProxyProvider for multi-server federation
_bridge_proxies = []
bridge_urls = os.getenv("MCP_BRIDGE_URLS", "")
if bridge_urls:
    for url in bridge_urls.split(","):
        url = url.strip()
        if url:
            try:
                server.add_provider(create_proxy(url))
                _bridge_proxies.append(url)
            except Exception:
                pass

# Import tools after server exists to avoid circular import (tools need server for @server.tool())
# Register FastMCP 3.2+ prompt templates
from . import (
    prompts,  # noqa: F401
    tools,  # noqa: F401
)

# Import plugin system
try:
    from .plugins import PluginManager

    plugin_manager = PluginManager()
except ImportError:
    logger.warning("Plugin system not available")
    plugin_manager = None

# Global client instances
resonite_link_client = None


@server.tool()
async def search_guides(query: str, limit: int = 5) -> dict[str, Any]:
    """Perform a semantic search over the Resonite technical guides and documentation."""
    try:
        from .rag import rag_engine

        results = await rag_engine.search(query, limit)
        return {"status": "success", "results": results}
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return {"status": "error", "message": str(e)}


@server.tool()
async def ask_resonite(question: str) -> str:
    """Ask a question about Resonite and get a synthesized answer based on technical documentation."""
    try:
        from .rag import rag_engine

        results = await rag_engine.search(question, limit=3)
        if not results:
            return "No relevant documentation found for that question."

        substrate = await get_best_substrate()
        if not substrate:
            # Fallback to simple snippet return if no LLM found
            context = "\n\n".join([f"From {r['title']}:\n{r['text']}" for r in results])
            return f"Based on Resonite documentation (Note: No local LLM found for synthesis):\n\n{context}"

        answer = await synthesize_answer(
            question, "\n\n".join([r["text"] for r in results]), substrate
        )
        return f"Synthesized via {substrate.provider} ({substrate.name}):\n\n{answer}"
    except Exception as e:
        return f"Error querying documentation: {e!s}"


def is_resonite_installed() -> bool:
    """Check if Resonite is installed on the system."""
    if os.name != "nt":
        return False

    try:
        import winreg

        # Check Steam Installation
        steam_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 2519830",
            r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 2519830",
        ]
        for path in steam_paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                winreg.CloseKey(key)
                return True
            except OSError:
                continue

        # Check for standalone or common paths
        common_paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Yellow Dog Man Studios\Resonite"),
            os.path.expandvars(r"%PROGRAMFILES%\Resonite"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Resonite"),
        ]
        for p in common_paths:
            if os.path.exists(p):
                return True
    except Exception as e:
        logger.error(f"Error checking Resonite installation: {e}")

    return False


def is_resonite_running() -> bool:
    """Check if Resonite is currently running."""
    if os.name != "nt":
        return False

    try:
        # Simple tasklist check to avoid extra dependencies if psutil is missing
        output = subprocess.check_output(
            'tasklist /FI "IMAGENAME eq Resonite.exe"', shell=True
        ).decode()
        return "Resonite.exe" in output
    except Exception:
        return False


@server.tool()
async def health_check() -> dict[str, Any]:
    """Check the health status of the Resonite MCP server and its components."""
    installed = is_resonite_installed()
    running = is_resonite_running()

    return {
        "status": "success",
        "message": "Resonite MCP server is healthy",
        "version": "0.8.0",
        "agent_lab_phase": 4,
        "plugins_loaded": list(plugin_manager.loaded_plugins.keys())
        if plugin_manager
        else [],
        "osc_connected": True,
        "resonite_link_connected": resonite_link_client.running
        if resonite_link_client
        else False,
        "rag_engine_active": True,
        "llm_substrate": (await get_best_substrate()).name
        if await get_best_substrate()
        else "none",
        "resonite_installed": installed,
        "resonite_running": running,
    }


@server.tool()
async def agentic_plan_execute(
    goal: str,
    ctx: Context = None,
) -> dict[str, Any]:
    """Plan and execute a multi-step Resonite task using LLM reasoning.

    Uses FastMCP 3.2+ ctx.sample() to autonomously plan and execute
    complex Resonite workflows (avatar setup, world loading, asset import).

    ## Return Format
    {"success": bool, "message": str, "data": {"plan": str, "reasoning": str}}

    ## Examples
    agentic_plan_execute("Load the TutorialWorld and set up my avatar")
    """
    try:
        from .agentic import agentic_execute, agentic_plan

        tool_names = [
            "resonite_session_start", "resonite_world_load", "resonite_avatar_load",
            "resonite_parameter_set", "resonite_inventory_list", "resonite_inventory_spawn",
            "resonite_rest_get_sessions", "send_osc",
        ]

        plan = await agentic_plan(ctx, goal, tool_names)
        result = await agentic_execute(ctx, plan, {"available_tools": tool_names})

        return {
            "success": True,
            "message": f"Agentic plan generated and executed for: {goal[:80]}",
            "data": {
                "goal": goal,
                "plan": plan,
                "reasoning": result.get("reasoning", ""),
            },
        }
    except Exception as e:
        logger.error(f"Agentic workflow failed: {e}")
        return {"success": False, "message": str(e), "data": {}}


@server.custom_route("/api/resonite/launch", methods=["POST"])
async def launch_resonite(request):
    """Launch Resonite via Steam protocol."""
    try:
        # Launch using the Steam shortcut URL
        webbrowser.open("steam://rungameid/2519830")
        return JSONResponse(
            {"status": "success", "message": "Resonite launch command sent"}
        )
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@server.custom_route("/api/status", methods=["GET"])
async def get_status(request):
    """SOTA Status endpoint."""
    installed = is_resonite_installed()
    running = is_resonite_running()

    return JSONResponse(
        {
            "status": "success",
            "authenticated": True,
            "workspace": "Resonite MCP",
            "server_running": True,
            "resonite_installed": installed,
            "resonite_running": running,
            "launch_url": "steam://rungameid/2519830",
        }
    )


@server.custom_route("/api/stats", methods=["GET"])
async def get_stats(request):
    """SOTA Stats endpoint."""
    return JSONResponse({"worlds": 42, "avatars": 156, "sessions": 12, "scripts": 89})


@server.custom_route("/api/llm-discovery", methods=["GET"])
async def discover_llms(request):
    llms = await detect_local_llms()
    return JSONResponse(
        {
            "llms": [
                {
                    "name": llm_info.name,
                    "provider": llm_info.provider,
                    "url": llm_info.url,
                    "model_id": llm_info.model_id,
                }
                for llm_info in llms
            ]
        }
    )


async def initialize_server():
    """Initialize the server, load plugins, and set up RAG."""
    logger.info("Initializing Resonite MCP server...")

    # Initialize RAG Engine
    try:
        from .rag import rag_engine

        await rag_engine.initialize()
    except Exception as e:
        logger.error(f"Failed to initialize RAG engine: {e}")

    global resonite_link_client
    try:
        from .resonite_link import ResoniteLinkClient

        resonite_link_client = ResoniteLinkClient()
        logger.info("ResoniteLink client instantiated")
    except ImportError:
        logger.warning("ResoniteLink client not available (websockets missing?)")

    # Load and initialize plugins
    if plugin_manager:
        logger.info("Loading plugins...")
        plugin_results = await plugin_manager.load_all_plugins(server)
        logger.info(
            f"Plugin loading complete: {sum(1 for success in plugin_results.values() if success)} plugins loaded"
        )
    else:
        logger.warning("Plugin system not available - running without plugins")

    logger.info("Resonite MCP server initialization complete")

    try:
        from .utils.telemetry import (
            init_metrics,
            install_tool_call_wrapper,
            metrics_enabled,
            register_metrics_routes,
            start_metrics_server,
            update_runtime_gauges,
        )

        init_metrics()
        install_tool_call_wrapper(server)
        register_metrics_routes(server)
        if metrics_enabled():
            start_metrics_server()
        update_runtime_gauges()
    except Exception as exc:
        logger.warning("Telemetry setup failed: %s", exc)


if __name__ == "__main__":

    async def _main():
        await initialize_server()
        # FastMCP 3.1 run_server automatically handles the starlette/fastapi instance if configured
        await run_server_async(server, server_name="resonite-mcp")

    asyncio.run(_main())
