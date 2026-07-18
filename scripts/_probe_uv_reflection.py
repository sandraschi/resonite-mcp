"""One-off: query ResoniteLink's reflection API for the actual UV_Coordinate
type discriminator instead of guessing blind."""
from __future__ import annotations
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions

async def main():
    sessions = await discover_sessions(timeout=15.0)
    port = sessions[0]["linkPort"]
    client = ResoniteLinkClient(host="localhost", port=port)
    await client.connect()

    for candidate in ["UV_Coordinate", "UVCoordinate", "float2"]:
        try:
            r = await client.get_type_definition(candidate)
            print(f"get_type_definition({candidate!r}) -> {json.dumps(r)[:2000]}")
        except Exception as exc:
            print(f"get_type_definition({candidate!r}) FAILED -> {exc}")

    # Also try asking the mesh-JSON accessor's own type via getComponentDefinition
    # on a StaticMesh, which likely has no UV field directly, so instead try
    # getSyncObjectDefinition (raw) if the wrapper doesn't cover it.
    try:
        raw = await client._send({"$type": "getSyncObjectDefinition", "type": "UV_Coordinate"})
        print(f"getSyncObjectDefinition(UV_Coordinate) -> {json.dumps(raw)[:2000]}")
    except Exception as exc:
        print(f"getSyncObjectDefinition FAILED -> {exc}")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
