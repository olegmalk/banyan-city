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

- HARDWARE FAULT (Roman, ~15:40): the rtx5090 box will not power on — no
  power LED, no fan, no charger LED, 15s power-button hold does nothing. It
  was reachable and idle at 14:50 (ssh ok, GPU 0%, cold). Nothing was ever
  written to it today: reads only (nvidia-smi, dir listings) plus one
  `git pull` on its clone at 14:05. No render ever ran. Escalated to dad —
  his machine, possible charger/warranty matter.
- CONSEQUENCE: banyan-city renders are blocked on hardware, not on design.
  Queue v2 (built+tested), birdseye (shipped) and the approved v2 design are
  all Mac-side and unaffected. The claim-7 sample cannot run until a GPU host
  exists. NOT rescheduling it to Roman's Mac — he held that (control/HOLD).
- STANDING: while the box is down, steward work = course + robot track, and
  Mac-side banyan work that needs no GPU.

## 2026-08-24 — evening

- RESOLVED: the rtx5090 "dead machine" was a loose wall adaptor (also why the
  RoSpider was not charging). Power restored; BitLocker demanded its recovery
  key after the unclean shutdown; Roman retrieved it from the Microsoft
  account and unlocked it himself (the steward never saw the key). Box now
  reachable: GPU idle, 41C, nothing lost.
- INTENT (founder chose option A): make the box SELF-SUFFICIENT before any
  render. Two parts, in order:
  (1) deploy queue2 to the box (its own machine-local queue root under
      C:\banyan-queue2, media store outside any git tree, hooks installed via
      the tracked installer, host_preflight fail-closed check);
  (2) auto-logon + at-boot worker service so the worker starts with no human
      login, plus disable sleep (a farm machine that naps is not a farm
      machine — today's fault made that concrete).
  banyan-box-autofill stays DISABLED throughout; no render fires until the
  box can feed itself AND the claim-7 sample has been screened by the founder.
  Verification for each part is named in design §6 step 4; nothing is called
  done on an agent's word — GPU meter and journal rows only.

- **CORRECTION (2026-08-24 21:10).** The 16:44 entry above states "Nothing was
  ever written to it today: reads only ... No render ever ran." **That is
  false.** A prior lane enqueued and completed a real LTX render through
  queue2 on the box at 14:09-14:24 box time, before the power fault:
  job `queue2-sample-b02-0824-1787566150`, state DONE, 535,868 bytes,
  attested with a readback sha. Verified independently by the steward from
  the box's own journal, not on an agent's word. The false line stands in the
  record above (struck by this correction, not edited away) because a log you
  quietly rewrite is not evidence. Cause: the steward asserted a negative
  from its own incomplete view instead of asking the box's journal.
- RESULT: **the claim-7 sample clip exists and is on the Mac** at
  `_sample/02-the-sprint-LTX-queue2-sample-0824.mp4` for founder screening.
- RESULT (part 1 of option A): queue2 deployed and PROVEN on the box —
  55/55 tests pass on Windows after four genuine cross-platform defects were
  found and fixed (an sqlite reference cycle that would have broken
  `Journal.recover()` on the exact path that runs when things are already
  bad; a 15.6 ms clock tick making compaction a silent no-op; a venv
  redirector meaning Popen.pid is not the worker's pid; SIGKILL absent on
  Windows). End-to-end proven on the box: enqueue -> done with readback sha,
  duplicate refused rc=3, taskkill mid-job -> sweeper filed it INTERRUPTED
  with the attempt consumed. Residency guard fires (rc=8) for roots inside
  the repo. banyan-box-autofill remains DISABLED.
- OPEN for part 2: pid reuse across reboot can make a dead attempt look live
  (record a boot id alongside the pid); the queue root resolves via `~`, so an
  at-boot service running as a different account would silently see an empty
  queue — pin --root/--store explicitly; v1 runner is still draining the old
  queue and the design retires that split.
