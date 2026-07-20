# resonite-mcp

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
  <img src="https://img.shields.io/badge/ResoniteLink-0.13.1_live--verified-22c55e?style=flat-square" alt="ResoniteLink live-verified">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT"></a>
</p>

**Natural-language control of the Resonite social VR platform** — read and
write a live world's data model over the official **ResoniteLink** protocol,
with OSC streaming, a World Inspector webapp, and fleet bridges to Blender,
Marble/World Labs, and the VRM avatar depot.

> **Live-verified 2026-07-18**: session discovery, connect, data-model read,
> and slot write confirmed against a running Resonite session
> (2026.7.14.913, protocol 0.13.1.0) — zero client fixes needed.

#### The Miko's Digital Shrine

In the spirit of kami and miko — this MCP server serves as a bridge between
human creators and the digital spirits of virtual worlds. The kawaii and
clever miko tends the shrines of code, ensuring the kami of creation
flow freely through our digital spaces.

## What it does

- **ResoniteLink first** *(primary path)*: official WebSocket JSON protocol
  (Resonite 2026.1.8.6+) — slot & component CRUD, reflection, sync method
  calls, batching, LAN session discovery (UDP 12512). See
  [RESONITELINK_GUIDE](docs/RESONITELINK_GUIDE.md) for the honest capability
  table (short version: no generic VRM/GLB import in the protocol; geometry
  travels as mesh-JSON — client wrapping of asset imports in progress).
- **World Inspector**: live scene-graph browser in the webapp — traverse
  slots, inspect components, edit fields.
- **OSC streaming** *(secondary)*: high-frequency parameter streaming
  (avatar parameters etc.), 8 tools, bidirectional.
- **Fleet bridges**: Marble/World Labs batch import staging, VRM staging from
  blender-mcp / avatar-mcp, inkscape overlays, voice macros
  (`resonite_fleet`, `resonite_voice` portmanteaus).
- **Session & presence**: cloud session browser, install/launch detection
  with onboarding gate, avatar + world management tools.
- **Dual interface**: MCP stdio for Claude Desktop + FastAPI HTTP
  (`/docs`, Prometheus `/metrics`).

## Quick start

```powershell
git clone https://github.com/sandraschi/resonite-mcp
cd resonite-mcp
just              # interactive dashboard; then: just bootstrap, just serve
```

Claude Desktop (`claude_desktop_config.json`):

```json
"mcpServers": {
  "resonite-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/resonite-mcp", "run", "resonite-mcp"]
  }
}
```

Or bundle it: `just mcpb-pack` → `dist/resonite-mcp-v1.1.0.mcpb`.

## How it runs (honest wrapper notes)

- You need the **Resonite client (or headless) running and hosting a session**;
  only the host can enable ResoniteLink (Dashboard → Session → Settings →
  Enable ResoniteLink). Headless: `enableResoniteLink <port>`.
- **Find the port via discovery** (`resonite_link_discover`, UDP 12512) — the
  dashboard's displayed port was wrong in live testing.
- Desktop mode is fine for everything; VR is optional.
- ResoniteLink upstream is **beta**: breaking changes possible. This client
  pins protocol 0.13.1 with 22 wire-format regression tests.

## Webapp (port 10978)

`.\web_sota\start.ps1` → Dashboard, Sessions browser, World Inspector,
Presence Gate, ResoniteLink monitor, Avatar, OSC, Dev Tools.

## Documentation

| Doc | What |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | High-level system architecture and data flows |
| [INSTALL.md](INSTALL.md) | All install paths |
| [docs/TOOLS.md](docs/TOOLS.md) | Tool & HTTP API reference |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | Env vars, Resonite setup, asset dirs |
| [docs/RESONITELINK_GUIDE.md](docs/RESONITELINK_GUIDE.md) | Protocol capabilities + live-verification record |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Dev setup, tests, quality stack |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common failures, debug mode |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Agent Lab phases (1–6 done, v1.1.0) |
| [MARBLE_RESONITE_GUIDE.md](MARBLE_RESONITE_GUIDE.md) | World Labs → Resonite pipeline |
| [PROTOFLUX_GUIDE.md](PROTOFLUX_GUIDE.md) + [hands-on](PROTOFLUX_HANDS_ON_GUIDE.md) | Visual programming |
| [BEGINNERS_GUIDE.md](BEGINNERS_GUIDE.md) · [RESONITE_ACCESS_GUIDE.md](RESONITE_ACCESS_GUIDE.md) | New to Resonite |

## Status

v1.1.0 — real ResoniteLink wire format (0.13.1), live-verified 2026-07-18.
Agent Lab phases 1–6 complete. Known honest gaps: asset-import messages not
yet wrapped as first-class client methods; some inventory/plugin tools still
adapter/mock-backed (`RESONITE_INVENTORY_MODE`); tool inventory re-audit
pending in [docs/TOOLS.md](docs/TOOLS.md). Current mission: **Nekomimi-chan's
Resonite home** — see mcp-central-docs `projects/RESONITE_HOME_NEKOMIMI_PLAN.md`.

## Acknowledgments

[Resonite](https://resonite.com/) & [Yellow Dog Man Studios](https://yellowdogman.com/) —
incl. the official [ResoniteLink](https://github.com/Yellow-Dog-Man/ResoniteLink)
protocol · [FastMCP](https://github.com/PrefectHQ/fastmcp) ·
[python-osc](https://pypi.org/project/python-osc/)

MIT licensed. Made with care for the Resonite community.
