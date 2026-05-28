"""Smoke test for resonite-mcp Agent Lab tool surface and metrics."""

from __future__ import annotations

import asyncio
import sys


async def main() -> int:
    from resonite_mcp.http_server import app
    from resonite_mcp.tools.fleet_tools import resonite_fleet
    from resonite_mcp.utils.telemetry import metrics_enabled, render_metrics

    print("=== resonite-mcp smoke test ===")

    presets = await resonite_fleet("list_presets")
    if not presets.get("success"):
        print(f"FAIL list_presets: {presets}")
        return 1
    print("OK resonite_fleet list_presets")

    mode = await resonite_fleet("execution_mode")
    print(f"OK execution_mode: {mode.get('data', {}).get('mode')}")

    pf = await resonite_fleet("list_protoflux_presets")
    if not pf.get("success"):
        print(f"FAIL list_protoflux_presets: {pf}")
        return 1
    print(f"OK protoflux presets: {pf.get('data', {}).get('count')}")

    marble = await resonite_fleet("list_marble_staging")
    if not marble.get("success"):
        print(f"FAIL list_marble_staging: {marble}")
        return 1
    print("OK list_marble_staging")

    inventory = await resonite_fleet("inventory_status")
    if not inventory.get("success"):
        print(f"FAIL inventory_status: {inventory}")
        return 1
    print(f"OK inventory_status mode={inventory.get('data', {}).get('mode')}")

    from resonite_mcp.tools.voice_tools import resonite_voice

    voice = await resonite_voice("list_macros")
    if not voice.get("success"):
        print(f"FAIL resonite_voice list_macros: {voice}")
        return 1
    print("OK resonite_voice list_macros")

    paths = {getattr(r, "path", None) for r in app.routes}
    for route in ("/api/metrics", "/metrics", "/api/v1/health"):
        if route not in paths:
            print(f"FAIL missing route: {route}")
            return 1
    print("OK metrics and health routes registered")

    metrics_body = render_metrics()
    if metrics_enabled() and b"disabled" in metrics_body:
        print("WARN metrics enabled but prometheus_client may be missing")
    else:
        print(f"OK metrics bytes={len(metrics_body)}")

    print("=== smoke test passed ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
