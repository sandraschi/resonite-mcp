"""Prefab App Tools — Rich in-chat cards for Resonite MCP.

Provides FastMCP app=True tools that render Prefab UI cards for dashboard
status and inventory browsing in supporting MCP clients (Claude Desktop,
Cursor when supported).

Disable with RESONITE_PREFAB_APPS=0.

## Return Format
All tools return ToolResult with structured_content=PrefabApp when Prefab
is available; plain-text fallback otherwise.
"""

import logging
from typing import Any

from ..server import server

logger = logging.getLogger(__name__)


@server.tool(app=True)
async def resonite_dashboard_card() -> dict[str, Any]:
    """Show Resonite MCP fleet status as a rich Prefab card.

    Displays server health, Resonite process status, OSC connectivity,
    ResoniteLink status, and tool counts in a scannable card.
    """
    from ..server import is_resonite_running, resonite_link_client

    try:
        from ..tools.osc import osc_servers

        osc_active = len(osc_servers) > 0
        osc_ports = list(osc_servers.keys())
    except Exception:
        osc_active = False
        osc_ports = []

    res_running = is_resonite_running()
    rl_connected = resonite_link_client.running if resonite_link_client else False

    return {
        "status": "ok",
        "server": "Resonite MCP",
        "version": "0.8.0",
        "resonite_running": res_running,
        "osc_active": osc_active,
        "osc_ports": osc_ports,
        "resonite_link_connected": rl_connected,
        "tool_count": 55,
        "ports": {"frontend": 10978, "backend": 10979},
        "summary": (
            f"Resonite: {'Running' if res_running else 'Not running'} | "
            f"OSC: {'Active' if osc_active else 'Inactive'} | "
            f"Link: {'Connected' if rl_connected else 'Disconnected'}"
        ),
    }


@server.tool(app=True)
async def resonite_inventory_card(limit: int = 10) -> dict[str, Any]:
    """Show a browsable inventory preview as a rich Prefab card.

    Displays recent inventory items with names, types, and availability
    status in a scannable card format.

    Args:
        limit: Max items to display (default 10)
    """
    try:
        from ..models import InventoryListInput
        from .inventory import resonite_inventory_list

        result = await resonite_inventory_list(InventoryListInput(limit=min(limit, 50), offset=0))
        items = result.get("items", [])
        total = result.get("total_count", 0)

        return {
            "status": result.get("status", "error"),
            "items": list(items)[:limit] if items else [],
            "total_count": total,
            "display_count": min(len(items), limit),
            "has_more": result.get("pagination", {}).get("has_more", False),
        }
    except Exception as e:
        logger.error("Inventory card failed: %s", e)
        return {"status": "error", "items": [], "total_count": 0, "error": str(e)}
