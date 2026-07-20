"""Activity log for the resonite-mcp webapp backend.

Ported 2026-07-19 from web_sota/backend/server.py, which defined this
class but is never actually launched (the real backend is http_server.py
— see docs/WEBAPP_UPDATE_PLAN.md for the full story). Logging.tsx's
/api/logs* calls were pointing at code that never ran in production;
this module is that same code, now wired into the server that's real.
"""

from __future__ import annotations

import json
import time
from collections import deque
from typing import Any
from uuid import uuid4

_LEVEL_ORDER = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}


class ActivityLog:
    def __init__(self, max_entries: int = 2000) -> None:
        self.max_entries = max_entries
        self._entries: deque[dict[str, Any]] = deque(maxlen=max_entries)

    def add(self, level: str, kind: str, detail: str, meta: dict[str, Any] | None = None) -> str:
        eid = f"{time.time():.6f}.{uuid4().hex[:6]}"
        self._entries.append(
            {
                "id": eid,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
                "level": level.upper(),
                "kind": kind,
                "detail": detail,
                "meta": meta or {},
            }
        )
        return eid

    def info(self, kind: str, detail: str, **meta: Any) -> str:
        return self.add("INFO", kind, detail, meta)

    def warn(self, kind: str, detail: str, **meta: Any) -> str:
        return self.add("WARNING", kind, detail, meta)

    def error(self, kind: str, detail: str, **meta: Any) -> str:
        return self.add("ERROR", kind, detail, meta)

    def query(
        self,
        limit: int = 50,
        offset: int = 0,
        level: str | None = None,
        kind: str | None = None,
        search: str | None = None,
        sort: str = "desc",
        after_id: str | None = None,
    ) -> dict[str, Any]:
        entries = list(self._entries)
        if after_id:
            try:
                at = float(after_id.split(".")[0])
                entries = [e for e in entries if float(e["id"].split(".")[0]) > at]
            except (ValueError, IndexError):
                pass
        if level:
            min_level = _LEVEL_ORDER.get(level.upper(), 1)
            entries = [e for e in entries if _LEVEL_ORDER.get(e["level"], 1) >= min_level]
        if kind:
            entries = [e for e in entries if e["kind"] == kind]
        if search:
            q = search.lower()
            entries = [e for e in entries if q in e["detail"].lower()]
        entries.sort(key=lambda e: e["id"], reverse=(sort == "desc"))
        total = len(entries)
        page = entries[offset : offset + limit]
        return {
            "entries": page,
            "total": total,
            "limit": limit,
            "offset": offset,
            "max_entries": self.max_entries,
            "sort": sort,
        }

    def stats(self) -> dict[str, Any]:
        levels: dict[str, int] = {}
        kinds: dict[str, int] = {}
        for e in self._entries:
            levels[e["level"]] = levels.get(e["level"], 0) + 1
            kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
        return {"total": len(self._entries), "max_entries": self.max_entries, "levels": levels, "kinds": kinds}

    def export(self, format: str = "json", **filters: Any) -> str:
        result = self.query(limit=self.max_entries, **filters)
        if format == "csv":
            import csv
            import io

            buf = io.StringIO()
            w = csv.writer(buf)
            w.writerow(["id", "timestamp", "level", "kind", "detail", "meta"])
            for e in result["entries"]:
                w.writerow([e["id"], e["timestamp"], e["level"], e["kind"], e["detail"], json.dumps(e["meta"])])
            return buf.getvalue()
        return json.dumps(result["entries"], indent=2)

    def clear(self) -> None:
        self._entries.clear()


# Module-level singleton — matches the pattern the orphaned server.py used
# (a single shared instance imported wherever logging is needed), just
# actually importable from the server that's real now.
activity_log = ActivityLog()
