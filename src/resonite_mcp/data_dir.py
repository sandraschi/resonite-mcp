"""Where persistent app-written JSON (the spawn registry) lives.

In normal dev use (`uv run`), this is `<repo>/data`. In the frozen Tauri app,
`Path(__file__).resolve().parents[N]` resolves into PyInstaller's onefile
_MEIPASS extraction temp directory — a fresh path created on every launch and
wiped on exit. Writing the registry there means every recorded spawn would be
silently lost the next time the app is closed and reopened (see obs-mcp/
norirobotics-mcp/depot-mcp's identical fix and TAURI_PRODUCTION_PITFALLS.md
§13 item 15). Frozen builds use %LOCALAPPDATA%\\{identifier}\\data instead,
matching where the Rust side writes its own logs (must match
native/tauri.conf.json's "identifier").
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_TAURI_IDENTIFIER = "com.sandraschi.resonite-mcp"


def data_dir() -> Path:
    override = os.getenv("RESONITE_MCP_DATA_DIR")
    if override:
        return Path(override)
    if getattr(sys, "frozen", False):
        local_app_data = os.getenv("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / _TAURI_IDENTIFIER / "data"
    return Path(__file__).resolve().parents[2] / "data"
