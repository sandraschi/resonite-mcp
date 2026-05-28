# resonite-mcp HTTP MCP server (Resonite client runs on HOST).
#
# Build:
#   docker build --target production -t ghcr.io/sandraschi/resonite-mcp:local .
#
# Run:
#   docker run --rm -p 10979:10979 -p 9079:9079 ghcr.io/sandraschi/resonite-mcp:local

FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=10979
ENV PROMETHEUS_PORT=9079
ENV RESONITE_MCP_METRICS_ENABLED=true
ENV RESONITE_MCP_LOG_FORMAT=json
ENV RESONITE_MCP_LOG_LEVEL=INFO
ENV RESONITE_MCP_LOG_DIR=/app/logs
ENV RESONITE_LINK_HOST=host.docker.internal
ENV RESONITE_LINK_PORT=4242

WORKDIR /app

FROM base AS production

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir -e ".[monitoring]"

RUN useradd --create-home --shell /bin/bash mcp \
    && mkdir -p /app/logs \
    && chown -R mcp:mcp /app

USER mcp

EXPOSE 10979 9079

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:10979/api/health', timeout=5)"

CMD ["python", "-m", "resonite_mcp", "--host", "0.0.0.0", "--port", "10979"]

ARG BUILD_DATE
ARG VERSION
ARG VCS_REF

LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.title="Resonite MCP" \
      org.opencontainers.image.description="Agentic Resonite MCP server with fleet handoff and ResoniteLink sidecar pattern" \
      org.opencontainers.image.vendor="FlowEngineer sandraschi" \
      org.opencontainers.image.source="https://github.com/sandraschi/resonite-mcp" \
      org.opencontainers.image.licenses="MIT"
