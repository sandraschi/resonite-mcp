import json
d = json.load(open(r"C:\temp\nekomimi_meshjson_test.json"))
verts = d["vertices"]
xs = [v["position"]["x"] for v in verts]
ys = [v["position"]["y"] for v in verts]
zs = [v["position"]["z"] for v in verts]
print(f"X: {min(xs):.4f} to {max(xs):.4f} (span {max(xs)-min(xs):.4f})")
print(f"Y: {min(ys):.4f} to {max(ys):.4f} (span {max(ys)-min(ys):.4f})")
print(f"Z: {min(zs):.4f} to {max(zs):.4f} (span {max(zs)-min(zs):.4f})")
print(f"vertex count: {len(verts)}")
