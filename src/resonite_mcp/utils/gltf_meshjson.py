"""
glTF/GLB -> ResoniteLink mesh-JSON converter.

Bridges blender-mcp's glTF exports (home-shell refinery, furniture kit-bash,
and eventually VRM-derived avatar meshes) into the wire format resonite-mcp's
ResoniteLinkClient.import_mesh_json() sends over the wire — see
resonite_mcp.resonite_link for the schema this targets.

COORDINATE FIX (confirmed live 2026-07-19): glTF (right-handed, Y-up,
-Z-forward) and Resonite/FrooxEngine's coordinate convention don't match.
A naive 1:1 copy produces a mesh that is completely invisible from any
external viewing angle — not corrupted, just uniformly inside-out (verified
mathematically: 99.9% of a 2000-triangle sample had winding fully
consistent with their own stored normals, meaning the *source* data was
fine; the mismatch is the target engine's convention, not the parser).
Fix, applied by default here: negate Z on every position and normal, and
reverse each triangle's winding (swap vertex1Index/vertex2Index). Live-
verified: Nekomimi-chan's full VRM mesh (190,111 vertices, 45,451
triangles) spawned into a real Resonite session and was visually confirmed
visible with this fix applied, invisible without it. Set
`resonite_coordinate_fix=False` only if you're feeding output somewhere
that already expects raw glTF-convention data (e.g. re-exporting).

Reads GLB binary containers (JSON chunk + BIN chunk) using only the stdlib —
no pygltflib/trimesh dependency, so nothing new to install on Goliath.

HONESTY NOTE: vertex "position" and "normal" (with the coordinate fix
above) are now live-verified end-to-end. "uvs" shape is confirmed to be a
LIST of {"x","y"} dicts (multi-UV-channel support), but each element's
`$type` polymorphic discriminator is still unknown after four live
attempts (`UV_Coordinate`/`float2`/`uv`/`UVCoordinate` all rejected) —
UVs will fail to import until that's resolved; strip them if you hit that.
Bones/blendshapes (needed for the VRM avatar path) are intentionally NOT
implemented here yet — GLB skinning data (JOINTS_0/WEIGHTS_0) decodes
differently and deserves its own pass once this static-mesh path is proven.

Known simplifications (v1, not silent — logged as warnings):
  - Only the first primitive of each mesh is converted; multi-material
    meshes with several primitives will lose all but the first.
  - Only TRIANGLES-mode primitives (glTF mode 4, the default) are handled.
  - Multiple meshes in one glTF are merged into one combined vertex/
    submesh list (vertex indices offset accordingly) — fine for a single
    collider/shell blob, may not be what you want for a scene with many
    independent objects; revisit if that case shows up.
"""

from __future__ import annotations

import base64
import json
import logging
import struct
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

GLB_MAGIC = 0x46546C67  # b'glTF' little-endian
CHUNK_TYPE_JSON = 0x4E4F534A  # b'JSON'
CHUNK_TYPE_BIN = 0x004E4942  # b'BIN\0'

# glTF componentType -> (struct format char, byte size)
_COMPONENT_TYPES: dict[int, tuple[str, int]] = {
    5120: ("b", 1),  # BYTE
    5121: ("B", 1),  # UNSIGNED_BYTE
    5122: ("h", 2),  # SHORT
    5123: ("H", 2),  # UNSIGNED_SHORT
    5125: ("I", 4),  # UNSIGNED_INT
    5126: ("f", 4),  # FLOAT
}

# glTF accessor "type" -> number of components
_TYPE_COMPONENT_COUNTS: dict[str, int] = {
    "SCALAR": 1,
    "VEC2": 2,
    "VEC3": 3,
    "VEC4": 4,
    "MAT2": 4,
    "MAT3": 9,
    "MAT4": 16,
}


class GltfConversionError(Exception):
    """Raised when a glTF/GLB file can't be parsed or converted."""


def _read_glb(path: Path) -> tuple[dict[str, Any], bytes | None]:
    """Parse a .glb container into (json_dict, binary_chunk_or_None).

    Also accepts plain .gltf (JSON-only, no BIN chunk framing) — detected by
    the absence of the GLB magic number, in which case the file is parsed as
    plain JSON and any buffers must be embedded as base64 data URIs.
    """
    raw = path.read_bytes()
    if len(raw) < 12 or struct.unpack_from("<I", raw, 0)[0] != GLB_MAGIC:
        # Not a binary GLB — treat as plain-text .gltf JSON.
        return json.loads(raw.decode("utf-8")), None

    _magic, _version, total_length = struct.unpack_from("<III", raw, 0)
    if total_length != len(raw):
        logger.warning(
            "%s: header length %d != actual file size %d (continuing anyway)",
            path.name,
            total_length,
            len(raw),
        )

    offset = 12
    json_chunk: dict[str, Any] | None = None
    bin_chunk: bytes | None = None
    while offset < len(raw):
        if offset + 8 > len(raw):
            break
        chunk_length, chunk_type = struct.unpack_from("<II", raw, offset)
        offset += 8
        chunk_data = raw[offset : offset + chunk_length]
        offset += chunk_length
        if chunk_type == CHUNK_TYPE_JSON:
            json_chunk = json.loads(chunk_data.decode("utf-8"))
        elif chunk_type == CHUNK_TYPE_BIN:
            bin_chunk = chunk_data
        else:
            logger.warning("%s: skipping unknown chunk type 0x%08X", path.name, chunk_type)

    if json_chunk is None:
        raise GltfConversionError(f"{path}: no JSON chunk found in GLB container")
    return json_chunk, bin_chunk


def _resolve_buffer(gltf: dict[str, Any], buffer_index: int, glb_bin: bytes | None, base_dir: Path) -> bytes:
    """Return the raw bytes for buffers[buffer_index].

    Handles: no-URI buffers (the GLB BIN chunk), base64 data URIs, and
    external file URIs (relative to the glTF/GLB's own directory).
    """
    buffer_def = gltf["buffers"][buffer_index]
    uri = buffer_def.get("uri")
    if uri is None:
        if glb_bin is None:
            raise GltfConversionError(
                f"buffer {buffer_index} has no uri and this file has no GLB BIN chunk"
            )
        return glb_bin
    if uri.startswith("data:"):
        header, _, encoded = uri.partition(",")
        if ";base64" not in header:
            raise GltfConversionError(f"buffer {buffer_index}: unsupported non-base64 data URI")
        return base64.b64decode(encoded)
    # External file reference, relative to the glTF file's own directory.
    ext_path = base_dir / uri
    if not ext_path.exists():
        raise GltfConversionError(f"buffer {buffer_index}: external file not found: {ext_path}")
    return ext_path.read_bytes()


def _decode_accessor(
    gltf: dict[str, Any],
    accessor_index: int,
    glb_bin: bytes | None,
    base_dir: Path,
    _buffer_cache: dict[int, bytes],
) -> list[tuple[float, ...]]:
    """Decode an accessor into a list of component tuples (one tuple per element)."""
    accessor = gltf["accessors"][accessor_index]
    count = accessor["count"]
    component_type = accessor["componentType"]
    accessor_type = accessor["type"]
    normalized = accessor.get("normalized", False)

    if component_type not in _COMPONENT_TYPES:
        raise GltfConversionError(f"accessor {accessor_index}: unsupported componentType {component_type}")
    if accessor_type not in _TYPE_COMPONENT_COUNTS:
        raise GltfConversionError(f"accessor {accessor_index}: unsupported type {accessor_type}")

    fmt_char, comp_size = _COMPONENT_TYPES[component_type]
    n_components = _TYPE_COMPONENT_COUNTS[accessor_type]
    element_size = comp_size * n_components

    buffer_view_index = accessor.get("bufferView")
    if buffer_view_index is None:
        # Accessor has no data (sparse-only or fully zero) — not needed for
        # this project's fixtures; fail loudly rather than fake zeros.
        raise GltfConversionError(f"accessor {accessor_index}: sparse/zero-filled accessors not supported")

    buffer_view = gltf["bufferViews"][buffer_view_index]
    buffer_index = buffer_view["buffer"]
    if buffer_index not in _buffer_cache:
        _buffer_cache[buffer_index] = _resolve_buffer(gltf, buffer_index, glb_bin, base_dir)
    buffer_bytes = _buffer_cache[buffer_index]

    view_offset = buffer_view.get("byteOffset", 0)
    accessor_offset = accessor.get("byteOffset", 0)
    stride = buffer_view.get("byteStride", element_size)
    start = view_offset + accessor_offset

    results: list[tuple[float, ...]] = []
    fmt = f"<{n_components}{fmt_char}"
    for i in range(count):
        elem_start = start + i * stride
        values = struct.unpack_from(fmt, buffer_bytes, elem_start)
        if normalized and fmt_char in ("b", "B", "h", "H"):
            max_val = {"b": 127, "B": 255, "h": 32767, "H": 65535}[fmt_char]
            values = tuple(v / max_val for v in values)
        results.append(values)
    return results


def _decode_accessor_int(
    gltf: dict[str, Any],
    accessor_index: int,
    glb_bin: bytes | None,
    base_dir: Path,
    _buffer_cache: dict[int, bytes],
) -> list[tuple[int, ...]]:
    """Like _decode_accessor but forces integer results (for JOINTS_0, which
    is UNSIGNED_BYTE or UNSIGNED_SHORT and must NOT go through the
    `normalized` float-division path _decode_accessor applies to those
    component types for color/UV-style data)."""
    accessor = gltf["accessors"][accessor_index]
    saved_normalized = accessor.get("normalized")
    accessor["normalized"] = False
    try:
        raw = _decode_accessor(gltf, accessor_index, glb_bin, base_dir, _buffer_cache)
    finally:
        if saved_normalized is None:
            accessor.pop("normalized", None)
        else:
            accessor["normalized"] = saved_normalized
    return [tuple(int(v) for v in tup) for tup in raw]


def _quat_to_matrix(qx: float, qy: float, qz: float, qw: float) -> list[list[float]]:
    """Quaternion (glTF order x,y,z,w) -> 3x3 rotation matrix, row-major."""
    xx, yy, zz = qx * qx, qy * qy, qz * qz
    xy, xz, yz = qx * qy, qx * qz, qy * qz
    wx, wy, wz = qw * qx, qw * qy, qw * qz
    return [
        [1 - 2 * (yy + zz), 2 * (xy - wz), 2 * (xz + wy)],
        [2 * (xy + wz), 1 - 2 * (xx + zz), 2 * (yz - wx)],
        [2 * (xz - wy), 2 * (yz + wx), 1 - 2 * (xx + yy)],
    ]


def _trs_to_matrix(
    translation: list[float], rotation: list[float], scale: list[float]
) -> list[list[float]]:
    """Compose glTF TRS (translation, quaternion xyzw, scale) into a 4x4
    row-major matrix (last row [0,0,0,1], translation in the last COLUMN —
    the convention this project's rl_value("float4x4", ...) output uses,
    matching FrooxEngine's row-major m_rowcol field naming)."""
    r = _quat_to_matrix(*rotation)
    sx, sy, sz = scale
    tx, ty, tz = translation
    return [
        [r[0][0] * sx, r[0][1] * sy, r[0][2] * sz, tx],
        [r[1][0] * sx, r[1][1] * sy, r[1][2] * sz, ty],
        [r[2][0] * sx, r[2][1] * sy, r[2][2] * sz, tz],
        [0.0, 0.0, 0.0, 1.0],
    ]


def _matrix_multiply(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [
        [sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)]
        for i in range(4)
    ]


def _matrix_to_wire(m: list[list[float]]) -> dict[str, float]:
    return {f"m{i}{j}": m[i][j] for i in range(4) for j in range(4)}


def _wire_to_matrix(w: dict[str, float]) -> list[list[float]]:
    return [[w[f"m{i}{j}"] for j in range(4)] for i in range(4)]


def _reflect_z_matrix(w: dict[str, float]) -> dict[str, float]:
    """Mirror a rigid-transform matrix across Z, matching the same
    coordinate fix applied to vertex positions/normals elsewhere in this
    module. Conjugation (Z @ M @ Z, with Z = diag(1,1,-1,1)) is the
    mathematically correct way to mirror a full rotation+translation
    matrix — flipping individual fields by hand (an earlier, sloppier
    version of this function) risks getting the rotation part wrong."""
    z = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, -1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
    m = _wire_to_matrix(w)
    return _matrix_to_wire(_matrix_multiply(_matrix_multiply(z, m), z))


def _build_child_to_parent_map(nodes: list[dict[str, Any]]) -> dict[int, int]:
    child_to_parent: dict[int, int] = {}
    for parent_idx, node in enumerate(nodes):
        for child_idx in node.get("children", []):
            child_to_parent[child_idx] = parent_idx
    return child_to_parent


def _node_world_matrix(
    node_idx: int,
    nodes: list[dict[str, Any]],
    child_to_parent: dict[int, int],
    cache: dict[int, list[list[float]]],
) -> list[list[float]]:
    """World-space (bind pose) matrix for a node — its own local TRS
    composed with every ancestor's, walking up the FULL node graph (not
    just joints in this skin), since a bind pose is relative to the
    mesh's own local space, which may sit under non-joint ancestor nodes."""
    if node_idx in cache:
        return cache[node_idx]
    node = nodes[node_idx]
    if "matrix" in node:
        # glTF allows a raw 16-value column-major matrix instead of TRS;
        # rare for VRM exporters but handled for correctness. glTF's
        # `matrix` array is column-major; transpose into our row-major form.
        flat = node["matrix"]
        local = [[flat[c * 4 + r] for c in range(4)] for r in range(4)]
    else:
        local = _trs_to_matrix(
            node.get("translation", [0.0, 0.0, 0.0]),
            node.get("rotation", [0.0, 0.0, 0.0, 1.0]),
            node.get("scale", [1.0, 1.0, 1.0]),
        )
    parent_idx = child_to_parent.get(node_idx)
    if parent_idx is None:
        world = local
    else:
        world = _matrix_multiply(
            _node_world_matrix(parent_idx, nodes, child_to_parent, cache), local
        )
    cache[node_idx] = world
    return world


def _extract_skeleton(gltf: dict[str, Any], skin_index: int) -> list[dict[str, Any]]:
    """Build a `bones` list matching the REAL ResoniteLink schema, confirmed
    2026-07-19 by reading the actual open-source C# models
    (ResoniteLink/Models/Assets/Mesh/JSON/Bone.cs): each bone is just
    {"name": str, "bindPose": <float4x4>} — NOT the parentIndex/position/
    rotation/scale shape an earlier version of this function guessed
    (which the server silently accepted, ignoring the unrecognized fields
    — a real, since-fixed bug: bind poses were never actually being set).

    bindPose is each joint's world-space transform at rest pose, computed
    by composing TRS matrices up the full node ancestor chain (not just
    joints in this skin) via quaternion-to-matrix + matrix multiplication,
    implemented from scratch here (stdlib only, no numpy).

    Returns bones in the SAME order as the skin's `joints` array, so
    JOINTS_0 vertex indices map directly onto this list by position.
    """
    skins = gltf.get("skins")
    if not skins or skin_index >= len(skins):
        raise GltfConversionError(f"skin index {skin_index} not found in gltf.skins")
    skin = skins[skin_index]
    joint_node_indices: list[int] = skin["joints"]
    nodes = gltf.get("nodes", [])
    child_to_parent = _build_child_to_parent_map(nodes)
    matrix_cache: dict[int, list[list[float]]] = {}

    bones: list[dict[str, Any]] = []
    for node_idx in joint_node_indices:
        node = nodes[node_idx] if node_idx < len(nodes) else {}
        name = node.get("name", f"bone_{node_idx}")
        world_matrix = _node_world_matrix(node_idx, nodes, child_to_parent, matrix_cache)
        bones.append({"name": name, "bindPose": _matrix_to_wire(world_matrix)})
    return bones


def _decode_morph_targets(
    gltf: dict[str, Any],
    primitive: dict[str, Any],
    glb_bin: bytes | None,
    base_dir: Path,
    buffer_cache: dict[int, bytes],
) -> list[dict[str, Any]]:
    """Decode glTF morph targets (blend shapes) on a primitive into a list
    of {"name": str, "frames": [{"position": 1.0, "positionDeltas": [...]}]}
    — one entry per target (confirmed shape, see below).

    CONFIRMED 2026-07-19 by reading the real C# model (BlendshapeFrame.cs):
    blendshapes need a "frames" wrapper around positionDeltas, and each
    frame's progress field is "position" (0..1), not "weight" as an
    earlier version of this function guessed.

    glTF stores morph targets as extra POSITION/NORMAL/TANGENT *delta*
    accessors under primitive["targets"], with optional human-readable
    names in mesh["extras"]["targetNames"] (a common but non-standard
    convention many exporters, including VRM, follow).
    """
    targets = primitive.get("targets")
    if not targets:
        return []
    target_names = primitive.get("_meshExtrasTargetNames") or []

    blendshapes = []
    for i, target in enumerate(targets):
        name = target_names[i] if i < len(target_names) else f"blendshape_{i}"
        pos_accessor = target.get("POSITION")
        if pos_accessor is None:
            continue
        deltas = _decode_accessor(gltf, pos_accessor, glb_bin, base_dir, buffer_cache)
        blendshapes.append(
            {
                "name": name,
                # CONFIRMED 2026-07-19 by reading the real C# model
                # (BlendshapeFrame.cs): the frame's field is "position"
                # (0..1 progress within the blendshape animation, 1.0 for
                # a single-frame shape) — NOT "weight", which an earlier
                # version of this function guessed and which the server
                # silently accepted while ignoring (so it was never
                # actually being set).
                "frames": [
                    {
                        "position": 1.0,
                        "positionDeltas": [{"x": d[0], "y": d[1], "z": d[2]} for d in deltas],
                    }
                ],
            }
        )
    return blendshapes


def gltf_to_mesh_json(
    path: str | Path,
    resonite_coordinate_fix: bool = True,
    include_skinning: bool = False,
) -> dict[str, Any]:
    """Convert a .glb/.gltf file into the ResoniteLink importMeshJSON payload shape.

    Returns {"vertices": [...], "submeshes": [...]} ready to pass straight
    into ResoniteLinkClient.import_mesh_json(**result) or .spawn_mesh(**result).
    If `include_skinning` is True and the source has skin/morph data, the
    result also has "bones" and/or "blendshapes" keys (see
    `import_mesh_json`'s signature) — pass those through too.

    resonite_coordinate_fix (default True): negate Z on every position/
    normal and reverse triangle winding to compensate for the glTF-vs-
    Resonite coordinate mismatch (see module docstring). Live-verified
    necessary — leave this on unless you have a specific reason not to.

    include_skinning (default False, EXPERIMENTAL 2026-07-19, UNPROVEN):
    decode JOINTS_0/WEIGHTS_0 into per-vertex "boneWeights" and glTF
    skins into a "bones" list; decode morph targets into "blendshapes".
    The Resonite-side wire shape for both has not been confirmed against
    a live session (see TODO/STATUS docs) — treat any output using this
    flag as "parses the source correctly, wire shape not yet verified."

    Merges every TRIANGLES-mode primitive across every mesh in the file into
    one combined vertex/submesh list (see module docstring for the v1
    simplifications this implies). Raises GltfConversionError with a specific
    reason if the file has nothing convertible.
    """
    path = Path(path)
    if not path.exists():
        raise GltfConversionError(f"file not found: {path}")

    gltf, glb_bin = _read_glb(path)
    base_dir = path.parent
    buffer_cache: dict[int, bytes] = {}

    meshes = gltf.get("meshes")
    if not meshes:
        raise GltfConversionError(f"{path.name}: no meshes[] in this glTF")

    # Map mesh index -> node that references it (needed to find that node's
    # skin, since skin is a NODE property in glTF, not a mesh property).
    mesh_to_skin: dict[int, int] = {}
    if include_skinning:
        for node in gltf.get("nodes", []):
            if "mesh" in node and "skin" in node:
                mesh_to_skin[node["mesh"]] = node["skin"]

        # glTF's non-standard-but-common convention for morph target names
        # lives at mesh["extras"]["targetNames"] — stash it per-primitive
        # under a private key so _decode_morph_targets can find it without
        # threading another parameter through every call site.
        for mesh in meshes:
            target_names = (mesh.get("extras") or {}).get("targetNames")
            if target_names:
                for primitive in mesh.get("primitives", []):
                    primitive["_meshExtrasTargetNames"] = target_names

    all_vertices: list[dict[str, Any]] = []
    all_triangles: list[dict[str, int]] = []
    all_blendshapes: list[dict[str, Any]] = []
    bones: list[dict[str, Any]] | None = None
    vertex_offset = 0
    primitives_converted = 0
    primitives_skipped = 0

    for mesh_idx, mesh in enumerate(meshes):
        if include_skinning and mesh_idx in mesh_to_skin and bones is None:
            bones = _extract_skeleton(gltf, mesh_to_skin[mesh_idx])
            if resonite_coordinate_fix:
                for bone in bones:
                    bone["bindPose"] = _reflect_z_matrix(bone["bindPose"])

        for prim_idx, primitive in enumerate(mesh.get("primitives", [])):
            mode = primitive.get("mode", 4)  # 4 = TRIANGLES is the glTF default
            if mode != 4:
                logger.warning(
                    "%s: mesh %d primitive %d has mode=%d (not TRIANGLES) — skipped",
                    path.name, mesh_idx, prim_idx, mode,
                )
                primitives_skipped += 1
                continue

            attributes = primitive.get("attributes", {})
            if "POSITION" not in attributes:
                logger.warning(
                    "%s: mesh %d primitive %d has no POSITION attribute — skipped",
                    path.name, mesh_idx, prim_idx,
                )
                primitives_skipped += 1
                continue

            positions = _decode_accessor(gltf, attributes["POSITION"], glb_bin, base_dir, buffer_cache)
            normals = (
                _decode_accessor(gltf, attributes["NORMAL"], glb_bin, base_dir, buffer_cache)
                if "NORMAL" in attributes else None
            )
            uvs = (
                _decode_accessor(gltf, attributes["TEXCOORD_0"], glb_bin, base_dir, buffer_cache)
                if "TEXCOORD_0" in attributes else None
            )
            joints = weights = None
            if include_skinning and "JOINTS_0" in attributes and "WEIGHTS_0" in attributes:
                joints = _decode_accessor_int(gltf, attributes["JOINTS_0"], glb_bin, base_dir, buffer_cache)
                weights = _decode_accessor(gltf, attributes["WEIGHTS_0"], glb_bin, base_dir, buffer_cache)

            for i, pos in enumerate(positions):
                z = -pos[2] if resonite_coordinate_fix else pos[2]
                vertex: dict[str, Any] = {"position": {"x": pos[0], "y": pos[1], "z": z}}
                if normals is not None:
                    n = normals[i]
                    nz = -n[2] if resonite_coordinate_fix else n[2]
                    vertex["normal"] = {"x": n[0], "y": n[1], "z": nz}
                if uvs is not None:
                    uv = uvs[i]
                    # CONFIRMED 2026-07-19 by reading the real C# model
                    # (UV_Coordinate.cs): the discriminator is "2D" (not
                    # any of "UV_Coordinate"/"float2"/"uv"/"UVCoordinate",
                    # all tried and rejected live 2026-07-18), and the
                    # value lives under a "uv" field (a float2), not bare
                    # top-level x/y. Still a LIST (multi-UV-channel support).
                    vertex["uvs"] = [{"$type": "2D", "uv": {"x": uv[0], "y": uv[1]}}]
                if joints is not None:
                    # CONFIRMED via reflection and a successful live test
                    # 2026-07-19: BoneWeight.cs is exactly
                    # {"boneIndex": int, "weight": float} — matches what
                    # was already here.
                    vertex["boneWeights"] = [
                        {"boneIndex": joints[i][k], "weight": weights[i][k]}
                        for k in range(len(joints[i]))
                        if weights[i][k] > 0.0
                    ]
                all_vertices.append(vertex)

            if include_skinning:
                targets_this_prim = _decode_morph_targets(gltf, primitive, glb_bin, base_dir, buffer_cache)
                if resonite_coordinate_fix:
                    for bs in targets_this_prim:
                        for frame in bs["frames"]:
                            for d in frame["positionDeltas"]:
                                d["z"] = -d["z"]
                all_blendshapes.extend(targets_this_prim)

            indices_accessor = primitive.get("indices")
            if indices_accessor is not None:
                indices = _decode_accessor(gltf, indices_accessor, glb_bin, base_dir, buffer_cache)
                flat_indices = [int(v[0]) for v in indices]
            else:
                # No index buffer: positions are already in triangle order.
                flat_indices = list(range(len(positions)))

            if len(flat_indices) % 3 != 0:
                raise GltfConversionError(
                    f"{path.name}: mesh {mesh_idx} primitive {prim_idx} has "
                    f"{len(flat_indices)} indices, not a multiple of 3"
                )

            for tri_start in range(0, len(flat_indices), 3):
                v0 = flat_indices[tri_start] + vertex_offset
                v1 = flat_indices[tri_start + 1] + vertex_offset
                v2 = flat_indices[tri_start + 2] + vertex_offset
                if resonite_coordinate_fix:
                    v1, v2 = v2, v1  # reverse winding to match the Z-negation above
                all_triangles.append(
                    {
                        "vertex0Index": v0,
                        "vertex1Index": v1,
                        "vertex2Index": v2,
                    }
                )

            vertex_offset += len(positions)
            primitives_converted += 1

    if primitives_converted == 0:
        raise GltfConversionError(f"{path.name}: no convertible TRIANGLES primitives found")

    logger.info(
        "%s: converted %d primitive(s) (%d skipped) -> %d vertices, %d triangles"
        + (f", {len(bones)} bones" if bones else "")
        + (f", {len(all_blendshapes)} blendshapes" if all_blendshapes else ""),
        path.name, primitives_converted, primitives_skipped, len(all_vertices), len(all_triangles),
    )

    result: dict[str, Any] = {
        "vertices": all_vertices,
        "submeshes": [{"$type": "triangles", "triangles": all_triangles}],
    }
    if bones:
        result["bones"] = bones
    if all_blendshapes:
        result["blendshapes"] = all_blendshapes
    return result


def _main() -> int:
    """CLI smoke test: convert a file and print/save a summary.

    Usage: python -m resonite_mcp.utils.gltf_meshjson <path.glb> [output.json]
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    if len(sys.argv) < 2:
        print("Usage: gltf_meshjson.py <path.glb> [output.json]")
        return 1

    src = Path(sys.argv[1])
    try:
        result = gltf_to_mesh_json(src)
    except GltfConversionError as exc:
        print(f"CONVERSION FAILED: {exc}")
        return 1

    n_verts = len(result["vertices"])
    n_tris = sum(len(sm["triangles"]) for sm in result["submeshes"])
    has_normals = n_verts > 0 and "normal" in result["vertices"][0]
    has_uvs = n_verts > 0 and "uvs" in result["vertices"][0]
    print(f"{src.name}: {n_verts} vertices, {n_tris} triangles "
          f"(normals={'yes' if has_normals else 'no'}, uvs={'yes' if has_uvs else 'no'})")

    if len(sys.argv) >= 3:
        out_path = Path(sys.argv[2])
        out_path.write_text(json.dumps(result), encoding="utf-8")
        print(f"Wrote mesh-JSON to {out_path} ({out_path.stat().st_size:,} bytes)")

    return 0


if __name__ == "__main__":
    sys.exit(_main())
