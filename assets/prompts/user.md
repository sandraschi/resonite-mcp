# Resonite MCP - User Guide and Tutorials

Version 1.2.0. This guide is the companion to system.md. It walks through installing and
configuring the server, then gives concrete step-by-step tutorials for the workflows people
actually run: session control, avatar control, inventory, OSC, the cloud REST API,
ResoniteLink world editing, ProtoFlux, vBots, and the cross-fleet asset pipeline. Each
tutorial names the tools to call and the arguments to pass, with realistic examples.

## 1. Introduction

Resonite MCP turns natural language into actions inside Resonite. You ask an assistant to
"load my home world and put on the fox avatar", and the server translates that into the
right OSC messages and REST calls. Under the hood it talks to Resonite three ways: OSC for
lightweight control, ResoniteLink for structured world-graph editing, and the Resonite Cloud
REST API for account-level operations. The same surface is exposed both as MCP tools (for
AI clients) and as HTTP routes (for the bundled web dashboard).

This guide assumes you have a Resonite account, have Resonite installed, and have Python
3.12+ with uv. If you only want the AI assistant without the dashboard, you can run the
server in stdio mode and skip the frontend entirely.

## 2. Installation and First Run

### 2.1 Clone and install

Clone the repository and install dependencies with uv:

```powershell
git clone https://github.com/sandraschi/resonite-mcp
cd resonite-mcp
uv sync
```

uv creates a virtual environment and installs all Python dependencies, including FastMCP
3.4.x, the RAG indexer, and the OSC and HTTP libraries.

### 2.2 Launch Resonite and enable ResoniteLink

1. Start Resonite from Steam and log in.
2. Open the in-session settings: Dashboard -> Session -> Settings.
3. Enable ResoniteLink. This opens a WebSocket bridge the server connects to on port 4242.
4. Confirm your OSC send port is 9000 (the default the server uses for outbound control) and
   that UDP traffic is not blocked by your firewall.

### 2.3 Start the dashboard (full stack)

```powershell
just bootstrap
just serve
```

The web dashboard is then available at http://localhost:10978 and the backend/MCP endpoint
at http://localhost:10979.

### 2.4 Run headless or as an MCP server

For AI-only use you can run just the backend:

```powershell
uv run python -m resonite_mcp --port 10979
```

For a stdio MCP server (Claude Desktop / Cursor):

```powershell
uv run python -m resonite_mcp --stdio
```

Register it in your MCP host config:

```json
"mcpServers": {
  "resonite-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/resonite-mcp", "run", "resonite-mcp"]
  }
}
```

Or install the packaged .mcpb bundle and register it from there.

### 2.5 Verify the server is up

Call health_check(). It reports the version, agent lab phase, whether plugins are loaded,
the OSC and ResoniteLink and RAG status, and whether Resonite is installed and running. A
healthy response means every transport is ready.

## 3. Configuration Reference

Most settings are environment variables (see system.md section 4). The three you are most
likely to change:

- RESONITE_OSC_PORT: the port the server sends OSC to (default 9000). Change it if your
  Resonite OSC input is on a different port.
- RESONITELINK_PORT: the ResoniteLink WebSocket port (default 4242).
- RESONITE_TOKEN and RESONITE_USER_ID: set these if you want the cloud REST and cloud
  variable tools to work across restarts without re-logging in. Otherwise log in once per
  process with resonite_rest_login.

Copy any overrides into an .env file or your environment before starting the server.

## 4. Tutorial 1 - Start a Session and Load a World

Goal: get Resonite into a known state in a world you choose.

1. Call resonite_session_start() to begin a session. Pass an optional world_path if you want
   a specific world now.
2. Check resonite_session_status() to confirm the session name and connected users.
3. If you did not pass a world at start, call resonite_world_load(world_path) with a path
   such as resonite:///0000-0000-0000-0000 or inventory://MyWorld. The path must start with
   resonite://, file://, or inventory://.
4. Verify with resonite_session_status() again.

If world_load fails, it is almost always because the path prefix is not allow-listed or
Resonite is not running. Confirm Resonite is running (health_check) and that your path uses
an allowed prefix.

## 5. Tutorial 2 - Change Your Avatar

Goal: put on an avatar and tune a parameter.

1. Call resonite_avatar_load(avatar_id) with the id of the avatar you want. Use slot=0 by
   default, or pass a different slot to target another body.
2. Set a parameter with resonite_parameter_set(parameter_name, value). For example, to
   adjust tracking smoothing you set the appropriate parameter name to a numeric value.
   Use the avatar_slot argument only if your avatar is not in slot 0.
3. If the avatar has custom parameters, enumerate them via the REST user records or the
   inventory, then set the ones you care about.

## 6. Tutorial 3 - Spawn an Inventory Item Into the World

Goal: place an asset from your inventory at a position.

1. List what you have: resonite_inventory_list(item_type="Prop", search_query="table") to
   find the item id.
2. Spawn it: resonite_inventory_spawn(item_id, position=[x,y,z], scale=1). Position and
   scale are optional; omit them to spawn at the default location.
3. Confirm placement with a ResoniteLink get_slot or get_children call on the root to see
   the new object, or visually in Resonite.
4. To clean up, delete it: resonite_inventory_delete(item_id, confirm_deletion=true). The
   confirmation flag is mandatory by design.

## 7. Tutorial 4 - Send and Receive OSC

Goal: verify OSC works and observe telemetry.

1. Run test_osc_echo(port=9000) to verify a round-trip through the default OSC port.
2. Start a receiver with start_osc_server(9001) if you want to observe messages Resonite
   sends to the server.
3. Inspect traffic with get_received_messages(9001, limit=50) or get_latest_message(9001).
4. When done, clear the buffer with clear_osc_message_buffer(9001) or stop with
   stop_osc_server(9001).
5. For raw control you can bypass the wrappers with send_osc(host, port, address, values),
   but prefer the typed tools (resonite_avatar_load, resonite_parameter_set, and so on)
   because they validate addresses and arguments for you.

## 8. Tutorial 5 - The Resonite Cloud REST API

Goal: browse public sessions and look up a user without a running client.

1. Get a token: resonite_rest_login(username, password, remember_me=true). With
   remember_me the token lasts 30 days; without it, 24 hours. The token lives in a process
   store; to persist it across restarts set RESONITE_TOKEN and RESONITE_USER_ID.
2. Browse public sessions: resonite_rest_get_sessions(min_active_users=1) to find active
   rooms, optionally filtered by name or host.
3. Look up a user: resonite_rest_get_user("username") or by id.
4. Send a friend a message: resonite_rest_send_message(target_user_id, "hello from my AI
   assistant"). This is also how you deliver a GLB or SPZ URL into a session.

## 9. Tutorial 6 - Cloud Variables

Goal: read and write a persistent key-value store on the Resonite cloud.

1. Ensure you are authenticated (login or env token).
2. Write a value: resonite_cloud_var_set("Cloud/MyVar", "hello"). The PUT creates the
   variable if it does not exist.
3. Read it back: resonite_cloud_var_get("Cloud/MyVar").
4. List variables under a path: resonite_cloud_var_list(path="Cloud").
5. Delete it: resonite_cloud_var_delete("Cloud/MyVar").

## 10. Tutorial 7 - Edit the World Graph With ResoniteLink

Goal: inspect and modify the live world object graph.

1. Discover the bridge: resonite_link_discover() over UDP 12512, then connect with
   resonite_link_connect(host="localhost", port=4242).
2. Read the root: resonite_link_get_slot(slot_id="Root", include_component_data=true).
3. Walk the tree: resonite_link_get_children(slot_id) to list immediate children, and
   resonite_link_get_node(ref_id) to inspect any single slot or component.
4. Add a slot: resonite_link_add_slot(name="myBox", parent_id="Root", pos_x=0, pos_y=1,
   pos_z=0).
5. Add a component to it: resonite_link_add_component(slot_id, component_type="Transform").
6. Write a field: resonite_link_write_field(component_id, member="scale", value=2.0). Use
   resonite_link_set(component_id, field, value) for the shorthand form.
7. For multiple coordinated edits, use resonite_link_batch(operations) so the whole set
   applies atomically as a dataModelOperationBatch.

## 11. Tutorial 8 - Procedural Mesh Spawning

Goal: place a simple mesh into the world entirely from code.

1. Build a vertex array and submesh list for a quad or box.
2. Call resonite_link_spawn_mesh(vertices, submeshes, name="quad", pos_x=0, pos_y=0, pos_z=0,
   color_r=0.8, color_g=0.2, color_b=0.1, color_a=1.0). The server runs the full render
   chain: importMeshJSON, addSlot, StaticMesh, MeshRenderer, PBS_Metallic.
3. Verify the resulting slot with resonite_link_get_node(ref_id).
4. If you only need the asset URL (to reuse elsewhere), use
   resonite_link_import_mesh_json(vertices, submeshes) instead, which returns the asset URL
   without spawning a slot.

## 11b. Tutorial 8b - Animate, Fixtures, and the Model/Texture Depot (backport from overte-mcp)

Goal: loop-animate a slot, drop in a preset test fixture, and manage reusable model/texture
assets - all added 2026-09-02 as a backport from overte-mcp's equivalent tools.

1. Animate a slot in place: resonite_link_animate(slot_id="myBox", mode="bounce",
   amplitude=0.3, damping=0.6, duration_s=6). mode is "spin", "bob", or "bounce" (a real
   drop-and-rebound simulation, not a sine wave). Blocks for duration_s.
2. Spawn a preset test fixture: resonite_link_spawn_fixture(fixture="ball", pos_x=0, pos_y=1,
   pos_z=2). fixture is "box", "cup", "ball", "table", or "chair". Unlike overte-mcp, there is
   no avatar-relative default placement - ResoniteLink cannot read your position, so
   pos_x/y/z are required.
3. Add a model or texture to the depot: resonite_link_depot_add(kind="model",
   file_path="C:/path/to/thing.glb", description="a chair", category="furniture"). kind is
   "model" (.glb/.vrm/.gltf) or "texture" (.png/.jpg/.jpeg).
4. List what's in the depot: resonite_link_depot_list(kind="model").
5. Spawn a depot model into the world: resonite_link_depot_spawn(kind="model", name=
   "thing.glb", pos_x=0, pos_y=0, pos_z=0). For kind="texture" this instead returns an
   asset_url to wire into a material yourself (no mesh to attach it to automatically).
6. Snapshot the depot: resonite_link_depot_backup(), then resonite_link_depot_list_backups()
   to see it, and resonite_link_depot_restore_backup(name=...) to roll back.

## 12. Tutorial 9 - ProtoFlux Scripts

Goal: generate, run, and refine ProtoFlux logic.

1. Generate from a template: protoflux_generate_template("world_interaction",
   customization="door opens when clicked"). The supported templates are
   avatar_animation, world_interaction, ui_control, data_processing, network_sync, and
   physics_simulation.
2. Execute it: resonite_protoflux_execute(script_name).
3. Debug it: protoflux_debug_session(script_name, debug_mode="step_through").
4. Optimize it: protoflux_optimize_script(script_name, optimization_level="moderate").
5. Produce readable docs for it: protoflux_document_script(script_name).
6. Analyze an existing graph: protoflux_analyze_script(script_name).

## 13. Tutorial 10 - Control a vBot

Goal: spawn a robot and drive it around the world.

1. Confirm available types: resonite_vbot_list_types(). Types include yahboom, mechazilla,
   bumi, godzilla, and custom.
2. Spawn one: resonite_vbot_spawn(robot_type="yahboom", robot_id="bot1", position_x=0,
   position_y=1, position_z=0, scale=1).
3. Move it: resonite_vbot_move(robot_id="bot1", linear=0.5, angular=0.0).
4. Aim its head: resonite_vbot_head(robot_id="bot1", yaw_deg=30, pitch_deg=-5).
5. Stop it: resonite_vbot_stop(robot_id="bot1").

## 14. Tutorial 11 - Voice Macro Control

Goal: turn a natural-language phrase into an OSC macro.

1. List available macros: resonite_voice(operation="list_macros"). Built-ins include wave,
   jump, sit, toggle_ui, and import_staging.
2. Parse a phrase: resonite_voice(operation="parse_command", phrase="wave at the audience").
   The server resolves it to the wave macro, optionally refining with a local LLM.
3. Send it: resonite_voice(operation="send_macro", macro="wave").
4. Check which execution mode applies: resonite_voice(operation="execution_mode").

## 15. Tutorial 12 - The Cross-Fleet Asset Pipeline

Goal: bring an Inkscape UI mockup, Blender model, and GIMP texture into Resonite as one
asset. This is the flagship "build-and-inhabit" workflow.

1. First check the execution mode: resonite_fleet(operation="execution_mode"). This reports
   hands_in (Resonite running), hands_off_launch (installed, not running), or
   hands_off_install (absent). It decides whether you can complete the whole chain now.
2. Pull the Inkscape UI: resonite_fleet(operation="pull_inkscape_ui", staging_dir=...).
3. Import the Blender asset: resonite_fleet(operation="import_blender_asset",
   object_name="chair", export_format="glb").
4. Apply a GIMP texture: resonite_fleet(operation="import_gimp_texture",
   texture_path=...).
5. Pull the avatar VRM: resonite_fleet(operation="pull_blender_vrm", export_format="vrm")
   or import a batch from staging: resonite_fleet(operation="import_vrm_batch",
   vrm_dir=...).
6. Optionally stage a Marble world: resonite_fleet(operation="run_marble_pipeline",
   marble_dir=...) or import WorldLabs splats:
   resonite_fleet(operation="import_worldlabs_batch", manifest=...).
7. Review the outcome: resonite_fleet(operation="inventory_status") to see what is staged.
8. For a single coordinated pass use resonite_fleet(operation="run_fleet_pipeline",
   ...) or the stricter run_strict_fleet_pipeline.

The per-step skip_* switches let you run only the stages you have tooling for.

## 16. Tutorial 13 - Import a WorldLabs Splat

Goal: place a gaussian-splat scan into the world.

1. Use resonite_import_worldlabs_url(splat_url, world_name, target_slot). It downloads the
   SPZ/GLB to a temp location, tries a ResoniteLink import, and always sends OSC
   /worldlabs/import on port 9000.
2. If the structured ResoniteLink import is unavailable (the protocol rejects the legacy
   payload), the server falls back to the OSC route. That fallback is a real behavior, not a
   silent failure.
3. Alternatively import several at once with
   resonite_import_worldlabs_batch(manifest, target_slot).

## 17. Tutorial 14 - Federate With Other MCP Servers

Goal: let Resonite MCP route through other fleet servers.

1. Set MCP_BRIDGE_URLS to a comma-separated list of other MCP server URLs before starting.
2. Restart the server. Each URL is added as a proxy provider.
3. Use the dashboard apps catalog to navigate to 12+ fleet services, or call bridged tools
   directly. This is what powers workflows that pull assets from blender-mcp or
   inkscape-mcp and land them in Resonite.

## 18. Tutorial 15 - The Agentic Planner

Goal: ask the server to accomplish a multi-step goal autonomously.

1. Call agentic_plan_execute(goal) with a concrete goal, for example "load my home world,
   put on the fox avatar, set walking locomotion, then list what is in my inventory".
2. The server plans (using ctx.sample) restricted to eight safe tools, then executes the
   plan step by step, reasoning between steps.
3. It returns the plan and the outcome of each step. Only the curated safe subset is used:
   session start, world load, avatar load, parameter set, inventory list, inventory spawn,
   session browse, and raw OSC send.
4. Run the server with --agentic to enable CodeMode BM25 skill discovery, which improves
   planning by retrieving relevant skill context.

## 19. REST API Reference

The FastAPI backend exposes these endpoint groups (all under the bind host/port). This is
the surface the web dashboard uses; the MCP tools are the programmatic equivalent.

- /health and /api/v1/health: liveness and phase.
- /docs and /redoc: OpenAPI documentation.
- /api/v1/tool: Agent Lab bridge for resonite_fleet, resonite_voice, and health_check.
- /api/logs*: activity log query, stats, export.
- /api/metrics and /metrics: Prometheus metrics (port 9079).
- /api/osc/*: send, start/stop server, received messages, buffer control.
- /api/resonite/*: session, avatar, protoflux, world, inventory, platform, sessions,
  contacts.
- /api/control/move and /api/control/view: avatar movement and view toggling.
- /api/world/map-data: spatial data for the 2D world map.
- /rl/*: ResoniteLink CRUD, discover, reflect, batch.
- /rl/world/*: world inspector, asset-file scan, VRM endpoints.
- /api/resonite/vbot/*: vBot types, receiver spec, test sequence.
- /api/v1/fleet/launch: launch a fleet app; paths must resolve under D:/Dev/repos.
- POST /api/resonite/worldlabs/listen: host the OSC import listener (binds 127.0.0.1:9001).
- GET /api/resonite/worldlabs/protoflux: serve a ProtoFlux import template.

## 20. Troubleshooting

- Resonite not responding to OSC: confirm the OSC port (9000) matches your Resonite OSC
  input, and that UDP is allowed. Run test_osc_echo(port=9000).
- world_load fails: the path must start with resonite://, file://, or inventory://. Also
  confirm Resonite is running via health_check.
- REST tools fail with auth errors: you are not logged in. Run resonite_rest_login or set
  RESONITE_TOKEN and RESONITE_USER_ID.
- ResoniteLink connect fails: enable ResoniteLink in-session settings and check the port
  (4242). Use resonite_link_discover() to confirm the bridge is advertising.
- Inventory returns MOCK data: RESONITE_INVENTORY_MODE is auto and live is unavailable, so
  the adapter fell back to a declared mock catalog. Switch to live or fix the Resonite
  connection.
- A "not_implemented" for a file import: that path is not supported by ResoniteLink 0.13.1.
  Use the OSC /worldlabs/import route or import_mesh_json / spawn_mesh for procedural
  meshes.
- Version strings disagree (0.8.0 vs 1.2.0): the FastMCP name/health and Prefab cards carry
  a stale 0.8.0. The package version 1.2.0 is authoritative.
- Prometheus metrics missing: ensure RESONITE_MCP_METRICS_ENABLED is not set to 0/false.

## 21. FAQ

- Do I need the web dashboard? No. Run python -m resonite_mcp --stdio for MCP-only use.
- Do I need a Resonite account? Yes for cloud REST, cloud variables, inventory, and friends.
  Local OSC/ResoniteLink work with a running client.
- Does it work without Resonite installed? Partially. health_check reports the execution
  mode; local world/avatar tools need a running client. Cloud REST and session browsing work
  without one.
- What Python do I need? 3.12+. FastMCP 3.4.x is installed by uv.
- How do I make cloud tools persist across restarts? Set RESONITE_TOKEN and
  RESONITE_USER_ID.
- Can it import arbitrary 3D files? Not through ResoniteLink 0.13.1 directly. Use
  import_mesh_json for procedural meshes, the fleet pipeline for staged Blender/VRM assets,
  and the OSC WorldLabs route for splats.
- Is inventory deletion destructive? It is gated behind confirm_deletion=true on purpose.
- How do I expose it to the network? Run with --host 0.0.0.0 --port 10979 and ensure
  RESONITE_TAURI or the dashboard CORS covers your clients.

## 22. End-to-End Worked Example

A single narrative that exercises most of the surface in sequence, the way an agent would
handle a request like "set up a small showcase: load a splat, spawn a chair, and drive a
robot around it".

1. health_check() - confirm Resonite is running and all transports are ready.
2. resonite_session_start() - start a session.
3. resonite_world_load("inventory://Showcase") - enter the showcase world (valid prefix).
4. resonite_import_worldlabs_url(splat_url="https://example.com/scene.spz",
   world_name="Sculpture") - place the splat via OSC /worldlabs/import.
5. resonite_inventory_list(item_type="Prop", search_query="chair") - find a chair id.
6. resonite_inventory_spawn(item_id, position=[0,1,0], scale=1) - place it.
7. resonite_vbot_spawn(robot_type="yahboom", robot_id="guide", position_x=0,
   position_y=1, position_z=2) - add the robot.
8. resonite_vbot_move("guide", linear=0.3, angular=0.1) - start it moving.
9. resonite_parameter_set("LightBlend", 0.5) - adjust a world/avatar parameter.
10. resonite_link_get_children("Root") - verify the objects are present in the graph.
11. resonite_session_status() - final state check.

Each step is a real, validated operation; any validation failure stops the chain with a
clear error rather than a fabricated success.

## 23. OSC Monitoring and Analysis Recipes

Beyond one-off sends, the server can observe and analyze OSC traffic in real time.

- Monitor a port for a window: osc_monitor_start(port=9001, address_filter="/avatar",
  duration_seconds=30) to capture only avatar-related messages.
- Batch sends with spacing: osc_batch_send(port, messages, delay_ms=50) to fire a scripted
  sequence with controlled pacing.
- Record a session: osc_record_session(port, session_name="debug-run",
  duration_seconds=60) to log traffic for later inspection.
- Analyze traffic patterns: osc_analyze_traffic(port, analysis_duration=10) to summarize
  message rates, addresses, and payload sizes.

Combine these with get_osc_server_stats to see error counts, and clear_osc_message_buffer
to reset between experiments. These plugins live under plugins/osc_extensions.py and are
enabled by the plugin manager.

## 24. Security and Permissions Model

The server takes a defensive posture by default.

- World paths are allow-listed to resonite://, file://, and inventory://. Arbitrary paths
  are rejected.
- Inventory deletion is gated behind confirm_deletion=true.
- The fleet launch endpoint only resolves paths under D:/Dev/repos (otherwise 403).
- OSC addresses must start with / and ports must be within 1..65535.
- REST/cloud-variable/friends tools require an authenticated session (login or
  RESONITE_TOKEN + RESONITE_USER_ID). Without a token they fail with an auth error instead
  of degrading to an anonymous guess.
- CORS origins are restricted to the dashboard host and, with RESONITE_TAURI, Tauri
  origins. The server does not open itself to arbitrary origins.
- Execution-mode gating (hands_in / hands_off_launch / hands_off_install) lets the server
  tell an agent when a human step is required, so an autonomous run can stop and ask rather
  than silently pretending work happened.
- NOT-implemented and degraded paths are explicit: file/VRM/GLB/FBX import through
  ResoniteLink, URL/template spawning, and the demo-data and MOCK inventory fallbacks all
  declare themselves rather than masquerading as live results.

This honesty contract is deliberate. An agent should treat a not_implemented or MOCK
response as a real signal and route to the supported path, never assume a fake success.

## 25. Performance and Concurrency Notes

- OSC is UDP and fire-and-forget, so it is fast but not guaranteed delivery. For commands
  that must take effect reliably, prefer the typed tools that wait for a response on 9001
  (inventory spawn, session start) or verify with a follow-up status call.
- The OSC receive buffer is capped at 1000 messages per port. Long monitors should drain
  frequently with get_received_messages(max_age_seconds=...) or reset with
  clear_osc_message_buffer.
- ResoniteLink batch operations are atomic (dataModelOperationBatch). Prefer batching
  several related edits in one call over many individual writes when consistency matters.
- RAG queries and ask_resonite call a local LLM substrate; the first call may be slower
  while the substrate loads. Subsequent calls are faster.
- Local LLM probing (Ollama, LM Studio) uses short timeouts so a missing substrate does not
  block unrelated tool calls.
- Telemetry: with metrics enabled, Prometheus scrapes on port 9079. This is cheap and
  intended to stay on unless you need to reduce surface area.

## 26. Example Prompts for an AI Client

These are natural-language requests that map onto the tools above. Hand them to a client
wired to this server.

- "Load my home world and tell me what session it is." -> resonite_world_load +
  resonite_session_status.
- "Switch me to a taller avatar and smooth out my tracking." -> resonite_avatar_load +
  resonite_parameter_set.
- "Put a wooden table prop in front of me." -> resonite_inventory_list +
  resonite_inventory_spawn.
- "What rooms are open right now?" -> resonite_rest_get_sessions.
- "Save my current brightness to a cloud variable called Cloud/Brightness." ->
  resonite_cloud_var_set.
- "Spawn a small red cube above the root slot." -> resonite_link_add_slot +
  resonite_link_add_component + resonite_link_write_field, or resonite_link_spawn_mesh.
- "Make a physics interaction script that reacts to touch." -> protoflux_generate_template +
  resonite_protoflux_execute.
- "Bring the chair model I designed into the world." -> resonite_fleet
  (import_blender_asset + import_gimp_texture + import_vrm_batch).
- "Drop that splat of the park into the world." -> resonite_import_worldlabs_url.
- "Do everything from world load to robot control for a showcase." ->
  agentic_plan_execute.

## 27. When to Use Which Transport

A quick decision rule:

- MCP host (Claude Desktop, Cursor): use stdio. Register the repo or the .mcpb bundle.
- Agent lab / remote / multiple consumers: use http at 127.0.0.1:10979/mcp.
- Browser dashboard only: just serve (frontend 10978 + backend 10979).
- CI or scripted automation: headless backend, and use the HTTP endpoints or MCP tools
  directly.

When in doubt, stdio is the safest default for single AI clients, and http is the right
choice once you want the dashboard or more than one consumer.

## 28. HTTP API Worked Examples

The FastAPI backend exposes the same capabilities over HTTP. These are concrete exchanges.

Health check:

```
GET http://127.0.0.1:10979/api/v1/health
```

Response carries the version, agent lab phase, and transport status.

Launch Resonite:

```
POST http://127.0.0.1:10979/api/resonite/launch
```

Launches Resonite via steam://rungameid/2519830.

Read a world slot over ResoniteLink:

```
GET http://127.0.0.1:10979/rl/world/root
GET http://127.0.0.1:10979/rl/world/children/{slot_id}
GET http://127.0.0.1:10979/rl/world/node/{ref_id}
```

Reflection over component types:

```
GET http://127.0.0.1:10979/rl/reflect
GET http://127.0.0.1:10979/rl/reflect?component_type=Transform
```

Atomic batch:

```
POST http://127.0.0.1:10979/rl/batch
Content-Type: application/json

{ "operations": [ { "op": "AddSlot", "name": "lamp", "parent": "Root" } ] }
```

Send an OSC message:

```
POST http://127.0.0.1:10979/api/osc/send
Content-Type: application/json

{ "address": "/resonite/avatar/load", "values": ["avatarId123"] }
```

Browse public sessions:

```
GET http://127.0.0.1:10979/api/resonite/cloud-sessions?min_active_users=1
```

World map data for the 2D view:

```
GET http://127.0.0.1:10979/api/world/map-data
```

Fleet launch (path must resolve under D:/Dev/repos):

```
POST http://127.0.0.1:10979/api/v1/fleet/launch
```

The Prometheus metrics endpoint:

```
GET http://127.0.0.1:9079/metrics
```

The OpenAPI interactive docs live at /docs, which is the fastest way to explore every route
with a working request builder.

## 29. Best Practices

- Prefer the typed domain tools (resonite_avatar_load, resonite_world_load,
  resonite_inventory_spawn) over raw send_osc. They validate addresses, ports, and values and
  return structured confirmations. Reach for send_osc only for bespoke addresses the wrappers
  do not cover.
- Confirm the execution mode before starting a multi-step world workflow. If it is
  hands_off_install, ask the user to install or launch Resonite rather than pretending the
  world was touched.
- Treat MOCK and not_implemented responses as real signals. A declared mock inventory or a
  not_implemented file import is the server being honest; route around it with the supported
  path.
- Authenticate once early for cloud work: run resonite_rest_login at the start of a session,
  or set RESONITE_TOKEN + RESONITE_USER_ID, so cloud variables, friends, records, and
  messages do not fail later with auth errors.
- Use ResoniteLink batch for multi-edit operations to keep them atomic.
- Drain the OSC receive buffer during long monitoring runs to avoid hitting the 1000-message
  cap.
- Prefer agentic_plan_execute for goals that need several steps; it self-limits to the safe
  subset and reasons between steps. Reserve direct multi-tool sequences for when you need
  precise control over each call.
- Check health_check() first whenever behavior is unexpected; it reports which transport is
  down without guesswork.

## 30. Deeper: OSC and ResoniteLink Together

OSC and ResoniteLink are complementary, and knowing when to use each is the difference
between a fragile and a robust integration.

OSC is the right tool when you want a lightweight, immediate control signal and do not need
to inspect the result. Avatar parameter changes, session start, world load, vBot movement,
and fire-and-forget notifications all go over OSC. It is UDP, so it is fast, but there is no
guaranteed delivery and no structured response. If a command must definitely land, follow it
with a status check on the same channel (resonite_session_status, get_received_messages on
9001, or a ResoniteLink read).

ResoniteLink is the right tool when you need structure, precision, and inspectability. The
world object graph is a tree of slots and components, and ResoniteLink lets you read and
write it directly with ref ids, run atomic batches, reflect over component types, and import
procedural meshes. This is how you add a component to a slot, change a field value, or
verify that a spawned object actually exists in the graph. It is TCP/WebSocket, so delivery
and responses are reliable, and the data model is explicit.

A common combined pattern is: use OSC to perform an action that is not represented in the
graph (send an avatar parameter, launch a splat import), then use ResoniteLink to verify and
refine the graph (find the new slot, read its fields, adjust a value). This gives you the
speed of OSC and the confidence of ResoniteLink without over-relying on either.

The Cloud REST API is the third leg and lives outside the graph entirely. Use it for
account-level facts and actions that exist independent of any open session: browsing public
sessions, user lookup, sending a message to deliver an asset URL, managing cloud variables,
and friends. It is the correct choice whenever no client needs to be running.

## 31. Known Limitations and Working Around Them

- ResoniteLink 0.13.1 does not support generic file/VRM/GLB/FBX import. The server is honest
  about this: resonite_link_spawn with a URL/file template returns not_implemented, and the
  /rl/world/inject-file and /rl/world/import-vrm routes return 501. The supported routes are
  import_mesh_json / spawn_mesh for procedural meshes, the fleet pipeline for staged
  Blender/VRM assets, and the OSC /worldlabs/import route for splats.
- The avatar-info HTTP fallback returns demo data, and the gallery falls back to Unsplash
  images. These are declared placeholders, not live telemetry. If a dashboard number looks
  suspicious, check whether it came from a declared fallback.
- The FastMCP name, health, and Prefab cards carry a stale 0.8.0 version while the package is
  1.2.0. Trust the package/HTTP version and flag the discrepancy rather than relying on one
  string.
- Some integration helpers send a legacy ResoniteLink payload shape that the real protocol
  rejects (it requires $type). When that surfaces, the call falls back to the OSC route
  rather than reporting a fake success; that fallback is intended behavior.

## 32. More FAQ

- Can two agents control the same Resonite instance at once? The server keeps a single
  client and OSC server set per session. Coordinate access rather than assuming concurrent
  control is safe; use the session tools to establish a clean state first.
- Does the dashboard need the MCP server? No. The dashboard talks to the FastAPI backend
  over HTTP; the MCP tools are an equivalent surface for AI clients.
- Can I use it on a headless machine with no display? Yes for cloud REST, session browsing,
  and cloud variables. Local OSC/ResoniteLink world tools need a running Resonite client on
  the same machine (or reachable over the configured host/port).
- How do I reset a stuck state? Use resonite_session_end() to tear down cleanly (closes OSC
  servers, clears clients, disconnects ResoniteLink), then start a fresh session.
- Where do VRM avatars live? ~/.avatarmcp/models/, shared with avatar-mcp and vrchat-mcp. The
  fleet pipeline stages VRMs there before import.
- What if my RAG index is stale? The index is built from the repo markdown at startup. Re-run
  the server or trigger a reindex to pick up doc changes.
- Is it safe to give an agent delete access? Inventory deletion is gated behind
  confirm_deletion=true and the fleet launch endpoint is path-restricted to the repo tree.
  Grant broad autonomy only if you accept those limits.
