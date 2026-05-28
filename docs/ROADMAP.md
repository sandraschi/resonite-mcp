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

**Status: complete (v0.7.0)**

| Item | Tool / module |
|------|----------------|
| VRM staging scan | `resonite_fleet` → `list_vrm_staging` |
| Batch VRM import | `resonite_fleet` → `import_vrm_batch` |
| Blender VRM export staging | `resonite_fleet` → `pull_blender_vrm` |
| avatar-mcp handoff | `resonite_fleet` → `pull_avatar_vrm` |
| ProtoFlux parameter maps | `list_protoflux_presets`, `utils/protoflux_avatar_presets.py` |
| Agent Lab VRM tab | webapp `/agent-tools` |
| Phase 3 tests | `tests/unit/test_phase3_tools.py` |

## Phase 4 — Telemetry, Docker, monitoring (0.8.0)

**Status: complete (v0.8.0)**

| Item | Tool / module |
|------|----------------|
| Prometheus metrics | `GET /metrics`, `GET /api/metrics`, sidecar `:9079` |
| Tool + fleet counters | `utils/telemetry.py` |
| Structured JSON logs | `utils/structured_logging.py` |
| Fleet import audit trail | `utils/fleet_audit.py`, `fleet_tools._finalize` |
| Docker + GHCR | `Dockerfile`, `docker-compose.yml` |
| Monitoring stack | `monitoring/` (Prometheus 9093, Grafana 3003, Loki 3103) |
| Smoke test | `scripts/smoke_test.py` |
| Phase 4 tests | `tests/unit/test_phase4_tools.py` |

## Phase 5 — World Labs and Marble worlds (0.9.0)

**Status: complete (v0.9.0)**

| Item | Tool / module |
|------|----------------|
| Marble splat batch import | `resonite_fleet` → `import_worldlabs_batch` |
| Marble staging scan | `resonite_fleet` → `list_marble_staging` |
| Inkscape fab art overlays | `resonite_fleet` → `pull_inkscape_fab` |
| Robotics DXF references | staged via `pull_inkscape_fab` → `marble/dxf` |
| Marble pipeline | `resonite_fleet` → `run_marble_pipeline` |
| Staging helpers | `utils/marble_staging.py` |
| Agent Lab Marble tab | webapp `/agent-tools` |
| Phase 5 tests | `tests/unit/test_phase5_tools.py` |

## Phase 6 — Social VR polish (1.0.0)

**Status: complete (v1.0.0)**

| Item | Tool / module |
|------|----------------|
| Inventory mock → live adapter | `utils/inventory_adapter.py`, `inventory_status` |
| Voice command hooks | `resonite_voice` portmanteau (`list_macros`, `parse_command`, `send_macro`) |
| Strict fleet E2E in CI | `utils/fleet_e2e_strict.py`, `--strict-fleet` smoke flag |
| HTTP bridge voice tool | `POST /api/v1/tool` → `resonite_voice` |
| Phase 6 tests | `tests/unit/test_phase6_tools.py` |

### CI strict fleet smoke

```powershell
cd D:\Dev\repos\resonite-mcp
$Env:PYTHONPATH = "src"
uv run python scripts/fleet_e2e_smoke.py --strict-fleet --strict
```

## Fleet pipeline role

```text
inkscape-mcp (SVG UI) → resonite_fleet (import_staged_assets)
blender-mcp (GLB/VRM) → resonite_fleet (import_blender_asset)
gimp-mcp (textures)   → resonite_fleet (import_gimp_texture)
worldlabs-mcp (splats) → resonite_import_worldlabs_url
```
