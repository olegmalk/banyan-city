# This job ran TWICE on 2026-08-19, and the second run is a duplicate

**The files in this directory are from the FIRST run and the second run
interchangeably, because they are byte-identical.** That is not a guess — it is
measured below. Nothing here is stale and nothing needs re-pulling; this note
exists so a reader who finds two completed job records for one job id does not
have to work out which artifact they are looking at.

## The two runs

| | job file | started (UTC) | outcome |
|---|---|---|---|
| first | `ep2-b19-dropmotion-0819-1787128259.json` | 08:30 | rc=0, published, **this is the run the verdict was scored on** |
| duplicate | `ep2-b19-dropmotion-0819-1787129173.json` | 08:46:22 | rc=0, published over the same courier directory |

Both are in the box's `done/`. The verdict in
`pipeline/jobs/ep2-b19-dropmotion-0819.yaml` (`verdict_0819`) was scored against
the **first**, and it applies unchanged to the second.

## What the duplicate proves, which is the one thing salvaged from it

**LTX i2v is bit-exact reproducible on this box at a fixed seed.** Same spec,
same seed 20260819, two independent runs 16 minutes apart, each with its own
model load and its own libx264 conditioning round trip:

```
333ea495a33d6043fa612a303bcfb9a7f1fc112fc07af3fdd0de5763180a13e6  19-the-drop-LTX-sapgloss-0819.mp4      IDENTICAL
ea42d2e4b99bd4e31387e5864d0ac22bfc880d564e95b054ddcafb3e710464de  b19-init-704x1280.png                  IDENTICAL
316497b3084b45e53ef6c2112c5018b98a9245b82ad0f3b0a163b7168f466d4f  ...mp4.meta.yaml                       IDENTICAL
68586cd6a02d1f55742202f326d60a5b3317ee7751148ef00e0a61438084dab5  b19-motion-prompt.txt                  IDENTICAL
28c235b70d12bd94a9685d30e86669b31f2b9254eb0e6231992fa5e41b69b065  b19-negative.txt                       IDENTICAL
```

**The only file that differs is `bench-b19-dropmotion.jsonl`**, which records
wall-clock seconds and peak memory and therefore cannot match. The committed copy
on `main` is the first run's; the farm branch carries the second's.

Nobody had measured this determinism before, so it is worth stating plainly and
also worth stating narrowly: **one spec, one seed, two runs, same machine, same
weights.** It does not establish reproducibility across machines, driver
versions or torch builds.

## Why it happened

**`box_enqueue.py` has no duplicate-id guard on its direct path.** Established
from disk, not inferred:

- The box's `autofill.log` shows `BACKLOG EMPTY` at **every** tick across the
  window — 08:36, 08:39, 08:42, 08:45, 08:48, 08:51. There is **no fill event at
  08:46**, so the duplicate never came through `backlog/`.
- There is **no `.SUPERSEDED` parked file**, so `box_autofill.plan_fill` — which
  *does* dedupe, by skipping any backlog entry whose id is already in
  `ready/`/`running/`/`done/`/`failed/` — never saw it.
- Therefore the duplicate was written **straight into `ready/`**, which is what
  `box_enqueue.py <spec>` does when `--backlog` is omitted, and the runner
  claimed it.

`box_enqueue`'s only collision check is on **payload paths already claimed by a
LIVE job** (`ready/` or `running/`). By 08:46 the first run was in `done/`, so
nothing objected. **The dedupe exists one layer downstream of the tool that
needed it.**

The second call came from this lane being interrupted and re-logged twice while
the render was in flight; a resumed copy re-ran the file-and-fire step. That is
the "resumed agents fork" hazard meeting a tool with no idempotency check — the
agent-side mistake was ordinary and recoverable, and the tool turned it into
264s of GPU on a question its own first run had already answered.

**Prevention is filed as a tooling rung in `pipeline/work-ladder-0819.md`:** an
idempotency refusal in `box_enqueue` — same job id, or same spec sha, already
present in `ready/`, `running/`, `done/` or `failed/` ⇒ refuse, with an explicit
`--again` to override for a deliberate re-run.
