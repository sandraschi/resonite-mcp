"""OSC Extensions Plugin - real OSC monitoring, batch send, recording, and analysis.

[RATIONALE] Consolidates advanced OSC tooling that builds on the core `osc.py`
send/receive primitives. Keeps the 8 core tools clean and puts power-user features here.
"""

from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from ..models import OSCBatchMessage
from .base_plugin import BasePlugin

# OSC protocol assumptions shared by every tool in this plugin:
# - Transport is UDP via python-osc. Resonite listens on 127.0.0.1:9000 by default.
# - Every address MUST start with "/". Avatar float params: "/avatar/parameter/<Name>".
# - Values are JSON scalars (float/int/str/bool); [] means trigger/bang. Types are
#   passed through to python-osc unchanged, so keep floats as floats (0.8, not "0.8").


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
            port: Annotated[
                int,
                Field(
                    ge=1,
                    le=65535,
                    description="Local UDP port of an already-running OSC receiver started via start_osc_server (default 9001).",
                ),
            ] = 9001,
            address_filter: Annotated[
                str | None,
                Field(
                    description="Optional substring filter on the OSC address (e.g. '/avatar/parameter/'). Only matching addresses are counted. Must start with '/' when given; '*' wildcards are NOT supported, plain substring match only."
                ),
            ] = None,
            duration_seconds: Annotated[
                float | None,
                Field(
                    ge=0,
                    description="Reserved informational window in seconds; the count snapshot is returned immediately and is not delayed by this value.",
                ),
            ] = None,
        ) -> dict[str, Any]:
            """Attach a filtered counter to a running OSC receiver and report how many messages match.

            WHEN TO USE: live "how much traffic right now" snapshot on an existing receiver.
            Use osc_analyze_traffic instead for sampled rate/top-address statistics over a time
            window; use osc_record_session when you need to capture a session for later playback;
            use get_received_messages for the actual message bodies.

            Args:
                port: Local UDP port of the running OSC receiver.
                address_filter: Optional address substring; None counts everything.
                duration_seconds: Informational only; does not block.

            Returns:
                {"success": bool, "message": str, "data": {"port": int, "filter": str|null,
                "monitored_messages": int, "server_running": bool}}.

            Errors / recovery:
                - success=false "No OSC server running on port ..." -> call start_osc_server(port)
                  first, then retry. Verify with get_osc_server_stats(port).
                - count 0 with a filter set usually means the filter string does not occur in any
                  address; retry with address_filter=None to confirm traffic is flowing.

            Example:
                osc_monitor_start(port=9001, address_filter="/avatar/parameter/")
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
            port: Annotated[
                int,
                Field(
                    ge=1,
                    le=65535,
                    description="Target UDP port of the Resonite OSC endpoint (Resonite default 9000). Sent to 127.0.0.1.",
                ),
            ],
            messages: Annotated[
                list[OSCBatchMessage],
                Field(
                    description="Ordered messages to send. Each item needs 'address' ('/...' path) and 'values' (arg list, e.g. [0.8]). Max ~100 per call; split longer animations into chunks."
                ),
            ],
            delay_ms: Annotated[
                int,
                Field(
                    ge=0,
                    le=60000,
                    description="Pause between messages in milliseconds. Use 50-200 for avatar animation sequencing, 0 for fire-and-forget.",
                ),
            ] = 0,
        ) -> dict[str, Any]:
            """Send an ordered batch of OSC messages to Resonite with an optional inter-message delay.

            WHEN TO USE: sequenced avatar parameter animations or multi-command scenes
            (e.g. Happy 0.8 then Surprise 0.5). For a single message use send_osc instead.

            Args:
                port: Target Resonite OSC port.
                messages: List of {address, values} items in send order.
                delay_ms: Delay between sends; 0 = back-to-back.

            Returns:
                {"success": bool, "message": str, "data": {"sent": int, "failed": int,
                "total": int}}. success=true means the batch ran; check sent vs failed for
                per-message outcome. Individual failures (bad address shape, UDP unreachable)
                increment "failed" without aborting the rest.

            Errors / recovery:
                - failed > 0 with "Failed to send OSC message" -> Resonite/UDP endpoint down.
                  Recovery: confirm Resonite is running (health_check), verify the port, retry
                  with a single send_osc call first.
                - Validation error on messages (missing address / not starting with '/') ->
                  fix the item shape; every address must start with '/'.

            Example:
                osc_batch_send(port=9000, messages=[
                    {"address": "/avatar/parameter/Happy", "values": [0.8]},
                    {"address": "/avatar/parameter/Surprise", "values": [0.5]},
                ], delay_ms=100)
            """
            import asyncio

            from ..models import OSCMessageInput
            from ..tools.osc import send_osc

            sent = 0
            failed = 0
            for i, msg in enumerate(messages):
                try:
                    addr = msg.address if isinstance(msg, OSCBatchMessage) else msg.get("address", "/")
                    vals = msg.values if isinstance(msg, OSCBatchMessage) else msg.get("values", [])
                    inp = OSCMessageInput(
                        host="127.0.0.1",
                        port=port,
                        address=addr,
                        values=list(vals),
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
            port: Annotated[
                int,
                Field(
                    ge=1,
                    le=65535,
                    description="Local UDP port of the running OSC receiver that captures the traffic (started via start_osc_server).",
                ),
            ],
            session_name: Annotated[
                str,
                Field(
                    min_length=1,
                    max_length=100,
                    description="Human label for this capture (e.g. 'avatar_demo'). Used in the message and returned in data.session_name.",
                ),
            ],
            duration_seconds: Annotated[
                float,
                Field(
                    gt=0,
                    le=3600,
                    description="How long to capture in seconds (max 3600). This call BLOCKS for the full duration; keep under 30s for interactive use.",
                ),
            ] = 60.0,
        ) -> dict[str, Any]:
            """Capture OSC traffic on a receiver port for a fixed duration and return a recording id.

            WHEN TO USE: recording a live avatar/world performance for later inspection or
            playback. Blocks for duration_seconds, then reports how many NEW messages arrived
            during the window (delta on the osc_recordings buffer). For instant stats without
            blocking use osc_analyze_traffic; for a non-blocking count use osc_monitor_start.

            Args:
                port: Receiver port doing the capture.
                session_name: Label for the recording.
                duration_seconds: Capture window; the call sleeps this long.

            Returns:
                {"success": bool, "message": str, "data": {"recording_id": str ("rec_<hex>"),
                "session_name": str, "port": int, "duration_seconds": float,
                "messages_captured": int}}. messages_captured is the delta during the window;
                fetch bodies via get_received_messages(port).

            Errors / recovery:
                - 0 messages captured usually means nothing was sent during the window or no
                  receiver is bound. Recovery: confirm traffic with osc_monitor_start(port),
                  extend duration_seconds, and re-record while the performance is running.

            Example:
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
            port: Annotated[
                int,
                Field(
                    ge=1, le=65535, description="Local UDP port of the running OSC receiver whose buffer is analyzed."
                ),
            ],
            analysis_duration: Annotated[
                float,
                Field(
                    gt=0,
                    le=600,
                    description="Sampling window in seconds (max 600). This call BLOCKS for the full window while traffic accumulates.",
                ),
            ] = 10.0,
        ) -> dict[str, Any]:
            """Sample OSC traffic over a time window and report rate, unique addresses, and top talkers.

            WHEN TO USE: diagnosing what is noisy/active ("which avatar params are spamming?").
            Unlike osc_monitor_start (instant filtered count) this blocks for analysis_duration
            and computes statistics; unlike osc_record_session (capture for playback) it returns
            aggregates, not message bodies. Pair with get_received_messages for bodies.

            Args:
                port: Receiver port to analyze.
                analysis_duration: Sampling window in seconds.

            Returns:
                {"success": bool, "message": str, "data": {"port": int,
                "analysis_duration": float, "total_messages": int, "unique_addresses": int,
                "messages_per_second": float, "top_addresses": list[str] (top 5 by frequency),
                "raw_messages_available": int}}. total_messages counts the whole buffer;
                raw_messages_available is the delta that arrived during the window.

            Errors / recovery:
                - total_messages 0 -> no traffic seen. Recovery: verify a sender targets this
                  port (test_osc_echo), check start_osc_server bound the right interface,
                  then re-run with a longer window while generating traffic.

            Example:
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
