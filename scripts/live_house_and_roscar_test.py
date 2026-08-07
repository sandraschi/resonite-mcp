"""
Live proof script for the Phase 1 gate: pushes a synthetic multi-block
"house" mesh and the Boomy chassis STL (raw + decimated) through a real
ResoniteLink session via spawn_mesh(). One-off script, not part of the
package's importable API — run with:

  uv run python scripts/live_house_and_roscar_test.py

Requires Resonite running with ResoniteLink enabled; port is discovered
via discover_sessions() (do not hardcode a port — the dashboard readout has
been wrong before, see Phase 0 handoff).
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions
from resonite_mcp.utils.decimate_meshjson import decimate_mesh_json
from resonite_mcp.utils.stl_meshjson import stl_to_mesh_json


def build_house_mesh_json() -> dict:
    """A few-block "house": a rectangular body + a triangular-prism roof.
    Hand-authored directly in mesh-JSON (not round-tripped through glTF) —
    this is the live-wire-call test, not another converter test.
    """
    vertices = []
    triangles = []

    def add_box(cx, cy, cz, sx, sy, sz):
        """Axis-aligned box centered at (cx,cy,cz), size (sx,sy,sz). 8 verts, 12 tris."""
        base = len(vertices)
        hx, hy, hz = sx / 2, sy / 2, sz / 2
        corners = [
            (cx - hx, cy - hy, cz - hz),
            (cx + hx, cy - hy, cz - hz),
            (cx + hx, cy + hy, cz - hz),
            (cx - hx, cy + hy, cz - hz),
            (cx - hx, cy - hy, cz + hz),
            (cx + hx, cy - hy, cz + hz),
            (cx + hx, cy + hy, cz + hz),
            (cx - hx, cy + hy, cz + hz),
        ]
        for x, y, z in corners:
            vertices.append({"position": {"x": x, "y": y, "z": z}})
        faces = [
            (0, 1, 2),
            (0, 2, 3),  # bottom
            (4, 6, 5),
            (4, 7, 6),  # top
            (0, 5, 1),
            (0, 4, 5),  # front
            (1, 6, 2),
            (1, 5, 6),  # right
            (2, 7, 3),
            (2, 6, 7),  # back
            (3, 4, 0),
            (3, 7, 4),  # left
        ]
        for a, b, c in faces:
            triangles.append({"vertex0Index": base + a, "vertex1Index": base + b, "vertex2Index": base + c})

    def add_roof_prism(cx, base_y, cz, width_x, depth_z, height_y):
        """Triangular prism roof, Y-up (matches add_box's convention): ridge
        runs along the z-axis, base sits at y=base_y, peak at y=base_y+height_y.
        """
        base = len(vertices)
        hx, hz = width_x / 2, depth_z / 2
        # Base rectangle corners (y = base_y) + two ridge points (y = base_y+height_y)
        A = (cx - hx, base_y, cz - hz)  # base front-left
        B = (cx + hx, base_y, cz - hz)  # base front-right
        C = (cx + hx, base_y, cz + hz)  # base back-right
        D = (cx - hx, base_y, cz + hz)  # base back-left
        R0 = (cx, base_y + height_y, cz - hz)  # ridge front
        R1 = (cx, base_y + height_y, cz + hz)  # ridge back
        for pt in (A, B, C, D, R0, R1):
            vertices.append({"position": {"x": pt[0], "y": pt[1], "z": pt[2]}})
        idx = {"A": 0, "B": 1, "C": 2, "D": 3, "R0": 4, "R1": 5}
        faces = [
            ("A", "B", "R0"),  # front gable
            ("C", "D", "R1"),  # back gable
            ("A", "R0", "R1"),
            ("A", "R1", "D"),  # left slope
            ("B", "C", "R1"),
            ("B", "R1", "R0"),  # right slope
        ]
        for a, b, c in faces:
            triangles.append(
                {"vertex0Index": base + idx[a], "vertex1Index": base + idx[b], "vertex2Index": base + idx[c]}
            )

    # Body: 2m x 2m x 1.5m box, base sitting on y=0 (Resonite is Y-up)
    add_box(0, 0.75, 0, 2.0, 1.5, 2.0)
    # Roof: sits on top of the body, ridge along z, same width/depth footprint
    add_roof_prism(0, 1.5, 0, 2.2, 2.2, 0.9)

    return {"vertices": vertices, "submeshes": [{"$type": "triangles", "triangles": triangles}]}


async def main() -> None:
    print("Discovering ResoniteLink sessions...")
    sessions = await discover_sessions(timeout=8.0)
    if not sessions:
        print("No ResoniteLink sessions discovered. Is Resonite running with ResoniteLink enabled?")
        return
    session = sessions[0]
    port = session["linkPort"]
    host = session.get("host", "localhost")
    print(f"Found session '{session.get('sessionName')}' at {host}:{port}")

    # Discovery reports the WSL2/Hyper-V bridge address (this script runs on
    # the same machine that's hosting Resonite), which got an HTTP 400 on
    # first try — trying localhost instead before giving up.
    connected = False
    for candidate_host in (host, "localhost", "127.0.0.1"):
        client = ResoniteLinkClient(host=candidate_host, port=port)
        connected = await client.connect()
        if connected:
            print(f"Connected via host={candidate_host}")
            break
        print(f"Connect via host={candidate_host} failed, trying next candidate...")
    if not connected:
        print("Failed to connect to ResoniteLink via any candidate host.")
        return

    results = {}

    # 1. Simple multi-block house
    print("\n--- House (multi-block, hand-authored) ---")
    house = build_house_mesh_json()
    print(f"House: {len(house['vertices'])} vertices, {len(house['submeshes'][0]['triangles'])} triangles")
    # BUG FOUND (not a server-side issue after all): spawn_mesh()'s second
    # arg is `submeshes` — the FULL list of {"$type":..., "triangles":[...]}
    # dicts — but this script was passing house["submeshes"][0]["triangles"]
    # (just the raw triangle-index array, no $type wrapper at all). THAT is
    # exactly why the server said "must specify a type discriminator": it's
    # correct, my payload was actually malformed. Fixed below by passing
    # house["submeshes"] (the whole wrapped list) instead.
    try:
        r = await client.spawn_mesh(
            house["vertices"],
            house["submeshes"],
            position={"x": 0, "y": 1, "z": 5},
            name="phase1-test-house",
            color={"r": 0.8, "g": 0.6, "b": 0.3, "a": 1.0},
        )
        print(f"House spawn SUCCESS: {r}")
        results["house"] = {"status": "success", **r}
    except Exception as exc:
        print(f"House spawn FAILED: {exc}")
        results["house"] = {"status": "failed", "error": str(exc)}

    # 2. Boomy chassis STL, raw
    stl_path = Path(r"D:\Dev\repos\yahboom-mcp\webapp\dist\assets\meshes\base_link_X3.STL")
    print(f"\n--- Roscar chassis: {stl_path.name} (raw) ---")
    roscar_mesh = stl_to_mesh_json(stl_path)
    n_verts = len(roscar_mesh["vertices"])
    n_tris = len(roscar_mesh["submeshes"][0]["triangles"])
    print(f"Raw: {n_verts} vertices, {n_tris} triangles")
    results["roscar_raw_stats"] = {"vertices": n_verts, "triangles": n_tris}

    # 3. Decimate it, then try to spawn the decimated version live
    print("\n--- Roscar chassis: decimated (vertex clustering, ratio=0.01) ---")
    decimated = decimate_mesh_json(roscar_mesh, target_ratio=0.01)
    stats = decimated["_decimation_stats"]
    print(f"Decimated: {stats}")
    results["roscar_decimation_stats"] = stats

    try:
        r = await client.spawn_mesh(
            decimated["vertices"],
            decimated["submeshes"],
            position={"x": 3, "y": 1, "z": 5},
            name="phase1-test-roscar-decimated",
            color={"r": 0.2, "g": 0.5, "b": 0.9, "a": 1.0},
        )
        print(f"Decimated roscar spawn SUCCESS: {r}")
        results["roscar_decimated_spawn"] = {"status": "success", **r}
    except Exception as exc:
        print(f"Decimated roscar spawn FAILED: {exc}")
        results["roscar_decimated_spawn"] = {"status": "failed", "error": str(exc)}

    await client.disconnect()

    out_path = Path(r"C:\temp\live_house_and_roscar_test_results.json")
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nResults written to {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
