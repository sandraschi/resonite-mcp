#!/usr/bin/env python3
"""HTTP server for Resonite MCP - FastAPI interface for web-based control."""

# --- HEALTH_ENDPOINT_STANDARD (mcp-central-docs/standards/HEALTH_ENDPOINT_STANDARD.md) ---
import datetime
import logging

# Functions will be imported inside endpoints to avoid tool wrapping
# Configure logging and telemetry
import os
import shutil
import subprocess
import subprocess as _subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import __version__
from .activity_log import activity_log
from .utils.structured_logging import configure_file_logging, configure_json_logging_if_enabled
from .utils.telemetry import init_metrics, metrics_enabled, register_metrics_routes, start_metrics_server

_STARTED = datetime.datetime.now(datetime.UTC)


def _git_sha() -> str:
    """Short git SHA, resolved once at import -- never per-request, never
    crashes health on a missing git (per the standard)."""
    try:
        repo_root = Path(__file__).resolve().parents[2]  # src/resonite_mcp/http_server.py -> repo root
        git_path = shutil.which("git") or "git"
        result = _subprocess.run(  # noqa: S603 -- fixed args (rev-parse --short HEAD), no user input
            [git_path, "-C", str(repo_root), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


_GIT_SHA = _git_sha()
_SHUTTING_DOWN = {"value": False}

configure_json_logging_if_enabled()
if os.getenv("RESONITE_MCP_LOG_DIR"):
    configure_file_logging()

init_metrics()
if metrics_enabled():
    start_metrics_server()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Resonite MCP Server",
    description="HTTP API for Resonite social VR platform control",
    version="1.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

register_metrics_routes(app)

activity_log.info("server", "Server started")

_RESONITE_TAURI = os.environ.get("RESONITE_TAURI", "").lower() in ("1", "true", "yes")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:10978",
        "http://localhost:10978",
        "http://goliath:10978",
        "http://tauri.localhost",
        "https://tauri.localhost",
        "tauri://localhost",
    ],
    allow_origin_regex=r"https?://tauri\.localhost(:\d+)?" if _RESONITE_TAURI else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API requests
class OSCMessageRequest(BaseModel):
    host: str
    port: int
    address: str
    values: list[Any] = []


class OSCServerRequest(BaseModel):
    port: int
    address: str = "0.0.0.0"  # noqa: S104


class OSCServerStopRequest(BaseModel):
    port: int


class ResoniteSessionRequest(BaseModel):
    session_name: str = None
    world_path: str = None
    avatar_slot: int = None


class AvatarLoadRequest(BaseModel):
    avatar_path: str
    slot: int = None
    parameters: dict[str, Any] = None


class ParameterSetRequest(BaseModel):
    parameter: str
    value: Any
    avatar_slot: int | None = None


class AvatarLocomotionRequest(BaseModel):
    type: str


class ProtoFluxExecuteRequest(BaseModel):
    script_name: str
    parameters: dict[str, Any] = None


class InventoryListRequest(BaseModel):
    item_type: str = None
    search_query: str = None
    limit: int = 50
    offset: int = 0


class InventorySpawnRequest(BaseModel):
    item_id: str
    position: list[float] = None
    rotation: list[float] = None
    scale: list[float] = None


class InventoryUploadRequest(BaseModel):
    item_path: str
    item_name: str
    item_type: str
    description: str = None
    is_public: bool = False


class InventoryDeleteRequest(BaseModel):
    item_id: str
    confirm_deletion: bool = True


class InventoryShareRequest(BaseModel):
    item_id: str
    share_with: str
    permission_level: str = "read"


class PluginLoadRequest(BaseModel):
    plugin_name: str


class PluginUnloadRequest(BaseModel):
    plugin_name: str


class PluginReloadRequest(BaseModel):
    plugin_name: str


class WorldLabsImportRequest(BaseModel):
    splat_url: str
    mesh_url: str = ""
    world_name: str = "WorldLabs_World"
    target_slot: str = "root"


class BlenderImportRequest(BaseModel):
    object_name: str
    format: str = "glb"


class UnitySyncRequest(BaseModel):
    avatar_path: str
    unity_package: str | None = None


class ControlMoveRequest(BaseModel):
    x: float
    y: float


class ControlViewRequest(BaseModel):
    view_type: str  # "first-person", "third-person", "toggle"


class FleetLaunchRequest(BaseModel):
    """Request model for launching a fleet application."""

    repo_path: str = Field(..., description="Absolute path to the repository root")


class FleetLaunchResponse(BaseModel):
    """Response model for fleet launch operation."""

    success: bool
    message: str


class MCPToolRequest(BaseModel):
    tool: str
    params: dict[str, Any] = Field(default_factory=dict)


# API Routes
@app.get("/api/v1/health")
@app.get("/api/health")
@app.get("/health")
async def health_check():
    """Health check endpoint (HEALTH_ENDPOINT_STANDARD-compliant, 2026-07-19).

    Required fields per mcp-central-docs/standards/HEALTH_ENDPOINT_STANDARD.md:
    status, server, version, git_sha, started_at, uptime_seconds,
    shutting_down, transport, port. Extra fields (capabilities,
    metrics_enabled, agent_lab_phase) kept as additions -- the standard
    says "at minimum", not "only these".
    """
    now = datetime.datetime.now(datetime.UTC)
    return {
        "status": "ok",
        "server": "resonite-mcp-sota",
        "version": __version__,
        "git_sha": _GIT_SHA,
        "started_at": _STARTED.isoformat(),
        "uptime_seconds": (now - _STARTED).total_seconds(),
        "shutting_down": _SHUTTING_DOWN["value"],
        "transport": "streamable-http",
        "port": int(os.environ.get("RESONITE_MCP_PORT", "10979")),
        "agent_lab_phase": 6,
        "metrics_enabled": metrics_enabled(),
        "capabilities": [
            "osc_communication",
            "avatar_control",
            "world_management",
            "protoflux_scripting",
            "session_management",
            "integrations",
            "fleet_orchestration",
            "agent_lab_tools",
            "marble_world_import",
            "voice_macros",
            "inventory_adapter",
        ],
    }


@app.on_event("shutdown")
async def _mark_shutting_down():
    """Flip the health endpoint's shutting_down flag (graceful-shutdown
    standard, 2026-07-13 rollout) -- best-effort, FastAPI's shutdown event
    fires before the process actually exits, giving health checks a
    window to see this."""
    _SHUTTING_DOWN["value"] = True


@app.post("/api/v1/tool")
async def api_v1_tool(body: MCPToolRequest) -> dict[str, Any]:
    """Bridge endpoint for webapp Agent Lab to invoke MCP tools over HTTP."""
    tool = body.tool
    params = dict(body.params or {})
    try:
        if tool == "resonite_fleet":
            from .tools.fleet_tools import resonite_fleet

            operation = params.pop("operation", None)
            if not operation:
                raise HTTPException(status_code=400, detail="operation required for resonite_fleet")
            result = await resonite_fleet(operation, **params)
            return {
                "success": bool(result.get("success")),
                "data": result,
                "error": result.get("error") or None,
            }
        if tool == "resonite_voice":
            from .tools.voice_tools import resonite_voice

            operation = params.pop("operation", None)
            if not operation:
                raise HTTPException(status_code=400, detail="operation required for resonite_voice")
            result = await resonite_voice(operation, **params)
            return {
                "success": bool(result.get("success")),
                "data": result,
                "error": result.get("error") or None,
            }
        if tool == "health_check":
            from .server import health_check as mcp_health_check

            result = await mcp_health_check()
            ok = result.get("status") == "success"
            return {"success": ok, "data": result, "error": None if ok else result.get("message")}
        raise HTTPException(status_code=404, detail=f"Unknown tool: {tool}")
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Tool %s failed", tool)
        return {"success": False, "error": str(exc), "data": None}


# Activity log endpoints — ported 2026-07-19 from web_sota/backend/server.py
# (which defined this same logic but was never actually launched — see
# docs/WEBAPP_UPDATE_PLAN.md). Logging.tsx's /api/logs* calls now hit real code.
@app.get("/api/logs")
async def get_logs(
    limit: int = 50,
    offset: int = 0,
    level: str | None = None,
    kind: str | None = None,
    search: str | None = None,
    sort: str = "desc",
    after_id: str | None = None,
):
    """Query the activity log."""
    return activity_log.query(
        limit=limit, offset=offset, level=level, kind=kind, search=search, sort=sort, after_id=after_id
    )


@app.get("/api/logs/stats")
async def logs_stats():
    """Get activity log statistics (counts by level/kind)."""
    return activity_log.stats()


@app.get("/api/logs/export")
async def logs_export(
    format: str = "json", level: str | None = None, kind: str | None = None, search: str | None = None
):
    """Export the activity log as JSON or CSV."""
    from fastapi.responses import Response

    content = activity_log.export(format=format, level=level, kind=kind, search=search)
    media = "text/csv" if format == "csv" else "application/json"
    return Response(
        content=content, media_type=media, headers={"Content-Disposition": f'attachment; filename="logs.{format}"'}
    )


@app.delete("/api/logs")
async def clear_logs():
    """Clear the activity log."""
    activity_log.clear()
    return {"success": True, "message": "Logs cleared."}


@app.post("/api/v1/fleet/launch", response_model=FleetLaunchResponse)
async def launch_app(request: FleetLaunchRequest) -> FleetLaunchResponse:
    """Launch another MCP app via its start.ps1 script."""
    path = Path(request.repo_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Path {request.repo_path} does not exist")

    # Security check: Ensure path is within D:/Dev/repos
    try:
        allowed_base = Path("D:/Dev/repos").resolve()
        target_path = path.resolve()
        target_path.relative_to(allowed_base)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail="Access denied: Path outside allowed directory") from exc

    start_script = path / "web_sota" / "start.ps1"
    if not start_script.exists():
        start_script = path / "web" / "start.ps1"
        if not start_script.exists():
            start_script = path / "start.ps1"
            if not start_script.exists():
                raise HTTPException(status_code=400, detail="No valid SOTA entry point found")

    try:
        powershell_path = shutil.which("powershell.exe") or "powershell.exe"
        subprocess.Popen(  # noqa: S603 -- repo_path already validated against allowed_base above
            [powershell_path, "-ExecutionPolicy", "Bypass", "-File", str(start_script)],
            cwd=str(path),
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        return FleetLaunchResponse(success=True, message=f"Launched {path.name} successfully")
    except Exception as e:
        logger.error(f"Failed to launch {path.name}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "name": "Resonite MCP Server",
        "version": "2026.2.17",
        "description": "HTTP API for Resonite social VR platform control",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/v1/health",
            "fleet": "/api/v1/fleet/*",
            "osc": "/api/osc/*",
            "resonite": "/api/resonite/*",
        },
    }


# OSC API endpoints
@app.get("/api/osc/status")
async def get_osc_status():
    """Get status of all running OSC servers."""
    try:
        from .tools.osc import get_osc_server_stats, osc_servers

        results = []
        for port in list(osc_servers.keys()):
            stats = await get_osc_server_stats(port)
            results.append(stats)

        return {"status": "success", "servers": results}
    except Exception as e:
        logger.error(f"OSC status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/osc/send")
async def send_osc_message_route(request: OSCMessageRequest):
    """Send an OSC message."""
    try:
        from .http_functions import send_osc_http

        result = await send_osc_http(request.host, request.port, request.address, request.values)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"OSC send failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/osc/server/start")
async def start_osc_server_endpoint(request: OSCServerRequest):
    """Start an OSC server."""
    try:
        from .http_functions import start_osc_server_http

        result = await start_osc_server_http(request.port, request.address)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"OSC server start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/osc/server/stop")
async def stop_osc_server_endpoint(request: OSCServerStopRequest):
    """Stop an OSC server."""
    try:
        from .http_functions import stop_osc_server_http

        result = await stop_osc_server_http(request.port)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"OSC server stop failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/osc/received")
async def get_received_messages_endpoint(
    port: int,
    address_pattern: str | None = None,
    max_age_seconds: float | None = None,
    limit: int = 100,
):
    """Get received OSC messages."""
    try:
        from .http_functions import get_received_messages_http

        result = await get_received_messages_http(port, address_pattern, max_age_seconds, limit)
        return result
    except Exception as e:
        logger.error(f"Get received messages failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/osc/clear")
async def clear_osc_buffer_endpoint(port: int):
    """Clear the OSC message buffer for a specific port."""
    try:
        from .http_functions import clear_osc_message_buffer_http

        result = await clear_osc_message_buffer_http(port)
        return result
    except Exception as e:
        logger.error(f"Clear OSC buffer failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# Resonite-specific API endpoints
@app.post("/api/resonite/session/start")
async def start_resonite_session(request: ResoniteSessionRequest):
    """Start a new Resonite session."""
    try:
        from .http_functions import resonite_session_start_http

        result = await resonite_session_start_http(request.session_name, request.world_path, request.avatar_slot)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Session start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/resonite/session/status")
async def get_session_status():
    """Get current session status."""
    try:
        from .http_functions import resonite_session_status_http

        result = await resonite_session_status_http()
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Unknown error"))
        return result
    except Exception as e:
        logger.error(f"Session status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/resonite/avatar/load")
async def load_avatar(request: AvatarLoadRequest):
    """Load an avatar."""
    try:
        from .http_functions import resonite_avatar_load_http

        result = await resonite_avatar_load_http(request.avatar_path, request.slot, request.parameters)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Avatar load failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/resonite/avatar/info")
async def get_avatar_info():
    """Get current avatar info."""
    try:
        from .http_functions import resonite_avatar_info_http

        result = await resonite_avatar_info_http()
        return result
    except Exception as e:
        logger.error(f"Avatar info failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/resonite/avatar/set_parameter")
async def set_parameter(request: ParameterSetRequest):
    """Set an avatar parameter."""
    try:
        from .http_functions import resonite_parameter_set_http

        result = await resonite_parameter_set_http(request.parameter, request.value, request.avatar_slot)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Parameter set failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/resonite/avatar/reset_pose")
async def reset_avatar_pose():
    """Reset avatar pose."""
    try:
        from .http_functions import resonite_avatar_reset_pose_http

        result = await resonite_avatar_reset_pose_http()
        return result
    except Exception as e:
        logger.error(f"Reset pose failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/resonite/avatar/locomotion")
async def set_avatar_locomotion(request: AvatarLocomotionRequest):
    """Set avatar locomotion mode."""
    try:
        from .http_functions import resonite_avatar_locomotion_http

        result = await resonite_avatar_locomotion_http(request.type)
        return result
    except Exception as e:
        logger.error(f"Locomotion set failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/resonite/avatar/kill_sequences")
async def kill_avatar_sequences():
    """Kill all avatar sequences."""
    try:
        from .http_functions import resonite_avatar_kill_sequences_http

        result = await resonite_avatar_kill_sequences_http()
        return result
    except Exception as e:
        logger.error(f"Kill sequences failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/resonite/protoflux/execute")
async def execute_protoflux(request: ProtoFluxExecuteRequest):
    """Execute a ProtoFlux script."""
    try:
        from .http_functions import resonite_protoflux_execute_http

        result = await resonite_protoflux_execute_http(request.script_name, request.parameters)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"ProtoFlux execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/resonite/world/load")
async def load_world(world_path: str):
    """Load a world."""
    try:
        from .http_functions import resonite_world_load_http

        result = await resonite_world_load_http(world_path)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"World load failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/resonite/session/end")
async def end_session():
    """End the current session."""
    try:
        from .http_functions import resonite_session_end_http

        result = await resonite_session_end_http()
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Session end failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# Platform & Status Endpoints
@app.get("/api/platform")
async def get_platform_info():
    """Get Resonite platform information."""
    from .http_functions import resonite_platform_info_http

    return await resonite_platform_info_http()


@app.get("/api/sessions")
async def list_sessions(
    name: str | None = None,
    host_name: str | None = None,
    host_id: str | None = None,
    min_active_users: int = 0,
    include_empty_headless: bool = True,
):
    """List public Resonite sessions."""
    from .http_functions import resonite_sessions_list_http

    return await resonite_sessions_list_http(
        name=name,
        host_name=host_name,
        host_id=host_id,
        min_active_users=min_active_users,
        include_empty_headless=include_empty_headless,
    )


@app.get("/api/contacts")
async def get_contacts():
    """Get Resonite contacts list."""
    try:
        from .http_functions import resonite_contacts_list_http

        result = await resonite_contacts_list_http()
        if isinstance(result, dict) and result.get("status") == "error":
            # If not authenticated, return a 401 Unauthorized
            status_code = 401 if "Not authenticated" in result.get("detail", "") else 400
            raise HTTPException(status_code=status_code, detail=result.get("detail", "Error fetching contacts"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Contacts list failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/resonite/start")
async def start_resonite():
    """Launch Resonite application."""
    from .http_functions import resonite_start_app_http

    return await resonite_start_app_http()


@app.get("/api/status")
async def get_system_status_api():
    """Get full system status."""
    from .http_functions import resonite_system_status_http

    return await resonite_system_status_http()


# Integration API endpoints
@app.post("/api/resonite/integrations/worldlabs")
async def import_worldlabs(request: WorldLabsImportRequest):
    """Import a WorldLabs splat from URL into Resonite.

    Downloads the SPZ/GLB from the bridge proxy, then imports via
    ResoniteLink (if connected) or falls back to inventory upload.
    """
    from .tools.integrations import resonite_import_worldlabs_url

    if not request.splat_url:
        raise HTTPException(status_code=400, detail="splat_url is required")

    return await resonite_import_worldlabs_url(
        splat_url=request.splat_url,
        mesh_url=request.mesh_url,
        world_name=request.world_name,
        target_slot=request.target_slot,
    )


@app.post("/api/resonite/integrations/blender")
async def import_blender(request: BlenderImportRequest):
    """Import Blender object."""
    from .tools.integrations import resonite_import_blender

    return await resonite_import_blender(request.object_name, request.format)


@app.post("/api/resonite/integrations/unity")
async def sync_unity_avatar(request: UnitySyncRequest):
    """Sync Unity avatar."""
    from .tools.integrations import resonite_avatar_unity

    return await resonite_avatar_unity(request.avatar_path, request.unity_package)


# Inventory API endpoints
@app.get("/api/resonite/inventory/list")
async def list_inventory(
    item_type: str | None = None, search_query: str | None = None, limit: int = 50, offset: int = 0
):
    """List inventory items."""
    try:
        from .http_functions import resonite_inventory_list_http

        result = await resonite_inventory_list_http(item_type, search_query, limit, offset)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Inventory list failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/resonite/inventory/search")
async def search_inventory(query: str, item_type: str | None = None):
    """Search inventory items."""
    try:
        from .http_functions import resonite_inventory_search_http

        result = await resonite_inventory_search_http(query, item_type)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Inventory search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/resonite/inventory/spawn")
async def spawn_inventory_item(request: InventorySpawnRequest):
    """Spawn an inventory item."""
    try:
        from .http_functions import resonite_inventory_spawn_http

        result = await resonite_inventory_spawn_http(request.item_id, request.position, request.rotation, request.scale)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Inventory spawn failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/resonite/inventory/upload")
async def upload_inventory_item(request: InventoryUploadRequest):
    """Upload an item to inventory."""
    try:
        from .http_functions import resonite_inventory_upload_http

        result = await resonite_inventory_upload_http(
            request.item_path,
            request.item_name,
            request.item_type,
            request.description,
            request.is_public,
        )
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Inventory upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.delete("/api/resonite/inventory/delete")
async def delete_inventory_item(request: InventoryDeleteRequest):
    """Delete an inventory item."""
    try:
        from .http_functions import resonite_inventory_delete_http

        result = await resonite_inventory_delete_http(request.item_id, request.confirm_deletion)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Inventory delete failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/resonite/inventory/share")
async def share_inventory_item(request: InventoryShareRequest):
    """Share an inventory item."""
    try:
        from .http_functions import resonite_inventory_share_http

        result = await resonite_inventory_share_http(request.item_id, request.share_with, request.permission_level)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Inventory share failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/resonite/inventory/info/{item_id}")
async def get_inventory_item_info(item_id: str):
    """Get detailed information about an inventory item."""
    try:
        from .http_functions import resonite_inventory_info_http

        result = await resonite_inventory_info_http(item_id)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Inventory info failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# Plugin management API endpoints
@app.get("/api/plugins/list")
async def list_plugins():
    """List all loaded plugins."""
    try:
        from .http_functions import plugin_list_http

        result = await plugin_list_http()
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Plugin list failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/plugins/discover")
async def discover_plugins():
    """Discover available plugins."""
    try:
        from .http_functions import plugin_discover_http

        result = await plugin_discover_http()
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Plugin discover failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/plugins/load")
async def load_plugin_endpoint(request: PluginLoadRequest):
    """Load a plugin."""
    try:
        from .http_functions import plugin_load_http

        result = await plugin_load_http(request.plugin_name)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Plugin load failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/plugins/unload")
async def unload_plugin_endpoint(request: PluginUnloadRequest):
    """Unload a plugin."""
    try:
        from .http_functions import plugin_unload_http

        result = await plugin_unload_http(request.plugin_name)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Plugin unload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/plugins/reload")
async def reload_plugin_endpoint(request: PluginReloadRequest):
    """Reload a plugin."""
    try:
        from .http_functions import plugin_reload_http

        result = await plugin_reload_http(request.plugin_name)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Plugin reload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/plugins/info")
async def get_plugin_info(plugin_name: str | None = None):
    """Get plugin information."""
    try:
        from .http_functions import plugin_info_http

        result = await plugin_info_http(plugin_name)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Plugin info failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ---------------------------------------------------------------------------
# ResoniteLink API  (WebSocket bridge — protocol 0.13.1, confirmed live
# 2026-07-18/19 against a real session; "v0.8.x" was the pre-rewrite
# fictional API version, no longer accurate — see docs/RESONITELINK_GUIDE.md)
#
# All endpoints share a single persistent ResoniteLinkClient instance.
# The client connects lazily on first use and reconnects on demand.
#
# TODO: When Resonite publishes an official local REST/HTTP API, add a
#       parallel implementation in resonite_link.py and toggle USE_REST_API=True.
# ---------------------------------------------------------------------------

# Pydantic models for ResoniteLink endpoints


class RLConnectRequest(BaseModel):
    host: str = "localhost"
    port: int = 4242


class RLWriteRequest(BaseModel):
    ref_id: str  # component ID
    member: str | None = None  # member name (Resonite inspector name) — required
    value: Any
    value_type: str | None = None  # optional protocol type ("float3", "colorX", ...)


class RLAddSlotRequest(BaseModel):
    parent_id: str
    name: str = "Slot"


class RLAddComponentRequest(BaseModel):
    slot_id: str
    component_type: str


class RLDestroyRequest(BaseModel):
    slot_id: str
    preserve_assets: bool = False


class RLBatchRequest(BaseModel):
    operations: list[dict[str, Any]]


class RLReflectRequest(BaseModel):
    component_type: str | None = None


# Module-level state for the ResoniteLink client singleton
_rl_state: dict[str, Any] = {"client": None}


# Singleton client accessor
def _get_rl_client():
    """Return (or lazily create) the module-level ResoniteLink client."""
    from .resonite_link import ResoniteLinkClient

    if _rl_state["client"] is None:
        _rl_state["client"] = ResoniteLinkClient()
    return _rl_state["client"]


# --- Connection ---


@app.post("/rl/connect")
async def rl_connect(req: RLConnectRequest):
    """Connect to ResoniteLink WebSocket in Resonite. Prefer calling
    /rl/discover first and passing its result — port 4242 is only a
    fallback default, not a guarantee (sessions announce their real
    port via UDP broadcast, discovered dynamically)."""
    from .resonite_link import ResoniteLinkClient

    client = ResoniteLinkClient(host=req.host, port=req.port)
    _rl_state["client"] = client
    ok = await client.connect()
    if not ok:
        raise HTTPException(status_code=503, detail=f"Could not connect to ResoniteLink at {req.host}:{req.port}")
    return {
        "status": "connected",
        "uri": client.uri,
        "session_info": client.session_info,
    }


@app.post("/rl/disconnect")
async def rl_disconnect():
    """Disconnect from ResoniteLink."""
    client = _get_rl_client()
    await client.disconnect()
    return {"status": "disconnected"}


@app.get("/rl/status")
async def rl_status():
    """Get ResoniteLink connection status and session info."""
    client = _get_rl_client()
    return {
        "connected": client.connected,
        "uri": client.uri,
        "session_info": client.session_info,
    }


# --- Data Model ---


@app.get("/rl/discover")
async def rl_discover(timeout_seconds: float = 12.0):
    """Discover ResoniteLink sessions on the LAN (UDP 12512, protocol 0.12.0+)."""
    from .resonite_link import discover_sessions

    try:
        sessions = await discover_sessions(timeout=timeout_seconds)
        return {"sessions": sessions, "count": len(sessions)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/rl/field/{ref_id}")
async def rl_read_field(ref_id: str):
    """Read a component's data (type + members) by component ID."""
    client = _get_rl_client()
    try:
        value = await client.get_component(ref_id)
        return {"ref_id": ref_id, "value": value}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/rl/field")
async def rl_write_field(req: RLWriteRequest):
    """Write one member on a component (updateComponent). Requires 'member'."""
    if not req.member:
        raise HTTPException(
            status_code=422,
            detail="'member' is required: ResoniteLink writes component members, not bare field refs.",
        )
    client = _get_rl_client()
    try:
        resp = await client.set_component_value(req.ref_id, req.member, req.value, req.value_type)
        return {"status": "ok", "response": resp}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/rl/node/{ref_id}")
async def rl_get_node(ref_id: str):
    """Get slot or component info by ref ID."""
    client = _get_rl_client()
    try:
        return await client.get_node(ref_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/rl/children/{slot_id}")
async def rl_get_children(slot_id: str):
    """List direct children of a slot."""
    client = _get_rl_client()
    try:
        children = await client.get_children(slot_id)
        return {"slot_id": slot_id, "children": children}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/rl/slot")
async def rl_add_slot(req: RLAddSlotRequest):
    """Add a named child slot under a parent slot."""
    client = _get_rl_client()
    try:
        new_id = await client.add_slot(req.parent_id, req.name)
        return {"status": "ok", "ref_id": new_id, "name": req.name}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/rl/component")
async def rl_add_component(req: RLAddComponentRequest):
    """Add a component to a slot. component_type is the fully-qualified C# type name."""
    client = _get_rl_client()
    try:
        new_id = await client.add_component(req.slot_id, req.component_type)
        return {"status": "ok", "ref_id": new_id, "component_type": req.component_type}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


class RLUpdateSlotRequest(BaseModel):
    """Partial slot update — include only the fields you want to change.
    Real, working (client.update_slot()) — unlike /rl/world/write-field,
    which the protocol has no equivalent for."""

    name: str | None = None
    position: dict[str, float] | None = None
    rotation: dict[str, float] | None = None
    scale: dict[str, float] | None = None


@app.patch("/rl/slot/{slot_id}")
async def rl_update_slot(slot_id: str, req: RLUpdateSlotRequest):
    """Update a slot's name/position/rotation/scale. Only send fields you want changed."""
    from .resonite_link import rl_value

    client = _get_rl_client()
    data: dict[str, Any] = {"id": slot_id}
    if req.name is not None:
        data["name"] = rl_value("string", req.name)
    if req.position is not None:
        data["position"] = rl_value("float3", req.position)
    if req.rotation is not None:
        data["rotation"] = rl_value("floatQ", req.rotation)
    if req.scale is not None:
        data["scale"] = rl_value("float3", req.scale)
    try:
        resp = await client.update_slot(data)
        return {"status": "ok", "response": resp}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.delete("/rl/slot/{slot_id}")
async def rl_destroy_slot(slot_id: str, preserve_assets: bool = False):
    """Destroy a slot and all its children."""
    client = _get_rl_client()
    try:
        resp = await client.destroy_slot(slot_id, preserve_assets)
        return {"status": "ok", "response": resp}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/rl/batch")
async def rl_batch(req: RLBatchRequest):
    """Execute multiple ResoniteLink operations atomically (dataModelOperationBatch, protocol 0.13.1)."""
    client = _get_rl_client()
    try:
        results = await client.batch(req.operations)
        return {"status": "ok", "results": results}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/rl/reflect")
async def rl_reflect(req: RLReflectRequest):
    """
    Reflection API (protocol 0.13.1).
    Without component_type: list all supported component types.
    With component_type: list all fields/members for that type.
    """
    client = _get_rl_client()
    try:
        return await client.reflect(req.component_type)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Resonite Cloud API proxy  (unauthenticated public endpoints)
# ---------------------------------------------------------------------------

RESONITE_API_BASE = "https://api.resonite.com"


@app.get("/api/resonite/cloud-sessions")
async def list_cloud_sessions(
    name: str = Query("", description="Filter by session name"),
    host: str = Query("", description="Filter by host username"),
    min_active_users: int = Query(0, alias="minActiveUsers"),
    include_empty_headless: bool = Query(True, alias="includeEmptyHeadless"),
):
    """
    Proxy to api.resonite.com/sessions — returns public world sessions.
    No authentication required.
    """
    params: dict[str, Any] = {"minActiveUsers": min_active_users}
    if name:
        params["name"] = name
    if host:
        params["hostName"] = host
    if not include_empty_headless:
        params["includeEmptyHeadless"] = False
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{RESONITE_API_BASE}/sessions", params=params)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"Resonite API error: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not reach Resonite API: {exc}") from exc


@app.get("/api/resonite/cloud-sessions/{session_id}")
async def get_cloud_session(session_id: str):
    """Get full metadata for a specific public session."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{RESONITE_API_BASE}/sessions/{session_id}")
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"Resonite API error: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not reach Resonite API: {exc}") from exc


# ---------------------------------------------------------------------------
# World Inspector shortcuts  (thin wrappers around existing /rl/* routes)
# ---------------------------------------------------------------------------


@app.get("/rl/world/root")
async def world_root():
    """Get the Root slot of the currently connected Resonite world."""
    client = _get_rl_client()
    if not client.connected:
        raise HTTPException(status_code=503, detail="Not connected to ResoniteLink")
    try:
        return await client.get_node("Root")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/rl/world/children/{slot_id}")
async def world_children(slot_id: str):
    """List direct children of any slot (use 'Root' for top level)."""
    client = _get_rl_client()
    if not client.connected:
        raise HTTPException(status_code=503, detail="Not connected to ResoniteLink")
    try:
        children = await client.get_children(slot_id)
        return {"slot_id": slot_id, "children": children}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/rl/world/node/{ref_id}")
async def world_node(ref_id: str):
    """Get full slot/component data by ref ID."""
    client = _get_rl_client()
    if not client.connected:
        raise HTTPException(status_code=503, detail="Not connected to ResoniteLink")
    try:
        return await client.get_node(ref_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# VRM Avatar Injection
#
# Canonical VRM directory: ~/.avatarmcp/models/
# This is the same directory used by avatar-mcp's VRMManager.
# Other tools (vrchat-mcp, blender-mcp) should also use this location.
# ---------------------------------------------------------------------------

VRM_DIR = Path.home() / ".avatarmcp" / "models"

# Canonical asset root — shared across all MCP servers that deal with 3D content.
# Subdirectories map to categories: props/, furniture/, architecture/, avatars/
# avatars/ symlinks/mirrors ~/.avatarmcp/models/ for convenience.
ASSET_ROOT = Path.home() / "Documents" / "ResoniteAssets"

_3D_EXTS = {".vrm", ".fbx", ".obj", ".glb", ".gltf", ".blend", ".dae", ".3ds", ".ply", ".splat"}

ASSET_CATEGORIES = {
    "avatars": VRM_DIR,  # ~/.avatarmcp/models/
    "props": ASSET_ROOT / "props",
    "furniture": ASSET_ROOT / "furniture",
    "architecture": ASSET_ROOT / "architecture",
    "misc": ASSET_ROOT / "misc",
}


class RLWorldWriteFieldRequest(BaseModel):
    ref_id: str
    value: Any
    value_type: str | None = None


@app.post("/rl/world/write-field")
async def world_write_field(req: RLWorldWriteFieldRequest):
    """Update a specific field/property in Resonite."""
    client = _get_rl_client()
    try:
        resp = await client.write_field(req.ref_id, req.value, req.value_type)
        return {"status": "ok", "response": resp}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/rl/world/inject-file")
async def inject_file(
    file: UploadFile = File(...),
    target_slot: str = Form("Root"),
    pos_x: float = Form(0.0),
    pos_y: float = Form(0.0),
    pos_z: float = Form(0.0),
):
    """Directly inject a file from the browser into the Resonite world."""
    client = _get_rl_client()
    if not client.connected:
        raise HTTPException(status_code=503, detail="Not connected to ResoniteLink")

    # 1. Save to a temporary location
    temp_dir = Path(tempfile.gettempdir()) / "resonite_mcp_inject"
    temp_dir.mkdir(exist_ok=True)

    # Use a unique name to avoid collisions
    timestamp = int(time.time())
    safe_filename = f"{timestamp}_{file.filename}"
    temp_path = temp_dir / safe_filename

    try:
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Generic model import is NOT supported by ResoniteLink (verified
        # against protocol 0.13.1: only texture/mesh-JSON/audio imports exist).
        # Fail honestly instead of sending a fictional message.
        raise HTTPException(
            status_code=501,
            detail=(
                "not_implemented: ResoniteLink (0.13.1) has no generic file import. "
                "Model import must be done in-game; a future importMeshJSON "
                "conversion pipeline may cover glTF/GLB."
            ),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"File injection failed: {exc}") from exc
    finally:
        # Clean up the temporary file after import attempt
        if temp_path.exists():
            temp_path.unlink()


@app.get("/rl/world/asset-files")
async def list_asset_files(category: str = "avatars"):
    """
    Scan the canonical asset directory for a given category.

    Categories:
      avatars      → ~/.avatarmcp/models/           (VRM only)
      props        → ~/Documents/ResoniteAssets/props/
      furniture    → ~/Documents/ResoniteAssets/furniture/
      architecture → ~/Documents/ResoniteAssets/architecture/
      misc         → ~/Documents/ResoniteAssets/misc/

    Returns files matching 3D formats: .vrm .fbx .obj .glb .gltf .blend .dae .ply
    """
    if category not in ASSET_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown category '{category}'. Valid: {list(ASSET_CATEGORIES)}",
        )
    scan_dir = ASSET_CATEGORIES[category]
    scan_dir.mkdir(parents=True, exist_ok=True)

    files = []
    for f in sorted(scan_dir.rglob("*")):
        if f.suffix.lower() in _3D_EXTS and f.is_file():
            try:
                rel = str(f.relative_to(scan_dir))
            except ValueError:
                rel = f.name
            files.append(
                {
                    "name": f.stem,
                    "filename": f.name,
                    "path": str(f),
                    "extension": f.suffix.lower().lstrip("."),
                    "size_bytes": f.stat().st_size,
                    "relative": rel,
                    "category": category,
                }
            )

    return {
        "category": category,
        "scan_dir": str(scan_dir),
        "files": files,
        "all_categories": list(ASSET_CATEGORIES.keys()),
    }


class VRMImportRequest(BaseModel):
    file_path: str  # absolute path to .vrm on the Resonite host machine
    target_slot: str = "Root"  # slot to parent the avatar under
    position: dict[str, float] = {"x": 0.0, "y": 0.0, "z": 0.0}


@app.get("/rl/world/vrm-files")
async def list_vrm_files():
    """
    Scan ~/.avatarmcp/models/ for .vrm files.
    Returns list of {name, path, size_bytes} objects.
    Canonical VRM dir shared across avatar-mcp, resonite-mcp, vrchat-mcp.
    """
    VRM_DIR.mkdir(parents=True, exist_ok=True)
    vrm_files = []
    for f in sorted(VRM_DIR.rglob("*.vrm")):
        vrm_files.append(
            {
                "name": f.stem,
                "filename": f.name,
                "path": str(f),
                "size_bytes": f.stat().st_size,
                "relative": str(f.relative_to(VRM_DIR)),
            }
        )
    return {"vrm_dir": str(VRM_DIR), "files": vrm_files}


@app.post("/rl/world/import-vrm")
async def import_vrm(req: VRMImportRequest):
    """
    Inject a VRM avatar into the connected world.

    NOT IMPLEMENTED: ResoniteLink (protocol 0.13.1) has no generic model/file
    import. This endpoint validates the file, then returns 501 honestly.
    """
    client = _get_rl_client()
    if not client.connected:
        raise HTTPException(status_code=503, detail="Not connected to ResoniteLink")

    # Verify file exists on this machine (same as Resonite host in local dev)
    vrm_path = Path(req.file_path)
    if not vrm_path.exists():
        raise HTTPException(status_code=404, detail=f"VRM file not found: {req.file_path}")
    if vrm_path.suffix.lower() != ".vrm":
        raise HTTPException(status_code=400, detail="File must be a .vrm file")

    # ResoniteLink (0.13.1) has no generic file import — VRM injection over the
    # link is not possible. Fail honestly (Implementation Honesty standard).
    raise HTTPException(
        status_code=501,
        detail=(
            "not_implemented: ResoniteLink (0.13.1) cannot import VRM/model files "
            f"('{vrm_path.name}' validated OK). Import in-game, or track upstream "
            "for model-import support."
        ),
    )


# ---------------------------------------------------------------------------
# Control & Mapping (Phase 8)
# ---------------------------------------------------------------------------


@app.post("/api/control/move")
async def control_move(req: ControlMoveRequest):
    """
    Control avatar movement.
    Sends OSC messages to Resonite (typically localhost:9000).
    Requires 'MoveX' and 'MoveY' parameters to be set up in the avatar via ProtoFlux or Avatar Rig.
    """
    try:
        from .tools.avatar import resonite_parameter_set

        # Set MoveX (X-axis joystick)
        await resonite_parameter_set("MoveX", req.x)
        # Set MoveY (Y-axis joystick)
        await resonite_parameter_set("MoveY", req.y)

        return {"status": "ok", "x": req.x, "y": req.y}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/control/view")
async def control_view(req: ControlViewRequest):
    """
    Toggle first/third person view.
    Requires 'ThirdPerson' parameter in the avatar.
    """
    try:
        from .tools.avatar import resonite_parameter_set

        # Toggle or set specific view
        # If 'toggle', we might need to read the current state first,
        # but for now we'll assume the frontend tracks it or we just set specific values.
        val = 1.0 if req.view_type == "third-person" else 0.0
        await resonite_parameter_set("ThirdPerson", val)

        return {"status": "ok", "view_type": req.view_type}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/world/map-data")
async def world_map_data():
    """
    Get spatial data for 2D map visualization.
    Scans the world for active users and important slots.
    """
    client = _get_rl_client()
    if not client.connected:
        return {"status": "ok", "nodes": [], "connected": False}

    try:
        # Attempt to get children of the Root slot
        # This gives us a coarse map of everything in the world
        children = await client.get_children("Root")
        nodes = []

        for child in children:
            # Basic heuristic: names containing 'User' or certain patterns are likely avatars
            name = child.get("name", "Unknown")
            is_avatar = "User" in name or name.startswith("[")  # Common user tag patterns

            nodes.append(
                {
                    "id": child.get("id"),
                    "name": name,
                    "position": child.get("position", {"x": 0, "y": 0, "z": 0}),
                    "type": "avatar" if is_avatar else "object",
                }
            )

        return {"status": "ok", "nodes": nodes, "connected": True}
    except Exception as exc:
        logger.error(f"Map data fetch failed: {exc}")
        return {"status": "error", "message": f"Could not fetch map data: {exc}"}


# ---------------------------------------------------------------------------
# WorldLabs import OSC receiver
# ---------------------------------------------------------------------------

_worldlabs_osc_server: Any = None


@app.post("/api/resonite/worldlabs/listen")
async def start_worldlabs_listener() -> dict:
    """Start an OSC server that listens for /worldlabs/import messages.

    When Resonite sends an OSC message to this server, it automatically
    triggers the import pipeline (download → ResoniteLink → confirm).
    """
    global _worldlabs_osc_server
    try:
        from pythonosc import dispatchers, osc_server

        from .tools.integrations import resonite_import_worldlabs_url

        dispatcher = dispatchers.Dispatcher()
        dispatcher.map("/worldlabs/import", lambda *args: None)

        async def handle_import(address: str, *values: Any):
            splat_url = str(values[0]) if len(values) > 0 else ""
            mesh_url = str(values[1]) if len(values) > 1 else ""
            world_name = str(values[2]) if len(values) > 2 else "Imported"
            logger.info(f"OSC /worldlabs/import: {world_name}")
            try:
                await resonite_import_worldlabs_url(splat_url, mesh_url, world_name)
            except Exception as e:
                logger.error(f"Auto-import failed: {e}")

        dispatcher.map("/worldlabs/import", handle_import)

        server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 9001), dispatcher)
        import threading

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        _worldlabs_osc_server = server
        return {"status": "ok", "port": 9001, "address": "/worldlabs/import"}
    except ImportError:
        return {"status": "error", "detail": "python-osc not installed. Run: pip install python-osc"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.post("/api/resonite/worldlabs/stop")
async def stop_worldlabs_listener() -> dict:
    """Stop the WorldLabs import OSC receiver."""
    global _worldlabs_osc_server
    if _worldlabs_osc_server:
        _worldlabs_osc_server.shutdown()
        _worldlabs_osc_server = None
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Resonite platform detection (Steam vs Standalone)
# ---------------------------------------------------------------------------


@app.get("/api/resonite/platform")
async def detect_resonite_platform() -> dict:
    """Detect Resonite installation and running status.

    Checks for both Steam and standalone (store) versions.
    """
    import os
    import platform as pf

    result = {
        "running": False,
        "installations": [],
    }

    steam_paths = []
    standalone_paths = []

    if pf.system() == "Windows":
        # Steam
        steam_base = os.path.expandvars(r"%PROGRAMFILES(X86)%\Steam\steamapps\common")
        steam_paths = [
            os.path.join(steam_base, "Resonite", "Resonite.exe"),
            os.path.join(steam_base, "Resonite", "Resonite_x86.exe"),
        ]
        # Standalone (Store)
        appdata = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Resonite")
        standalone_paths = [
            os.path.join(appdata, "Resonite.exe"),
        ]

    for path in steam_paths + standalone_paths:
        exists = os.path.isfile(path)
        source = "steam" if path in steam_paths else "standalone"
        result["installations"].append(
            {
                "path": path,
                "exists": exists,
                "source": source,
                "running": False,
            }
        )

    # Check if Resonite is currently running
    try:
        import psutil

        for proc in psutil.process_iter(["name", "exe"]):
            name = (proc.info.get("name") or "").lower()
            if "resonite" in name:
                result["running"] = True
                for inst in result["installations"]:
                    exe = (proc.info.get("exe") or "").lower()
                    if inst["path"].lower() == exe:
                        inst["running"] = True
                        inst["pid"] = proc.info.get("pid")
    except ImportError:
        pass

    return result


# ---------------------------------------------------------------------------
# ProtoFlux graph template for Resonite-side OSC receiver
# ---------------------------------------------------------------------------


@app.get("/api/resonite/worldlabs/protoflux")
async def get_protoflux_graph() -> dict:
    """Return a JSON representation of a ProtoFlux graph that listens for
    /worldlabs/import OSC messages and imports splats into Resonite.

    This can be loaded into Resonite via the ProtoFlux editor to set up
    the automated import pipeline.
    """
    return {
        "graph": {
            "name": "WorldLabs Import Receiver",
            "description": (
                "Listens for OSC messages at /worldlabs/import and imports "
                "Gaussian splats into the Resonite world. Compatible with "
                "worldlabs-mcp's Resonite export feature."
            ),
            "nodes": [
                {
                    "id": "osc-input",
                    "type": "OSCDataInput",
                    "params": {
                        "address": "/worldlabs/import",
                        "port": 9000,
                        "type_hint": "string",
                    },
                },
                {
                    "id": "string-split",
                    "type": "StringSplit",
                    "params": {"delimiter": ","},
                    "inputs": {"input": {"node": "osc-input", "output": "value"}},
                },
                {
                    "id": "http-get",
                    "type": "HttpGet",
                    "inputs": {
                        "url": {"node": "string-split", "output": "output[0]"},
                    },
                },
                {
                    "id": "import-splat",
                    "type": "ImportSplat",
                    "inputs": {
                        "data": {"node": "http-get", "output": "response"},
                        "slot": {"value": "root"},
                    },
                },
            ],
        },
        "notes": (
            "This ProtoFlux graph listens on port 9000 for OSC messages at "
            "/worldlabs/import. The message should contain 3 strings: "
            "splat_url, mesh_url, world_name. The graph fetches the splat "
            "via HTTP GET and imports it into the root slot.\n\n"
            "To set up:\n"
            "1. Open Resonite\n"
            "2. Open the ProtoFlux editor\n"
            "3. Create a new graph\n"
            "4. Add an OSCDataInput node (address: /worldlabs/import, port: 9000)\n"
            "5. Connect it to a StringSplit node (delimiter: comma)\n"
            "6. Connect output[0] to an HttpGet node\n"
            "7. Connect the response to an ImportSplat node\n"
            "8. Save the graph as a reusable asset"
        ),
    }


# ---------------------------------------------------------------------------
# vBot OSC receiver (teleoperator vBoomy / vMechazilla loop)
# ---------------------------------------------------------------------------


@app.get("/api/resonite/vbot/types")
async def list_vbot_types_route() -> dict:
    """Catalog of creative virtual robot types sharing the fleet OSC contract."""
    from .utils.vbot_osc_receiver import list_vbot_types

    return list_vbot_types()


@app.get("/api/resonite/vbot/receiver")
async def get_vbot_receiver_spec(
    robot_id: str = Query(default="vbot_yahboom_01"),
    robot_type: str = Query(default="yahboom"),
    osc_port: int = Query(default=9000, ge=1, le=65535),
) -> dict:
    """ProtoFlux receiver build spec for in-world vBot OSC (robotics-mcp → Resonite)."""
    from .utils.vbot_osc_receiver import get_vbot_receiver_spec

    return get_vbot_receiver_spec(robot_id=robot_id, robot_type=robot_type, osc_port=osc_port)


@app.post("/api/resonite/vbot/test")
async def test_vbot_receiver(
    robot_id: str = Query(default="vbot_yahboom_01"),
    robot_type: str = Query(default="yahboom"),
    host: str = Query(default="127.0.0.1"),
    osc_port: int = Query(default=9000, ge=1, le=65535),
) -> dict:
    """Fire spawn + move + head + stop OSC sequence (Resonite must be listening)."""
    from .http_functions import send_osc_http
    from .utils.vbot_osc_receiver import get_vbot_receiver_spec

    spec = get_vbot_receiver_spec(robot_id=robot_id, robot_type=robot_type, osc_port=osc_port)
    results: list[dict] = []
    for step in spec["test_sequence"]:
        osc_result = await send_osc_http(host, osc_port, step["address"], step["values"])
        results.append({"address": step["address"], "values": step["values"], **osc_result})

    return {
        "status": "success",
        "robot_id": robot_id,
        "robot_type": robot_type,
        "host": host,
        "osc_port": osc_port,
        "steps": results,
        "message": "OSC test sequence sent — verify motion in Resonite if receiver graph is wired.",
    }
