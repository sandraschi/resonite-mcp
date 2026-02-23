# Webapp Start - Clears port, builds, runs
$WebPort = 10706
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

# 1. Clear port from zombies/squatters (cross-platform via npm)
Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) { npm install }
npx --yes kill-port $WebPort 2>$null

# 2. Build (optional for dev, but good for check)
# npm run build

# 3. Run server (Vite dev for now)
npm run dev -- --port $WebPort --host
