# Identity proof is process creation time + executable + exact command + token/runtime.
$ErrorActionPreference = 'Stop'
$ForgeRepoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..')).TrimEnd('\')

function Get-ForgeHash([string]$Text) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($Text)))).Replace('-','').ToLowerInvariant() }
    finally { $sha.Dispose() }
}

function Get-ForgeContext([string]$Directory) {
    if (-not $Directory) { $Directory = Join-Path $ForgeRepoRoot '.runtime' }
    $full = [IO.Path]::GetFullPath($Directory).TrimEnd('\')
    if ($full -eq [IO.Path]::GetPathRoot($full).TrimEnd('\')) { throw 'A filesystem root cannot be a Forge runtime directory' }
    $cursor = $full
    while ($cursor) {
        if (Test-Path -LiteralPath $cursor) {
            $entry = Get-Item -LiteralPath $cursor -Force
            if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Runtime path contains a link: $cursor" }
        }
        $parent = [IO.Path]::GetDirectoryName($cursor)
        if ($parent -eq $cursor) { break }; $cursor = $parent
    }
    return @{ Directory=$full; State=(Join-Path $full 'forge-runtime.json'); Script=(Join-Path $ForgeRepoRoot 'scripts\forge_server.py'); Python=(Join-Path $ForgeRepoRoot 'apps\api\.venv\Scripts\python.exe') }
}

function Enter-ForgeLock($Context) {
    $name = 'Local\Forge-' + (Get-ForgeHash ($Context.Directory.ToUpperInvariant()))
    $mutex = [Threading.Mutex]::new($false,$name)
    try {
        try { $acquired = $mutex.WaitOne(45000) } catch [Threading.AbandonedMutexException] { $acquired=$true }
        if (-not $acquired) { throw 'Another Forge launch/close is still in progress for this runtime directory' }
        return $mutex
    } catch { $mutex.Dispose(); throw }
}

function Read-ForgeState($Context) {
    if (-not (Test-Path -LiteralPath $Context.State)) { return $null }
    try { return Get-Content -LiteralPath $Context.State -Raw | ConvertFrom-Json } catch { return $null }
}

function Get-VerifiedForgeProcess($Context,$State) {
    if (-not $State -or $State.version -ne 2 -or $State.owner -notmatch '^[0-9a-f]{32}$' -or -not $State.pid) { return $null }
    if (-not [StringComparer]::OrdinalIgnoreCase.Equals($State.runtime_dir,$Context.Directory) -or -not [StringComparer]::OrdinalIgnoreCase.Equals($State.repo_root,$ForgeRepoRoot)) { return $null }
    $process=$null
    try {
        $process=[Diagnostics.Process]::GetProcessById([int]$State.pid)
        # Hold the OS process handle before comparing creation time. Kill() then
        # uses this same handle, so PID reuse cannot retarget a shutdown.
        $null=$process.Handle
        if ($process.HasExited -or [string]$process.StartTime.ToUniversalTime().ToFileTimeUtc() -ne [string]$State.creation_filetime) { $process.Dispose();return $null }
        $info=Get-CimInstance Win32_Process -Filter "ProcessId = $([int]$State.pid)"
        if (-not $info -or -not $info.CommandLine -or -not [StringComparer]::OrdinalIgnoreCase.Equals($info.ExecutablePath,$State.executable)) { $process.Dispose();return $null }
        $basePython=(& $Context.Python -I -S -c 'import sys; print(sys._base_executable)').Trim()
        if (-not [StringComparer]::OrdinalIgnoreCase.Equals($info.ExecutablePath,$basePython)) { $process.Dispose();return $null }
        $command=[string]$info.CommandLine
        if ((Get-ForgeHash $command) -ne $State.command_sha256) { $process.Dispose();return $null }
        $scriptPattern='(?:^|\s)"?' + [regex]::Escape($Context.Script) + '"?(?=\s|$)'
        $runtimePattern='--runtime-dir\s+"?' + [regex]::Escape($Context.Directory) + '"?(?=\s|$)'
        $ownerPattern='--owner\s+' + $State.owner + '(?=\s|$)'
        if ($command -notmatch $scriptPattern -or $command -notmatch $runtimePattern -or $command -notmatch $ownerPattern) { $process.Dispose();return $null }
        return $process
    } catch { if ($process) { $process.Dispose() };return $null }
}

function Move-StaleForgeState($Context) {
    if (Test-Path -LiteralPath $Context.State) {
        $destination=Join-Path $Context.Directory ('forge-runtime.stale-' + [guid]::NewGuid().ToString('N') + '.json')
        Move-Item -LiteralPath $Context.State -Destination $destination
    }
}

function Test-ForgeHealth($Context,$State) {
    if (-not $State -or [int]$State.port -lt 1 -or [int]$State.port -gt 65535) { return $false }
    try {
        $identity=Invoke-RestMethod -Uri "http://127.0.0.1:$($State.port)/__forge/identity" -TimeoutSec 2
        return $identity.owner -eq $State.owner -and [int]$identity.pid -eq [int]$State.pid -and [StringComparer]::OrdinalIgnoreCase.Equals($identity.runtime_dir,$Context.Directory)
    } catch { return $false }
}

function Quote-ForgeArgument([string]$Value) {
    if ($Value.Contains('"')) { throw 'A launcher argument cannot contain a quote' }
    return '"' + $Value + '"'
}
