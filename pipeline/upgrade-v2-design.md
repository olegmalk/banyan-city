# Upgrade v2 — the system that runs while nobody is awake

**Status: DRAFT for founder screening. Nothing in this document is in force.
No machine restarts, no queue unholds, no history rewrite happens until the
founder has read this and said the restart word. The hold stays until then —
and step 1 of the migration turns that hold from a prose marker into code.**

Scope: this is the *system* upgrade the founder asked for before continuation
("change and upgrade the system first for sure"). It is not a new production
process — episode-loop-v2.md remains the founder-ratified per-episode recipe
and carries into v2 unchanged (§7). This document answers the ~40-incident
failure inventory with enforced mechanisms, per the standing law: **a lesson
is learned only when a guard, gate, default or test enforces it.** Lessons
enforced in code stopped recurring; documented-only lessons recurred the same
week (proven empirically during ep2 week). Every answer below is therefore a
named piece of code, not a paragraph of advice.

---

## 1. One page — read this first (Roman: this page is for you)

**What this project is now.** A small render farm — a Windows gaming PC with
an RTX 5090, a laptop with a 5070 Ti, and some Macs — that makes short
animated episodes. Dad watches the finished options and picks; the machines do
everything else, including at night when nobody is awake.

**Why it stopped.** Two big reasons, and about forty small ones.

Big reason one: we stored the videos *inside git*. Git keeps every version of
every file forever, so the repository grew to 13 GB. Every deploy had to clone
all 13 GB before it could build a 2 MB website. One night the clone took 46
minutes and died, with nine more deploys queued behind it. The website host
never recovered and the project was stopped.

Big reason two: too many things only worked when a human remembered to run
them, and too many failures were *silent* — a job could crash the whole
machine and leave no record it had even been tried, so the machine would try
the same machine-crashing job again forever. A status page went stale because
"nothing scheduled them. Nothing ever had."

**What v2 does about it, in one sentence each:**

1. **Videos move out of git.** Each video lives on a disk under a name that is
   the fingerprint (sha256) of its own bytes; git keeps only a small text
   "manifest" saying what it is, where it came from, and its fingerprint. A
   gate in CI (the auto-checks GitHub runs on every push) refuses any commit that tries to put a big file back in.
2. **Every job writes "I am starting attempt 3" to a crash-proof journal
   BEFORE it starts** — so even if the job bluescreens the whole computer, the
   attempt is on record and a job gets at most N tries before it is retired to
   a `failed/` folder for a human to look at.
3. **Nothing is trusted until it is read back.** A file "exists" only when its
   bytes have been re-read and their sha256 matches. (We once rendered for
   days on a model file that was 93% holes but the right length.)
4. **Instruments are checked against reality before they judge anything.**
   Every automatic checker must first prove, on clips a human already labeled,
   that it agrees with human eyes. Numbers pick what to open; eyes decide.
5. **Every recurring action names its scheduler.** If a number on a status
   page is supposed to refresh hourly, there is a registered scheduled task
   that does it, and the page turns red by itself when the number goes stale.

**Your part.** The observability layer — the "bird-eye page" that shows every
machine's heartbeat, the queue depth, and the money meter (which must read
$0) — is **your CS capstone, Casefile 08** (§3.4). You build it in seven
layers, one lesson each, from "append a line to a CSV" up to "a CI job that
fails on purpose when a heartbeat goes stale." The steward scaffolds; you
write it.

**What humans still do.** Exactly three things: approve any spending (default
is $0 forever), approve anything published to the world, and make taste calls
(is this the goblin? which take is best?). Everything else runs in the
background and batches its questions for one screening pass. One honest
exception until the build finishes: if the big PC blue-screens overnight,
someone still has to log in next morning to restart it. v2 includes the fix
— the worker restarts itself when the machine boots — and until that fix is
in and tested, we say so instead of pretending.

---

## 2. Five failure classes → five enforced answers

Every mechanism below is a **guard, gate, default or test** with a name.
"Prose fix" is not a row in this table.

### 2.1 Git as distributed state (~10 incidents) → `MEDIA-OUT` + machine residency

Incidents answered: results stranded on unmerged branches; the box's 2-day
stale clone reporting committed files as missing; the 17-push night of
uncommitted fixes "not arriving" at remote runners; shared-index commit
clobbers; the 4.92 GiB pack that killed deploy clones
(pipeline/deploy-weight-finding-0818.md — "It will happen again"; it did:
6.11 GiB today); gitignore deciding durability by accident (macbook2 was not
even a git repo — 18 files stranded until `--collect` was finally built).

Enforced mechanisms:

- **`cas_gate` (pre-push + pre-commit hook on every machine; CI backstop):**
  refuses any new git object larger than 5 MB outside a small allowlist.
  The hook is the only *preventive* form — CI sees an oversized object only
  after it is already in history, where nothing short of another filter-repo
  rewrite removes it — and git does not distribute hooks, so the mechanism
  is named end to end: the hooks live in a **repo-tracked `pipeline/hooks/`
  directory**, activated per-machine by **`pipeline/install_hooks.sh`**
  (sets `core.hooksPath=pipeline/hooks`), and **`host_preflight` checks
  `core.hooksPath` on every machine at worker startup and refuses all jobs
  while the hooks are absent — fail-closed.** CI runs the same size check
  as the detection backstop, never as the mechanism. (Correction from the
  first draft, which claimed `safe_push.sh` "already wraps" this hook — it
  does not: it is an opt-in wrapper a bare `git push` walks straight past,
  and zero hooks are installed today. The tracked-hooks install is what
  changes that.) This is what makes the media migration *permanent* —
  without it, one stale clone or one habitual `git add` re-bloats the repo
  (community-known filter-repo pitfall).
- **CAS + manifest (default path for all render output):** artifacts land in
  the content-addressed store (§3.1), never in git. Durability is decided by
  *the manifest row*, never by gitignore: anything worth keeping gets a
  committed manifest (sha256, bytes, model, prompt, cost — the §7.2
  provenance leaf as it already exists), and the courier ships the bytes.
- **Machine residency (default):** queue state never leaves the machine that
  runs it (§3.2). Nothing operational is "distributed via git" anymore: git
  carries code, specs, manifests, ledgers — text. The farm-results branch
  pattern is retired for artifacts; the courier ships bytes to the CAS and
  the journal home. This removes the entire "is the remote clone fresh?"
  failure class instead of patching it.
- **`safe_commit.sh` / `safe_push.sh` go from opt-in to enforced.** Both
  are wrapper scripts today — a bare `git commit`/`git push` bypasses them
  entirely, and bare commit swept a peer's staged work twice. The same
  tracked-hooks mechanism closes this: the **pre-commit hook refuses any
  commit that is not path-scoped** (`git commit -- <paths>`), and the
  pre-push hook runs `cas_gate`. The wrappers stay as the ergonomic path;
  the hooks make bypassing them fail loudly instead of silently.

### 2.2 Silent failures (~9 incidents) → `VERIFY-THEN-ATTEST` + write-ahead attempts

Incidents answered: rc=0 jobs marked FAIL by hand-typed filename checks;
manifests attested before the copy happened; `allow_fail` swallowing exit
codes; identical jobs run twice for lack of idempotency keys (264 s of GPU on
2026-08-19; a byte-identical re-render on 2026-08-20); attempt counters blind
to BSODs (the animegen post-mortem in farm-queue.yaml: "any failure mode that
takes down the OS is invisible to the attempt counter"); weight files that
were 88–93% holes passing size checks on macbook1/macbook3.

Enforced mechanisms:

- **`attest_after_readback` (library default, used by runner, courier, and
  every manifest writer):** no DONE record, no manifest row, no receipt is
  written until the artifact's bytes have been *re-read* and their sha256
  computed and matched. `mac_preflight.py` (sha256-vs-filename) generalizes
  from model weights to every artifact class. A record that precedes its
  bytes is the bug this rule exists to kill. And because a "library
  default" is bypassable by any new hand-rolled manifest writer — the exact
  genesis of the original incident — the bypass is made loud:
  **`manifest_schema_gate` (CI check, in `lint_genome.py`)** requires every
  manifest row to carry `readback_sha256` + `readback_ts` fields that only
  the attest library writes. A manifest without them is a red build, not a
  quiet row.
- **Idempotency key = job id, enforced box-side (`dedupe_at_the_queue`):**
  the content-sha duplicate guard (box_enqueue guard 8) is *mirrored on the
  box*, where `done/` actually lives — so dedupe holds regardless of which
  machine enqueues and regardless of ssh health at filing time. The runner
  refuses a job whose id+sha already sits in done/failed; `--again` stays the
  loud override. Outputs land in job-id-keyed paths with the attempt number
  in the sidecar (SQS at-least-once contract: double execution is designed
  for, so it must be harmless).
- **`no_hand_typed_verdicts` (spec-compiler refusal + test):** exit code is
  the verdict; filename existence checks must be *derived* from the spec
  (the standing "publish glob derived from --arm, never typed" rule, now
  tested), and `allow_fail` is removed from the vocabulary — a step that
  may fail declares an expected rc set, anything else is FAIL. The
  enforcement point that covers specs which do not exist yet: the spec
  compiler (`bars_from_done_when`, §2.4) **refuses literal path/filename
  verdict clauses in any spec, runtime-authored included** — a checked-in
  test alone cannot vet a spec a lane writes at 3am; the compiler every
  spec passes through can.
- **Write-ahead attempt journal** (§3.2) — the attempt exists in history even
  if the machine bluescreens one second after the record is fsync'd.

### 2.3 Process/OS fundamentals (~9 incidents) → `JOURNAL+SWEEP` + host preflight

Incidents answered: heartbeats beating over dead children; window-CLOSE
killing workers silently (self-concealing — the death removed its own
evidence); cp1252 decode crashes on reader threads; blocked stderr pipes
indistinguishable from hangs; 64 GiB loads attempted on 31 GB machines;
wrong-venv verification; the b4 WDDM-thrash bugcheck loop.

Enforced mechanisms:

- **`attempt_journal` (machine-local, crash-proof):** SQLite in WAL with
  `synchronous=FULL` on the STARTED record (or fsync'd NDJSON). The STARTED
  row `{job_id, attempt_n, machine, pid, ts}` is committed and fsync'd
  **before the render process is spawned** — the Brandur/Stripe
  idempotency-key pattern (insert the intent record in its own transaction
  before doing the work). SQLite fine print is load-bearing: WAL +
  `synchronous=NORMAL` survives app crashes but **can lose a committed
  transaction on OS crash/power loss** — and a BSOD is an OS crash — so the
  pre-work record specifically runs at FULL. Heartbeat prose lines become a
  *projection* of the journal, never the source (today attempts are
  reconstructed by grepping prose — that inversion ends).
- **`startup_sweep` (runner default; replaces leases):** any job found in
  `running/` at worker startup is by definition an interrupted attempt —
  journal it as INTERRUPTED, requeue if attempts < max_attempts, else retire
  to `failed/`. With exactly one sequential worker per machine and
  machine-local queues, this is strictly simpler than visibility timeouts
  and has no clock-skew double-run mode (leases exist to arbitrate multiple
  consumers; we have one per queue — GitLab's Windows-runner heartbeat bugs
  are the cautionary tale for the alternative). box_runner's rc-93 adoption
  already does half of this; the journal makes it whole.
- **`failed/` as a first-class dead-letter dir (guard):** hard attempt cap
  enforced in code, and — inverting Kubernetes' "infra failures are free
  retries" — **a job that takes down its own host CONSUMES budget** and hits
  the cap fast. This is the code form of the b4 WDDM ban: a machine-killing
  job can never loop, because its attempts were journaled before each death.
- **`reader_hygiene` (defaults in the runner's spawn wrapper):** all
  subprocess pipes read with `utf-8, errors=replace` (kills the cp1252
  class); stderr always drained by a thread (a blocked pipe can no longer
  impersonate a hang); every job gets a `max_runtime` kill (box_runner has
  none today — named hole).
- **`host_preflight` (guard, runs on the host that will run the job —
  default-DENY):** the spec MUST declare its resource needs; a job with
  **no declared memory requirement is REFUSED, not waved through**, because
  the canonical 64-GiB-on-31-GB load was precisely an *undeclared*
  requirement — default-permit would re-admit the incident this guard
  exists to stop. Declared needs are checked against the host's measured
  RAM/VRAM, and declarations are sanity-checked against measured priors for
  the job kind (a job kind that historically peaks at 20 GB declaring 2 GB
  is flagged, not trusted). It also asserts the interpreter path
  (wrong-venv class), asserts host identity — box_autofill gets the host
  guard it lacked when it ran on the Mac and built a literal
  `C:\banyan-queue/` directory in the repo root while publishing a tick
  record about the wrong machine — and asserts the tracked hooks are
  installed (`core.hooksPath`, §2.1), fail-closed.
- **Workers run as at-boot scheduled tasks under auto-logon, never in a
  closable window** (deployment default) — with the mechanism and its
  compliance check named, because "run as services" was a phrase, not a
  fix. Mechanism on the box: Windows auto-logon + a `banyan-box-worker`
  scheduled task set to run at startup and restart on failure, so a BSOD
  reboot brings the worker back with nobody at the keyboard. Compliance
  check: `host_preflight` verifies the task exists and is enabled and that
  the worker's own process was launched by it, not from a console session —
  a worker started in a closable window FAILS preflight instead of silently
  reintroducing the class. Until this lands and passes its induced-failure
  test (§6 step 6), post-BSOD restart is an honest human-awake dependency,
  named as such in §4. And when death happens anyway, the journal+sweep
  pair means the evidence survives the window.

### 2.4 Measurement validity (~7 incidents) → `FALSIFY-FIRST` + derived bars

Incidents answered: a mean hiding 38% barely-moving frames (rendered 15×
before one human look); an experiment whose variable never reached the code
(byte-identical outputs "proving" no effect); QA checks asking
nearby-but-wrong questions for 4 cycles; detectors never falsified against
ground truth; the inverted depth metric (0.516 on a motionless clip vs 0.290
on a full stand-up — "ranking takes by it selects against the thing we
want", cycle 017/018); the 0.53× ship cutoff that passed five independent QA
gates; cycle 018's "12 of 12" measured against a 2-verb bar on a 3-verb
done_when (brush: 0 of 4 when audited — "an untested clause reports as
silence and silence got read as assent").

Enforced mechanisms:

- **`bars_from_done_when` (spec-compiler gate):** job spec bar clauses are
  derived mechanically from `review/ep2-picks/done-definitions.yaml` (and
  successors). Every done_when verb either gets an instrument clause or a
  loud `NO-INSTRUMENT: <verb>` flag in the spec and the report — no verb can
  be silently absent from the measurement again. Companion guard, already
  specified in the ladder: **spec derivation strips verdict/pick/sweep keys**
  so a child spec cannot inherit its parent's conclusions (found three times
  in one night).
- **`falsify_before_trust` (gate on every instrument, enforced at the spec
  compiler):** no detector scores a batch until it has passed an
  overlay-verified run against a labeled set — the head-top detector caught
  its own speckle bug only because "the overlay disagreed with the number."
  "By rule" alone is prose, so the rule gets a home:
  **`pipeline/instruments.yaml`** registers every instrument with the path
  of its falsification record (labeled set, overlay run, date), and the
  spec compiler **refuses to emit a verdict-grade bar clause from any
  instrument that has no falsification record** — unfalsified instruments
  may appear in triage clauses only. The registry itself is linted; a new
  detector nothing checks is now a lint error, not a habit.
- **`variable_reached_the_code` (assertion in every A/B spec):** an
  experiment's arms must produce non-byte-identical outputs, or the run
  FAILS as an invalid experiment rather than reporting "no effect."
- **Distribution clauses, not means (standard bar clauses):**
  `near_dup_pair_cap` (share of frame pairs under 0.5 interframe — the
  clause "three beats have needed and none has ever had") and
  **`playback_rate_check` in qa_episode** (the gate all five existing gates
  lacked when the 0.53× cut shipped; a person reading a log line caught it).
- **`sample_before_batch` (box_enqueue guard 9, mirrored box-side in
  box_autofill and box_runner):** the founder's loudest rule stops being
  prose — the first draft left it documented-only, which is this document's
  own definition of unlearned. Every job spec carries a **recipe
  fingerprint**: a hash over everything that defines the recipe (model,
  LoRA set, sampler/steps/CFG, prompt template, post chain — seed and beat
  excluded). Any batch — a spec fanning wider than one output, or a set of
  specs sharing a fingerprint — is **REFUSED unless
  `ledger/sample-verdicts.yaml` holds a founder-verdict row for that
  fingerprint** (`fingerprint, sample_job_id, verdict, by, date`), written
  at screening when he looks at the one sample. The guard slots in beside
  the consumer guard that already proves the pattern is implementable in
  box_enqueue; mirroring it box-side means no enqueue path around it.
  `judging_sentinel` (§3.3) is the complement, not the substitute — it
  blocks the *next* rung after an unjudged landing; this guard stops the
  batch-sized *first* rung the 15-beat waves used to ride in on. "A metric
  agreeing with me is not a sample" is now a return code.
- **Eyes verdict stands (unchanged rule):** metrics triage, cold-read of
  frames decides; instruments exist only for canon gates (identity, licence,
  publish QA) — never per-beat aesthetics. Promotion of any recipe element
  requires a **pre-registered seed wave** with the bar written before the
  renders (cycle 017's remedy: 4-of-5 holds or the lane stops — it retired
  the expanded camera negative at 2/5 by rule). Single watched samples
  promoted as levers at a ~25% base rate is the mistake this preserves the
  record of.

### 2.5 Staleness / concurrency / automation (~6 incidents) → `NAMED-SCHEDULER` + code holds

Incidents answered: TOCTOU races on the shared git index; liveness misjudged
from single stale signals seven times; the queue-history page refreshed only
by hand-run commands ("Nothing scheduled them. Nothing ever had." — stale
twice on the founder, ~40 overnight renders invisible); the stop itself
enforced by a prose marker (`.HOLD-project-stopped-0822`) that **no code
reads**, plus a powered-off box; the hourly queue-refresh workflow left
failing every hour after the stop.

Enforced mechanisms:

- **`schedulers.yaml` registry + `stale_gate` (test):** every recurring
  action — telemetry tick, autofill, queue-history refresh, kind-median
  refresh (`box_job_minutes.py --yaml`, hand-run today, drifted ~19% in a
  day), `local-disk.yaml` (hand-run today), dashboard build, deadman pings —
  has a registered scheduler (scheduled task, workflow, or tick) named in one
  committed file. Every measured file carries `generated_by`, `refreshed_by`,
  `max_age`; a CI test and the dashboard build **fail** when any measured
  surface is older than its declared cadence. A hand-refreshed number is a
  lint error, not a habit.
- **`HOLD` as a first-class code gate:** a `control/HOLD` file (mirrored to
  the queue root) that box_enqueue, box_autofill, box_runner and the
  queue-refresh workflow all check and refuse on. The honest current state,
  stated exactly: the stop today is a prose marker that lives **box-side
  only** (`.HOLD-project-stopped-0822` on the box's queue root — it is not
  in this repo), **no deployed code reads any queue-wide hold** (the box's
  autofill handles `.HOLD` only as per-job renames; box_runner and
  box_enqueue check nothing), and code cannot be deployed to a powered-off
  machine — so "re-express the hold before any machine powers on" was
  physically impossible as first written. The real sequence is §6 step 4:
  the box powers on **with its scheduled task disabled as the first human
  action**, the hold-aware code deploys, the task re-enables, and one tick
  is watched refusing on HOLD — all before any force-push. Re-powering with
  the task intact would resume ticking with nothing structurally stopping
  it. Unhold is a founder-word event, recorded.
- **One-writer / machine-residency (default) + the pre-commit scope hook:**
  the queue/artifact half of the TOCTOU class dies with
  distributed-state-via-git (§2.1) — but the shared-git-index half does NOT
  die by residency alone, because agent lanes still share the Mac worktree
  for code, manifests, ledgers and cycle docs. That half is closed by the
  tracked **pre-commit hook** (§2.1) refusing any commit that is not
  path-scoped — "ALWAYS `git commit -- <paths>`" as a return code instead
  of a memory entry that was already "not followed" by its own header's
  admission. Queues are single-writer by construction; ledgers are
  GENERATED, never merged (standing rule, kept).
- **Liveness is never one signal (rule + code):** the worker that owns a
  machine-local queue is the only thing that can truthfully say a job died,
  and it says so at its own restart (journal + sweep). Externally, liveness
  is judged from *multiple* surfaces: journal, heartbeat file age (computed
  client-side against `Date.now()`, because the static page itself can be
  stale), and the healthchecks.io deadman that alerts when pings *stop* —
  which a dashboard nobody is watching cannot (§3.4).
- **Stop-aware workflows:** queue-refresh.yml checks `control/HOLD` and
  exits green-as-skipped during a hold — no more hourly red runs on a
  stopped project. The same repair pass (§6 step 1) retires its stale
  assumptions before the rewrite invalidates them mid-flight: it still
  self-describes as a Vercel production deploy (Vercel is deleted) and
  pulls the farm-results-rtx5090 branch that §3.2 retires.

---

## 3. Architecture

### 3.1 Repo: media OUT of git

**Chosen pattern (research-backed): plain content-addressed store (CAS) +
manifest-in-git.**

- **Primary store:** sha256-named blobs on one designated LAN disk (the
  box's second disk or a Mac external, reachable over SMB/ssh-rsync). This
  is what LFS does internally (pointer = hash + size) minus the hosted
  quota, and the standard small-render-farm pattern. It is $0, quota-free,
  and identical on Windows and macOS — just files plus a python sha256
  check, an idiom the repo already speaks (`mac_preflight.py`).
- **Manifest-in-git:** one small committed YAML per artifact — sha256,
  bytes, model, prompt, cost — which is exactly the §7.2 provenance leaf
  already required. **Provenance is preserved by construction**, which is
  the constraint the never-made architecture call was reserved over.
- **Resolve script:** `cas_get` (manifest → blob by hash, sha256-verified on
  read) is the only sanctioned way to obtain media; `cas_put` the only way
  to store it (verify-then-attest built in). The courier repoints at the CAS
  disk instead of the git repo — the minimal change to the existing
  `C:\banyan-farm\courier-box\farm-out\` flow — and gets a **durable push
  path** (retry with backoff, no 60 s cap: 48 courier pushes died at that
  cap, blocking every box plate).
- **Durability tier:** GitHub Releases via `gh` for **founder-approved
  finished artifacts only** (per current docs: <2 GiB/file, 1000
  assets/release, no total-size or bandwidth limit, retained indefinitely,
  $0). One release per episode/milestone. CAS disk + Releases = two copies
  of everything worth keeping.
- **Rejected, with reasons:** Git LFS free tier (10 GiB storage + 10 GiB
  bandwidth/month; bandwidth is burned by every farm clone and a $0 budget
  hard-blocks LFS mid-month — recreating the deploy death one layer up);
  git-annex (right model, but it treats NTFS as a "crippled filesystem" —
  wrong for an unattended Windows box).

**Migration plan (Route A, recommended): in-place `git-filter-repo` rewrite.**

0. **Prerequisites, verified not assumed:** `pip install git-filter-repo`
   (it is NOT installed on this Mac today — the rewrite cannot run without
   it); confirm force-push feasibility on olegmalk/banyan-city main via
   `gh api` (if the branch is protected, lift force-push protection for the
   migration window and restore it after — a named step, not a surprise).
1. Stop all farm lanes — and per §6's order, the box is ON, its scheduled
   task disabled, hold-aware code and the tracked hooks deployed to it,
   BEFORE this rewrite's force-push. A powered-off machine can neither be
   updated nor trusted to wake politely.
2. Fresh clone; `git filter-repo --analyze` to enumerate big blobs.
3. **Copy every blob into the CAS and write its manifest BEFORE stripping**
   — no provenance is lost, verified by sha256 readback and a count match.
4. Strip: `--strip-blobs-bigger-than` + path filters on media dirs
   (genomes/sapling media 1070 MB/1948 files, review/, farm-out/ — "it is
   render media, essentially all of it").
5. Verify: `git count-objects -vH`, full site build, `qa_local.py` PASS.
6. Force-push. Workflow behavior at that moment, stated not assumed:
   pages.yml and mirror.yml fire on the push and rebuild from the rewritten
   tree — that is the desired outcome, watch them go green; queue-refresh.yml
   must already be HOLD-aware and stripped of its stale Vercel/farm-branch
   assumptions (repaired in §6 step 1, before this point). Then **every
   machine re-clones fresh** (one push from a stale clone reintroduces
   every stripped object — the `cas_gate` hooks, verified installed on
   every machine by host_preflight's fail-closed check, are the permanent
   safeguard; the fresh clones are the hygiene).
7. Record an old→new SHA mapping (loop docs and ledgers cite SHAs that go
   stale); note GitHub retains old objects server-side until support prunes,
   so the hosted size drop may lag.

Route A keeps the repo name, issues and URLs — critical because the repo IS
the product and standing memory says never recreate the old name (the
2026-08-10 move already killed redirects once). **Route B (fresh repo, old
one frozen read-only)** is the fallback only if the rewrite fails
verification. Context that makes this non-optional: 13 GB already exceeds
GitHub's documented 10 GB on-disk guidance, and the deploy death was
platform-side clone-throughput variance over a constant multi-GiB pack — a
20× spread with no input change. No ignore rule or build guard can fix it;
both run post-clone.

### 3.2 Queue v2: durable records, idempotency, machine residency

**Keep the directory queue.** The maildir/dirq pattern (write to staging,
fsync, atomic same-volume rename into `ready/`; claim = rename into
`running/`; terminal move into `done/`/`failed/`) is 25-year battle-tested
(qmail maildir, CERN dirq, Postfix's directory-per-state spool), and
box_runner/box_enqueue already implement ~80% of it. Flamenco — Blender's own
small-farm manager on plain SQLite — is the existence proof that this scale
needs no broker, no Redis, no always-on daemon. box_enqueue's eight guards
and measured thresholds (0.62 flatness, the refs denylist) carry over
untouched; retuning them requires re-running the labeled sets the file names.

**The four deltas (all named in §2):**

1. `attempt_journal` — typed, machine-local, fsync'd STARTED-before-spawn
   (§2.3). Journal rows ship home via the courier so attempt history
   survives even machine loss — never via the repo.
2. `startup_sweep` — running/ reconciled against the journal at worker
   start; directories are the queue, **the journal is the history**. (Windows
   caveat honored: same-volume rename is atomic on NTFS but there is no
   directory fsync — after power loss, trust the journal, not directory
   membership.)
3. `failed/` dead-letter with a hard cap; host-killing failures consume
   budget (§2.3).
4. `dedupe_at_the_queue` — the already-ran/content-sha check mirrored
   box-side where `done/` lives (§2.2).

**Zombie guard:** completion must present the attempt number it holds
(litequeue's claim_id pattern) — a resurrected process cannot mark DONE a job
that was requeued and re-run.

**Scheduling fixes with named owners at stop, now in scope:** box_autofill
scores by argv fingerprint and never reads `est_minutes` (a 55-min training
job scores 0.9 min) — fixed to est_minutes-aware scoring; box_runner gets
`max_runtime` kill and preemption of over-cap jobs; publish-token filenames
get collision-proof derivation (the beat-06-under-beat-12 incident, same
family twice in six hours).

**Deployment drift ends — generally, not one filename at a time:** the box
runs a hand-copied 2026-08-10 box_runner.py that has deliberately drifted
from the repo — the repo's runner improvements have never executed on the
card. v2 restart runs `box_autofill.py --verify-deployed`, chooses the
runner version deliberately, and makes runner drift *fatal* (today only
autofill drift is). The `--expect-drafts-sha256` stale-wording guard extends
to render_wave_sample.py (the named identical hole). And because gating
three named files leaves every OTHER repo script free to run stale one file
over: **every job spec pins `repo_sha`** — the repo commit it was authored
against — and **the runner refuses the job with a loud rc unless its
clone's HEAD matches or contains that SHA** before invoking any repo
script. A stale clone now refuses work instead of silently running old
code; that closes the stale-clone / 17-push class at the runner, not per
filename.

**Two-queue split resolved:** the older farm-queue.yaml/farm_worker layer is
formally retired to read-only history (its documented pathology — a public
queue card promising a render no machine could ever claim, ep2-b15 — came
from exactly this split). One queue system: the box directory queue plus
mac_enqueue for Macs, both under the same journal/sweep/dedupe contract. If
two workers ever share one queue, adopt the litequeue/goqite SQLite schema
(READY/LOCKED/DONE/FAILED + claim_id + visible_at) rather than inventing one
— not before.

### 3.3 Verification: verify-then-attest everywhere

- `attest_after_readback` on every artifact class (§2.2) — sha256 of content
  is the only existence proof; size/name/manifest presence prove nothing
  (the 88–93%-holes incident is the type specimen).
- `bars_from_done_when`, `falsify_before_trust`,
  `variable_reached_the_code`, `near_dup_pair_cap`, `playback_rate_check`
  (§2.4) — the instrument layer.
- Kept intact: proof_receipts, qa_local.py (route sweep + content checks),
  qa_episode.py (+ the new clauses), mac_preflight.py at worker startup and
  before every model load, the stale-drafts sha chain from enqueue to
  render-time rc 12.
- Judging debt becomes a gate, not a backlog: **`judging_sentinel`** — a
  landed-but-unjudged artifact **blocks its lane's next rung** (chained on
  sentinels per the no-artificial-delay rule: when X lands, judging X is the
  next runnable job, and rung N+1 depends on it). **WHO judges is named,
  not ambient**, per the widened 2026-08-18 boundary: defect/pick judgments
  (bars, defect rates, which take is usable) are the **steward's
  cold-read** — itself a runnable job the sentinel chains at any hour, so
  machines never wait on a human for those; taste-class judgments
  (identity, look changes, axis calls, anything R4) are the **founder's —
  Roman's** — batched into the next screening pass and **non-blocking for
  machines**: the one lane whose rung N+1 needs his verdict waits, the card
  works every other runnable lane meanwhile. Twelve beat-17 clips sitting
  unjudged, a rung already-run-and-unread for 7.5 hours, round 7 "ran and
  nobody read it", beat 20 riding eight cuts unjudged — that class ends by
  dependency, not diligence.

### 3.4 Observability: the bird-eye page — **Roman's Casefile 08 capstone** (steward-scaffolded)

$0, no always-on server, buildable by a 14-year-old — by design, because a
14-year-old is building it:

- **Per-machine status file** each tick: the node_exporter
  textfile-collector *contract* without the daemon — one small JSON/flat
  file (epoch, gpu util, queue ready/backlog depth, last job, disk free),
  written atomically (temp + rename; matters on the Windows box).
- **Transport = git-scraping** (Simon Willison's pattern, inverted to push):
  machines commit their status file to a **new tiny `banyan-status` repo**
  — never the main repo, whose committed media is the anti-pattern that
  killed deploys. Commit history IS the queue-depth/liveness history, free.
  Multi-writer handled honestly, since this is the one place v2 would
  otherwise reintroduce distributed-state-via-git: **each machine pushes
  only to its own `status/<machine>` branch** (the build reads all
  branches), so concurrent pushes cannot race a shared head and no
  retry/rebase dance exists to go wrong. Making this repo PUBLIC is a
  publication of telemetry under the founder's account and therefore his
  call — **§5.4, undecided**; the dashboard builds locally either way.
- **One Python build script** turns the ledgers (including a mirrored
  `ledger/render-spend.csv` vs `budget.yaml` caps) into a single static HTML
  page with inline-SVG sparklines: per-machine liveness tiles, queue
  depth/history, spend meter (which must read $0). Runs via GitHub Actions
  **on push** (a landing heartbeat rebuilds the page immediately) plus an
  hourly `schedule` safety net; published on GitHub Pages. Public repo →
  Actions minutes unlimited, Pages free — $0 forever (this is the why
  behind §5.4's public-repo recommendation; the decision is his). The
  status repo holds heartbeat timestamps, counts and spend totals only: no
  secrets, no media — and the deadman/ntfy URLs are *named* secrets that
  never enter it (below).
- **Liveness judged client-side** (inline JS: heartbeat epoch vs
  `Date.now()`) because the static page itself can be stale.
- **Deadman = healthchecks.io free tier** (20 checks; ~8–10 needed; the
  account creation is the founder's — **§5.4, undecided**): one
  `curl https://hc-ping.com/<uuid>` at the end of each machine tick and each
  scheduled task. It alerts when pings STOP — the thing a dashboard nobody
  is watching cannot do. Push-to-phone via ntfy.sh ($0, no account).
  **The ping UUIDs and the ntfy topic are CREDENTIALS**, named as such
  under the no-secrets rule: a leaked ping URL lets anyone keep a dead farm
  looking alive — silently defeating the one alert built for when nobody is
  watching — and a leaked ntfy topic lets anyone push to the founder's
  phone. They live in machine-local untracked config (`.env`-class files),
  never in the status repo, its workflows, or any public surface.
  **Actions cron is never the liveness detector** (best-effort, 5–30 min
  delays, 60-day auto-disable) — it is only the cosmetic refresh net.
- **Lessons-become-code hooks:** the build script **exits nonzero** when
  spend exceeds budget.yaml caps or any heartbeat/measured surface is stale
  beyond its registered `max_age` — the workflow itself goes red and GitHub
  emails. The threshold is a gate in code, not a sentence in a doc.
- **Falsified like any instrument:** acceptance test is killing a heartbeat
  on purpose and watching the alert fire (§6 step 5).

Roman's seven layers, one lesson each: (1) CSV append + atomic writes;
(2) git as transport/database; (3) parsing + staleness math from epochs;
(4) HTML by string-building + raw inline-SVG sparklines; (5) client-side JS
liveness; (6) CI as code — making the build FAIL on a crossed threshold;
(7) HTTP as a heartbeat — the one-line curl deadman.

### 3.5 Scheduling: no hand-run steps anywhere

`schedulers.yaml` + `stale_gate` (§2.5) is the whole story: **every
recurring action names its scheduler**, every measured file names its
refresher and max age, and staleness is a red build, not a discovery. Items
folded in on day one: queue-history refresh (repair the existing
queue-refresh.yml — it is the already-built automation of the previously
hand-run queue_history.py + queue_thumbs.py pair — and make it HOLD-aware),
kind medians, local-disk.yaml, telemetry tick, autofill tick, dashboard
build, deadman pings. The founder's own stop gets the same treatment: HOLD
is code (§2.5), checked by everything that could otherwise act.

---

## 4. Operating model: background by default, three human gates

- **Runs with nobody awake.** D19 provisional mode is already sanctioned:
  rendering, voice and assembly do not wait for the founder; machine work is
  scheduled by dependencies, never human hours; the GPU is never idle while
  a runnable job exists; `--backlog` + autofill is how work is left for a
  card nobody will be awake to feed. "Tomorrow" is valid only when a
  physical dependency sets the time.
- **Two human-awake dependencies survive, named rather than hidden:**
  (1) **post-BSOD worker restart on the box.** Today it needs a human
  login. The fix is in the v2 work — auto-logon + the at-boot
  `banyan-box-worker` scheduled task, with host_preflight's
  launched-by-task compliance check (§2.3) — and until that is deployed and
  its induced-failure test passes (§6 step 6), an overnight BSOD halts that
  machine until morning, and the report says so instead of pretending.
  (2) **Sample verdicts and taste-class judgments are founder eyes on
  purpose** — that is the human gate working, not leaking: a new recipe's
  batch waits for his look at its one sample (`sample_before_batch`, §2.4),
  and judging_sentinel routes taste-class verdicts to him batched while the
  steward's cold-read handles defect/pick judgments at any hour (§3.3).
  Machines never idle on either — every other runnable lane keeps the card
  busy while a human question is open.
- **Humans gate exactly three things:** money (any spend, engine + amount as
  pitched, substitutions stop and re-ask; default $0 — a key in .env is not
  permission), publication (the founder kept this gate explicitly: "i'd
  rather review the final result" — explicit pass, "not a window, not
  silence, not an inference from a passed bar"), and taste (R4: axis scores,
  trunk/graft calls, what a character IS). §6 stands as written: no voice,
  footage or assembly from a script the founder has not approved (modified
  only by D22's partial, uncountersigned trunk delegation).
- **Founder screening batches.** Per the 2026-08-21 amendment: the steward
  iterates find→fix→re-render until a beat has 2–4 genuinely good DISTINCT
  versions, then presents the selection — the founder picks from finished
  options, never receives a defect report as his to-do. ~One open taste
  question at a time, always with pixels. Blocking gates (first still of a
  beat, any character image, any look change, any assembled episode) summon
  the founder by push notification while the steward works on something
  unblocked.
- **One sample before any batch** (founder 2026-08-03 — now CODE, not
  prose): `sample_before_batch` (§2.4) refuses any batch whose recipe
  fingerprint has no founder-verdict row in `ledger/sample-verdicts.yaml`.
  One per recipe change, looked at, before anything scales. "A metric
  agreeing with me is not a sample" — and now not a bypass either.
- **No work without a consumer** (unchanged): the episode cut is the
  consumer; every queued job is consumer-named. Autofill never authors work;
  empty backlog is a loud state, not filler.

---

## 5. FOUNDER DECISIONS — options and a recommendation each; **nothing here is decided**

**5.1 Hosting** (both Vercel projects deleted; banyan.city 404s; GitHub repo
+ Pages mirror are the only surviving surfaces).

- **Option A — GitHub Pages mirror as the site (recommended):** already
  built, already deploying, $0, and after the media migration the clone is
  small. Limits (1 GB site, 100 GB/mo soft bandwidth) are comfortable for a
  text-plus-manifests site with media in the CAS/Releases. D18 satisfied
  trivially: no meter needed for an unmetered $0 surface.
- **Option B — re-create a cardless Hobby Vercel project *after* the repo
  slims:** viable post-migration (the deploy death was clone weight), but
  D18 binds: a code-side guard and a $0-fed monitoring line land in-repo
  **before** the service is connected — "a meter nobody can read is not a
  meter", and a dashboard toggle does not satisfy it. Never add a card.
- **Option C — no public site for now:** repo stays the shelf; episodes
  screen locally via serve_local/qa_local. Cheapest; loses the public tree.
- Also his: **confirm the Vercel billing cancellation actually happened** —
  it was left as a founder dashboard step and nobody verified it. And the
  domain: banyan.city currently points at nothing; Pages can serve it or it
  can lapse — founder's name, founder's call.

**5.2 Distribution — resume or not.** TikTok @banyan.city is live; Reddit
age-gated; HN parked; warm-account rule stands (2–3 days before links).
Posting/announcing is founder-reserved by list. **Recommendation:** hold all
distribution until an episode passes his publish gate under v2; then decide
per-platform. No new accounts warmed until he says the show is publishing
again.

**5.3 Money rails.** None are needed for anything in this document — every
component is $0 by construction. D5's rider stands (watering split
re-confirmed before the first real funds; money rails are human steps); D12
parked them indefinitely; D18 binds any future metered service.
**Recommendation:** keep $0; open nothing.

**5.4 Observability's two founder items** — moved here from the build
sequence, where the first draft had them buried inside a step; step-0
wholesale screening is not the "explicit pass, not inference" standard this
document holds everything else to.

- **The public `banyan-status` repo + its Pages page is a PUBLICATION** —
  machine telemetry (heartbeat epochs, queue depths, spend totals; no
  media, no names, no secrets) published to the open internet under the
  founder's account, and publication is founder-reserved. Options:
  **A — public repo** ($0 forever: unlimited Actions minutes, free Pages;
  content is telemetry only). **B — private repo** (Actions metered at
  2,000 free min/mo; Pages is not free on private repos at this plan, so
  the page becomes artifact-download-only — a worse dashboard, still $0 if
  it stays under the minutes). **C — no status repo** (dashboard builds and
  serves locally only; the deadman still alerts). **Recommendation: A.**
  Undecided until his explicit pass.
- **healthchecks.io requires creating an ACCOUNT** — account/credential
  creation sits on the founder-reserved boundary, so it is his to make or
  delegate, not the steward's to assume. Options: **A — founder creates
  it** (free tier, no card, ~2 minutes, 20 checks). **B — no deadman
  account:** ntfy.sh alone can push alerts but cannot notice *silence*,
  which is the entire point of a deadman — B keeps the dashboard but loses
  the 3am guarantee. **C — an Actions-cron deadman** (rejected already in
  §3.4: best-effort scheduling, 60-day auto-disable).
  **Recommendation: A.** Undecided.

**5.5 The decision queue** (batched for one pass, not a question chain —
listed so v2 doesn't silently re-decide any of them):

- **Media-split architecture sign-off** — the §3.1 design is the steward's
  recommendation for the call that was explicitly reserved founder-awake;
  §7.2 provenance is preserved by the manifest design. This one gates the
  whole migration.
- **D23** (automation charter) — effectively v2's operating-model contract,
  already drafted to his own quotes. Bring for signature ("D23 approved",
  partial signatures welcome); **silence is NOT acceptance**, and v2 does
  not behave as if it were signed. Pre-named build debt ships with the v2
  work so signing is not mistaken for having it (check_canon_drift.py into
  CI; a canon consumer for review/inbox/regen.py).
- **D19's one ratification commit** (§6 read-before-media → read-before-
  publish + retiring 002b's stale leaf sentence) — until then §6 stands as
  written. **D22 countersignature** (AI-trunk §6 delegation) — the restart
  conversation is the natural moment.
- **D15** (licence: three ways out; LICENCE_DEBT ratchet at 38, CI red until
  decided) and the **D16 item-18 scope ruling** (LTX train-on-output; the
  sapling LoRA used zero LTX pixels, enforced in code — his ruling, now with
  pixels attached). Both block any standing self-training program and
  general stills-derived publishing.
- **D9** (T3 publishable-leaf criteria), **D10** (four long-voice ep1 beats
  — touches an approved script, §6), **D11** (crowd shot board
  ratification), **D13** (five PixVerse beats vs CC BY), **D14** (beat 4's
  unshown fall). All founder-only; none block the system upgrade.
- **Two taste cards left open at the stop, re-surfaced not re-derived:**
  guardcast round 5 (four seated candidates C-spare/E/F/J on
  /review/ep2-guardcast2-0822 — he answers "guardcast5 <letter>") and the
  never-taken morning look at review/ep3-sapling-lora-0822/SHIP-0822.md.

---

## 6. Migration sequence — from the current held state, each step verified, one-sample-first

Order matters, and the numbered steps now agree with their own preamble
(the first draft said "machines before the force-push" and then force-pushed
one step before powering the box — fixed): enforcement lands before
machines, **the box powers on hold-safe before the media migration's
force-push**, migration before production. **Step 0 gates all.**

- **Step 0 — founder screens this document; prerequisites verified.**
  Restart word given or not. Verification: his word, recorded in
  DECISIONS.md. Two prerequisites are prep, not action, and are verified
  here rather than discovered mid-migration: `pip install git-filter-repo`
  (it is NOT installed on this Mac today) and the `gh api` branch-protection
  check on olegmalk/banyan-city main (§3.1 step 0 — if protected, the lift
  and restore are named steps). Until the word, only steps 1–3 (Mac-local
  code + tests: no GPU, no force-push, no spend, fully reversible) may
  proceed as prep.
- **Step 1 — make the stop true in code (repo-side).** Implement
  `control/HOLD` + checks in box_enqueue/box_autofill/box_runner/
  queue-refresh.yml. Honest referent: the current stop marker
  (`.HOLD-project-stopped-0822`) lives **box-side only** — it is not in
  this repo — so step 1 lands the repo-side gate and step 4 deploys it to
  the box; nothing here pretends a powered-off machine is already guarded.
  Repair queue-refresh.yml in the same pass: HOLD-aware (ends the hourly
  red runs), its stale Vercel-production-deploy self-description retired
  (Vercel is deleted), its farm-results-rtx5090 pull retired with the
  branch pattern (§3.2) — before the rewrite invalidates those assumptions
  mid-flight. Land `pipeline/hooks/` + `install_hooks.sh` and install on
  this Mac; add the box_autofill host guard. Verification: unit tests for
  the gate; `git config core.hooksPath` returns `pipeline/hooks`;
  `gh run list` shows green-skipped hourly runs.
- **Step 2 — settle the REAL dirty tree: 281 paths, not 14.** *(Steps 1–3
  are one Mac-local prep phase; within it tooling lands first — step 3's
  `cas_put` exists before this step runs.)* Three
  classes, three treatments, none of them "commit it all":
  (a) **Modified tracked media** — the ship mp4 and the two farm-out graded
  PNGs — are **CAS'd with manifests, then DISCARDED from the worktree
  (`git checkout -- <paths>`), never committed**: committing them would
  write fresh multi-MB blobs into history one step before the rewrite that
  exists to remove exactly that class (an interaction the first draft
  missed).
  (b) **Modified tracked text** — the beats 01/04/14 VO jsons (both trees),
  ship-manifest.yaml, ep2_finish_grade.py, and
  **pipeline/measured/local-disk.yaml** (omitted from the first draft's
  list) — triaged on the ep2 finish-grade judgment: cold-read the CAS'd
  graded frames, then path-scoped-commit the text that stands or revert it.
  local-disk.yaml is a measured surface and gets its schedulers.yaml row in
  the same pass. This is a defect/finish judgment — steward's call, not
  taste.
  (c) **~267 untracked root files** — the CONTACT-*.png and
  LABELED-WAVE-*.png sheets, COMPARISON.html, EVIDENCE/DIAG files, the
  AUDITION wav, the stray `C:\banyan-queue/` directory, `.claude/`:
  evidence artifacts worth keeping are CAS'd (`cas_put` + manifest — they
  are exactly the class the CAS exists for) and then removed from the
  worktree; the stray directory is deleted (its host guard landed in
  step 1); `.claude/` stays as untracked local config. Verification:
  `git status --short` is EMPTY — a gate this step can now actually reach,
  because it addresses the tree that exists; qa_local PASS; proof_receipts
  intact on whichever ep2 cut stands.
- **Step 3 — enforcement layer.** `cas_gate` hooks (tracked `pipeline/hooks/`
  + installer + host_preflight's fail-closed presence check), the
  pre-commit path-scope hook, `cas_put`/`cas_get` with readback verify,
  `attest_after_readback` library + `manifest_schema_gate` in CI,
  `schedulers.yaml` + `stale_gate`, `bars_from_done_when` compiler with
  literal-clause refusal, `pipeline/instruments.yaml` + the
  falsification-record gate, `sample_before_batch` +
  `ledger/sample-verdicts.yaml`, playback-rate + near-dup clauses in
  qa_episode, verdict-key stripping in spec derivation. Verification: each
  lands with its own failing-then-passing test (test_pipeline.py grows);
  lint green.
- **Step 4 — the box powers on, hold-safe — BEFORE any force-push.** The
  one race in the whole sequence is named and closed here: the box wakes
  holding a stale 13-GB clone and a scheduled task that fires every 3
  minutes running hold-blind code. In order: (1) power on; (2) **the first
  human action at the desk is disabling the `banyan-box-autofill` scheduled
  task** (`schtasks /change /disable`) — before anything else; (3) deploy
  the hold-aware runner/autofill/enqueue code and run `install_hooks.sh` on
  the box's clone; (4) re-express the stop as `control/HOLD` on the box
  queue root, retiring the box-side prose marker into it; (5) re-enable the
  task and WATCH one tick refuse on HOLD — the gate is falsified like any
  instrument. Verification: a tick record reading `status: held`;
  `box_autofill.py --verify-deployed` clean; hooks present per
  host_preflight.
- **Step 5 — media migration (the founder's §5.5 media-split sign-off is
  its gate).** ONE SAMPLE FIRST: migrate one artifact end-to-end —
  `cas_put`, manifest, `cas_get`, sha256 round-trip — before the batch.
  Then Route A per §3.1: analyze → copy-out + manifests (verified by count
  + sha spot-checks) → strip → `git count-objects -vH` + full site build +
  `qa_local.py` PASS → force-push (branch protection handled per step 0;
  pages/mirror rebuild from the rewritten tree and must go green;
  queue-refresh is already HOLD-aware and repointed per step 1) → **fresh
  clones on every machine — the box included, whose task stays disabled
  until its fresh clone and hooks verify** → old→new SHA map recorded.
  Verification: pack size target met; site builds; and "cannot regress"
  now means something checkable — hooks verified installed on every machine
  by host_preflight's fail-closed check, with CI as the backstop — not
  hope.
- **Step 6 — queue v2 on the box (HOLD still on).** Land journal/sweep/
  DLQ/box-side dedupe/est_minutes scoring/max_runtime/reader hygiene/
  `repo_sha` pinning; deploy auto-logon + the at-boot `banyan-box-worker`
  task (§2.3). Verification: ONE canary job through the full path (enqueue
  → claim → journal STARTED → render → readback attest → DONE → courier to
  CAS); then TWO induced failures: kill the worker mid-job, restart,
  confirm INTERRUPTED journaled and attempts counted; and reboot the box,
  confirm the worker returns with no human login and host_preflight passes
  its launched-by-task check. The journal is falsified like any instrument.
- **Step 7 — observability (Casefile 08).** Gated on the founder's §5.4
  passes (the public status repo is a publication; healthchecks.io is an
  account creation) — until those, the dashboard builds and serves locally
  and the deadman waits. Then: banyan-status repo with per-machine
  branches, status files, dashboard build, healthchecks + ntfy with their
  URLs held as machine-local credentials (§3.4). Verification: kill one
  heartbeat on purpose; the deadman alert must fire and the page tile must
  go red client-side. A monitor that has never caught a planted fault is an
  unfalsified detector.
- **Step 8 — resume production, exactly where it held.** Unhold on the
  founder's word. First runnable jobs are the *named* held work, in
  dependency order: (a) judge the beat-17 gradmotion sample, then and only
  then release b04/b07/b14 behind it (mid one-sample-before-batch at the
  stop); (b) fix the goblin pose path first — inpaint_fruit.py all-white
  mask at strength 1.0 + the eight-line `--lora` arm (the named cheapest
  fix) — ONE sample, then the pre-authorised 15-beat wave (its verdict row
  in `ledger/sample-verdicts.yaml` is exactly what `sample_before_batch`
  will check); (c) train-jerry stays HELD until the min_bucket_reso
  1024/832 pair is fixed and a sample passes; (d) ladder-sapling-0822's
  eight cells wait on their one rung being looked at. No prompt-side face
  work, ever — route closed by canon (route_closure_2026_08_22): pixels
  from his pixels.
- **Step 9 — founder batch card.** One screening pass: §5 decisions still
  open, the two open taste cards, and the first v2-produced selection. ~One
  open question at a time thereafter.

---

## 7. What stays unchanged (the working parts of v1, by name)

- **episode-loop-v2.md itself** — Step 0 identity-first; per-beat PLATE
  batch → contact sheet → eye pick → ≤2 remakes; CLIP i2v 4–8 seeds →
  eye pick → ≤2 remakes; "two batch rounds fail the same way → restage the
  beat"; voices+captions in one stable pass; the 2026-08-21
  selection-of-finished-options amendment.
- **loop.md** — DIAGNOSE→FIX(≤3, pipeline-level only)→RE-RENDER($0)→SCREEN→
  LOG to cycle-NNN.md; provisional mode D19; blocking taste gates with
  summon-and-work-elsewhere.
- **Queue law from work-ladder-0819.md, verbatim:** consumer-named jobs; the
  card never idle while a runnable job exists; ONE SAMPLE per recipe change;
  pre-registered bars with FAIL modes named and all reported; one variable
  per rung, child specs derived programmatically; three rungs close a
  wording ladder; seed-wave promotion with stop-on-miss.
- **box_enqueue.py's eight guards** and their measured thresholds; the
  stage-then-move enqueue; `--backlog`; box_autofill's never-authors
  contract, EXPIRED/SUPERSEDED refusals, `_before/_after` reporting.
- **safe_commit.sh / safe_push.sh** as the commit/push path — now
  hook-enforced rather than opt-in (§2.1); path-scoped commits; "the ledger
  is GENERATED, never merged"; "the publish glob is DERIVED from --arm,
  never typed".
- **Verification tools:** qa_local.py (screening gate), qa_episode.py,
  proof_receipts, mac_preflight.py sha checks, lint_genome.py,
  test_pipeline.py.
- **Measured laws in canon.yaml:** crf-conditioning (never condition through
  crf 33; "33 is wrong" is established, "10 is right" is not),
  positive-placement, noun law, composite-first; the goblin standard as a
  module; route_closure_2026_08_22 (no prompt-side face work, ever); the
  gross-motion engine law as a canon input, with make-the-small-action-
  largest resumed as the open experiment it was ("UNDER TEST, NOT A
  RESULT").
- **The composite/i2img finishing route** (structure-keeping 12-of-40-steps
  finish; 0.45 for made objects, 0.30 for leaves; six objects + 44 dataset
  frames carried without a loss; bnysapling proves LoRA-from-composites) and
  the i2i-at-0.30-from-canon identity route (his eye survives to 0.40; face
  breaks 0.40–0.45), with ControlNet-skeleton round two next.
- **VO/captions/assembly:** Chatterbox 0.5B on MPS, measured chunk
  manifests, render_t3 muxing, vo-archive (R6) — "they are stable."
- **The 4-step ship-manifest swap protocol** (copy clip + meta, DELETE the
  outgoing NN-*.mp4, edit both manifest rows with the fault named,
  re-assemble + proof_receipts + `git add -f`).
- **The human perimeter:** founder-reserved list verbatim (spend, posting,
  credentials, taste-axis/trunk-graft, governance, money rails); §6 approval
  in the T0 leaf; the taste-vs-picks boundary as widened 2026-08-18.

*Provenance of this document: steward-drafted 2026-08-23 from the compiled
failure inventory, the as-built audit (episode-loop-v2.md, loop.md,
work-ladder-0819.md, box_enqueue/box_runner/box_autofill/farm-queue.yaml),
DECISIONS.md/STATE.md at the stop, and outside research (GitHub
LFS/Releases/Pages/Actions current docs, qmail maildir, CERN dirq, Postfix
spool, Brandur/Stripe idempotency keys, SQLite WAL durability docs,
litequeue/goqite, Buildkite/GitLab/Kubernetes/SQS retry semantics, Flamenco,
node_exporter textfile contract, Simon Willison's git-scraping,
healthchecks.io/ntfy.sh). Model-written; the decisions in §5 are the
founder's alone. Revised 2026-08-23 against an adversarial, disk-verified
critique — every finding addressed, logged below.*

---

## Revision log — post-critique

Each line: what the critique found → what this revision does about it.

1. `cas_gate` had no preventive form — zero hooks installed, git does not
   distribute hooks, and the claim that safe_push.sh "already wraps" one was
   false to disk → false claim deleted; repo-tracked `pipeline/hooks/` +
   `install_hooks.sh` sets `core.hooksPath`, host_preflight fails closed
   when hooks are absent, CI stays as detection backstop only (§2.1, §2.3).
2. Box power-on window unguarded, and §6's preamble contradicted its own
   step order (force-push before power-on) → sequence reordered: box on,
   task disabled as the first human action, hold-aware code + hooks
   deployed, one tick watched refusing — all before the force-push
   (§2.5, §6 step 4, §3.1).
3. One-sample-before-batch was left as prose — the doc's clearest
   self-contradiction with its own lessons-become-code law →
   `sample_before_batch` guard in box_enqueue (guard 9), mirrored box-side:
   a recipe fingerprint cannot batch without a founder-verdict row in
   `ledger/sample-verdicts.yaml` (§2.4, §4, §6 steps 3/8).
4. safe_commit/safe_push were opt-in and the shared-index TOCTOU class was
   claimed dead when it is not → pre-commit hook refuses non-path-scoped
   commits via the same tracked-hooks mechanism; §2.5 corrected to say
   residency alone does not kill that half of the class (§2.1, §2.5).
5. Deployed-code drift gates covered only 3 named files → every job spec
   pins `repo_sha`; the runner refuses work on clone mismatch before
   invoking any repo script (§3.2).
6. `attest_after_readback` was a bypassable library default →
   `manifest_schema_gate` in CI (lint_genome.py): manifest rows must carry
   `readback_sha256` + `readback_ts` or the build is red (§2.2, §3.3).
7. `no_hand_typed_verdicts` / `falsify_before_trust` had no enforcement
   points for runtime-authored specs and new detectors → the spec compiler
   refuses literal path clauses in any spec; `pipeline/instruments.yaml`
   registry + compiler refusal of verdict clauses from unfalsified
   instruments (§2.2, §2.4).
8. `host_preflight` was default-permit on undeclared memory — the canonical
   incident WAS an undeclared requirement → default-DENY: no declaration is
   a refusal, and declarations are sanity-checked against measured priors
   (§2.3).
9. Two human-awake dependencies were unnamed → named in §4 and §1:
   post-BSOD restart (mechanism: auto-logon + at-boot task; compliance:
   host_preflight's launched-by-task check; honest interim state stated)
   and judging_sentinel's WHO (steward cold-reads defect/pick at any hour;
   founder — Roman — takes taste-class, batched, machines never blocked)
   (§2.3, §3.3, §4).
10. banyan-status reintroduced multi-writer git state, and the deadman/ntfy
    URLs were unnamed secrets in a public repo → per-machine status
    branches; ping UUIDs + ntfy topic named as credentials, machine-local
    untracked config only, never in the status repo or workflows (§3.4).
11. Money check came back clean (no unflagged spend anywhere), but two
    founder-adjacent decisions were buried in a build step → surfaced to
    §5.4 with options + recommendation, explicitly undecided: the public
    banyan-status repo (a publication) and the healthchecks.io account
    (an account creation); §6 step 7 now gates on both.
12. Step 2 was unexecutable against the real tree (281 dirty paths vs 14
    named; local-disk.yaml omitted; "commit" would have written media blobs
    one step before the rewrite) → rewritten in three classes: tracked
    media CAS'd + discarded, never committed; tracked text triaged
    including local-disk.yaml; untracked evidence CAS'd then removed
    (§6 step 2).
13. Step 4's preconditions were unstated (git-filter-repo not installed;
    force-push feasibility unchecked; pages/mirror/queue-refresh behavior
    during the rewrite unaddressed) → step 0 verifies the install and the
    branch-protection state with a named lift-and-restore; workflow
    behavior on the force-push stated; queue-refresh repaired and repointed
    in step 1, before the rewrite (§3.1 step 0/6, §6 steps 0/1/5).
14. Step 1 referenced the stop marker as if repo-side — it exists box-side
    only → corrected everywhere: repo-side gate lands step 1, deploys to
    the box step 4 (§2.5, §6 step 1).
15. Verified-real strengths (journal at FULL before spawn, sweep, DLQ,
    box-side dedupe, reader hygiene, bars_from_done_when with its source
    file present, playback-rate, variable-reached-the-code,
    schedulers/stale_gate/deadman — ~17 of ~27 canonical incidents
    genuinely prevented) → kept unchanged; no revision needed, recorded
    here so the fixes above are read as sharpening, not rebuilding.
