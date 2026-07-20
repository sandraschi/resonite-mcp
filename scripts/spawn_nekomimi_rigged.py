"""Push Nekomimi-chan into Home WITH her real skeleton (197 bones), no
blendshapes yet (pushing all 399 at 190k vertices each would be an
enormous JSON payload -- separate scaling concern from the now-confirmed
wire shape). Replaces the earlier static-mesh-only copy."""
from __future__ import annotations
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions
from resonite_mcp.utils.gltf_meshjson import gltf_to_mesh_json

VRM_PATH = Path(r"C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm")


async def main():
    print(f"Converting {VRM_PATH.name} with skinning...")
    mesh = gltf_to_mesh_json(VRM_PATH, include_skinning=True)
    for v in mesh["vertices"]:
        v.pop("uvs", None)  # UV discriminator still unresolved
    bones = mesh.get("bones", [])
    print(f"Converted: {len(mesh['vertices'])} vertices, {len(mesh['submeshes'][0]['triangles'])} triangles, {len(bones)} bones")

    sessions = await discover_sessions(timeout=15.0)
    home = next((s for s in sessions if "home" in s.get("sessionName", "").lower()), None)
    if not home:
        print("Could not find Home session.")
        return
    client = ResoniteLinkClient(host="localhost", port=home["linkPort"])
    if not await client.connect():
        print("Failed to connect.")
        return

    try:
        asset_url = await client.import_mesh_json(mesh["vertices"], mesh["submeshes"], bones=bones)
        print(f"import_mesh_json SUCCESS: {asset_url}")

        slot_id = await client.add_slot(name="nekomimi-chan-rigged", position={"x": 2, "y": 0, "z": 2})
        static_mesh_id = await client.add_component(
            slot_id, "[FrooxEngine]FrooxEngine.StaticMesh",
            {"URL": {"$type": "Uri", "value": asset_url}},
        )
        renderer_id = await client.add_component(
            slot_id, "[FrooxEngine]FrooxEngine.MeshRenderer",
            {"Mesh": {"$type": "reference", "targetId": static_mesh_id}},
        )
        material_id = await client.add_component(
            slot_id, "[FrooxEngine]FrooxEngine.PBS_Metallic",
            {"AlbedoColor": {"$type": "colorX", "value": {"r": 0.95, "g": 0.85, "b": 0.9, "a": 1.0}}},
        )
        await client.update_component(
            renderer_id, {"Materials": {"$type": "list", "elements": [{"$type": "reference", "targetId": material_id}]}},
        )
        print(f"SUCCESS: slot={slot_id}, static_mesh={static_mesh_id}, renderer={renderer_id}, material={material_id}")
    except Exception as exc:
        print(f"FAILED: {exc}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
