# Changelog

All notable changes to `resonite-mcp` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
