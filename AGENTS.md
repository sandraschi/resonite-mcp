# Resonite MCP — AGENTS.md

**FastMCP 3.2+** | **Python 3.12+** | **Ports: 10978/10979**

## Overview

Resonite MCP Server provides natural language control of the [Resonite](https://resonite.com) social VR platform. It bridges AI agents (Claude Desktop, Cursor, etc.) to Resonite via OSC protocol, ResoniteLink WebSocket, and the Resonite Cloud REST API.

## Quick Start

```bash
uv sync
uv run python -m resonite_mcp --port 10979
# Frontend at http://localhost:10978 (via web_sota/start.ps1)
```

## Architecture

| Layer | Tech | Port |
|-------|------|------|
| React frontend | Vite + React 19 + Tailwind | 10978 |
| FastAPI backend | FastAPI + FastMCP 3.2 | 10979 |
| MCP transport | stdio (default) / HTTP / SSE | — |
| OSC protocol | UDP to Resonite | 9000 |
| ResoniteLink | WebSocket to Resonite | 4242 |

## Tool Categories

- **OSC** (8 tools): send/receive/monitor OSC messages
- **Session** (4 tools): start/stop worlds and sessions
- **Avatar** (3 tools): load avatars, set parameters, execute ProtoFlux
- **Inventory** (7 tools): list/search/spawn/upload/delete/share items
- **Plugin** (6 tools): load/unload/discover plugins
- **REST API** (6 tools): Resonite cloud API bridge
- **ResoniteLink** (4 tools): WebSocket world manipulation
- **System** (2 tools): help, status
- **Integrations** (3 tools): WorldLabs/Blender/Unity asset import
- **Agentic** (1+): plan/execute/reason via ctx.sample()

Total: ~44 tools + 5 prompt templates

## Key Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `MCP_TRANSPORT` | stdio | Transport mode |
| `MCP_PORT` | 10979 | Backend bind port |
| `MCP_HOST` | 127.0.0.1 | Backend bind host |
| `RESONITE_OSC_HOST` | 127.0.0.1 | Resonite OSC host |
| `RESONITE_OSC_PORT` | 9000 | Resonite OSC port |
| `RESONITE_TOKEN` | — | Resonite cloud API auth |

## Agentic Features (FastMCP 3.2+)

- `--agentic` CLI flag enables CodeMode BM25 skill discovery
- `agentic_plan_execute()` uses `ctx.sample()` for autonomous multi-step reasoning
- 5 prompt templates for common workflows: session setup, avatar animation, world exploration, inventory management, cross-MCP integration

## Fleet Integration

Apps catalog provides cross-MCP navigation to 12+ fleet services. MCP Bridge (ProxyProvider) supports federation with other MCP servers via `MCP_BRIDGE_URLS` env var.

## Standards Compliance

- **Ports**: 10978/10979 (fleet range 10700-11000)
- **Startup**: `Clear-Port` → `uv sync` → health check → Vite
- **Lint**: Ruff (Python) + Biome (TypeScript)
- **CI**: GitHub Actions (uv, ruff, mypy, pytest)

Install docs: follow mcp-central-docs/standards/AGENT_INSTALL_REFERENCE.md
