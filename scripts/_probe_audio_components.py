import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions

async def main():
    sessions = await discover_sessions(timeout=15.0)
    port = sessions[0]["linkPort"]
    client = ResoniteLinkClient(host="localhost", port=port)
    await client.connect()

    for ctype in [
        "[FrooxEngine]FrooxEngine.AudioClipPlayer",
        "[FrooxEngine]FrooxEngine.AudioOutput",
        "[FrooxEngine]FrooxEngine.StaticAudioClip",
    ]:
        try:
            r = await client.get_component_definition(ctype)
            members = list(r.get("definition", {}).get("members", {}).keys())
            print(f"{ctype}: {json.dumps(members)}")
        except Exception as exc:
            print(f"{ctype}: FAILED -> {exc}")

    await client.disconnect()

asyncio.run(main())
