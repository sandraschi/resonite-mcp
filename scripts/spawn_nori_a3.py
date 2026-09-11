"""Spawn the real, rigged Nori A3 into a live Resonite session and play a "wave hello"
demo animation - the ResoniteLink equivalent of the web viewer's rig + Wave demo button.

Reads norirobotics-mcp/models/nori_description/nori_a3_rig.glb (per-body node hierarchy,
Y-up - see norirobotics-mcp/scripts/export_posed_mesh.py), walks its trimesh scene graph,
and rebuilds the same hierarchy as real Resonite slots: one slot per MuJoCo body, parented
correctly, each with its own StaticMesh/MeshRenderer/PBS_Metallic (one AlbedoColor per body,
from its dominant vertex color - matches the proven spawn_nekomimi_rigged.py pattern rather
than depending on unverified per-vertex mesh-color shading).

Animation is real ResoniteLink slot rotation, not a canned clip: same left-arm
shoulder/elbow/wrist joints, same axes/limits read from the URDF, same math as
web_sota/src/lib/bot-viewer.ts's WAVE_JOINTS - proven to work by test_bone_rotation.py /
test_nod_head_bone.py (rotate a named slot, the bound mesh moves with it).

Run: uv run --with trimesh --with websockets python scripts/spawn_nori_a3.py
"""

from __future__ import annotations

import asyncio
import math
import sys
import time
from pathlib import Path

import trimesh

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient

RIG_GLB = Path(r"D:\Dev\repos\norirobotics-mcp\models\nori_description\nori_a3_rig.glb")
RESONITE_HOST = "localhost"
RESONITE_PORT = 18028  # user-provided; ResoniteLink enabled via Sessions -> Enable ResoniteLink
SPAWN_POS = {"x": 2.0, "y": 0.0, "z": 2.0}

# Same joints/axes/angle functions as bot-viewer.ts's WAVE_JOINTS - real URDF axes/limits,
# not guessed. Left arm, arbitrary choice, mirrors the web viewer's demo exactly.
RAISE_S = 0.7


def smooth01(t: float, duration: float) -> float:
    x = min(max(t / duration, 0.0), 1.0)
    return x * x * (3 - 2 * x)


WAVE_JOINTS = [
    ("left_shoulder_pitch_link", (0.0, 1.0, 0.0), lambda t: -1.3 * smooth01(t, RAISE_S)),
    ("left_shoulder_roll_link", (1.0, 0.0, 0.0), lambda t: 0.5 * smooth01(t, RAISE_S)),
    ("left_elbow_pitch_link", (0.0, 1.0, 0.0), lambda t: -1.1 * smooth01(t, RAISE_S)),
    (
        "left_wrist_roll_link",
        (-1.0, 0.0, 0.0),
        lambda t: 0.0 if t < RAISE_S else 0.7 * math.sin((t - RAISE_S) * 2 * math.pi * 1.1),
    ),
]
ANIMATION_DURATION_S = 6.0
TICK_HZ = 12.0


def quat_mul(a: tuple, b: tuple) -> tuple:
    """Hamilton product a*b, both as (x,y,z,w) - same convention/order as
    test_nod_head_bone.py's proven head-bone rotation."""
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    )


def axis_angle_quat(axis: tuple, angle: float) -> tuple:
    half = angle / 2.0
    s = math.sin(half)
    return (axis[0] * s, axis[1] * s, axis[2] * s, math.cos(half))


def matrix_to_pos_quat(matrix: list[list[float]]) -> tuple[dict, dict]:
    """4x4 row-major -> Resonite float3 position + floatQ rotation (x,y,z,w)."""
    m = trimesh.transformations.quaternion_from_matrix(matrix)  # returns (w, x, y, z)
    w, x, y, z = m
    pos = {"x": float(matrix[0][3]), "y": float(matrix[1][3]), "z": float(matrix[2][3])}
    rot = {"x": float(x), "y": float(y), "z": float(z), "w": float(w)}
    return pos, rot


def dominant_color(mesh: trimesh.Trimesh) -> dict:
    vc = mesh.visual.vertex_colors
    r, g, b, a = (vc[:, i].mean() / 255.0 for i in range(4))
    return {"r": float(r), "g": float(g), "b": float(b), "a": float(a)}


def mesh_to_json(mesh: trimesh.Trimesh) -> tuple[list, list]:
    vertices = [{"position": {"x": float(v[0]), "y": float(v[1]), "z": float(v[2])}} for v in mesh.vertices]
    triangles = [{"vertex0Index": int(f[0]), "vertex1Index": int(f[1]), "vertex2Index": int(f[2])} for f in mesh.faces]
    return vertices, [{"$type": "triangles", "triangles": triangles}]


async def main() -> None:
    print(f"Loading {RIG_GLB.name}...")
    scene = trimesh.load(str(RIG_GLB))
    edges = scene.graph.to_edgelist()
    print(f"{len(edges)} nodes, {len(scene.geometry)} meshes")

    # child -> (parent, matrix, geometry_key|None)
    by_child: dict[str, tuple[str, list, str | None]] = {}
    children_of: dict[str, list[str]] = {}
    for parent, child, data in edges:
        by_child[child] = (parent, data["matrix"], data.get("geometry"))
        children_of.setdefault(parent, []).append(child)

    client = ResoniteLinkClient(host=RESONITE_HOST, port=RESONITE_PORT)
    print(f"Connecting to ResoniteLink at {RESONITE_HOST}:{RESONITE_PORT}...")
    if not await client.connect():
        print("Failed to connect. Is ResoniteLink enabled on this session (Sessions -> Enable ResoniteLink)?")
        return

    slot_ids: dict[str, str] = {}
    joint_rest_rot: dict[str, tuple] = {}

    try:
        info = await client.get_session_info()
        print(f"Connected: {info}")

        root_slot = await client.add_slot(name="nori_a3", position=SPAWN_POS)
        slot_ids["world"] = root_slot
        print(f"Root slot: {root_slot}")

        # BFS from "world" so every parent slot exists before its children are created.
        queue = list(children_of.get("world", []))
        node_count = 0
        while queue:
            name = queue.pop(0)
            parent_name, matrix, geom_key = by_child[name]
            parent_slot = slot_ids[parent_name]
            pos, rot = matrix_to_pos_quat(matrix)
            resonite_name = f"nori_{name}"
            slot_id = await client.add_slot(
                name=name, parent_id=parent_slot, position=pos, rotation=rot, slot_id=resonite_name
            )
            slot_ids[name] = slot_id
            joint_rest_rot[name] = (rot["x"], rot["y"], rot["z"], rot["w"])
            node_count += 1

            if geom_key:
                mesh = scene.geometry[geom_key]
                vertices, submeshes = mesh_to_json(mesh)
                asset_url = await client.import_mesh_json(vertices, submeshes)
                static_mesh_id = await client.add_component(
                    slot_id, "[FrooxEngine]FrooxEngine.StaticMesh", {"URL": {"$type": "Uri", "value": asset_url}}
                )
                renderer_id = await client.add_component(
                    slot_id,
                    "[FrooxEngine]FrooxEngine.MeshRenderer",
                    {"Mesh": {"$type": "reference", "targetId": static_mesh_id}},
                )
                material_id = await client.add_component(
                    slot_id,
                    "[FrooxEngine]FrooxEngine.PBS_Metallic",
                    {"AlbedoColor": {"$type": "colorX", "value": dominant_color(mesh)}},
                )
                await client.update_component(
                    renderer_id,
                    {"Materials": {"$type": "list", "elements": [{"$type": "reference", "targetId": material_id}]}},
                )
                print(
                    f"  [{node_count}/{len(edges)}] {name}: slot={slot_id} mesh={len(mesh.vertices)}v/{len(mesh.faces)}t"
                )
            else:
                print(f"  [{node_count}/{len(edges)}] {name}: slot={slot_id} (no geometry)")

            queue.extend(children_of.get(name, []))

        print(f"SUCCESS: spawned {node_count} slots under root {root_slot}")

        # -- Wave demo: same joints/axes as the web viewer, real ResoniteLink slot rotation --
        missing = [j[0] for j in WAVE_JOINTS if j[0] not in slot_ids]
        if missing:
            print(f"Cannot animate - joint slots not found: {missing}")
        else:
            print(f"Playing wave demo ({ANIMATION_DURATION_S}s)...")
            start = time.monotonic()
            tick_interval = 1.0 / TICK_HZ
            while (t := time.monotonic() - start) < ANIMATION_DURATION_S:
                ops = []
                for name, axis, angle_fn in WAVE_JOINTS:
                    rest = joint_rest_rot[name]
                    delta = axis_angle_quat(axis, angle_fn(t))
                    x, y, z, w = quat_mul(rest, delta)
                    ops.append(
                        {
                            "$type": "updateSlot",
                            "data": {
                                "id": slot_ids[name],
                                "rotation": {"$type": "floatQ", "value": {"x": x, "y": y, "z": z, "w": w}},
                            },
                        }
                    )
                await client.batch(ops)
                await asyncio.sleep(tick_interval)
            print("Wave demo done.")

    except Exception as exc:
        print(f"FAILED: {exc}")
        raise
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
