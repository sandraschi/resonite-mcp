"""Structured JSON logging for Loki ingestion and fleet audit trails."""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class JsonLogFormatter(logging.Formatter):
    """Emit one JSON object per log line for Promtail/Loki."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "resonite-mcp",
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        for key in (
            "operation",
            "tool",
            "duration_ms",
            "status",
            "mode",
            "path",
            "target_slot",
            "imported",
            "total",
        ):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=True)


def configure_json_logging(root: logging.Logger | None = None) -> None:
    target = root or logging.getLogger()
    formatter = JsonLogFormatter()
    for handler in target.handlers:
        handler.setFormatter(formatter)


def configure_json_logging_if_enabled() -> None:
    if os.getenv("RESONITE_MCP_LOG_FORMAT", "").strip().lower() == "json":
        configure_json_logging()


def configure_file_logging(log_dir: str | Path | None = None) -> None:
    """Append JSON or text logs to a file under log_dir (Docker /app/logs)."""
    directory = Path(log_dir or os.getenv("RESONITE_MCP_LOG_DIR", "/app/logs"))
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        logging.getLogger(__name__).warning("Could not create log dir %s: %s", directory, exc)
        return

    log_path = directory / "resonite-mcp.log"
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setLevel(logging.INFO)
    if os.getenv("RESONITE_MCP_LOG_FORMAT", "").strip().lower() == "json":
        handler.setFormatter(JsonLogFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
    root = logging.getLogger()
    root.addHandler(handler)
    logging.getLogger(__name__).info("File logging enabled at %s", log_path)
