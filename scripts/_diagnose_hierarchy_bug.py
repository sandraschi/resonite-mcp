"""Diagnose the skeleton hierarchy bug: for each joint in the skin, is its
glTF parent ALSO a joint, or is there a non-joint intermediate node in
between that the current _extract_skeleton silently drops (making the
joint a false 'root')?"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.utils.gltf_meshjson import _read_glb

VRM_PATH = Path(r"C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm")
gltf, _bin = _read_glb(VRM_PATH)

skins = gltf["skins"]
nodes = gltf["nodes"]
joint_indices = set(skins[0]["joints"])

# For each joint, find its real glTF parent (search all nodes' children[])
node_to_parent = {}
for idx, node in enumerate(nodes):
    for child in node.get("children", []):
        node_to_parent[child] = idx

false_roots = 0
non_joint_intermediate = 0
for j in skins[0]["joints"]:
    parent = node_to_parent.get(j)
    if parent is None:
        continue  # genuinely a root, fine
    if parent not in joint_indices:
        non_joint_intermediate += 1
        # walk up further to see how deep the non-joint chain goes
        depth = 0
        cur = parent
        while cur is not None and cur not in joint_indices:
            depth += 1
            cur = node_to_parent.get(cur)
        print(f"joint {j} ({nodes[j].get('name')}) -> non-joint parent {parent} "
              f"({nodes[parent].get('name')}), {depth} non-joint node(s) until nearest joint ancestor {cur}")

print(f"\nTotal joints with a non-joint intermediate parent: {non_joint_intermediate} / {len(skins[0]['joints'])}")
