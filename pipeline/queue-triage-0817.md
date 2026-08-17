# The 33 failed queue entries, triaged by cause — 2026-08-17

Read-only pass over `C:\banyan-queue\failed` on the rtx5090. **Nothing was
re-fired**; re-running a failed job is the lead's call. `pipeline/measured/queue-history.json`
was NOT consulted (days stale, twelve duplicate filings).

**33 job jsons, 35 logs. Eight causes, and only three of them are bugs.** The
counts below are logs, so they sum to 35; the two extra are §D, which never got a
json written — which is itself the finding.

| | Cause | n | Verdict |
|---|---|---|---|
| A | draft/prompt guard refused before drawing | 9 | working as designed |
| B | spec names a drafts key or marker that does not exist | 10 | **one bug, ten filings** |
| C | render COMPLETED, artifact declaration wrong | 8 | **pixels exist; 6 beats mis-filed** |
| D | process killed mid-render (window-CLOSE) | 2 | **silent death, twice, unnoticed** |
| E | syntax/name/key error in the spec's own inline python | 3 | bug, three separate specs |
| F | init path the box can never have | 1 | **live lane blocked today** |
| G | harness beat-kind guard | 1 | working as designed |
| H | input-shape mismatch | 1 | working as designed |

---

## C — SIX BEATS HAVE PIXELS ON THE BOX AND ARE FILED AS FAILURES

**This is the one that changes what we believe.** rc=92 is the runner's
`!! declared artifacts missing` check. It fires **after** the render step, so it
fails a job whose frames already exist when the declared path does not match what
the renderer actually wrote.

Timestamps settle it. The box is UTC+4; every one of these wrote its newest frame
in the **same minute** the job was marked failed:

| Job | Failed (UTC) | Newest PNG (box local) | PNGs |
|---|---|---|---|
| `ep2-b05-scene-0814` | 00:32:50 | 04:32 `05-the-patrol-ipa-r3-w015-s3.png` | **16** |
| `ep2-b09-scene-0814` | 00:35:52 | 04:35 `09-the-pause-ipa-r3-w015-s3.png` | **16** |
| `ep2-b11-scene-0814` | 00:38:51 | 04:38 `11-they-leave-ipa-r3-w015-s3.png` | **16** |
| `ep2-b12-scene-0814` | 00:39:53 | 04:39 `12-related-wave1-s3.png` | **4** |
| `ep2-b18-scene-0814` | 00:40:51 | 04:40 `18-the-decision-wave1-s3.png` | **4** |
| `ep2-b21-scene-0814` | 00:41:50 | 04:41 `21-the-answer-wave1-s3.png` | **4** |

The declarations asked for `...-ipa-r0-w01...`; the renderer wrote
`...-ipa-r3-w015-s3...`. **A round/weight/seed slug mismatch, not a render
failure.** This is the same trap the barkboard specs already carry a comment
about — "a glob without the beat slug matches nothing and publishes nothing while
still returning a code that reads like a render failure" — except here it is the
`artifacts:` list rather than a publish glob.

**60 frames for six beats exist and nobody has looked at them.** They were never
couriered to `farm-out`, because the publish step never ran. Whether any is usable
is a taste/pick question, not mine.

Two in this group are **not** proven and should not be treated as recoverable:

- `ep2-b01-final055-r2-0812` — the declared dir `out-b01-final055r2` does not
  exist anywhere on the box. Genuine no-output failure.
- `ep2-b01-shape-0813` — the dir exists with 2 PNGs, but they are stamped 08-13
  **17:45**, four hours *after* this job failed at 13:43. They belong to a
  different run. Absence proves nothing and so does presence at the wrong minute.

## D — THE SILENT DEATH HAS HAPPENED BEFORE, TWICE

`ep2-b04-balloon-pair-0813` and `ep2-b19-overhead-0812` are the **only two logs
with no matching json**, and they are the only two with
`forrtl: error (200): program aborting due to window-CLOSE event`
(rc `3221225786` = `0xC000013A`, `STATUS_CONTROL_C_EXIT`).

- `ep2-b19-overhead-0812` died at **`50%| 4/8 [01:43<01:15, 18.80s/it]`** — mid
  render, and its log has **no `finished rc=` footer at all**. The runner never
  got to write one.
- Both are consistent with the failure the lead just restarted the runner for:
  the process is gone while its bookkeeping says otherwise. Neither is a spec
  fault, and **neither job's spec was ever wrong.**

**The detection rule this gives us, and it is cheap:** a log with no json in
`failed\`, or a log with no `finished rc=` line, is a killed runner, not a failed
job. Two in seven days, both unnoticed until now. `ep2-b04-balloon-pair` also fits
the known WDDM-thrash pattern on b04 renders.

## F — THE EYEWEAR LANE IS BLOCKED RIGHT NOW, AND THE PATH CANNOT EVER RESOLVE

`ep2-b10-attrbind-eyewear-0817` failed **today at 12:14 UTC**, rc=2:

```
!! init not found: C:\banyan-farm\banyan-city\farm-out\ep2-b10-mac-plate-0817\10-no-form...
```

- `farm-out/ep2-b10-mac-plate-0817` **exists in the repo on this Mac.**
- The box's clone `C:\banyan-farm\banyan-city` is at **HEAD 2026-08-15 22:35**,
  two days stale; its newest `farm-out` subdirs are 08-15.
- **No `git pull` runs on the box by design** — the bark-plates spec states this
  explicitly. Payloads arrive by scp into `C:\banyan-farm\<job-id>\`.

So this is not a stale checkout to be refreshed: it is a **spec shape that can
never work.** A job must reference a payload dir it scp'd itself, or
`C:\banyan-farm\courier-box\farm-out\...` published by a prior job — never the box
clone's working tree. The eyewear lane's plate and mask are fine; the delivery step
is missing.

## B — ONE BUG, TEN FILINGS

Ten jobs (rc=4) died on the harness refusing to build a prompt because the spec
named something absent from `wave-drafts.yaml`:

- `ep2-goblin-design-d1..d6-0814` — **six filings of one bug**: *"beat 04
  (the-footnote, kind=goblin) carries no `{{GOBLIN}}` marker."*
- `ep3-charref-assessor-0812`, `ep3-charref-farmer-0812` — same marker fault on
  beat 03.
- `ep2-guard-sheet-a-0814`, `ep2-guard-sheet-b-0814` — *"beat 07 (confiscate) has
  no `authored_guard_sheet_a`/`_b` key."*

The guard is right every time. What is wrong is that **six identical specs were
filed before the first one's result was read** — the batch-before-a-sample habit,
showing up in the queue rather than in a render.

## A, G, H — the guards working, 11 entries

Not bugs. Recorded so nobody re-opens them looking for one.

- **A (9, rc=1) `!! FAULTS - nothing drawn`**, before any pixel: style anchor
  missing (`very aesthetic` absent from the positive) on `b06-ipa-guardcast`,
  `b08-refresh`, `b20-canonword` ×2, `ep3-charref-assessor-r2`; **count-tag
  mismatch** on `b06-plate-0815` and `b09-scene2-0815` (derived `2boys`, declared
  `1boy`) and `ep3-003b-b01-dialect` (`1other` vs `''`); *peopled beat negates its
  own subject* on `ep3-sapling-reference`. The count guard catching `2boys` under a
  `1boy` slot is the exact path that later caught `ep2-b06-plate-0815` by design.
- **G (1, rc=30)** `ep2-b07-plate-0814` — beat 7 is not a goblin beat and its
  draft has no goblin marker. Correct refusal.
- **H (1, rc=1)** `motion-poscontrol-0816` — *"the four embeds files are not four
  positives against one negative."* Input-shape mismatch, caught before the GPU.

## E — three spec-authoring bugs, three different specs

`autofill-proof-0816`: `SyntaxError: unterminated string literal` in a `-c`
payload. `ep2-b04-goblin-ipa-content`: `NameError: name 'CELLS' is not defined`.
`ep3-charref-magistrate-0812`: `KeyError: 'kind'`. Each is one spec, each needs a
one-line fix, none is systemic.

---

## Two questions asked after the first pass, both answered

**Does the stale wave sampler explain any of these? NO.** The box's sampler is five
days behind and missing the dedup fix, so the worry was that some of these renders
redrew a picture already drawn. Hashed every recovered frame in group C:
`out-b05-scene` **16 png / 16 distinct sha256**, `out-b09-scene` 16/16,
`out-b11-scene` 16/16, `out-b12-scene` 4/4. **No duplicates at all.** Not one of the
33 failures traces to sampler staleness, and the 60 recovered frames are 60
different pictures rather than a handful repeated. The sync still matters for
future IP-Adapter runs; it does not explain anything here.

**Where the failures actually live: `C:\banyan-queue\failed\`, not `done\`.**
`done\` holds 1736 files and none of the 33 are in it. `failed\` holds exactly 68 —
33 jsons + 35 logs — which is where the heartbeat's `failed: 33` comes from, and the
two-log surplus is §D.

## What I would do with this, in order (the lead's call, not mine)

1. **Look at the 60 frames in C** before re-rendering any of those six beats.
   Re-firing them would spend the card on work already done.
2. **Add the D detection rule to the runner or the tick**: a log with no json, or
   no `finished rc=` footer, is a dead runner and should page rather than sit in
   `failed\`. Two went unnoticed for a week.
3. **Fix F by moving the eyewear job's init to a scp'd payload dir.** No pull will
   ever fix it.
4. Leave A, G and H alone. They are the guards doing their job, and eleven of the
   thirty-three "failures" are the system working.
