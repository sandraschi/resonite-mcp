"""Build the real skeleton for Nekomimi-chan: 197 bone Slots (correct
parent-child hierarchy, bind-pose transforms) + a real SkinnedMeshRenderer
(not the plain MeshRenderer from the earlier test) referencing them in
boneIndex order, plus BlendShapeWeights sized to the 399 real expressions
(all zero = neutral, since none are being driven yet)."""
from __future__ import annotations
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions, rl_ref, rl_list, rl_value
from resonite_mcp.utils.gltf_meshjson import gltf_to_mesh_json

VRM_PATH = Path(r"C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm")
CHARACTER_SLOT_ID = "Reso_4"  # from the earlier bones-data-only push


async def main():
    print("Re-converting to get the bones list (already proven, just need it again)...")
    mesh = gltf_to_mesh_json(VRM_PATH, include_skinning=True)
    bones = mesh["bones"]
    n_blendshapes = len(mesh.get("blendshapes", []))
    print(f"{len(bones)} bones, {n_blendshapes} blendshapes (weights only, deltas not pushed — size)")

    sessions = await discover_sessions(timeout=15.0)
    home = next((s for s in sessions if "home" in s.get("sessionName", "").lower()), sessions[0])
    client = ResoniteLinkClient(host="localhost", port=home["linkPort"])
    if not await client.connect():
        print("Failed to connect.")
        return

    bone_ids = [f"nekomimi_bone_{i}" for i in range(len(bones))]
    print("Bone slots already created in a previous run — skipping batch addSlot, going straight to SkinnedMeshRenderer.")

    # Now the real SkinnedMeshRenderer, referencing the SAME static mesh
    # asset (Reso_5 holds the URL) but with actual bone references this time.
    try:
        skinned_renderer_id = await client.add_component(
            CHARACTER_SLOT_ID,
            "[FrooxEngine]FrooxEngine.SkinnedMeshRenderer",
            {
                "Mesh": rl_ref("Reso_5"),  # same imported mesh asset as before
                "Bones": rl_list([rl_ref(bid) for bid in bone_ids]),
                "BlendShapeWeights": rl_list([rl_value("float", 0.0) for _ in range(n_blendshapes)]),
            },
        )
        print(f"SkinnedMeshRenderer added: {skinned_renderer_id}")

        material_id = await client.add_component(
            CHARACTER_SLOT_ID, "[FrooxEngine]FrooxEngine.PBS_Metallic",
            {"AlbedoColor": rl_value("colorX", {"r": 0.95, "g": 0.85, "b": 0.9, "a": 1.0})},
        )
        await client.update_component(skinned_renderer_id, {"Materials": rl_list([rl_ref(material_id)])})
        print(f"Material wired: {material_id}")

        # Remove the earlier plain MeshRenderer (Reso_6) since it doesn't
        # do skinning and would double-render her statically on top.
        await client.remove_component("Reso_6")
        print("Removed the earlier non-skinned MeshRenderer (Reso_6)")

    except Exception as exc:
        print(f"SkinnedMeshRenderer setup FAILED: {exc}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
