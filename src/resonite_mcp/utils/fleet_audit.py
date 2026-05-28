"""Structured fleet import audit logging."""

from __future__ import annotations

import logging

from .telemetry import record_fleet_import

audit_logger = logging.getLogger("resonite_mcp.fleet_audit")


def log_fleet_operation(
    operation: str,
    *,
    status: str,
    duration_ms: float,
    tool: str = "resonite_fleet",
    message: str = "fleet operation complete",
    **fields: object,
) -> None:
    extra: dict[str, object] = {
        "operation": operation,
        "tool": tool,
        "status": status,
        "duration_ms": round(duration_ms, 2),
    }
    extra.update(fields)
    audit_logger.info(message, extra=extra)
    record_fleet_import(operation, status)
