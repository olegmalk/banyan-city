# Register banyan-box-autofill: one tick of box_autofill.py every three minutes,
# forever, with nobody logged in.
#
# WHY schtasks.exe AND NOT Register-ScheduledTask. The PowerShell path was tried
# first and this box refused it: a trigger repeating indefinitely is spelled
# `[TimeSpan]::MaxValue`, which serialises to `P99999999DT23H59M59S`, and the
# scheduler answers "The task XML contains a value which is incorrectly
# formatted or out of range" (HRESULT 0x80041318). `schtasks /sc MINUTE /mo 3`
# says the same thing in a form this Windows accepts, and it is the form the
# other banyan-* tasks were made with.
#
# SYSTEM, not the artvn SID. banyan-telemetry runs Interactive, so after an
# unattended reboot with nobody logged in it needs a hand. The whole claim of
# this task is that the card stays fed when no human and no agent is present, so
# a trigger that waits for a logon would fail in exactly the case it exists for.
# `/sc MINUTE` also survives a reboot on its own -- no boot trigger needed.
#
# One tick takes well under a second and does nothing but rename files, so no
# execution-time limit is needed; the default "do not start a new instance while
# one runs" is exactly the IgnoreNew behaviour we want, and it is the default.
#
# Idempotent -- /F replaces the registration. Re-run after any change to
# box-autofill.cmd. `python3 pipeline/box_autofill.py --deploy` does all of this
# from the Mac, including sending the files, and is the supported way in.
$ErrorActionPreference = 'Stop'

$out = schtasks /create /tn 'banyan-box-autofill' /tr 'C:\banyan-farm\box-autofill.cmd' `
    /sc MINUTE /mo 3 /ru SYSTEM /rl HIGHEST /f 2>&1
Write-Output ($out -join "`n")
if ($LASTEXITCODE -ne 0) { throw "schtasks /create failed rc=$LASTEXITCODE" }

# Fire one tick now, so registering it is also a test of it.
schtasks /run /tn 'banyan-box-autofill' | Out-Null

$i = Get-ScheduledTaskInfo -TaskName 'banyan-box-autofill'
$t = Get-ScheduledTask -TaskName 'banyan-box-autofill'
Write-Output "registered: $($t.TaskName) state=$($t.State)"
Write-Output "  action   : $($t.Actions[0].Execute)"
Write-Output "  runas    : $($t.Principal.UserId)"
Write-Output "  repeat   : $($t.Triggers[0].Repetition.Interval)"
Write-Output "  next run : $($i.NextRunTime)"
