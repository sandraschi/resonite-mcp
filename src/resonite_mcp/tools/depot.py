"""Model + texture depot - backport of overte-mcp's binary-file depot (2026-09-02).

Architectural note: overte-mcp's depot serves files over HTTP because Overte's spawn call
takes a URL. ResoniteLink is different - import_texture_file()/gltf_to_mesh_json() both take
a LOCAL FILE PATH on the machine Resonite itself reads from (see resonite_link.py's own
docstrings: "not the machine running this client - matters if they differ"). So this depot is
a plain on-disk folder + manifest.json, no HTTP static-mount needed - depot_spawn resolves a
name straight to a path and feeds it into the existing import pipeline.

Models: .glb/.vrm/.gltf, converted via utils.gltf_meshjson.gltf_to_mesh_json() (the exact path
already live-verified for Nekomimi-chan's full VRM mesh) then client.spawn_mesh(). VRM needs
no separate conversion step here - gltf_to_mesh_json reads the GLB binary container directly,
VRM-specific extensions are just ignored.

Textures: .png/.jpg/.jpeg, imported via client.import_texture_file() directly - no mesh
involved, so depot_spawn for a texture just returns the asset_url for the caller to wire into
a PBS_Metallic component (see resonite_link_add_component / resonite_link_spawn_mesh).
"""

import datetime
import json
import logging
import zipfile
from pathlib import Path
from typing import Any

from ..server import server
from ..utils.gltf_meshjson import GltfConversionError, gltf_to_mesh_json
from .resonite_link import get_client

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_MODELS_DEPOT = _REPO_ROOT / "models"
_MODELS_MANIFEST_PATH = _MODELS_DEPOT / "manifest.json"
_MODEL_EXTENSIONS = {".glb", ".vrm", ".gltf"}

_TEXTURES_DEPOT = _REPO_ROOT / "data" / "textures"
_TEXTURES_MANIFEST_PATH = _TEXTURES_DEPOT / "manifest.json"
_TEXTURE_EXTENSIONS = {".png", ".jpg", ".jpeg"}

_BACKUPS_DIR = _REPO_ROOT / "data" / "backups"

_DEPOTS: dict[str, dict[str, Any]] = {
    "model": {"dir": _MODELS_DEPOT, "manifest": _MODELS_MANIFEST_PATH, "extensions": _MODEL_EXTENSIONS},
    "texture": {"dir": _TEXTURES_DEPOT, "manifest": _TEXTURES_MANIFEST_PATH, "extensions": _TEXTURE_EXTENSIONS},
}


def _load_manifest(path: Path) -> list[dict[str, Any]]:
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _save_manifest(path: Path, manifest: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)


def _depot_or_error(kind: str) -> dict[str, Any] | None:
    return _DEPOTS.get(kind)


@server.tool()
async def resonite_link_depot_list(kind: str) -> dict[str, Any]:
    """List entries in the model or texture depot.

    kind: "model" or "texture".

    ## Return Format
    {"status": str, "kind": str, "items": [{"name","description","category","exists","size"}], "count": int}
    """
    depot = _depot_or_error(kind)
    if depot is None:
        return {"status": "error", "message": f"Unknown kind {kind!r}. Use 'model' or 'texture'."}
    manifest = _load_manifest(depot["manifest"])
    items = []
    for m in manifest:
        fp = depot["dir"] / m["name"]
        entry = dict(m)
        entry["exists"] = fp.exists()
        if fp.exists():
            entry["size"] = fp.stat().st_size
        items.append(entry)
    return {"status": "success", "kind": kind, "items": items, "count": len(items)}


@server.tool()
async def resonite_link_depot_add(
    kind: str,
    file_path: str,
    description: str = "",
    category: str = "uncategorized",
) -> dict[str, Any]:
    """Copy a local file into the model or texture depot and register it in the manifest.

    file_path must already exist on disk (this copies it in, it does not fetch URLs).
    Fails if a depot entry with the same filename already exists - use
    resonite_link_depot_update_metadata to change description/category, or
    resonite_link_depot_remove first to replace it.

    ## Return Format
    {"status": str, "kind": str, "name": str, "size": int}
    """
    depot = _depot_or_error(kind)
    if depot is None:
        return {"status": "error", "message": f"Unknown kind {kind!r}. Use 'model' or 'texture'."}

    src = Path(file_path)
    if not src.exists():
        return {"status": "error", "message": f"File not found: {file_path}"}
    ext = src.suffix.lower()
    if ext not in depot["extensions"]:
        return {
            "status": "error",
            "message": f"Unsupported {kind} extension {ext!r}. Allowed: {sorted(depot['extensions'])}",
        }

    dest = depot["dir"] / src.name
    if dest.exists():
        return {"status": "error", "message": f"{kind.capitalize()} {src.name!r} already exists in the depot"}

    depot["dir"].mkdir(parents=True, exist_ok=True)
    dest.write_bytes(src.read_bytes())
    manifest = _load_manifest(depot["manifest"])
    manifest.append({"name": src.name, "description": description, "category": category})
    _save_manifest(depot["manifest"], manifest)
    return {"status": "success", "kind": kind, "name": src.name, "size": dest.stat().st_size}


@server.tool()
async def resonite_link_depot_update_metadata(
    kind: str,
    name: str,
    description: str | None = None,
    category: str | None = None,
) -> dict[str, Any]:
    """Update description/category for an existing depot entry (file itself untouched).

    ## Return Format
    {"status": str, "kind": str, "name": str}
    """
    depot = _depot_or_error(kind)
    if depot is None:
        return {"status": "error", "message": f"Unknown kind {kind!r}. Use 'model' or 'texture'."}
    fp = depot["dir"] / name
    if not fp.exists():
        return {"status": "error", "message": f"{kind.capitalize()} not found: {name}"}

    manifest = _load_manifest(depot["manifest"])
    found = False
    for m in manifest:
        if m["name"] == name:
            if description is not None:
                m["description"] = description
            if category is not None:
                m["category"] = category
            found = True
            break
    if not found:
        manifest.append({"name": name, "description": description or "", "category": category or "uncategorized"})
    _save_manifest(depot["manifest"], manifest)
    return {"status": "success", "kind": kind, "name": name}


@server.tool()
async def resonite_link_depot_remove(kind: str, name: str) -> dict[str, Any]:
    """Delete a depot entry: removes the file on disk and its manifest entry.

    ## Return Format
    {"status": str, "kind": str, "name": str}
    """
    depot = _depot_or_error(kind)
    if depot is None:
        return {"status": "error", "message": f"Unknown kind {kind!r}. Use 'model' or 'texture'."}
    fp = depot["dir"] / name
    if fp.exists():
        fp.unlink()
    manifest = _load_manifest(depot["manifest"])
    manifest = [m for m in manifest if m["name"] != name]
    _save_manifest(depot["manifest"], manifest)
    return {"status": "success", "kind": kind, "name": name}


@server.tool()
async def resonite_link_depot_spawn(
    kind: str,
    name: str,
    pos_x: float = 0.0,
    pos_y: float = 0.0,
    pos_z: float = 0.0,
    slot_name: str = "",
) -> dict[str, Any]:
    """Spawn a depot model into the world, or import a depot texture and hand back its asset URL.

    kind="model": converts the .glb/.vrm/.gltf via gltf_to_mesh_json() (the same live-verified
    path used for Nekomimi-chan) and spawns it with client.spawn_mesh() at (pos_x,pos_y,pos_z).

    kind="texture": imports via client.import_texture_file() and returns the asset_url only -
    there is no mesh to attach it to here. Wire it into a material yourself, e.g.:
        resonite_link_add_component(slot_id, "[FrooxEngine]FrooxEngine.PBS_Metallic",
            {"AlbedoTexture": {"$type": "reference", "targetId": ...}})  # see resonite_link.py

    ## Return Format
    model: {"status": str, "kind": "model", "slot_id": str, "asset_url": str, ...spawn_mesh() extras}
    texture: {"status": str, "kind": "texture", "asset_url": str}
    """
    depot = _depot_or_error(kind)
    if depot is None:
        return {"status": "error", "message": f"Unknown kind {kind!r}. Use 'model' or 'texture'."}
    fp = depot["dir"] / name
    if not fp.exists():
        return {"status": "error", "message": f"{kind.capitalize()} not found in depot: {name}"}

    client = await get_client()
    if not client.running:
        return {"status": "error", "message": "ResoniteLink not connected."}

    if kind == "texture":
        try:
            asset_url = await client.import_texture_file(str(fp))
        except Exception as e:
            return {"status": "error", "message": str(e)}
        return {"status": "success", "kind": "texture", "asset_url": asset_url}

    try:
        mesh_data = gltf_to_mesh_json(fp)
    except GltfConversionError as e:
        return {"status": "error", "message": f"Could not convert {name}: {e}"}
    try:
        result = await client.spawn_mesh(
            mesh_data["vertices"],
            mesh_data["submeshes"],
            position={"x": pos_x, "y": pos_y, "z": pos_z},
            name=slot_name or Path(name).stem,
        )
    except Exception as e:
        return {"status": "error", "message": str(e)}
    return {"status": "success", "kind": "model", **result}


@server.tool()
async def resonite_link_depot_backup() -> dict[str, Any]:
    """Zip-snapshot the model and texture depots into data/backups/<timestamp>.zip.
    Does not touch the live Resonite world - this backs up depot files this server manages
    locally, not anything inside a running session.

    ## Return Format
    {"status": str, "name": str, "size": int}
    """
    _BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    backup_path = _BACKUPS_DIR / f"resonite-mcp-backup-{ts}.zip"

    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for kind, depot in _DEPOTS.items():
            d = depot["dir"]
            if not d.exists():
                continue
            for fp in d.rglob("*"):
                if fp.is_file():
                    zf.write(fp, arcname=f"{kind}s/{fp.relative_to(d)}")

    return {"status": "success", "name": backup_path.name, "size": backup_path.stat().st_size}


@server.tool()
async def resonite_link_depot_list_backups() -> dict[str, Any]:
    """List available depot backup archives, newest first.

    ## Return Format
    {"status": str, "backups": [{"name","size","created_at"}], "count": int}
    """
    if not _BACKUPS_DIR.exists():
        return {"status": "success", "backups": [], "count": 0}
    items = sorted(
        (
            {
                "name": p.name,
                "size": p.stat().st_size,
                "created_at": datetime.datetime.fromtimestamp(p.stat().st_mtime, tz=datetime.UTC).isoformat(),
            }
            for p in _BACKUPS_DIR.glob("*.zip")
        ),
        key=lambda x: x["created_at"],
        reverse=True,
    )
    return {"status": "success", "backups": items, "count": len(items)}


@server.tool()
async def resonite_link_depot_restore_backup(name: str) -> dict[str, Any]:
    """Restore a depot backup archive, OVERWRITING current files in the model/texture depots
    (matching names only - does not delete files the backup doesn't mention). Does not touch
    the live Resonite world.

    ## Return Format
    {"status": str, "name": str, "restored": int}
    """
    backup_path = _BACKUPS_DIR / name
    if not backup_path.exists() or backup_path.suffix != ".zip":
        return {"status": "error", "message": f"Backup not found: {name}"}

    depot_by_prefix = {f"{kind}s": depot["dir"] for kind, depot in _DEPOTS.items()}
    restored = 0
    with zipfile.ZipFile(backup_path, "r") as zf:
        for member in zf.namelist():
            prefix, _, rel = member.partition("/")
            target_dir = depot_by_prefix.get(prefix)
            if not target_dir or not rel:
                continue
            target_path = target_dir / rel
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(zf.read(member))
            restored += 1

    return {"status": "success", "name": name, "restored": restored}
