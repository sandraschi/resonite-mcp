
## [Unreleased] — 2026-06-14

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

# Changelog

All notable changes to `resonite-mcp` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- **vBot OSC receiver** — `GET /api/resonite/vbot/receiver`, `POST /api/resonite/vbot/test`, types `yahboom` / `mechazilla` / `godzilla` / `custom`; [docs/VBOT_OSC_RECEIVER.md](docs/VBOT_OSC_RECEIVER.md).
- Cross-links to teleoperator [VIRTUAL_TWINS](https://github.com/sandraschi/teleoperator-mcp/blob/master/docs/VIRTUAL_TWINS.md) and [VBOT_CREATIVE_TWINS](https://github.com/sandraschi/teleoperator-mcp/blob/master/docs/VBOT_CREATIVE_TWINS.md).

---

## [0.2.0] — 2026-05-19 — Fleet Pipeline Fixes 🔗

### Fixed
- **Blender import port**: `resonite_import_blender` was hardcoded to port 10700 (virtualization-mcp). Fixed to call blender-mcp's actual `/tool` endpoint on port 10849 using `blender_export_presets` with the Resonite GLTF preset.
- **Version consistency**: `pyproject.toml` and `__init__.py` now both read `0.2.0` (previously mismatched at 0.1.1 / 0.1.0).

### Changed
- `resonite_import_blender` now uses the canonical `/tool` MCP bridge endpoint instead of a non-existent `/api/export/file` path.

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

## [0.2.0] — 2026-02-23 — Webapp Expansion 🌐

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
- README: updated FastMCP version badge to 2.14.3+, Python badge to 3.12+, added Webapp section, updated roadmap
- Canonical asset dirs documented: `~/.avatarmcp/models/` (avatars), `~/Documents/ResoniteAssets/{category}/` (props/furniture/architecture/misc)

---

## [0.1.0] — 2025-12-xx — Initial Release

### Added
- 31 MCP tools (FastMCP 2.13.1+ compliant)
- Dual MCP stdio + FastAPI HTTP interface
- OSC communication (8 tools fully functional)
- Avatar control (3 tools)
- Session management (4 tools)
- ResoniteLink WebSocket client
- Plugin system scaffolding
- Inventory management scaffolding (mock responses)

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



