import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions

async def main():
    sessions = await discover_sessions(timeout=15.0)
    home = next((s for s in sessions if "home" in s.get("sessionName", "").lower()), sessions[0])
    client = ResoniteLinkClient(host="localhost", port=home["linkPort"])
    await client.connect()

    for type_name in [
        "Submesh", "TrianglesSubmesh", "PointsSubmesh",
        "UV_Coordinate", "Vertex",
    ]:
        try:
            r = await client._send({"$type": "getSyncObjectDefinition", "key": type_name})
            print(f"getSyncObjectDefinition(key={type_name!r}) -> {json.dumps(r)[:2000]}")
        except Exception as exc:
            print(f"getSyncObjectDefinition(key={type_name!r}) FAILED -> {exc}")

    await client.disconnect()

asyncio.run(main())
