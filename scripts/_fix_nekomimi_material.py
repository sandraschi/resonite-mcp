"""Fix: add a solid-color material to Nekomimi-chan's MeshRenderer, which
was spawned with an empty Materials list (spawn_mesh() called without a
`color` arg skips material creation entirely)."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions, rl_list, rl_ref, rl_value

SLOT_ID = "Reso_A1A"
RENDERER_ID = "Reso_A1C"


async def main():
    sessions = await discover_sessions(timeout=15.0)
    port = sessions[0]["linkPort"]
    client = ResoniteLinkClient(host="localhost", port=port)
    await client.connect()

    material_id = await client.add_component(
        SLOT_ID,
        "[FrooxEngine]FrooxEngine.PBS_Metallic",
        {"AlbedoColor": rl_value("colorX", {"r": 0.95, "g": 0.85, "b": 0.9, "a": 1.0})},  # pale skin tone, placeholder
    )
    print(f"Added material component: {material_id}")

    result = await client.update_component(RENDERER_ID, {"Materials": rl_list([rl_ref(material_id)])})
    print(f"Updated renderer Materials: {result}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
