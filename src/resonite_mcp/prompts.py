"""Resonite MCP Prompt Templates — FastMCP 3.2+ prompts.

Registered via import in server.py. Each prompt triggers a predefined
conversation template for common Resonite workflows.
"""

from ..server import server


@server.prompt()
def resonite_session_setup():
    """Walk through setting up a Resonite session with OSC and avatar control.

    Guides the user through starting Resonite, enabling OSC, and
    connecting the MCP server for avatar and world management.
    """
    return (
        "I'll help you set up a Resonite session for MCP control.\n\n"
        "1. Start Resonite (Steam: steam://rungameid/2519830)\n"
        "2. In Resonite, enable OSC Input: `Resonite → Settings → OSC → Enable Input`\n"
        "3. Confirm OSC port is 9000 (default)\n"
        "4. Run `resonite_session_start()` to initialize the MCP connection\n"
        "5. The MCP health endpoints will confirm `resonite_running: true`\n\n"
        "Need help with any step?"
    )


@server.prompt()
def avatar_animation_setup():
    """Set up avatar parameter animations via OSC.

    Walks through creating a basic avatar animation using OSC
    parameter control with the available tools.
    """
    return (
        "To animate a Resonite avatar via OSC:\n\n"
        "1. Load your avatar via `resonite_avatar_load(slot=0)`\n"
        "2. Discover available parameters in your avatar\n"
        "3. Use `resonite_parameter_set(name='Happy', value=0.8)` for expressions\n"
        "4. For animations, use `resonite_protoflux_execute(script_name='wave')`\n"
        "5. For sequenced animation, use `osc_batch_send()` with inter-message delay\n\n"
        "Pro tip: many avatars expose parameters like `Happy`, `Surprise`, `Angry`, `Blink_L`, etc."
    )


@server.prompt()
def world_exploration():
    """Guide for loading and exploring worlds in Resonite.

    Helps the user load a world, inspect its slot hierarchy,
    and navigate the environment.
    """
    return (
        "Exploring a Resonite world:\n\n"
        "1. Discover public sessions via `resonite_rest_get_sessions()`\n"
        "2. Load a world: `resonite_world_load(world_path='resonite://TutorialWorld')`\n"
        "3. Inspect the world slot hierarchy via ResoniteLink\n"
        "4. Use arcade-style controls for movement (`/api/control/move`)\n"
        "5. Import assets via WorldLabs integration\n\n"
        "The `/api/status` endpoint confirms Resonite is running."
    )


@server.prompt()
def inventory_management():
    """Guide for managing Resonite inventory assets.

    Walks through listing, searching, spawning, and sharing
    inventory items.
    """
    return (
        "Resonite inventory management:\n\n"
        "1. List items: `resonite_inventory_list()`\n"
        "2. Search: `resonite_inventory_search(query='avatar')`\n"
        "3. Spawn an item into the world: `resonite_inventory_spawn(item_id='...')`\n"
        "4. Share with another user: `resonite_inventory_share(item_id='...', user_id='...')`\n"
        "5. Delete: `resonite_inventory_delete(item_id='...', confirm=True)`\n\n"
        "Upload local files via `resonite_inventory_upload(file_path='...')`"
    )


@server.prompt()
def cross_mcp_integration():
    """Guide for using cross-MCP integrations with WorldLabs, Blender, and Unity.

    Shows how to import assets from other MCP servers in the fleet
    into Resonite.
    """
    return (
        "Cross-MCP asset import:\n\n"
        "1. WorldLabs splat → Resonite: `resonite_import_worldlabs_url(splat_url='...')`\n"
        "2. Blender 3D model → Resonite: via blender-mcp at port 10848\n"
        "3. Unity avatar → Resonite: via unity3d-mcp at port 10710\n\n"
        "All imports use ResoniteLink WebSocket for fastest throughput,\n"
        "with OSC fallback if ResoniteLink is unavailable."
    )
