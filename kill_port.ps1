param([int]$Port)
$process = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -First 1
if ($process) {
    Write-Host "Killing process $($process.OwningProcess) on port $Port"
    Stop-Process -Id $process.OwningProcess -Force
}
else {
    Write-Host "No process found on port $Port"
}
