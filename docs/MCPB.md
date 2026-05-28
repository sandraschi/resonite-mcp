# MCPB packaging

Fleet-standard Claude Desktop bundle for **stdio** MCP transport.

## Layout

```text
mcp-server/
  manifest.json
  README.md
  assets/icon.svg
  assets/prompts/{system.md,user.md,examples.json}
  src/resonite_mcp/    # synced from src/resonite_mcp/
dist/
  resonite-mcp-v{version}.mcpb
```

Source of truth remains `src/resonite_mcp/`. Run sync before every pack.

## Build

Prerequisites: Node.js (`npx`), Python 3.12+, `uv sync`.

```powershell
cd D:\Dev\repos\resonite-mcp
just mcpb-pack
```

Or step-by-step:

```powershell
uv run python tools/sync_mcpb_src.py
uv run python tools/pack_mcpb.py
```

Validate only:

```powershell
npx -y @anthropic-ai/mcpb@latest validate mcp-server/manifest.json
```

## Install in Claude Desktop

1. Build `dist/resonite-mcp-v1.0.0.mcpb`
2. Install via Claude Desktop MCPB UI or drag-and-drop per Anthropic docs
3. Configure OSC host/port in user_config if not using defaults

## Exclusions

See `.mcpbignore` — `web_sota/`, tests, Docker/monitoring, and fleet metadata are excluded from the bundle.

## References

- `D:/Dev/repos/mcp-central-docs/standards/MCPB_PACKAGING_STANDARDS.md`
- inkscape-mcp `docs/MCPB.md` (same sync + pack pattern)
