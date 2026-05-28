#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build PyInstaller sidecar for Tauri (resonite-mcp HTTP backend on :10979).
#>
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "=== resonite-mcp sidecar build ===" -ForegroundColor Cyan

Push-Location $Root
try {
    $pi = uv run pyinstaller --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "-> Installing PyInstaller..." -ForegroundColor Yellow
        uv pip install pyinstaller
    } else {
        Write-Host "-> PyInstaller: $pi" -ForegroundColor Gray
    }

    Remove-Item -Recurse -Force "$Root\build\resonite-mcp-backend" -ErrorAction SilentlyContinue
    Remove-Item -Force "$Root\dist\resonite-mcp-backend.exe" -ErrorAction SilentlyContinue

    Write-Host "-> Running PyInstaller (may take several minutes)..." -ForegroundColor Yellow
    uv run pyinstaller resonite-mcp-backend.spec --clean --noconfirm
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed (exit $LASTEXITCODE)" }

    $triple = "x86_64-pc-windows-msvc"
    $src = "$Root\dist\resonite-mcp-backend.exe"
    $dstDir = "$Root\native\binaries"
    $dst = "$dstDir\resonite-mcp-backend-$triple.exe"

    if (-not (Test-Path $src)) { throw "Build output not found: $src" }

    New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
    Copy-Item $src $dst -Force

    $sizeMB = [math]::Round((Get-Item $dst).Length / 1MB, 1)
    Write-Host "=== Sidecar ready ===" -ForegroundColor Green
    Write-Host "  $dst ($sizeMB MB)" -ForegroundColor Cyan
} finally {
    Pop-Location
}
