# Monitoring (Phase 4)

## Metrics

| Endpoint | Port | Purpose |
|----------|------|---------|
| `GET /api/metrics` | 10979 | Scrape via MCP HTTP |
| `GET /metrics` | 10979 | Same payload |
| Sidecar | 9079 | `PROMETHEUS_PORT` standalone scrape |

Enable/disable with `RESONITE_MCP_METRICS_ENABLED` (default `true`).

Install client:

```powershell
cd D:\Dev\repos\resonite-mcp
uv sync --extra monitoring
```

## Key series

- `resonite_mcp_tool_calls_total{tool,status}`
- `resonite_mcp_fleet_imports_total{operation,status}`
- `resonite_mcp_resonite_running`
- `resonite_mcp_resonite_link_connected`
- `resonite_mcp_execution_mode`

## JSON logs (Loki)

```powershell
$Env:RESONITE_MCP_LOG_FORMAT = "json"
$Env:RESONITE_MCP_LOG_DIR = "D:\Temp\logs\resonite-mcp"
uv run python -m resonite_mcp --port 10979
```

Fleet import audit records use logger `resonite_mcp.fleet_audit` with fields:
`operation`, `tool`, `status`, `duration_ms`, `imported`, `total`.

## Docker monitoring profile

```powershell
cd D:\Dev\repos\resonite-mcp
docker compose --profile monitoring up -d
```

| Service | Host port |
|---------|-----------|
| Prometheus | 9093 |
| Grafana | 3003 (admin/admin) |
| Loki | 3103 |
