# Where the candidate corpus actually lives — 2026-08-10

`.gitignore` keeps candidate render media out of the tree on purpose (`takes/`
by extension, `review/` the same way). The rule is right: pick-of-N frames are
~1.2 MB each and dozens per beat, and only the frame the founder picks gets
promoted into git. But it has a cost that had never been written down:

> **A clean `git status` over `takes/` means "ignored", not "safe".**

Nothing in the repo recorded that those frames existed, so nothing could tell
you whether a copy survived somewhere else. This file is that record, and
`pipeline/takes_backup.py` is the tool that keeps it honest.

## What was measured (2026-08-10)

Node **002b-first-citizen** — episode 2's entire candidate corpus, 21 beats,
0 canon stills picked so far:

| | files | bytes |
|---|---|---|
| `takes/stills/*.png` (gitignored) | 237 | 286,970,393 (273.7 MiB) |
| `takes/stills/*.png.meta.yaml` (**tracked**) | 216 | ~0.6 MiB |
| whole `takes/` tree | 453 | 287,641,881 |

Sidecars were never at risk — the ignore rule matches extensions, not the
directory, exactly so the provenance stays visible. The pixels were the
exposure.

**The scare was smaller than it looked, and the reason matters.** Hashing all
237 stills against every PNG on the rtx5090 box (`C:\banyan-farm`, 815 files)
found **232 of 237 already present byte-identical** — they were rendered there
and pulled down, and the per-run `...\out\` directories still hold the
originals under their run-local names. Only **5 files (6.06 MiB)** existed
nowhere but this laptop:

```
01-cold-open-i2i-r2s0-str045.png
01-cold-open-i2i-r2s3-str035.png
01-cold-open-i2i-r2s3-str055.png
01-cold-open-i2i-r3s3-nub-str035.png
01-cold-open-i2i-r3s3-nub2-pea-str035.png
```

Those are the 2026-08-06 beat-01 img2img repaints, rendered on the Mac's MPS
rather than the box — and they are also the five stills in the corpus with **no
`.meta.yaml` sidecar at all**, so git held no trace of them whatsoever. That is
the shape of the real risk: not the big corpus, but the handful of frames drawn
somewhere off the normal path.

Two things that were *not* at risk, both verified rather than assumed:

- **Node 001's `takes/`** — 373 files on disk, 373 tracked. The
  `!genomes/sapling/nodes/001-capability-inventory/takes/**` un-ignore at
  `.gitignore:48` is real and complete.
- **The sidecars** — 216 of them, tracked, including the full recipe, prompt,
  negative and reasoning for every round.

Still open, measured but not acted on (see "What is not covered"):
**`review/` holds 227 ignored media files, 156.3 MiB, of which 96 have no
byte-identical copy on the box.**

## Re-measured 17:35, same day — and the scary number was a counting error

A later pass counted **457** `takes/**/*.png|jpg` on disk and read it as "the
237 nearly doubled while the card rendered all afternoon". It did not. 457 is
**both nodes added together**, and the split is the whole answer:

| | files | where it lives |
|---|---|---|
| 001's stills | 216 | **tracked in git**, all 216 present in `origin/main` |
| 002b's manifest corpus | 237 | laptop + box archive, byte-identical |
| 002b's `04-the-footnote-wave1-*` | 4 | **tracked in git** (force-added at `4d3ffc5`), in `origin/main` |
| | **457** | |

Nothing rendered into `takes/` after **12:38** — the afternoon's output went to
`review/`, which is a different (and still open) problem. So the corpus did not
grow by 220 files; the count changed because it started including a node whose
stills were never at risk.

Re-verified rather than assumed, by hash on both ends:

- Every one of 002b's 237 manifest stills and 216 sidecars is on the box
  **byte-identical** — 453/453, no truncation, no same-name-different-bytes.
- The 4 new stills were the only files missing anywhere, and only from the box;
  git already held them. They have since been copied over and hashed at both
  ends, 9/9 match (4 png + 4 yaml + a per-round `.sha256`).
- Manifest rebuilt to **462 files, 291,247,279 bytes**; `verify` now says
  `462/462 match  /  TAKES-VERIFY: PASS` with nothing unrecorded.

**Files that exist in exactly one place: zero.** Every still in `takes/` is on
at least two machines, and 220 of the 457 are in GitHub as well.

**The tool has no schedule and never had one.** `takes_backup.py` is invoked by
hand; CI runs `test_takes_backup.py` (that the tool works), never the tool
itself. No crontab entry, no LaunchAgent, nothing in `farm-queue.yaml`. Between
06:42 and 17:35 the manifest silently fell 9 files behind, which is exactly the
failure this file was written to make visible — and the reason `verify` prints
`UNRECORDED` instead of staying quiet. Rebuild it after every round.

## What was done

1. **A second physical copy, on the box**, at
   `C:\banyan-farm\take-archive\002b-first-citizen\stills\` — all 462 files
   (453 at 06:42, +9 at 17:41) under their repo filenames, not scattered
   run-local names. 267.9 GB free there; the transfer took 93 s over the LAN.
2. **`takes/MANIFEST.sha256`, tracked in git** — sha256 and path for all 462
   files. Text, ~40 KB, so it costs the repo nothing and it is what turns an
   off-repo copy into a *restorable* one: without it, the box copies are
   duplicates nobody can map back to filenames.
3. **`pipeline/takes_backup.py`** — `manifest` writes it, `verify` checks any
   copy against it. Tests in `pipeline/test_takes_backup.py`, wired into CI.

**Why not just track the PNGs.** The pack is already 1.79 GiB; +274 MB of
incompressible PNG is ~15% growth that git can never give back, and reversing
a rule whose comment explains itself is a design decision, not a chore. It is
listed below as the founder's call, not taken here.

**Two copies on two unbacked machines is not "backed up".** Neither this laptop
(no Time Machine destination configured, no external volume mounted, 8.2 GiB
free of 460) nor the box has any backup of its own. What changed today is that
losing either one no longer loses the corpus, and the manifest proves whether
what survives is intact. Off-site is still a founder decision.

## Restore procedure

If the corpus is gone from the laptop and the box still lives:

```sh
mkdir -p genomes/sapling/nodes/002b-first-citizen/takes/stills
cd       genomes/sapling/nodes/002b-first-citizen/takes/stills
scp rtx5090:'C:/banyan-farm/take-archive/002b-first-citizen/stills/*' .
cd /Users/artovonkugler/banyan-city
python3 pipeline/takes_backup.py verify sapling 002b-first-citizen
# expect: 462/462 match  /  TAKES-VERIFY: PASS
```

`rtx5090` is an ssh alias for 192.168.3.157 (see `~/.ssh/config`); the box uses
`cmd.exe` as its shell, so quote Windows paths as above. A copy of the manifest
sits at `C:\banyan-farm\take-archive\002b-first-citizen\MANIFEST.sha256`, so the
archive is self-verifying even without the repo:

```sh
shasum -a 256 -c genomes/sapling/nodes/002b-first-citizen/takes/MANIFEST.sha256
```

If the *box* is gone instead, re-push from the laptop:

```sh
cd genomes/sapling/nodes/002b-first-citizen/takes/stills
ssh rtx5090 'mkdir C:\banyan-farm\take-archive\002b-first-citizen\stills'
scp *.png *.meta.yaml rtx5090:'C:/banyan-farm/take-archive/002b-first-citizen/stills/'
```

This was **rehearsed end to end on 2026-08-10**, not just written: the whole
453-file archive was pulled back off the box into a scratch directory and
verified against the manifest at 453/453 before the rehearsal copy was deleted.

## Keeping it true

The manifest goes stale the moment a new round renders. After any render that
adds candidates:

```sh
python3 pipeline/takes_backup.py manifest sapling 002b-first-citizen
# then re-push the new frames to the box archive (scp block above)
```

`verify` reports unrecorded files as `UNRECORDED` and says
`PASS (manifest stale — N unrecorded)` rather than failing, because a new frame
is not a lost one — but a stale manifest is exactly the state this document
exists to prevent, so rebuild it.

## What is not covered

- **`review/`** — 227 ignored media files, 156.3 MiB, **96 of them single-copy**
  (no byte-identical twin on the box). Same pattern would fix it. Not done here
  because live lanes are writing into `review/` right now and copying under an
  active writer is how you archive a half-written file. Worth doing as its own
  pass once the card lanes settle.
- **Other nodes' `takes/`** — only 001 (tracked) and 002b (this) exist today.
  `takes_backup.py` takes any genome/node, so the same two commands cover the
  next one.
- **Off-site anything.** Both copies are in the same room.

## Founder's calls, not the steward's

1. **Should take corpora be tracked in git after all?** The measured cost is
   ~274 MB on a 1.79 GiB pack for 002b alone, permanent, and it would grow with
   every node. The alternative in place today is manifest-in-git plus pixels on
   a second machine.
2. **Off-site backup.** Everything durable right now is two machines on one
   LAN. Any off-site option costs money, which is founder-reserved; none was
   set up or priced here.
3. **Do the 5 sidecar-less repaints deserve provenance?** They are candidates
   with no `.meta.yaml`, so the manifest is currently the only record that they
   exist. Backfilling a sidecar means asserting what recipe drew them, which is
   a claim about the work rather than a chore.
