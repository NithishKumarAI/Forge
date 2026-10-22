param(
    [switch]$NoBrowser,
    [string]$RuntimeDir='',
    [string]$DatabasePath='',
    [string]$SnapshotPath='',
    [string]$BackupPath='',
    [string]$FrontendDist='',
    [int]$PreferredPort=18101,
    [int]$PortStart=18100,
    [int]$PortEnd=18149
)
. "$PSScriptRoot\launcher-common.ps1"
$mutex=$null
try {
    $context=Get-ForgeContext $RuntimeDir
    if (-not (Test-Path -LiteralPath $context.Python)) { throw 'Forge virtual environment is missing. Install apps/api/requirements.txt first.' }
    if ($RuntimeDir -and -not $DatabasePath) { throw 'An isolated RuntimeDir requires an explicit DatabasePath to protect normal learner data.' }
    if ($PortStart -lt 1 -or $PortEnd -gt 65535 -or $PortStart -gt $PortEnd -or $PortEnd-$PortStart -gt 100) { throw 'Choose a bounded valid port range (at most 101 ports)' }
    if ($PreferredPort -lt $PortStart -or $PreferredPort -gt $PortEnd) { throw 'PreferredPort must be inside the selected range' }
    if (-not $FrontendDist) { $FrontendDist=Join-Path $ForgeRepoRoot 'apps\web\dist' }
    $FrontendDist=[IO.Path]::GetFullPath($FrontendDist)
    if (-not (Test-Path -LiteralPath (Join-Path $FrontendDist 'index.html'))) { throw "Frontend production build is missing: $FrontendDist. Run npm run build in apps/web." }
    New-Item -ItemType Directory -Path $context.Directory -Force | Out-Null
    $mutex=Enter-ForgeLock $context
    $state=Read-ForgeState $context
    $existing=Get-VerifiedForgeProcess $context $state
    if ($existing) {
        try {
            if (Test-ForgeHealth $context $state) {
                Write-Host "Forge is already running at $($state.url)"
                if (-not $NoBrowser) { Start-Process $state.url }
                exit 0
            }
            throw 'An owned Forge process is running but unhealthy. Close this runtime explicitly before restarting.'
        } finally { $existing.Dispose() }
    }
    if (Test-Path -LiteralPath $context.State) { Write-Warning 'Quarantining stale/unverified state; no unrelated process will be stopped.'; Move-StaleForgeState $context }
    $ports=@($PreferredPort)+@($PortStart..$PortEnd | Where-Object { $_ -ne $PreferredPort })
    $selected=$null
    foreach ($candidate in $ports) {
        $listener=$null
        try {
            $listener=[Net.Sockets.TcpListener]::new([Net.IPAddress]::Parse('127.0.0.1'),$candidate)
            $listener.ExclusiveAddressUse=$true;$listener.Start();$selected=$candidate;break
        } catch {} finally { if ($listener) { $listener.Stop() } }
    }
    if (-not $selected) { throw 'No available loopback port exists in the selected range' }
    $owner=[guid]::NewGuid().ToString('N')
    $env:FORGE_FRONTEND_DIST_PATH=$FrontendDist
    if ($DatabasePath) {
        $database=[IO.Path]::GetFullPath($DatabasePath)
        $env:FORGE_DATABASE_URL='sqlite:///' + $database.Replace('\','/')
        if (-not $SnapshotPath) { $SnapshotPath=Join-Path $context.Directory 'snapshots' }
        if (-not $BackupPath) { $BackupPath=Join-Path $context.Directory 'backups' }
    }
    if ($SnapshotPath) { $env:FORGE_CONTENT_SNAPSHOT_PATH=[IO.Path]::GetFullPath($SnapshotPath) }
    if ($BackupPath) { $env:FORGE_DATABASE_BACKUP_PATH=[IO.Path]::GetFullPath($BackupPath) }
    $stdout=Join-Path $context.Directory ("forge-$owner.log")
    $stderr=Join-Path $context.Directory ("forge-$owner-error.log")
    $arguments=@('-u',(Quote-ForgeArgument $context.Script),'--owner',$owner,'--runtime-dir',(Quote-ForgeArgument $context.Directory),'--port',[string]$selected)
    $launched=Start-Process -FilePath $context.Python -ArgumentList $arguments -WorkingDirectory (Join-Path $ForgeRepoRoot 'apps\api') -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
    $ready=$false
    for ($attempt=0;$attempt -lt 80;$attempt++) {
        Start-Sleep -Milliseconds 500
        $state=Read-ForgeState $context
        if ($state -and $state.owner -eq $owner -and (Test-ForgeHealth $context $state)) {
            $verified=Get-VerifiedForgeProcess $context $state
            if ($verified) { $verified.Dispose();$ready=$true;break }
        }
        $launched.Refresh();if ($launched.HasExited) { break }
    }
    $launched.Dispose()
    if (-not $ready) {
        $state=Read-ForgeState $context
        if ($state -and $state.owner -eq $owner) {
            $owned=Get-VerifiedForgeProcess $context $state
            if ($owned) { try { $owned.Kill();$null=$owned.WaitForExit(5000) } finally { $owned.Dispose() } }
            Move-StaleForgeState $context
        }
        throw "Forge startup failed. Inspect the isolated error log: $stderr"
    }
    Write-Host "Forge is ready at $($state.url) (owned PID $($state.pid))."
    if (-not $NoBrowser) { Start-Process $state.url }
} catch { Write-Error $_;exit 1 }
finally { if ($mutex) { $mutex.ReleaseMutex();$mutex.Dispose() } }
