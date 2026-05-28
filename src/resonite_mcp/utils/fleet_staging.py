"""Filesystem staging helpers for fleet UI/asset handoff."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_FLEET_STAGING = Path("D:/Temp/fleet_pipeline/resonite_fleet")
DEFAULT_INKSCAPE_UI_STAGING = Path("D:/Temp/fleet_pipeline/inkscape_sim_art/resonite_ui")

_UI_SUFFIXES = {".svg", ".png", ".webp", ".jpg", ".jpeg"}
_MODEL_SUFFIXES = {".glb", ".gltf", ".vrm", ".fbx", ".obj", ".spz"}


def list_staging_files(staging_dir: Path) -> dict[str, Any]:
    if not staging_dir.is_dir():
        return {"success": True, "files": [], "staging_dir": str(staging_dir)}
    files = sorted(str(p.resolve()) for p in staging_dir.rglob("*") if p.is_file())
    return {"success": True, "files": files, "staging_dir": str(staging_dir.resolve())}


def classify_staged_assets(files: list[str]) -> dict[str, list[str]]:
    ui: list[str] = []
    models: list[str] = []
    other: list[str] = []
    for raw in files:
        path = Path(raw)
        suffix = path.suffix.lower()
        if suffix in _UI_SUFFIXES:
            ui.append(raw)
        elif suffix in _MODEL_SUFFIXES:
            models.append(raw)
        else:
            other.append(raw)
    return {"ui": ui, "models": models, "other": other}


async def stage_file(
    *,
    source_path: str,
    staging_dir: Path,
    subdir: str = "incoming",
) -> dict[str, Any]:
    src = Path(source_path)
    if not src.is_file():
        return {"success": False, "error": f"Source not found: {source_path}"}

    dest_dir = staging_dir / subdir
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        shutil.copy2(src, dest)
    except OSError as exc:
        logger.exception("Staging copy failed for %s", source_path)
        return {"success": False, "error": str(exc)}

    return {
        "success": True,
        "source_path": str(src.resolve()),
        "staged_path": str(dest.resolve()),
        "staging_dir": str(staging_dir.resolve()),
    }
