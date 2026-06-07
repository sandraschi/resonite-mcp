Param([switch]$Headless)

# Fast port helpers (scripts/PortHelpers.ps1)
Param([switch]$Headless)
$SkipFrontend = $Headless

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# Resonite MCP SOTA - Backend (HTTP MCP + SOTA API) + Vite frontend
# Backend: 10979, Frontend: 10978 (proxy /api to backend). No manual uv/uvicorn.

$WebPort = 10978
$BackendPort = 10979
$ProjectRoot = Split-Path -Parent $PSScriptRoot

function Clear-Port {
    param([int]$Port)
    $procIds = Get-PortListenerPidsFast -Port $port
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

# 3. Start Python backend (HTTP mode via cli entry point)
Write-Host "[RESONITE-MCP] Starting backend on port $BackendPort ..." -ForegroundColor Green
$serverArgs = @("run", "python", "-m", "resonite_mcp", "--port", [string]$BackendPort)
$backendProc = Start-Process -FilePath "uv" -ArgumentList $serverArgs -WorkingDirectory $ProjectRoot -NoNewWindow -PassThru
Pop-Location

# 4. Health-check backend before starting frontend
$backendUrl = "http://127.0.0.1:$BackendPort/health"
Write-Host "[RESONITE-MCP] Waiting for backend at $backendUrl ..." -ForegroundColor Gray
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $null = Invoke-WebRequest -Uri $backendUrl -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        $ready = $true
        Write-Host "[RESONITE-MCP] Backend is ready." -ForegroundColor Green
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    Write-Host "[WARNING] Backend did not respond within 30s. Starting frontend anyway..." -ForegroundColor Yellow
}

# 5. Frontend from web_sota
Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) {
    Write-Host "[RESONITE-MCP] Installing frontend deps..." -ForegroundColor Yellow
    npm install --quiet
}
Write-Host "[RESONITE-MCP] Starting Vite on port $WebPort ..." -ForegroundColor Green

# 6. Launch background task to open browser once frontend is ready
$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
if ($SkipFrontend) { return }
npm run dev -- --port $WebPort --host
_RepoRootForPorts = Split-Path -Parent $PSScriptRoot
Param([switch]$Headless)
$SkipFrontend = $Headless

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# Resonite MCP SOTA - Backend (HTTP MCP + SOTA API) + Vite frontend
# Backend: 10979, Frontend: 10978 (proxy /api to backend). No manual uv/uvicorn.

$WebPort = 10978
$BackendPort = 10979
$ProjectRoot = Split-Path -Parent $PSScriptRoot

function Clear-Port {
    param([int]$Port)
    $procIds = Get-PortListenerPidsFast -Port $port
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

# 3. Start Python backend (HTTP mode via cli entry point)
Write-Host "[RESONITE-MCP] Starting backend on port $BackendPort ..." -ForegroundColor Green
$serverArgs = @("run", "python", "-m", "resonite_mcp", "--port", [string]$BackendPort)
$backendProc = Start-Process -FilePath "uv" -ArgumentList $serverArgs -WorkingDirectory $ProjectRoot -NoNewWindow -PassThru
Pop-Location

# 4. Health-check backend before starting frontend
$backendUrl = "http://127.0.0.1:$BackendPort/health"
Write-Host "[RESONITE-MCP] Waiting for backend at $backendUrl ..." -ForegroundColor Gray
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $null = Invoke-WebRequest -Uri $backendUrl -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        $ready = $true
        Write-Host "[RESONITE-MCP] Backend is ready." -ForegroundColor Green
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    Write-Host "[WARNING] Backend did not respond within 30s. Starting frontend anyway..." -ForegroundColor Yellow
}

# 5. Frontend from web_sota
Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) {
    Write-Host "[RESONITE-MCP] Installing frontend deps..." -ForegroundColor Yellow
    npm install --quiet
}
Write-Host "[RESONITE-MCP] Starting Vite on port $WebPort ..." -ForegroundColor Green

# 6. Launch background task to open browser once frontend is ready
$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
if ($SkipFrontend) { return }
npm run dev -- --port $WebPort --host
_PortHelpers = Join-Path Param([switch]$Headless)
$SkipFrontend = $Headless

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# Resonite MCP SOTA - Backend (HTTP MCP + SOTA API) + Vite frontend
# Backend: 10979, Frontend: 10978 (proxy /api to backend). No manual uv/uvicorn.

$WebPort = 10978
$BackendPort = 10979
$ProjectRoot = Split-Path -Parent $PSScriptRoot

function Clear-Port {
    param([int]$Port)
    $procIds = Get-PortListenerPidsFast -Port $port
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

# 3. Start Python backend (HTTP mode via cli entry point)
Write-Host "[RESONITE-MCP] Starting backend on port $BackendPort ..." -ForegroundColor Green
$serverArgs = @("run", "python", "-m", "resonite_mcp", "--port", [string]$BackendPort)
$backendProc = Start-Process -FilePath "uv" -ArgumentList $serverArgs -WorkingDirectory $ProjectRoot -NoNewWindow -PassThru
Pop-Location

# 4. Health-check backend before starting frontend
$backendUrl = "http://127.0.0.1:$BackendPort/health"
Write-Host "[RESONITE-MCP] Waiting for backend at $backendUrl ..." -ForegroundColor Gray
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $null = Invoke-WebRequest -Uri $backendUrl -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        $ready = $true
        Write-Host "[RESONITE-MCP] Backend is ready." -ForegroundColor Green
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    Write-Host "[WARNING] Backend did not respond within 30s. Starting frontend anyway..." -ForegroundColor Yellow
}

# 5. Frontend from web_sota
Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) {
    Write-Host "[RESONITE-MCP] Installing frontend deps..." -ForegroundColor Yellow
    npm install --quiet
}
Write-Host "[RESONITE-MCP] Starting Vite on port $WebPort ..." -ForegroundColor Green

# 6. Launch background task to open browser once frontend is ready
$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
if ($SkipFrontend) { return }
npm run dev -- --port $WebPort --host
_RepoRootForPorts 'scripts\PortHelpers.ps1'
if (Test-Path -LiteralPath Param([switch]$Headless)
$SkipFrontend = $Headless

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# Resonite MCP SOTA - Backend (HTTP MCP + SOTA API) + Vite frontend
# Backend: 10979, Frontend: 10978 (proxy /api to backend). No manual uv/uvicorn.

$WebPort = 10978
$BackendPort = 10979
$ProjectRoot = Split-Path -Parent $PSScriptRoot

function Clear-Port {
    param([int]$Port)
    $procIds = Get-PortListenerPidsFast -Port $port
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

# 3. Start Python backend (HTTP mode via cli entry point)
Write-Host "[RESONITE-MCP] Starting backend on port $BackendPort ..." -ForegroundColor Green
$serverArgs = @("run", "python", "-m", "resonite_mcp", "--port", [string]$BackendPort)
$backendProc = Start-Process -FilePath "uv" -ArgumentList $serverArgs -WorkingDirectory $ProjectRoot -NoNewWindow -PassThru
Pop-Location

# 4. Health-check backend before starting frontend
$backendUrl = "http://127.0.0.1:$BackendPort/health"
Write-Host "[RESONITE-MCP] Waiting for backend at $backendUrl ..." -ForegroundColor Gray
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $null = Invoke-WebRequest -Uri $backendUrl -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        $ready = $true
        Write-Host "[RESONITE-MCP] Backend is ready." -ForegroundColor Green
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    Write-Host "[WARNING] Backend did not respond within 30s. Starting frontend anyway..." -ForegroundColor Yellow
}

# 5. Frontend from web_sota
Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) {
    Write-Host "[RESONITE-MCP] Installing frontend deps..." -ForegroundColor Yellow
    npm install --quiet
}
Write-Host "[RESONITE-MCP] Starting Vite on port $WebPort ..." -ForegroundColor Green

# 6. Launch background task to open browser once frontend is ready
$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
if ($SkipFrontend) { return }
npm run dev -- --port $WebPort --host
_PortHelpers) { . Param([switch]$Headless)
$SkipFrontend = $Headless

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# Resonite MCP SOTA - Backend (HTTP MCP + SOTA API) + Vite frontend
# Backend: 10979, Frontend: 10978 (proxy /api to backend). No manual uv/uvicorn.

$WebPort = 10978
$BackendPort = 10979
$ProjectRoot = Split-Path -Parent $PSScriptRoot

function Clear-Port {
    param([int]$Port)
    $procIds = Get-PortListenerPidsFast -Port $port
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

# 3. Start Python backend (HTTP mode via cli entry point)
Write-Host "[RESONITE-MCP] Starting backend on port $BackendPort ..." -ForegroundColor Green
$serverArgs = @("run", "python", "-m", "resonite_mcp", "--port", [string]$BackendPort)
$backendProc = Start-Process -FilePath "uv" -ArgumentList $serverArgs -WorkingDirectory $ProjectRoot -NoNewWindow -PassThru
Pop-Location

# 4. Health-check backend before starting frontend
$backendUrl = "http://127.0.0.1:$BackendPort/health"
Write-Host "[RESONITE-MCP] Waiting for backend at $backendUrl ..." -ForegroundColor Gray
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $null = Invoke-WebRequest -Uri $backendUrl -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        $ready = $true
        Write-Host "[RESONITE-MCP] Backend is ready." -ForegroundColor Green
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    Write-Host "[WARNING] Backend did not respond within 30s. Starting frontend anyway..." -ForegroundColor Yellow
}

# 5. Frontend from web_sota
Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) {
    Write-Host "[RESONITE-MCP] Installing frontend deps..." -ForegroundColor Yellow
    npm install --quiet
}
Write-Host "[RESONITE-MCP] Starting Vite on port $WebPort ..." -ForegroundColor Green

# 6. Launch background task to open browser once frontend is ready
$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
if ($SkipFrontend) { return }
npm run dev -- --port $WebPort --host
_PortHelpers }
$SkipFrontend = $Headless

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# Resonite MCP SOTA - Backend (HTTP MCP + SOTA API) + Vite frontend
# Backend: 10979, Frontend: 10978 (proxy /api to backend). No manual uv/uvicorn.

$WebPort = 10978
$BackendPort = 10979
$ProjectRoot = Split-Path -Parent $PSScriptRoot

function Clear-Port {
    param([int]$Port)
    $procIds = Get-PortListenerPidsFast -Port $port
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

# 3. Start Python backend (HTTP mode via cli entry point)
Write-Host "[RESONITE-MCP] Starting backend on port $BackendPort ..." -ForegroundColor Green
$serverArgs = @("run", "python", "-m", "resonite_mcp", "--port", [string]$BackendPort)
$backendProc = Start-Process -FilePath "uv" -ArgumentList $serverArgs -WorkingDirectory $ProjectRoot -NoNewWindow -PassThru
Pop-Location

# 4. Health-check backend before starting frontend
$backendUrl = "http://127.0.0.1:$BackendPort/health"
Write-Host "[RESONITE-MCP] Waiting for backend at $backendUrl ..." -ForegroundColor Gray
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $null = Invoke-WebRequest -Uri $backendUrl -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        $ready = $true
        Write-Host "[RESONITE-MCP] Backend is ready." -ForegroundColor Green
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    Write-Host "[WARNING] Backend did not respond within 30s. Starting frontend anyway..." -ForegroundColor Yellow
}

# 5. Frontend from web_sota
Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) {
    Write-Host "[RESONITE-MCP] Installing frontend deps..." -ForegroundColor Yellow
    npm install --quiet
}
Write-Host "[RESONITE-MCP] Starting Vite on port $WebPort ..." -ForegroundColor Green

# 6. Launch background task to open browser once frontend is ready
$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
if ($SkipFrontend) { return }
npm run dev -- --port $WebPort --host

