"""Cheap live test: is the guessed 'bones'/'boneWeights'/'blendshapes' wire
shape accepted by importMeshJSON at all? Uses a tiny 3-vertex triangle with
one bone and one blendshape -- fast to iterate on, unlike the full VRM."""
from __future__ import annotations
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions


async def main():
    sessions = await discover_sessions(timeout=15.0)
    home = next((s for s in sessions if "home" in s.get("sessionName", "").lower()), sessions[0])
    client = ResoniteLinkClient(host="localhost", port=home["linkPort"])
    await client.connect()

    vertices = [
        {"position": {"x": 0, "y": 0, "z": 0}, "boneWeights": [{"boneIndex": 0, "weight": 1.0}]},
        {"position": {"x": 1, "y": 0, "z": 0}, "boneWeights": [{"boneIndex": 0, "weight": 1.0}]},
        {"position": {"x": 0, "y": 1, "z": 0}, "boneWeights": [{"boneIndex": 0, "weight": 1.0}]},
    ]
    submeshes = [{"$type": "triangles", "triangles": [{"vertex0Index": 0, "vertex1Index": 1, "vertex2Index": 2}]}]
    bones = [{"name": "test_bone", "parentIndex": None,
              "position": {"x": 0, "y": 0, "z": 0}, "rotation": {"x": 0, "y": 0, "z": 0, "w": 1},
              "scale": {"x": 1, "y": 1, "z": 1}}]

    print("--- Test 1: vertices + submeshes + bones (no blendshapes) ---")
    try:
        url = await client.import_mesh_json(vertices, submeshes, bones=bones)
        print(f"SUCCESS: {url}")
    except Exception as exc:
        print(f"FAILED: {exc}")

    variants = [
        ("positionDeltas", lambda deltas: {"name": "test_shape", "positionDeltas": deltas}),
        ("deltaPositions", lambda deltas: {"name": "test_shape", "deltaPositions": deltas}),
        ("vertices", lambda deltas: {"name": "test_shape", "vertices": [{"position": d} for d in deltas]}),
        ("frames-wrapped", lambda deltas: {"name": "test_shape", "frames": [{"weight": 1.0, "positionDeltas": deltas}]}),
    ]
    deltas = [{"x": 0, "y": 0.1, "z": 0}, {"x": 0, "y": 0.1, "z": 0}, {"x": 0, "y": 0.1, "z": 0}]
    for label, make in variants:
        print(f"\n--- Test 2 variant: {label} ---")
        try:
            url = await client.import_mesh_json(vertices, submeshes, bones=bones, blendshapes=[make(deltas)])
            print(f"SUCCESS ({label}): {url}")
            break
        except Exception as exc:
            print(f"FAILED ({label}): {exc}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
