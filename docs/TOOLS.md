# resonite-mcp — Tool & API Reference

Moved out of README.md 2026-07-18 per fleet README_STRUCTURE standard.

> **Re-audit pending**: the tool inventory below dates from the 31-tool era and
> predates Agent Lab phases 1–6 (v0.5.0–v1.0.0: resonite_fleet, resonite_voice,
> Marble pipeline, VRM fleet ops, inventory adapter) and the 1.1.0 ResoniteLink
> protocol rewrite. Counts and mock/live status need re-verification against
> `src/resonite_mcp/tools/`. The ResoniteLink section below IS current (1.1.0).

## ResoniteLink (current, live-verified 2026-07-18)

Client implements upstream protocol **0.13.1** (see `docs/RESONITELINK_GUIDE.md`
for the capability table and live-verification record).

- `resonite_link_discover()` — LAN session discovery via UDP 12512. **Always use
  this instead of trusting the dashboard's displayed port.**
- `resonite_link_connect(host?, port?)` — connect; session metadata fetched on connect
- `resonite_link_spawn(...)` — creates named slots (template-URL spawning: not_implemented)
- `resonite_link_set(component_id, field, value)` / `resonite_link_get(component_id, field)`
- `resonite_link_call_method(...)` — sync method calls (protocol 0.11.0)
- `resonite_link_import_mesh_json(vertices, submeshes, bones?, blendshapes?)` —
  live-verified 2026-07-18; returns an asset URL (`local://...`), not an entity ID.
- `resonite_link_spawn_mesh(vertices, submeshes, name?, pos_x/y/z?, color_r/g/b/a?)`
  — convenience: import + StaticMesh + MeshRenderer + optional PBS_Metallic
  material in one call. Live-verified 2026-07-18 as three manual steps, now wrapped.
- `resonite_link_import_texture(file_path)` — wire shape confirmed against
  upstream source, **not yet live-tested**. `file_path` resolves on the
  Resonite host machine.
- Python client (`resonite_mcp.resonite_link.ResoniteLinkClient`): full slot &
  component CRUD, reflection, batching, `rl_value`/`rl_ref`/`rl_auto`/`rl_list`
  helpers, plus `import_mesh_json`/`import_texture_file`/`spawn_mesh` above.
- **Not in the protocol** (endpoints return not_implemented honestly): generic
  VRM/GLB/FBX file import, per-field-ref writes.
- **In the protocol but not implemented client-side**: `import_mesh_raw()`
  (`importMeshRawData`) requires a binary WebSocket payload frame this client
  doesn't send; it raises with guidance instead of faking it. Use mesh-JSON.
  Audio/cubemap imports also remain unwrapped.

## Session Management (4 tools)
- `resonite_session_start(session_name?, world_path?, avatar_slot?)`
- `resonite_session_status()`
- `resonite_session_end()`
- `resonite_world_load(world_path)`

## Avatar Control (3 tools)
- `resonite_avatar_load(avatar_path, slot?, parameters?)`
- `resonite_parameter_set(parameter_name, value, avatar_slot?)`
- `resonite_protoflux_execute(script_name, parameters?)`

## Inventory Management (7 tools)
`resonite_inventory_list / search / spawn / upload / delete / share / info` —
adapter modes mock/live/auto via `RESONITE_INVENTORY_MODE` (v1.0.0), plus
`inventory_status`.

## OSC Communication (8 tools)
`send_osc`, `start_osc_server`, `stop_osc_server`, `get_received_messages`,
`get_latest_message`, `get_osc_server_stats`, `clear_osc_message_buffer`,
`test_osc_echo`. OSC remains useful for high-frequency parameter streaming
(e.g. avatar parameters); ResoniteLink is the primary control path.

## Fleet & Voice (Agent Lab era)
- `resonite_fleet` portmanteau — inkscape UI import, blender/gimp bridges,
  Marble staging (`list_marble_staging`, `import_worldlabs_batch`,
  `run_marble_pipeline`), VRM fleet ops (`list_vrm_staging`, `import_vrm_batch`,
  `pull_blender_vrm`, `pull_avatar_vrm`), ProtoFlux presets.
- `resonite_voice` portmanteau — voice macros + HTTP bridge.

## Plugin Management (6 tools)
`plugin_list / load / unload / reload / discover / info`

## System (3 tools)
`help(level?, topic?)`, `status(level?, focus?)`, `health_check()`

## Usage Examples

```python
# ResoniteLink-first workflow (the modern path)
sessions = await resonite_link_discover()
await resonite_link_connect(host="localhost", port=sessions[0]["linkPort"])
# ... slot CRUD via the client / World Inspector

# Session + avatar (legacy tools)
await resonite_session_start(session_name="MySession")
await resonite_world_load("resonite://TutorialWorld")
await resonite_avatar_load("resonite://DefaultAvatar", slot=0)
await resonite_parameter_set("Happy", 0.8)

# OSC parameter streaming
await send_osc("127.0.0.1", 9000, "/avatar/parameters/CustomParam", [0.75])
```

## HTTP API

HTTP mode: `resonite-mcp --host 127.0.0.1 --port 8000` → interactive docs at
`/docs`. Endpoint families: `/rl/*` (ResoniteLink incl. `GET /rl/discover`),
`/osc/*`, `/resonite/session|avatar|world|inventory/*`, `/plugins/*`,
`POST /api/v1/tool` (Agent Lab bridge), `/metrics` (Prometheus), `/health`.
