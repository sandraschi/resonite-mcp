# Resonite World Building & Testing

You are helping a human build, test, and animate content in a live Resonite session through
resonite-mcp's ResoniteLink tools (`resonite_link_*`, `src/resonite_mcp/tools/resonite_link.py`
and `depot.py`). This is a task-oriented recipe skill; for the full tool/protocol reference
see `assets/prompts/system.md` §5.9, and `assets/prompts/user.md` §10-11b for longer
walkthroughs.

New 2026-09-03. resonite-mcp had no FastMCP-native skill before this.

## Before anything: discover and connect

ResoniteLink is enabled per-session (Dashboard -> Session -> Settings -> Enable ResoniteLink
in-game, or `enableResoniteLink` in headless config). It is NOT always-on.

1. `resonite_link_discover(timeout_seconds=12.0)` - listens on UDP 12512 for the session's
   broadcast, returns its real port. Don't guess/hardcode a port.
2. `resonite_link_connect(host="localhost", port=<from discover>)`.
3. **After any world save/load or world/session change, reconnect and re-resolve slot IDs by
   name.** Slot/component IDs are NOT persistent across a world reload (confirmed against the
   upstream `Yellow-Dog-Man/ResoniteLink` docs) - a cached ID from before a reload is stale,
   not a bug to chase.

## What ResoniteLink cannot do (don't try to build around these silently)

- **No local-user position query.** The protocol only exposes the world data model, not
  session/user data - there is no way to read where the connected human currently is. Every
  spawn tool here needs explicit `pos_x/y/z`; none can default to "in front of you" the way
  overte-mcp's fixture spawner can.
- **No generic model file import.** VRM/GLB/FBX cannot be imported as a single opaque asset -
  only `importTexture2DFile`/`importMeshJSON`/`importMeshRawData`/`importAudioClipFile` exist.
  Use `resonite_link_depot_spawn(kind="model", ...)` (below), which decomposes the GLB/VRM
  into mesh-JSON first - don't hand-roll a raw file-import call, it doesn't exist.

## Recipe: build something from scratch

1. `resonite_link_add_slot(name="myBox", parent_id="Root", pos_x=0, pos_y=1, pos_z=0)`.
2. `resonite_link_add_component(slot_id, component_type="[FrooxEngine]FrooxEngine.BoxMesh")`
   or wire up a full custom mesh - see `resonite_link_spawn_mesh` for the one-call version
   (importMeshJSON -> addSlot -> StaticMesh -> MeshRenderer -> PBS_Metallic, given vertices +
   submeshes + optional `color_r/g/b/a`).
3. Read it back to confirm: `resonite_link_get_node(ref_id)` or `resonite_link_get_slot`.

## Recipe: animate a slot

`resonite_link_animate(slot_id, mode, ...)` blocks for `duration_s` while it runs.
- Spin: `mode="spin", axis_x/y/z, speed` (radians/second).
- Bob: `mode="bob", amplitude, speed` (oscillations/second) - smooth sinusoidal.
- Bounce: `mode="bounce", amplitude, damping, speed` - real closed-form drop physics (each
  landing loses energy, settles instead of bouncing forever), not a sine wave.

## Recipe: spawn a gripper/manipulation test fixture

`resonite_link_spawn_fixture(fixture="ball", pos_x=0, pos_y=1, pos_z=2)`. `fixture` is one of
`box`/`cup`/`ball`/`table`/`chair`. `pos_x/y/z` are required (see the position-query gap
above) and default to the world origin if omitted, NOT to anywhere near the user. Multi-part
fixtures (table/chair) spawn as several independent same-colored slots - move each one
separately if you need to relocate the whole thing.

## Recipe: manage reusable models/textures (the depot)

1. Add a local file: `resonite_link_depot_add(kind="model", file_path="C:/path/to/thing.glb",
   description="...", category="...")`. `kind` is `"model"` (.glb/.vrm/.gltf) or `"texture"`
   (.png/.jpg/.jpeg). This copies the file in - it does not fetch URLs.
2. List what's there: `resonite_link_depot_list(kind="model")`.
3. Spawn a depot model: `resonite_link_depot_spawn(kind="model", name="thing.glb", pos_x=0,
   pos_y=0, pos_z=0)`. For `kind="texture"` this instead imports and returns an `asset_url` -
   there's no mesh to attach it to automatically, wire it into a `PBS_Metallic` component
   yourself.
4. Snapshot before risky changes: `resonite_link_depot_backup()`, list with
   `resonite_link_depot_list_backups()`, roll back with
   `resonite_link_depot_restore_backup(name=...)`.

## Not built yet

Nearby-object spatial search (like overte-mcp's `find_nearby`) has no ResoniteLink
equivalent - there's no `Entities.findEntities`-style primitive to build it on. See
`README.md`'s Status & Roadmap.

## Common mistakes to avoid
- Assuming a slot ID from before a world reload is still valid - it isn't, re-resolve by name.
- Calling a fixture/depot spawn tool without `pos_x/y/z` and expecting it near the user - it
  lands at the world origin instead.
- Trying to import a `.fbx`/`.obj` via the depot - only `.glb`/`.vrm`/`.gltf` are supported
  (the conversion path is `gltf_to_mesh_json`, which reads GLB-family containers only).
