# resonite-mcp — Development

Moved out of README.md 2026-07-18 per fleet README_STRUCTURE standard.

## Project Structure

```
resonite-mcp/
  src/resonite_mcp/
    server.py            # Main MCP server
    resonite_link.py     # ResoniteLink protocol client (0.13.1)
    http_server.py       # FastAPI HTTP server
    tools/               # Tool modules (session, avatar, inventory, fleet, ...)
    plugins/             # Plugin system (OSC extensions, ProtoFlux helpers)
  tests/
    unit/                # incl. test_resonite_link_protocol.py (22 wire-format tests)
    integration/
  web_sota/              # Dashboard webapp (port 10978)
  docs/                  # This folder
  assets/prompts/
```

Note: `mcp-server/` at repo root is a legacy duplicate tree — treat
`src/resonite_mcp/` as canonical (cleanup candidate).

## Workflow

```powershell
just              # interactive recipe dashboard
just bootstrap    # install deps
just dev          # dev server
just lint / fix   # ruff
just mcpb-pack    # Claude Desktop bundle -> dist/*.mcpb
just build-all    # Tauri NSIS installer
```

## Tests

```bash
pytest                        # all
pytest tests/unit/            # wire-format regression suite lives here
pytest --cov=resonite_mcp --cov-report=html
python scripts/fleet_e2e_smoke.py --live      # live HTTP chain
# strict fleet E2E: fleet_e2e_strict.py / CI --strict-fleet
```

Live ResoniteLink E2E is an operator-in-the-loop test (needs a hosted session
with Link enabled) — first successful run 2026-07-18, see RESONITELINK_GUIDE.

## Quality stack

Ruff (T201: no prints in handlers), Biome for the webapp, hardened
stdout/stderr isolation for JSON-RPC, bandit + safety audits, justfile-driven.

## Contributing

Branch → tests → `pytest` green → docs updated → PR. Type hints and docstrings
on all public functions. Per fleet standard: no GitHub Actions on private
repos — quality gates run locally (`just check`).
