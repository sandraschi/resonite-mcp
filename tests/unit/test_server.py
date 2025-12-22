"""Unit tests for Resonite MCP server."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from resonite_mcp.server import (
    send_osc,
    start_osc_server,
    stop_osc_server,
    resonite_session_start,
    resonite_world_load,
    resonite_avatar_load,
    resonite_parameter_set,
    resonite_protoflux_execute,
)


class TestOSCTools:
    """Test OSC-related tools."""

    @pytest.mark.asyncio
    async def test_send_osc_success(self):
        """Test successful OSC message sending."""
        with patch("resonite_mcp.server.SimpleUDPClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Clear client cache
            from resonite_mcp.server import osc_clients
            osc_clients.clear()

            result = await send_osc(
                host="127.0.0.1",
                port=9000,
                address="/test",
                values=[1, 2, 3]
            )

            assert result["status"] == "success"
            assert result["host"] == "127.0.0.1"
            assert result["port"] == 9000
            assert result["address"] == "/test"
            assert result["values"] == [1, 2, 3]
            mock_client.send_message.assert_called_once_with("/test", [1, 2, 3])

    @pytest.mark.asyncio
    async def test_send_osc_no_values(self):
        """Test OSC message sending with no values."""
        with patch("resonite_mcp.server.SimpleUDPClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Clear client cache
            from resonite_mcp.server import osc_clients
            osc_clients.clear()

            result = await send_osc(
                host="127.0.0.1",
                port=9000,
                address="/test"
            )

            assert result["status"] == "success"
            assert result["values"] == []
            mock_client.send_message.assert_called_once_with("/test", [])

    @pytest.mark.asyncio
    async def test_send_osc_error(self):
        """Test OSC message sending error handling."""
        with patch("resonite_mcp.server.SimpleUDPClient") as mock_client_class:
            mock_client_class.side_effect = Exception("Connection failed")

            # Clear client cache
            from resonite_mcp.server import osc_clients
            osc_clients.clear()

            result = await send_osc(
                host="127.0.0.1",
                port=9000,
                address="/test",
                values=[1]
            )

            assert result["status"] == "error"
            assert "Connection failed" in result["message"]


class TestResoniteTools:
    """Test Resonite-specific tools."""

    @pytest.mark.asyncio
    async def test_resonite_session_start_success(self):
        """Test successful session start."""
        with patch("resonite_mcp.server.send_osc") as mock_send_osc:
            mock_send_osc.return_value = {"status": "success"}

            result = await resonite_session_start(
                session_name="test_session"
            )

            assert result["status"] == "success"
            assert "test_session" in result["session_info"]["session_id"]
            assert result["session_info"]["platform"] == "resonite"
            assert result["session_info"]["osc_connected"] is True
            assert "avatar_control" in result["session_info"]["capabilities"]

    @pytest.mark.asyncio
    async def test_resonite_session_start_with_world(self):
        """Test session start with world loading."""
        with patch("resonite_mcp.server.send_osc") as mock_send_osc, \
             patch("resonite_mcp.server.resonite_world_load") as mock_world_load:

            mock_send_osc.return_value = {"status": "success"}
            mock_world_load.return_value = {"status": "success"}

            result = await resonite_session_start(
                session_name="test_session",
                world_path="resonite://TestWorld"
            )

            assert result["status"] == "success"
            assert "initial_world" in result["session_info"]
            assert result["session_info"]["initial_world"]["path"] == "resonite://TestWorld"

    @pytest.mark.asyncio
    async def test_resonite_world_load_success(self):
        """Test successful world loading."""
        with patch("resonite_mcp.server.send_osc") as mock_send_osc:
            mock_send_osc.return_value = {"status": "success"}

            result = await resonite_world_load(
                world_path="resonite://TestWorld"
            )

            assert result["status"] == "success"
            assert result["world_path"] == "resonite://TestWorld"
            assert "World load initiated" in result["message"]

    @pytest.mark.asyncio
    async def test_resonite_world_load_invalid_path(self):
        """Test world loading with invalid path."""
        result = await resonite_world_load(
            world_path="invalid://path"
        )

        assert result["status"] == "error"
        assert "Invalid world path format" in result["message"]

    @pytest.mark.asyncio
    async def test_resonite_avatar_load_success(self):
        """Test successful avatar loading."""
        with patch("resonite_mcp.server.send_osc") as mock_send_osc:
            mock_send_osc.return_value = {"status": "success"}

            result = await resonite_avatar_load(
                avatar_path="resonite://TestAvatar",
                slot=0,
                parameters={"happy": 0.8}
            )

            assert result["status"] == "success"
            assert result["avatar_path"] == "resonite://TestAvatar"
            assert result["slot"] == 0
            assert result["initial_parameters"] == {"happy": 0.8}

    @pytest.mark.asyncio
    async def test_resonite_parameter_set_success(self):
        """Test successful parameter setting."""
        with patch("resonite_mcp.server.send_osc") as mock_send_osc:
            mock_send_osc.return_value = {"status": "success"}

            result = await resonite_parameter_set(
                parameter_name="Happy",
                value=0.8,
                avatar_slot=1
            )

            assert result["status"] == "success"
            assert result["parameter"] == "Happy"
            assert result["value"] == 0.8
            assert result["avatar_slot"] == 1

    @pytest.mark.asyncio
    async def test_resonite_protoflux_execute_success(self):
        """Test successful ProtoFlux script execution."""
        with patch("resonite_mcp.server.send_osc") as mock_send_osc:
            mock_send_osc.return_value = {"status": "success"}

            result = await resonite_protoflux_execute(
                script_name="TestScript",
                parameters={"param1": "value1"}
            )

            assert result["status"] == "success"
            assert result["script_name"] == "TestScript"
            assert result["parameters"] == {"param1": "value1"}
