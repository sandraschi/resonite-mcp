# Resonite MCP API Reference

Complete reference for all Resonite MCP server tools and HTTP endpoints.

## Table of Contents

- [OSC Communication Tools](#osc-communication-tools)
- [Resonite Session Management](#resonite-session-management)
- [Avatar Control](#avatar-control)
- [World Management](#world-management)
- [ProtoFlux Scripting](#protoflux-scripting)
- [Inventory Management](#inventory-management)
- [Plugin Management](#plugin-management)
- [HTTP API Endpoints](#http-api-endpoints)

## OSC Communication Tools

Low-level OSC protocol tools for direct communication with Resonite.

### send_osc

Send an OSC message to a target host and port.

```python
await send_osc(host, port, address, values=None)
```

**Parameters:**
- `host` (str): Target hostname/IP (e.g., "127.0.0.1")
- `port` (int): Target UDP port (default: 9000)
- `address` (str): OSC address pattern starting with "/"
- `values` (List[Any], optional): Values to send

**Returns:** Dict with operation status and details

**Examples:**
```python
# Send parameter value
await send_osc("127.0.0.1", 9000, "/avatar/parameters/Happy", [0.8])

# Send trigger/bang
await send_osc("127.0.0.1", 9000, "/action/jump", [])
```

### start_osc_server

Start a UDP server to receive OSC messages from Resonite.

```python
await start_osc_server(port, address="0.0.0.0")
```

**Parameters:**
- `port` (int): UDP port to listen on
- `address` (str): Network interface (default: "0.0.0.0")

**Returns:** Dict with server status

### stop_osc_server

Stop a running OSC server.

```python
await stop_osc_server(port)
```

**Parameters:**
- `port` (int): Port of server to stop

**Returns:** Dict with operation status

### get_received_messages

Retrieve OSC messages received by a server.

```python
await get_received_messages(port, address_pattern=None, max_age_seconds=None, limit=100)
```

**Parameters:**
- `port` (int): Server port to query
- `address_pattern` (str, optional): Filter by OSC address
- `max_age_seconds` (float, optional): Only recent messages
- `limit` (int): Maximum messages to return

**Returns:** Dict with messages array

### get_latest_message

Get the most recent OSC message.

```python
await get_latest_message(port, address_pattern=None)
```

**Parameters:**
- `port` (int): Server port to query
- `address_pattern` (str, optional): Filter by OSC address

**Returns:** Dict with latest message

### get_osc_server_stats

Get OSC server statistics.

```python
await get_osc_server_stats(port)
```

**Parameters:**
- `port` (int): Server port to query

**Returns:** Dict with server statistics

### clear_osc_message_buffer

Clear all buffered OSC messages.

```python
await clear_osc_message_buffer(port)
```

**Parameters:**
- `port` (int): Server port to clear

**Returns:** Dict with clear operation results

### test_osc_echo

Test OSC functionality with echo.

```python
await test_osc_echo(port=9000)
```

**Parameters:**
- `port` (int): Port to use for echo test

**Returns:** Dict with test results

## Resonite Session Management

Tools for managing Resonite sessions and connections.

### resonite_session_start

Start a new Resonite session.

```python
await resonite_session_start(session_name=None, world_path=None, avatar_slot=None)
```

**Parameters:**
- `session_name` (str, optional): Custom session name
- `world_path` (str, optional): Initial world to load
- `avatar_slot` (int, optional): Avatar slot to use

**Returns:** Dict with session information

### resonite_session_status

Get current session status.

```python
await resonite_session_status()
```

**Returns:** Dict with session status information

### resonite_session_end

End the current Resonite session.

```python
await resonite_session_end()
```

**Returns:** Dict with cleanup status

## Avatar Control

Tools for controlling avatars in Resonite.

### resonite_avatar_load

Load an avatar into the session.

```python
await resonite_avatar_load(avatar_path, slot=None, parameters=None)
```

**Parameters:**
- `avatar_path` (str): Path to avatar (resonite://, inventory://, file://)
- `slot` (int, optional): Avatar slot (0-7)
- `parameters` (Dict[str, Any], optional): Initial parameter values

**Returns:** Dict with avatar loading status

### resonite_parameter_set

Set an avatar parameter value.

```python
await resonite_parameter_set(parameter_name, value, avatar_slot=None)
```

**Parameters:**
- `parameter_name` (str): Parameter name (e.g., "Happy", "Angry")
- `value` (float): Parameter value (0.0 to 1.0)
- `avatar_slot` (int, optional): Specific avatar slot

**Returns:** Dict with parameter setting status

## World Management

Tools for loading and managing worlds.

### resonite_world_load

Load a world in the current session.

```python
await resonite_world_load(world_path)
```

**Parameters:**
- `world_path` (str): Path to world (resonite://, inventory://, file://)

**Returns:** Dict with world loading status

## ProtoFlux Scripting

Tools for ProtoFlux visual scripting.

### resonite_protoflux_execute

Execute a ProtoFlux script.

```python
await resonite_protoflux_execute(script_name, parameters=None)
```

**Parameters:**
- `script_name` (str): Name of the script to execute
- `parameters` (Dict[str, Any], optional): Script parameters

**Returns:** Dict with execution status

## Inventory Management

Tools for managing user inventory and assets.

### resonite_inventory_list

List inventory items with filtering.

```python
await resonite_inventory_list(item_type=None, search_query=None, limit=50, offset=0)
```

**Parameters:**
- `item_type` (str, optional): Filter by type (avatar, world, item, tool, script)
- `search_query` (str, optional): Search query
- `limit` (int): Maximum items to return
- `offset` (int): Pagination offset

**Returns:** Dict with inventory items and pagination

### resonite_inventory_search

Search inventory with full-text search.

```python
await resonite_inventory_search(query, item_type=None)
```

**Parameters:**
- `query` (str): Search query
- `item_type` (str, optional): Type filter

**Returns:** Dict with search results

### resonite_inventory_spawn

Spawn an inventory item into the world.

```python
await resonite_inventory_spawn(item_id, position=None, rotation=None, scale=None)
```

**Parameters:**
- `item_id` (str): Inventory item identifier
- `position` (List[float], optional): Spawn position [x, y, z]
- `rotation` (List[float], optional): Spawn rotation quaternion
- `scale` (List[float], optional): Spawn scale [x, y, z]

**Returns:** Dict with spawn operation status

### resonite_inventory_upload

Upload a file to inventory.

```python
await resonite_inventory_upload(item_path, item_name, item_type, description=None, is_public=False)
```

**Parameters:**
- `item_path` (str): Local file path to upload
- `item_name` (str): Name for uploaded item
- `item_type` (str): Item type (avatar, world, item, tool, script)
- `description` (str, optional): Item description
- `is_public` (bool): Whether item is publicly accessible

**Returns:** Dict with upload status

### resonite_inventory_delete

Delete an item from inventory.

```python
await resonite_inventory_delete(item_id, confirm_deletion=True)
```

**Parameters:**
- `item_id` (str): Item to delete
- `confirm_deletion` (bool): Safety confirmation

**Returns:** Dict with deletion status

### resonite_inventory_share

Share an inventory item with another user.

```python
await resonite_inventory_share(item_id, share_with, permission_level="read")
```

**Parameters:**
- `item_id` (str): Item to share
- `share_with` (str): Username to share with
- `permission_level` (str): Permission level (read, write, admin)

**Returns:** Dict with sharing status

### resonite_inventory_info

Get detailed information about an inventory item.

```python
await resonite_inventory_info(item_id)
```

**Parameters:**
- `item_id` (str): Item to get information about

**Returns:** Dict with detailed item information

## Plugin Management

Tools for managing MCP server plugins.

### plugin_list

List all loaded plugins.

```python
await plugin_list()
```

**Returns:** Dict with plugin information and statistics

### plugin_load

Load and initialize a plugin.

```python
await plugin_load(plugin_name)
```

**Parameters:**
- `plugin_name` (str): Name of plugin to load

**Returns:** Dict with plugin loading status

### plugin_unload

Unload a plugin.

```python
await plugin_unload(plugin_name)
```

**Parameters:**
- `plugin_name` (str): Name of plugin to unload

**Returns:** Dict with plugin unloading status

### plugin_reload

Reload a plugin.

```python
await plugin_reload(plugin_name)
```

**Parameters:**
- `plugin_name` (str): Name of plugin to reload

**Returns:** Dict with plugin reload status

### plugin_discover

Discover available plugins.

```python
await plugin_discover()
```

**Returns:** Dict with available plugins

### plugin_info

Get detailed plugin information.

```python
await plugin_info(plugin_name=None)
```

**Parameters:**
- `plugin_name` (str, optional): Specific plugin name, or None for all

**Returns:** Dict with plugin information

## HTTP API Endpoints

REST API endpoints for web-based control.

### Core Endpoints

```
GET  /                     # Server information
GET  /health              # Health check
GET  /docs                # Interactive API documentation
```

### OSC Endpoints

```
POST /osc/send            # Send OSC message
POST /osc/server/start    # Start OSC server
POST /osc/server/stop     # Stop OSC server
GET  /osc/messages        # Get received messages
GET  /osc/stats           # Get server statistics
POST /osc/buffer/clear    # Clear message buffer
```

### Resonite Endpoints

```
POST /resonite/session/start     # Start session
GET  /resonite/session/status    # Get session status
POST /resonite/session/end       # End session

POST /resonite/avatar/load       # Load avatar
POST /resonite/parameter/set     # Set parameter

POST /resonite/world/load        # Load world

POST /resonite/protoflux/execute # Execute ProtoFlux script

GET  /resonite/inventory/list    # List inventory
GET  /resonite/inventory/search  # Search inventory
POST /resonite/inventory/spawn   # Spawn item
POST /resonite/inventory/upload  # Upload item
DELETE /resonite/inventory/delete # Delete item
POST /resonite/inventory/share   # Share item
GET  /resonite/inventory/info/{item_id} # Get item info
```

### Plugin Endpoints

```
GET  /plugins/list         # List plugins
GET  /plugins/discover     # Discover plugins
POST /plugins/load         # Load plugin
POST /plugins/unload       # Unload plugin
POST /plugins/reload       # Reload plugin
GET  /plugins/info         # Get plugin info
```

## Data Models

### Pydantic Models

All tools use Pydantic models for input validation:

```python
class OSCMessageInput(BaseModel):
    host: str
    port: int = Field(gt=0, le=65535)
    address: str = Field(pattern=r"^/.*")
    values: List[Any] = []

class ResoniteSessionInput(BaseModel):
    session_name: Optional[str] = None
    world_path: Optional[str] = None
    avatar_slot: Optional[int] = Field(None, ge=0, le=7)

class AvatarControlInput(BaseModel):
    avatar_path: str
    slot: Optional[int] = Field(None, ge=0, le=7)
    parameters: Optional[Dict[str, Any]] = None

class ProtoFluxScriptInput(BaseModel):
    script_name: str
    script_data: Optional[Dict[str, Any]] = None
    execute: bool = True

class InventoryListInput(BaseModel):
    item_type: Optional[str] = Field(None, regex="^(avatar|world|item|tool|script)$")
    search_query: Optional[str] = None
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)
```

## Error Handling

All tools return structured error responses:

```python
{
    "status": "error",
    "message": "Human-readable error description",
    "error_code": "OPTIONAL_ERROR_CODE",
    "details": {}  # Optional additional error information
}
```

## Rate Limiting

- OSC operations: No explicit rate limiting (UDP protocol)
- HTTP API: 100 requests per minute per IP
- Inventory operations: 10 operations per minute

## Authentication

Currently no authentication required. For production deployments, consider:

- API key authentication
- OAuth integration
- Resonite account linking

## Versioning

API follows semantic versioning:

- **Major version**: Breaking changes
- **Minor version**: New features
- **Patch version**: Bug fixes

Current version: `0.1.0`

## SDKs and Libraries

### Python Client

```python
import httpx

async def control_avatar(parameter: str, value: float):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/resonite/parameter/set",
            json={
                "parameter_name": parameter,
                "value": value
            }
        )
        return response.json()
```

### JavaScript/TypeScript

```javascript
const resoniteAPI = {
    async setParameter(parameterName, value) {
        const response = await fetch('/resonite/parameter/set', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                parameter_name: parameterName,
                value: value
            })
        });
        return response.json();
    }
};
```

## Changelog

### Version 0.1.0

**Initial Release**
- OSC communication tools
- Resonite session management
- Avatar control tools
- World management
- ProtoFlux scripting support
- Inventory management
- Plugin system
- HTTP REST API
- Claude Desktop DXT packaging

---

**API Version**: 0.1.0
**Last Updated**: December 22, 2025


