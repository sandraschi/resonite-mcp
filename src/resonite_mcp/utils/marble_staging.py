"""Marble / World Labs / fab art staging helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

DEFAULT_MARBLE_STAGING = Path("D:/Temp/fleet_pipeline/resonite_marble")
DEFAULT_FAB_STAGING = Path("D:/Temp/fleet_pipeline/inkscape_fab_art")
DEFAULT_WORLDLABS_URL = "http://127.0.0.1:10865"

_SPLAT_SUFFIXES = {".spz", ".ply", ".splat"}
_DXF_SUFFIXES = {".dxf", ".svg", ".png"}


def list_marble_files(*roots: Path) -> dict[str, Any]:
    splats: list[str] = []
    overlays: list[str] = []
    dxf_refs: list[str] = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            resolved = str(path.resolve())
            suffix = path.suffix.lower()
            if suffix in _SPLAT_SUFFIXES:
                splats.append(resolved)
            elif suffix in _DXF_SUFFIXES:
                if suffix == ".dxf":
                    dxf_refs.append(resolved)
                else:
                    overlays.append(resolved)
    return {
        "splats": splats,
        "overlays": overlays,
        "dxf_refs": dxf_refs,
        "files": splats + overlays + dxf_refs,
    }
