import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions, rl_value

PLAYER_ID = "Reso_A3B"

async def main():
    sessions = await discover_sessions(timeout=15.0)
    port = sessions[0]["linkPort"]
    client = ResoniteLinkClient(host="localhost", port=port)
    await client.connect()

    result = await client.update_component(
        PLAYER_ID,
        {"playback": rl_value("playback", {"play": True, "loop": True, "position": 0.0, "speed": 1.0})},
    )
    print(f"Play triggered: {result}")

    await client.disconnect()

asyncio.run(main())
