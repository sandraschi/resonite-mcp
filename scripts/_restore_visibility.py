import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions, rl_ref, rl_list

CHARACTER_SLOT = "Reso_4"

async def main():
    sessions = await discover_sessions(timeout=15.0)
    home = next((s for s in sessions if "home" in s.get("sessionName", "").lower()), sessions[0])
    client = ResoniteLinkClient(host="localhost", port=home["linkPort"])
    await client.connect()

    # Disable the (likely broken-bind-pose) SkinnedMeshRenderer rather than
    # delete it -- keep the wiring around to debug later.
    try:
        await client.update_component("Reso_9", {"Enabled": False})
        print("Disabled SkinnedMeshRenderer (Reso_9)")
    except Exception as exc:
        print(f"Disable FAILED: {exc}")

    # Restore a plain MeshRenderer -- known-good, static, visible.
    try:
        renderer_id = await client.add_component(
            CHARACTER_SLOT, "[FrooxEngine]FrooxEngine.MeshRenderer",
            {"Mesh": rl_ref("Reso_5")},
        )
        await client.update_component(renderer_id, {"Materials": rl_list([rl_ref("Reso_7")])})
        print(f"Restored plain MeshRenderer: {renderer_id}")
    except Exception as exc:
        print(f"Restore FAILED: {exc}")

    await client.disconnect()

asyncio.run(main())
