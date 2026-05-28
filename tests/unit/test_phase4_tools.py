"""Tests for Phase 4 telemetry, logging, Docker helpers, and metrics routes."""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient


class TestTelemetry:
    def test_metrics_disabled_render(self):
        from resonite_mcp.utils import telemetry

        telemetry._metrics_initialized = False
        with patch.object(telemetry, "metrics_enabled", return_value=False):
            telemetry.init_metrics()
        body = telemetry.render_metrics()
        assert b"disabled" in body

    def test_json_log_formatter(self):
        import logging

        from resonite_mcp.utils.structured_logging import JsonLogFormatter

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="fleet operation complete",
            args=(),
            exc_info=None,
        )
        record.operation = "import_vrm_batch"
        record.status = "ok"
        record.duration_ms = 12.5
        line = JsonLogFormatter().format(record)
        assert '"service": "resonite-mcp"' in line
        assert "import_vrm_batch" in line

    def test_fleet_audit_logger(self):
        from resonite_mcp.utils.fleet_audit import log_fleet_operation

        with patch("resonite_mcp.utils.fleet_audit.record_fleet_import") as mock_metric:
            log_fleet_operation("import_staged_assets", status="ok", duration_ms=3.0, imported=1, total=1)
        mock_metric.assert_called_once_with("import_staged_assets", "ok")


class TestMetricsRoutes:
    def test_metrics_routes_registered(self):
        from resonite_mcp.http_server import app

        paths = {getattr(r, "path", None) for r in app.routes}
        assert "/api/metrics" in paths
        assert "/metrics" in paths

    def test_health_reports_phase4(self):
        from resonite_mcp.http_server import app

        client = TestClient(app)
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        body = response.json()
        assert body["version"] == "1.0.0"
        assert body["agent_lab_phase"] == 6
        assert "metrics_enabled" in body

    def test_metrics_endpoint(self):
        from resonite_mcp.http_server import app

        client = TestClient(app)
        response = client.get("/metrics")
        assert response.status_code == 200
        assert response.content
