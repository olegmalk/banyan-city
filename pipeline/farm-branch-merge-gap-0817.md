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

- **A branch-divergence check in CI or the heartbeat:** count paths present in
  `origin/farm-results-rtx5090:farm-out/` and absent from `main`. Non-zero is a
  number that should always be zero, and it names the stranded job ids directly.
  This is a two-command check and it is the one to build first.
- **Cross-check `done/` against `main`:** every `done/` job with rc=0 and a
  `farm-out` publish step should have its directory in `main`. A job that
  succeeded and whose results are not in the repo is a leak by definition, and
  this catches strandings the branch check would miss (results published to a
  path no branch tracks).
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
- **Two farm-out directories are genuinely invisible to the box:**
  `farm-out/ep2-b14-mac-plate-0817` (14 files) and
  `farm-out/ep2-b14-fieldcomp-0817` (7 files). Both were committed locally and
  are on neither `origin/main` nor `farm-results-rtx5090`, so they exist in the
  worktree and nowhere the box can reach. **No spec references either one yet,
  so no lane is blocked right now** — but the first spec that points an init at
  `C:\banyan-farm\banyan-city\farm-out\ep2-b14-...` will fail rc=2 `init not
  found`, which is precisely how `ep2-b10-attrbind-eyewear-0817` died at 12:14Z
  today. The other eleven farm-out dirs in the gap are the recovered sets, and
  the box already holds those under `courier-box\farm-out\`, so they cost
  nothing.
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
today.** The hold is affordable, and the thing to watch is the first b14 spec
that inits from the clone.
