# Close Forge Launcher
# Safely stops the running Forge backend process recorded in .runtime/forge-runtime.json
# NEVER stops arbitrary Python processes or affects other running applications

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path "$PSScriptRoot\..").Path
$RuntimeDir = Join-Path $RepoRoot ".runtime"
$RuntimeFile = Join-Path $RuntimeDir "forge-runtime.json"

if (-not (Test-Path $RuntimeFile)) {
    Write-Host "Forge is not running (no runtime file found)."
    exit 0
}

try {
    $state = Get-Content $RuntimeFile -Raw | ConvertFrom-Json
    $pidToKill = $state.pid
} catch {
    Write-Warning "Runtime file was invalid. Cleaning up..."
    Remove-Item -Path $RuntimeFile -Force -ErrorAction SilentlyContinue
    exit 0
}

if (-not $pidToKill) {
    Write-Host "No process ID recorded in runtime file."
    Remove-Item -Path $RuntimeFile -Force -ErrorAction SilentlyContinue
    exit 0
}

$proc = Get-Process -Id $pidToKill -ErrorAction SilentlyContinue
if ($proc) {
    Write-Host "Stopping Forge (PID: $pidToKill)..."
    try {
        Stop-Process -Id $pidToKill -Force
        # Wait up to 3 seconds for exit
        $waitCount = 0
        while (-not $proc.HasExited -and $waitCount -lt 30) {
            Start-Sleep -Milliseconds 100
            $waitCount++
        }
        Write-Host "Forge stopped."
    } catch {
        Write-Warning "Could not stop process ${pidToKill}: $_"
    }
} else {
    Write-Host "Forge process (PID: $pidToKill) is not running."
}

Remove-Item -Path $RuntimeFile -Force -ErrorAction SilentlyContinue
Write-Host "Forge closed successfully."
exit 0
