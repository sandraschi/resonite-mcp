#!/usr/bin/env python3
"""HTTP server for Resonite MCP - FastAPI interface for web-based control."""

import logging
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import subprocess

# Functions will be imported inside endpoints to avoid tool wrapping

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Resonite MCP Server",
    description="HTTP API for Resonite social VR platform control",
    version="0.7.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API requests
class OSCMessageRequest(BaseModel):
    host: str
    port: int
    address: str
    values: List[Any] = []


class OSCServerRequest(BaseModel):
    port: int
    address: str = "0.0.0.0"


class OSCServerStopRequest(BaseModel):
    port: int


class ResoniteSessionRequest(BaseModel):
    session_name: str = None
    world_path: str = None
    avatar_slot: int = None


class AvatarLoadRequest(BaseModel):
    avatar_path: str
    slot: int = None
    parameters: Dict[str, Any] = None


class ParameterSetRequest(BaseModel):
    parameter: str
    value: Any
    avatar_slot: Optional[int] = None


class AvatarLocomotionRequest(BaseModel):
    type: str


class ProtoFluxExecuteRequest(BaseModel):
    script_name: str
    parameters: Dict[str, Any] = None


class InventoryListRequest(BaseModel):
    item_type: str = None
    search_query: str = None
    limit: int = 50
    offset: int = 0


class InventorySpawnRequest(BaseModel):
    item_id: str
    position: List[float] = None
    rotation: List[float] = None
    scale: List[float] = None


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
    unity_package: Optional[str] = None


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
    params: Dict[str, Any] = Field(default_factory=dict)


# API Routes
@app.get("/api/v1/health")
@app.get("/api/health")
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "server": "resonite-mcp-sota",
        "version": "0.7.0",
        "agent_lab_phase": 3,
        "capabilities": [
            "osc_communication",
            "avatar_control",
            "world_management",
            "protoflux_scripting",
            "session_management",
            "integrations",
            "fleet_orchestration",
            "agent_lab_tools",
        ],
    }


@app.post("/api/v1/tool")
async def api_v1_tool(body: MCPToolRequest) -> Dict[str, Any]:
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
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied: Path outside allowed directory")

    start_script = path / "web_sota" / "start.ps1"
    if not start_script.exists():
        start_script = path / "web" / "start.ps1"
        if not start_script.exists():
            start_script = path / "start.ps1"
            if not start_script.exists():
                raise HTTPException(status_code=400, detail="No valid SOTA entry point found")

    try:
        subprocess.Popen(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(start_script)],
            cwd=str(path),
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        return FleetLaunchResponse(success=True, message=f"Launched {path.name} successfully")
    except Exception as e:
        logger.error(f"Failed to launch {path.name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
        from .tools.osc import osc_servers, get_osc_server_stats

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
    address_pattern: Optional[str] = None,
    max_age_seconds: Optional[float] = None,
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

        result = await resonite_session_start_http(
            request.session_name, request.world_path, request.avatar_slot
        )
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

        result = await resonite_avatar_load_http(
            request.avatar_path, request.slot, request.parameters
        )
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

        result = await resonite_parameter_set_http(
            request.parameter, request.value, request.avatar_slot
        )
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
    name: str = None,
    host_name: str = None,
    host_id: str = None,
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
    item_type: str = None, search_query: str = None, limit: int = 50, offset: int = 0
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
async def search_inventory(query: str, item_type: str = None):
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

        result = await resonite_inventory_spawn_http(
            request.item_id, request.position, request.rotation, request.scale
        )
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

        result = await resonite_inventory_share_http(
            request.item_id, request.share_with, request.permission_level
        )
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
async def get_plugin_info(plugin_name: str = None):
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
# ResoniteLink API  (WebSocket bridge — official protocol v0.8.x)
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
    ref_id: str
    value: Any
    value_type: Optional[str] = None


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
    operations: List[Dict[str, Any]]


class RLReflectRequest(BaseModel):
    component_type: Optional[str] = None


# Module-level state for the ResoniteLink client singleton
_rl_state: Dict[str, Any] = {"client": None}


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
    """Connect to ResoniteLink WebSocket in Resonite (port 4242 default)."""
    from .resonite_link import ResoniteLinkClient

    client = ResoniteLinkClient(host=req.host, port=req.port)
    _rl_state["client"] = client
    ok = await client.connect()
    if not ok:
        raise HTTPException(
            status_code=503, detail=f"Could not connect to ResoniteLink at {req.host}:{req.port}"
        )
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


@app.get("/rl/field/{ref_id}")
async def rl_read_field(ref_id: str):
    """Read a field value by its ResoniteLink ref ID."""
    client = _get_rl_client()
    try:
        value = await client.read_field(ref_id)
        return {"ref_id": ref_id, "value": value}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/rl/field")
async def rl_write_field(req: RLWriteRequest):
    """Write a value to a field by its ref ID."""
    client = _get_rl_client()
    try:
        resp = await client.write_field(req.ref_id, req.value, req.value_type)
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
    """Execute multiple ResoniteLink operations atomically (v0.8.3+ batch support)."""
    client = _get_rl_client()
    try:
        results = await client.batch(req.operations)
        return {"status": "ok", "results": results}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/rl/reflect")
async def rl_reflect(req: RLReflectRequest):
    """
    Reflection API (v0.8.3+).
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


@app.get("/api/sessions")
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
    params: Dict[str, Any] = {"minActiveUsers": min_active_users}
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
        raise HTTPException(
            status_code=exc.response.status_code, detail=f"Resonite API error: {exc}"
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not reach Resonite API: {exc}") from exc


@app.get("/api/sessions/{session_id}")
async def get_cloud_session(session_id: str):
    """Get full metadata for a specific public session."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{RESONITE_API_BASE}/sessions/{session_id}")
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, detail=f"Resonite API error: {exc}"
        ) from exc
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


class RLWriteRequest(BaseModel):
    ref_id: str
    value: Any
    value_type: Optional[str] = None


@app.post("/rl/world/write-field")
async def world_write_field(req: RLWriteRequest):
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

        # 2. Trigger the import via ResoniteLink
        # We use the absolute path so Resonite can find it on the local disk
        payload = {
            "type": "importFile",
            "filePath": str(temp_path),
            "targetSlotId": target_slot,
            "position": {"x": pos_x, "y": pos_y, "z": pos_z},
        }

        resp = await client._send(payload)

        return {
            "status": "ok",
            "filename": file.filename,
            "temp_path": str(temp_path),
            "target_slot": target_slot,
            "response": resp,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"File injection failed (requires Resonite build ≥ 2026.1.8.6): {exc}",
        ) from exc
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
    position: Dict[str, float] = {"x": 0.0, "y": 0.0, "z": 0.0}


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
    Inject a VRM avatar into the connected world via ResoniteLink importFile
    (available in Resonite build 2026.1.8.6+).

    The file_path must be accessible on the machine running Resonite.
    For local dev setups this is the same machine as the backend.
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

    try:
        resp = await client._send(
            {
                "type": "importFile",
                "filePath": str(vrm_path),
                "targetSlotId": req.target_slot,
                "position": req.position,
            }
        )
        return {"status": "ok", "response": resp}
    except Exception as exc:
        # importFile may not be supported in older builds — surface the error clearly
        raise HTTPException(
            status_code=400,
            detail=f"VRM import failed (requires Resonite build ≥ 2026.1.8.6): {exc}",
        ) from exc


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
        result["installations"].append({
            "path": path,
            "exists": exists,
            "source": source,
            "running": False,
        })

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

