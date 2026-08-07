import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions


async def main():
    sessions = await discover_sessions(timeout=15.0)
    home = next((s for s in sessions if "home" in s.get("sessionName", "").lower()), sessions[0])
    client = ResoniteLinkClient(host="localhost", port=home["linkPort"])
    await client.connect()

    print("--- Reso_4 (should be the rigged character slot) ---")
    try:
        data = await client.get_slot("Reso_4", include_component_data=True, depth=0)
        print(json.dumps(data, indent=2)[:3000])
    except Exception as exc:
        print(f"FAILED: {exc}")

    print("\n--- Root children (list everything at top level) ---")
    try:
        children = await client.get_children("Root")
        for c in children:
            name_field = c.get("name", {})
            name = name_field.get("value", "") if isinstance(name_field, dict) else str(name_field)
            print(f"  {c.get('id')}: {name}")
    except Exception as exc:
        print(f"FAILED: {exc}")

    await client.disconnect()


asyncio.run(main())
