import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions

HEAD_BONE_SLOT = "nekomimi_bone_42"
ORIGINAL_ROTATION = {"x": 0, "y": 0.3826835, "z": 0, "w": 0.9238796}  # captured before the nod test


async def main():
    sessions = await discover_sessions(timeout=15.0)
    home = next((s for s in sessions if "home" in s.get("sessionName", "").lower()), sessions[0])
    client = ResoniteLinkClient(host="localhost", port=home["linkPort"])
    await client.connect()

    # 1. Reset head bone to its original bind-pose rotation (undo the nod)
    try:
        await client.update_slot(
            {
                "id": HEAD_BONE_SLOT,
                "rotation": {"$type": "floatQ", "value": ORIGINAL_ROTATION},
            }
        )
        print("Head bone rotation reset to original bind pose")
    except Exception as exc:
        print(f"Reset FAILED: {exc}")

    # 2. Disable the plain MeshRenderer, re-enable SkinnedMeshRenderer --
    # isolated test: skinning ON, but at neutral pose, nothing rotated.
    try:
        await client.update_component("Reso_E8B", {"Enabled": False})
        print("Disabled plain MeshRenderer (Reso_E8B)")
    except Exception as exc:
        print(f"Disable plain renderer FAILED: {exc}")

    try:
        await client.update_component("Reso_9", {"Enabled": True})
        print("Re-enabled SkinnedMeshRenderer (Reso_9) -- AT NEUTRAL POSE, nothing rotated")
    except Exception as exc:
        print(f"Enable skinned renderer FAILED: {exc}")

    await client.disconnect()


asyncio.run(main())
