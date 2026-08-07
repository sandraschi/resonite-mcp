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

    for candidate in [
        "[FrooxEngine]FrooxEngine.SkinnedMeshRenderer",
        "[FrooxEngine]FrooxEngine.Bone",
        "[FrooxEngine]FrooxEngine.Armature",
    ]:
        try:
            r = await client.get_component_definition(candidate)
            members = list(r.get("definition", {}).get("members", {}).keys())
            print(f"{candidate}: EXISTS, members={members}")
        except Exception as exc:
            print(f"{candidate}: FAILED -> {exc}")

    await client.disconnect()


asyncio.run(main())
