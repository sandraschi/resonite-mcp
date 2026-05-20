set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# Open the interactive recipe dashboard in the browser
default:
    @pwsh.exe -NoProfile -ExecutionPolicy Bypass -File ../mcp-central-docs/scripts/just-dashboard.ps1 -Path .

# ── Setup ─────────────────────────────────────────────────────────────────────

# Install Python dependencies via uv
install:
    uv sync

# Install frontend dependencies
install-fe:
    Set-Location '{{justfile_directory()}}\web_sota'; npm install

# Initialize full project (deps + dev deps)
init: install install-fe
    uv sync --group dev

# ── Development ────────────────────────────────────────────────────────────────

# Start the backend server (port 10979)
start-be:
    uv run python -m resonite_mcp --port 10979

# Start the backend with agentic CodeMode
start-be-agentic:
    uv run python -m resonite_mcp --port 10979 --agentic

# Start the frontend dev server (port 10978)
start-fe:
    Set-Location '{{justfile_directory()}}\web_sota'; npm run dev

# Start the fullstack SOTA (backend + frontend)
start:
    ./web_sota/start.ps1

# Start headless (backend only)
start-headless:
    ./web_sota/start.ps1 -Headless

# ── Quality ────────────────────────────────────────────────────────────────────

# Lint Python (Ruff) and TypeScript (Biome)
lint:
    uv run ruff check src/resonite_mcp/
    uv run ruff check tests/
    Set-Location '{{justfile_directory()}}\web_sota'; npx @biomejs/biome ci .

# Auto-fix lint issues (Ruff fix + Biome write)
fix:
    uv run ruff check src/resonite_mcp/ --fix --unsafe-fixes
    uv run ruff format src/resonite_mcp/
    Set-Location '{{justfile_directory()}}\web_sota'; npx @biomejs/biome check --write .

# Run type checker (Mypy strict)
typecheck:
    uv run mypy src/resonite_mcp/

# Run Python tests with coverage
test:
    uv run pytest tests/ -v --cov=resonite_mcp --cov-report=term-missing

# ── Hardening ──────────────────────────────────────────────────────────────────

# Security audit (Bandit)
check-sec:
    uv run bandit -r src/resonite_mcp/

# Dependency vulnerability audit (Safety)
audit-deps:
    uv run safety check

# Run all checks: lint + typecheck + test + sec
check-all: lint typecheck test check-sec
    @Write-Host 'All checks passed!' -ForegroundColor Green

# ── Build ──────────────────────────────────────────────────────────────────────

# Build the frontend for production
build-fe:
    Set-Location '{{justfile_directory()}}\web_sota'; npm run build

# Build the Zed extension (Rust WASM)
build-zed:
    ./build.ps1

# ── Cleanup ────────────────────────────────────────────────────────────────────

# Clear Python cache and temp files
clean:
    Remove-Item -Recurse -Force '{{justfile_directory()}}\.ruff_cache' -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force '{{justfile_directory()}}\.pytest_cache' -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force '{{justfile_directory()}}\.mypy_cache' -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force '{{justfile_directory()}}\htmlcov' -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force '{{justfile_directory()}}\**\__pycache__' -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force '{{justfile_directory()}}\*.egg-info' -ErrorAction SilentlyContinue
    Write-Host 'Cache directories cleaned.' -ForegroundColor Green

# Kill zombie processes on the app ports
kill-ports:
    foreach ($port in @(10978, 10979)) { \
        $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue; \
        if ($conns) { \
            $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique; \
            foreach ($p in $pids) { \
                if ($p -and $p -ne 0) { Stop-Process -Id $p -Force -ErrorAction Stop } \
            }; \
            Write-Host "Port $port cleared" -ForegroundColor Yellow \
        } \
    }
