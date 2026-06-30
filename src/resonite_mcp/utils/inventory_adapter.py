"""Inventory adapter: mock catalog vs live OSC/API when available."""

from __future__ import annotations

import os
from typing import Any, Literal

InventoryMode = Literal["mock", "live", "auto"]

_MOCK_CATALOG: list[dict[str, Any]] = [
    {"id": "mock_avatar_01", "name": "Fleet Test Avatar", "type": "avatar", "source": "mock"},
    {"id": "mock_world_01", "name": "Agent Lab World", "type": "world", "source": "mock"},
    {"id": "mock_prop_ui", "name": "Inkscape UI Pack", "type": "object", "source": "mock"},
]


def get_inventory_mode() -> InventoryMode:
    raw = os.getenv("RESONITE_INVENTORY_MODE", "auto").strip().lower()
    if raw in {"mock", "live", "auto"}:
        return raw  # type: ignore[return-value]
    return "auto"


async def list_inventory_items(
    *,
    item_type: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    mode = get_inventory_mode()
    if mode == "mock":
        items = _MOCK_CATALOG
    elif mode == "live":
        items = await _list_live_inventory(item_type=item_type, limit=limit)
        if items is None:
            return {
                "success": False,
                "mode": "live",
                "error": "Live inventory API unavailable; set RESONITE_INVENTORY_MODE=mock",
                "items": [],
            }
    else:
        items = await _list_live_inventory(item_type=item_type, limit=limit)
        if items is None:
            items = _MOCK_CATALOG
            mode = "mock"
        else:
            mode = "live"

    if item_type:
        items = [row for row in items if str(row.get("type", "")).lower() == item_type.lower()]

    return {
        "success": True,
        "mode": mode,
        "items": items[:limit],
        "count": min(len(items), limit),
    }


async def _list_live_inventory(*, item_type: str | None, limit: int) -> list[dict[str, Any]] | None:
    try:
        from ..models import InventoryListInput
        from ..tools.inventory import resonite_inventory_list

        result = await resonite_inventory_list(InventoryListInput(item_type=item_type, limit=limit, offset=0))
        if result.get("status") != "success":
            return None
        payload = result.get("data") or result
        items = payload.get("items") if isinstance(payload, dict) else None
        return items if isinstance(items, list) else None
    except Exception:
        return None
