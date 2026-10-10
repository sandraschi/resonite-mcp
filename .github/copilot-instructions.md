# Resonite MCP — Copilot instructions

Python 3.12+, `uv run`, Ruff 120 cols, no `print()` in server code. Ports
10978/10979 only. just recipes: one powershell.exe per line, join
`Set-Location` with `; `.

## Session Context (Resonite MCP)

Before starting work: `GET /health`, `POST /api/v1/tool`
(`search_guides`/`ask_resonite`); read `docs/assess-reports/2026-10-10.md`.
At end of work: `ruff check src/` + `pytest tests/ -q`.
