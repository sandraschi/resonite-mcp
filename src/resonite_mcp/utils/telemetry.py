"""Prometheus metrics helpers for resonite-mcp."""

from __future__ import annotations

import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

_metrics_initialized = False
_tool_calls_total = None
_tool_duration_seconds = None
_resonite_running = None
_resonite_link_connected = None
_execution_mode = None
_fleet_imports_total = None
_app_info = None


def metrics_enabled() -> bool:
    value = os.getenv("RESONITE_MCP_METRICS_ENABLED", "true").strip().lower()
    return value not in {"0", "false", "no", "off"}


def init_metrics() -> None:
    """Initialize Prometheus metrics (idempotent)."""
    global _metrics_initialized, _tool_calls_total, _tool_duration_seconds
    global _resonite_running, _resonite_link_connected, _execution_mode
    global _fleet_imports_total, _app_info

    if _metrics_initialized or not metrics_enabled():
        return

    try:
        from prometheus_client import REGISTRY

        if "resonite_mcp_tool_calls_total" in getattr(REGISTRY, "_names_to_collectors", {}):
            _metrics_initialized = True
            return
    except ImportError:
        pass

    try:
        from prometheus_client import Counter, Gauge, Histogram, Info
    except ImportError:
        logger.warning(
            "prometheus_client not installed; metrics disabled. "
            "Install with: uv sync --extra monitoring"
        )
        return

    try:
        _tool_calls_total = Counter(
            "resonite_mcp_tool_calls_total",
            "Total MCP tool invocations",
            ["tool", "status"],
        )
        _tool_duration_seconds = Histogram(
            "resonite_mcp_tool_duration_seconds",
            "MCP tool execution duration",
            ["tool"],
            buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
        )
        _resonite_running = Gauge(
            "resonite_mcp_resonite_running",
            "Whether Resonite.exe is running on the host (1=yes)",
        )
        _resonite_link_connected = Gauge(
            "resonite_mcp_resonite_link_connected",
            "Whether ResoniteLink WebSocket is connected (1=yes)",
        )
        _execution_mode = Gauge(
            "resonite_mcp_execution_mode",
            "Execution mode: 0=hands_off, 1=hands_in",
        )
        _fleet_imports_total = Counter(
            "resonite_mcp_fleet_imports_total",
            "Fleet import operations via resonite_fleet",
            ["operation", "status"],
        )
        _app_info = Info("resonite_mcp", "Resonite MCP application info")

        from resonite_mcp import __version__

        _app_info.info({"version": __version__, "service": "resonite-mcp"})
    except ValueError as exc:
        if "Duplicated timeseries" not in str(exc):
            raise
        logger.debug("Prometheus metrics already registered")

    _metrics_initialized = True


def record_tool_call(tool: str, status: str, duration_seconds: float | None = None) -> None:
    if not _metrics_initialized:
        init_metrics()
    if _tool_calls_total is not None:
        _tool_calls_total.labels(tool=tool, status=status).inc()
    if duration_seconds is not None and _tool_duration_seconds is not None:
        _tool_duration_seconds.labels(tool=tool).observe(duration_seconds)


def record_fleet_import(operation: str, status: str) -> None:
    if not _metrics_initialized:
        init_metrics()
    if _fleet_imports_total is not None:
        _fleet_imports_total.labels(operation=operation, status=status).inc()


def set_resonite_running(running: bool) -> None:
    if not _metrics_initialized:
        init_metrics()
    if _resonite_running is not None:
        _resonite_running.set(1 if running else 0)


def set_resonite_link_connected(connected: bool) -> None:
    if not _metrics_initialized:
        init_metrics()
    if _resonite_link_connected is not None:
        _resonite_link_connected.set(1 if connected else 0)


def set_execution_mode(hands_in: bool) -> None:
    if not _metrics_initialized:
        init_metrics()
    if _execution_mode is not None:
        _execution_mode.set(1 if hands_in else 0)


def update_runtime_gauges() -> None:
    """Refresh host/runtime gauges from server helpers."""
    try:
        from resonite_mcp.server import is_resonite_running, resonite_link_client

        set_resonite_running(is_resonite_running())
        link_ok = bool(resonite_link_client and resonite_link_client.connected)
        set_resonite_link_connected(link_ok)
        set_execution_mode(is_resonite_running())
    except Exception as exc:
        logger.debug("Runtime gauge update skipped: %s", exc)


def render_metrics() -> bytes:
    if not _metrics_initialized:
        return b"# metrics disabled\n"
    update_runtime_gauges()
    from prometheus_client import generate_latest

    return generate_latest()


def metrics_content_type() -> str:
    from prometheus_client import CONTENT_TYPE_LATEST

    return CONTENT_TYPE_LATEST


def start_metrics_server(port: int | None = None) -> None:
    if not _metrics_initialized:
        init_metrics()
    if not _metrics_initialized:
        return

    scrape_port = port or int(os.getenv("PROMETHEUS_PORT", "9079"))
    try:
        from prometheus_client import start_http_server

        start_http_server(scrape_port)
        logger.info("Prometheus metrics server listening on port %s", scrape_port)
    except OSError as exc:
        logger.error("Failed to start Prometheus metrics server on %s: %s", scrape_port, exc)


def register_metrics_routes(fastapi_app: Any) -> None:
    """Attach /api/metrics and /metrics to a FastAPI or FastMCP app."""
    from starlette.requests import Request
    from starlette.responses import Response

    if hasattr(fastapi_app, "get"):

        @fastapi_app.get("/api/metrics")
        async def _api_metrics() -> Response:
            return Response(content=render_metrics(), media_type=metrics_content_type())

        @fastapi_app.get("/metrics")
        async def _metrics_endpoint() -> Response:
            return Response(content=render_metrics(), media_type=metrics_content_type())

        logger.info("Registered /api/metrics and /metrics on FastAPI app")
        return

    if hasattr(fastapi_app, "custom_route"):

        @fastapi_app.custom_route("/api/metrics", methods=["GET"])
        async def _api_metrics_mcp(_request: Request) -> Response:
            return Response(content=render_metrics(), media_type=metrics_content_type())

        @fastapi_app.custom_route("/metrics", methods=["GET"])
        async def _metrics_route_mcp(_request: Request) -> Response:
            return Response(content=render_metrics(), media_type=metrics_content_type())

        logger.info("Registered /api/metrics and /metrics on FastMCP app")


def install_tool_call_wrapper(app: Any) -> None:
    if not metrics_enabled():
        return
    init_metrics()
    if not _metrics_initialized:
        return
    if getattr(app, "_telemetry_wrapped", False):
        return

    original = app.call_tool

    async def wrapped_call_tool(name: str, arguments: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        with ToolMetricsContext(name) as ctx:
            try:
                return await original(name, arguments or {}, **kwargs)
            except Exception:
                ctx.status = "error"
                raise

    app.call_tool = wrapped_call_tool
    app._telemetry_wrapped = True
    logger.info("Installed MCP tool telemetry wrapper")


class ToolMetricsContext:
    def __init__(self, tool: str) -> None:
        self.tool = tool
        self._start = 0.0
        self.status = "ok"

    def __enter__(self) -> ToolMetricsContext:
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if exc_type is not None:
            self.status = "error"
        duration = time.perf_counter() - self._start
        record_tool_call(self.tool, self.status, duration)
