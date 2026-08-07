"""Spawn Nekomimi-chan into Sandra's persistent Home, with the Z-flip +
winding-reversal fix applied (strong evidence from tonight's investigation:
99.9% winding/normal self-consistency check, plus the untested Z-flip
hypothesis) -- this is the real destination now, not the ephemeral Tutorial
session."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions
from resonite_mcp.utils.gltf_meshjson import gltf_to_mesh_json

VRM_PATH = Path(r"C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm")


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
    print(f"Converting {VRM_PATH.name}...")
    mesh = gltf_to_mesh_json(VRM_PATH)
    for v in mesh["vertices"]:
        v.pop("uvs", None)  # UV discriminator still unresolved; solid material for now
    flipped = flip_z_and_reverse_winding(mesh)
    print(
        f"Converted + flipped: {len(flipped['vertices'])} vertices, {len(flipped['submeshes'][0]['triangles'])} triangles"
    )

    print("Discovering ResoniteLink sessions...")
    sessions = await discover_sessions(timeout=15.0)
    home = next((s for s in sessions if "home" in s.get("sessionName", "").lower()), None)
    if not home:
        print(f"Could not find a Home session among: {[s.get('sessionName') for s in sessions]}")
        return
    print(f"Found '{home['sessionName']}' on port {home['linkPort']}")

    client = ResoniteLinkClient(host="localhost", port=home["linkPort"])
    if not await client.connect():
        print("Failed to connect.")
        return

    try:
        r = await client.spawn_mesh(
            flipped["vertices"],
            flipped["submeshes"],
            position={"x": 0, "y": 0, "z": 2},
            name="nekomimi-chan",
            color={"r": 0.95, "g": 0.85, "b": 0.9, "a": 1.0},
        )
        print(f"SUCCESS: {json.dumps(r, indent=2)}")
    except Exception as exc:
        print(f"FAILED: {exc}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
