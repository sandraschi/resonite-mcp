import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions

async def main():
    sessions = await discover_sessions(timeout=15.0)
    home = next((s for s in sessions if "home" in s.get("sessionName", "").lower()), sessions[0])
    client = ResoniteLinkClient(host="localhost", port=home["linkPort"])
    await client.connect()
    r = await client.get_component_definition("[FrooxEngine]FrooxEngine.SkinnedMeshRenderer")
    members = r["definition"]["members"]
    print("ALL members:", list(members.keys()))
    await client.disconnect()

asyncio.run(main())
