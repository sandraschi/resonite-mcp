"""Server-side log of world slots spawned through the HTTP webapp path.

Every entry records what was created, how, and the slot ID needed to
delete it again. Coverage is deliberately narrow and stated, not silent:

- RECORDED: /rl/world/spawn-model results, /api/world-builder/build rooms.
- NOT recorded: MCP-tool spawns (tools/depot.py bypasses HTTP entirely)
  and inventory OSC spawns (fire-and-forget, no slot ID comes back).

Storage is a plain JSON file under data/ (gitignored) so the list
survives backend restarts. Entries whose slots were deleted in-world
simply fail at delete time with the backend's real error.
"""

from __future__ import annotations

import datetime
import json
import uuid
from pathlib import Path
from typing import Any

from .data_dir import data_dir as _resolve_data_dir


def default_path() -> Path:
    data_dir = _resolve_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "spawn_registry.json"


def _load(path: Path | None = None) -> list[dict[str, Any]]:
    target = path or default_path()
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return raw if isinstance(raw, list) else []


def _save(entries: list[dict[str, Any]], path: Path | None = None) -> None:
    target = path or default_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def record(
    kind: str,
    name: str,
    slot_id: str | None = None,
    detail: str = "",
    path: Path | None = None,
) -> dict[str, Any]:
    """Append one spawn entry, newest-last on disk. Returns the entry."""
    entries = _load(path)
    entry = {
        "id": uuid.uuid4().hex[:12],
        "kind": kind,
        "name": name,
        "slot_id": slot_id,
        "detail": detail,
        "created_at": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
    }
    entries.append(entry)
    _save(entries, path)
    return entry


def list_entries(path: Path | None = None) -> list[dict[str, Any]]:
    """Newest first, for the Spawned page."""
    return list(reversed(_load(path)))


def remove(entry_id: str, path: Path | None = None) -> dict[str, Any] | None:
    """Drop one entry by id. Returns the removed entry, or None."""
    entries = _load(path)
    for i, entry in enumerate(entries):
        if entry.get("id") == entry_id:
            removed = entries.pop(i)
            _save(entries, path)
            return removed
    return None
