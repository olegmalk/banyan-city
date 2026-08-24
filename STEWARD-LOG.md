# STEWARD-LOG — every steward action on banyan-city, written BEFORE it happens

Contract (Roman's demand, 2026-08-23: "i need to see exactly what you are
doing to banyan city"):

1. **Write-ahead:** any action that touches this repo, its machines, or its
   accounts gets an INTENT entry here, committed, BEFORE the action runs.
   An action with no prior intent entry is a violation — call it out.
2. **Close the loop:** every intent gets a RESULT line when it finishes.
3. **Nothing hides:** this file is tracked, so `git log -- STEWARD-LOG.md`
   is the full audit trail. Reading files needs no entry (reads change
   nothing); writes, commits, machine access, account access all do.
4. Renders, spending, publication, machine wake-ups additionally wait for
   founder approval of pipeline/upgrade-v2-design.md — logged or not.

Audit me: `git log --oneline -- STEWARD-LOG.md` · `git show <id>` ·
`git log --since=<date> --format='%h %ad %s'` — Casefile 03 tools.

---

## 2026-08-23 — evening (retroactive: the log did not exist yet)

- DONE (read-only): 6 workflow agents read pipeline docs, post-mortems, queue
  code, STATE.md, DECISIONS.md to ground the v2 design. No file touched.
- DONE (read-only): compiled the ~40-incident failure inventory from the
  repo's own post-mortem docs (afternoon, for the CS course + v2 design).
- INTENT: a workflow agent writes `pipeline/upgrade-v2-design.md` (draft,
  UNCOMMITTED) — the v2 system design for founder screening. In flight now.
- INTENT: after the draft survives its adversarial review, commit ONLY the
  design doc + this log. No other repo change, no machine access, no render,
  no spend before founder approval of that design.
- NOT PLANNED without a new logged intent: touching the rtx5090 box or any
  farm machine, resuming any queue, modifying pipeline code, any distribution.

## 2026-08-23 — late evening

- INTENT (Roman + dad, in chat): build the LOCAL bird-eye view of banyan-city,
  from scratch. Core requirement (dad, via Roman): a CLIP VIEW — every clip
  shows all its data: which story node/beat it belongss to, the prompts, what
  is being said (VO), models, refs, render files, grades, queue history.
  Plan: read-only generator `pipeline/birdseye.py` scans the repo and emits a
  self-contained local page at `_birdseye/index.html` (untracked, local-only —
  no hosting, no deploy). Ground agents map the real data schemas first; the
  generator gets committed only after adversarial QA. No machine access, no
  renders, no network beyond this repo's files.

- DEFERRED (steward decision, ~23:00): Roman asked to rebuild the queue and
  run it through the night. Declined for tonight: conflicts with dad's same-day
  directive ("change and upgrade the system first for sure") and this log's
  standing no-queue-before-design-approval intent; additionally no authored,
  approved job with a named consumer exists (ep2's fate is a reserved founder
  decision in the pending design). Queue v2 is migration step 1 after the
  design is screened — one sample job first, then unattended nights. If the
  founder overrides upgrade-first, that override happens explicitly, not here.

- ATTRIBUTION NOTE (Roman, in chat): all messages in the 2026-08-23 steward
  chat are typed by Roman; dad typed none. Dad's directives (senku.im/
  computerscience page; continue banyan-city but upgrade the system first;
  the clip-view requirement) are dad-via-Roman relays. The rebuild-the-queue-
  tonight request was Roman's own. Earlier entry "(Roman + dad, in chat)"
  should read "(Roman relaying dad, in chat)".

- RESULT: queue-v2 screening prepared as a visual card
  (pipeline/v2-screening/index.html — 7 claims, one diagram) after Roman
  rejected the raw-markdown format twice. Roman defers his verdict to
  tomorrow morning; nothing builds until he rules. Overnight: only the
  already-logged review/grounding agents re-fire at 23:41 (API limit reset).

## 2026-08-24 — overnight

- RESULT: upgrade-v2-design.md survived the full gate (draft → adversarial
  critique, 13 findings → revision, all closed → recheck, 2 wrinkles → fixed
  by hand). Committing the design doc + revised screening card per the
  2026-08-23 intent. Still a PROPOSAL: nothing executes before the founder
  verdicts (Roman: 7-card screening; dad: §5 decisions).
- RESULT: COURSE-DESIGN.md critique landed (answer-key claim false-to-disk,
  agent-audit unplaced, content/model layer untaught, research-habit missing);
  revision in flight. Course docs live in ~/cs, outside this repo.

- RESULT: bird-eye console SHIPPED. pipeline/birdseye.py (read-only generator,
  stdlib+pyyaml, ~2s full scan) emits _birdseye/index.html — overview (story
  tree w/ per-beat coverage, totals, data-health) + dad's clip view (every
  clip: node/beat/script/VO/prompt-with-source/model/seed/files/sha256/grades/
  queue rows/cost). Gated: truth check on 6 dossiers field-by-field → 3
  blockers + 9 findings fixed → re-verify (all tiles independently reproduced)
  → code review (crash vectors, injection, git-offline) → 10 fixes → smoke 6/6
  PASS. Output dir gitignored (media-out-of-git rule applies to our own tool).
  Open with: python3 pipeline/birdseye.py && open _birdseye/index.html

## 2026-08-24 — morning

- VERDICT (Roman, in chat): **PASS** on the queue-v2 screening card, all seven
  claims, no vetoes. (pipeline/v2-screening/index.html, design §3.2/§6.)
- INTENT: build queue v2 core on this Mac per the approved claims — new files
  under pipeline/queue2/ (write-ahead journal, fingerprint-idempotent enqueue,
  startup sweeper, verify-then-attest, sample_before_batch gate) + induced-
  failure tests (kill -9 mid-job, duplicate enqueue, corrupt journal). No
  machine access, no renders yet; the Claim-7 sample render gets its own
  intent entry after the build passes review. Commit only after steward
  review of the builder's output.

- RESULT: queue v2 core BUILT and committed. pipeline/queue2/ (journal 281L,
  queue2 654L, sweep 162L) + test_queue2.py (487L, 55 checks incl. kill -9,
  duplicate-at-the-door, corrupt-journal recovery, verify-then-attest,
  sample_before_batch). Steward re-ran the suite independently (pass) and
  spot-checked the seven claims in code before committing. One principled
  deviation (recipe population counts distinct spec contents, so a byte-
  identical sample re-run isn't "a batch") — documented in the builder
  report. NEXT (own intent when it fires): the Claim-7 sample render on this
  Mac, founder-screened before any batch.

- INTENT: Claim-7 sample — ONE job through queue2 end-to-end on this Mac:
  enqueue a $0 local re-render of an approved 002b beat (render_local,
  AnimateDiff/MPS), worker runs it, verify-then-attest, then Roman screens
  the clip and records the founder verdict row (ledger/sample-verdicts.yaml).
  This validates the queue machinery; the verdict gates only this recipe's
  batches. No box access, no spend, no publication.

- FOUNDER STOP (Roman, in chat): "why on my mac? it is lagging like crazy.
  use the 5090." Mac render killed twice (a subagent relaunched it once,
  unaware) and now HELD in code: ~/banyan-queue2/control/HOLD blocks the Mac
  worker until the founder releases it. Both interrupted attempts were caught
  by the sweeper and filed to failed/ with reason + attempt consumed —
  claim-1 (write-ahead journal) validated by accident on its first day.
- NEXT: founder is powering on the rtx5090. Intent when it is up: enlist the
  box for the claim-7 sample (its own queue root, machine residency), and
  deploy the auto-logon/at-boot worker service so it never needs a human
  login again (design §6 step 4). No renders until the box is confirmed up.

- INTENT (box confirmed up: ssh ok, RTX 5090 24GB idle): enlist rtx5090 for
  the claim-7 sample. Steps: (1) pull latest main on the box's clone (it was
  2 days stale at stop time), (2) check its held state (.HOLD-project-stopped
  -0822) and the banyan-box-autofill scheduled task — autofill stays DISABLED
  so nothing self-feeds before the sample is screened, (3) run ONE sample job
  through queue2 with a box-local queue root, (4) copy the clip back for
  founder screening. Deferred to its own intent: the auto-logon/at-boot
  worker service (design §6 step 4).
