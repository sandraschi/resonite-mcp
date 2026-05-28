# Competitive Analysis — Resonite MCP Ecosystem

Last updated: 2026-05-28 (Agent Lab planning)

Compares **sandraschi/resonite-mcp** with other social VR / world-building MCP and automation projects.

## Summary

| Project | Scale | Architecture | Standout |
|---------|-------|--------------|----------|
| ResoniteLink + OSC (official) | Native | WebSocket + UDP | Live slot/component control |
| Generic VRChat MCP servers | Various | OSC-only | Platform-specific, no Resonite depth |
| Manual Resonite GUI | Human | In-world editing | Precision, no agent loop |
| **sandraschi/resonite-mcp** | 31+ tools | FastMCP 3.2 + dual transport | RAG guides, presence gate, fleet integrations |

## Where we lead

- **Dual protocol** — ResoniteLink WebSocket + OSC fallback
- **Presence awareness** — install detection, launch orchestration, webapp gate
- **Cross-MCP integrations** — WorldLabs, Blender, Unity (existing) + fleet portmanteau (Phase 1)
- **RAG + local LLM** — `ask_resonite`, `search_guides`
- **Fleet webapp** — dashboard on :10978/:10979

## Gaps we are closing (roadmap)

See [ROADMAP.md](ROADMAP.md).

| Gap | Our response | Phase |
|-----|--------------|-------|
| Inkscape UI vector handoff | `resonite_fleet` + inkscape `stage_resonite_ui` | 1 (done) |
| Agent execution mode guidance | `resonite_fleet` → `execution_mode` | 1 (done) |
| Webapp Agent Lab page | `/agent-tools` tabs | 2 |
| avatar-mcp VRM HTTP handoff | fleet VRM batch | 3 |
| Docker / Prometheus / smoke | telemetry + GHCR | 4 |
| Marble / fab art overlays | worldlabs + inkscape fab | 5 |
| Inventory live API + voice | polish for 1.0.0 | 6 |

## Fleet pipeline role

```text
inkscape-mcp (UI vectors) → resonite-mcp (in-world UI slots)
blender-mcp (VRM/GLB)     → resonite-mcp (avatar/props)
gimp-mcp (textures)       → resonite-mcp (material QA + import)
worldlabs-mcp (splats)    → resonite-mcp (environment)
```

## References

- [ROADMAP.md](ROADMAP.md)
- [inkscape-mcp ROADMAP](https://github.com/sandraschi/inkscape-mcp/blob/master/docs/ROADMAP.md)
- [ResoniteLink protocol](https://github.com/Yellow-Dog-Man/ResoniteLink)
