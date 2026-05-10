Param([switch]$Headless)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# Resonite MCP SOTA - Backend (HTTP MCP + SOTA API) + Vite frontend
# Backend: 10715, Frontend: 10714 (proxy /api to backend). No manual uv/uvicorn.

$WebPort = 10714
$BackendPort = 10715
$ProjectRoot = Split-Path -Parent $PSScriptRoot

function Clear-Port {
    param([int]$Port)
    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $conns) { return $false }
    $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($p in $pids) {
        if ($p -and $p -ne 0) {
            try {
                Stop-Process -Id $p -Force -ErrorAction Stop
                Write-Host "      PID $p (port $Port) stopped" -ForegroundColor DarkGray
            }
            catch { }
        }
    }
    Start-Sleep -Milliseconds 400
    return $true
}

Write-Host "[RESONITE-MCP] SOTA startup (backend $BackendPort, frontend $WebPort)..." -ForegroundColor Cyan

# 1. Clear port squatters
foreach ($port in @($WebPort, $BackendPort)) {
    $cleared = Clear-Port -Port $port
    if ($cleared) { Write-Host "      Port $port cleared" -ForegroundColor Yellow }
}

# 2. Sync deps and env from project root
Push-Location $ProjectRoot
if (-not (Test-Path "pyproject.toml")) {
    Write-Host "[ERROR] pyproject.toml not found. Run from web_sota folder." -ForegroundColor Red
    exit 1
}
uv sync --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] uv sync failed." -ForegroundColor Red
    exit 1
}
$env:PYTHONPATH = Join-Path $ProjectRoot "src"
$env:MCP_TRANSPORT = "http"
$env:MCP_PORT = [string]$BackendPort
$env:MCP_HOST = "127.0.0.1"

# 3. Start Python backend (HTTP mode; SOTA API via on_app_init)
Write-Host "[RESONITE-MCP] Starting backend on port $BackendPort ..." -ForegroundColor Green
$serverArgs = @("run", "python", "-m", "resonite_mcp.server", "--http", "--port", [string]$BackendPort)
Start-Process -FilePath "uv" -ArgumentList $serverArgs -WorkingDirectory $ProjectRoot -NoNewWindow -PassThru
Pop-Location

Start-Sleep -Seconds 2

# 4. Frontend from web_sota
Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) {
    Write-Host "[RESONITE-MCP] Installing frontend deps..." -ForegroundColor Yellow
    npm install --quiet
}
Write-Host "[RESONITE-MCP] Starting Vite on port $WebPort ..." -ForegroundColor Green

# 4b. Launch background task to open browser once frontend is ready (Auto-opened by Antigravity)
$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
npm run dev -- --port $WebPort --host



