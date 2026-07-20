import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from resonite_mcp.resonite_link import discover_sessions

async def main():
    sessions = await discover_sessions(timeout=15.0)
    print(f"Found {len(sessions)} session(s):")
    for s in sessions:
        print(json.dumps(s, indent=2))

asyncio.run(main())
