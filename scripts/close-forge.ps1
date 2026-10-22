param([string]$RuntimeDir='')
. "$PSScriptRoot\launcher-common.ps1"
$mutex=$null
try {
    $context=Get-ForgeContext $RuntimeDir
    if (-not (Test-Path -LiteralPath $context.State)) { Write-Host 'Forge is already closed for this runtime.';exit 0 }
    $mutex=Enter-ForgeLock $context
    $state=Read-ForgeState $context
    $owned=Get-VerifiedForgeProcess $context $state
    if (-not $owned) {
        Write-Warning 'Runtime identity is stale or unverifiable. No process was stopped; state is retained in quarantine.'
        Move-StaleForgeState $context;exit 0
    }
    try {
        if (-not $owned.HasExited) { $owned.Kill();$null=$owned.WaitForExit(5000) }
    } finally { $owned.Dispose() }
    Remove-Item -LiteralPath $context.State -Force
    Write-Host 'The verified Forge process is closed.'
} catch { Write-Error $_;exit 1 }
finally { if ($mutex) { $mutex.ReleaseMutex();$mutex.Dispose() } }
