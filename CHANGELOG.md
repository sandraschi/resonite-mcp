# Changelog

All notable changes to `resonite-mcp` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased] — 2026-09-02 — Animate + fixture spawner (backport from overte-mcp)

### Added
- `resonite_link_spawn_fixture(fixture, ...)` — preset test fixtures (box/cup/ball/table/
  chair) for gripper/manipulation testing, ported from overte-mcp's `post_fixture_spawn`.
  Box parts reuse `add_box()` from `scripts/live_house_and_roscar_test.py` verbatim (that
  script's own docstring: "Live proof script for the Phase 1 gate" - already live-verified
  there). Ball parts are a new icosahedron mesh generator whose winding is derived
  programmatically to match the proven box convention rather than assumed.
  **Verification status: offline-only.** No Resonite session was reachable during this
  change, so this was checked with a standalone script confirming every preset produces
  non-empty, non-degenerate geometry with winding consistent with the proven box (12/12 box
  triangles, 20/20 ball triangles inward-winding, matching `add_box`'s empirically-correct
  convention) - it has NOT been spawned into a real running session yet. Treat as unverified
  until that happens, especially the ball geometry.
  Unlike overte-mcp's version, there is no avatar-relative default placement: ResoniteLink's
  protocol only exposes the world data model, not session/user data (confirmed against the
  upstream `Yellow-Dog-Man/ResoniteLink` docs), so there is no way to read the local user's
  position to place a fixture "in front of you" - `pos_x/y/z` must be given explicitly.
- `resonite_link_animate(slot_id, mode, ...)` — loop-animate any slot: `spin` (continuous
  rotation), `bob` (sinusoidal oscillation), or `bounce` (real drop-and-rebound physics with
  energy loss per landing, not a sine wave). Server-driven repeated `updateSlot` calls, same
  pattern as the wave-demo in `norirobotics-mcp/scripts/spawn_nori_a3.py` and (verified
  independently) `overte-mcp`'s `overte_entity_animate` - this port reuses the identical
  closed-form bounce-physics math, not a reimplementation.
- Live-verified: spawned a real test box, read its rest position via `get_slot`, ran the
  bounce loop for 3s (26 ticks at ~10Hz, matching the requested tick rate), cleaned up with
  `destroy_slot`.
- First step of a planned backport of overte-mcp's session (2026-09-02) additions across
  resonite-mcp/godot-mcp/unity3d-mcp - fixture spawner, model/texture depot, backup/restore,
  and a live-world "nearby" search are still open; resonite-mcp already had more of the
  low-level primitives those would build on (`destroy_slot`, `set`/`get`, `import_texture`,
  `batch`) than overte-mcp did before that session, so the gap here is narrower than it looks.

## [1.2.0] — 2026-07-18/19 — Live Asset & Audio Pipeline, Webapp Audit 🎨🔊

### Added (rig/skeleton, 2026-07-19)
- `gltf_meshjson.py`: new `include_skinning` parameter decodes glTF
  `JOINTS_0`/`WEIGHTS_0` skinning and morph targets into `bones`/
  `blendshapes` for `import_mesh_json()`. Confirmed live against
  Nekomimi-chan's real VRM: 197 bones (VRM humanoid naming), 399
  blendshapes (VRM expression naming) — genuinely parsed, not synthetic.
- Confirmed live, error-driven (not guessed): the `bones` wire shape
  worked first try; `blendshapes` needed a `frames` wrapper
  (`{"name","frames":[{"weight","positionDeltas"}]}`) — the bare shape
  threw a server-side NullReferenceException. `SkinnedMeshRenderer.Bones`
  is a `SyncRefList<Slot>`, `.BlendShapeWeights` a `SyncFieldList<float>`
  (both confirmed via reflection, not assumed).
- Built and live-verified: 197 real bone Slots (correct parent-child
  hierarchy, one batch call) + a real `SkinnedMeshRenderer` (not the
  plain `MeshRenderer` a naive port would use) referencing all 197 bones
  in boneIndex order, replacing an earlier non-skinned renderer.
- Known gap, stated explicitly: blend-shape *deltas* were not pushed
  (399 shapes × 190k vertices each is a real payload-size problem,
  separate from the now-solved wire shape) — only the zeroed weights
  list exists so far. Whether the skeleton actually deforms the mesh on
  a bone rotation has not been tested yet.


- Found and permanently fixed a glTF-vs-Resonite coordinate-handedness
  mismatch that made every glTF/VRM-derived mesh invisible from any
  viewing angle (the mesh's own winding was 99.9% self-consistent with
  its stored normals — confirmed mathematically before the visual check —
  so the bug was in the target engine's convention, not the parser).
  `gltf_meshjson.py`'s `gltf_to_mesh_json()` now negates Z on every
  position/normal and reverses triangle winding by default (new
  `resonite_coordinate_fix: bool = True` parameter). Live-verified:
  Nekomimi-chan's full VRM mesh (190,111 vertices, 45,451 triangles)
  spawned into Sandra's own persistent Home session and confirmed
  visually visible.


- All 24 pre-existing `ruff` errors resolved for real, not suppressed
  blindly: 2 `B904` (missing `raise ... from`), 7 `RUF013` (implicit
  `Optional`), 6 `E501` (long lines wrapped without changing meaning),
  1 `S110` (silent `except: pass` → actual logging), 1 `E402` (justified,
  noqa — intentional circular-import avoidance, already documented in a
  comment), 1 `server.py` subprocess call rewritten to drop `shell=True`
  and resolve `tasklist`/`powershell.exe` via `shutil.which()` instead of
  bare names (fixes `S602`/`S607`/`S607` together, not just silenced).
  3 genuine `S104` ("binds all interfaces") suppressed with `# noqa` and
  justification — these are OSC servers that must accept LAN traffic
  from other devices, not a bug. Verified clean via `ruff check` re-run,
  a full-module import smoke test, and a functional call to the rewritten
  `is_resonite_running()` — not just re-running the linter and assuming.
  `tests/` was already clean; `web_sota/` biome findings (3,880 errors/
  2,804 warnings) are pre-existing frontend debt, untouched by tonight's
  Python-only changes, and out of scope for this pass.

### Added
- **`src/resonite_mcp/utils/gltf_meshjson.py`** — stdlib-only GLB/glTF parser
  (accessors/bufferViews/buffers: GLB BIN chunk, base64 data URI, external
  file references all handled) producing the exact vertex/submesh shape
  `import_mesh_json()` expects. No new dependency. Live-verified against all
  three free Marble Adventure `_collider.glb` fixtures (70k/49k/119k
  vertices) and against `Nekomimi-chan.vrm` (VRM is glTF-based under the
  hood — 190,111 vertices / 45,451 triangles, imported raw with no
  decimation needed).
- **`src/resonite_mcp/utils/stl_meshjson.py`** — binary + ASCII STL parser,
  stdlib only. Live-verified against Boomy's real chassis mesh
  (`base_link_X3.STL`, 69,192 triangles).
- **`src/resonite_mcp/utils/decimate_meshjson.py`** — vertex-clustering
  (grid-quantization) mesh decimation. Explicitly documented as NOT
  equivalent to Blender's quadric edge-collapse Decimate modifier — a
  no-Blender-available fallback, not the recommended production path for
  final assets. 83% triangle reduction demonstrated on Boomy's chassis.
- **`ResoniteLinkClient.import_audio_clip_file()`** and
  **`ResoniteLinkClient.spawn_audio()`** — new client methods completing
  the audio pipe: import a file → `StaticAudioClip` → `AudioClipPlayer` →
  `AudioOutput` (spatialized), with playback auto-triggered. Live-verified
  end to end with a stdlib-generated test tone.
- **UV_Coordinate wire shape corrected**: `uvs` is a **list** of coordinate
  objects (multi-UV-channel support), not a bare `{x,y}` dict as
  previously guessed — confirmed via a live server error, not assumed.

### Fixed
- Corrected the previously-unverified UV vertex-attribute shape in
  `gltf_meshjson.py` (see above) after a live import attempt returned a
  precise, actionable server error.

### Known limitations, stated explicitly (not silently shipped)
- The `UV_Coordinate` polymorphic type discriminator (needed for textured,
  non-solid-color materials) is still unknown after four live attempts
  (`UV_Coordinate`/`float2`/`uv`/`UVCoordinate` all rejected). `float2` is
  confirmed as a real Resonite type via `getTypeDefinition`, but that's not
  necessarily the same string the polymorphic slot expects. Needs upstream
  source inspection, not more guessing.
- VRM bones/blendshapes (skinning + expressions) are not implemented —
  `gltf_meshjson.py` reads static geometry only; `JOINTS_0`/`WEIGHTS_0` and
  morph targets are unparsed.
- `import_mesh_raw()` (binary WebSocket payload frame per
  `ImportMeshRawData.cs`) remains unimplemented — `import_mesh_json()` is
  the only working mesh-import path, proven up to 45k+ triangles without
  decimation.

### Webapp audit (`web_sota/`) — see `docs/WEBAPP_UPDATE_PLAN.md`
- Corrected a same-session mistake: an initial audit wrongly concluded the
  entire webapp backend was fictional, having checked
  `web_sota/backend/server.py` — a file that is **never actually
  launched**. The real server (`src/resonite_mcp/http_server.py`, started
  by `web_sota/start.ps1` via `cli.py`) implements 76 routes, most
  genuinely wired to the real `ResoniteLinkClient`.
- Found, while correcting the above: `Logging.tsx`'s `/api/logs*` +
  `ActivityLog` only exist in the unused `server.py` — genuinely broken in
  production, the reverse of what was first assumed.
- Found: `/api/sessions` is defined twice in `http_server.py` (line 584
  and 1089); the second (a real proxy to `api.resonite.com/sessions`) is
  dead code — FastAPI/Starlette always matches the first registration.
- Found: several pages call slightly-wrong paths for otherwise-real
  endpoints (`dashboard.tsx`/`status.tsx`'s `/api/resonite/launch` and
  `/api/start` vs. the real `/api/resonite/start`; `integrations.tsx`'s
  missing `resonite/` path segment and missing request body;
  `inventory.tsx`/`io.tsx`'s `/api/records` vs. the real
  `/api/resonite/inventory/list`).
- Found: `help.tsx` actively teaches the pre-2026-07-11 fictional
  ResoniteLink protocol (`ReadField`/`WriteField`/`GetNode`, "port 4242
  default", "v0.8.3") and repeats an unverified "65 tools" claim in three
  places — a content fix, not a missing feature.
- Confirmed fictional, admitted in the previous author's own code
  comments: `search.tsx` ("mock the search behavior"), `status.tsx` ("mock
  logs"). Confirmed with zero backend at all: `marketplace.tsx`
  (hardcoded array), `apps.tsx` (stub).
- Full phased remediation plan in `docs/WEBAPP_UPDATE_PLAN.md`.

### Added (fleet standard compliance, 2026-07-19)
- `/health`, `/api/health`, `/api/v1/health` now comply with
  `mcp-central-docs/standards/HEALTH_ENDPOINT_STANDARD.md`: real `version`
  (single source, `resonite_mcp.__version__`, was hardcoded `"1.0.0"`),
  `git_sha` (resolved once at import via `git rev-parse --short HEAD`,
  verified live against the actual repo — matched exactly, not assumed),
  `started_at`/`uptime_seconds`, `shutting_down` (flips on FastAPI's
  shutdown event), `transport`, and `port` (threaded through via env var
  from `cli.py`, since uvicorn imports the app by string path and can't
  pass args directly). `cli.py --version` also fixed to report the real
  version instead of a separately-hardcoded `"1.0.0"`.

---

## [1.1.0] — 2026-07-11 — Real ResoniteLink Protocol (0.13.1) 🔌

### BREAKING / Fixed
- **Complete ResoniteLink client rewrite.** The previous client implemented a
  fictional wire format (`ReadField`/`WriteField`/`GetNode`/`Reflect`/`Batch`
  with `type`/`id` keys) that never existed upstream and could not have talked
  to real Resonite. The client now speaks the verified real protocol
  (upstream 0.13.1): `$type` discriminators, `messageId`/`sourceMessageId`
  correlation, typed value wrappers (`{"$type":"float3","value":{...}}`),
  camelCase messages (`getSlot`, `addSlot`, `updateSlot`, `removeSlot`,
  `getComponent`, `addComponent`, `updateComponent`, `removeComponent`,
  `requestSessionData`, reflection family, `dataModelOperationBatch`).
  Verified against the reference C# implementation and upstream docs.
- Legacy client method names (`get_node`, `get_children`, `destroy_slot`,
  `reflect`, `batch`, `set_component_value`, `get_component_value`,
  `spawn_object`) are kept as compatibility mappings onto real messages.
- `write_field` and generic `import_file` now raise honest errors:
  per-field-ref writes and generic model/file import (VRM/GLB/FBX) **do not
  exist** in the real protocol. `/rl/world/import-vrm` and the upload-import
  endpoint return 501 not_implemented; `fleet_import_local_file` surfaces the
  same instead of fake-success.

### Added
- **LAN session discovery** (protocol 0.12.0): `discover_sessions()` listens on
  UDP 12512 for Resonite's session announcements — no more hardcoded port 4242
  guessing. New MCP tool `resonite_link_discover`, new HTTP `GET /rl/discover`.
- **Sync method calls** (protocol 0.11.0): `call_sync_method` /
  `call_static_sync_method` + MCP tool `resonite_link_call_method`.
- **Reflection**: `getComponentTypeList`, `getComponentDefinition` (with the
  0.9.0 type-reference change documented), `getTypeDefinition`,
  `getEnumDefinition`.
- New MCP tools: `resonite_link_get_slot` (depth/component-data control),
  `resonite_link_write_field` (component member writes with typed values).
- Value-encoding helpers `rl_value` / `rl_ref` / `rl_auto` (bool/int/float/
  string/float3/float4 auto-detection, explicit types for everything else).
- Session metadata on connect via `requestSessionData` (Resonite version,
  protocol version, unique session id).
- 22 wire-format regression tests (`tests/unit/test_resonite_link_protocol.py`)
  locking the real protocol shapes against drift.

### Changed
- `POST /rl/field` now requires `member` (component member writes);
  `GET /rl/field/{id}` returns full component data.
- `resonite_link_spawn` creates named/positioned slots; template-URL spawning
  returns not_implemented (does not exist in the protocol).

---

## [1.0.1] — 2026-07-11 — Standards & Upstream Audit 🔍

### Fixed
- **Version consistency**: `__init__.py` was stranded at 0.8.0 while `pyproject.toml` / MCPB manifest claimed 1.0.0. All three now read 1.0.1.
- **Changelog ordering**: entries were chronologically scrambled (duplicate 0.2.0, unreleased blocks interleaved mid-file). Rebuilt in proper reverse-chronological order; the 2026-02-23 webapp expansion re-numbered to 0.2.1 to resolve the duplicate.
- **Unicode safety**: removed em dash from `web_sota/start.ps1` (fleet Unicode Safety standard).
- **glama.json**: framework field updated from stale "FastMCP 2.13+" to "FastMCP 3.4+".
- **.gitignore**: now covers `htmlcov/`, `.coverage`, `.lancedb/`, `*.bak`, `*.py.backup`, `test_output.txt`.

### Changed
- **ResoniteLink protocol audit (docs)**: upstream ResoniteLink is now **0.13.1** (2026-03-11); this client targets **0.8.3**. Documented the gap in `resonite_link.py` and `docs/RESONITELINK_GUIDE.md` — new upstream capabilities (SyncPlayback 0.9.0, dictionaries 0.10.0, sync method calls 0.11.0, LAN session discovery 0.12.0, spherical harmonics 0.13.x) are **not yet implemented** here. Note: 0.9.0 changed member definition types to type references (affects `Reflect` responses) and 0.9.2 removed redundant type fields — wire-format review required before claiming 0.9+ support.
- ASSESSMENT.md refreshed with 2026-07-11 audit findings and improvement plan.

---

## [Unreleased backlog]

### Added (pending release)
- **vBot OSC receiver** — `GET /api/resonite/vbot/receiver`, `POST /api/resonite/vbot/test`, types `yahboom` / `mechazilla` / `godzilla` / `custom`; [docs/VBOT_OSC_RECEIVER.md](docs/VBOT_OSC_RECEIVER.md).
- Cross-links to teleoperator [VIRTUAL_TWINS](https://github.com/sandraschi/teleoperator-mcp/blob/master/docs/VIRTUAL_TWINS.md) and [VBOT_CREATIVE_TWINS](https://github.com/sandraschi/teleoperator-mcp/blob/master/docs/VBOT_CREATIVE_TWINS.md).

---

## [1.0.0] — 2026-06-14 — Tauri / CUA-NSIS Certification 📦

### Fixed
- Tauri build: resolved Rust crate conflict (brotli/alloc-no-stdlib)
- Tauri build: fixed PyInstaller path mismatch (hyphen to underscore in src dirs)
- Tauri build: fixed TypeScript errors (unused imports, useRef arg, import.meta.env)
- Tauri CORS: allow_origins includes tauri://localhost for WebView access

### Added
- CUA-NSIS: just cua-nsis-test recipe, smoke script, config
- CUA-NSIS: build.ps1 now copies NSIS installer to dist/
- CUA-NSIS: 11-phase smoke test (install, launch, WebView OCR, diagnostics, uninstall)
- CUA-NSIS: local certification — all 11 phases pass locally (2026-06-14)

---

## [0.6.0] — 2026-05-19 — Fleet Pipeline Fixes 🔗

### Fixed
- **Blender import port**: `resonite_import_blender` was hardcoded to port 10700 (virtualization-mcp). Fixed to call blender-mcp's actual `/tool` endpoint on port 10849 using `blender_export_presets` with the Resonite GLTF preset.
- **Version consistency**: `pyproject.toml` and `__init__.py` aligned (previously mismatched at 0.1.1 / 0.1.0).

### Changed
- `resonite_import_blender` now uses the canonical `/tool` MCP bridge endpoint instead of a non-existent `/api/export/file` path.

---

## [0.5.0] — 2026-05-07 — WorldLabs Import Pipeline 🚀

### Added

#### Backend (`http_server.py`, `integrations.py`)
- **WorldLabs import endpoint** — `POST /api/v1/import/worldlabs` accepts `splat_url`, `mesh_url`, `world_name`. Downloads files from the bridge proxy, imports via ResoniteLink, sends OSC confirmation. No mocks, no placeholders.
- **OSC receiver** — `POST /api/resonite/worldlabs/listen` starts a background OSC server on port 9001 listening for `/worldlabs/import`. Auto-triggers download + import pipeline.
- **OSC receiver stop** — `POST /api/resonite/worldlabs/stop` shuts down the listener.
- **ProtoFlux graph template** — `GET /api/resonite/worldlabs/protoflux` returns a JSON graph definition for OSCDataInput → StringSplit → HttpGet → ImportSplat.
- **Platform detection** — `GET /api/resonite/platform` detects Resonite installations (Steam/Standalone) and checks if currently running via psutil.
- **`python-osc` dependency** added for OSC server support.

#### Integration Tools (`integrations.py`)
- **`resonite_import_worldlabs_url()`** — real implementation: downloads SPZ/GLB from URL, imports via ResoniteLink, sends OSC. No mocks.
- **`resonite_import_blender()`** — real implementation: calls blender-mcp, downloads exported file, imports via ResoniteLink.
- **`resonite_avatar_unity()`** — real implementation: downloads avatar model, imports via ResoniteLink.

#### Documentation
- **WorldLabs import section** added to `PROTOFLUX_GUIDE.md` — step-by-step graph setup for OSC → import pipeline.
- **MARBLE_RESONITE_GUIDE.md** — updated with automated import flow using resonite-mcp + worldlabs-mcp.
- **Cross-server flow** documented: worldlabs-mcp (10865) → resonite-mcp (10979) → Resonite (OSC/ResoniteLink).

### Changed
- **`WorldLabsImportRequest`** model changed from `splat_id: str` to `splat_url: str, mesh_url: str, world_name: str` — accepts real URLs instead of fake IDs.
- **`import_worldlabs` endpoint** updated to use the new model and call the real download/import pipeline.

### Removed
- **All mock/placeholder code** removed from integration tools. `resonite_import_worldlabs` (the old stubbed version) replaced with `resonite_import_worldlabs_url`.

---

## [0.4.0] — 2026-03-08 — Presence Awareness & Onboarding 🛡️

### Added

#### Backend (`server.py`)
- **Presence Detection**: Robust detection for Resonite installations (Steam/Standalone) and active process monitoring.
- **Launch Command**: Added `POST /api/resonite/launch` to trigger Resonite startup via `steam://rungameid/2519830`.
- **Telemetry Expansion**: `health_check` and `/api/status` now broadcast `resonite_installed` and `resonite_running` flags.

#### Frontend (`web_sota/src/`)
- **`components/presence-gate.tsx`**: New high-level gate that locks MCP features when Resonite is inactive.
- **Onboarding Workflow**: Premium "Welcome" screen for first-time users or missing installations.
- **Start UI**: Interactive "Start Resonite" interface with live polling and state transitions.
- **Dashboard Telemetry**: Integrated presence status into the Hardware Matrix and added contextual alerts.

---

## [0.3.0] — 2026-03-07 — Local LLM Substrate (Glom On) 🧠

### Added

#### Backend (`llm.py`, `server.py`)
- **Glom On Substrate Detection**: Proactive probing for Ollama (port 11434) and LM Studio (port 1234).
- **Autonomous AI Synthesis**: Upgraded `ask_resonite` tool to perform local AI synthesis of documentation search results.
- **LLM Discovery API**: Added real-time discovery of available local LLM models and providers via `GET /api/llm-discovery`.
- **SOTA Health Check**: `health_check` now reports the active LLM substrate (e.g., "Ollama - qwen2.5-coder").

### Changed
- `ask_resonite`: Now prioritizes local compute for answering technical questions about Resonite.
- `get_status` / `health_check`: Enhanced with LLM diagnostic metadata.

---

## [0.2.1] — 2026-02-23 — Webapp Expansion 🌐

### Added

#### Backend (`http_server.py`)
- `GET /api/sessions` — Cloud API proxy to `api.resonite.com/sessions` with name/host/usercount filters
- `GET /api/sessions/{session_id}` — Cloud API proxy for individual session details
- `GET /rl/world/root` — ResoniteLink convenience shortcut to fetch root node
- `GET /rl/world/children/{slot_id}` — Fetch direct children of any slot by refId
- `GET /rl/world/node/{ref_id}` — Fetch full node details (position, scale, components)
- `GET /rl/world/vrm-files` — Scan `~/.avatarmcp/models/` for `.vrm` files
- `GET /rl/world/asset-files?category=` — Multi-category 3D asset scanner across 5 canonical dirs
- `POST /rl/world/import-vrm` — Delegate `importFile` message to ResoniteLink for asset injection
- `httpx` async client for outbound HTTP requests (Resonite Cloud API)

#### Frontend (`web_sota/src/`)
- **`pages/world.tsx`** — New World Inspector page:
  - Collapsible slot hierarchy tree (lazy-loaded children, depth-indent via Tailwind class map)
  - Inspector panel (position, scale, components for selected slot)
  - `AssetPanel` — multi-category injector with tab buttons (Avatars / Props / Furniture / Architecture / Misc)
  - Spawn-position XYZ inputs, target-slot display, real-time toast feedback
- **`App.tsx`** — `/world` route added
- **`components/layout/sidebar.tsx`** — World nav item with `TreePine` icon

### Fixed
- `aria-expanded` lint in `tools.tsx` and `help.tsx` (boolean → string coercion)
- CSS inline-style lint in `world.tsx` (replaced `style={{ paddingLeft }}` with Tailwind depth-class table)

### Changed
- README: updated FastMCP version badge, Python badge to 3.12+, added Webapp section, updated roadmap
- Canonical asset dirs documented: `~/.avatarmcp/models/` (avatars), `~/Documents/ResoniteAssets/{category}/` (props/furniture/architecture/misc)

---

## [0.1.0] — 2025-12-xx — Initial Release

### Added
- 31 MCP tools (FastMCP 2.13.1+ compliant at the time)
- Dual MCP stdio + FastAPI HTTP interface
- OSC communication (8 tools fully functional)
- Avatar control (3 tools)
- Session management (4 tools)
- ResoniteLink WebSocket client
- Plugin system scaffolding
- Inventory management scaffolding (mock responses)
