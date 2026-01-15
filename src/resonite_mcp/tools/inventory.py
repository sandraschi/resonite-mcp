"""Inventory Management Tools - Portmanteau for Resonite inventory operations.

This module provides comprehensive inventory management functionality for Resonite,
including listing, searching, spawning, uploading, and managing inventory items.
"""

import asyncio
import logging
import os
import time
from typing import Any, Dict, Optional

from ..models import (
    InventoryDeleteInput,
    InventoryListInput,
    InventoryShareInput,
    InventorySpawnInput,
    InventoryUploadInput,
    OSCMessageInput,
    OSCServerInput,
)
from ..server import server
from .osc import osc_recordings, osc_servers, send_osc, start_osc_server

logger = logging.getLogger(__name__)


async def _wait_for_osc_response(
    address_pattern: str, timeout: float = 5.0, port: int = 9001
) -> Optional[Dict[str, Any]]:
    """Wait for an OSC message matching the pattern in the recordings buffer.

    Args:
        address_pattern: OSC address pattern to look for
        timeout: Maximum time to wait in seconds
        port: Port of the OSC server to check

    Returns:
        The matching message dictionary or None if timeout
    """
    start_time = time.time()
    port_str = str(port)

    while time.time() - start_time < timeout:
        if port_str in osc_recordings:
            # Check for messages received AFTER start_time
            for msg in reversed(osc_recordings[port_str]):
                if msg["timestamp"] >= start_time and address_pattern in msg["address"]:
                    return msg

        await asyncio.sleep(0.1)

    return None


async def resonite_inventory_list(input_data: InventoryListInput) -> Dict[str, Any]:
    """List items in the user's Resonite inventory.

    Args:
        input_data: Inventory list configuration (item_type, search_query, limit, offset)

    Returns:
        Dictionary with inventory items and pagination info
    """
    item_type = input_data.item_type
    search_query = input_data.search_query
    limit = input_data.limit
    offset = input_data.offset

    try:
        # Ensure OSC server is running to receive responses
        # Defaulting to port 9001 for responses
        if 9001 not in osc_servers:
            # In a real scenario we'd check if the server is already running
            # For now, we assume one is configured or we try to start one
            try:
                await start_osc_server(OSCServerInput(port=9001))
            except Exception as e:
                logger.warning(f"Failed to start response OSC server: {e}")

        query_params = {
            "limit": limit,
            "offset": offset,
        }
        if item_type:
            query_params["type"] = item_type
        if search_query:
            query_params["search"] = search_query

        osc_input = OSCMessageInput(
            host="127.0.0.1", port=9000, address="/inventory/list", values=[query_params]
        )
        await send_osc(osc_input)

        # Wait for response from Resonite
        response = await _wait_for_osc_response("/inventory/list/response")

        if response:
            items = response["args"][0] if response["args"] else []
            total_count = response["args"][1] if len(response["args"]) > 1 else len(items)

            return {
                "status": "success",
                "message": f"Retrieved {len(items)} inventory items",
                "items": items,
                "total_count": total_count,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "has_more": total_count > (offset + len(items)),
                },
            }
        else:
            return {
                "status": "warning",
                "message": "Timed out waiting for Resonite inventory response. Returning mock data for safety.",
                "items": [
                    {"id": "mock_id_1", "name": "Default Avatar", "type": "avatar"},
                    {"id": "mock_id_2", "name": "Tutorial World", "type": "world"},
                ],
                "total_count": 2,
                "pagination": {"limit": limit, "offset": offset, "has_more": False},
            }

    except Exception as e:
        error = f"Failed to list inventory items: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


server.tool()(resonite_inventory_list)


async def resonite_inventory_search(query: str, item_type: Optional[str] = None) -> Dict[str, Any]:
    """Search for items in the user's Resonite inventory."""
    try:
        input_data = InventoryListInput(item_type=item_type, search_query=query, limit=100)
        result = await resonite_inventory_list(input_data)
        if result["status"] == "success":
            return {
                "status": "success",
                "query": query,
                "results": result["items"],
            }
        return result
    except Exception as e:
        error = f"Failed to search inventory: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


server.tool()(resonite_inventory_search)


async def resonite_inventory_spawn(input_data: InventorySpawnInput) -> Dict[str, Any]:
    """Spawn an item from inventory into the current world."""
    item_id = input_data.item_id
    position = input_data.position
    rotation = input_data.rotation
    scale = input_data.scale

    try:
        spawn_params = {"item_id": item_id}
        if position:
            spawn_params["position"] = position
        if rotation:
            spawn_params["rotation"] = rotation
        if scale:
            spawn_params["scale"] = scale

        osc_input = OSCMessageInput(
            host="127.0.0.1", port=9000, address="/inventory/spawn", values=[spawn_params]
        )
        result = await send_osc(osc_input)
        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"Successfully spawned item {item_id}",
                "item_id": item_id,
            }
        return result
    except Exception as e:
        error = f"Failed to spawn inventory item: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


server.tool()(resonite_inventory_spawn)


async def resonite_inventory_upload(input_data: InventoryUploadInput) -> Dict[str, Any]:
    """Upload a local file to Resonite inventory."""
    item_path = input_data.item_path
    item_name = input_data.item_name
    item_type = input_data.item_type
    description = input_data.description
    is_public = input_data.is_public

    try:
        if not os.path.exists(item_path):
            return {"status": "error", "message": f"File not found: {item_path}"}

        upload_params = {
            "file_path": item_path,
            "name": item_name,
            "type": item_type,
            "public": is_public,
        }
        if description:
            upload_params["description"] = description

        osc_input = OSCMessageInput(
            host="127.0.0.1", port=9000, address="/inventory/upload", values=[upload_params]
        )
        result = await send_osc(osc_input)
        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"Successfully uploaded {item_name}",
            }
        return result
    except Exception as e:
        error = f"Failed to upload item: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


server.tool()(resonite_inventory_upload)


async def resonite_inventory_delete(input_data: InventoryDeleteInput) -> Dict[str, Any]:
    """Delete an item from the user's Resonite inventory."""
    item_id = input_data.item_id
    confirm_deletion = input_data.confirm_deletion

    try:
        if not confirm_deletion:
            return {"status": "error", "message": "Deletion not confirmed."}

        osc_input = OSCMessageInput(
            host="127.0.0.1", port=9000, address="/inventory/delete", values=[item_id]
        )
        result = await send_osc(osc_input)
        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"Successfully deleted item {item_id}",
            }
        return result
    except Exception as e:
        error = f"Failed to delete item: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


server.tool()(resonite_inventory_delete)


async def resonite_inventory_share(input_data: InventoryShareInput) -> Dict[str, Any]:
    """Share an inventory item with another user."""
    item_id = input_data.item_id
    share_with = input_data.share_with
    permission_level = input_data.permission_level

    try:
        share_params = {
            "item_id": item_id,
            "username": share_with,
            "permission": permission_level,
        }
        osc_input = OSCMessageInput(
            host="127.0.0.1", port=9000, address="/inventory/share", values=[share_params]
        )
        result = await send_osc(osc_input)
        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"Successfully shared item {item_id} with {share_with}",
            }
        return result
    except Exception as e:
        error = f"Failed to share item: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


server.tool()(resonite_inventory_share)


async def resonite_inventory_info(item_id: str) -> Dict[str, Any]:
    """Get detailed information about an inventory item."""
    try:
        osc_input = OSCMessageInput(
            host="127.0.0.1", port=9000, address="/inventory/info", values=[item_id]
        )
        await send_osc(osc_input)

        # Wait for response from Resonite
        response = await _wait_for_osc_response("/inventory/info/response")

        if response:
            item_info = response["args"][0] if response["args"] else {}
            return {
                "status": "success",
                "message": f"Retrieved information for item {item_id}",
                "item_info": item_info,
            }
        else:
            return {
                "status": "warning",
                "message": f"Timed out waiting for Resonite info response for item {item_id}. Returning mock info.",
                "item_info": {
                    "id": item_id,
                    "name": f"Item {item_id}",
                    "description": "Information could not be retrieved from Resonite.",
                    "created_at": "2025-01-01T00:00:00Z",
                },
            }
    except Exception as e:
        error = f"Failed to get item info: {e}"
        logger.error(error)
        return {"status": "error", "message": error}


server.tool()(resonite_inventory_info)
