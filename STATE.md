# State — the running log

Moved out of `CLAUDE.md` on 2026-07-25 so that the always-loaded session
context holds standing rules, not dated status. **Append here**, newest
block last, and keep `CLAUDE.md` to constraints that don't expire.

Standing constraints derived from this log live in `CLAUDE.md` under
"Current state". Open vs resolved decisions live in `DECISIONS.md`. Per-cycle
loop detail lives in `pipeline/loop/cycle-NNN.md`.

## Render routes (2026-07-19, verified — `pipeline/t3-trials/free-routes.md`)

Free path chosen: **Alibaba Model Studio (DashScope Singapore)** — wan2.7
API, native 9:16, watermark-off default, ~1,650 free video-seconds for new
accounts (90 days, no card; amount needs console confirmation). Adapter
live: `generate_shots.py --provider wan` (+`--quota-covered` ledger mode,
founder-attested, still behind `--yes`). Permanent $0 floor:
`pipeline/kaggle/render-kaggle.ipynb` (open Wan 1.3B on free Kaggle GPU).

**DONE 2026-07-20 (small hours):** THE WHOLE TRUNK IS FILMED AND LIVE.
001-t3-b (founder-released, v2 cut) + 002b/003b/004/005 t3-a leaves — all
anime, full-cast kokoro dialogue, manifest-synced captions, faststart,
$0 billed (~$21 list, all provider free quota, ledgered). Founder screened
every episode. Remaining wan quota ≈ 130s (wan2.1/2.2 mostly + scraps).
T3 v2 fitting: slots fit material, footage loops (never freezes), dialogue
never trimmed. Parser hardened twice (speaker-colon rule; headings require
timing ranges). Voice upgrade (emotional TTS — CosyVoice on same quota)
parked: founder said voice doesn't matter for now; dad wants human touch
eventually.

**SEASON COMPLETE (2026-07-22):** 7 trunk episodes filmed, voiced, live —
001→002b→003b→004→005→006a→007a. Trunk call 006a made by steward under
founder delegation (edl 07-22); 006b/007b alive per R6. 'Previously:'
recap cards on all episodes (comprehension wince). Free quota SPENT
(~$35 list, $0 billed, ledgered); next renders = Kaggle/paid/watering.
MAKING ERA CLOSED by design: no ep 8 until sap says so.

## The loop (2026-07-23, dad's directive — `pipeline/loop.md`)

Standing process: diagnose→fix-in-pipeline→re-render→founder screens→log
(`pipeline/loop/cycle-NNN.md`).

- **Cycle 001:** killed the silent 2.5s title-card open (title is an overlay
  now), added wind bed + 2-pass loudnorm to −14 LUFS, chunked 46px bold
  captions — KEPT.
- **Cycle 002:** measured caption sync + directed pauses (`synth_vo.py`) —
  founder saw no difference → engine was the ceiling.
- **Cycle 003:** **Chatterbox 0.5B local on MPS**, voice-cloned from the
  kokoro cast via `build_refs.py` (`~/.cache/banyan-tts/cb-refs/`), per-line
  emotion direction from script cues, ~3x realtime, $0 — founder:
  "improving for sure", rolled to eps 2-7. VO manifests now carry measured
  `lines[].chunks`; `render_t3` prefers them. Old VO takes in
  `clips/vo-archive/` (R6).

## Distribution (as of 2026-07-23)

Drops re-based to 1/day 21:00 (`distribution/schedule.md`); a launchd agent
`city.banyan.drop-reminder` (script `distribution/reminder/remind.sh`,
voiced by the tree) fires nightly, copies the caption to clipboard,
self-retires after the finale. Eps 1-3 posted (TikTok/Shorts/Reels,
AI-labeled). Reddit: post auto-removed on r/generativeAI (new account);
founder declined modmail; warming continues, retry ~+1wk; drafts in
`distribution/reddit-drafts.md` (project-first angle — founder: the PROJECT
is the hook, not the rough videos). X appeal pending, Vercel analytics
pending (founder), v0.3 verdict pending. Regrow-era top fix: character
consistency across episodes. Standing: warm new accounts 2-3 days before
posting links. Do NOT suggest multi-account quota cycling — declined on
ToS + provenance grounds, founder accepted.

## Snapshot (2026-07-19, night)

Launched 2026-07-18: node 001 flagship T3 leaf live (founder's manual
Veo/Flow clips beats 1/2/4; beats 3/5 are designed slates — prompts ready in
`.../001-capability-inventory/shots.md`). **16 nodes**, all with T0/T1/T2.
Tree tip is a live R4 fork, now one episode deep per side: **006a "The
Miracle Clause" → 007a "The Demo"** vs **006b "Reconciliation" → 007b "The
Hearth"** (issues #13–#16). `distribution/launch-kit.md` holds ready draft
copy. **Every trunk node (001, 002b, 003b, 004, 005) has a complete
shots.md** — 21 prompts; one funded D8 afternoon = a five-episode season.
Sap cron was silently failing 07-15→07-19 (unmatched screening.yaml
pathspec); fixed and verified green. Trials scored (objective axes only) at
`/trials/`. Open founder decisions: D8, D9, taste scores, watering rail.
**Style is v2: low-detail anime** (founder call 2026-07-19;
`genomes/sapling/style.md` is the visual bible) — all shot prompts
rewritten; 001's photoreal Veo clips are archived v1 evidence; D8 bake-off
should re-run on anime prompts. **T2 renderer is v2 + voice**: kinetic-text
cut (one shot per script element, Ken Burns, title cards) voiced end-to-end
by kokoro-82M local TTS — per-character cast in `genomes/sapling/voices.yaml`
(founder-amendable, R4), narrator for stage directions, wind bed, loudnorm;
~2-3min/episode, $0. Site leads node pages with Watch; homepage shows a
lineage-derived live-fork banner.

Superseded by later blocks above: the 006 trunk call (made 07-22) and the
"no social distribution yet" decision (distribution began 07-23).

## The molt (2026-07-25, night — cycle 007 executed)

Dad's verdict on 2026-07-25 — *"the video is not matching the audio at all,
or the script; it feels like a random video playing that isn't correlating"*
— was diagnosed as **shot starvation** and fixed at the script level.
`SCRIPT-SPEC.md` now governs T0 ("one beat = one shot", 3–6s, ≤2 spoken
lines, camera on the referent), and **all seven trunk nodes are molted**:
001, 002b, 003b, 004, 005, 006a, 007a. Measured: 35 shots → **166 shots**,
one cut every 19.2s → **5.8s**, 5.0 spoken lines per shot → **0.87**. No
dialogue was invented; the predecessor T0 leaf of each node is archived
whole and marked `superseded_by` (R6). Full numbers in
`pipeline/loop/cycle-007.md`.

Two canon defects fixed while rewriting: the tree's **size had never been
defined** in a series whose town is named Shade (now a growth ladder in
`style.md`, ~15cm at 001 → ~1.6m at the finale), and motion grammar was
implicit so prompts described tableaux. Every rewrite was gated by a
context-free cold reader before commit; transcripts in each node's `sap/`.
**Open and reserved to the author (R4): the protagonist has no name.**

What the molt costs, discovered after:

- **All 166 shots need footage.** Nothing carries forward.
- **Every VO track is stale.** VO is per-beat `NN-vo.mp3`; the existing
  files are numbered against the old 4–7 beat structure. Re-voicing the
  trunk is ~150 lines of local Chatterbox time.
- **Kaggle interactive sessions yield nothing.** The founder's first real
  run rendered a beat in a browser tab; the session died with the tab and
  `kernels output` 404s — there is no saved version to fetch, so that clip
  is gone. **Batch (`kernels push`) is the only mode that produces
  retrievable output.** `run_remote.py push <node> --steps N` drives it
  headless from this machine; the notebook now re-zips after every clip and
  logs per-shot minutes, so a 12-hour cap costs one clip, not the run.

In flight tonight: **001 queued on Kaggle batch at STEPS=25, 18 shots**
(status RUNNING, first genuinely headless render) and 001's VO being rebuilt
against the new script. Founder screening (R4) is the gate on whether the
picture now matches — it cannot be self-assessed.

Kaggle: token lives in `~/.kaggle/kaggle.json` (founder action). **The
access token pasted into the 2026-07-25 session transcript must be
rotated** — credentials in a transcript are burned.

## The renderer works (2026-07-26)

**A free renderer exists.** AnimateDiff on an SD1.5 checkpoint, on Kaggle's free
T4, produces a coherent on-genre shot in **~80 seconds** at $0. Beat 1 of 001
assembles end to end: captioned 9:16 episode, title overlay, voice in sync, all
twelve `qa_episode` checks green. Twenty beats is roughly half an hour of compute,
so the whole season is a few hours rather than a week.

Working configuration, every element of which cost a push to find:

- **AnimateDiff, not Wan 2.1.** Wan is trained in bf16 and no Kaggle free
  accelerator has bf16 (T4 is sm_75, P100 sm_60, bf16 starts at Ampere sm_80). In
  fp16 it decodes flat grey.
- **512x512, 16 frames** — the motion module's native size. `render_t3` does the
  9:16 framing, verified with real footage.
- **The checkpoint must be probed, not assumed.** `Counterfeit-V2.5` renders
  beautiful stills and produces NOTHING once the motion adapter is attached. The
  notebook now animates 8 frames per candidate and takes the first that yields a
  picture. `Lykon/dreamshaper-8` works; vanilla SD1.5 works (watercolour house
  style); Counterfeit does not.
- **Prompts are compressed for CLIP's 77 tokens** (`pipeline/sd_prompt.py`). All
  182 ran 113-145 tokens, so the model never saw the action. Order is **subject,
  then framing, then style** — whatever leads becomes the composition.
- **Negations move to the negative prompt.** "no buildings, no people" in a
  positive prompt asks *for* them.
- **`transformers` shims:** `FLAX_WEIGHTS_NAME` and `CLIPFeatureExtractor` no
  longer exist; diffusers 0.33 imports both. Checkpoints load with
  `feature_extractor=None`.
- **The checkout goes to `/kaggle/tmp`**, never `/kaggle/working` — Kaggle
  publishes the working dir as output and caps its file count, and a repo checkout
  there crowded the clips out entirely.

**The tree got bigger, by founder decision.** SD1.5 will not draw a 15 cm two-leaf
sprout as a character — five attempts gave abstract lineart, a leaf close-up, and
a lilypad, and negative-prompting "mature tree" made the trunk *thicker*. The
growth ladder in `style.md` now starts at ~60 cm and rises to 1.6 m, and the whole
genome's prompts and scripts were swept to match. The pathetic miniature scale was
a steward invention of 2026-07-25, not something the scripts required.

**Local rendering is off the table.** AnimateDiff on this M1 Pro measured 4-5
minutes *per denoising step* — ~1.5 h per clip, ~30 h per episode, and it made the
machine unusable. `render_local.py` refuses without an explicit flag. Kaggle's T4
is the right compute; Kaggle also remains the citizen-reproducible path.

**Pending before any episode is assembled:** the trunk needs re-voicing. Every
story decision of 2026-07-25/26 changed lines — 001's restored want, Jerry in
006a, the new beat in 005, the roots-west fix in 004, 002b's height — and
`retime_beats` now refuses when a take does not say what the script says. That is
a ~1 hour MPS job.

**Still unsolved:** character consistency across 166 shots. SD1.5 has no
reference-image conditioning; four recurring characters have to look like
themselves in every shot. Predicted by cycle-007, untouched by any prompt fix.

## 2026-07-27 — SDXL + SVD is the render stack, and two stale entries above

**The renderer changed.** SD1.5 was only ever in the pipeline because AnimateDiff
required an SD1.5 checkpoint; when AnimateDiff was dropped for being "cool looking
static", its dependency stayed and went unexamined for a cycle. Stage 1 is now
Animagine XL 3.1 (SDXL anime finetune) at 832×1216, stage 2 is Stable Video
Diffusion at 512×768, both on Kaggle's free T4. Measured: ~30 s per still, 4.3 min
per clip, **median frame-to-frame motion 11.3 where AnimateDiff measured 0.1–1.0
on the same beats.** Full diagnosis in `pipeline/loop/cycle-009.md`.

Five fixes went with it, four of them faults of mine that no metric caught:
`text` was being negated on beats whose subject *is* a screen; framing was a
trailing tag and therefore ignored (a "medium shot" of a man drew his chair);
Animagine's booster tags and its `abstract` negative were missing; provenance
logged the global negative rather than the per-beat one actually sent (§7.2); and
the §6 approval gate could not read an approval it had been given — it built its
leaf glob from the caller's argument string, so `push 001` passed and
`push 001-capability-inventory` reported "no T0 leaf found" for the same approved
node. It failed closed, but it now globs the node's own `leaves/` dir, and §6 has
a test for the first time.

**Correction to the entry above — the growth ladder was reverted by the founder.**
This log still says the ladder "now starts at ~60 cm and rises to 1.6 m". It does
not. The founder's answer was *"no, i prefered the sapling idea, lets revert"*, and
`style.md` is canonical: 001 is **~15 cm, two cotyledon leaves, no trunk**. The
sprout then rendered fine under SDXL, so the argument that the story had to change
to suit the renderer was wrong on the facts as well as out of my lane (R4).

**Correction — character consistency is no longer unsolved for want of a mechanism.**
That entry says "SD1.5 has no reference-image conditioning". SDXL does: IP-Adapter
is wired into the notebook, loaded before cpu-offload and only when a beat in the
run needs a reference. Scale 0.35 carries identity without hijacking the pose (0.6
does hijack it), and a reference transfers tone and background as well as face.
Jerry has a reference plate in `genomes/sapling/refs/`. Not yet proven across a
whole episode.

**Open, and a founder call (R4):** a *style plate* — one image that defines the
show's look, conditioned into every beat at ~0.3 — is the remaining answer to
"looks like fifteen unrelated AI images". It needs the founder to say which frame
*is* the show. That is taste, not stewardship.

**Still pending:** re-voicing the trunk (002b–007a) — every story decision of
2026-07-25/26 left those takes stale, and `retime_beats` now refuses when a take
does not say what the script says. ~1 h MPS job.

## 2026-07-27 evening — the founder took the wheel, and the look changed

**The visual language is new.** The founder reviewed ~10 iteration rounds live (dad's
directive: iterate in minutes, founder reviews everything) and killed the flat/
low-detail/pastel look — "i can barely make anything out of it". The approved
look is Animagine XL 3.1's native register: full cinematic detail, real light,
tag-dialect prompts. 001's shot list is rewritten in it. `style.md` is now STALE
(still describes the killed look); its v3 rewrite awaits the founder's word.
Cast locked: protagonist = glasses, messy hair, hoodie with hood DOWN.

**Stills approval state, episode 1:** beats 1/2/3/8/9/13 approved and committed
as canonical pixels in `nodes/001-*/stills/` — the notebook reuses a committed
still rather than redrawing, so approval binds pixels, not prompts. Beats
4/5/6/7/10/11/12/14/15 in round 4 (pick-of-4 seeds, kernel v46). Standing
lesson after three all-miss rounds: the model draws what anime is full of and
gambles on rare compositions — so story-critical graphics (10/15's sonar rings)
moved to deterministic POST overlays, and stubborn beats get seed-variants, not
rewording.

**Process now enforced in loop.md:** stills are the review unit; a beat earns
motion only after its still is approved; review gates BLOCK; the steward
summons the founder (push notification) and never proceeds past a gate because
the reviewer is slow. Batches run on Kaggle (STILLS_ONLY mode, SEEDS_PER_BEAT
dial) — never on the founder's Mac after the fan incident; local MPS is for
single frames only (still_local.py, fp32 — fp16 NaNs to black on this machine).

**CI incident:** lint-genome was red 15:39–18:10 across ~20 pushes (numpy import
CI lacks; estimate-vs-exact token counter divergence) and the founder found out
from his inbox. Fixed both, plus the habit: `gh run list` after every push, and
a CI-simulation venv holding exactly what the workflow installs.

## 2026-07-28 — the marketplace closed its first loops, and the prototype exists

**Stills: 11 of 15 canon** (founder votes via the public thread, both his
accounts). Cast locked: protagonist = candidate A (`refs/protagonist.png`),
delegated by the founder ("all valid"); the notebook conditions 1boy/glasses/
hoodie beats on him. Open ballots: 04 (cast-conditioned candidates), 06
(native `no humans` dialect after five failed English rounds), 07 (beat-8
vocabulary — the previous "round 3" accidentally re-rolled the old prompt,
founder caught it), 15 (deterministic proposal: beat 10's approved pixels +
closer rings).

**The request marketplace is live and proven** (dad's design): render-request
issues per beat, board banners, drag-a-file fulfillment, screening, intake
with provenance + compute-credit ledger rows. First three loops closed same
day by the founder himself (PixVerse daily credits, $0): beats 02, 08, 13.

**Motion:** POST (deterministic, post_motion.py) is the prototype's default by
founder decision. Paid takes exist as benchmarks (Hailuo $0.28 — authorized;
wan2.7 $0.40 — the unauthorized substitution, recorded in loop.md). PixVerse
free tier: generation free, watermark-free download paywalled. Veo free tier:
found already dead. Tencent: WeChat-locked. Self-hosted Wan 2.2 5B test on the
T4: in flight.

**PROTOTYPE-001.mp4 assembled** ($0): 15 beats, ~103s, 11 real + 4 slates,
QA 12 checks green. Bench render, founder screening pending.

**Money to date, total:** $0.68 estimated/ledgered ($0.28 authorized Hailuo +
$0.40 unauthorized wan). fal balance ~$9.72 in reserve, founder-named spends only.

**Self-hosted Wan 2.2 verdict (2026-07-28, four takes, all documented):** the
5B model loads and runs on the free T4 (12.7 min/clip, subprocess-isolated
diffusers ≥0.35, sequential offload) but outputs BLACK — the bf16-native
weights NaN in fp16, and the T4 has neither bf16 nor room for fp32. Free
self-hosted wan on Kaggle: **not viable.** The wan family stays reachable two
ways only: contributors' own fresh-account quotas (a suggested route on render
requests), and paid API at founder-named spend. The notebook's wan22 branch
stays as the documented experiment.

## 2026-07-29 — the day the machine grew hands

**Episode 1 remake: ALL 15 BEATS CANON.** Final rounds: 04-D (implied hand at
the keyboard, after wide-shot and violent-still directions both died in
votes), 06-B (one pale leaf in mostly-blue — 9 rounds, the episode's
stubbornest shot), 07-A (macro flail, differentiated from 08 per founder),
08-A (true-scale rebuild from 09's frame; old too-tall canon REVOKED and
archived). Screening cut assembled (~132s, new voice, audio-mux bug caught in
QA: VO lives in clips/, takes assembly must copy it beside the takes) and
delivered to the founder. D10 (loop vs split on 08/10/13/14) surfaces at
screening.

**RunPod lane: PROVEN.** 14 fires today. The heartbeat courier
(runpod_boot.sh) turned silent $0.22 corpses into named bugs at ~$0.01 each:
unpinned diffusers needed torch>=2.5 (pin to 0.29.2 era), stale results
branch fooled the watcher (clear before fire), community 3090 pool had broken
drivers (CUDA preflight + poisoned-rung auto-climb), community supply flaky
(--secure flag: SECURE 4090 = instant match, ~$0.03/round). Delivered rounds
for beats 04, 06 (×4), 07. Day's total RunPod spend ~$0.25; balance $9.55±.

**The farm was born.** farm_worker.py = universal heartbeat worker (cuda/mps,
§6 gate, farm-queue.yaml on main, results on farm-results-<name>) — doubles
as the future contributor compute daemon (D11/D12). MSI Vector 16 HX (RTX
5070 Ti 12GB) enrollment: USB bundle (git bundle beats exFAT ._ pollution;
model-cache carried to skip the 7GB pull), dedicated deploy key (id
158682502, revocable alone), setup doc pipeline/farm-setup-windows.md
(founder-requested: generalize to farm-join.md after onboarding, USB
choreography moves out of the repo). Onboarding stalled at torch WinError
1114 → VC++ redist upgraded → retry pending. Roster: MSI = primary once
lit; Dan's M1 16GB = overnight tier (needs his yes); Olivia's M1 8GB =
benched; this Mac = voice/assembly/orchestration.

**Marketplace:** founder fulfilled beats 05 + 11 via PixVerse (requests
19/23 closed, artovonmago compute credits ×2 — five fulfillments lifetime).

**Fixed in pipeline:** post_motion sidecars wrote illegal YAML (unquoted
colons) — writer quoted, 14 files healed.

## 2026-07-30 (night shift) — the honest bake-off and the reference library

**Model bake-off, invalidated then redone:** the first "4-model" bake-off
compared Animagine 3.1 with itself — the msi worker ran stale code that
ignored the model dial (md5 proof: identical checksums). Canary-verified
worker update, then the REAL runs: Animagine 4.0, Illustrious XL, NoobAI XL
on beats 1/6/9, same seeds, checksums distinct. Gallery:
banyan-drops/model-bakeoff.html. NoobAI ran handicapped (v-pred model,
eps sampler) — flagged in the gallery, not judged. FOUNDER VERDICT PENDING.

**World-reference library:** 36 anchors committed to nodes/001.../refs/
(growth ladder 40/90cm, field noon/night/rain/dusk, wider roots) — $0,
farm-rendered. img2img raw material for future consistency.

**Worker hardening (night's lessons):** task-id filename prefix for
model tasks (collisions ate two rounds), canary-verification after code
pushes (self-update can't bootstrap itself onto pre-update workers),
md5 distinctness checks in any A/B. M2/M3-Pro measured for dad's decision:
122s full / 62s working / 37s floor per image; ANE dead end (2x slower);
decision card + extensive 3-tier 15-beat gallery in banyan-drops.

**Fleet:** msi 13.5 s/img · m3pro(m2) 125 s · m1pro 178 s · RunPod reserve
$9.55. Total project cash still ~$1.20.

## 2026-07-30 — the grove at night (site redesign, commit b3e18b1)

Dad flagged the episode page: "UX of this page is complete garbage." Ultracode
run: 4 stranger-eyes audits → 4 Opus implementers (one per page family,
exclusive file ownership) → 3 adversarial verifiers before push.

- **One design system** (`pipeline/site_theme.py`): serif story / mono
  receipts / sap-amber CTAs / forest-dark + grain; light mode kept; zero
  external assets. All builders import it.
- **Watch = walk the tree** (Roman's directive: "really redesign, think of
  some new thing"): every episode ends on its scripted cliffhanger question,
  the real branches are doors, growing tips invite "write what happens next."
  Stateless trail URLs at `watch/<slug>.html`; straight-line binge kept at
  `watch/season.html`.
- **Banyan City = the place, Sapling = the series** (Roman's correction) —
  chrome de-conflated everywhere.
- Episode pages: one player, receipts one fold down. Shot board eager weight
  49 MB → ~0.4 MB. Status speaks plain English. Lab: base64 → `lab/img/`
  (69 tracked JPEGs), money figures reconciled to the ledger ($1.24 total).
- Link gate now sweeps all 69 published pages (href/src/poster) and fails the
  build loudly. The verifier caught untracked `site_theme.py` + `lab/img/`
  before CI could die on a clean checkout — that check earned its cost.

Founder-facing: the stranger-review found product-level gaps that are NOT
steward calls: audience thread separate from ballot threads, one public word
for scene/shot/beat, episode-status wording ("final" vs "working cut").
Logged for the next founder session.

## 2026-08-01 — licence gate: 46 violations found, 25 fixed, 21 open (D13)

`pipeline/licence_gate.py` ran fully for the first time. Every violation was
pre-existing; almost all were in node 001. The tree publishes **CC BY 4.0**,
which grants commercial reuse, so a non-commercial input inside an episode
makes our own licence a false statement — the argument does not depend on
anyone enforcing it.

**Fixed (records, not standards):**

- 15 Kaggle/SVD takes → `clips/footage-archive/` (R6). Non-commercial research
  licence; all were orphans (no leaf referenced them), left in the live
  assembly dir when cycle 012 moved assembly to `takes/clips/`.
- `post_motion.py` was writing sidecars to `NN-slug.meta.yaml` instead of
  `NN-slug.POST.meta.yaml` — `.with_suffix("").with_suffix(...)` strips both
  suffixes. 15 clips read as unprovenanced while 15 orphan sidecars sat beside
  them, each claiming to describe a different take. Cause fixed, 15 renamed.
- 006b's 4 VO manifests: engine backfilled from `voices.yaml` (kokoro-82M,
  Apache-2.0), corroborated by mp3 mtimes predating Chatterbox. Audio untouched.

**The live hole, closed.** `build_site.py` published `takes/clips/` with a bare
`iterdir()` and no licence check — that is how `13-i-always-left.PIXVERSE.mp4`
became a downloadable file on banyan.city while D8 had already recorded
PixVerse's free tier as personal-use-only. `publishable()` now asks the gate
and withholds **deny and unknown** (unread terms are not a licence to publish);
the board renders an honest withheld card + `WITHHELD.md` instead of a dead
player. 10 clips withheld, sidecars still shipped, link check green over 69
pages.

**Open, founder call (D13):** beats 2, 4, 8, 11, 13 of the LIVE episode are
PixVerse free-tier — re-render queued on Wan 2.2 (Apache-2.0, $0), or swap to
the `.POST.mp4` alternates that already exist for all five, or record a paid
plan if one was used. Flow (6) and LTXV (2) need their terms actually read.

**Ratchet, deliberately.** `pages.yml` runs lint before `build_site`, so hard-
failing 21 pre-existing violations would have stopped banyan.city deploying
overnight rather than reddening a badge. Debt is advisory; the COUNT is
asserted at `LICENCE_DEBT = 21`. A new violation fails lint and tests
immediately (verified by probe). Number may only fall.
`LICENCE_GATE_STRICT=1` = everything fatal, the founder's switch.

Renders: 5090 re-rendering 8 motion beats at **704x1280 / 50 steps** — the only
size Wan 2.2 TI2V-5B supports, against the 480x832 / 20 steps every previously
judged clip used. Five PixVerse beats queued behind it, then the A14B prefetch
(download only).

## 2026-08-01 — the death was a nine-second hole (cycle 014)

The founder's note "his death is very anticlimatic" survived four rounds of work
on the thump because **the thump was never the problem** — at 14s it is the
loudest moment in the episode, louder than any dialogue.

**Beat 4 runs 10.08s where the script gives it 5** (`THE FALL — 0:15–0:20`): two
full-length 5.04s shots concatenated, carrying no VO at all. RMS decays -28 →
-46 dB across it while dialogue sits at -13. That silent double-length beat IS
the anticlimax, it is in every cut ever screened (v11 6.5s, v13 6.2s, v17 7.5s,
v18 9.5s), and the -17 LUFS re-master shipped as the fix for this very note made
it 2s longer and 5 dB deeper.

`qa_episode.quiet_hole()` now measures the longest stretch far below the
episode's OWN 90th-percentile speech level — relative, because an absolute floor
cannot express "far below the speech around it". `silencedetect` thresholds on
peaks and returned green for three cycles.

Three options built and measured SEPARATELY (14-25s mean / hole):
baseline -35.0 / 9.5s · beat-4 trim -27.2 / gone · + fan up + black beat 5
-24.9 / gone. **The trim alone is the fix** and is not a taste call. On the
founder's desk: `ep1-v19-BASELINE / -B4TRIM / -FULL.mp4`,
`DEATH-before-after.png`, `death-fix-sound.patch`. Nothing committed to the cut.

Also: **beat 5, scripted "Black, and the sound of a cooling fan spinning down",
is a 4-second copy of the bright sky** (luma 135.8 vs 136.2). Cycle 013
attributes that choice to the founder; his traceable words object to the beat
showing the TERMINAL. A paraphrase became an attributed decision and node.md was
never updated. Flagged, not reverted — R4.

Voice: `pipeline/synth_voxcpm.py` maps the script's own parentheticals ("VO
(tired, flat)") to VoxCPM2's per-line style prompt — the first engine we have
that takes direction rather than dials. Apache-2.0, commercial use explicit,
licence read BEFORE the work this time. Wants CUDA, so it belongs on the 5090.
`--dry-run` reviews every line's direction with no model or GPU.

**VoxCPM2 verified working on THIS Mac (MPS), 2026-08-01 ~23:00Z** — the model
card asks for CUDA >= 12 but it auto-adjusts bfloat16 -> float32 for mps and
runs at 48 kHz, ~1.4x realtime (4.96s of audio in 7s, 26s model load). No 5090
needed for voice. Venv: `~/banyan-tts-venvs/vox` (python 3.11, torch 2.13.0).

The control that matters: same sentence, no direction 6.40s / "(exhausted, flat,
low energy, speaking slowly at 3am)" 6.72s / "(bright, quick, genuinely
delighted)" **4.80s**. The direction changes delivery, and it is NOT spoken aloud
— the direction text would add 3-4s if recited, and directed is +0.32s over
plain. VoxCPM-0.5B DID recite it; VoxCPM2 does not. Different behaviour, same
family — do not carry the 0.5B lesson across.

Samples on the founder's desk: `voice-voxcpm2/` (3 of episode 1's own lines, A/B
vs Chatterbox, + the 3-way control) with `LISTEN.md`. Caveats recorded there:
voxcpm2 runs LONGER than the current voice on all three lines (6.72 vs 4.38,
4.32 vs 3.13, 2.08 vs 1.36), so adopting it means re-timing the cut; and these
are voice-DESIGN samples with no reference clip, so the character is invented
rather than matched. Cloning + direction together is the next step and the code
supports it.

## 2026-08-01 01:15Z — TWO workers were sharing the 5090 all night

The failed 704x1280 batch was not mis-sized. Two `farm_worker.py` processes were
running on the 5090, started 21 minutes apart, both polling the same queue and
both claiming the same tasks. Heartbeat evidence: `2x STARTED
task=vid-720p-all-1785529520`, two `PREFETCH_START`s, and two separate timeouts
firing at 14430s and 14404s against the 14400s limit — each process ran the same
8-clip batch to its own timeout.

Throughput proves the contention: single beats rendered in ~13 min each
(18:23-19:03), the same work under contention took ~26. Eight clips at 13 min is
under two hours — comfortably inside the 4h cap. It only overran because it ran
at half speed. Both processes also `git push -qf` the same branch from the same
working tree, so results can erase each other, which is likely why zero clips ever
landed even before the timeouts.

Fixed with an O_CREAT|O_EXCL lock outside the repo (farm-out is committed and
force-pushed, so a lock inside would be shipped and clobbered by the race it
guards). No automatic staleness takeover — two workers racing to judge staleness
is the same bug again; the refusal message tells a human what to do and `--force`
clears a stale lock. The self-restart path releases before spawning the child, or
every code update would deadlock the worker against its own lock. Deploys itself:
both workers restart on the push, first child takes the lock, second stands down.

**Expect one console window on the 5090 reading "another worker already holds this
machine" — that is the fix working.**

Also this session: CC BY sound credits were never published anywhere ("Gravity
Sound" appeared nowhere in _site; SOURCES.md is not copied to the site). Node
pages now render a Sound credits section from the node's own SOURCES.md, and
POSTING-KIT.md step 0 carries the caption line — the site fix does nothing for a
TikTok post. licence_gate is narrow here by design: it answers "does this licence
permit use" and has no notion of permission granted IN EXCHANGE for something, so
CC BY passes as `allow` and nothing checks the exchange happened.
