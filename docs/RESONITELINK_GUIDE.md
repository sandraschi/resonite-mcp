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
| Asset imports: audio / cubemap | ⚠️ Not yet wrapped |
| Generic model/file import (VRM/GLB/FBX) | ❌ Does not exist in the protocol — endpoints return not_implemented |
| Dictionaries (0.10.0), spherical harmonics (0.13.x) | ✅ Pass-through (JSON client; use explicit `rl_value` types) |

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
First, establish a connection to the ResoniteLink server:

```python
await resonite_link_connect(host="localhost", port=4242)
```

## Available Tools

### `resonite_link_spawn`
Spawns an object from the Resonite inventory or a public URL.

```python
await resonite_link_spawn(
    template_url="resonite:///items/ExampleCube.7pb",
    position={"x": 5.0, "y": 1.0, "z": 0.0}
)
```

### `resonite_link_set`
Sets a field on a specific component using its unique ID.

```python
await resonite_link_set(
    component_id="ID_OF_THE_COMPONENT",
    field="Color",
    value=[1.0, 0.0, 0.0, 1.0] # Red RGBA
)
```

### `resonite_link_get`
Requests the current value of a component field.

```python
await resonite_link_get(
    component_id="ID_OF_THE_COMPONENT",
    field="IsActive"
)
```

## Best Practices

1. **ID Management**: Capture component IDs during spawn or by using the Resonite inspector to target specific elements.
2. **Batching**: While ResoniteLink is fast, avoid spamming `set` commands in high-frequency loops (above 60Hz) to prevent network congestion.
3. **Template URLs**: Use standard `resonite:///` URIs for inventory items to ensure reliable spawning across different world instances.

---
**Note**: ResoniteLink is currently in Beta. Protocol changes may occur.
