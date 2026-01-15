"""Pytest configuration for Resonite MCP tests."""

import asyncio
import sys
from pathlib import Path

import pytest

# Add src to Python path for tests
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def reset_osc_state():
    """Reset OSC client and server state before each test."""
    from resonite_mcp.tools.osc import osc_clients, osc_recordings, osc_servers

    # Clear all OSC state
    osc_clients.clear()
    osc_servers.clear()
    osc_recordings.clear()


@pytest.fixture
def mock_osc_client():
    """Mock OSC client for testing."""
    with pytest.mock.patch("resonite_mcp.tools.osc.SimpleUDPClient") as mock_client:
        yield mock_client


