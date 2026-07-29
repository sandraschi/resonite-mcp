# Docker (Phase 4)

Resonite and ResoniteLink stay on the **host**. The container runs the MCP HTTP API and metrics sidecar only.

## Quick start

```powershell
cd D:\Dev\repos\resonite-mcp
docker compose up resonite-mcp
```

MCP: `http://127.0.0.1:10979`
Metrics sidecar: `http://127.0.0.1:9079/metrics`

## With monitoring stack

```powershell
docker compose --profile monitoring up -d
```

## Environment

| Variable | Default | Notes |
|----------|---------|-------|
| `MCP_PORT` | 10979 | HTTP API |
| `PROMETHEUS_PORT` | 9079 | Metrics sidecar |
| `RESONITE_LINK_HOST` | host.docker.internal | ResoniteLink on host |
| `RESONITE_LINK_PORT` | 4242 | ResoniteLink WebSocket |
| `RESONITE_MCP_LOG_FORMAT` | json | Loki-friendly logs |
| `RESONITE_MCP_LOG_DIR` | /app/logs | Promtail volume |

## GHCR

Image: `ghcr.io/sandraschi/resonite-mcp:latest`
Published via `.github/workflows/docker-publish.yml`.
