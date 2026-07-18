"""Test: does a Z-flip + winding-reversal fix Nekomimi-chan's invisibility?
Spawns a SECOND copy next to the original (which stays as-is) so both can
be compared without losing the first attempt."""
from __future__ import annotations
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions

MESH_JSON_PATH = Path(r"C:\temp\nekomimi_meshjson_test.json")


def flip_z_and_reverse_winding(mesh: dict) -> dict:
    new_verts = []
    for v in mesh["vertices"]:
        nv = {"position": {"x": v["position"]["x"], "y": v["position"]["y"], "z": -v["position"]["z"]}}
        if "normal" in v:
            n = v["normal"]
            nv["normal"] = {"x": n["x"], "y": n["y"], "z": -n["z"]}
        new_verts.append(nv)
    new_subs = []
    for sm in mesh["submeshes"]:
        new_tris = [
            {"vertex0Index": t["vertex0Index"], "vertex1Index": t["vertex2Index"], "vertex2Index": t["vertex1Index"]}
            for t in sm["triangles"]
        ]
        new_subs.append({"$type": "triangles", "triangles": new_tris})
    return {"vertices": new_verts, "submeshes": new_subs}


async def main():
    mesh = json.loads(MESH_JSON_PATH.read_text(encoding="utf-8"))
    for v in mesh["vertices"]:
        v.pop("uvs", None)
    flipped = flip_z_and_reverse_winding(mesh)

    sessions = await discover_sessions(timeout=15.0)
    port = sessions[0]["linkPort"]
    client = ResoniteLinkClient(host="localhost", port=port)
    await client.connect()

    r = await client.spawn_mesh(
        flipped["vertices"], flipped["submeshes"],
        position={"x": -6, "y": 0, "z": 5}, name="nekomimi-chan-zflip-test",
        color={"r": 0.95, "g": 0.85, "b": 0.9, "a": 1.0},
    )
    print(f"Z-flip test spawn: {r}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
