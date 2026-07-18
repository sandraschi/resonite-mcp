"""
glTF/GLB -> ResoniteLink mesh-JSON converter.

Bridges blender-mcp's glTF exports (home-shell refinery, furniture kit-bash,
and eventually VRM-derived avatar meshes) into the wire format resonite-mcp's
ResoniteLinkClient.import_mesh_json() sends over the wire — see
resonite_mcp.resonite_link for the schema this targets.

Status (2026-07-18): first implementation, not yet run against real fixtures.
Reads GLB binary containers (JSON chunk + BIN chunk) using only the stdlib —
no pygltflib/trimesh dependency, so nothing new to install on Goliath.

HONESTY NOTE: only vertex "position" was live-verified end-to-end through
ResoniteLink in the original Phase 0 spike (hand-built unit cube). This
converter also emits "normal" and "uvs" per vertex. Update 2026-07-18:
"uvs" shape has now been LIVE-CONFIRMED (via a real server error against
Nekomimi-chan.vrm, 45k triangles) to be a LIST of {"x","y"} dicts, not a
bare dict — Resonite supports multiple UV channels per vertex, this
converter always emits a single-element list (TEXCOORD_0 only). "normal"
remains unverified live but follows the same {"x","y","z"} pattern as
position, which is now proven correct.
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


def gltf_to_mesh_json(path: str | Path) -> dict[str, Any]:
    """Convert a .glb/.gltf file into the ResoniteLink importMeshJSON payload shape.

    Returns {"vertices": [...], "submeshes": [...]} ready to pass straight
    into ResoniteLinkClient.import_mesh_json(**result) or .spawn_mesh(**result).

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

    all_vertices: list[dict[str, Any]] = []
    all_triangles: list[dict[str, int]] = []
    vertex_offset = 0
    primitives_converted = 0
    primitives_skipped = 0

    for mesh_idx, mesh in enumerate(meshes):
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

            for i, pos in enumerate(positions):
                vertex: dict[str, Any] = {"position": {"x": pos[0], "y": pos[1], "z": pos[2]}}
                if normals is not None:
                    n = normals[i]
                    vertex["normal"] = {"x": n[0], "y": n[1], "z": n[2]}
                if uvs is not None:
                    uv = uvs[i]
                    # CONFIRMED live 2026-07-18 (Nekomimi-chan.vrm test): uvs is a
                    # LIST of UV_Coordinate, not a bare {x,y} dict — Resonite
                    # supports multiple UV channels (TEXCOORD_0, TEXCOORD_1, ...).
                    # This converter only reads TEXCOORD_0, so always a 1-element list.
                    vertex["uvs"] = [{"x": uv[0], "y": uv[1]}]
                all_vertices.append(vertex)

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
                all_triangles.append(
                    {
                        "vertex0Index": flat_indices[tri_start] + vertex_offset,
                        "vertex1Index": flat_indices[tri_start + 1] + vertex_offset,
                        "vertex2Index": flat_indices[tri_start + 2] + vertex_offset,
                    }
                )

            vertex_offset += len(positions)
            primitives_converted += 1

    if primitives_converted == 0:
        raise GltfConversionError(f"{path.name}: no convertible TRIANGLES primitives found")

    logger.info(
        "%s: converted %d primitive(s) (%d skipped) -> %d vertices, %d triangles",
        path.name, primitives_converted, primitives_skipped, len(all_vertices), len(all_triangles),
    )

    return {
        "vertices": all_vertices,
        "submeshes": [{"$type": "triangles", "triangles": all_triangles}],
    }


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
