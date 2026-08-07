import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions


async def main():
    sessions = await discover_sessions(timeout=15.0)
    home = next((s for s in sessions if "home" in s.get("sessionName", "").lower()), sessions[0])
    client = ResoniteLinkClient(host="localhost", port=home["linkPort"])
    await client.connect()

    data = await client.get_slot("Reso_4", include_component_data=True, depth=0)
    components = data["data"]["components"]
    print(f"Total components on Reso_4: {len(components)}")
    for c in components:
        ctype = c["componentType"]
        cid = c["id"]
        members = c.get("members", {})
        summary = {}
        for mname in ("Enabled", "Mesh", "Bones", "Materials", "BlendShapeWeights"):
            if mname in members:
                m = members[mname]
                if mname == "Bones":
                    summary[mname] = f"list of {len(m.get('elements', []))} refs"
                elif mname == "Materials":
                    summary[mname] = f"list of {len(m.get('elements', []))} refs"
                elif mname == "BlendShapeWeights":
                    summary[mname] = f"list of {len(m.get('elements', []))} floats"
                else:
                    summary[mname] = m.get("value") or m.get("targetId")
        print(f"  {cid} ({ctype}): {summary}")

    await client.disconnect()


asyncio.run(main())
