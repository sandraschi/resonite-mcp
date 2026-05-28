# resonite-mcp (MCPB bundle)

Claude Desktop / MCPB bundle for **stdio** MCP transport.

## Runtime

- Entry: `python -m resonite_mcp --stdio`
- Requires Python 3.12+ and dependencies from the host environment (`uv sync` in the dev repo).
- HTTP dashboard mode (`web_sota/`, port 10979) is **not** included in this bundle.

## Fleet staging defaults

| Path | Purpose |
|------|---------|
| `D:/Temp/fleet_pipeline/resonite_fleet` | General fleet staging |
| `D:/Temp/fleet_pipeline/inkscape_sim_art/resonite_ui` | Inkscape UI vectors |
| `D:/Temp/fleet_pipeline/resonite_fleet/models` | VRM models |
| `D:/Temp/fleet_pipeline/resonite_marble` | Marble / World Labs splats |

## Build (from repo root)

```powershell
just mcpb-pack
```

Output: `dist/resonite-mcp-v{version}.mcpb`
