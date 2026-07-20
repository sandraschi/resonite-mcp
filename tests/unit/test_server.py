"""Unit tests for Resonite MCP server tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from resonite_mcp.models import (
    AvatarControlInput,
    OSCMessageInput,
    ProtoFluxScriptInput,
    ResoniteSessionInput,
)
from resonite_mcp.tools.avatar import (
    resonite_avatar_load,
    resonite_parameter_set,
    resonite_protoflux_execute,
)
from resonite_mcp.tools.osc import send_osc
from resonite_mcp.tools.session import resonite_session_start, resonite_world_load


class TestOSCTools:
    """Test OSC-related tools."""

    @pytest.mark.asyncio
    async def test_send_osc_success(self):
        """Test successful OSC message sending."""
        with patch("resonite_mcp.tools.osc.udp_client.SimpleUDPClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Clear client cache
            from resonite_mcp.tools.osc import osc_clients

            osc_clients.clear()

            result = await send_osc(OSCMessageInput(host="127.0.0.1", port=9000, address="/test", values=[1, 2, 3]))

            assert result["status"] == "success"
            assert result["host"] == "127.0.0.1"
            assert result["port"] == 9000
            assert result["address"] == "/test"
            assert result["values"] == [1, 2, 3]
            mock_client.send_message.assert_called_once_with("/test", [1, 2, 3])

    @pytest.mark.asyncio
    async def test_send_osc_no_values(self):
        """Test OSC message sending with no values."""
        with patch("resonite_mcp.tools.osc.udp_client.SimpleUDPClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Clear client cache
            from resonite_mcp.tools.osc import osc_clients

            osc_clients.clear()

            result = await send_osc(OSCMessageInput(host="127.0.0.1", port=9000, address="/test"))

            assert result["status"] == "success"
            assert result["values"] == []
            mock_client.send_message.assert_called_once_with("/test", [])

    @pytest.mark.asyncio
    async def test_send_osc_error(self):
        """Test OSC message sending error handling."""
        with patch("resonite_mcp.tools.osc.udp_client.SimpleUDPClient") as mock_client_class:
            mock_client_class.side_effect = Exception("Connection failed")

            # Clear client cache
            from resonite_mcp.tools.osc import osc_clients

            osc_clients.clear()

            result = await send_osc(OSCMessageInput(host="127.0.0.1", port=9000, address="/test", values=[1]))

            assert result["status"] == "error"
            assert "Connection failed" in result["message"]


class TestResoniteTools:
    """Test Resonite-specific tools."""

    @pytest.mark.asyncio
    async def test_resonite_session_start_success(self):
        """Test successful session start."""
        with patch("resonite_mcp.tools.session.send_osc") as mock_send_osc:
            mock_send_osc.return_value = {"status": "success"}

            result = await resonite_session_start(ResoniteSessionInput(session_name="test_session"))

            assert result["status"] == "success"
            assert "test_session" in result["session_info"]["session_id"]
            assert result["session_info"]["platform"] == "resonite"
            assert result["session_info"]["osc_connected"] is True

    @pytest.mark.asyncio
    async def test_resonite_session_start_with_world(self):
        """Test session start with world loading."""
        with (
            patch("resonite_mcp.tools.session.send_osc") as mock_send_osc,
            patch("resonite_mcp.tools.session.resonite_world_load") as mock_world_load,
        ):
            mock_send_osc.return_value = {"status": "success"}
            mock_world_load.return_value = {"status": "success"}

            result = await resonite_session_start(
                ResoniteSessionInput(session_name="test_session", world_path="resonite://TestWorld")
            )

            assert result["status"] == "success"
            assert "initial_world" in result["session_info"]
            assert result["session_info"]["initial_world"]["path"] == "resonite://TestWorld"

    @pytest.mark.asyncio
    async def test_resonite_world_load_success(self):
        """Test successful world loading."""
        with (
            patch("resonite_mcp.server.is_resonite_running", return_value=True),
            patch(
                "resonite_mcp.tools.session.send_osc",
                new=AsyncMock(return_value={"status": "success", "message": "sent"}),
            ),
        ):
            result = await resonite_world_load(world_path="resonite://TestWorld")

        assert result["status"] == "success"
        assert result["world"]["world_path"] == "resonite://TestWorld"
        assert "World load command sent" in result["message"]

    @pytest.mark.asyncio
    async def test_resonite_world_load_invalid_path(self):
        """Test world loading with invalid path."""
        result = await resonite_world_load(world_path="invalid://path")

        assert result["status"] == "error"
        assert "Invalid world path format" in result["message"]

    @pytest.mark.asyncio
    async def test_resonite_avatar_load_success(self):
        """Test successful avatar loading."""
        with patch("resonite_mcp.tools.avatar.send_osc") as mock_send_osc:
            mock_send_osc.return_value = {"status": "success"}

            result = await resonite_avatar_load(
                AvatarControlInput(avatar_id="resonite://TestAvatar", slot=0, parameters={"happy": 0.8})
            )

            assert result["status"] == "success"
            assert "Avatar load initiated" in result["message"]

    @pytest.mark.asyncio
    async def test_resonite_parameter_set_success(self):
        """Test successful parameter setting."""
        with patch("resonite_mcp.tools.avatar.send_osc") as mock_send_osc:
            mock_send_osc.return_value = {"status": "success"}

            result = await resonite_parameter_set(parameter_name="Happy", value=0.8, avatar_slot=1)

            assert result["status"] == "success"
            assert result["message"] == "Parameter 'Happy' set to 0.8"

    @pytest.mark.asyncio
    async def test_resonite_protoflux_execute_success(self):
        """Test successful ProtoFlux script execution."""
        with patch("resonite_mcp.tools.avatar.send_osc") as mock_send_osc:
            mock_send_osc.return_value = {"status": "success"}

            result = await resonite_protoflux_execute(
                ProtoFluxScriptInput(script_name="TestScript", script_data={"param1": "value1"})
            )

            assert result["status"] == "success"
            assert "executed" in result["message"]


class TestIsResoniteRunning:
    """Test is_resonite_running function."""

    @patch("os.name", "nt")
    def test_is_resonite_running_psutil(self):
        """Test detection via psutil."""
        from resonite_mcp.server import is_resonite_running

        mock_proc = MagicMock()
        mock_proc.info = {"name": "Resonite.exe"}

        with patch("psutil.process_iter", return_value=[mock_proc]):
            assert is_resonite_running() is True

    @patch("os.name", "nt")
    def test_is_resonite_running_tasklist_fallback(self):
        """Test fallback to tasklist when psutil fails or does not match."""
        from resonite_mcp.server import is_resonite_running

        with (
            patch("psutil.process_iter", side_effect=Exception("psutil error")),
            patch("subprocess.check_output") as mock_check_output,
        ):
            mock_check_output.return_value = b"Image Name                     PID Session Name        Session#    Mem Usage\r\n========================= ======== ================ =========== ============\r\nResonite.exe                 16856 Console                    1    265,492 K\r\n"
            assert is_resonite_running() is True
            mock_check_output.assert_called_once()

    @patch("os.name", "nt")
    def test_is_resonite_running_not_running(self):
        """Test when resonite is not running."""
        from resonite_mcp.server import is_resonite_running

        with (
            patch("psutil.process_iter", return_value=[]),
            patch("subprocess.check_output") as mock_check_output,
        ):
            mock_check_output.return_value = b"INFO: No tasks are running which match the specified criteria.\r\n"
            assert is_resonite_running() is False

    @patch("os.name", "posix")
    def test_is_resonite_running_non_windows(self):
        """Test that it returns False on non-Windows systems."""
        from resonite_mcp.server import is_resonite_running
        assert is_resonite_running() is False
