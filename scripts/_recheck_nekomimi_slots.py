import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions

ORIGINAL_SLOT = "Reso_A1A"
ZFLIP_SLOT_HINT = None  # will search by name if needed


async def main():
    sessions = await discover_sessions(timeout=15.0)
    port = sessions[0]["linkPort"]
    client = ResoniteLinkClient(host="localhost", port=port)
    await client.connect()

    for label, slot_id in []:
        try:
            data = await client.get_slot(slot_id, include_component_data=True, depth=0)
            print(f"--- {label} ({slot_id}) ---")
            print(json.dumps(data, indent=2)[:3000])
        except Exception as exc:
            print(f"{label} ({slot_id}) FAILED: {exc}")

    # Find the z-flip test slot by listing Root's children and matching the name
    root_children = await client.get_children("Root")
    for child in root_children:
        name_field = child.get("name", {})
        name = name_field.get("value", "") if isinstance(name_field, dict) else str(name_field)
        if "zflip" in name.lower():
            print(f"\n--- found z-flip slot: {child.get('id')} ({name}) ---")
            data = await client.get_slot(child.get("id"), include_component_data=True, depth=0)
            print(json.dumps(data, indent=2)[:3000])

    await client.disconnect()


asyncio.run(main())
