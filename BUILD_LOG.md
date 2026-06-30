# Resonite MCP — Build Log

## 2026-06-25 — Fleet Compliance Sprint

### Changes
- **native/build.ps1**: Fixed dangling `} -ForegroundColor Green` syntax error.
  Added API_BASE port gate, >=5 MB PyInstaller size gate, frozen binary smoke
  test. Bundles `.env.example` instead of `.env` (API key leak prevention).
- **native/tauri.conf.json**: `targets` changed from `"all"` to `["nsis"]`.
  Resources changed from `resources/.env` to `resources/.env.example`.
- **native/windows/hooks.nsh**: Fixed process names (`resonite-backend.exe` →
  `resonite-mcp-backend.exe`, `resonite-native.exe` → `resonite-mcp-native.exe`).
  Added `UninstallPrevious` macro. Increased `Sleep 2000` → `3000`.
- **pyproject.toml**: Added `prefab-ui>=0.14.0` to core dependencies.
- **.env.example**: Created at repo root with all documented env vars.
- **llms.txt / llms-full.txt**: Created LLM documentation files.
- **src/resonite_mcp/tools/resonite_link.py**: Surfaced 8 low-level client
  methods as MCP tools (read_field, write_field, get_node, get_children,
  add_slot, add_component, destroy_slot, reflect, batch).
- **src/resonite_mcp/tools/rest_api.py**: Added cloud variables CRUD tools
  and friends/contacts tools (`resonite_friends_list`, `resonite_friend_requests`,
  `resonite_friend_presence`).
- **src/resonite_mcp/tools/vbot.py**: New VBOT tools module wrapping existing
  OSC receiver spec (spawn, move, head, stop, list_types).
- **src/resonite_mcp/tools/prefab_cards.py**: Prefab App tools for dashboard
  status card and inventory list card.

### Build Result
- (pending first build after changes)
