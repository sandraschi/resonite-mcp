import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions

async def main():
    sessions = await discover_sessions(timeout=15.0)
    home = next((s for s in sessions if "home" in s.get("sessionName", "").lower()), sessions[0])
    client = ResoniteLinkClient(host="localhost", port=home["linkPort"])
    await client.connect()

    vertices = [
        {"position": {"x": 0, "y": 0, "z": 0}, "uvs": [{"$type": "2D", "uv": {"x": 0.0, "y": 0.0}}]},
        {"position": {"x": 1, "y": 0, "z": 0}, "uvs": [{"$type": "2D", "uv": {"x": 1.0, "y": 0.0}}]},
        {"position": {"x": 0, "y": 1, "z": 0}, "uvs": [{"$type": "2D", "uv": {"x": 0.0, "y": 1.0}}]},
    ]
    submeshes = [{"$type": "triangles", "triangles": [{"vertex0Index": 0, "vertex1Index": 1, "vertex2Index": 2}]}]

    print("--- Test: corrected UV shape ($type=2D, uv field) ---")
    try:
        url = await client.import_mesh_json(vertices, submeshes)
        print(f"SUCCESS: {url}")
    except Exception as exc:
        print(f"FAILED: {exc}")

    # Also a corrected bone (real bindPose matrix shape).
    identity = {"m00": 1.0, "m01": 0.0, "m02": 0.0, "m03": 0.0,
                "m10": 0.0, "m11": 1.0, "m12": 0.0, "m13": 0.0,
                "m20": 0.0, "m21": 0.0, "m22": 1.0, "m23": 0.0,
                "m30": 0.0, "m31": 0.0, "m32": 0.0, "m33": 1.0}
    bones = [{"name": "test_bone", "bindPose": identity}]
    verts2 = [
        {"position": {"x": 0, "y": 0, "z": 0}, "boneWeights": [{"boneIndex": 0, "weight": 1.0}]},
        {"position": {"x": 1, "y": 0, "z": 0}, "boneWeights": [{"boneIndex": 0, "weight": 1.0}]},
        {"position": {"x": 0, "y": 1, "z": 0}, "boneWeights": [{"boneIndex": 0, "weight": 1.0}]},
    ]
    print("\n--- Test: corrected bone shape (bindPose float4x4) ---")
    try:
        url = await client.import_mesh_json(verts2, submeshes, bones=bones)
        print(f"SUCCESS: {url}")
    except Exception as exc:
        print(f"FAILED: {exc}")

    # And corrected blendshape frame (position, not weight).
    blendshapes = [{"name": "test_shape", "frames": [
        {"position": 1.0, "positionDeltas": [{"x": 0, "y": 0.1, "z": 0}] * 3}
    ]}]
    print("\n--- Test: corrected blendshape frame (position field) ---")
    try:
        url = await client.import_mesh_json(verts2, submeshes, bones=bones, blendshapes=blendshapes)
        print(f"SUCCESS: {url}")
    except Exception as exc:
        print(f"FAILED: {exc}")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
