import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions

OLD_STATIC_SLOT = "Reso_0"
RIGGED_SLOT = "Reso_4"


async def main():
    sessions = await discover_sessions(timeout=15.0)
    home = next((s for s in sessions if "home" in s.get("sessionName", "").lower()), sessions[0])
    client = ResoniteLinkClient(host="localhost", port=home["linkPort"])
    await client.connect()

    try:
        r = await client.remove_slot(OLD_STATIC_SLOT)
        print(f"Removed old static copy ({OLD_STATIC_SLOT}): {r}")
    except Exception as exc:
        print(f"Remove FAILED (maybe already gone?): {exc}")

    try:
        r = await client.update_slot(
            {
                "id": RIGGED_SLOT,
                "position": {"$type": "float3", "value": {"x": 0, "y": 0, "z": 2}},
            }
        )
        print(f"Moved rigged copy to the original spot: {r}")
    except Exception as exc:
        print(f"Move FAILED: {exc}")

    await client.disconnect()


asyncio.run(main())
