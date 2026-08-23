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
