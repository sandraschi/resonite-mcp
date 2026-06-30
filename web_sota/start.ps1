Param([switch]$Headless)
$SkipFrontend = $Headless

if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    $a = @('-NoProfile', '-File', $PSCommandPath, '-Headless')
    Start-Process pwsh -ArgumentList $a -WindowStyle Hidden
    exit
}

$WebPort = 10978
$BackendPort = 10979
$ProjectRoot = Split-Path -Parent $PSScriptRoot

$FleetStartPath = Join-Path $ProjectRoot "scripts\FleetStartMode.ps1"
if (-not (Test-Path -LiteralPath $FleetStartPath)) {
    Write-Host "ERROR: Missing vendored launcher helper: $FleetStartPath" -ForegroundColor Red
    exit 1
}
. $FleetStartPath

function Clear-Port($Port) {
    $c = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if (-not $c) { return $false }
    $c | Select-Object -ExpandProperty OwningProcess -Unique | Where-Object { $_ -and $_ -ne 0 } | ForEach-Object {
        taskkill /F /PID $_ 2>$null
        Write-Host "  Killed PID $_ on port $Port" -ForegroundColor DarkGray
    }
    return $true
}

function Force-Kill-Zombies {
    param([int]$BP, [int]$FP)
    Write-Host "[RESONITE-MCP] Force-killing zombies..." -ForegroundColor DarkGray
    Clear-Port $BP
    Clear-Port $FP
    taskkill /F /IM "resonite-mcp-backend.exe" /T 2>$null
    taskkill /F /IM "resonite-mcp-native.exe" /T 2>$null
    taskkill /F /IM "python.exe" /T 2>$null
    taskkill /F /IM "uv.exe" /T 2>$null
    Start-Sleep -Milliseconds 500
    $remaining = Get-NetTCPConnection -LocalPort $BP -ErrorAction SilentlyContinue
    if ($remaining) {
        Write-Host "  Port $BP still occupied — elevated kill (UAC)..." -ForegroundColor Yellow
        $cmd = "Get-NetTCPConnection -LocalPort $BP -ErrorAction SilentlyContinue | ForEach-Object { taskkill /F /PID `$_.OwningProcess /T 2>null }; taskkill /F /IM resonite-mcp-backend.exe /T 2>null; taskkill /F /IM python.exe /T 2>null"
        Start-Process powershell -Verb RunAs -WindowStyle Hidden -ArgumentList "-NoProfile", "-Command", $cmd
        Start-Sleep 4
    }
    if (Get-NetTCPConnection -LocalPort $BP -ErrorAction SilentlyContinue) {
        Write-Host "  WARNING: Port $BP still busy" -ForegroundColor Red
    } else {
        Write-Host "  All ports clear" -ForegroundColor Green
    }
}

Write-Host "[RESONITE-MCP] Starting backend $BackendPort, frontend $WebPort" -ForegroundColor Cyan

Force-Kill-Zombies -BP $BackendPort -FP $FrontendPort

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

Write-Host "[RESONITE-MCP] Starting backend on port $BackendPort ..." -ForegroundColor Green
$sa = @("run", "python", "-m", "resonite_mcp", "--port", [string]$BackendPort)
Start-Process -FilePath "uv" -ArgumentList $sa -WorkingDirectory $ProjectRoot -NoNewWindow -PassThru
Pop-Location

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
    Write-Host "[WARNING] Backend did not respond within 30s." -ForegroundColor Yellow
}

Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) {
    Write-Host "[RESONITE-MCP] Installing frontend deps..." -ForegroundColor Yellow
    npm install --quiet
}
Write-Host "[RESONITE-MCP] Starting Vite on port $WebPort ..." -ForegroundColor Green

$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollCode = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
$pa = @("-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollCode)
Start-Process powershell -ArgumentList $pa

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
if ($SkipFrontend) { return }
npm run dev -- --port $WebPort --host
