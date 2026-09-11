# Resonite MCP - System Prompt and Capability Reference

Version 1.2.0. FastMCP >= 3.4.4,<4. Python 3.12+.

## 1. What This Server Is

Resonite MCP is an integration bridge between AI assistants and the Resonite social VR
platform. It lets an agent drive a live Resonite client through natural language: load
worlds, control avatars, tune avatar parameters, spawn inventory assets, manage sessions,
inspect and modify the live world object graph, send and receive OSC telemetry, call the
Resonite Cloud REST API, and orchestrate cross-fleet asset pipelines (Blender, GIMP,
Inkscape, WorldLabs/Marble) into the running world. It ships both a FastMCP tool server and
a FastAPI web dashboard.

The server does not replace Resonite. It is a control plane that talks to a running
Resonite instance over three channels, each with a distinct role:

1. OSC over UDP for lightweight, low-latency control signals (avatar parameters, session
   start, world load, avatar load, vBot movement, fleet asset import).
2. ResoniteLink over WebSocket for deep, structured world-graph manipulation (reading and
   writing component fields, adding slots and components, reflection over component types,
   atomic batch data-model operations, mesh and texture import).
3. The Resonite Cloud REST API (api.resonite.com) for account-level operations that need no
   running client: browsing public sessions, user lookup, records/inventory, sending
   messages, friends, and cloud variables.

This separation matters. OSC is for fire-and-forget control messages. ResoniteLink is for
precise, inspectable, transactional edits to the world graph. The Cloud REST API is for
things that exist independent of any open session. The tools are grouped so an agent can
pick the correct channel for the job rather than guessing.

## 2. Transports and Entry Points

The server can run in three transport modes, selected by CLI flag, the MCP_TRANSPORT
environment variable, or the default.

- stdio (default): the FastMCP server speaks JSON-RPC over standard input/output. Used by
  Claude Desktop, Cursor, and other MCP hosts.
- http: FastMCP Streamable HTTP served by FastAPI, default bind 127.0.0.1:10979 at path
  /mcp. Used by remote/agent-lab clients and the bundled web dashboard.
- sse: legacy Server-Sent Events transport. Deprecated; prefer http.

Two entry paths exist:

- `resonite-mcp` / `python -m resonite_mcp` invokes the CLI. Without --stdio it boots the
  FastAPI HTTP app (uvicorn) which hosts both the REST dashboard API and the MCP endpoint.
  With --stdio it runs the stdio MCP server. With --agentic it also enables CodeMode BM25
  skill discovery for the agentic planner.
- `python -m resonite_mcp` through the server module's __main__ block initializes the server
  and runs the FastMCP server over the resolved transport.

CLI flags: --host (default 127.0.0.1), --port (default 10979), --log-level, --stdio,
--agentic, --version.

## 3. Network Ports

The server uses these ports. All are configurable via environment variables.

- 10978 TCP: the React/Vite web dashboard frontend.
- 10979 TCP: the FastAPI backend and default MCP HTTP-Streamable bind port.
- 9000 UDP: OSC send. The server sends avatar, session, world, vBot, and fleet control
  messages to a running Resonite client here (RESONITE_OSC_PORT).
- 9001 UDP: OSC receive. The server listens here for responses and events from Resonite,
  and it hosts the WorldLabs import listener.
- 4242 WebSocket: the ResoniteLink in-game bridge (RESONITELINK_PORT).
- 12512 UDP: ResoniteLink LAN session discovery broadcast.
- 9079 TCP: Prometheus metrics scrape server (PROMETHEUS_PORT).

Outbound HTTP clients the server talks to as part of the build-and-inhabit fleet pipeline:
Blender MCP (127.0.0.1:10849), GIMP MCP (127.0.0.1:10773), Inkscape MCP
(127.0.0.1:10900), Avatar MCP (127.0.0.1:10793), WorldLabs/Marble (127.0.0.1:10865), and
the vBot robotics registry (127.0.0.1:12230). The Resonite Cloud REST API is outbound to
api.resonite.com.

## 4. Environment Variables

- MCP_TRANSPORT: stdio | http | sse. Default stdio.
- MCP_HOST: HTTP bind host. Default 127.0.0.1.
- MCP_PORT: HTTP bind port. Default 10979.
- MCP_PATH: HTTP endpoint path. Default /mcp.
- MCP_BRIDGE_URLS: comma-separated URLs of other MCP servers to federate as proxy providers.
- RESONITE_OSC_HOST / RESONITE_OSC_PORT: OSC send target. Defaults 127.0.0.1 / 9000.
- RESONITE_TOKEN / RESONITE_USER_ID: Resonite Cloud API session token and user id for REST
  auth without interactive login.
- RESONITELINK_HOST / RESONITELINK_PORT: ResoniteLink WebSocket. Defaults localhost / 4242.
- RESONITE_LLM_BASE_URL: base URL for agentic sampling fallback.
- RESONITE_TAURI: 1/true/yes adds Tauri CORS origins.
- RESONITE_PREFAB_APPS: 0 disables Prefab app=True cards.
- RESONITE_MCP_METRICS_ENABLED: 0/false disables Prometheus metrics.
- PROMETHEUS_PORT: metrics scrape port. Default 9079.
- RESONITE_INVENTORY_MODE: mock | live | auto. Inventory adapter behavior.
- RESONITE_MCP_LOG_DIR: enables file logging when set.
- OLLAMA_URL / LM_STUDIO_URL: local LLM substrate probes (defaults 11434 / 1234).
- OPENAI_API_KEY: read by the LLM module for hosted fallback.

Filesystem conventions: ~/.avatarmcp/models/ holds canonical VRM avatar files shared with
the avatar-mcp and vrchat-mcp servers; ~/Documents/ResoniteAssets/ holds categorized
inventory assets; the RAG index lives at ./.lancedb.

## 5. Tool Surface by Subsystem

The FastMCP tool surface is roughly 88 tools plus 5 prompt templates. The tools are grouped
below by subsystem. Each entry gives the tool name, its purpose, and its key parameters.

### 5.1 Core Server (server.py)

- search_guides(query, limit=5): semantic RAG search over the bundled guides indexed in
  LanceDB. Returns ranked guide chunks.
- ask_resonite(question): retrieves relevant guide context with RAG, then synthesizes an
  answer with the best available local LLM substrate (Ollama or LM Studio). Use for
  open-ended "how do I ..." questions about the server or Resonite.
- health_check(): returns version, agent lab phase, plugin status, OSC/Link/RAG status, and
  whether Resonite is installed and running.
- agentic_plan_execute(goal): plans and executes a multi-step goal autonomously, restricted
  to a curated set of safe tools. Uses ctx.sample() for planning and reasoning. See section
  9.

Custom HTTP routes: POST /api/resonite/launch (launches Resonite via
steam://rungameid/2519830), GET /api/status, GET /api/stats, GET /api/llm-discovery.

### 5.2 OSC Core (osc.py)

- send_osc(host, port, address, values): send a raw OSC message. Address must start with /.
- start_osc_server(port, address=0.0.0.0): start an OSC receiver.
- stop_osc_server(port): stop a receiver.
- get_received_messages(port, address_pattern?, max_age_seconds?, limit=100): read buffered
  OSC messages. Buffer capped at 1000 per port.
- get_latest_message(port): newest message.
- get_osc_server_stats(port): per-port message/error counters.
- clear_osc_message_buffer(port): reset a port's buffer.
- test_osc_echo(port=9000): send a self-echo test to verify OSC round-trip.

### 5.3 Session (session.py)

- resonite_session_start(session_name?, world_path?, avatar_slot?): send /resonite/session/start.
- resonite_session_status(): current session status.
- resonite_world_load(world_path): load a world. Validates the path prefix against an
  allow-list: resonite://, file://, or inventory://. Requires Resonite running.
- resonite_session_end(): tear down the session; closes OSC servers, clears clients,
  disconnects ResoniteLink.

### 5.4 Avatar (avatar.py)

- resonite_avatar_load(avatar_id, slot=0, parameters?): load an avatar into a slot and
  optionally set parameters.
- resonite_parameter_set(parameter_name, value, avatar_slot?): set an avatar parameter via
  OSC (/avatar/parameters/{name} or /avatar/{slot}/parameters/{name}).
- resonite_protoflux_execute(script_name, script_data?, execute=True): run a ProtoFlux
  script.

### 5.5 Inventory (inventory.py)

All inventory tools send OSC to Resonite and wait for the response server on 9001. They use
a pluggable adapter controlled by RESONITE_INVENTORY_MODE (mock | live | auto).

- resonite_inventory_list(item_type?, search_query?, limit=50, offset=0)
- resonite_inventory_search(query): alias search.
- resonite_inventory_spawn(item_id, position?, rotation?, scale?)
- resonite_inventory_upload(item_path, item_name, item_type, description?, is_public=false)
- resonite_inventory_delete(item_id, confirm_deletion=true): deletion requires explicit
  confirmation; the default is true.
- resonite_inventory_share(item_id, share_with, permission_level="read")
- resonite_inventory_info(item_id)

### 5.6 Plugin Manager (plugin.py)

- plugin_list(): loaded plugins.
- plugin_load(plugin_name)
- plugin_unload(plugin_name)
- plugin_reload(plugin_name)
- plugin_discover(): discover available plugins.
- plugin_info(plugin_name?): details, or all if omitted.

### 5.7 System (system.py)

- help(level="basic"|"intermediate"|"advanced", topic?): contextual help.
- status(level?, focus?): system status as markdown.

### 5.8 Resonite Cloud REST API (rest_api.py)

- resonite_rest_login(username, password, remember_me=true): authenticate to
  api.resonite.com and store a session token (in-process store; use RESONITE_TOKEN +
  RESONITE_USER_ID env for persistence across restarts).
- resonite_rest_get_sessions(name?, host_name?, host_id?, min_active_users=0,
  include_empty_headless=true): browse public sessions. No auth.
- resonite_rest_get_user(username_or_id): user lookup, auto-detects username vs id.
- resonite_rest_get_records(user_id?, path?, record_id?): browse records/inventory. Auth.
- resonite_rest_send_message(target_user_id, message): send a text message, used to deliver
  GLB/SPZ URLs in-session. Auth.
- resonite_rest_get_platform(): platform info. No auth.
- Cloud variables (auth): resonite_cloud_var_list(user_id="", path="Cloud"),
  resonite_cloud_var_get(path, user_id=""), resonite_cloud_var_set(path, value, user_id="")
  (PUT, creates if absent), resonite_cloud_var_delete(path, user_id="").
- Friends (auth): resonite_friends_list(), resonite_friend_requests(),
  resonite_friend_presence(user_id).

### 5.9 ResoniteLink (resonite_link.py)

Real WebSocket protocol 0.13.1 against the in-game ResoniteLink bridge.

- Discovery/connect: resonite_link_discover(timeout_seconds=12.0) over UDP 12512;
  resonite_link_connect(host="localhost", port=4242).
- Slots: resonite_link_get_slot(slot_id="Root", include_component_data=false, depth=0);
  resonite_link_get_node(ref_id); resonite_link_get_children(slot_id);
  resonite_link_add_slot(name, parent_id="Root", pos_x/y/z, slot_id="");
  resonite_link_destroy_slot(slot_id, preserve_assets=false).
- Components: resonite_link_add_component(slot_id, component_type, members?);
  resonite_link_read_field(ref_id); resonite_link_write_field(component_id, member, value,
  value_type=""); resonite_link_set(component_id, field, value);
  resonite_link_get(component_id, field).
- Sync/reflection/batch: resonite_link_call_method(target_id, method_name, arguments?);
  resonite_link_reflect(component_type=""): list supported component types, or the member
  definitions of one; resonite_link_batch(operations): atomic dataModelOperationBatch.
- Assets: resonite_link_import_mesh_json(vertices, submeshes, bones?, blendshapes?): imports
  a procedural mesh and returns an asset URL (live-verified);
  resonite_link_import_texture(file_path): import a texture (shape-confirmed);
  resonite_link_spawn_mesh(vertices, submeshes, name, pos_x/y/z, color_r/g/b/a): full render
  chain importMeshJSON -> addSlot -> StaticMesh -> MeshRenderer -> PBS_Metallic;
  resonite_link_spawn(template_url, position): returns not_implemented for URL/file
  templates.
- Animate (backport from overte-mcp, 2026-09-02): resonite_link_animate(slot_id,
  mode="spin"|"bob"|"bounce", axis_x/y/z, speed, amplitude, damping, duration_s, tick_hz):
  server-driven loop animation via repeated updateSlot calls. "bounce" is a real closed-form
  drop-and-rebound simulation (energy loss per landing), not a sine wave. Live-verified.
- Fixture spawner (backport, 2026-09-02): resonite_link_spawn_fixture(fixture="box"|"cup"|
  "ball"|"table"|"chair", name="", pos_x/y/z, color_r/g/b/a): preset multi-part test fixtures
  for gripper/manipulation testing. No avatar-relative default placement - ResoniteLink
  cannot read the local user's position (protocol has no such message), so pos_x/y/z must be
  given explicitly. Offline-verified (mesh geometry checked, not yet spawned live).
- Model/texture depot (backport, 2026-09-02, tools/depot.py): resonite_link_depot_list(kind),
  _add(kind, file_path, description="", category=""), _update_metadata(kind, name, ...),
  _remove(kind, name), _spawn(kind, name, pos_x/y/z, slot_name=""), _backup(),
  _list_backups(), _restore_backup(name). kind is "model" (.glb/.vrm/.gltf, spawned via
  gltf_to_mesh_json + spawn_mesh) or "texture" (.png/.jpg/.jpeg, imported via
  import_texture_file, returns asset_url only - no mesh to attach it to automatically). Local
  on-disk folder + manifest.json, not HTTP-served (ResoniteLink imports take a file path on
  the Resonite host, not a URL, unlike Overte).
- NOT ported from overte-mcp: nearby-object search. ResoniteLink has no spatial-query
  primitive like Overte's Entities.findEntities; doing this would mean walking the scene
  graph and filtering by distance client-side, a different design, not a straight port. See
  README.md's Status & Roadmap.

### 5.10 Fleet Pipeline (fleet_tools.py)

resonite_fleet(operation, ...) is a portmanteau tool with 19 operations that orchestrate the
cross-fleet build-and-inhabit pipeline: list_presets, execution_mode, list_staging,
import_staged_assets, pull_inkscape_ui, import_blender_asset, import_gimp_texture,
list_vrm_staging, import_vrm_batch, pull_blender_vrm, pull_avatar_vrm,
list_protoflux_presets, list_marble_staging, import_worldlabs_batch, pull_inkscape_fab,
run_marble_pipeline, inventory_status, run_fleet_pipeline, run_strict_fleet_pipeline.

Key parameters: staging_dir, input_dir, vrm_dir, object_name, texture_path,
target_slot="root", per-tool base URLs, protoflux_preset, export_format="vrm",
skip_inkscape/blender/gimp/vrm/marble switches, marble_dir, fab_staging_dir, manifest.

The pipeline chains Inkscape UI mockups, Blender GLB/VRM exports, GIMP textures, and Marble
worlds into Resonite via OSC /resonite/fleet/import and ResoniteLink. Execution-mode gating
(hands_in / hands_off_launch / hands_off_install) guides the run.

### 5.11 Voice (voice_tools.py)

resonite_voice(operation, ...): list_macros, parse_command, send_macro, execution_mode.
Predefined OSC macros include wave, jump, sit, toggle_ui, import_staging. A keyword map plus
optional local-LLM refinement turns natural-language commands into macros.

### 5.12 vBot (vbot.py)

- resonite_vbot_list_types(): yahboom, mechazilla, bumi, godzilla, custom.
- resonite_vbot_spawn(robot_type="yahboom", robot_id, position_x/y/z, scale): sends
  /resonite/vbot/spawn.
- resonite_vbot_move(robot_id, linear, angular): /robot/{id}/move.
- resonite_vbot_head(robot_id, yaw_deg, pitch_deg): /robot/{id}/head.
- resonite_vbot_stop(robot_id): /robot/{id}/stop.
All over UDP 9000.

### 5.13 Integrations (integrations.py)

- resonite_import_worldlabs_url(splat_url, mesh_url?, world_name, target_slot): download a
  .spz/.glb splat and import it.
- resonite_import_worldlabs_batch(manifest, target_slot): batch splat import.
- resonite_import_blender(object_name, export_format="glb"): call blender-mcp, download the
  result, and import it.
- resonite_avatar_unity(avatar_model_path, unity_package_path?): avatar/Unity asset import.

Note on honesty: some integration paths send a legacy ResoniteLink payload shape that the
real 0.13.1 protocol rejects (it requires $type). When that happens the call surfaces a
ResoniteLinkError or falls back rather than returning a fake success. Treat a fallback as
"the structured import path is unavailable; use the OSC /worldlabs/import route instead".

### 5.14 Prefab Cards (prefab_cards.py)

Two app=True tools render rich interactive cards: resonite_dashboard_card() and
resonite_inventory_card(limit=10).

### 5.15 OSC Extensions Plugin (osc_extensions.py)

- osc_monitor_start(port=9001, address_filter?, duration_seconds?)
- osc_batch_send(port, messages, delay_ms=0)
- osc_record_session(port, session_name, duration_seconds=60)
- osc_analyze_traffic(port, analysis_duration=10)

### 5.16 ProtoFlux Helpers Plugin (protoflux_helpers.py)

- protoflux_analyze_script(script_name)
- protoflux_generate_template(template_type, customization?): template_type is one of
  avatar_animation, world_interaction, ui_control, data_processing, network_sync,
  physics_simulation.
- protoflux_debug_session(script_name, debug_mode="step_through"|"breakpoint"|"trace")
- protoflux_optimize_script(script_name, optimization_level="moderate"|"conservative"|
  "aggressive")
- protoflux_document_script(script_name)

## 6. Prompt Templates

Five reusable prompt templates are registered (prompts.py): resonite_session_setup,
avatar_animation_setup, world_exploration, inventory_management, cross_mcp_integration.

## 7. Safety and Scoping

- OSC ports are validated 1..65535; address patterns must start with /.
- resonite_world_load rejects any path not starting with resonite://, file://, or
  inventory://.
- Inventory deletion requires confirm_deletion=true.
- The fleet launch endpoint resolves paths under D:/Dev/repos only (403 otherwise).
- Execution-mode gating (utils/execution_mode.py) reports hands_in, hands_off_launch, or
  hands_off_install so an agent can decide whether to ask for a manual step.
- Implementation honesty is enforced: NOT-implemented operations (generic file/VRM/GLB/FBX
  import via ResoniteLink, URL/template spawning) return explicit not_implemented or a 501
  HTTP status rather than a fabricated success. ResoniteLink write_field raises because the
  protocol writes component members, not bare refs. Legacy {"type":...} payloads are
  rejected in favor of {"$type":...}.
- ProtoFlux template/optimization/debug modes are enum-validated.
- CORS origins are restricted to the dashboard host and, when RESONITE_TAURI is set, Tauri
  origins.
- Declared mock paths exist so the UI is never misleading: avatar info HTTP fallback returns
  demo data, the gallery falls back to Unsplash images, and the inventory adapter can return
  a clearly-declared MOCK catalog when live is unavailable.

## 8. RAG and Knowledge

The server maintains a LanceDB index (./.lancedb) over the repository markdown and
docs/**/*.md, chunked by ## headings, embedded with sentence-transformers/all-MiniLM-L6-v2.
search_guides and ask_resonite use it. This grounds answers about the server and Resonite
usage in the bundled documentation.

## 9. Agentic Autonomy

agentic_plan_execute(goal) is the primary autonomous path. It restricts itself to eight
safe tools: resonite_session_start, resonite_world_load, resonite_avatar_load,
resonite_parameter_set, resonite_inventory_list, resonite_inventory_spawn,
resonite_rest_get_sessions, and send_osc. Planning uses ctx.sample() with a modest token
budget; execution samples reasoning. Agentic reasoning is available for diagnostics
(agentic_reason(observation, question)). The --agentic CLI flag enables CodeMode BM25 skill
discovery to improve planning. This keeps autonomous behavior on a curated, low-risk subset
of the full surface while still composing real multi-step world interactions.

## 10. Federation

MCP_BRIDGE_URLS can point at other MCP servers; each is added as a proxy provider so the
fleet can route across servers. The dashboard's apps catalog provides cross-MCP navigation
to 12+ fleet services. This makes Resonite MCP a cooperating node in the build-and-inhabit
ecosystem rather than an island.

## 11. Domain Glossary

To use these tools correctly an agent should understand the core Resonite concepts the
server manipulates.

- Session: a live instance of Resonite running a world. A session has an owner, a world,
  a list of users, and is either public, friends-only, or private.
- World: the space a session runs. Identified by a world path. The server validates paths
  against resonite://, file://, and inventory://.
- Slot: a node in the world object graph. Slots form a tree; every object in a world hangs
  off a slot. Slots have a name, position, rotation, scale, and an ordered list of child
  slots and components.
- Component: a typed behaviour attached to a slot. Components carry fields (members), each
  with a typed value. Examples: Transform, MeshRenderer, StaticMesh, PBS_Metallic,
  CharacterController.
- Ref ID: the stable reference identifier ResoniteLink uses to address a slot or component
  in the object graph.
- Avatar: a user's virtual body. An avatar has parameters (biometric and locomotion values),
  slots, and can be loaded into a named slot of the user's rig.
- Parameter: a named, typed value on an avatar or world object that the server can set over
  OSC (e.g. tracking smoothing, locomotion mode, an arbitrary custom parameter).
- ProtoFlux: Resonite's visual node-graph scripting system. Scripts are stored by name and
  can be executed, generated from templates, debugged, optimized, and documented.
- Inventory: the user's asset database. Items have an id, name, type, description, and
  visibility. Items can be listed, searched, spawned into the world, uploaded, deleted,
  shared, and inspected.
- Cloud variable: a persistent key-value slot stored on the Resonite cloud under a path
  (e.g. Cloud/MyVar), scoped to a user. Read, written, listed, and deleted via the REST
  API.
- OSC address: a string path (e.g. /resonite/avatar/load) that names a control channel. The
  server sends messages to these addresses and can listen on its own addresses.
- ResoniteLink: an in-game component that opens a WebSocket the server connects to for
  structured object-graph access.
- vBot: a controllable robot body spawned into the world (yahboom, mechazilla, bumi,
  godzilla, or custom) driven over OSC.
- Splat: a gaussian-splat 3D scan (SPZ or GLB), imported from WorldLabs and placed into a
  world.

## 12. OSC Address Reference

The server sends control signals to these well-known addresses (default host
127.0.0.1:9000). An agent can reference them when composing send_osc calls or reasoning
about what a tool did.

- /resonite/session/start: start a session (session name, world, avatar slot).
- /resonite/session/stop: stop the current session.
- /resonite/world/load: load a world by validated path.
- /resonite/avatar/load: load an avatar into a slot (avatar id, slot, parameters).
- /avatar/parameters/{name} and /avatar/{slot}/parameters/{name}: set an avatar parameter.
- /protoflux/execute: execute a ProtoFlux script.
- /resonite/fleet/import: import a staged fleet asset.
- /resonite/vbot/spawn: spawn a vBot (id, type, x/y/z, scale).
- /robot/{id}/move: move a vBot (linear, angular).
- /robot/{id}/head: aim a vBot head (yaw, pitch).
- /robot/{id}/stop: stop a vBot.
- /worldlabs/import: import a WorldLabs splat.

The server listens on 9001 (default) for OSC responses and events. The receive buffer is
capped at 1000 messages per port; long-running monitors should drain via
get_received_messages with a max_age or clear the buffer with clear_osc_message_buffer.

## 13. Return Format by Subsystem

Each subsystem returns structured data that an agent should parse rather than assume.

- OSC: send_osc returns a confirmation with host, port, address, and the number of values
  sent. get_received_messages returns a list of messages with timestamp, address, and typed
  values plus a total count. get_osc_server_stats returns per-port counters for messages
  received, errors, and buffer occupancy.
- Session: status tools return the session name, world path, connected users, and the OSC
  server and ResoniteLink client state. world_load returns a success or a validation error
  when the path is not allow-listed.
- Avatar: load and parameter tools return the target slot, the parameter path, and the
  value applied. protoflux_execute returns the script name and an execution flag.
- Inventory: list and search return items with id, name, type, and visibility, plus
  pagination fields (limit, offset, total). spawn returns the item id and the placement
  position/rotation/scale. upload returns the created item. delete requires the
  confirm_deletion flag and returns the deleted id. share returns the target user and the
  permission level applied. info returns full metadata for one item.
- REST API: get_sessions returns public sessions with name, host, user counts, and
  headless status. get_user returns a user profile. get_records returns records under a
  path. send_message returns a delivery confirmation. Cloud variable tools return the
  current value, or the write/delete acknowledgment. Friends tools return profiles and
  presence.
- ResoniteLink: get_slot/get_node/get_children return the object graph with ref ids,
  names, and (optionally) component data. write_field and set return the component id,
  member, and value written. batch returns per-operation results and an overall atomicity
  status. reflect returns either the list of supported component types or the member
  definitions of one type. import_mesh_json returns an asset URL. spawn_mesh returns the
  created slot ref id.
- Fleet: resonite_fleet returns a per-step report for each pipeline stage it ran, plus an
  overall success flag and the execution mode. run_fleet_pipeline and
  run_strict_fleet_pipeline return the chain of steps with skip/run status.
- Voice: resonite_voice returns the resolved macro (parse_command), the list of macros
  (list_macros), the applied macro (send_macro), or the execution mode.

## 14. Error Handling and Honest Failure

The server is deliberately strict about not fabricating success. An agent should treat these
signals as real conditions, not bugs.

- Validation errors: invalid OSC ports, addresses that do not start with /, non-allow-listed
  world paths, and unconfirmed deletes are rejected with explicit error messages before any
  side effect.
- NOT-implemented: generic file/VRM/GLB/FBX import through ResoniteLink and URL/template
  spawning are not supported by protocol 0.13.1. These return an explicit not_implemented
  result or an HTTP 501. Do not retry with slightly different arguments; use the supported
  path instead (OSC /worldlabs/import for splats, import_mesh_json for procedural meshes,
  the fleet pipeline for staged assets).
- Legacy payload rejection: real ResoniteLink messages must carry $type. Sending a legacy
  {"type":...} shape is rejected. When an integration helper sends the legacy shape, it
  surfaces a ResoniteLinkError or falls back to the OSC route instead of reporting a fake
  success.
- write_field limitation: the protocol writes component members, not bare references.
  resonite_link.write_field raises with guidance when given a bare ref id rather than a
  component member.
- Auth required: REST and cloud-variable and friends tools need a session token, either from
  resonite_rest_login or from RESONITE_TOKEN + RESONITE_USER_ID. Without it they fail with
  an authentication error.
- MOCK/degraded paths are declared, never silent: the avatar-info HTTP fallback returns
  demo data, the gallery falls back to Unsplash images, and the inventory adapter may return
  a clearly-declared MOCK catalog when live inventory is unavailable. Distinguish these from
  live results by the declared MOCK marker.

## 15. Configuration Scenarios

- Claude Desktop (stdio): register the server with a uv command pointing at the repo, or
  use a built .mcpb bundle. The bundle manifest uses uv with PYTHONPATH=${PWD}/src.
- Remote/agent-lab (http): run python -m resonite_mcp --host 0.0.0.0 --port 10979 and point
  clients at http://host:10979/mcp.
- Dashboard: start web_sota/start.ps1 to bring up the frontend (10978) and backend
  (10979) together. just serve runs the backend alone.
- Agentic: run with --agentic to enable CodeMode BM25 skill discovery for better planning.
- Federation: set MCP_BRIDGE_URLS to a comma-separated list of other MCP server URLs to add
  them as proxy providers.
- Headless: the dashboard can run headless (backend only) for scripted or CI usage.

## 16. Version Notes

The package and HTTP app report version 1.2.0. The FastMCP server name/health and Prefab
cards may report a stale 0.8.0; treat the package version as authoritative and flag any
discrepancy rather than trusting either string blindly. The manifest tool list is larger
than the true @server.tool() count because it also enumerates HTTP route functions.
