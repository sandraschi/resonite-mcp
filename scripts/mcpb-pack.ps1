#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build a fleet-standard MCPB bundle for resonite-mcp (fresh-stage, verify, pack).

.DESCRIPTION
    Per MCPB_PACKAGING_STANDARDS.md (mcp-central-docs) this script:
      0. Fresh-stages repo src/<pkg> -> mcpb/src/<pkg> (wipe + recopy, never flatten)
      1. Copies the canonical prompts from repo assets/prompts -> mcpb/assets/prompts
      2. Verifies the entry point imports with only mcpb/src on sys.path
      3. Asserts no __pycache__ / *.pyc / *.bak / *.bak.* / *.orig / *.rej under mcpb/
      4. Only then runs `mcpb pack`
      5. Removes mcpb/src again so the next run cannot reuse a stale twin

.PARAMETER RepoRoot
    Repo root. Defaults to the parent of this script's directory.

.PARAMETER KeepStage
    If set, leave mcpb/src/ in place after packing (diagnostic only).

.EXAMPLE
    pwsh -NoProfile -File scripts/mcpb-pack.ps1
#>
param(
    [string]$RepoRoot = "",
    [switch]$KeepStage
)

$ErrorActionPreference = "Stop"
if (-not $RepoRoot) { $RepoRoot = Split-Path $PSScriptRoot -Parent }

Write-Host "`n=== mcpb-pack.ps1 - resonite-mcp ===" -ForegroundColor Cyan

# --- Resolve mcpb CLI (global install, or full-path fallback) ---
$mcpbCmd = Get-Command mcpb.cmd -ErrorAction SilentlyContinue
if (-not $mcpbCmd) { $mcpbCmd = Get-Command mcpb -ErrorAction SilentlyContinue }
if (-not $mcpbCmd) {
    $npmMcpb = Join-Path $env:APPDATA "npm\mcpb.cmd"
    if (Test-Path $npmMcpb) { $mcpbCmd = $npmMcpb } else { throw "mcpb CLI not found. Install: npm install -g @anthropic-ai/mcpb" }
}
Write-Host "  mcpb CLI: $mcpbCmd" -ForegroundColor Green

# --- Project metadata ---
$pyproj = Get-Content (Join-Path $RepoRoot "pyproject.toml") -Raw -Encoding UTF8
$name = if ($pyproj -match '(?m)^name\s*=\s*"([^"]*)"') { $matches[1] } else { "resonite-mcp" }
$version = if ($pyproj -match '(?m)^version\s*=\s*"([^"]*)"') { $matches[1] } else { "0.0.0" }

# --- 0. Fresh-stage source (wipe + recopy, preserve package dir) ---
$pkg = Get-ChildItem (Join-Path $RepoRoot "src") -Directory -ErrorAction SilentlyContinue |
    Where-Object { Test-Path (Join-Path $_.FullName "__init__.py") } | Select-Object -First 1
if (-not $pkg) { throw "No Python package found under $RepoRoot\src" }
$pkgName = $pkg.Name
$stagePkg = Join-Path $RepoRoot "mcpb\src\$pkgName"

Write-Host "  Fresh-staging src\$pkgName -> mcpb\src\$pkgName ..." -ForegroundColor Yellow
if (Test-Path (Join-Path $RepoRoot "mcpb\src")) { Remove-Item -Recurse -Force (Join-Path $RepoRoot "mcpb\src") }
New-Item -ItemType Directory -Force -Path (Split-Path $stagePkg) | Out-Null
Copy-Item -Recurse -Force $pkg.FullName $stagePkg
# Strip bytecode the source tree may itself carry before the pollution check
Get-ChildItem $stagePkg -Recurse -Filter "__pycache__" -Directory -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem $stagePkg -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "  Staged fresh source (0. fresh stage proved)" -ForegroundColor Green

# --- 1. Canonical prompts -> staging ---
$srcPrompts = Join-Path $RepoRoot "assets\prompts"
$destPrompts = Join-Path $RepoRoot "mcpb\assets\prompts"
if (Test-Path $srcPrompts) {
    New-Item -ItemType Directory -Force -Path $destPrompts | Out-Null
    Copy-Item -Recurse -Force (Join-Path $srcPrompts "*") $destPrompts
    Write-Host "  Copied canonical prompts -> mcpb/assets/prompts" -ForegroundColor Green
} else {
    Write-Host "  WARNING: repo assets/prompts missing - using existing mcpb prompts" -ForegroundColor DarkYellow
}

# --- 1b. Sync .mcpbignore to the pack root (mcpb/), else mcpb pack excludes nothing ---
# ALWAYS overwrite from repo-root (never copy-if-missing) - a copy-if-missing check syncs
# once then goes stale forever after mcpb/.mcpbignore first exists. Found 2026-09-03 while
# fixing the identical bug freshly-introduced into overte-mcp/godot-mcp/robotics-mcp/
# avatar-mcp's scripts: this script (the one those were modeled on) had the same gap - a
# stale mcpb/.mcpbignore sitting here since Aug 27 was silently reused on every run since,
# though a diff against the current repo-root version showed it happened to still match
# byte-for-byte (no actual bundle impact this time, but the mechanism was broken regardless).
$rootIgnore = Join-Path $RepoRoot ".mcpbignore"
$packIgnore = Join-Path $RepoRoot "mcpb\.mcpbignore"
if (Test-Path $rootIgnore) {
    Copy-Item $rootIgnore $packIgnore -Force
    Write-Host "  Synced mcpb/.mcpbignore from repo root" -ForegroundColor Green
} elseif (Test-Path $packIgnore) {
    Write-Host "  [WARN] no repo-root .mcpbignore - using existing (possibly stale) mcpb/.mcpbignore" -ForegroundColor Yellow
} else {
    throw "No .mcpbignore at repo root or mcpb/ pack root"
}

# --- 2. Entry point import resolves from mcpb/src only ---
# Use the repo's uv environment (deps present) but pin PYTHONPATH to mcpb/src so we can
# assert the package resolves from the staged copy, not from site-packages.
# PYTHONDONTWRITEBYTECODE stops the import from leaving __pycache__/*.pyc in the stage.
$prevPath = $env:PYTHONPATH
$prevNoByte = $env:PYTHONDONTWRITEBYTECODE
$env:PYTHONDONTWRITEBYTECODE = "1"
$uv = "C:\Users\sandr\.local\bin\uv.exe"
$pyRunner = if (Test-Path $uv) { $uv } else { (Get-Command uv -ErrorAction SilentlyContinue).Source }
if (-not $pyRunner) {
    $py = (Get-Command python -ErrorAction SilentlyContinue).Source
    $env:PYTHONPATH = Join-Path $RepoRoot "mcpb\src"
    $importOut = (& $py -c "import $pkgName; print('import-ok', $pkgName.__file__)" 2>&1 | Out-String)
} else {
    $env:PYTHONPATH = Join-Path $RepoRoot "mcpb\src"
    $importOut = (& $pyRunner run --project $RepoRoot python -c "import $pkgName; print('import-ok', $pkgName.__file__)" 2>&1 | Out-String)
}
$env:PYTHONPATH = $prevPath
$env:PYTHONDONTWRITEBYTECODE = $prevNoByte
if ($LASTEXITCODE -ne 0 -or $importOut -notmatch "import-ok") {
    throw "Entry import FAILED from mcpb/src only: $importOut"
}
if ($importOut -match "site-packages") { throw "Entry resolved from site-packages (false pass) - not self-contained" }
Write-Host "  Entry import OK from mcpb/src only (2. self-contained)" -ForegroundColor Green

# --- 3. No pollution under mcpb/ (after import, so any bytecode the import left is caught) ---
$bad = Get-ChildItem (Join-Path $RepoRoot "mcpb") -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match "^(.*\.(pyc|bak|orig|rej)$)|(^__pycache__$)" -or $_.Name -match "\.bak\." }
if ($bad) { throw "Pollution found under mcpb/: $($bad.FullName -join ', ')" }
Write-Host "  No __pycache__ / *.pyc / *.bak / *.orig / *.rej under mcpb/ (4. clean)" -ForegroundColor Green

# --- 4. Pack ---
$distDir = Join-Path $RepoRoot "dist"
New-Item -ItemType Directory -Force -Path $distDir | Out-Null
$outputFile = Join-Path $distDir "$name-v$version.mcpb"
if (Test-Path $outputFile) { Remove-Item $outputFile -Force }
Write-Host "  Packing -> $outputFile ..." -ForegroundColor Yellow
& $mcpbCmd pack (Join-Path $RepoRoot "mcpb") $outputFile 2>&1 | Out-String | Write-Host
if (-not (Test-Path $outputFile)) { throw "mcpb pack did not produce $outputFile" }

# --- 5. Remove staging src so next run cannot reuse a stale twin ---
if (-not $KeepStage -and (Test-Path (Join-Path $RepoRoot "mcpb\src"))) {
    Remove-Item -Recurse -Force (Join-Path $RepoRoot "mcpb\src")
    Write-Host "  Removed mcpb/src staging (5. no stale twin)" -ForegroundColor Green
}

$sizeMB = [math]::Round((Get-Item $outputFile).Length / 1MB, 2)
Write-Host "`n  BUILT: $outputFile ($sizeMB MB)" -ForegroundColor Green
Write-Host "  Package: $name v$version" -ForegroundColor Cyan
