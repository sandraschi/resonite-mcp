# Competitive Analysis — Resonite MCP Ecosystem

Last updated: 2026-05-28 (Agent Lab v1.0.0)

Compares **sandraschi/resonite-mcp** with other social VR / world-building MCP and automation projects.

## Summary

| Project | Scale | Architecture | Standout |
|---------|-------|--------------|----------|
| ResoniteLink + OSC (official) | Native | WebSocket + UDP | Live slot/component control |
| Generic VRChat MCP servers | Various | OSC-only | Platform-specific, no Resonite depth |
| Manual Resonite GUI | Human | In-world editing | Precision, no agent loop |
| **sandraschi/resonite-mcp** | 31+ tools | FastMCP 3.2 + dual transport | RAG guides, presence gate, Agent Lab fleet |

## Where we lead

- **Dual protocol** — ResoniteLink WebSocket + OSC fallback
- **Presence awareness** — install detection, launch orchestration, webapp gate
- **Agent Lab fleet** — inkscape → blender → gimp → avatar → marble → resonite orchestration
- **RAG + local LLM** — `ask_resonite`, `search_guides`, voice command refine
- **Fleet webapp** — Agent Lab on :10978/:10979, Prometheus sidecar :9079
- **MCPB bundle** — stdio Claude Desktop package via `just mcpb-pack`

## Roadmap gaps — status

See [ROADMAP.md](ROADMAP.md). Agent Lab Phases 1–6 are **complete**.

| Gap | Response | Status |
|-----|----------|--------|
| Inkscape UI handoff | `resonite_fleet` + inkscape staging | done |
| Execution mode guidance | `execution_mode` | done |
| Webapp Agent Lab | `/agent-tools` tabs | done |
| VRM / avatar pipeline | batch import, ProtoFlux presets | done |
| Telemetry / Docker | Prometheus, GHCR, audit logs | done |
| Marble / fab art | worldlabs batch, DXF refs | done |
| Inventory + voice | adapter + `resonite_voice` | done (live inventory pending Resonite OSC) |

## Post-1.0 differentiation

- **Strict fleet E2E** in CI (offline mocks; live chain manual)
- **Cross-fleet portmanteau** vs single-purpose OSC wrappers
- **Inventory adapter** mock/live/auto vs hard-coded mocks only

## Fleet pipeline role

```text
inkscape-mcp (UI vectors) → resonite-mcp (in-world UI slots)
blender-mcp (VRM/GLB)     → resonite-mcp (avatar/props)
gimp-mcp (textures)       → resonite-mcp (material QA + import)
worldlabs-mcp (splats)    → resonite-mcp (environment)
avatar-mcp (VRM)          → resonite-mcp (avatar staging)
```

## References

- [ROADMAP.md](ROADMAP.md)
- [MCPB.md](MCPB.md)
- [inkscape-mcp ROADMAP](https://github.com/sandraschi/inkscape-mcp/blob/master/docs/ROADMAP.md)
- [ResoniteLink protocol](https://github.com/Yellow-Dog-Man/ResoniteLink)
