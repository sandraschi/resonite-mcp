# Onboarding — resonite-mcp

Get from zero to a talking Resonite bridge in ~10 minutes.

## What this is

MCP + HTTP bridge that lets AI agents control the Resonite social-VR platform:
avatars, worlds/sessions, inventory, ProtoFlux scripts, OSC, and asset import
(WorldLabs/Blender/Unity). You do NOT need VR hardware to run the server, but
live world control needs a running Resonite client.

## Prerequisites

- Python 3.12+, `uv` — `uv sync --group dev`
- Node 22+ (npm; webapp at `web_sota/`)
- Optional: Resonite (Steam id 2519830) for live control; Ollama (:11434) for chat

## Sanity check

```powershell
uv run python -m resonite_mcp --port 10979
Invoke-WebRequest http://127.0.0.1:10979/health -UseBasicParsing  # status ok
```

Then `./web_sota/start.ps1` — dashboard on :10978, backend :10979.

## Configuration

Copy `.env.example` to `.env`. Keys that matter:

| Variable | Purpose |
|---|---|
| `RESONITE_TOKEN` | Resonite cloud API auth (inventory/REST tools) |
| `RESONITE_OSC_HOST/PORT` | OSC target, default 127.0.0.1:9000 |
| `MCP_PORT/MCP_HOST` | Backend bind, default 127.0.0.1:10979 |

No account or wrappee install is needed for guides/OSC-simulation paths; live
session tools need Resonite running and reachable.

## Pitfalls

- Ports 10978/10979 must be free; `just kill-ports` clears zombies.
- Chat page needs Ollama on :11434 (direct fetch today; backend proxy planned).
- Companion Resonite mods (issue #3) are OPTIONAL and not required.
