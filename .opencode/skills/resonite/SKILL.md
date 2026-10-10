---
name: resonite
description: Control Resonite VR via MCP — OSC, avatars, worlds, inventory, ProtoFlux
---

# Resonite MCP skill

Drive the Resonite social-VR platform through this repo's MCP + HTTP surface.

## Before starting work

- `GET http://127.0.0.1:10979/health` — backend up? (`status: ok`)
- `POST /api/v1/tool` `{tool: search_guides}` / `{tool: ask_resonite}` — live help
- Read `docs/assess-reports/2026-10-10.md` for known gaps (chat proxy, transport)

## Key tools

`search_guides`, `ask_resonite`, `agentic_plan_execute`, `health_check` (MCP);
`/api/resonite/*`, `/api/osc/*`, `/api/resonite/inventory/*` (HTTP).

## At end of work

`uv run ruff check src/` and `uv run pytest tests/ -q` must pass.
