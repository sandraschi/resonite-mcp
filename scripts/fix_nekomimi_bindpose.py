"""Rebuild Nekomimi-chan's imported mesh asset with CORRECT bindPose
matrices (real schema, confirmed against the actual ResoniteLink source),
and repoint her existing SkinnedMeshRenderer at it. The 197 bone Slots
already in her Home are untouched -- those used real ResoniteLink Slot
semantics all along and were never wrong, only the mesh asset's internal
bones list was."""
from __future__ import annotations
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions, rl_ref, rl_value
from resonite_mcp.utils.gltf_meshjson import gltf_to_mesh_json

VRM_PATH = Path(r"C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm")
STATIC_MESH_ID = "Reso_5"  # the StaticMesh component SkinnedMeshRenderer already references


async def main():
    print("Re-converting with the CORRECTED bindPose matrices...")
    mesh = gltf_to_mesh_json(VRM_PATH, include_skinning=True)
    for v in mesh["vertices"]:
        v.pop("uvs", None)  # texture still separately unresolved
    print(f"{len(mesh['vertices'])} vertices, {len(mesh['bones'])} bones with real bindPose matrices")

    sessions = await discover_sessions(timeout=15.0)
    home = next((s for s in sessions if "home" in s.get("sessionName", "").lower()), sessions[0])
    client = ResoniteLinkClient(host="localhost", port=home["linkPort"])
    if not await client.connect():
        print("Failed to connect.")
        return

    try:
        new_asset_url = await client.import_mesh_json(
            mesh["vertices"], mesh["submeshes"], bones=mesh["bones"]
        )
        print(f"Re-imported mesh with correct bindPose: {new_asset_url}")

        await client.update_component(
            STATIC_MESH_ID, {"URL": rl_value("Uri", new_asset_url)}
        )
        print(f"Repointed StaticMesh ({STATIC_MESH_ID}) at the corrected asset — done.")
    except Exception as exc:
        print(f"FAILED: {exc}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
