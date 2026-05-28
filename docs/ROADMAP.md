# Improvement Roadmap

Phased Agent Lab plan for **resonite-mcp**, aligned with inkscape-mcp / gimp-mcp / blender-mcp fleet playbooks.

**Current baseline:** v0.4.x — OSC, ResoniteLink, presence gate, WorldLabs/Blender/Unity integrations.

## Phase 1 — Fleet handoff and execution guidance (0.5.0)

**Status: complete (v0.5.0)**

| Item | Tool / module |
|------|----------------|
| Fleet preset catalog | `resonite_fleet` → `list_presets` |
| Hands-In vs Hands-Off guidance | `resonite_fleet` → `execution_mode` |
| Inkscape UI staging import | `resonite_fleet` → `pull_inkscape_ui`, `import_staged_assets` |
| Blender / GIMP bridge | `import_blender_asset`, `import_gimp_texture` |
| Fleet E2E smoke | `scripts/fleet_e2e_smoke.py --offline --strict` |
| Phase 1 tests | `tests/unit/test_phase1_fleet_tools.py` |

### CI offline smoke

```powershell
cd D:\Dev\repos\resonite-mcp
$Env:PYTHONPATH = "src"
uv run python scripts/fleet_e2e_smoke.py --offline --strict
```

## Phase 2 — Webapp Agent Lab (0.6.0)

**Status: complete (v0.6.0)**

| Item | Tool / module |
|------|----------------|
| Webapp `/agent-tools` page | tabbed Agent Lab UI (runtime, fleet, staging, pipeline) |
| `POST /api/v1/tool` proxy | `http_server.py` REST bridge |
| Staging gallery | localStorage snapshots from `list_staging` |
| Live inkscape → resonite HTTP E2E | `utils/fleet_e2e_live.py`, `--live` smoke flag |
| Phase 2 tests | `tests/unit/test_phase2_tools.py` |

### Live HTTP smoke (both servers on localhost)

```powershell
cd D:\Dev\repos\resonite-mcp
$Env:PYTHONPATH = "src"
uv run python scripts/fleet_e2e_smoke.py --live --strict
```

## Phase 3 — Avatar and VRM pipeline (0.7.0)

| Item | Tool / module |
|------|----------------|
| avatar-mcp HTTP handoff | VRM/thumbnail import |
| blender-mcp VRM export staging | `resonite_fleet` VRM batch |
| ProtoFlux avatar parameter maps | preset manifests |

## Phase 4 — Telemetry, Docker, monitoring (0.8.0)

| Item | Tool / module |
|------|----------------|
| Prometheus metrics | HTTP `/metrics` |
| Docker + GHCR image | headless ResoniteLink sidecar pattern |
| Structured JSON logs | fleet import audit trail |

## Phase 5 — World Labs and Marble worlds (0.9.0)

| Item | Tool / module |
|------|----------------|
| Marble splat batch import | extend `resonite_import_worldlabs_url` |
| Gazebo schematic overlays | inkscape fab art → resonite UI slots |
| Robotics fab path visualization | staged DXF references |

## Phase 6 — Social VR polish (1.0.0)

| Item | Tool / module |
|------|----------------|
| Inventory mock → live API | when Resonite exposes stable inventory HTTP |
| Voice command hooks | local LLM + OSC macro portmanteau |
| Strict fleet E2E in CI | inkscape → gimp → blender → resonite chain |

## Fleet pipeline role

```text
inkscape-mcp (SVG UI) → resonite_fleet (import_staged_assets)
blender-mcp (GLB/VRM) → resonite_fleet (import_blender_asset)
gimp-mcp (textures)   → resonite_fleet (import_gimp_texture)
worldlabs-mcp (splats) → resonite_import_worldlabs_url
```
