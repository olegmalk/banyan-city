# Handover — 2026-08-17

Written by the steward at the end of a long session. Everything below is on
disk; this file is the connective tissue that otherwise lives only in a
conversation. Read `STATE.md` for the running log, this for what today means.

## 1. Waiting on Oleg — nothing else unblocks these

| # | Decision | What it unblocks |
|---|---|---|
| 1 | **Read the five rewritten beats (12/13/15/19/20) + the 003b line.** | STEWARDSHIP §6: no voice, no render, no assembly from them until read. Biggest single unblock on the board. |
| 2 | **May I push?** 147 commits ahead of origin. | A push deploys banyan.city, and the rewritten beats he has not read are in it. Held deliberately. Cost of holding measured: **one future failure mode, two named directories (`farm-out/ep2-b14-mac-plate-0817`, `ep2-b14-fieldcomp-0817`), zero lanes blocked today.** |
| 3 | **Beat 14** — clears all seven axes; the lane that built it **would not hand it to motion** (an unresolved pale limb-like mass no axis catches, coords committed). Ship, or fix. |
| 4 | **Beat 17's brush** — exhausted by evidence. Three routes, all R4: accept ~1-in-5 and render-five-pick; restage so the brush isn't required; change checkpoint. **`brushes off` is in approved line 002b-t0-c, so conceding it is a rewrite.** |
| 5 | **Beat 21's two blades** — are they his "average leaves"? Also its soft background object: dressing or reshoot? |
| 6 | **Beat 01** — its only 2-blade frame is also the frame carrying the LOOK fault. Is there a usable frame at all? |
| 7 | **Guards read adolescent** on b05/b06/b10/b11 — one taste question, not four. Plus: may the goblin read as a plain green man? |
| 8 | **Beat 11 r1s1** — a 9-of-10 plate on a beat recorded BROKEN TAKE. Nobody promoted it, deliberately. |

## 2. Laws proven today — these generalise

- **Broadcast-class attributes.** An attribute token lands on **every eligible
  figure**, and **scoping it inside one character's clause does not contain
  it.** Proven twice independently: eyewear (1 face → binds 7/7; 2 faces →
  lands on both 5/5) and `bald` (token present → 12/12; `green skin, bald
  head, patched cloak` is as tightly scoped as prose gets and the *guard* went
  bald). Diagnostic: test any new attribute at 1 / 2 / 0 eligible figures.
  **Lands on both ⇒ no wording will fix it.**
- **Add, never remove.** Masked *addition* works (5/5, protected face
  byte-identical). Masked *removal* fails (0/1) — a thin band along an
  object's own outline thins it rather than deleting it, because the unmasked
  pixels either side still describe it.
- **Remove the cue, not just the object** — and **some cues are not maskable.**
  Beat 01 regrew a blade at the stem node 4/4; patching the attachment too
  still regrew 3/4. The mask deletes a blade but not the anatomy. Beat 21 is
  the control: same recipe, 4/4, because its vacancy sat against open sky with
  nothing to complete.
- **Numbers barely reach the model.** CLIP embeddings are near-identical
  across numerals (T2ICountBench, arXiv 2503.06884). Nobody has published
  exact count control on SDXL. This predicted our split exactly: height (a
  continuous adjective) binds; "exactly two" does not.
- **Composite-then-inpaint at 0.30 is the answer to count.** With a composited
  init the thing you want is **not a sample from the model**. 8 of 8 exact
  two-leaf count across two independent inits, zero GPU for the count itself.
  At 0.2–0.35 only `steps × strength` steps run, so structure survives.
- **Geometry binds — but bind it to the right object.** `opposed one either
  side of the stem` scored 2 of 16 on count, a real null by its
  pre-registered rule. But re-reading the clean cells at full resolution
  inverted the mechanism: **the clause bound, and bound well.** Stems show
  swollen node joints, and at *every* node there are exactly two leaves,
  opposed. What it never constrained is **how many nodes the plant has**, so
  the model honoured the arrangement and stacked it two or three times up the
  stem — eight cells each obeying "opposed, one either side" and returning
  four to six leaves. The clause **describes a node, not a plant**, so it was
  never a count constraint and could not have been.
  **Next lever, designed and deliberately unfired:** constrain the node —
  `one node`, `the stem bare beneath them` — with its own bar pre-registered
  before its own pixels, folding in "average leaves" so `cotyledon` is not
  carried a third time. This is a new variable and wants its own lane.
- **Tools lie about success — four instances today.** A canon gate green on
  struck-through prose; a frame-count assertion neutered by `allow_fail`; a
  publish step writing a manifest for files it never copied; a runner
  reporting `State: Running` with the GPU at 0% and 0 MiB. **The signal is the
  artifact state, not the exit code.**
- **Testing corollaries.** A guard function written perfectly with its **call
  site unwired** passed **42 of 47** checks — only end-to-end assertions
  demanding the real exit code caught it. And **a fixture must not stand in
  for the code it exercises** (a mutation survived exactly that way).
- **Compositor faults have been the real problem more often than the model** —
  five on beat 14 alone, plus a residual lamina on half the leaf variants. A
  tool must measure whether its region actually covers the object it claims to
  act on.

## 3. Traps that will cost hours

- **The fallback token estimator changes verdicts, not just numbers.** Same
  draft: real CLIP 74/77 with 0 faults, fallback 85/77 with 2 faults —
  `compress()` sheds the tail then faults the draft for what it shed. **Measure
  only with** `~/banyan-farm-m1pro/venv`, `openai/clip-vit-large-patch14`,
  offline. A count without a stated method is not evidence.
- **`git ls-files` on `main` is not "what is filmed."** Farm results live on
  `origin/farm-results-rtx5090` and **nothing merges them back.** Eleven sets
  were stranded three days on exactly this. Any audit must read both branches.
  `pipeline/check_results_merged.py` now detects it (gate 2 = 0 at HEAD, names
  exactly the 7 historical strandings pre-recovery).
- **Read `C:\banyan-queue\done` before believing `failed/`.** Without it a
  check reports 15 leaks and 9 are wrong. I re-fired a clip that already
  existed by skipping this; a lane repeated the same mistake filing `a2`.
  **An orphan log with no json means "retried and finished"** — the failure
  count is not a floor; 33 was right.
- **An output dir proves a job ran; absence proves nothing.**
  `pipeline/measured/queue-history.json` is days stale — caused twelve
  duplicate filings. Never use it.
- **`--amend` has no pathspec form** and swept six of a peer's staged
  deletions. Always `git commit -- <explicit paths>`.
- **A matching byte delta is not proof of a correct edit.** One insert
  anchor would have written 26 lines *inside* a folded scalar with a perfect
  byte count and a sha that moved exactly as predicted — only the
  parsed-variant diff caught it.
- **The scratchpad is not private between lanes.** A peer overwrote another
  lane's `-F` message files. Verify immediately before committing.
- **The box reads `<harness>/wave-drafts.yaml`, not `repo/pipeline/`.**
- **Lanes die mid-stream constantly.** ~16 today, several losing transcripts.
  **Commit after every single unit**; batching loses whole runs. The one
  agent that batched lost the same verdicts three times.

## 4. State of the episode

**Solved today:** two-leaf count via composite (8/8); eyewear control (5/5,
protected face byte-identical); all seven guard beats cast-corrected and
scored; the story rewritten at knee height with **no shippable footage
stranded**; a 40% render waste (box sampler was five days stale, missing
`dedup_cells`); eleven stranded result sets recovered (155 files, sha-verified);
the canon guard's strikethrough hole closed; `test_pipeline.py` green for the
first time in days.

**Closed by evidence, do not reopen:** beat 17's brush by any plate a lane can
build (12 seeds, 0 brushes; handed the gesture mid-stroke from its own best
frame it still would not complete a stroke). Beat 01's mask route (stop rule
honoured). Beat 10's adjacency lever for props (1 of 12 — duplication tracks
look-alikeness, not depth; **occupied hands** is the untested cheaper lever).

**Open technical work, briefed but unstarted (I hit the 200-agent cap):**
1. **Purple fig pass** — 25+ live prompts still say `green` against a
   retroactive purple canon. Pure wording debt; purple is reachable (beat 18
   measured purple, and a 16-frame arm read deep purple-violet 16/16).
2. **Wire `apply_variant_declaration`** in `goblin_ipa_sample.py` — it exists
   and is **never called**, which is why beat 07 cannot declare two figures
   without faulting every sibling draft. Beat 07's own action is missing
   (**0 of 12 contain a point**) because `points` takes `white sash` as its
   subject and the goblin has no noun.
3. **Collision guard into `box_enqueue`** — `check_job_collisions.py` catches
   it at rc=1 but is a hand-run wrapper, so nothing stops the next colliding
   pair. Spend guards are code; this one is not yet.
4. **Bark board** — 0 of 36 across b06/b08/b10. Wording exhausted; the only
   board that ever shipped was composited.
5. **Beat 07's residual baldness** — removing the token fixed b08 12/12 but
   left b07 at 8/12 bald. Open. Both drafts name the hair, so the obvious
   answer is excluded; a prior measurement suggests the checkpoint defaults
   him bald on this beat family.

## 5. Where the records are

- `review/ep2-picks/cast-0817-scores.yaml` — seven guard beats, N of 12
- `review/ep2-picks/nobald-0817-verdict.yaml` — the `bald` ladder
- `review/ep2-picks/farm-recovered-0814-scores.yaml` — nine recovered sets
  ⚠ cites "card 2/3/4 below" that were **never written**, and still claims
  `a2` never ran (it ran 2026-08-13). Left unedited: the disagreement is the record.
- `review/ep2-picks/farm-recovered-0814-b01shape-scores.yaml` — the last two
- `pipeline/plate-verdicts-0817.md` — six plant plates
- `pipeline/composite-init-pattern.md` §12 — the composite laws
- `pipeline/research/count-control-sdxl-0817.md` — why counting fails
- `pipeline/queue-failure-triage-0817.md` — the 35 failures, six causes
- `pipeline/farm-branch-merge-gap-0817.md` — the merge gap + b14 tripwire
- `pipeline/canon-patch-cotyledon-0817.md` — applied, kept for provenance

## 6. Standing constraints

$0 only. Never `--amend`, never `git add -A`/`-a`. `git status` before any
Write in this shared tree. Do not push without Oleg. Media needs his approval
first (§6). One sample before any batch. Pre-register bars **before** pixels;
tighten forward only, never retroactively — bending bars after the picture is
how 8/12 "passes" became 0/12 usable.
