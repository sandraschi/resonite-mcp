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
    r = await client.get_component_definition("[FrooxEngine]FrooxEngine.PBS_Metallic")
    members = list(r.get("definition", {}).get("members", {}).keys())
    print("ALL MEMBER NAMES:")
    print(json.dumps(members, indent=2))
    await client.disconnect()


asyncio.run(main())
