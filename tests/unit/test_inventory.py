"""Unit tests for Resonite inventory tools."""

import asyncio
import time
from unittest.mock import AsyncMock, patch

import pytest

from resonite_mcp.models import InventoryListInput
from resonite_mcp.tools.inventory import (
    resonite_inventory_info,
    resonite_inventory_list,
    resonite_inventory_search,
)
from resonite_mcp.tools.osc import osc_recordings


@pytest.mark.asyncio
async def test_resonite_inventory_list_success():
    """Test successful inventory listing with OSC response."""
    with patch(
        "resonite_mcp.tools.inventory.send_osc", new_callable=AsyncMock
    ) as mock_send_osc, patch(
        "resonite_mcp.tools.inventory.start_osc_server", new_callable=AsyncMock
    ):
        mock_send_osc.return_value = {"status": "success"}

        # Simulate OSC response after a short delay
        async def simulate_response():
            await asyncio.sleep(0.2)
            osc_recordings["9001"] = [
                {
                    "timestamp": time.time(),
                    "address": "/inventory/list/response",
                    "args": [
                        [
                            {"id": "item1", "name": "Avatar 1", "type": "avatar"},
                            {"id": "item2", "name": "World 1", "type": "world"},
                        ],
                        2,  # Total count
                    ],
                }
            ]

        input_data = InventoryListInput(limit=10)

        # Run both the tool and the response simulation
        results = await asyncio.gather(resonite_inventory_list(input_data), simulate_response())

        result = results[0]
        assert result["status"] == "success"
        assert len(result["items"]) == 2
        assert result["items"][0]["id"] == "item1"
        assert result["total_count"] == 2


@pytest.mark.asyncio
async def test_resonite_inventory_list_timeout():
    """Test inventory listing timeout fallback."""
    with patch(
        "resonite_mcp.tools.inventory.send_osc", new_callable=AsyncMock
    ) as mock_send_osc, patch(
        "resonite_mcp.tools.inventory.start_osc_server", new_callable=AsyncMock
    ), patch(
        "resonite_mcp.tools.inventory._wait_for_osc_response", new_callable=AsyncMock
    ) as mock_wait:
        mock_send_osc.return_value = {"status": "success"}
        mock_wait.return_value = None  # Simulate timeout

        input_data = InventoryListInput(limit=10)
        result = await resonite_inventory_list(input_data)

        assert result["status"] == "warning"
        assert "Timed out" in result["message"]
        assert result["items"] == []


@pytest.mark.asyncio
async def test_resonite_inventory_info_success():
    """Test successful item info retrieval."""
    with patch("resonite_mcp.tools.inventory.send_osc", new_callable=AsyncMock) as mock_send_osc:
        mock_send_osc.return_value = {"status": "success"}

        async def simulate_response():
            await asyncio.sleep(0.1)
            osc_recordings["9001"] = [
                {
                    "timestamp": time.time(),
                    "address": "/inventory/info/response",
                    "args": [{"id": "item1", "name": "Item One", "description": "A test item"}],
                }
            ]

        results = await asyncio.gather(resonite_inventory_info("item1"), simulate_response())

        result = results[0]
        assert result["status"] == "success"
        assert result["item_info"]["id"] == "item1"
        assert result["item_info"]["name"] == "Item One"


@pytest.mark.asyncio
async def test_resonite_inventory_search_success():
    """Test inventory search using the list tool."""
    with patch(
        "resonite_mcp.tools.inventory.resonite_inventory_list", new_callable=AsyncMock
    ) as mock_list:
        mock_list.return_value = {
            "status": "success",
            "items": [{"id": "item1", "name": "Avatar 1"}],
        }

        result = await resonite_inventory_search("Avatar")

        assert result["status"] == "success"
        assert result["query"] == "Avatar"
        assert len(result["results"]) == 1
