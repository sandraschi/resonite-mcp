"""
STL -> ResoniteLink mesh-JSON converter.

Companion to gltf_meshjson.py, for the same import_mesh_json() target shape.
STL (binary or ASCII) is a triangle soup: every triangle carries its own
three vertices and one face normal, with no shared-vertex indexing and no
UVs. That's a real limitation carried through to the output: each triangle
gets its own 3 fresh vertices (no de-duplication), so vertex count == 3x
triangle count. Fine for the mesh sizes this project deals with; revisit
with a position-based de-dup pass if a converted STL ever needs to be
edited/deformed in-world (shared vertices matter for that, not for static
display).

Status (2026-07-18): first implementation, tested against real Yahboom
ROS meshes (base_link_X3.STL etc.) via the CLI smoke test below.
"""

from __future__ import annotations

import json
import logging
import struct
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class StlConversionError(Exception):
    """Raised when an STL file can't be parsed or converted."""


def _is_ascii_stl(raw: bytes) -> bool:
    """Binary STL has an 80-byte header then a triangle count; ASCII STL
    starts with the literal text 'solid'. The only reliable check is
    whether the byte-length matches the binary format's implied size,
    since some binary STL exporters also start their header with 'solid'.
    """
    if len(raw) < 84:
        return raw.lstrip().lower().startswith(b"solid")
    tri_count = struct.unpack_from("<I", raw, 80)[0]
    expected_size = 84 + tri_count * 50
    if expected_size == len(raw):
        return False  # binary, and the size checks out
    return raw.lstrip().lower().startswith(b"solid")


def _parse_binary_stl(raw: bytes) -> list[tuple[tuple[float, float, float], list[tuple[float, float, float]]]]:
    """Return [(normal, [v0, v1, v2]), ...] for every triangle."""
    tri_count = struct.unpack_from("<I", raw, 80)[0]
    triangles = []
    offset = 84
    for _ in range(tri_count):
        nx, ny, nz, v0x, v0y, v0z, v1x, v1y, v1z, v2x, v2y, v2z = struct.unpack_from(
            "<12f", raw, offset
        )
        triangles.append(
            ((nx, ny, nz), [(v0x, v0y, v0z), (v1x, v1y, v1z), (v2x, v2y, v2z)])
        )
        offset += 50  # 12 floats (48 bytes) + 2-byte attribute count
    return triangles


def _parse_ascii_stl(text: str) -> list[tuple[tuple[float, float, float], list[tuple[float, float, float]]]]:
    """Minimal ASCII STL parser: pulls 'facet normal' and 'vertex' lines in order."""
    triangles = []
    current_normal: tuple[float, float, float] | None = None
    current_verts: list[tuple[float, float, float]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("facet normal"):
            parts = stripped.split()
            current_normal = (float(parts[2]), float(parts[3]), float(parts[4]))
            current_verts = []
        elif stripped.startswith("vertex"):
            parts = stripped.split()
            current_verts.append((float(parts[1]), float(parts[2]), float(parts[3])))
        elif stripped.startswith("endfacet"):
            if current_normal is not None and len(current_verts) == 3:
                triangles.append((current_normal, current_verts))
            current_normal = None
            current_verts = []
    return triangles


def stl_to_mesh_json(path: str | Path) -> dict[str, Any]:
    """Convert an STL file into the ResoniteLink importMeshJSON payload shape.

    No shared indexing: every triangle contributes 3 unique vertices, so
    vertex count is always exactly 3x triangle count. See module docstring.
    """
    path = Path(path)
    if not path.exists():
        raise StlConversionError(f"file not found: {path}")

    raw = path.read_bytes()
    if _is_ascii_stl(raw):
        triangles = _parse_ascii_stl(raw.decode("utf-8", errors="replace"))
    else:
        triangles = _parse_binary_stl(raw)

    if not triangles:
        raise StlConversionError(f"{path.name}: no triangles parsed")

    vertices: list[dict[str, Any]] = []
    tri_indices: list[dict[str, int]] = []
    for normal, verts in triangles:
        base = len(vertices)
        for v in verts:
            vertices.append(
                {
                    "position": {"x": v[0], "y": v[1], "z": v[2]},
                    "normal": {"x": normal[0], "y": normal[1], "z": normal[2]},
                }
            )
        tri_indices.append({"vertex0Index": base, "vertex1Index": base + 1, "vertex2Index": base + 2})

    logger.info("%s: converted %d triangles -> %d vertices (unindexed)", path.name, len(triangles), len(vertices))
    return {
        "vertices": vertices,
        "submeshes": [{"$type": "triangles", "triangles": tri_indices}],
    }


def _main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    if len(sys.argv) < 2:
        print("Usage: stl_meshjson.py <path.stl> [output.json]")
        return 1
    src = Path(sys.argv[1])
    try:
        result = stl_to_mesh_json(src)
    except StlConversionError as exc:
        print(f"CONVERSION FAILED: {exc}")
        return 1
    n_verts = len(result["vertices"])
    n_tris = sum(len(sm["triangles"]) for sm in result["submeshes"])
    print(f"{src.name}: {n_verts} vertices, {n_tris} triangles")
    if len(sys.argv) >= 3:
        out_path = Path(sys.argv[2])
        out_path.write_text(json.dumps(result), encoding="utf-8")
        print(f"Wrote mesh-JSON to {out_path} ({out_path.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
