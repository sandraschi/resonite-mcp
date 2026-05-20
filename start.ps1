Param([switch]$Headless)

# resonite-mcp Start — delegates to full SOTA startup in web_sota/
$ScriptDir = Split-Path -Parent $PSCommandPath
$WebSotaStart = Join-Path $ScriptDir "web_sota\start.ps1"

if (-not (Test-Path -LiteralPath $WebSotaStart)) {
    Write-Host "[ERROR] web_sota\start.ps1 not found." -ForegroundColor Red
    exit 1
}

$Args = if ($Headless) { @('-Headless') } else { @() }
& $WebSotaStart @Args
