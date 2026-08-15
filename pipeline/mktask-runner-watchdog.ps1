# Register banyan-runner-watchdog: one tick of runner_watchdog.py --local every
# five minutes, forever, with nobody logged in.
#
# WHAT THIS REPLACES, and why it is not just a re-enable. The task existed and
# was DISABLED on 2026-08-12 after its PowerShell script asked Task Scheduler for
# the runner task's state -- a query that returns an empty string under the
# scheduled context -- read empty as "runner dead", and logged sixty consecutive
# false "restarted" lines, one every five minutes for five hours. Those restarts
# happened to be inert (a bare /run is ignored while an instance is Running), so
# the flap cost nothing but trust. The script was then rewritten to check the
# process table instead and fired correctly once; the task was disabled minutes
# later and never came back.
#
# The rewrite fixed the probe but kept the shape that made the flap possible: one
# signal, no queue check, no log-age check, no cap on how many times it will
# restart. It also declares in its own comments that it runs as SYSTEM while the
# registration ran it as artvn/Limited -- the same class of mistake as reading a
# state string in a context it was never tried in. So the action now points at
# pipeline/runner_watchdog.py, which requires FOUR independent conditions before
# it will touch anything (work waiting, nothing claimed, no multi-GB render
# resident, runner.log silent past the longest real job) and refuses after three
# restarts in an hour, and whose rule has 11 test cases -- eight of them about
# NOT firing.
#
# WHY schtasks.exe AND NOT Register-ScheduledTask. Same reason as
# mktask-autofill.ps1: a trigger repeating indefinitely is spelled
# `[TimeSpan]::MaxValue` there, which serialises to `P99999999DT23H59M59S`, and
# this box answers "The task XML contains a value which is incorrectly formatted
# or out of range" (HRESULT 0x80041318). `/sc MINUTE /mo 5` says it in a form
# this Windows accepts, survives a reboot on its own, and is the form the other
# banyan-* tasks were made with.
#
# SYSTEM, not the artvn SID. The old registration ran Limited as artvn, which is
# the weakest possible context for a watchdog: `tasklist` there cannot see every
# process, and a probe that cannot see the runner reports the runner missing.
# SYSTEM sees the whole process table and needs no logon -- and the entire claim
# of this task is that a wedged card gets fixed when no human is present.
#
# Idempotent -- /F replaces the registration. Re-run after any change to
# box-runner-watchdog.cmd. `python3 pipeline/runner_watchdog.py --deploy` does
# all of this from the Mac, including sending the files, and is the way in.
$ErrorActionPreference = 'Stop'

# Preserve the script being replaced, do not delete it: the change has to be
# reversible by hand from the box alone, without a checkout or a network.
$old = 'C:\banyan-farm\runner-watchdog.ps1'
$kept = 'C:\banyan-farm\runner-watchdog.ps1.retired-v4'
if ((Test-Path $old) -and -not (Test-Path $kept)) {
    Move-Item -Path $old -Destination $kept
    Write-Output "retired: $old -> $kept"
} elseif (Test-Path $kept) {
    Write-Output "already retired: $kept"
}

$out = schtasks /create /tn 'banyan-runner-watchdog' /tr 'C:\banyan-farm\box-runner-watchdog.cmd' `
    /sc MINUTE /mo 5 /ru SYSTEM /rl HIGHEST /f 2>&1
Write-Output ($out -join "`n")
if ($LASTEXITCODE -ne 0) { throw "schtasks /create failed rc=$LASTEXITCODE" }

# Fire one tick now, so registering it is also a test of it. Safe by
# construction: with a job claimed or a render resident the rule refuses to act,
# and it prints its reasoning either way.
schtasks /run /tn 'banyan-runner-watchdog' | Out-Null

$i = Get-ScheduledTaskInfo -TaskName 'banyan-runner-watchdog'
$t = Get-ScheduledTask -TaskName 'banyan-runner-watchdog'
Write-Output "registered: $($t.TaskName) state=$($t.State)"
Write-Output "  action   : $($t.Actions[0].Execute)"
Write-Output "  runas    : $($t.Principal.UserId)"
Write-Output "  repeat   : $($t.Triggers[0].Repetition.Interval)"
Write-Output "  next run : $($i.NextRunTime)"
