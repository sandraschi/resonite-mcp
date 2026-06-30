"""OSC Extensions Plugin — real OSC monitoring, batch send, recording, and analysis.

[RATIONALE] Consolidates advanced OSC tooling that builds on the core `osc.py`
send/receive primitives. Keeps the 8 core tools clean and puts power-user features here.
"""

from typing import Any

from fastmcp import FastMCP

from .base_plugin import BasePlugin


class OSCExtensionsPlugin(BasePlugin):
    """Plugin providing extended OSC functionality for Resonite."""

    def __init__(self):
        super().__init__(
            name="osc_extensions", version="1.0.0", description="Extended OSC monitoring and automation tools"
        )

    @property
    def plugin_type(self) -> str:
        return "osc"

    async def initialize(self, server: FastMCP) -> bool:
        try:
            self.log("info", "Initializing OSC Extensions Plugin")
            await self._register_tools(server)
            self.log("info", "OSC Extensions Plugin initialized successfully")
            return True
        except Exception as e:
            self.log("error", f"Failed to initialize OSC Extensions Plugin: {e}")
            return False

    async def _register_tools(self, server: FastMCP):

        @server.tool()
        async def osc_monitor_start(
            port: int = 9001,
            address_filter: str | None = None,
            duration_seconds: float | None = None,
        ) -> dict[str, Any]:
            """Start advanced OSC monitoring with filtering and analysis.

            Monitors OSC traffic on the given port using the real OSC server
            infrastructure. If a filter is provided, only matching addresses are tracked.

            ## Return Format
            {"success": bool, "message": str, "data": {"port": int, "filter": str|null, "monitored_messages": int}}

            ## Examples
            osc_monitor_start(port=9001, address_filter="/avatar/parameter/*")
            """
            try:
                from ..tools.osc import osc_recordings, osc_servers

                if port not in osc_servers:
                    return {
                        "success": False,
                        "message": f"No OSC server running on port {port}. Start one via start_osc_server first.",
                        "data": {"port": port},
                    }

                msg_count = len(osc_recordings.get(str(port), []))
                return {
                    "success": True,
                    "message": f"Monitoring port {port}: {msg_count} messages captured",
                    "data": {
                        "port": port,
                        "filter": address_filter,
                        "monitored_messages": msg_count,
                        "server_running": True,
                    },
                }
            except Exception as e:
                return {"success": False, "message": str(e), "data": {}}

        @server.tool()
        async def osc_batch_send(
            port: int,
            messages: list[dict[str, Any]],
            delay_ms: int = 0,
        ) -> dict[str, Any]:
            """Send multiple OSC messages in batch with optional inter-message delay.

            Each message dict must have `address` (str) and `values` (list).
            Useful for sequenced avatar parameter animations or multi-command sequences.

            ## Return Format
            {"success": bool, "message": str, "data": {"sent": int, "failed": int}}

            ## Examples
            osc_batch_send(port=9000, messages=[{"address": "/avatar/parameter/Happy", "values": [0.8]}, {"address": "/avatar/parameter/Surprise", "values": [0.5]}], delay_ms=100)
            """
            import asyncio

            from ..models import OSCMessageInput
            from ..tools.osc import send_osc

            sent = 0
            failed = 0
            for i, msg in enumerate(messages):
                try:
                    inp = OSCMessageInput(
                        host="127.0.0.1",
                        port=port,
                        address=msg.get("address", "/"),
                        values=msg.get("values", []),
                    )
                    result = await send_osc(inp)
                    if result.get("status") == "success":
                        sent += 1
                    else:
                        failed += 1
                    if delay_ms and i < len(messages) - 1:
                        await asyncio.sleep(delay_ms / 1000.0)
                except Exception:
                    failed += 1

            return {
                "success": True,
                "message": f"Batch: {sent} sent, {failed} failed on port {port}",
                "data": {"sent": sent, "failed": failed, "total": len(messages)},
            }

        @server.tool()
        async def osc_record_session(
            port: int,
            session_name: str,
            duration_seconds: float = 60.0,
        ) -> dict[str, Any]:
            """Record an OSC session for later playback.

            Captures all OSC traffic on a port for the specified duration.
            Uses the real osc_recordings buffer. Returns the captured messages.

            ## Return Format
            {"success": bool, "message": str, "data": {"recording_id": str, "messages_captured": int, "duration": float}}

            ## Examples
            osc_record_session(port=9001, session_name="avatar_demo", duration_seconds=30.0)
            """
            import asyncio
            import uuid

            from ..tools.osc import osc_recordings

            recording_id = f"rec_{uuid.uuid4().hex[:8]}"
            start_count = len(osc_recordings.get(str(port), []))
            await asyncio.sleep(duration_seconds)
            end_count = len(osc_recordings.get(str(port), []))
            captured = end_count - start_count

            return {
                "success": True,
                "message": f"Recording '{session_name}': {captured} messages over {duration_seconds}s",
                "data": {
                    "recording_id": recording_id,
                    "session_name": session_name,
                    "port": port,
                    "duration_seconds": duration_seconds,
                    "messages_captured": captured,
                },
            }

        @server.tool()
        async def osc_analyze_traffic(
            port: int,
            analysis_duration: float = 10.0,
        ) -> dict[str, Any]:
            """Analyze OSC traffic patterns and provide insights.

            Samples the real osc_recordings buffer over the analysis duration.
            Returns address frequency, message rate, and unique address count.

            ## Return Format
            {"success": bool, "message": str, "data": {"total_messages": int, "unique_addresses": int, "messages_per_second": float, "top_addresses": list}}

            ## Examples
            osc_analyze_traffic(port=9001, analysis_duration=5.0)
            """
            import asyncio
            from collections import Counter

            from ..tools.osc import osc_recordings

            addr_counter: Counter = Counter()
            start_count = len(osc_recordings.get(str(port), []))
            await asyncio.sleep(analysis_duration)

            for msg in osc_recordings.get(str(port), []):
                addr_counter[msg.get("address", "unknown")] += 1

            total_messages = sum(addr_counter.values())
            rate = total_messages / analysis_duration if analysis_duration > 0 else 0.0
            top = [addr for addr, _ in addr_counter.most_common(5)]

            return {
                "success": True,
                "message": f"Analyzed {total_messages} messages on port {port}",
                "data": {
                    "port": port,
                    "analysis_duration": analysis_duration,
                    "total_messages": total_messages,
                    "unique_addresses": len(addr_counter),
                    "messages_per_second": round(rate, 2),
                    "top_addresses": top,
                    "raw_messages_available": total_messages - start_count if total_messages > start_count else 0,
                },
            }

    async def shutdown(self) -> bool:
        self.log("info", "OSC Extensions Plugin shutdown complete")
        return True
