# The Mac farm, actually wired — 2026-08-18

`farm-six-macs.md` is a **design** doc ("Status: design only, nothing wired",
2026-08-10). This is the part that now works, written down because it was
rediscovered the slow way and the next session should not have to.

## What is real

Four Macs render stills in parallel today. Measured 2026-08-18 (four beats in
one pass); macbook4 added 2026-08-19:

| host | chip | weights | one 832x1216 / 40-step plate |
|---|---|---|---|
| macbook1 | M1 Max | `verdict: READY` | 70.6 s |
| macbook2 | M1 Pro | `READY` | 137.7 s |
| macbook3 | M1 Pro | `READY` | 137.3 s |
| macbook4 | M1 Pro, 32 GB | `READY` (2026-08-19) | 139.6 s |
| macbook5 | M1 Pro | not checked | **no python3** — Xcode CLT never installed |
| rtx5070  | — | — | 192.168.3.153 times out |

**macbook4, onboarded 2026-08-19.** It needed no provisioning: the venv
(`~/banyan-farm-macbook4/venv`, py3.11.16, torch 2.13.0 + MPS, diffusers
0.29.2) and the 6.5 GB HF cache were already on disk from the 08-15 round, so
bring-up was the three rsync/preflight commands below and nothing was copied
over WiFi. Its first plate (beat 19 r1) came back **byte-identical** to the
r1 plate already in `farm-out/` — same `png_sha256`
`3cc0b6bc…`. That is the cheapest possible proof a new machine renders
truthfully, and it is worth asking for on every future onboard: file a beat
whose plate the repo already owns and compare the sha, rather than eyeballing
a picture nothing can be diffed against.

**It was NOT dead, it was asleep on WiFi.** `hostname does not resolve` above
was measured during one of the association drops STATE.md 2026-08-16 already
diagnosed. On 08-19 mDNS resolved `192.168.3.190` while ARP stayed
`(incomplete)` and every ping failed for ten minutes; a WoL magic packet to
`bc:d0:74:a0:7f:6d` (read out of macbook3's ARP cache — this Mac's was empty)
plus sustained pings and it answered with `up 14 days`. **Never conclude a farm
Mac is gone from one failed ssh.** Sweep, WoL, retry for five minutes first.

Three beats finished in ~2.3 min wall clock against ~5.7 min if they had been
queued one after another on one machine. That ratio is the whole argument for
using them.

## Bring-up, per Mac — three commands, no clone

**Do not `git clone`.** The repo now carries 38 mp4s and hundreds of frames;
a `--depth 50` clone was still running when two separate attempts were killed.
The Macs need code and text, not media.

    ssh <host> 'mkdir -p ~/banyan-city/pipeline'

    rsync -a --include='*/' --include='*.py' --include='*.yaml' --include='*.yml' \
          --include='*.md' --include='*.txt' --include='*.json' --exclude='*' \
          --exclude='__pycache__/' pipeline/ <host>:~/banyan-city/pipeline/

    rsync -a --include='*/' --include='*.md' --include='*.yaml' --exclude='*' \
          --exclude='takes/' --exclude='clips/' genomes/ <host>:~/banyan-city/genomes/

The genomes half is NOT optional and copying `plate_scratch.py` alone does not
work. Its import chain is `plate_scratch -> render_local -> generate_shots`,
and `render_local.approved()` reads the node's leaf yaml to check founder
approval. Uploading files one at a time as each `ModuleNotFoundError` appears
is how the first attempt went; the rsync above is the short version.

## Preflight is not optional

    scp pipeline/mac_preflight.py <host>:/tmp/ && ssh <host> 'python3 /tmp/mac_preflight.py'

Wants `verdict: READY`, `problems: []`, `zero_mib: 0`. macbook1 and macbook3
once rendered SDXL as pure noise for days on a UNet that was 88% / 93% holes
while its size, file count and manifest all compared equal. Both hash clean as
of 2026-08-18. It needs no venv, no torch and no network, so there is no excuse
to skip it.

## Rendering

    ssh <host> '~/banyan-farm-<host>/venv/bin/python3 \
        ~/banyan-city/pipeline/plate_scratch.py --beat <n> [--dry]'

`--dry` measures tokens and draws nothing; run it first on a machine you have
not used before. Beats with inline prompts: **5, 8, 9, 10, 11, 14, 15, 17, 19,
20** — don't trust that list, `mac_enqueue.known_beats()` reads them out of
`plate_scratch.py` and is the one that cannot go stale. Output lands in
`~/banyan-city/farm-out/ep2-b<NN>-mac-plate-<MMDD>/` ON THAT MACHINE; pull it
with `mac_enqueue.py --collect` (additive, never overwrites) or `scp`.

`plate_scratch.py` refuses more than one seed without
`--i-have-seen-a-sample`, which is the one-sample rule enforced in code.

## There IS a Mac queue now — prefer it to the ssh one-liner

This section said "there is no Mac queue" when the runbook was written. There
is: `pipeline/mac_worker.py` drains `~/banyan-queue/{ready,running,done,failed}`
on each Mac and `pipeline/mac_enqueue.py` files into it. Start the worker once
per machine, then never hold a live ssh session across a render again:

    ssh <host> 'mkdir -p ~/banyan-queue && nohup caffeinate -dimsu python3 \
        /Users/<host>/banyan-city/pipeline/mac_worker.py \
        >> /Users/<host>/banyan-queue/worker.log 2>&1 &'

    python3 pipeline/mac_enqueue.py --status
    python3 pipeline/mac_enqueue.py --host macbook4 --beat 19
    python3 pipeline/mac_enqueue.py --collect          # scp the frames back

`HOSTS` at the top of `mac_enqueue.py` is a hardcoded tuple — a newly onboarded
Mac is invisible to `--status`, `--spread` and `--collect` until it is added
there. That is the step that gets forgotten.

## What is still missing

**No autofill.** The 5090 tops `ready` up from `backlog/` every three minutes;
the Macs have no equivalent, and `mac_worker` deliberately never authors work,
so an empty `ready/` stays empty. The machines now survive a lane walking away
mid-render, but not a lane that files nothing. Only two specs on disk carry
`runner: local-mac`.
