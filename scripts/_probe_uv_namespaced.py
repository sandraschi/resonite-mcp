import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions

CANDIDATES = [
    "[FrooxEngine]FrooxEngine.UV_Coordinate",
    "[Elements.Core]Elements.Core.float2",
    "[FrooxEngine]FrooxEngine.UVCoordinate",
    "[BaseX]BaseX.UV_Coordinate",
]


async def main():
    sessions = await discover_sessions(timeout=15.0)
    home = next((s for s in sessions if "home" in s.get("sessionName", "").lower()), sessions[0])
    client = ResoniteLinkClient(host="localhost", port=home["linkPort"])
    await client.connect()

    for candidate in CANDIDATES:
        try:
            r = await client.get_type_definition(candidate)
            print(f"get_type_definition({candidate!r}) -> {json.dumps(r)[:1500]}")
        except Exception as exc:
            print(f"get_type_definition({candidate!r}) FAILED -> {exc}")

    await client.disconnect()


asyncio.run(main())
