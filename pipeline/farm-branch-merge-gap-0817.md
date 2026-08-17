# The gap: nothing merges `farm-results-rtx5090` back to `main` (2026-08-17)

Found while recovering the eleven stranded sets in
`queue-failure-triage-0817.md`. The eleven sets are the symptom; this is the
defect, and it is permanent rather than a one-off, because no step anywhere
performs the merge and nothing notices that it has not happened.

## What actually happens today

```
sampler writes    C:\banyan-farm\out-b05-scene\05-the-patrol-ipa-r0-w015-s0.png
publish copies    C:\banyan-farm\courier-box\farm-out\ep2-b05-scene-0814\...
runner commits    courier-box is a CLONE, on branch farm-results-rtx5090
runner pushes     origin/farm-results-rtx5090     <-- the chain ends here
                  ...................................................
main                                              <-- nothing arrives
```

`C:\banyan-farm\courier-box` is not a staging directory. It is a git clone whose
checked-out branch is `farm-results-rtx5090`, and the runner commits into it and
pushes. That part is sound: the bytes are committed, checksummed, pushed to
origin, and attested by a `.sha256` manifest. MEMORY's "copy artifacts into
`courier-box\farm-out\` and the runner pushes them itself" is accurate as far as
it goes.

The chain has no last link. There is no merge, no cherry-pick, no PR, no
scheduled job, and no guard that compares the two branches. Results accumulate
on a branch that nothing reads.

## Why it stays invisible for days

**Every question anyone asks is asked of `main`.** `git ls-files`, the site
build, `build_shotboard.py`, the review pages, the release picture, and every
triage that has ever run — all of them read the working tree or `HEAD`. A set
sitting on `farm-results-rtx5090` answers "does this exist?" with **no**, in
exactly the same voice as a set that was never rendered.

That is what happened on 2026-08-17. The triage ran `git ls-files farm-out/<job>`
for six sets, got 0 for all six, correctly concluded they were not in the repo,
and then reasonably inferred they existed in exactly one place and were one disk
failure from gone. They were on origin, pushed, since 08-14. The inference was
wrong and the evidence for it was clean, which is the dangerous combination: a
`failed/` entry plus an unmerged branch is indistinguishable from lost work, and
it costs the same as lost work, because everything downstream treats absence
from `main` as absence.

Eleven sets, not six, had accumulated this way — 60 scene/wave images, the b01
styleprobe arms, the b01 shape mp4, and both clips from the console-killed jobs
whose retries succeeded. The oldest was three days old. Nobody had looked at any
of them.

## Where the merge should happen

The push is the only moment when the set is known-complete, known-manifested and
known-attributable to a job id, so the merge belongs immediately after it, in the
same process, as part of "publish" — not in a separate sweep. Concretely, the
runner's courier step should, after a successful push of a job's results:

1. fetch `origin/main`,
2. take **only that job's** `farm-out/<job-id>/` paths onto `main`
   (`git checkout origin/farm-results-rtx5090 -- farm-out/<job-id>` is exactly
   what the recovery did by hand, and it is the right primitive: the bytes come
   from git's own checksummed objects, not a second copy),
3. verify the arrivals against the set's own `.sha256` before committing,
4. commit with explicit paths and push `main`.

Two properties matter more than the mechanism. **Per-job, not per-branch:** a
whole-branch merge would drag every historical result into `main` at once and
would conflict with live lanes; one job's directory is a disjoint set of new
files and cannot conflict with anything. **Manifest-verified at the destination,**
because a courier that reports success while copying nothing is the same defect
class this repo hit three times on 2026-08-17 — see `publish_farm_out.py`.

## What should own it

The runner, in `farm_worker.py`'s courier path, because it is the only component
that knows a job finished and holds credentials to push. The alternative — a Mac
lane sweeping the branch periodically — is worse for the reason this gap exists:
it is a step someone must remember, and the record shows nobody did for three
days.

Note the constraint that makes this a design decision rather than a patch: **the
same push publishes the site.** Vercel deploys on every push to `main`, so an
auto-merging courier deploys whatever else is sitting in `main` at that moment.
That is not a reason to skip the merge; it is a reason the merge should carry
only `farm-out/` paths and never rebase or carry other lanes' commits.

## How someone would notice next time

The reason three days passed is that no check compares the branches. Any one of
these would have caught it on day one, and the first is cheap enough to be a
lint:

**BUILT: `pipeline/check_results_merged.py`.** Both halves proposed below were
implemented, and measuring them changed both. What was proposed as one
always-zero gate turned out to be one gate, one bounded worklist and one number
that is never zero and must never gate. The reasoning is in that file's
docstring; the short version:

- **"count paths on the results branch and absent from `main`; it should always
  be zero" is FALSE.** Measured: 716 job dirs / 8850 paths on the branch, 26 dirs
  in `main`. `main` holds a curated subset **by policy** — `.gitignore` says so
  outright: "Media does not go into git; only the frame the founder picks does,
  promoted deliberately." A gate reading 8850 is as useless as one reading 0
  always; nobody reads either. So the divergence is printed as a number **with
  its reason attached** and never decides the exit code.
- **"any rc=0 job whose published dir is not in `main` is a leak by definition"
  is also false** — 1095 violations across 776 jobs, same cause.
- **What does gate, because it can honestly be zero:**
  1. **Set consistency.** A `.sha256` with no lines, or a line count disagreeing
     with the directory's file count, means a publish step attested to something
     it never copied. Across all 716 dirs: 697 consistent, 0 mismatched, **1
     empty** — `ep2-b01-final055-r2`, the live instance of the defect
     `publish_farm_out.py` now refuses at source. One known instance is a gate
     that can reach zero and stay there.
  2. **A `failed/` entry must not own a complete attested set.** If the board says
     a job failed while the branch holds a complete manifest-consistent set under
     that job's publish directory, the board is wrong about what is filmed. This
     is the eleven-set defect exactly, and it is a worklist that shrinks rather
     than a structural number.
- **The `done/` lookup is what makes gate 2 true.** Without it the gate reports
  15 entries and **9 are wrong**: `ep2-b04-goblin-ipa-content`,
  `ep2-b06-ipa-guardcast-0812`, `ep2-b08-refresh` and all six
  `ep2-goblin-design-d*` each have a *later* rc=0 run publishing into the same
  directory, so the set belongs to the success. Before believing a `failed/`
  entry, read `done/` for the same directory — the same lesson that nearly cost
  two re-rendered clips and five re-fired jobs today.

**Proof it fires, on real history rather than a fixture.** Run against the tree
the triage saw (`--main-ref 5f4cdb2a`) gate 2 names **exactly the seven** real
strandings — the six 08-14 scene sheets and `ep2-b01-shape` — and against `HEAD`
after the recovery it is **0**. The divergence count drops 9005 → 8850 and 716 →
705 dirs, which is precisely the 155 paths and 11 dirs recovered. Eleven checks
in `test_silent_gates.py`; five mutations that restore the pre-fix behaviour
verbatim are each caught. One of those mutations initially **survived**, because
the fixture stubbed `farm_out_paths` — the very function whose error handling was
under test — and swallowing its exception changed nothing. The fixture now patches
`git_out` one level down. A fixture must not stand in for the code it exercises,
and only the mutation run exposed that.

**Not wired into CI, deliberately.** CI clones a single branch, so
`origin/farm-results-rtx5090` is unreadable there and the check would exit
RC_CANNOT_CHECK on every run — and gate 1 is red today on the one real empty
manifest. A gate that is red on arrival trains people to skip it. It wants either
a fetch step plus that manifest cleaned up, or a home in the heartbeat where the
box already has both branches. The *tests* are in CI now, which is what protects
the logic.

Still worth doing and not built:

- **Make the failure-count question ask the right thing.** The triage's own
  method — `git ls-files` on `main` — is what produced the wrong conclusion. Any
  future audit of "what is filmed" must read `main` *and* the results branch, or
  it will report finished work as missing. Recording this here so the next audit
  does not have to rediscover it.

## Related but separate: `main` is 122 commits ahead of `origin/main`

The mirror image of the same principle — **a commit is not delivered until the
thing that reads it can see it** — one level up. Measured 2026-08-17, with
`origin/main` at `145a02d5` and the box's clone pulled to match it.

The push is being held deliberately: among those commits are rewritten beats and
a rewritten published line the founder has not read, and a push deploys
banyan.city, so pushing would put unread rewrites on the live site ahead of
STEWARDSHIP §6. The cost of holding is therefore worth stating precisely rather
than in the abstract.

**What the box cannot see, measured rather than assumed** (310 added / 25
modified paths in the gap):

- **The workhorse renderer is NOT affected.** `pipeline/ltx_i2v.py` — referenced
  1063 times across `pipeline/jobs/` and read from the clone at
  `C:\banyan-farm\banyan-city\pipeline\ltx_i2v.py` — is **identical** in
  `origin/main` and local `main`. So are `render_b01r9.py` and
  `runpod_render.py`, the only other clone-path scripts any spec invokes, and so
  are the 001 stills three specs read from the clone. Nothing currently
  renderable is blocked by a stale script.
- **Two farm-out directories are genuinely invisible to the box** — see the
  tripwire section below. The other eleven farm-out dirs in the gap are the
  recovered sets, and the box already holds those under `courier-box\farm-out\`,
  so they cost nothing.
- **`pipeline/wave-drafts.yaml` is covered by a different route and is current on
  the box.** `--sync-drafts` copies the repo's working file directly over every
  harness copy, bypassing the clone entirely: both `wave-goblin-prep` and
  `wave-scale-0816` are at `cbb3658e…` (local `main`), while the clone's own copy
  sits at `542879b1…` (`origin/main`). The samplers read the harness copies, so
  drafts are not a consequence of the hold.
- **`pipeline/canon.yaml` is modified in the gap and does not matter to the box.**
  The three specs that mention it do so in prose; the canon guards run at
  enqueue time on the Mac, against the local file. No box step reads it.
- Everything else in the gap — `review/ep2-demo-0817` (71 paths), the recovered
  `farm-out` sets, `pipeline/jobs` specs (27, read from the Mac at filing time,
  not from the clone), `pipeline/research`, and the new Mac-side scripts — is
  read on the Mac or not read at all. None of it reaches the box.

**Net: one future failure mode, two named directories, zero lanes blocked
today.** The hold is affordable, and the thing to watch is the tripwire below.

## THE LIVE TRIPWIRE: two beat-14 directories the box cannot reach

```
farm-out/ep2-b14-mac-plate-0817     14 files
farm-out/ep2-b14-fieldcomp-0817      7 files
```

Both are committed in the local worktree and are on **neither** `origin/main`
**nor** `farm-results-rtx5090`. They were made on a Mac, so no farm-out job ever
published them to the results branch, and the push hold keeps them off
`origin/main`. They therefore exist in exactly one place — the worktree — and
nothing the box reads can see them.

**The exact failure, when it comes.** The first spec that points an init at
either directory through the clone path

```
!! init not found: C:\banyan-farm\banyan-city\farm-out\ep2-b14-mac-plate-0817\...
```

exits **rc=2**, which is precisely how `ep2-b10-attrbind-eyewear-0817` died at
**12:14Z today**. The plate will not be missing; the clone will simply be unable
to see it, and the log will say "not found" either way. That is the whole reason
this is worth writing down: the message names the wrong cause, and someone will
spend the next hour looking for a plate that is sitting in the worktree.

**Likelihood: low but not zero.** A beat-14 lane is the only one that would hit
it, and beat 14 is parked pending a founder ruling, so nothing is aimed there
right now. `git ls-files` returns them, so any Mac-side check sees them and only
a box-side init fails.

**Do not resolve this by pushing.** Pushing would put unread rewrites on the live
site — that is what the hold exists for, and it is the founder's call, not a
lane's. The two ways to unblock a b14 job without touching the hold are to publish
the plate through a farm-out job so it reaches the results branch the way every
other plate does, or to stage it onto the box directly and point the spec at the
staged path rather than at the clone.

The check above does not catch this one, and cannot: it compares the results
branch against `main`, and these two directories are on neither. A stranding with
no branch at all is only visible as a diff between the worktree and `origin/main`,
which is why it is written here rather than automated.
