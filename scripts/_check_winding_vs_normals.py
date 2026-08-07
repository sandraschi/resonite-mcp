import json

d = json.load(open(r"C:\temp\nekomimi_meshjson_test.json"))
verts = d["vertices"]
tris = d["submeshes"][0]["triangles"]


def sub(a, b):
    return (a["x"] - b["x"], a["y"] - b["y"], a["z"] - b["z"])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def avg_normal(i0, i1, i2):
    n0 = verts[i0].get("normal")
    n1 = verts[i1].get("normal")
    n2 = verts[i2].get("normal")
    if not (n0 and n1 and n2):
        return None
    return (
        (n0["x"] + n1["x"] + n2["x"]) / 3,
        (n0["y"] + n1["y"] + n2["y"]) / 3,
        (n0["z"] + n1["z"] + n2["z"]) / 3,
    )


agree = 0
disagree = 0
sample = tris[:: max(1, len(tris) // 2000)]  # sample ~2000 triangles spread across mesh
for t in sample:
    i0, i1, i2 = t["vertex0Index"], t["vertex1Index"], t["vertex2Index"]
    p0, p1, p2 = verts[i0]["position"], verts[i1]["position"], verts[i2]["position"]
    e1 = sub(p1, p0)
    e2 = sub(p2, p0)
    face_normal = cross(e1, e2)  # winding-order-derived normal (CCW convention: v0->v1->v2)
    stored = avg_normal(i0, i1, i2)
    if stored is None:
        continue
    d_val = dot(face_normal, stored)
    if d_val > 0:
        agree += 1
    elif d_val < 0:
        disagree += 1

total = agree + disagree
print(f"Sampled {len(sample)} triangles, {total} had normals to compare")
print(f"Winding agrees with stored normal (CCW-consistent): {agree} ({100 * agree / total:.1f}%)")
print(
    f"Winding disagrees with stored normal (would be backface-culled if CCW expected): {disagree} ({100 * disagree / total:.1f}%)"
)
