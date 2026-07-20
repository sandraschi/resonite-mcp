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
    for name in ("BoundsComputeMethod", "ProxyBoundsSource", "ExplicitLocalBounds"):
        print(f"--- {name} ---")
        print(json.dumps(members[name], indent=2)[:1500])

    # Read back the actual live values on the tiny quad test's renderer
    print("\n--- Live values on Reso_E90 (tiny quad renderer) ---")
    data = await client.get_component("Reso_E90")
    m = data.get("data", {}).get("members", data.get("members", {}))
    for name in ("BoundsComputeMethod", "ExplicitLocalBounds", "ProxyBoundsSource"):
        print(f"{name}: {json.dumps(m.get(name))}")

    await client.disconnect()

asyncio.run(main())
