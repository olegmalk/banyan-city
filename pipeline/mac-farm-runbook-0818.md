# The Mac farm, actually wired — 2026-08-18

`farm-six-macs.md` is a **design** doc ("Status: design only, nothing wired",
2026-08-10). This is the part that now works, written down because it was
rediscovered the slow way and the next session should not have to.

## What is real

Three Macs render stills in parallel today. Measured 2026-08-18, four beats in
one pass:

| host | chip | weights | one 832x1216 / 40-step plate |
|---|---|---|---|
| macbook1 | M1 Max | `verdict: READY` | 70.6 s |
| macbook2 | M1 Pro | `READY` | 137.7 s |
| macbook3 | M1 Pro | `READY` | 137.3 s |
| macbook5 | M1 Pro | not checked | **no python3** — Xcode CLT never installed |
| macbook4 | — | — | hostname does not resolve |
| rtx5070  | — | — | 192.168.3.153 times out |

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
not used before. Beats with inline prompts: **5, 8, 9, 10, 11, 14, 17, 20**.
Output lands in `~/banyan-city/farm-out/ep2-b<NN>-mac-plate-<MMDD>/` ON THAT
MACHINE and must be pulled back with `scp` — nothing collects it for you.

`plate_scratch.py` refuses more than one seed without
`--i-have-seen-a-sample`, which is the one-sample rule enforced in code.

## What is still missing, and it is the important part

**There is no Mac queue.** The 5090 has `C:\banyan-queue` with an autofill task
topping `ready` up from `backlog` every three minutes; the Macs have nothing.
Every plate these machines have ever drawn was hand-driven over ssh, which is
exactly why `origin/farm-results-m1pro`'s last heartbeat is 2026-08-07 while
mac plates kept appearing in `farm-out` through 08-17: lanes drove them by hand
and the machines went idle the moment a lane stopped watching. Only two specs
on disk carry `runner: local-mac`.

Until a backlog exists, these three are useful *while someone is driving them*
and idle otherwise. That is a real limit and should not be described as a farm.
