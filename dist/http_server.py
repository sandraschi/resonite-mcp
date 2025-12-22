#!/usr/bin/env python3
"""HTTP server for Resonite MCP - FastAPI interface for web-based control."""

import logging
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .server import server

# Configure logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Resonite MCP Server",
    description="HTTP API for Resonite social VR platform control",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
    parameter_name: str
    value: float
    avatar_slot: int = None

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

# API Routes
@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "name": "Resonite MCP Server",
        "version": "0.1.0",
        "description": "HTTP API for Resonite social VR platform control",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "osc": "/osc/*",
            "resonite": "/resonite/*"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server": "Resonite MCP",
        "version": "0.1.0",
        "capabilities": [
            "osc_communication",
            "avatar_control",
            "world_management",
            "protoflux_scripting",
            "session_management"
        ]
    }

# OSC API endpoints
@app.post("/osc/send")
async def send_osc_message(request: OSCMessageRequest):
    """Send an OSC message."""
    try:
        from .server import send_osc
        result = await send_osc(
            request.host,
            request.port,
            request.address,
            request.values
        )
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"OSC send failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/osc/server/start")
async def start_osc_server_endpoint(request: OSCServerRequest):
    """Start an OSC server."""
    try:
        from .server import start_osc_server
        result = await start_osc_server(request.port, request.address)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"OSC server start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/osc/server/stop")
async def stop_osc_server_endpoint(request: OSCServerStopRequest):
    """Stop an OSC server."""
    try:
        from .server import stop_osc_server
        result = await stop_osc_server(request.port)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"OSC server stop failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Resonite-specific API endpoints
@app.post("/resonite/session/start")
async def start_resonite_session(request: ResoniteSessionRequest):
    """Start a new Resonite session."""
    try:
        from .server import resonite_session_start
        result = await resonite_session_start(
            request.session_name,
            request.world_path,
            request.avatar_slot
        )
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Session start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/resonite/session/status")
async def get_session_status():
    """Get current session status."""
    try:
        from .server import resonite_session_status
        result = await resonite_session_status()
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Session status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/resonite/avatar/load")
async def load_avatar(request: AvatarLoadRequest):
    """Load an avatar."""
    try:
        from .server import resonite_avatar_load
        result = await resonite_avatar_load(
            request.avatar_path,
            request.slot,
            request.parameters
        )
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Avatar load failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/resonite/parameter/set")
async def set_parameter(request: ParameterSetRequest):
    """Set an avatar parameter."""
    try:
        from .server import resonite_parameter_set
        result = await resonite_parameter_set(
            request.parameter_name,
            request.value,
            request.avatar_slot
        )
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Parameter set failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/resonite/protoflux/execute")
async def execute_protoflux(request: ProtoFluxExecuteRequest):
    """Execute a ProtoFlux script."""
    try:
        from .server import resonite_protoflux_execute
        result = await resonite_protoflux_execute(
            request.script_name,
            request.parameters
        )
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"ProtoFlux execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/resonite/world/load")
async def load_world(world_path: str):
    """Load a world."""
    try:
        from .server import resonite_world_load
        result = await resonite_world_load(world_path)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"World load failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/resonite/session/end")
async def end_session():
    """End the current session."""
    try:
        from .server import resonite_session_end
        result = await resonite_session_end()
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Session end failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Inventory API endpoints
@app.get("/resonite/inventory/list")
async def list_inventory(
    item_type: str = None,
    search_query: str = None,
    limit: int = 50,
    offset: int = 0
):
    """List inventory items."""
    try:
        from .server import resonite_inventory_list
        result = await resonite_inventory_list(item_type, search_query, limit, offset)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Inventory list failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/resonite/inventory/search")
async def search_inventory(query: str, item_type: str = None):
    """Search inventory items."""
    try:
        from .server import resonite_inventory_search
        result = await resonite_inventory_search(query, item_type)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Inventory search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/resonite/inventory/spawn")
async def spawn_inventory_item(request: InventorySpawnRequest):
    """Spawn an inventory item."""
    try:
        from .server import resonite_inventory_spawn
        result = await resonite_inventory_spawn(
            request.item_id,
            request.position,
            request.rotation,
            request.scale
        )
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Inventory spawn failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/resonite/inventory/upload")
async def upload_inventory_item(request: InventoryUploadRequest):
    """Upload an item to inventory."""
    try:
        from .server import resonite_inventory_upload
        result = await resonite_inventory_upload(
            request.item_path,
            request.item_name,
            request.item_type,
            request.description,
            request.is_public
        )
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Inventory upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/resonite/inventory/delete")
async def delete_inventory_item(request: InventoryDeleteRequest):
    """Delete an inventory item."""
    try:
        from .server import resonite_inventory_delete
        result = await resonite_inventory_delete(
            request.item_id,
            request.confirm_deletion
        )
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Inventory delete failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/resonite/inventory/share")
async def share_inventory_item(request: InventoryShareRequest):
    """Share an inventory item."""
    try:
        from .server import resonite_inventory_share
        result = await resonite_inventory_share(
            request.item_id,
            request.share_with,
            request.permission_level
        )
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Inventory share failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/resonite/inventory/info/{item_id}")
async def get_inventory_item_info(item_id: str):
    """Get detailed information about an inventory item."""
    try:
        from .server import resonite_inventory_info
        result = await resonite_inventory_info(item_id)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Inventory info failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Plugin management API endpoints
@app.get("/plugins/list")
async def list_plugins():
    """List all loaded plugins."""
    try:
        from .server import plugin_list
        result = await plugin_list()
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Plugin list failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/plugins/discover")
async def discover_plugins():
    """Discover available plugins."""
    try:
        from .server import plugin_discover
        result = await plugin_discover()
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Plugin discover failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/plugins/load")
async def load_plugin_endpoint(request: PluginLoadRequest):
    """Load a plugin."""
    try:
        from .server import plugin_load
        result = await plugin_load(request.plugin_name)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Plugin load failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/plugins/unload")
async def unload_plugin_endpoint(request: PluginUnloadRequest):
    """Unload a plugin."""
    try:
        from .server import plugin_unload
        result = await plugin_unload(request.plugin_name)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Plugin unload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/plugins/reload")
async def reload_plugin_endpoint(request: PluginReloadRequest):
    """Reload a plugin."""
    try:
        from .server import plugin_reload
        result = await plugin_reload(request.plugin_name)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Plugin reload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/plugins/info")
async def get_plugin_info(plugin_name: str = None):
    """Get plugin information."""
    try:
        from .server import plugin_info
        result = await plugin_info(plugin_name)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Plugin info failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
