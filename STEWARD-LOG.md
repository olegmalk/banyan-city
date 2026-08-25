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

- FOUNDER VERDICT (Roman): claim-7 sample REJECTED — "barely looks like the
  goblin" + "the animation is trash". Recorded in ledger/sample-verdicts.yaml.
  Gate is fail-closed so no batch was ever possible; this makes the rejection
  durable and names the defects. Tonight = self-sufficiency proof + diagnosis
  (resemblance -> character-reference thread incl. the IPA run where the ref
  provably never reached the code; motion -> frozen-frames/metric thread).
  ONE new sample comes out of diagnosis, not fifteen.

- RESULT: bird-eye v2 — "SAPLING · production atlas" — built to a full design
  spec (screening-room look: charcoal, leaf accent, the show's frames doing
  the work; story-tree rail -> 9:16 hover-play filmstrip -> beat dossier with
  script/VO/prompt/provenance/files/queue/grades; health honest but folded
  into the footer). Steward iterated on screenshots before anyone else saw
  it: problem-dots thresholded to serious classes only (an alarm that always
  rings is silence), long production-history paragraphs dimmed + collapsed.
  Same generator, same data layer, same one-file local output. Overnight
  adversarial gate (dad-lens UX + display-truth spot check) runs before it is
  shown to dad.

- FOUNDER DECISION (Roman relaying dad, 2026-08-24 ~23:20): "dad wants us to
  continue" — the night queue RESUMES ep2 finish work (grading/finish passes
  on already-approved footage; risks were laid out to Roman first: day-one
  code, box crash, spec mistranslation, wasted-effort-if-ep2-dead — dad's
  continue answers the last one). Constraints in force tonight: ONE job filed
  and verified before the rest release (one-before-batch applied to the
  migration itself); NO new motion renders except the single diagnosis sample
  (founder's rejection stands, gate is fail-closed); publication still gated;
  $0 only.
- INTENT: inventory the held ep2-finish backlog, translate specs to queue2,
  file one, verify its attestation, release the remainder for the night.
  Depends on the box's self-sufficiency canary (in flight).

- LESSON->CODE (from the diagnosis lane's adversarial checker, ~23:30): the
  founder's rejection was prose-durable only — the hand-typed ledger row used
  key recipe_fp (placeholder value) where queue2 reads `fingerprint`, so the
  gate could never see it; and population is counted per-host, so a fanout-1
  respin on the Mac would have slipped through. Fixed: row rewritten through
  record_sample_verdict() with the REAL fingerprint (854622022405…, read from
  the box journal), reasons preserved; queue2 now blocks a rejected recipe on
  EVERY host regardless of population ("a rejected recipe does not run again;
  change the recipe and sample that"). Proven: 55/55 suite + a live respin
  attempt refused with the founder's verdict quoted. The steward hand-typed a
  row whose own docstring says the shape is code — noted, and the docstring
  won.

- RESULT (night queue, ~23:35): the ONE job ran end-to-end on the standing
  self-started worker and attested clean — ep2-b11g2-guardgrade (finish-class,
  CPU, $0, 7s): the b11 guard2 plate re-graded onto guard1's founder-accepted
  light, completing the b05g2/b07 trio. Journal DONE, three independent
  hashers agree (2efcbec5…). Graded bytes await founder screening.
- FINDING: there is NO releasable "rest of the backlog." The 88 held v1 specs
  are ALL motion/generation-class, and most carry pre-stop FOUNDER TASTE HOLDS
  (age-pivot, eyesize-unsettled, r4-sample-teen) that are not the steward's to
  lift. The pending gradmotion wave (b17 sample, then b04/b07/b14) is
  motion-class and stays blocked by tonight's own logged constraint (no new
  motion except the diagnosis sample). So the night queue's honest total is:
  one job, done, verified. Machines go quiet on renders — not idle-while-
  runnable-work-exists; there is no runnable render work tonight that would
  not violate a standing hold. No-work-without-a-consumer holds.
- STATUS: cycle-019 (diagnosis) writer has died on API connection errors 4x
  tonight; the API is flaky. One retry queued; if it fails again the document
  waits for morning — no sample renders without it passing its gate anyway.

- RESULT (~23:40): atlas gate findings ALL fixed and re-verified. The big one:
  a leftover git worktree (wt-pre/) was being walked as production data —
  inflating every count ~25% (renders 3,426→2,778 real, unresolved 1,941→
  1,123), showing STALE takes on 4 filmstrip faces, and breaking newest-first
  ordering. Now any registered worktree is pruned from the scan. Also: the
  red dot judges only the current take (2/21 lit on 002b, was 21/21 — an
  alarm that always rings is silence), cost+wall-time hoisted into the recipe
  line, "21/21 beats with footage" coverage sentence + color legend, ship
  picks resolved by sha to byte-identical local copies, contrast/ellipsis/
  arithmetic nits closed. Steward screened the final pixels. Committing.

- RESULT (~00:10): cycle-019 diagnosis WRITTEN and adversarially CONFIRMED-SOUND
  (all quotes verbatim, both commits verified, byte-identity proven, blobs
  exist, one $0 render, new fingerprint; two cosmetic filename nits fixed).
  Headline finding: last night's rejected pixels were an UNSCREENED 08-21
  steward pick the founder had already effectively rejected (commit 5412a4522
  reverted it as "worse than the last one") — not a regression, this recipe's
  first real founder screening, consistent with every prior note. Fault 1
  (resemblance) is decided at frame 0, so the prescribed sample is a STILL
  (inpaint_fruit.py + jerry-v3 LoRA, pose-net path), stills-before-motion per
  the founder's own rule; fault 2 (motion) levers named for the video rung.
  Step zero is $0 and needs no GPU: grade four already-rendered-but-unlooked-at
  v3 probe grids first. NOTHING rendered/enqueued — awaits founder screening.

- FINDING (Roman, 2026-08-25 ~00:40): the box got LOGGED OUT and the
  banyan-q2-worker task stopped with the session; Roman re-logged in and it
  resumed (confirmed Running, polling clean, empty queue). So self-sufficiency
  is only PARTIAL: the task survives a reboot (auto-logon brings the session
  back) but NOT an interactive logout. Fix for the morning: register the
  worker to "run whether user is logged on or not" (SYSTEM or stored creds,
  /RU /RP or a service wrapper) so a logout can't idle the farm. Until then a
  logout is a real stop — same human-awake-dependency class the v2 design
  names. Nothing lost; no approved work was waiting to run anyway.

## 2026-08-25 — Olga ad prep
- CONSENT recorded: Olga agreed to AI likeness + voice clone for her own ad
  (Roman relaying, 2026-08-25). Privacy enforced in code/process: assets live
  in ~/olga-ad/ ONLY (outside every repo), never uploaded, never committed.
- Project scaffold built at ~/olga-ad/ (README w/ consent+privacy, exact VO
  lines + motion prompts, clipped-string placeholders awaiting dad's plain text).
- INTENT: install Chatterbox-multilingual on the rtx5090 box (the one missing
  capability for Russian VO; ~2-3GB, $0, no human dependency). Read-only survey
  confirmed no TTS on the box. No renders; no Olga assets exist yet.

- RESULT: Chatterbox-multilingual installed on the box, GPU-verified for
  RUSSIAN. Isolated venv C:\banyan-tts\venv (render venvs untouched); Blackwell
  torch 2.11+cu128 protected via --no-deps (chatterbox pins torch 2.6 which
  lacks sm_120 — that trap avoided). Russian selftest ran on cuda:0 (no one's
  voice). Clone helper: C:\banyan-tts\clone_ru.py <ref.wav> <out.wav> "<ru text>".
  One caveat: auto Russian STRESS-marking is unavailable (russian_text_stresser
  missing) — synthesis works, but the brief's stress notes (директ/верхо́в/
  низо́в last-syllable) must be hand-marked in the input text. Watermarked by
  design (fine).
- Olga voice ref staged from her no-music talking-to-camera video: 41s clean,
  48kHz mono, + a normalized copy (source was -42dB). Face refs staged (3
  photos + 44 video frames), appearance line written from the photos.
- BLOCKED on: dad's clipped prompt strings (anchor/wardrobe/negative) before
  stills; then the pipeline runs stills -> screen -> 1 sample shot -> screen ->
  rest -> voice.

- RESULT: dad re-sent the brief un-clipped ("C1 local render brief (1).pdf");
  all 4 previously-clipped strings recovered (anchor+wardrobe tail, crammed,
  sorted, negative). Still prompts A/B/C ASSEMBLED at ~/olga-ad/stills/prompts/
  with the real text + Olga's photo-derived appearance line. AWAITING file
  retired. Prompt/text gate = CLOSED.
- NEXT gap (last technical one before generating her face): the STILLS need a
  PHOTOREAL image model + face-identity method (brief: IP-Adapter FaceID /
  InstantID / PuLID, or an image-edit model fed her photo). Box has an ANIME
  checkpoint + BASIC IP-Adapter only. Surveying the box for the shortest $0
  path to a photoreal on-model still of Olga before any generation.

- FOUNDER DECISION (Roman): Route B for Olga stills — RealVisXL + IP-Adapter-
  FaceID + InsightFace (~8GB, ungated, $0, no account). Goal: generate ONE
  Still A, screen with Roman+mom (the likeness moment of truth). Escalate to
  Flux Kontext (Route A, needs dad's HF account) ONLY if likeness is
  insufficient. Nothing sent/published; local only; her refs never leave box.
- INTENT: on the box, dedicated venv (protect render + tts venvs + Blackwell
  torch), download RealVisXL_V5.0 + ip-adapter-faceid-plusv2_sdxl + antelopev2,
  pip insightface/onnxruntime, write a small diffusers gen script, produce ONE
  Still A (576x1024) from ~/olga-ad refs + the assembled A prompt. Copy back to
  the Mac for screening. One image only — no batch, no other stills yet.

- STILL A attempt 1: REJECT (steward pre-read, LOOKED at pixels — the FaceID
  cosine 0.12 metric was nearly trusted blind; caught per cycle-016 lesson).
  Failures: (1) hallucinated glasses (no ref has them), (2) unnatural pink
  cheek/nose blush artifact, (3) SCENE IGNORED — text asked robe + crammed
  wardrobe + hangers + medium shot; output was a white-shirt selfie in a
  doorway. Diagnosis: FaceID identity weight too high -> her selfie-framed refs
  dominated composition, overrode the text scene (or img2img bleed). Likeness
  itself: partial-promising (resembles her). Images at ~/olga-ad/stills/
  A_sample.png + A_raw.png.
- INTENT: bounded iteration (attempts 2-4) — text-to-image (not img2img),
  FaceID identity-only at moderate scale (~0.6), add glasses/heavy-blush/red-
  cheeks to negative, confirm the wardrobe scene renders. Steward pre-reads by
  LOOKING; only a candidate passing (right scene, no artifacts, reads as her)
  goes to Roman+mom for the taste verdict. $0, local, one-at-a-time.

- STILL A iteration (attempts 2-4): FaceID-PlusV2 confirmed scene-vs-face
  cliff — any identity scale >0 forces a frontal portrait (+ blush/glasses
  return); scale-0 renders the wardrobe scene beautifully but is a stranger.
  Steward LOOKED at A_v2.png (scale 0): scene is correct + photoreal, and the
  stranger is coincidentally blonde/fair/blue-eyed = close to Olga's coloring.
- INTENT (method choice, steward's per taste-vs-picks boundary; $0/local/no
  account/same refs, within approved Route B "produce a screenable Still A"):
  FACE-SWAP path — render scene identity-off (have it), swap Olga's face on via
  InsightFace inswapper (already installed) which is pose/scene-agnostic. Prove
  it on the A_v2 scene first; if her face lands photoreally, apply to the
  proper A/B/C scenes. Fallback if inswapper weights unavailable: InstantID.
  Founder screens the RESULT for taste; steward pre-reads for bars.

- STILL A: face-swap SUCCEEDED and PASSES steward pre-read (I looked at pixels,
  not cosine). inswapper_128.onnx (554MB, sha-verified genuine) from public
  mirror; Olga's face (4-frontal-ref averaged embedding, buffalo_l) swapped
  onto the scale-0 wardrobe scene. Result ~/olga-ad/stills/A_swap.png (576x1024):
  reads as a plausible Olga, scene intact (open wardrobe, rail, hangers, grey
  robe over white tee, medium shot), no glasses/blush, seamless, only mild
  face-softness. GATE HELD: no B/C/video until Roman+Olga give the TASTE
  verdict on this one still. $0, local, refs stayed on box.
