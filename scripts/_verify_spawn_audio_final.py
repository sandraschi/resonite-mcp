import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions

async def main():
    sessions = await discover_sessions(timeout=15.0)
    port = sessions[0]["linkPort"]
    client = ResoniteLinkClient(host="localhost", port=port)
    await client.connect()
    result = await client.spawn_audio(
        r"C:\temp\test_beep_440hz.wav",
        position={"x": 2, "y": 1.5, "z": 8}, name="phase1-audio-pipe-final-test",
        loop=False, volume=0.8,
    )
    print(f"Final consolidated spawn_audio (with autoplay) SUCCESS: {json.dumps(result)}")
    await client.disconnect()

asyncio.run(main())
