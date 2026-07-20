"""Prove the rig actually works: rotate Nekomimi-chan's head bone and see
if the mesh deforms with it. This is the real test -- everything before
this only proved the DATA was accepted, not that skinning functions."""
from __future__ import annotations
import asyncio
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions

HEAD_BONE_SLOT = "nekomimi_bone_42"  # J_Bip_C_Head


def quat_mul(a, b):
    """Hamilton product a*b, both as (x,y,z,w)."""
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    )


async def main():
    sessions = await discover_sessions(timeout=15.0)
    home = next((s for s in sessions if "home" in s.get("sessionName", "").lower()), sessions[0])
    client = ResoniteLinkClient(host="localhost", port=home["linkPort"])
    await client.connect()

    # Read current bind-pose rotation of the head bone
    slot_data = await client.get_slot(HEAD_BONE_SLOT, include_component_data=False, depth=0)
    current_rot = slot_data["data"]["rotation"]["value"]
    current = (current_rot["x"], current_rot["y"], current_rot["z"], current_rot["w"])
    print(f"Current head bone rotation: {current}")

    # A 40-degree "nod" (rotation around local X axis), composed onto the
    # existing bind pose rather than replacing it outright.
    half_angle = math.radians(40) / 2
    delta = (math.sin(half_angle), 0.0, 0.0, math.cos(half_angle))
    new_rot = quat_mul(current, delta)
    print(f"New head bone rotation (bind pose + 40deg nod): {new_rot}")

    try:
        result = await client.update_slot({
            "id": HEAD_BONE_SLOT,
            "rotation": {"$type": "floatQ", "value": {"x": new_rot[0], "y": new_rot[1], "z": new_rot[2], "w": new_rot[3]}},
        })
        print(f"SUCCESS: head bone rotated. {result}")
    except Exception as exc:
        print(f"FAILED: {exc}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
