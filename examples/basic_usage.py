#!/usr/bin/env python3
"""Basic usage examples for Resonite MCP server.

This script demonstrates common usage patterns for controlling Resonite
through the MCP server API.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for direct execution
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from resonite_mcp.server import (
    resonite_avatar_load,
    resonite_parameter_set,
    resonite_protoflux_execute,
    resonite_session_end,
    resonite_session_start,
    send_osc,
    start_osc_server,
    stop_osc_server,
)


async def basic_session_workflow():
    """Demonstrate a basic Resonite session workflow."""
    print("🚀 Starting Resonite session workflow...")

    try:
        # 1. Start a new session
        print("\\n1. Starting session...")
        session_result = await resonite_session_start(
            session_name="DemoSession",
            world_path="resonite://TutorialWorld"
        )
        print(f"✅ Session started: {session_result['session_info']['session_id']}")

        # 2. Load an avatar
        print("\\n2. Loading avatar...")
        avatar_result = await resonite_avatar_load(
            avatar_path="resonite://DefaultAvatar",
            slot=0,
            parameters={"Happy": 0.7, "Relaxed": 0.8}
        )
        print(f"✅ Avatar loaded: {avatar_result['avatar_path']}")

        # 3. Set some parameters
        print("\\n3. Setting avatar parameters...")
        await resonite_parameter_set("Excited", 0.6)
        await resonite_parameter_set("Confident", 0.9)
        print("✅ Parameters set")

        # 4. Execute a ProtoFlux script
        print("\\n4. Executing ProtoFlux script...")
        protoflux_result = await resonite_protoflux_execute(
            "WelcomeAnimation",
            {"duration": 3.0, "intensity": 0.8}
        )
        print(f"✅ Script executed: {protoflux_result['script_name']}")

        # 5. Send custom OSC messages
        print("\\n5. Sending custom OSC messages...")
        osc_result = await send_osc(
            "127.0.0.1", 9000, "/custom/gesture", ["wave", 1.0]
        )
        print(f"✅ OSC message sent: {osc_result['address']}")

        # Wait a bit for things to settle
        await asyncio.sleep(2)

        # 6. End session
        print("\\n6. Ending session...")
        await resonite_session_end()
        print("✅ Session ended cleanly")

    except Exception as e:
        print(f"❌ Error in workflow: {e}")
        import traceback
        traceback.print_exc()


async def osc_communication_demo():
    """Demonstrate OSC server setup and communication."""
    print("\\n🎛️  OSC Communication Demo...")

    try:
        # Start OSC server to receive messages
        print("Starting OSC server on port 9001...")
        server_result = await start_osc_server(9001)
        print(f"✅ OSC server started: {server_result['port']}")

        # Send some test messages
        print("Sending test messages...")
        for i in range(3):
            await send_osc("127.0.0.1", 9001, f"/test/message/{i}", [i, f"value_{i}"])
            await asyncio.sleep(0.5)

        print("✅ Test messages sent")

        # Get received messages
        messages_result = await get_received_messages(9001, limit=5)
        print(f"📨 Received {messages_result['count']} messages")

        # Stop OSC server
        print("Stopping OSC server...")
        await stop_osc_server(9001)
        print("✅ OSC server stopped")

    except Exception as e:
        print(f"❌ OSC demo failed: {e}")


async def advanced_workflow():
    """Demonstrate an advanced workflow with multiple avatars and worlds."""
    print("\\n🔥 Advanced Workflow Demo...")

    try:
        # Start session with specific world
        session_result = await resonite_session_start(
            session_name="AdvancedDemo",
            world_path="resonite://SocialHub"
        )
        print(f"✅ Advanced session started in: {session_result['session_info'].get('initial_world', {}).get('path', 'default')}")

        # Load multiple avatars
        avatars = [
            ("resonite://RobotAvatar", 0, {"Techy": 0.9}),
            ("resonite://AnimalAvatar", 1, {"Playful": 0.8}),
        ]

        for avatar_path, slot, params in avatars:
            await resonite_avatar_load(avatar_path, slot, params)
            print(f"✅ Loaded avatar in slot {slot}: {Path(avatar_path).name}")

        # Execute complex ProtoFlux sequence
        scripts = [
            ("EnvironmentSetup", {"lighting": "warm", "particles": True}),
            ("SoundscapeGenerator", {"genre": "ambient", "intensity": 0.7}),
            ("InteractionTriggers", {"auto_greeting": True}),
        ]

        for script_name, params in scripts:
            await resonite_protoflux_execute(script_name, params)
            print(f"✅ Executed script: {script_name}")

        # Demonstrate parameter animation
        print("\\nAnimating parameters...")
        for value in [0.0, 0.3, 0.6, 0.9, 0.6, 0.3, 0.0]:
            await resonite_parameter_set("Energy", value)
            await asyncio.sleep(0.2)

        print("✅ Animation complete")

        # Clean up
        await resonite_session_end()
        print("✅ Advanced workflow completed")

    except Exception as e:
        print(f"❌ Advanced workflow failed: {e}")


async def main():
    """Run all demo workflows."""
    print("🎭 Resonite MCP Server - Usage Examples")
    print("=" * 50)

    # Check if we can import the server
    try:
        import resonite_mcp
        print(f"✅ Server version: {resonite_mcp.__version__}")
        print("✅ Server ready for demos")
    except ImportError as e:
        print(f"❌ Cannot import server: {e}")
        return

    # Run demos
    await basic_session_workflow()
    await osc_communication_demo()
    await advanced_workflow()

    print("\\n🎉 All demos completed!")
    print("\\n💡 Tips:")
    print("   - Make sure Resonite is running with OSC enabled")
    print("   - Check Resonite's OSC settings (default port 9000)")
    print("   - Use the HTTP API at http://127.0.0.1:8000/docs for web interface")
    print("   - Run with --log-level DEBUG for detailed logging")


if __name__ == "__main__":
    asyncio.run(main())








