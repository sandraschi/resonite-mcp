import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions

async def main():
    sessions = await discover_sessions(timeout=15.0)
    port = sessions[0]["linkPort"]
    client = ResoniteLinkClient(host="localhost", port=port)
    await client.connect()
    r = await client.get_component_definition("[FrooxEngine]FrooxEngine.AudioClipPlayer")
    print(json.dumps(r["definition"]["members"]["playback"], indent=2))
    print("---CLIP---")
    print(json.dumps(r["definition"]["members"]["Clip"], indent=2))
    await client.disconnect()

asyncio.run(main())
