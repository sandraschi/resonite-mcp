# Resonite MCP DXT Build Script
# Builds and packages the Resonite MCP server for Claude Desktop deployment

param(
    [string]$OutputPath = "dist",
    [switch]$Clean,
    [switch]$Verbose
)

# PowerShell settings for reliability
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Setup logging
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
}

Write-Log "=== Resonite MCP DXT Build Script ==="

# Clean previous builds if requested
if ($Clean) {
    Write-Log "Cleaning previous builds..."
    if (Test-Path $OutputPath) {
        Remove-Item -Path $OutputPath -Recurse -Force
    }
    Write-Log "✅ Clean complete"
}

# Create output directory
if (-not (Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
}

# Validate required files exist
Write-Log "Validating required files..."
$requiredFiles = @(
    "dxt/dxt.json",
    "dxt/manifest.json",
    "src/resonite_mcp/server.py",
    "src/resonite_mcp/__init__.py"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        throw "Required file missing: $file"
    }
}
Write-Log "✅ All required files present"

# Copy source files to dist directory
Write-Log "Copying source files..."
$sourceFiles = @(
    "src/resonite_mcp/server.py",
    "src/resonite_mcp/cli.py",
    "src/resonite_mcp/http_server.py",
    "src/resonite_mcp/__init__.py"
)

foreach ($file in $sourceFiles) {
    $destFile = Join-Path $OutputPath (Split-Path $file -Leaf)
    Copy-Item -Path $file -Destination $destFile -Force
    if ($Verbose) {
        Write-Log "Copied: $file -> $destFile"
    }
}
Write-Log "✅ Source files copied"

# Copy plugins if they exist
if (Test-Path "src/resonite_mcp/plugins") {
    Write-Log "Copying plugins..."
    $pluginsDest = Join-Path $OutputPath "plugins"
    Copy-Item -Path "src/resonite_mcp/plugins" -Destination $pluginsDest -Recurse -Force
    Write-Log "✅ Plugins copied"
}

# Copy DXT configuration
Write-Log "Copying DXT configuration..."
Copy-Item -Path "dxt/dxt.json" -Destination (Join-Path $OutputPath "dxt.json") -Force
Copy-Item -Path "dxt/manifest.json" -Destination (Join-Path $OutputPath "manifest.json") -Force
Write-Log "✅ DXT configuration copied"

# Copy prompt templates
if (Test-Path "dxt/prompts") {
    Write-Log "Copying prompt templates..."
    $promptsDest = Join-Path $OutputPath "prompts"
    Copy-Item -Path "dxt/prompts" -Destination $promptsDest -Recurse -Force
    Write-Log "✅ Prompt templates copied"
}

# Create package info
$packageInfo = @{
    name = "resonite-mcp"
    version = "0.1.0"
    description = "Resonite social VR platform MCP server"
    author = "Sandra Schipal"
    build_date = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    files = (Get-ChildItem -Path $OutputPath -Recurse -File | Measure-Object).Count
}

$packageInfo | ConvertTo-Json | Out-File -FilePath (Join-Path $OutputPath "package.json") -Encoding UTF8
Write-Log "✅ Package info created"

# Validate the package
Write-Log "Validating package..."
$packageJsonPath = Join-Path $OutputPath "package.json"
$dxtJsonPath = Join-Path $OutputPath "dxt.json"

if (-not (Test-Path $packageJsonPath)) {
    throw "package.json not created"
}

if (-not (Test-Path $dxtJsonPath)) {
    throw "dxt.json not created"
}

# Test that server.py can be imported (basic syntax check)
try {
    $serverPath = Join-Path $OutputPath "server.py"
    $pythonCode = @"
import sys
import os
sys.path.insert(0, r'$OutputPath')
try:
    import server
    print('SUCCESS: Server module imports correctly')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
"@

    $tempScript = [System.IO.Path]::GetTempFileName() + ".py"
    $pythonCode | Out-File -FilePath $tempScript -Encoding UTF8

    try {
        $result = & python $tempScript 2>&1
        if ($result -match "ERROR") {
            throw "Server import failed: $result"
        }
        Write-Log "✅ Server module validation passed"
    } finally {
        Remove-Item -Path $tempScript -Force -ErrorAction SilentlyContinue
    }
} catch {
    Write-Log "❌ Server validation failed: $_" "ERROR"
    throw
}

# List package contents
Write-Log "Package contents:"
Get-ChildItem -Path $OutputPath -Recurse | ForEach-Object {
    $relativePath = $_.FullName.Replace((Resolve-Path $OutputPath).Path + "\", "")
    $size = if ($_.PSIsContainer) { "" } else { " ($('{0:N0}' -f $_.Length) bytes)" }
    Write-Log "  $($_.PSIsContainer ? '[DIR]' : '[FILE]') $relativePath$size"
}

Write-Log ""
Write-Log "=== Build Complete ==="
Write-Log "Package created in: $OutputPath"
Write-Log "Files created: $($packageInfo.files)"
Write-Log ""
Write-Log "To install in Claude Desktop:"
Write-Log "1. Copy the '$OutputPath' folder to your Claude Desktop extensions directory"
Write-Log "2. Restart Claude Desktop"
Write-Log "3. The Resonite MCP server should appear in the tools menu"
