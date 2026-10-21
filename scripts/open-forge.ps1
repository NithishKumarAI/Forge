# Open Forge Launcher
# Discovers an open port in 18100-18149 (preferred 18101)
# Serves FastAPI backend with production React frontend static build
# Avoids collisions with other apps and prevents duplicate instances

param(
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path "$PSScriptRoot\..").Path
$RuntimeDir = Join-Path $RepoRoot ".runtime"
$RuntimeFile = Join-Path $RuntimeDir "forge-runtime.json"
$ApiDir = Join-Path $RepoRoot "apps\api"
$PythonExe = Join-Path $ApiDir ".venv\Scripts\python.exe"
$DistDir = Join-Path $RepoRoot "apps\web\dist"
$DistIndex = Join-Path $DistDir "index.html"

# Ensure runtime directory exists
if (-not (Test-Path $RuntimeDir)) {
    New-Item -ItemType Directory -Path $RuntimeDir -Force | Out-Null
}

# 1. Check if virtualenv exists
if (-not (Test-Path $PythonExe)) {
    Write-Error "Python virtual environment not found at '$PythonExe'. Please run setup first."
    exit 1
}

# 2. Check if frontend build exists
if (-not (Test-Path $DistIndex)) {
    Write-Warning "Frontend production build not found at '$DistIndex'. Web UI may not load properly. Run 'npm run build' in apps/web."
}

# 3. Check for existing running instance
if (Test-Path $RuntimeFile) {
    try {
        $state = Get-Content $RuntimeFile -Raw | ConvertFrom-Json
        if ($state.pid -and $state.port) {
            $existingProc = Get-Process -Id $state.pid -ErrorAction SilentlyContinue
            if ($existingProc) {
                # Test health endpoint
                $healthUrl = "http://127.0.0.1:$($state.port)/health"
                try {
                    $health = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 2 -ErrorAction Stop
                    if ($health.status -eq "ok") {
                        Write-Host "Forge is already running at $($state.url) (PID: $($state.pid))."
                        if (-not $NoBrowser) {
                            Start-Process $state.url
                        }
                        exit 0
                    }
                } catch {
                    # Health check failed; stale or unresponsive process
                }
            }
        }
    } catch {
        # Corrupt runtime file
    }
    # Clean up stale state
    Remove-Item -Path $RuntimeFile -Force -ErrorAction SilentlyContinue
}

# 4. Port Discovery (Preferred: 18101, Range: 18100-18149)
function Test-PortAvailable([int]$Port) {
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Parse("127.0.0.1"), $Port)
        $listener.Start()
        $listener.Stop()
        return $true
    } catch {
        return $false
    }
}

$PreferredPort = 18101
$PortRange = @($PreferredPort) + (18102..18149) + @(18100)
$SelectedPort = $null

foreach ($p in $PortRange) {
    if (Test-PortAvailable $p) {
        $SelectedPort = $p
        break
    }
}

if (-not $SelectedPort) {
    Write-Error "No available port found in range 18100-18149 for Forge."
    exit 1
}

$Url = "http://127.0.0.1:$SelectedPort/"
Write-Host "Starting Forge on port $SelectedPort..."

# 5. Launch FastAPI backend in background
$StdOutLog = Join-Path $RuntimeDir "forge.log"
$StdErrLog = Join-Path $RuntimeDir "forge-error.log"

$processArgs = @(
    "-u",
    "-m", "uvicorn", "app.main:app",
    "--host", "127.0.0.1",
    "--port", "$SelectedPort"
)

$proc = Start-Process -FilePath $PythonExe `
    -ArgumentList $processArgs `
    -WorkingDirectory $ApiDir `
    -WindowStyle Hidden `
    -RedirectStandardOutput $StdOutLog `
    -RedirectStandardError $StdErrLog `
    -PassThru

# 6. Record runtime state immediately
$runtimeState = @{
    pid = $proc.Id
    port = $SelectedPort
    url = $Url
    started_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
}
[System.IO.File]::WriteAllText($RuntimeFile, ($runtimeState | ConvertTo-Json), [System.Text.UTF8Encoding]::new($false))

# 7. Wait for health check (max 15 seconds)
$healthUrl = "http://127.0.0.1:$SelectedPort/health"
$healthy = $false
$maxAttempts = 30

for ($i = 0; $i -lt $maxAttempts; $i++) {
    Start-Sleep -Milliseconds 500

    if ($proc.HasExited) {
        Write-Error "Forge backend process exited unexpectedly with code $($proc.ExitCode)."
        if (Test-Path $StdErrLog) {
            Get-Content $StdErrLog -Tail 20 | Write-Host
        }
        Remove-Item -Path $RuntimeFile -Force -ErrorAction SilentlyContinue
        exit 1
    }

    try {
        $healthResponse = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 1 -ErrorAction Stop
        if ($healthResponse.status -eq "ok") {
            $healthy = $true
            break
        }
    } catch {
        # Still starting up
    }
}

if (-not $healthy) {
    Write-Error "Forge failed to become healthy within 15 seconds."
    try {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    } catch {}
    Remove-Item -Path $RuntimeFile -Force -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "Forge is ready! (PID: $($proc.Id))"
if (-not $NoBrowser) {
    Write-Host "Opening $Url in your browser..."
    Start-Process $Url
}
exit 0
