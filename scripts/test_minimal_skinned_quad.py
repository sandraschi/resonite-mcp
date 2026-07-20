"""Smallest possible skinned-mesh test: a flat quad (4 vertices) bound to
2 bones (root + 1 child bone offset upward), all vertices weighted 100% to
the child bone. If this renders correctly (visible, in the right place),
skinning works and Nekomimi's problem is specific to her mesh/hierarchy
complexity. If THIS tiny case is also invisible, the bind-pose mechanism
itself is broken regardless of complexity -- much cheaper to learn that
here than on a 45k-triangle mesh."""
from __future__ import annotations
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions, rl_ref, rl_list, rl_value


async def main():
    sessions = await discover_sessions(timeout=15.0)
    home = next((s for s in sessions if "home" in s.get("sessionName", "").lower()), sessions[0])
    client = ResoniteLinkClient(host="localhost", port=home["linkPort"])
    await client.connect()

    # A 1x1 quad in the XY plane, all 4 vertices weighted 100% to bone 1
    # (the child bone), so it should render exactly where bone 1 sits.
    vertices = [
        {"position": {"x": -0.5, "y": 0, "z": 0}, "boneWeights": [{"boneIndex": 1, "weight": 1.0}]},
        {"position": {"x": 0.5, "y": 0, "z": 0}, "boneWeights": [{"boneIndex": 1, "weight": 1.0}]},
        {"position": {"x": 0.5, "y": 1, "z": 0}, "boneWeights": [{"boneIndex": 1, "weight": 1.0}]},
        {"position": {"x": -0.5, "y": 1, "z": 0}, "boneWeights": [{"boneIndex": 1, "weight": 1.0}]},
    ]
    submeshes = [{"$type": "triangles", "triangles": [
        {"vertex0Index": 0, "vertex1Index": 1, "vertex2Index": 2},
        {"vertex0Index": 0, "vertex1Index": 2, "vertex2Index": 3},
    ]}]
    bones = [
        {"name": "root", "parentIndex": None,
         "position": {"x": 0, "y": 0, "z": 0}, "rotation": {"x": 0, "y": 0, "z": 0, "w": 1},
         "scale": {"x": 1, "y": 1, "z": 1}},
        {"name": "child", "parentIndex": 0,
         "position": {"x": 0, "y": 0, "z": 0}, "rotation": {"x": 0, "y": 0, "z": 0, "w": 1},
         "scale": {"x": 1, "y": 1, "z": 1}},
    ]

    print("Importing tiny skinned quad...")
    try:
        asset_url = await client.import_mesh_json(vertices, submeshes, bones=bones)
        print(f"Import SUCCESS: {asset_url}")
    except Exception as exc:
        print(f"Import FAILED: {exc}")
        await client.disconnect()
        return

    # Real Slots for the 2 bones, spawned somewhere clearly visible.
    char_slot = await client.add_slot(name="tiny-skin-test", position={"x": -3, "y": 1, "z": 5})
    root_bone_id = await client.add_slot(name="root", parent_id=char_slot, position={"x": 0, "y": 0, "z": 0})
    child_bone_id = await client.add_slot(name="child", parent_id=root_bone_id, position={"x": 0, "y": 0, "z": 0})
    print(f"Character slot: {char_slot}, root bone: {root_bone_id}, child bone: {child_bone_id}")

    static_mesh_id = await client.add_component(
        char_slot, "[FrooxEngine]FrooxEngine.StaticMesh", {"URL": rl_value("Uri", asset_url)}
    )
    renderer_id = await client.add_component(
        char_slot, "[FrooxEngine]FrooxEngine.SkinnedMeshRenderer",
        {"Mesh": rl_ref(static_mesh_id), "Bones": rl_list([rl_ref(root_bone_id), rl_ref(child_bone_id)])},
    )
    material_id = await client.add_component(
        char_slot, "[FrooxEngine]FrooxEngine.PBS_Metallic",
        {"AlbedoColor": rl_value("colorX", {"r": 1.0, "g": 0.2, "b": 0.2, "a": 1.0})},  # bright red, easy to spot
    )
    await client.update_component(renderer_id, {"Materials": rl_list([rl_ref(material_id)])})
    print(f"SkinnedMeshRenderer wired: {renderer_id}, material: {material_id}")
    print(f"\nLook at position (-3, 1, 5) for a small BRIGHT RED quad.")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
