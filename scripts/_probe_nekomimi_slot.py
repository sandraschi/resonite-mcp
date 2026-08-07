"""Diagnostic: inspect the Nekomimi-chan static-mesh slot/components to find
out why it's not visible (spawn_mesh() succeeded and returned real IDs, so
something else is wrong — material, position, or scale)."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions

SLOT_ID = "Reso_A1A"  # from the successful spawn result


async def main():
    sessions = await discover_sessions(timeout=15.0)
    port = sessions[0]["linkPort"]
    client = ResoniteLinkClient(host="localhost", port=port)
    await client.connect()

    slot = await client.get_slot(SLOT_ID, include_component_data=True, depth=0)
    print("SLOT DATA:")
    print(json.dumps(slot, indent=2)[:4000])

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
