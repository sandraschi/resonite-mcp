"""Live test: the new audio pipe (import_audio_clip_file + spawn_audio)."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import ResoniteLinkClient, discover_sessions


async def main():
    sessions = await discover_sessions(timeout=15.0)
    port = sessions[0]["linkPort"]
    client = ResoniteLinkClient(host="localhost", port=port)
    await client.connect()

    try:
        result = await client.spawn_audio(
            r"C:\temp\test_beep_440hz.wav",
            position={"x": 0, "y": 1.5, "z": 8},
            name="phase1-audio-pipe-test",
            loop=True,
            volume=1.0,
        )
        print(f"spawn_audio SUCCESS: {json.dumps(result, indent=2)}")

        # Read back the AudioClipPlayer's live "playback" member shape —
        # don't guess how to trigger play, look at what Resonite actually
        # returns.
        player_data = await client.get_component(result["player_id"])
        print("\nAudioClipPlayer live component data:")
        print(json.dumps(player_data, indent=2)[:3000])

    except Exception as exc:
        print(f"FAILED: {exc}")

    await client.disconnect()


asyncio.run(main())
