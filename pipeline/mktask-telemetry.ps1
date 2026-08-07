# Register banyan-telemetry as a detached task, so an ssh drop cannot kill the
# sampler and a render's console has nothing to do with it.
#
# Copied from mktask.ps1's recipe, with three deliberate differences:
#   - ExecutionTimeLimit 0 = unlimited. This is a daemon; a 4-hour cap would
#     silently stop the history exactly once per shift.
#   - MultipleInstances IgnoreNew, so the AtLogOn trigger below can never stack a
#     second sampler on top of a running one (the 2026-07-31 two-workers lesson).
#   - an AtLogOn trigger as well as the manual fire-now. The other banyan-* tasks
#     are ONCE and must be re-fired by hand after a reboot; the whole reason this
#     task exists is that we had no history through today's bluescreen, so the one
#     thing it must survive is a restart. LogonType Interactive means it starts
#     when artvn logs in — after an unattended reboot with no logon, it is still
#     a hand re-fire: `schtasks /run /tn banyan-telemetry`.
$ErrorActionPreference = 'Stop'

$bat = Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue
if ($bat) {
    Write-Output "battery: status=$($bat.BatteryStatus) charge=$($bat.EstimatedChargeRemaining)%"
} else {
    Write-Output "battery: none reported (desktop-like power)"
}

$action = New-ScheduledTaskAction -Execute 'C:\banyan-farm\telemetry.cmd'
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Seconds 0) `
    -MultipleInstances IgnoreNew -StartWhenAvailable
# The SID, not "$env:USERDOMAIN\$env:USERNAME": over ssh that pair does not
# resolve. Same SID the existing banyan-* tasks run under.
$principal = New-ScheduledTaskPrincipal `
    -UserId 'S-1-5-21-1349636699-4150225552-2638108493-1001' `
    -LogonType Interactive
$trigger = New-ScheduledTaskTrigger -AtLogOn

Register-ScheduledTask -TaskName 'banyan-telemetry' -Action $action `
    -Settings $settings -Principal $principal -Trigger $trigger -Force | Out-Null

$t = Get-ScheduledTask -TaskName 'banyan-telemetry'
Write-Output "registered: $($t.TaskName) state=$($t.State)"
Write-Output "  action  : $($t.Actions[0].Execute)"
Write-Output "  limit   : '$($t.Settings.ExecutionTimeLimit)' (PT0S = unlimited)"
Write-Output "  instances: $($t.Settings.MultipleInstances)"
Write-Output "  triggers: $($t.Triggers.Count) ($(($t.Triggers | ForEach-Object { $_.CimClass.CimClassName }) -join ', '))"
