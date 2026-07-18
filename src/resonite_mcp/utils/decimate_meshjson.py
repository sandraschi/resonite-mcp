"""
Mesh decimation for mesh-JSON dicts (the shape gltf_meshjson/stl_meshjson
produce and ResoniteLinkClient.import_mesh_json() consumes).

HONESTY NOTE: this is **vertex clustering** (grid quantization) decimation —
snap every vertex to the nearest cell of a 3D grid sized by target_ratio,
merge vertices that land in the same cell, drop triangles that degenerate
to zero area once their corners collapse together. This is a real, simple
simplification technique (Rossignac & Borrel 1993), but it is NOT the same
algorithm as Blender's Decimate modifier (quadric edge collapse), which
picks which edges to collapse based on surface-error cost and produces
better-shaped results at the same triangle count. Use this to prove the
pipeline and get a rough size reduction; for production-quality decimation
of the actual home shell, do it in Blender (blender-mcp) before conversion,
not with this function.
"""

from __future__ import annotations

import math
from typing import Any


def decimate_mesh_json(mesh_json: dict[str, Any], target_ratio: float) -> dict[str, Any]:
    """Reduce a mesh-JSON dict's vertex/triangle count via vertex clustering.

    target_ratio: approximate fraction of the ORIGINAL BOUNDING-BOX EXTENT
        to use as the grid cell size (e.g. 0.02 = cells 2% of the mesh's
        largest dimension). Smaller = coarser grid = more decimation.
        This is a size-based knob, not a target triangle count — the
        actual reduction depends on how the geometry is distributed.

    Only the first submesh is decimated (matches this project's converters,
    which currently always emit exactly one). Only position is used for
    clustering; normals from whichever vertex is kept survive as-is (not
    re-averaged) — acceptable for a proof-of-pipeline pass, not a
    production simplifier.
    """
    if not 0 < target_ratio < 1:
        raise ValueError(f"target_ratio must be between 0 and 1, got {target_ratio}")

    vertices = mesh_json["vertices"]
    triangles = mesh_json["submeshes"][0]["triangles"]
    if not vertices or not triangles:
        raise ValueError("mesh_json has no vertices/triangles to decimate")

    xs = [v["position"]["x"] for v in vertices]
    ys = [v["position"]["y"] for v in vertices]
    zs = [v["position"]["z"] for v in vertices]
    extent = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    if extent <= 0:
        raise ValueError("mesh has zero bounding-box extent; cannot size a grid")
    cell_size = extent * target_ratio

    def cell_key(pos: dict[str, float]) -> tuple[int, int, int]:
        return (
            math.floor(pos["x"] / cell_size),
            math.floor(pos["y"] / cell_size),
            math.floor(pos["z"] / cell_size),
        )

    # Map original vertex index -> new (deduplicated) vertex index.
    cell_to_new_index: dict[tuple[int, int, int], int] = {}
    old_to_new: list[int] = []
    new_vertices: list[dict[str, Any]] = []

    for v in vertices:
        key = cell_key(v["position"])
        new_idx = cell_to_new_index.get(key)
        if new_idx is None:
            new_idx = len(new_vertices)
            cell_to_new_index[key] = new_idx
            new_vertices.append(v)  # keep the first vertex seen in this cell as-is
        old_to_new.append(new_idx)

    new_triangles: list[dict[str, int]] = []
    degenerate_dropped = 0
    for tri in triangles:
        a = old_to_new[tri["vertex0Index"]]
        b = old_to_new[tri["vertex1Index"]]
        c = old_to_new[tri["vertex2Index"]]
        if a == b or b == c or a == c:
            degenerate_dropped += 1
            continue
        new_triangles.append({"vertex0Index": a, "vertex1Index": b, "vertex2Index": c})

    return {
        "vertices": new_vertices,
        "submeshes": [{"$type": "triangles", "triangles": new_triangles}],
        "_decimation_stats": {
            "technique": "vertex_clustering",
            "cell_size": cell_size,
            "original_vertices": len(vertices),
            "original_triangles": len(triangles),
            "new_vertices": len(new_vertices),
            "new_triangles": len(new_triangles),
            "degenerate_triangles_dropped": degenerate_dropped,
        },
    }
