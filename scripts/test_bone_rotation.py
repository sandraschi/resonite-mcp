import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions
from resonite_mcp.utils.gltf_meshjson import gltf_to_mesh_json

VRM_PATH = Path(r"C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm")

async def main():
    mesh = gltf_to_mesh_json(VRM_PATH, include_skinning=True)
    bones = mesh["bones"]
    names = [b["name"] for b in bones]

    # Find a head/neck bone -- VRM standard naming.
    head_idx = next((i for i, n in enumerate(names) if "Head" in n and "J_Bip" in n), None)
    print(f"Head bone index: {head_idx}, name: {names[head_idx] if head_idx is not None else 'NOT FOUND'}")
    if head_idx is None:
        print("Searching for any bone with 'Head' in the name:")
        for i, n in enumerate(names):
            if "head" in n.lower():
                print(f"  [{i}] {n}")
        return

    bone_id = f"nekomimi_bone_{head_idx}"

    sessions = await discover_sessions(timeout=15.0)
    home = next((s for s in sessions if "home" in s.get("sessionName", "").lower()), sessions[0])
    client = ResoniteLinkClient(host="localhost", port=home["linkPort"])
    await client.connect()

    # Rotate the head bone 45 degrees around Y (a visible head-turn).
    import math
    angle = math.radians(45)
    qy = {"x": 0.0, "y": math.sin(angle / 2), "z": 0.0, "w": math.cos(angle / 2)}
    try:
        result = await client.update_slot({"id": bone_id, "rotation": {"$type": "floatQ", "value": qy}})
        print(f"Rotated head bone ({bone_id}) 45deg around Y: SUCCESS -> {result}")
    except Exception as exc:
        print(f"FAILED: {exc}")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
