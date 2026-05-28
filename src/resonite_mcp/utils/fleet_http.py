"""HTTP helpers for cross-fleet MCP tool calls."""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_BLENDER_URL = "http://127.0.0.1:10849"
DEFAULT_GIMP_URL = "http://127.0.0.1:10773"
DEFAULT_INKSCAPE_URL = "http://127.0.0.1:10900"
DEFAULT_RESONITE_URL = "http://127.0.0.1:10979"

_HEALTH_PATHS = ("/api/v1/health", "/api/health", "/health", "/v1/health")
_TOOL_PATHS = ("/api/v1/tool", "/v1/tool", "/tool")


async def check_http_health(base_url: str) -> bool:
    for path in _HEALTH_PATHS:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(base_url.rstrip("/") + path)
                if response.status_code == 200:
                    return True
        except httpx.HTTPError:
            continue
    return False


async def call_http_tool(
    base_url: str,
    tool: str,
    params: dict[str, Any],
    *,
    timeout: float = 300.0,
) -> dict[str, Any]:
    """Call a fleet MCP POST tool endpoint (tries common paths)."""
    last_error = "no endpoint responded"
    for tool_path in _TOOL_PATHS:
        url = base_url.rstrip("/") + tool_path
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json={"tool": tool, "params": params})
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            last_error = str(exc)
            continue

        if isinstance(body, dict) and body.get("data") is not None:
            data = body["data"]
            if isinstance(data, dict):
                if body.get("success") is False and "success" not in data:
                    data = {**data, "success": False}
                elif "success" not in data:
                    data = {**data, "success": bool(body.get("success", True))}
                return data
        return body if isinstance(body, dict) else {"success": False, "error": "Invalid tool response"}

    logger.warning("HTTP tool call failed tool=%s base=%s error=%s", tool, base_url, last_error)
    return {"success": False, "error": last_error, "tool": tool}
