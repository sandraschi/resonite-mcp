"""
Live push: Nekomimi-chan's static VRM mesh (no rig, no expressions yet —
that's the separate bones/blendshapes phase) into a running Resonite
session. Sub-goal 1 of the "spawn Nekomimi-chan" task.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions
from resonite_mcp.utils.gltf_meshjson import gltf_to_mesh_json

VRM_PATH = Path(r"C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm")


async def main() -> None:
    print(f"Converting {VRM_PATH.name}...")
    mesh = gltf_to_mesh_json(VRM_PATH)
    n_verts = len(mesh["vertices"])
    n_tris = len(mesh["submeshes"][0]["triangles"])
    print(f"Converted: {n_verts} vertices, {n_tris} triangles")

    # UV_Coordinate's polymorphic $type discriminator is unknown as of
    # 2026-07-18 — tried UV_Coordinate/float2/uv/UVCoordinate, all rejected
    # as "unrecognized type discriminator id" (float2 IS a valid Resonite
    # type per get_type_definition, so the discriminator string is some
    # other internal name not yet found). Stripping uvs for now — she'll
    # get a solid-color material, not a textured one, until this is
    # resolved. Not blocking: getting her standing there doesn't need UVs.
    for v in mesh["vertices"]:
        v.pop("uvs", None)

    print("Discovering ResoniteLink sessions...")
    sessions = await discover_sessions(timeout=8.0)
    if not sessions:
        print("No ResoniteLink sessions discovered.")
        return
    port = sessions[0]["linkPort"]
    print(f"Found session at port {port}")

    client = ResoniteLinkClient(host="localhost", port=port)
    if not await client.connect():
        print("Failed to connect.")
        return

    result = {}
    print(f"\nAttempting live import: {n_verts} vertices, {n_tris} triangles (raw, no decimation)...")
    try:
        r = await client.spawn_mesh(
            mesh["vertices"],
            mesh["submeshes"],
            position={"x": -3, "y": 0, "z": 5},
            name="nekomimi-chan-static-mesh",
        )
        print(f"SUCCESS (raw): {r}")
        result = {"status": "success", "decimated": False, "vertices": n_verts, "triangles": n_tris, **r}
    except Exception as exc:
        print(f"FAILED (raw): {exc}")
        result = {"status": "failed_raw", "error": str(exc)}

    await client.disconnect()
    Path(r"C:\temp\nekomimi_static_spawn_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("\nResult written to C:\\temp\\nekomimi_static_spawn_result.json")


if __name__ == "__main__":
    asyncio.run(main())
