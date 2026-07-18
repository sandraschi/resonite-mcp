import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions

async def main():
    sessions = await discover_sessions(timeout=15.0)
    port = sessions[0]["linkPort"]
    client = ResoniteLinkClient(host="localhost", port=port)
    await client.connect()
    try:
        r = await client.get_type_definition("[FrooxEngine]FrooxEngine.SyncPlayback")
        print("getTypeDefinition:", json.dumps(r, indent=2)[:2500])
    except Exception as exc:
        print("getTypeDefinition FAILED:", exc)
    try:
        r2 = await client._send({"$type": "getSyncObjectDefinition", "type": "[FrooxEngine]FrooxEngine.SyncPlayback"})
        print("getSyncObjectDefinition:", json.dumps(r2, indent=2)[:2500])
    except Exception as exc:
        print("getSyncObjectDefinition FAILED:", exc)
    await client.disconnect()

asyncio.run(main())
