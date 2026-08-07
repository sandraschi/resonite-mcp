"""One-off: isolate the correct UV_Coordinate wire shape via a tiny 3-vertex
triangle with uvs, trying candidate shapes against the real server until one
works. Throwaway diagnostic script, not part of the package."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions

CANDIDATES = [
    ("type=UV_Coordinate", lambda u, v: {"$type": "UV_Coordinate", "x": u, "y": v}),
    ("type=float2", lambda u, v: {"$type": "float2", "value": {"x": u, "y": v}}),
    ("type=uv", lambda u, v: {"$type": "uv", "x": u, "y": v}),
    ("type=UVCoordinate", lambda u, v: {"$type": "UVCoordinate", "x": u, "y": v}),
]


async def main():
    sessions = await discover_sessions(timeout=8.0)
    if not sessions:
        print("Discovery empty, retrying with longer window...")
        sessions = await discover_sessions(timeout=15.0)
    if not sessions:
        print("Still no sessions discovered; aborting.")
        return
    port = sessions[0]["linkPort"]
    for label, make in CANDIDATES:
        client = ResoniteLinkClient(host="localhost", port=port)
        await client.connect()
        verts = [
            {"position": {"x": 0, "y": 0, "z": 0}, "uvs": [make(0.0, 0.0)]},
            {"position": {"x": 1, "y": 0, "z": 0}, "uvs": [make(1.0, 0.0)]},
            {"position": {"x": 0, "y": 1, "z": 0}, "uvs": [make(0.0, 1.0)]},
        ]
        subs = [{"$type": "triangles", "triangles": [{"vertex0Index": 0, "vertex1Index": 1, "vertex2Index": 2}]}]
        try:
            url = await client.import_mesh_json(verts, subs)
            print(f"{label}: SUCCESS -> {url}")
            await client.disconnect()
            return
        except Exception as exc:
            print(f"{label}: FAILED -> {exc}")
        await client.disconnect()
    print("All candidates failed.")


if __name__ == "__main__":
    asyncio.run(main())
