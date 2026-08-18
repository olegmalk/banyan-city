# The Vercel clone has stopped finishing — 2026-08-18, night

Three production deployments in a row have failed to get past `git clone`. I stopped
cancelling after the third, per the standing instruction, and I have **not** touched the
deploy architecture. This file is the evidence and the open decision, for a daytime
session with the founder awake.

## The symptom, stated precisely

Vercel builds print four lines and then either continue or go silent:

```
Running build in Cleveland, USA (East) – cle1
Build machine configuration: 4 cores, 8 GB
Cloning github.com/olegmalk/banyan-city (Branch: main, Commit: <sha>)
Previous build caches not available.
Cloning completed: <m:ss.mmm>          <- this line is the one that matters
```

**Two red herrings to kill before anyone else chases them:**

1. `Previous build caches not available.` is printed on **healthy** builds too — it is on
   the last successful production deploy. It is not the symptom and it is not a clue.
2. Today's `CANCELED` count is 28, and most of those are **our own build guard working as
   designed**: `pipeline/vercel-ignore-build.sh` returns SKIP when no site input changed,
   and Vercel records that as CANCELED. Two of the deploys that looked wedged had in fact
   cloned successfully and were then skipped on purpose. Counting them as failures
   overstates the problem.

The real marker is a missing `Cloning completed:` line.

## The measurements

Clone durations on `main`, newest last, same repo, same region, same 4-core/8 GB machine:

| Commit | Age at reading | Clone | Outcome |
|---|---|---|---|
| `5396ee8` | 4.9 h | **2:15** | READY (total build 2.6 min) |
| `5d872ac` | 3.3 h | **3:41** | clone fine; build guard SKIP → canceled on purpose |
| `138e7e9` | 2.8 h | **41:22** | clone fine but took 41 min; build guard SKIP → canceled on purpose |
| `fea977d` | 2.3 h | never completed | ERROR at 46 min (platform gave up) |
| `32407b2` | 57 min | never completed | CANCELED at 29 min (a lane cancelled it) |
| `3cb36a2` | 31 min | never completed | still BUILDING when this was written |

Nine further production deploys sit QUEUED behind it, one per push tonight.

Repo weight, measured locally the same night:

- `git count-objects -vH` → **size-pack 4.92 GiB**
- `HEAD` checkout → **1976 MB across 5458 files**
- heaviest paths in `HEAD`: `genomes/sapling` 1070 MB (1948 files), `review/tonight`
  103 MB, `review/ep2-picks` 99 MB, `pipeline/research` 58 MB, `review/SHEETS` 47 MB,
  `farm-out/ep2-b08-tightshot-0815` 33 MB. It is render media, essentially all of it.

## What the numbers do and do not support

The instruction I was working from expected to find that repo weight had crossed a
threshold. The weight **is** the precondition, but the trigger was not a heavy commit, and
the record should say so plainly:

- The last 25 commits added **~8 MB in total** — largest single commit 3.4 MB. Nothing was
  dumped into the repo tonight. The weight has been there for days.
- On the healthy 2.6-minute build, the clone was **2:15 of it** — about 85% of total build
  time. The repo was already almost entirely clone-bound while it was still succeeding.
- The same repo then cloned in 3:41, then in 41:22, then not at all. A 20x spread with no
  input change means we are sitting exactly at the edge of the platform's tolerance and
  the variance (GitHub-side throughput, machine, contention) now decides each build.

So: **not a cliff we fell off, an edge we have been balancing on.** The repo did not get
heavier tonight; it simply stopped getting lucky.

Two aggravating factors worth weighing in the daytime call:

- **Nine queued deploys all want to clone the same 4.92 GiB.** Whether Vercel serialises
  them or not, the herd is self-inflicted: one production deploy per push, and a push is
  how every record in this project lands.
- **The build guard runs after the clone.** `vercel-ignore-build.sh` is what spares us the
  *build* on a docs-only push, and it is doing that correctly — but it cannot spare us the
  clone, because the clone is what delivers the script that decides. Two of tonight's
  30-to-41-minute clones ended in "no site input changed, skip". A project-level ignore
  command would not help either; it also runs post-clone.

## Why I stopped cancelling

Cancelling is premised on a stuck slot that a fresh attempt would clear. The 41:22 clone
disproves that: the clone is not stuck, it is slow, and killing it at 20 minutes only
guarantees that no attempt is ever given long enough to finish. Three attempts in a row
have now failed to complete a clone, so per the standing rule I stopped, left the current
build alone and wrote this instead. The nine queued deploys are also untouched.

## Meanwhile the site is up

- `https://banyan.city/` → 200, and `https://banyan.city/watch` → 200. Production is
  **serving, just stale** — its content is the commit from 4.9 hours ago. Routes added
  since then 308/404 on prod.
- The GitHub Pages mirror `https://olegmalk.github.io/banyan-city/` → 200, `/watch` → 200,
  and it carries tonight's new pages (e.g. `/review/ep2-cold-open-0818/`). It lags a push
  by minutes, not hours.

**So nothing is down and nothing is lost.** Hand out Pages URLs until this is decided.
There is no outage to fix at 3 a.m., which is exactly why the fix should not be improvised
at 3 a.m.

## The decision that is NOT mine

The durable fix is to get render media off main's deploy path, and every version of that
is architectural and irreversible-ish — it rewrites where the project's own evidence
lives, which is the product. Options exist (a media branch or separate repo the site
pulls from; an artifact store; splitting the deployed site from the archive; asking
whether the deploy needs the full history at all). I am deliberately **not** picking one,
not prototyping one, and not moving a single media file. Weighing them is a founder-awake
conversation, and the wrong choice quietly breaks provenance, which is the one thing
§7.2 does not let us break.

What I did tonight: measured it, killed two false leads, stopped the cancel loop, verified
the fallback serves, and wrote this down.

---

## Update, ~70 minutes later: it cleared on its own

Everything above was written while a sixth build sat wedged at 31 minutes with nine
deploys queued behind it. I stopped cancelling, wrote the file, and went back to
reading renders. By the next check:

- the wedged build and the entire nine-deep queue had **drained**;
- four commits pushed in the interval deployed **READY** normally;
- one of them was CANCELED, correctly — it touched only a job spec, so the build
  guard returned SKIP, which is the designed behaviour and not a failure;
- `https://banyan.city/` is **current**, not merely up: it serves tonight's pages,
  including `review/ep2-cold-open-0818/` with its new six-seed sheet.

So the episode lasted roughly three hours and resolved with **no intervention at
all**. That is worth as much as the measurements, and it points the same way they
did:

1. **The "edge, not cliff" reading holds.** A permanent weight threshold does not
   un-cross itself while the repo keeps growing. Clone throughput dipped, three
   builds fell off the far side of it, and it recovered. The repo is the
   precondition; the variance is the trigger.
2. **Cancelling was never the fix, and now there is proof.** The one thing that
   demonstrably worked is the thing I did after stopping: nothing. Whoever meets
   this next should let a slow clone finish — one of them took 41:22 and completed —
   rather than kill it at 20 minutes and start a fresh clone at the back of the
   queue.
3. **It will happen again.** Nothing was fixed, and the underlying number is
   unchanged: 4.92 GiB of pack for a site whose build takes ~20 seconds once the
   clone lands. The architectural question in the section above is still open, and
   still not mine to answer at 3 a.m.

The practical guidance for the next steward is therefore short. Check `Cloning
completed:` — not the cache line, which is on healthy builds too. If it is missing
on three builds in a row, note the time and leave it alone. If the site is serving
(it was, throughout), there is no outage; hand out Pages URLs and let the daytime
conversation decide whether to move the media.
