# The CFG-1 dead-negative audit — 94 specs, zero corrupted findings

2026-08-18, night supervisor (v2) · zero GPU, zero spend · repo-wide sweep of
`pipeline/jobs/**/*.yaml`

**Headline: the defect is real, it is already known here, it is already guarded in
code, and no finding on the books rests on it. The audit closes clean, and the one
thing it changes is where the remaining risk lives — the future, not the past.**

---

## 1. The mechanism, and who found it

At guidance 1.0 the negative prompt is inert. `do_classifier_free_guidance` is
`(guidance_scale > 1.0) or (audio_guidance_scale > 1.0)`, and audio defaults to the
video scale, so at exactly 1.0 the unconditional pass — the only thing that ever
reads the negative embeddings — never runs. Whatever the negative says, it changed
no pixel.

**This is not a discovery of tonight's.** It was established here on 2026-08-16 by
the beat-13 negative-vs-CFG job, and the write-up is
`pipeline/research/ltx23-negcfg-b13-0816.md`. That work went further than the
mechanism: it separated the negative's *content* from CFG's *strength* by deleting
the negative entirely at guidance 2.0 and finding the hold **exactly where it was**
— period 3, 32.0 distinct pictures, 8.0 effective fps. The negative's thirteen
clauses were innocent. It also found the guidance→cadence relation is a **step, not
a ramp**, with the edge inside `(1.0, 1.5]`.

The fix is likewise already in the tree, in `pipeline/ltx_i2v.py:265`
`sidecar_negative()`, which appends `[unused: guidance %g on the distilled path runs
no uncond pass, so this changed no pixel]` **only when guidance ≤ 1.0**. Its
docstring records that until 2026-08-16 the caveat was appended *unconditionally*,
which made it false on every render above 1.0 — our specs pass 2.0 — so sidecars of
renders whose negative genuinely bit were all claiming it changed no pixel. That
inversion is fixed. The function is sidecar text only and has never touched a pixel.

## 2. What the sweep found

643 specs carry an explicit `--guidance`/`--cfg` flag. Distribution:

| guidance | specs | negative live? |
|---|---|---|
| **1.0** | 98 | **no — uncond pass never runs** |
| 1.5 | 1 | yes |
| **2.0** | **516** | yes |
| 2.5 | 1 | yes |
| 7.5 | 27 | yes (SDXL-side, not the video path) |

Of the 98 at guidance 1.0, **94 also ship a non-empty negative prompt** — the
configuration that "lies about what it does". The remaining 4 pass no negative and
are honest by omission.

**Where the 94 live:** 81 are episode-1 jobs, 9 episode-2, 1 a probe; 4 sit under
`pipeline/jobs/cancelled-by-founder/`. By date the newest are `0815`; the bulk are
the undated `ep1-*-v34-plate-*-reseed` and `*-vo-length` families from the 0811–0813
era. **Nothing from 0816 onward appears.**

**Two of the 94 are not bugs at all.** `ltx-gprobe-g10-0811.yaml` and
`ep2-b13-guidance-0815.yaml` are deliberate guidance probes in which 1.0 *was the
variable under test*. Carrying a negative there is correct: the point was to observe
what happens when the uncond pass stops running.

## 3. The check that actually mattered — and it comes back zero

A stale spec harms nobody. A **verdict that credits a negative which never ran** is
a false finding still on the books, and the next lane reads it as a measurement.

So every one of the 94 was scanned across all its prose fields for any sentence
mentioning the negative *and* crediting it with an effect — removed, suppressed,
kept out, prevented, stopped, banned, excluded, worked, bit, did its job, effective.

**Result: 0 of 94.** Not one guidance-1.0 spec in this repo claims its negative
accomplished anything. The dead-negative configuration exists in the tree; the
dead-negative *reasoning error* does not.

That is a stronger result than "we fixed it", and it is worth saying why it happened:
these lanes were measuring cadence, hold period and plate fidelity, and they attributed
outcomes to guidance and to the plate. Nobody reached for the negative as an
explanation, so nobody built on sand.

## 4. Exposure to current work: none

Every active video recipe runs **guidance 2.0**, where the negative is live — that is
516 of 643 specs, including tonight's beat-17 shake sample, the beat-18 tremble set,
the cold-open growmotion sweep and the beat-14 motion jobs. No conclusion drawn in
the last three days depends on a dead negative.

One adjacent finding is worth keeping in view, because it is the *opposite* trap: the
cold-open sweep's negative lists "zoom, dolly, push in" at guidance 2.0 — fully live —
**and four of six seeds pushed in anyway**, measured at 1.10 to 1.30. So the failure
mode we should be alert to now is not a negative that cannot fire; it is a negative
that fires and is simply ignored. Those are different problems and the second one is
currently the live one.

## 5. What remains, and what this licenses

The past is clean and the code annotates the sidecar correctly. The residual risk is
prospective: **nothing warns at queue time.** `pipeline/box_enqueue.py` runs plate,
refs and payload guards but does not notice a guidance ≤ 1.0 paired with a non-empty
negative, so a new spec could be written tomorrow that pairs them and a lane could
then reason about a negative that never ran. `sidecar_negative()` catches it only
*after* the render, in provenance.

**Named, not built:** an enqueue-time warning in `box_enqueue.py` — a warning, not a
block, since the two probes above are legitimate. It is a small guard and it belongs
in code rather than in a habit, per the standing "guards live in code" rule. It is
NOT implemented here: it touches the script every job in the queue passes through,
and changing that at night to fix a problem with zero live instances is a bad trade.
Filed for a daytime pass.

**This audit licenses no render, no re-run and no spec edit.** The 94 specs are
history and history is not rewritten: they record what was asked at the time, and
their verdicts are sound because none of them leaned on the inert clause. Nothing was
edited by this audit.
