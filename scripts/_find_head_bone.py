import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.utils.gltf_meshjson import gltf_to_mesh_json

VRM_PATH = Path(r"C:\Users\sandr\.avatarmcp\models\Nekomimi-chan.vrm")
mesh = gltf_to_mesh_json(VRM_PATH, include_skinning=True)
bones = mesh["bones"]
for i, b in enumerate(bones):
    if "head" in b["name"].lower() or "neck" in b["name"].lower():
        print(i, b["name"])
