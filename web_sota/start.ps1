
# Fast port helpers (scripts/PortHelpers.ps1)
$__RepoRootForPorts = Split-Path -Parent $PSScriptRoot
$__PortHelpers = Join-Path $__RepoRootForPorts 'scripts\PortHelpers.ps1'
if (Test-Path -LiteralPath $__PortHelpers) { . $__PortHelpers }
Param([switch]$Headless) $SkipFrontend = $Headless  # --- SOTA Headless Standard --- if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {     Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden     exit } $WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' } # ------------------------------  # Resonite MCP SOTA - Backend (HTTP MCP + SOTA API) + Vite frontend # Backend: 10979, Frontend: 10978 (proxy /api to backend). No manual uv/uvicorn.  $WebPort = 10978 $BackendPort = 10979 $ProjectRoot = Split-Path -Parent $PSScriptRoot  function Clear-Port {     param([int]$Port)     $procIds = Get-PortListenerPidsFast -Port $port
