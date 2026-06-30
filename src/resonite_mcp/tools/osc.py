"""OSC Communication Tools - Individual tool registration.

This module provides comprehensive OSC (Open Sound Control) communication
functionality for real-time control of audio/visual applications and devices.
"""

import asyncio
import logging
import threading
import time
from typing import Any

from pythonosc import dispatcher, osc_server, udp_client

from ..models import OSCMessageInput, OSCServerInput, OSCServerStopInput

logger = logging.getLogger(__name__)

# Import server for tool registration
from ..server import server  # noqa: E402

# Global OSC state management
osc_clients: dict[str, udp_client.SimpleUDPClient] = {}
osc_servers: dict[int, osc_server.ThreadingOSCUDPServer] = {}
osc_recordings: dict[str, list[dict[str, Any]]] = {}


async def send_osc(input_data: OSCMessageInput) -> dict[str, Any]:
    """Send an OSC message to the specified address.

    This is a low-level OSC function for direct protocol control.
    Most users should use the higher-level Resonite-specific tools instead.

    Args:
        input_data: OSC message details (host, port, address, values)

    Returns:
        Dictionary with operation status and details

    Examples:
        Send a parameter value:
        send_osc({"host": "127.0.0.1", "port": 9000, "address": "/avatar/happy", "values": [0.8]})
    """
    host = input_data.host
    port = input_data.port
    address = input_data.address
    values = input_data.values
    try:
        client_key = f"{host}:{port}"
        if client_key not in osc_clients:
            osc_clients[client_key] = udp_client.SimpleUDPClient(host, port)

        client = osc_clients[client_key]
        if values:
            client.send_message(address, values)
        else:
            # Send empty message (bang)
            client.send_message(address, [])

        logger.info(f"Sent OSC message to {host}:{port}{address} with values: {values}")
        return {
            "status": "success",
            "message": f"OSC message sent to {host}:{port}{address}",
            "values": values or [],
            "host": host,
            "port": port,
            "address": address,
        }

    except Exception as e:
        logger.error(f"Failed to send OSC message: {e}")
        return {
            "status": "error",
            "message": f"Failed to send OSC message: {e!s}",
            "address": address,
            "host": host,
            "port": port,
        }


server.tool()(send_osc)


async def start_osc_server(input_data: OSCServerInput) -> dict[str, Any]:
    """Start an OSC server to receive incoming messages from Resonite.

    This creates a UDP server that can receive OSC messages from Resonite
    for bidirectional communication and real-time feedback.

    Args:
        input_data: Server configuration (port, address)

    Returns:
        Dictionary with server status and connection details

    Examples:
        Start server for Resonite feedback: start_osc_server({"port": 9001})
    """
    port = input_data.port
    address = input_data.address
    try:
        if port in osc_servers:
            return {
                "status": "error",
                "message": f"OSC server already running on port {port}",
                "port": port,
            }

        # Create dispatcher for handling incoming messages
        disp = dispatcher.Dispatcher()

        def message_handler(address: str, *args):
            """Handle incoming OSC messages."""
            timestamp = time.time()
            message = {
                "timestamp": timestamp,
                "address": address,
                "args": list(args),
                "source": f"{address}:{port}",
            }

            # Store in recordings
            if str(port) not in osc_recordings:
                osc_recordings[str(port)] = []
            osc_recordings[str(port)].append(message)

            # Keep only last 1000 messages per port
            if len(osc_recordings[str(port)]) > 1000:
                osc_recordings[str(port)] = osc_recordings[str(port)][-1000:]

            logger.info(f"Received OSC message: {address} {args}")

        # Add default handler for all messages
        disp.set_default_handler(message_handler)

        # Create and start server
        new_server = osc_server.ThreadingOSCUDPServer((address, port), disp)
        server_thread = threading.Thread(target=new_server.serve_forever, daemon=True)
        server_thread.start()

        osc_servers[port] = new_server

        logger.info(f"Started OSC server on {address}:{port}")
        return {
            "status": "success",
            "message": f"OSC server started on {address}:{port}",
            "port": port,
            "address": address,
        }

    except Exception as e:
        logger.error(f"Failed to start OSC server: {e}")
        return {
            "status": "error",
            "message": f"Failed to start OSC server: {e!s}",
            "port": port,
            "address": address,
        }


server.tool()(start_osc_server)


async def stop_osc_server(input_data: OSCServerStopInput) -> dict[str, Any]:
    """Stop a running OSC server.

    Args:
        input_data: Port of the server to stop

    Returns:
        Dictionary with operation status

    Examples:
        Stop OSC server: stop_osc_server({"port": 9001})
    """
    port = input_data.port
    try:
        if port not in osc_servers:
            return {
                "status": "error",
                "message": f"No OSC server running on port {port}",
                "port": port,
            }

        target_server = osc_servers[port]
        target_server.shutdown()
        target_server.server_close()
        del osc_servers[port]

        logger.info(f"Stopped OSC server on port {port}")
        return {"status": "success", "message": f"OSC server stopped on port {port}", "port": port}

    except Exception as e:
        logger.error(f"Failed to stop OSC server: {e}")
        return {"status": "error", "message": f"Failed to stop OSC server: {e!s}", "port": port}


server.tool()(stop_osc_server)


async def get_received_messages(
    port: int,
    address_pattern: str | None = None,
    max_age_seconds: float | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Get OSC messages received by a running OSC server.

    Args:
        port: Port of the OSC server to query
        address_pattern: Filter by OSC address pattern (substring match)
        max_age_seconds: Only return messages newer than this age
        limit: Maximum number of messages to return

    Returns:
        Dictionary with messages and metadata

    Examples:
        Get recent messages: get_received_messages(9001)
        Filter by address: get_received_messages(9001, "/avatar")
        Get last 10 messages: get_received_messages(9001, limit=10)
    """
    try:
        if str(port) not in osc_recordings:
            return {"status": "success", "messages": [], "count": 0, "port": port}

        messages = osc_recordings[str(port)]
        current_time = time.time()

        # Apply filters
        filtered_messages = []
        for msg in messages:
            # Age filter
            if max_age_seconds and (current_time - msg["timestamp"]) > max_age_seconds:
                continue

            # Address pattern filter
            if address_pattern and address_pattern not in msg["address"]:
                continue

            filtered_messages.append(msg)

        # Sort by timestamp (newest first) and limit
        filtered_messages.sort(key=lambda x: x["timestamp"], reverse=True)
        filtered_messages = filtered_messages[:limit]

        return {
            "status": "success",
            "messages": filtered_messages,
            "count": len(filtered_messages),
            "port": port,
            "total_available": len(messages),
        }

    except Exception as e:
        logger.error(f"Failed to get received messages: {e}")
        return {
            "status": "error",
            "message": f"Failed to get received messages: {e!s}",
            "port": port,
        }


server.tool()(get_received_messages)


async def get_latest_message(port: int, address_pattern: str | None = None) -> dict[str, Any]:
    """Get the most recent OSC message from a running server."""
    try:
        result = await get_received_messages(port, address_pattern, limit=1)
        if result["status"] == "success" and result["messages"]:
            return {"status": "success", "message": result["messages"][0], "port": port}
        else:
            return {
                "status": "success",
                "message": None,
                "port": port,
                "info": "No messages found matching criteria",
            }

    except Exception as e:
        logger.error(f"Failed to get latest message: {e}")
        return {
            "status": "error",
            "message": f"Failed to get latest message: {e!s}",
            "port": port,
        }


server.tool()(get_latest_message)


async def get_osc_server_stats(port: int) -> dict[str, Any]:
    """Get statistics about a running OSC server's message buffer."""
    try:
        if port not in osc_servers:
            return {
                "status": "error",
                "message": f"No OSC server running on port {port}",
                "port": port,
            }

        message_count = len(osc_recordings.get(str(port), []))
        server_running = osc_servers[port] is not None

        # Get some basic stats
        if str(port) in osc_recordings and osc_recordings[str(port)]:
            oldest_msg = min(osc_recordings[str(port)], key=lambda x: x["timestamp"])
            newest_msg = max(osc_recordings[str(port)], key=lambda x: x["timestamp"])
            age_range = newest_msg["timestamp"] - oldest_msg["timestamp"]
        else:
            age_range = 0

        return {
            "status": "success",
            "port": port,
            "server_running": server_running,
            "messages_buffered": message_count,
            "buffer_age_seconds": age_range,
            "max_buffer_size": 1000,
        }

    except Exception as e:
        logger.error(f"Failed to get OSC server stats: {e}")
        return {
            "status": "error",
            "message": f"Failed to get OSC server stats: {e!s}",
            "port": port,
        }


server.tool()(get_osc_server_stats)


async def clear_osc_message_buffer(port: int) -> dict[str, Any]:
    """Clear all messages from an OSC server's buffer."""
    try:
        if str(port) in osc_recordings:
            cleared_count = len(osc_recordings[str(port)])
            osc_recordings[str(port)] = []
            logger.info(f"Cleared {cleared_count} messages from OSC buffer for port {port}")
            return {
                "status": "success",
                "message": f"Cleared {cleared_count} messages from buffer",
                "port": port,
                "messages_cleared": cleared_count,
            }
        else:
            return {
                "status": "success",
                "message": "No messages to clear",
                "port": port,
                "messages_cleared": 0,
            }

    except Exception as e:
        logger.error(f"Failed to clear OSC message buffer: {e}")
        return {
            "status": "error",
            "message": f"Failed to clear OSC message buffer: {e!s}",
            "port": port,
        }


server.tool()(clear_osc_message_buffer)


async def test_osc_echo(port: int = 9000) -> dict[str, Any]:
    """Test OSC functionality by sending and receiving a message."""
    try:
        # Start a test server if not already running
        if port not in osc_servers:
            start_result = await start_osc_server(OSCServerInput(port=port))
            if start_result["status"] != "success":
                return {
                    "status": "error",
                    "message": f"Failed to start test server: {start_result['message']}",
                    "port": port,
                }
            # Give server time to start
            await asyncio.sleep(0.1)

        # Send a test message
        test_address = "/test/echo"
        test_values = ["hello", 42, 3.14]

        send_result = await send_osc(
            OSCMessageInput(host="127.0.0.1", port=port, address=test_address, values=test_values)
        )
        if send_result["status"] != "success":
            return {
                "status": "error",
                "message": f"Failed to send test message: {send_result['message']}",
                "port": port,
            }

        # Wait a bit for message to be received
        await asyncio.sleep(0.1)

        # Check if message was received
        messages_result = await get_received_messages(port, test_address, limit=1)
        if messages_result["status"] == "success" and messages_result["messages"]:
            received_msg = messages_result["messages"][0]
            return {
                "status": "success",
                "message": "OSC echo test successful",
                "port": port,
                "sent": {"address": test_address, "values": test_values},
                "received": received_msg,
            }
        else:
            return {
                "status": "warning",
                "message": "OSC message sent but not received (server may not be bound to loopback)",
                "port": port,
                "sent": {"address": test_address, "values": test_values},
            }

    except Exception as e:
        logger.error(f"OSC echo test failed: {e}")
        return {"status": "error", "message": f"OSC echo test failed: {e!s}", "port": port}


server.tool()(test_osc_echo)
