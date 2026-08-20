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
| macbook5 | M1 Pro, 32 GB, macOS 26.4 | `READY` (2026-08-20) | 147.6 s |
| macbook6 | M1 Pro, macOS 26.6.1 | provisioning 2026-08-20 | see "Onboarding 5 and 6" |
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

**macbook5 passed the same proof on 2026-08-20** — beat 19 r1, seed 20260819,
`png_sha256` `3cc0b6bc…` again, 147.6 s. So that sha is now reproduced on an M1
Max and three separate M1 Pros across macOS 26.4 and 26.6, which retires the
"maybe it is only stable per machine" caveat: a mismatch on a new Mac is a real
defect, not a machine-class difference, and should be treated as one.

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

## Onboarding 5 and 6 — what a Mac that was NEVER provisioned costs

macbook4's bring-up was three commands because its venv and its 6.5 GB cache
were already on disk. macbook5 and macbook6 (2026-08-20) were bare, and a bare
Mac is a **five**-part job, not a three-part one. In order, with the traps:

**1. Xcode CLT, headless.** Neither had `python3` at all. The GUI-less install
works and needs no keyboard:

    ssh <host> 'touch /tmp/.com.apple.dt.CommandLineTools.installondemand.in-progress'
    ssh <host> 'softwareupdate -l'          # read the exact label
    # then, DETACHED -- it runs 20-60 min and an ssh session that drops kills it:
    ssh <host> "cat > /tmp/clt.sh <<'EOS'
    touch /tmp/.com.apple.dt.CommandLineTools.installondemand.in-progress
    printf '%s\n' '<sudo-pw>' | sudo -S -p '' softwareupdate -i '<label>' --verbose
    rm -f /tmp/.com.apple.dt.CommandLineTools.installondemand.in-progress
    echo DONE
    EOS
    chmod +x /tmp/clt.sh; nohup caffeinate -dimsu /tmp/clt.sh > /tmp/clt.log 2>&1 &"

Both machines offered `Command Line Tools for Xcode 26.6-26.6`. Verify with
`python3 --version` (3.9.6) and `xcode-select -p`. The touch file is what makes
`softwareupdate` list CLT at all; remove it after or the machine keeps thinking
an install is pending.

**2. CLT python is NOT the render python.** `/usr/bin/python3` is 3.9.6.
macbook4's venv is **uv-managed CPython 3.11.16** — `pyvenv.cfg` says
`uv = 0.12.5`, `home = ~/.local/share/uv/python/cpython-3.11-macos-aarch64-none`.
There is no `pip` module in that venv; `pip freeze` returns
`No module named pip` and reads as an empty venv when it is nothing of the kind.
Enumerate it with `importlib.metadata` instead. CLT is still needed — `python3`
is what starts `mac_worker` and `mac_preflight` — but torch never touches it.

**3. The 31-package lockfile.** Copy macbook4's exact versions, not "latest":
torch 2.13.0, diffusers 0.29.2, transformers 4.44.2, accelerate 0.33.0,
tokenizers 0.19.1, numpy 1.26.4, safetensors 0.8.0, pillow 12.3.0.

    ssh <host> 'curl -LsSf https://astral.sh/uv/install.sh | sh'
    ssh <host> 'uv venv --python 3.11 ~/banyan-farm-<host>/venv'
    ssh <host> 'uv pip install --python ~/banyan-farm-<host>/venv/bin/python3 -r /tmp/reqs.txt'

**`export UV_HTTP_TIMEOUT=600` OR THIS STEP LIES TO YOU.** uv's default HTTP
timeout is 30 s. On the farm's link that is not enough for the transformers
wheel, and the failure mode is the dangerous kind: `uv pip install` exits 1
with `Failed to download distribution due to network timeout`, but the venv
directory and its `bin/python3` **still exist**, so every `test -x` and every
`--version` check passes on a venv with no torch in it. Gate on
`python3 -c 'import torch, diffusers, transformers'`, never on the path.
Wrap the install in a retry loop as well; one uv installer download died with
`curl: (35) Recv failure` purely from link contention.

**4. The 6.5 GB HF cache comes over the LAN, never from the internet.** It is
`models--cagliostrolab--animagine-xl-3.1` (unet 5.1 GB, text_encoder_2 1.39 GB,
vae 246 MB, text_encoder 167 MB — no fat to trim) plus
`models--openai--clip-vit-large-patch14` (3.6 MB):

    rsync -a ~/.cache/huggingface/hub/models--cagliostrolab--animagine-xl-3.1 \
             ~/.cache/huggingface/hub/models--openai--clip-vit-large-patch14 \
             <host>:~/.cache/huggingface/hub/
    rsync -a ~/.cache/huggingface/version.txt \
             ~/.cache/huggingface/version_diffusers_cache.txt <host>:~/.cache/huggingface/

**Budget hours, and do not run two of these at once.** Measured 2026-08-20:
**every Mac in the farm is associated to 2.4 GHz 802.11n, channel 6, 20 MHz** —
1-4 included — and the whole farm shares that one medium. Two parallel cache
copies plus a CLT download measured **887 KB/s and 546 KB/s**, i.e. ~1.4 MB/s
aggregate, so 13 GB of provisioning is a ~2.5 hour physical dependency. The
machines are all a/b/g/n/**ax** capable and 5 GHz APs are visible to them, so
the ceiling is an association choice, not hardware — but re-homing a headless
Mac's Wi-Fi over its own ssh session risks losing the machine to a room nobody
is in, so it was not attempted. Serialize instead: `kill -STOP` the second
rsync while the first machine's toolchain lands, `kill -CONT` it after.
Serializing paid — with the CLT and wheel downloads out of the way the single
remaining copy ran at ~2 MB/s, better than double what it managed while racing.
Two cautions: **`kill -STOP` on the rsync pid you can see does not stop the
transfer** (that is the parent; its children keep streaming, and macbook6 took
on 600 MB while "paused" — suspend the process group or just accept it), and
the whole ~2.5 h is unattended, so chain it on sentinels (`while ps -p <rsync>;
do sleep; done` into preflight into the render) rather than sitting on it.

**5. `HOSTS` in `mac_enqueue.py` AND `~/.ssh/config`.** The registration step
is two files, not one: `mac_enqueue` ssh's by the *short* name, so a host that
is only reachable as `macbook6s-macbook-pro.local` is invisible to it. macbook6
had no `~/.ssh/config` alias at all.

## Bring-up, per Mac — three commands, no clone

*(this is the macbook4 path — a machine that already has venv + cache; a bare
Mac needs the five steps above first)*

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

Wants `verdict: READY`, `problems: []`, `zero_mib: 0`. **It reports
`torch: "MISSING: No module named 'torch'"` and `mps: false` on a perfectly
healthy node** — it runs under CLT `python3` 3.9.6, which is not the render
venv, by design (it needs no venv, no torch and no network). Those two lines
are not the verdict; `problems: []` is. Do not "fix" them. macbook1 and macbook3
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
