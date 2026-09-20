"""Procedural room builder over ResoniteLink (live-verified primitives only).

Every component type and member used here was verified against a live
session on 2026-09-20 via /rl/reflect:
  BoxMesh.Size (float3), MeshRenderer.Mesh/Materials, PBS_Metallic.AlbedoColor,
  Grabbable (defaults), BoxCollider.Size/Offset, Light.Color/Intensity/Range.

The per-piece assembly mirrors ResoniteLinkClient.spawn_mesh (importMeshJSON
-> addSlot -> StaticMesh -> MeshRenderer -> PBS_Metallic), except boxes use
the engine's procedural BoxMesh (Assets/Procedural Meshes) instead of an
uploaded mesh asset -- no mesh upload, no UVs, no winding pitfalls.

Furniture dimensions are stylised low-poly (Kenney-like) rather than
realistic: chunky proportions read well at VR scale and keep every piece a
single box. Nothing here is measured from a real catalogue; sizes are chosen
to look right, stated as-is.
"""

from __future__ import annotations

import logging
from typing import Any

from .resonite_link import rl_list, rl_ref, rl_value

logger = logging.getLogger(__name__)

BOX_MESH = "[FrooxEngine]FrooxEngine.BoxMesh"
MESH_RENDERER = "[FrooxEngine]FrooxEngine.MeshRenderer"
PBS_METALLIC = "[FrooxEngine]FrooxEngine.PBS_Metallic"
GRABBABLE = "[FrooxEngine]FrooxEngine.Grabbable"
BOX_COLLIDER = "[FrooxEngine]FrooxEngine.BoxCollider"
LIGHT = "[FrooxEngine]FrooxEngine.Light"

RGBA = dict[str, float]


def _c(r: float, g: float, b: float, a: float = 1.0) -> RGBA:
    return {"r": r, "g": g, "b": b, "a": a}


# -- Styles: palette per room -------------------------------------------------
# Keys: floor, wall, trim, fabric, accent, glow, wood.

STYLES: dict[str, dict[str, Any]] = {
    "loft": {
        "name": "Modern Loft",
        "description": "Warm concrete, rust fabric, teal accents.",
        "floor": _c(0.23, 0.22, 0.24),
        "wall": _c(0.82, 0.80, 0.77),
        "trim": _c(0.12, 0.12, 0.14),
        "fabric": _c(0.72, 0.32, 0.12),
        "accent": _c(0.10, 0.55, 0.60),
        "glow": _c(1.0, 0.80, 0.55),
        "wood": _c(0.45, 0.30, 0.18),
    },
    "scifi": {
        "name": "Sci-Fi Lab",
        "description": "Clean panels, cyan trim that reads as glow.",
        "floor": _c(0.16, 0.19, 0.25),
        "wall": _c(0.62, 0.68, 0.75),
        "trim": _c(0.05, 0.75, 0.90),
        "fabric": _c(0.90, 0.45, 0.10),
        "accent": _c(0.75, 0.15, 0.55),
        "glow": _c(0.55, 0.95, 1.0),
        "wood": _c(0.30, 0.34, 0.42),
    },
    "tavern": {
        "name": "Medieval Tavern",
        "description": "Dark wood, plaster, hearth reds and brass.",
        "floor": _c(0.32, 0.22, 0.13),
        "wall": _c(0.78, 0.70, 0.55),
        "trim": _c(0.25, 0.15, 0.08),
        "fabric": _c(0.60, 0.12, 0.10),
        "accent": _c(0.85, 0.62, 0.18),
        "glow": _c(1.0, 0.62, 0.25),
        "wood": _c(0.35, 0.22, 0.12),
    },
    "tea": {
        "name": "Tea Room",
        "description": "Tatami, shoji white, indigo textile, vermillion.",
        "floor": _c(0.62, 0.57, 0.42),
        "wall": _c(0.90, 0.88, 0.82),
        "trim": _c(0.20, 0.12, 0.08),
        "fabric": _c(0.15, 0.25, 0.45),
        "accent": _c(0.80, 0.20, 0.10),
        "glow": _c(1.0, 0.85, 0.60),
        "wood": _c(0.30, 0.18, 0.10),
    },
    "outpost": {
        "name": "Desert Outpost",
        "description": "Sand plaster, bronze trim, turquoise textile.",
        "floor": _c(0.72, 0.60, 0.42),
        "wall": _c(0.80, 0.68, 0.50),
        "trim": _c(0.30, 0.22, 0.12),
        "fabric": _c(0.10, 0.55, 0.55),
        "accent": _c(0.55, 0.30, 0.10),
        "glow": _c(1.0, 0.75, 0.45),
        "wood": _c(0.40, 0.28, 0.15),
    },
}

# -- Sizes: (width, height, depth) in metres -----------------------------------

SIZES: dict[str, dict[str, Any]] = {
    "cosy": {"name": "Cosy", "dims": (6.0, 3.0, 6.0), "description": "6 x 6 m, 3 m ceiling."},
    "hall": {"name": "Hall", "dims": (10.0, 4.0, 8.0), "description": "10 x 8 m, 4 m ceiling."},
    "grand": {"name": "Grand", "dims": (14.0, 5.0, 12.0), "description": "14 x 12 m, 5 m ceiling."},
}

# -- Furniture sets -------------------------------------------------------------

FURNITURE: dict[str, dict[str, str]] = {
    "dining": {"name": "Dining set", "description": "Table, chairs, pendant lamp."},
    "lounge": {"name": "Lounge", "description": "Sofa, coffee table, rug, floor lamp."},
    "sleep": {"name": "Sleeping nook", "description": "Bed, shelf, side lamp."},
    "work": {"name": "Workbench", "description": "Desk, stool, shelf, lamp."},
}


class Piece:
    """One box in the room: size, offset from room origin, palette key."""

    def __init__(
        self,
        name: str,
        size: tuple[float, float, float],
        offset: tuple[float, float, float],
        color: str,
        grabbable: bool = False,
        collider: bool = False,
        light: bool = False,
    ) -> None:
        self.name = name
        self.size = size
        self.offset = offset
        self.color = color
        self.grabbable = grabbable
        self.collider = collider
        self.light = light


def _shell(w: float, h: float, d: float, t: float = 0.2) -> list[Piece]:
    """Floor, ceiling, four walls; front wall split for a 1.2 m doorway."""
    door_w = 1.4
    seg = (d - door_w) / 2
    return [
        Piece("Floor", (w, t, d), (0, -t / 2, 0), "floor", collider=True),
        Piece("Ceiling", (w, t, d), (0, h + t / 2, 0), "wall"),
        Piece("WallBack", (w, h, t), (0, h / 2, -d / 2), "wall", collider=True),
        Piece("WallLeft", (t, h, d), (-w / 2, h / 2, 0), "wall", collider=True),
        Piece("WallRight", (t, h, d), (w / 2, h / 2, 0), "wall", collider=True),
        Piece("WallFrontL", (seg, h, t), (-(door_w / 2 + seg / 2), h / 2, d / 2), "wall", collider=True),
        Piece("WallFrontR", (seg, h, t), (door_w / 2 + seg / 2, h / 2, d / 2), "wall", collider=True),
        Piece("DoorTrimL", (0.12, 2.3, 0.3), (-door_w / 2, 1.15, d / 2), "trim"),
        Piece("DoorTrimR", (0.12, 2.3, 0.3), (door_w / 2, 1.15, d / 2), "trim"),
        Piece("DoorTrimTop", (door_w + 0.24, 0.12, 0.3), (0, 2.36, d / 2), "trim"),
    ]


def _pillars(w: float, h: float, d: float) -> list[Piece]:
    inset = 0.45
    return [
        Piece(
            f"Pillar{i}",
            (0.35, h, 0.35),
            (sx * (w / 2 - inset), h / 2, sz * (d / 2 - inset)),
            "trim",
            collider=True,
        )
        for i, (sx, sz) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)])
    ]


def _rug(cx: float, cz: float, w: float = 3.0, d: float = 2.2) -> Piece:
    return Piece("Rug", (w, 0.04, d), (cx, 0.02, cz), "fabric")


def _table(cx: float, cz: float, top: tuple[float, float, float] = (1.8, 0.08, 1.0)) -> list[Piece]:
    tw, th, td = top
    leg_h = 0.72
    return [
        Piece("TableTop", top, (cx, leg_h + th / 2, cz), "wood", grabbable=True),
        *[
            Piece(
                f"TableLeg{i}",
                (0.09, leg_h, 0.09),
                (cx + sx * (tw / 2 - 0.1), leg_h / 2, cz + sz * (td / 2 - 0.1)),
                "wood",
                grabbable=True,
            )
            for i, (sx, sz) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)])
        ],
    ]


def _chair(cx: float, cz: float, rot_y: float = 0.0) -> list[Piece]:
    # rot_y ignored in v1 (slots default orientation); chairs face +z.
    del rot_y
    return [
        Piece("ChairSeat", (0.5, 0.07, 0.5), (cx, 0.45, cz), "fabric", grabbable=True),
        Piece("ChairBack", (0.5, 0.6, 0.07), (cx, 0.78, cz - 0.22), "fabric", grabbable=True),
        *[
            Piece(f"ChairLeg{i}", (0.07, 0.45, 0.07), (cx + sx * 0.19, 0.225, cz + sz * 0.19), "wood", grabbable=True)
            for i, (sx, sz) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)])
        ],
    ]


def _sofa(cx: float, cz: float) -> list[Piece]:
    return [
        Piece("SofaBase", (2.2, 0.45, 0.95), (cx, 0.225, cz), "fabric", grabbable=True),
        Piece("SofaBack", (2.2, 0.65, 0.25), (cx, 0.775, cz - 0.35), "fabric", grabbable=True),
        Piece("SofaArmL", (0.25, 0.35, 0.95), (cx - 0.975, 0.625, cz), "fabric", grabbable=True),
        Piece("SofaArmR", (0.25, 0.35, 0.95), (cx + 0.975, 0.625, cz), "fabric", grabbable=True),
    ]


def _bed(cx: float, cz: float) -> list[Piece]:
    return [
        Piece("BedFrame", (2.2, 0.3, 1.8), (cx, 0.15, cz), "wood", grabbable=True),
        Piece("Mattress", (2.05, 0.25, 1.65), (cx, 0.425, cz), "fabric", grabbable=True),
        Piece("Headboard", (2.2, 1.0, 0.12), (cx, 0.8, cz - 0.84), "wood", grabbable=True),
        Piece("Pillow", (0.7, 0.15, 0.5), (cx - 0.5, 0.62, cz - 0.45), "accent", grabbable=True),
        Piece("Pillow2", (0.7, 0.15, 0.5), (cx + 0.5, 0.62, cz - 0.45), "accent", grabbable=True),
    ]


def _shelf(cx: float, cz: float, against_wall: str = "back") -> list[Piece]:
    del against_wall
    return [
        Piece("ShelfSideL", (0.08, 1.8, 0.4), (cx - 0.56, 0.9, cz), "wood", grabbable=True),
        Piece("ShelfSideR", (0.08, 1.8, 0.4), (cx + 0.56, 0.9, cz), "wood", grabbable=True),
        *[Piece(f"ShelfBoard{i}", (1.2, 0.06, 0.4), (cx, 0.3 + i * 0.5, cz), "wood", grabbable=True) for i in range(3)],
        Piece("ShelfBookRow", (0.9, 0.28, 0.22), (cx, 0.47, cz), "accent", grabbable=True),
    ]


def _desk(cx: float, cz: float) -> list[Piece]:
    return [
        Piece("DeskTop", (1.6, 0.07, 0.8), (cx, 0.75, cz), "wood", grabbable=True),
        Piece("DeskSideL", (0.07, 0.75, 0.8), (cx - 0.765, 0.375, cz), "wood", grabbable=True),
        Piece("DeskSideR", (0.07, 0.75, 0.8), (cx + 0.765, 0.375, cz), "wood", grabbable=True),
        Piece("DeskLampBase", (0.25, 0.05, 0.25), (cx + 0.55, 0.81, cz - 0.2), "trim", grabbable=True),
        Piece("DeskLampArm", (0.06, 0.5, 0.06), (cx + 0.55, 1.06, cz - 0.2), "trim", grabbable=True),
        Piece("DeskLampHead", (0.22, 0.14, 0.22), (cx + 0.55, 1.32, cz - 0.2), "glow", grabbable=True, light=True),
    ]


def _floor_lamp(cx: float, cz: float) -> list[Piece]:
    return [
        Piece("LampPole", (0.09, 1.6, 0.09), (cx, 0.8, cz), "trim", grabbable=True),
        Piece("LampShade", (0.45, 0.4, 0.45), (cx, 1.7, cz), "glow", grabbable=True, light=True),
        Piece("LampBase", (0.35, 0.06, 0.35), (cx, 0.03, cz), "trim", grabbable=True),
    ]


def _pendant(cx: float, cz: float, h: float) -> list[Piece]:
    return [
        Piece("PendantCord", (0.04, h - 2.2, 0.04), (cx, (h + 2.2) / 2, cz), "trim"),
        Piece("PendantShade", (0.5, 0.35, 0.5), (cx, 2.0, cz), "glow", light=True),
    ]


def _counter(cx: float, cz: float) -> list[Piece]:
    return [
        Piece("CounterTop", (2.4, 0.09, 0.7), (cx, 0.95, cz), "wood", grabbable=True),
        Piece("CounterBody", (2.4, 0.9, 0.6), (cx, 0.45, cz), "trim", grabbable=True),
        Piece("CounterShelf", (2.2, 0.3, 0.3), (cx, 1.15, cz - 0.1), "accent", grabbable=True),
    ]


def layout(style_id: str, size_id: str, furniture: list[str]) -> tuple[list[Piece], list[str]]:
    """Assemble the piece list. Returns (pieces, warnings)."""
    warnings: list[str] = []
    style = STYLES.get(style_id)
    if style is None:
        raise ValueError(f"Unknown style {style_id!r} (have: {sorted(STYLES)})")
    size = SIZES.get(size_id)
    if size is None:
        raise ValueError(f"Unknown size {size_id!r} (have: {sorted(SIZES)})")
    w, h, d = size["dims"]
    unknown = [f for f in furniture if f not in FURNITURE]
    if unknown:
        warnings.append(f"Ignored unknown furniture sets: {unknown}")
    furniture = [f for f in furniture if f in FURNITURE]

    pieces: list[Piece] = _shell(w, h, d)
    if size_id in ("hall", "grand"):
        pieces += _pillars(w, h, d)

    # Furniture placement anchors (floor area, front = +z with the doorway).
    if "dining" in furniture:
        pieces += _table(0, -0.5)
        pieces += _chair(-1.3, -0.5)
        pieces += _chair(1.3, -0.5)
        pieces += _chair(0, -1.6)
        pieces += _pendant(0, -0.5, h)
    if "lounge" in furniture:
        pieces.append(_rug(0, 1.8))
        pieces += _sofa(0, 2.3)
        pieces += _table(0, 1.2, top=(1.1, 0.07, 0.6))
        pieces += _floor_lamp(-w / 2 + 0.8, d / 2 - 0.8)
    if "sleep" in furniture:
        pieces += _bed(-w / 2 + 1.6, -d / 2 + 1.5)
        pieces += _shelf(w / 2 - 0.8, -d / 2 + 0.6)
        pieces += _floor_lamp(-w / 2 + 2.9, -d / 2 + 0.7)
    if "work" in furniture:
        pieces += _desk(w / 2 - 1.4, 0.5)
        pieces += _chair(w / 2 - 1.4, 1.5)
        pieces += _shelf(-w / 2 + 0.8, 0.5)

    # Clamp nothing: anchors assume hall+ sizes; on cosy some pieces may
    # overlap walls. Warn instead of silently overlapping.
    if size_id == "cosy" and len(furniture) > 2:
        warnings.append("Cosy rooms fit ~2 furniture sets; extras may overlap walls.")
    return pieces, warnings


async def build_room(
    client: Any,
    name: str,
    style_id: str,
    size_id: str,
    furniture: list[str],
    origin: dict[str, float],
) -> dict[str, Any]:
    """Spawn every piece into the connected session. Returns a full report."""
    style = STYLES[style_id]
    pieces, warnings = layout(style_id, size_id, furniture)
    ox, oy, oz = float(origin.get("x", 0.0)), float(origin.get("y", 0.0)), float(origin.get("z", 0.0))

    room_id = await client.add_slot(name=name)
    results: list[dict[str, Any]] = []
    ok_count = 0
    for piece in pieces:
        entry: dict[str, Any] = {"name": piece.name}
        try:
            pos = {"x": ox + piece.offset[0], "y": oy + piece.offset[1], "z": oz + piece.offset[2]}
            slot_id = await client.add_slot(name=f"{name}/{piece.name}", parent_id=room_id, position=pos)
            entry["slot_id"] = slot_id
            color = style[piece.color]
            mesh_id = await client.add_component(
                slot_id,
                BOX_MESH,
                {"Size": rl_value("float3", {"x": piece.size[0], "y": piece.size[1], "z": piece.size[2]})},
            )
            renderer_id = await client.add_component(slot_id, MESH_RENDERER, {"Mesh": rl_ref(mesh_id)})
            material_id = await client.add_component(slot_id, PBS_METALLIC, {"AlbedoColor": rl_value("colorX", color)})
            await client.update_component(renderer_id, {"Materials": rl_list([rl_ref(material_id)])})
            entry["mesh_id"] = mesh_id
            entry["renderer_id"] = renderer_id
            entry["material_id"] = material_id
            if piece.grabbable:
                entry["grabbable_id"] = await client.add_component(slot_id, GRABBABLE)
            if piece.collider:
                entry["collider_id"] = await client.add_component(
                    slot_id,
                    BOX_COLLIDER,
                    {"Size": rl_value("float3", {"x": piece.size[0], "y": piece.size[1], "z": piece.size[2]})},
                )
            if piece.light:
                # LightType left default (Point on standard assets); starting
                # Intensity/Range are guesses the user can tune in-world.
                entry["light_id"] = await client.add_component(
                    slot_id,
                    LIGHT,
                    {
                        "Color": rl_value("colorX", style["glow"]),
                        "Intensity": rl_value("float", 2.0),
                        "Range": rl_value("float", 8.0),
                    },
                )
            entry["ok"] = True
            ok_count += 1
        except Exception as exc:  # per-piece: one failure must not abort the room
            logger.warning("world_builder: piece %s failed: %s", piece.name, exc)
            entry["ok"] = False
            entry["error"] = str(exc)
        results.append(entry)

    return {
        "status": "built" if ok_count == len(pieces) else "partial",
        "room": name,
        "room_slot_id": room_id,
        "style": style["name"],
        "pieces_ok": ok_count,
        "pieces_total": len(pieces),
        "warnings": warnings,
        "pieces": results,
    }


def presets_payload() -> dict[str, Any]:
    """Form metadata for the webapp builder page (backend-driven, no copy rot)."""

    def swatches(palette: dict[str, Any]) -> list[str]:
        out = []
        for key in ("floor", "wall", "trim", "fabric", "accent", "glow"):
            c = palette[key]
            out.append(f"rgb({int(c['r'] * 255)},{int(c['g'] * 255)},{int(c['b'] * 255)})")
        return out

    return {
        "styles": [
            {"id": sid, "name": s["name"], "description": s["description"], "swatches": swatches(s)}
            for sid, s in STYLES.items()
        ],
        "sizes": [{"id": sid, "name": s["name"], "description": s["description"]} for sid, s in SIZES.items()],
        "furniture": [{"id": fid, "name": f["name"], "description": f["description"]} for fid, f in FURNITURE.items()],
        "defaults": {
            "style": "loft",
            "size": "hall",
            "furniture": ["lounge"],
            "origin": {"x": 0.0, "y": 0.0, "z": 0.0},
        },
    }
