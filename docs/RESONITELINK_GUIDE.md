# ResoniteLink Technical Guide

ResoniteLink is a high-performance, real-time WebSocket JSON protocol for interacting with Resonite worlds. It provides a more robust and lower-latency alternative to OSC for complex data model manipulation.

## Overview

Unlike OSC, which sends individual packets, ResoniteLink maintains a persistent state-aware connection. It allows you to:
- **Spawn objects** using template URLs.
- **Set component values** directly by unique ID.
- **Get component values** asynchronously with reliable delivery.

## Getting Started

### 1. Prerequisites
- Resonite client (or headless) running and **hosting** the session — only the host can enable ResoniteLink.
- ResoniteLink is **official and built into Resonite** (no mod required). Enable it:
  - Graphical client: Sessions → "Enable ResoniteLink"
  - Headless config: `"enableResoniteLink": true` (optional `"forceResoniteLinkPort"`)
  - Running headless console: `enableResoniteLink <port>` (0 = random port)
- Default ResoniteLink port: **4242**.

### Upstream protocol status (upgraded 2026-07-11)

This server implements the **real ResoniteLink wire format, verified against
upstream 0.13.1** (2026-03-11): `$type` discriminators, `messageId` /
`sourceMessageId` correlation, typed value wrappers, and camelCase message
names. The protocol is still labeled beta upstream; breaking changes remain
possible, so re-verify on upstream releases.

| Capability | Status in this server |
|-----------|----------------------|
| Slot/component CRUD (`getSlot`, `addSlot`, `updateSlot`, `removeSlot`, `getComponent`, `addComponent`, `updateComponent`, `removeComponent`) | ✅ Implemented |
| Session metadata (`requestSessionData`) | ✅ Implemented (fetched on connect) |
| Reflection (`getComponentTypeList`, `getComponentDefinition`, `getTypeDefinition`, `getEnumDefinition`) — 0.9.0 type-reference semantics | ✅ Implemented |
| Batching (`dataModelOperationBatch`) | ✅ Implemented |
| Sync method calls (0.11.0: `callSyncMethod`, `callStaticSyncMethod`) | ✅ Implemented |
| LAN session discovery (0.12.0: UDP 12512 announcements) | ✅ Implemented (`discover_sessions`, tool `resonite_link_discover`) |
| Asset imports: mesh-JSON (`import_mesh_json` / `resonite_link_import_mesh_json`) | ✅ Wrapped + live-verified 2026-07-18 |
| Asset imports: convenience `spawn_mesh` / `resonite_link_spawn_mesh` (import + StaticMesh + MeshRenderer + optional PBS_Metallic material, one call) | ✅ Wrapped 2026-07-18, built from individually-verified steps |
| Asset imports: texture (`import_texture_file` / `resonite_link_import_texture`) | ⚠️ Wrapped 2026-07-18, wire shape confirmed against upstream source, **not yet live-tested** |
| Asset imports: raw mesh (`importMeshRawData`) | ❌ Not implemented — requires a binary WebSocket payload frame this client doesn't send yet; `import_mesh_raw()` raises with guidance rather than faking it. Use mesh-JSON instead. |
| Asset imports: audio (`import_audio_clip_file` / `spawn_audio`, tools `resonite_link_import_audio` / `resonite_link_spawn_audio`) | ✅ Wrapped + live-verified 2026-07-19 (full playback chain: StaticAudioClip → AudioClipPlayer → AudioOutput, autoplay) |
| Asset imports: cubemap | ⚠️ Not yet wrapped |
| Mesh source converters (`utils/gltf_meshjson.py`, `utils/stl_meshjson.py`) — GLB/glTF and STL to mesh-JSON, stdlib only | ✅ Live-verified 2026-07-18/19 against real fixtures (Marble colliders, Boomy's chassis STL, a full VRM avatar) |
| Mesh decimation (`utils/decimate_meshjson.py`) — vertex clustering | ✅ Live-verified; explicitly NOT equivalent to Blender's quadric Decimate — a no-Blender fallback, not the production path |
| Generic model/file import (VRM/GLB/FBX) | ❌ Does not exist in the protocol — endpoints return not_implemented |
| Dictionaries (0.10.0), spherical harmonics (0.13.x) | ✅ Pass-through (JSON client; use explicit `rl_value` types) |

**LIVE VALIDATED 2026-07-18/19 (second session)**: pushed a hand-authored
multi-block mesh and a decimated real robot chassis (STL) live, then a full
undecimated VRM avatar (190,111 vertices / 45,451 triangles — no decimation
needed at all, well above the previous ~11.5k-triangle proof point). Found
and fixed one real, previously-wrong assumption: `uvs` is a **list** of
coordinate objects, not a bare `{x,y}` dict — confirmed via a live server
error, not guessed. Built and live-verified the full audio pipe (import →
StaticAudioClip → AudioClipPlayer → AudioOutput, autoplay). **Still open**:
the `UV_Coordinate` polymorphic `$type` discriminator is unknown after four
live attempts (`UV_Coordinate`/`float2`/`uv`/`UVCoordinate` all rejected) —
blocks textured (non-solid-color) materials until resolved via upstream
source inspection. VRM bones/blendshapes remain unparsed — static geometry
only so far. Details: mcp-central-docs
`projects/resonite-living/RESONITE_LIVING_STATUS_20260718.md`.

**LIVE VALIDATED 2026-07-18**: end-to-end run against a running Resonite
instance succeeded with zero client fixes — Resonite **2026.7.14.913**, protocol
**0.13.1.0** (exact match for this client). Verified live: UDP session discovery
(port 12512; note the in-game dashboard port readout was WRONG in this test —
always use `discover_sessions()`), connect + session metadata, `getSlot` on Root
with component data, `addSlot` with position + protocol readback verification,
`importMeshJSON` (hand-built unit cube), the StaticMesh -> MeshRenderer render
chain, and PBS_Metallic material wiring via the list-member `Materials`
encoding. All of that is now wrapped into first-class client methods
(`import_mesh_json`, `spawn_mesh`) and MCP tools (`resonite_link_import_mesh_json`,
`resonite_link_spawn_mesh`) rather than left as raw `_send()` calls. The 30
wire-format regression tests (up from 22) are the offline gate; next live-test
target is `import_texture_file`/`resonite_link_import_texture` (shape-correct,
unproven) and the Blender-mesh-JSON volume path. Evidence: mcp-central-docs
`projects/RESONITE_PHASE0_RUNBOOK.md` execution log,
`projects/RESONITE_PHASE0_HANDOFF.md` wire-shape cheat sheet.

### 2. Connection
Prefer discovery over guessing a port — call `resonite_link_discover`
first (UDP 12512 broadcast) and connect to whatever it finds. The
default port below is a fallback only:

```python
sessions = await resonite_link_discover()
await resonite_link_connect(host=sessions[0]["host"], port=sessions[0]["linkPort"])
```

## Available Tools

### `resonite_link_spawn_mesh` (real, live-verified)
Imports mesh-JSON data and wires the full render chain (StaticMesh →
MeshRenderer → optional PBS_Metallic material) in one call.

```python
await resonite_link_spawn_mesh(
    vertices=[...],       # [{"position": {"x","y","z"}, ...}, ...]
    submeshes=[...],      # [{"$type": "triangles", "triangles": [...]}]
    position={"x": 0, "y": 1, "z": 5},
    name="my-object",
    color={"r": 0.8, "g": 0.4, "b": 0.1, "a": 1.0},
)
```

### `resonite_link_spawn_audio` (real, live-verified)
Imports an audio file and wires the full playback chain (StaticAudioClip →
AudioClipPlayer → AudioOutput), autoplaying it.

```python
await resonite_link_spawn_audio(
    file_path="C:/path/to/clip.wav",
    position={"x": 0, "y": 1.5, "z": 5},
    loop=False,
    volume=1.0,
)
```

### `resonite_link_add_component` / `resonite_link_update_component`
Adds a component to a slot, or updates members on an existing one — the
real mechanism for setting values (there is no generic per-field-ref
"set"; the protocol writes named members on a specific component).

```python
material_id = await resonite_link_add_component(
    slot_id="Reso_A12",
    component_type="[FrooxEngine]FrooxEngine.PBS_Metallic",
    members={"AlbedoColor": {"$type": "colorX", "value": {"r": 1.0, "g": 0.0, "b": 0.0, "a": 1.0}}},
)
```

### `resonite_link_get_component`
Reads a component's full data (type + all members) by ID — there is no
per-field read; the protocol returns the whole component.

```python
await resonite_link_get_component(component_id="Reso_A13")
```

## Best Practices

1. **Discover, don't guess ports.** Always call `resonite_link_discover`
   (UDP 12512 broadcast) rather than assuming a port — the in-game
   dashboard's displayed port has been observed wrong in testing, and the
   client's own default (4242) is just a fallback, not a guarantee.
2. **No template-URL spawning.** The protocol has no `resonite:///` item
   spawning — build content with `add_slot`/`add_component`, or import
   assets via the real asset-import messages (mesh-JSON, texture, audio).
3. **Batching**: avoid spamming component updates in high-frequency loops
   (above 60Hz) to prevent network congestion; use
   `dataModelOperationBatch` for grouped changes instead.
4. **IDs are not persistent** across world save/load — capture them fresh
   each session rather than hardcoding.

---
**Note**: ResoniteLink is currently in Beta. Protocol changes may occur.
