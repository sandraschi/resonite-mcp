# Resonite MCP - Launch Both Backend + Frontend
# Backend: FastAPI on port 10715
# Frontend: Vite on port 10714

$WebPort = 10714
$BackendPort = 10715
$RepoRoot = Split-Path -Parent $PSScriptRoot   # d:\Dev\repos\resonite-mcp

# 1. Install frontend deps if needed
Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) { npm install }

# 2. Kill any zombies on both ports
npx --yes kill-port $WebPort $BackendPort 2>$null
Start-Sleep -Milliseconds 500

# 3. Start the FastAPI backend in a new PowerShell window
$backendCmd = "Set-Location '$RepoRoot'; uv run uvicorn resonite_mcp.http_server:app --host 127.0.0.1 --port $BackendPort --log-level info"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# Give backend a moment to bind
Start-Sleep -Seconds 2

# 4. Start Vite dev server (foreground - this window)
Write-Host "Backend started in a separate window on port $BackendPort" -ForegroundColor Cyan
Write-Host "Starting Vite frontend on port $WebPort ..." -ForegroundColor Cyan
npm run dev -- --port $WebPort --host
