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

## 2026-08-02 → 03 (overnight) — 720p works, and the slowness was VRAM paging

**Episode 1 is rendered at 704x1280, all 15 beats, zero slate.** Screening cut
`ep1-v22-hires.mp4` (untracked, repo root), 87.8s, every frame Wan 2.2
(Apache-2.0). No leaf written — canon is the founder's call. See
`MORNING-2026-08-03.md` and `pipeline/loop/cycle-015.md`.

**Standing facts this adds:**

- **`--offload` is mandatory, not optional.** Controlled pair, same beat/seed/
  steps: 462s at 480x832 without it, **240s at 704x1280 with it**. The 24.4/26GB
  residency was making the renderer page against itself. This is
  `enable_model_cpu_offload()` — NOT the hand-rolled text-encoder eviction, which
  corrupted every frame on 2026-08-02.
- **704x1280 is the render size from now on.** `render_t3` delivers 720x1280, so
  704 is near-native; 480x832 was a 1.5x upscale and that upscale is what the
  founder rejected as "too low quality". 720p had failed 5/5 times before
  offload.
- **Measured rate: 95.6s of compute per 1s of video** (median of 16 clips, 239s,
  range 232-242). One 88s episode ≈ 2.3h. A 24/7 month ≈ 7.5h of video. This
  SUPERSEDES the 208s/s figure quoted on 2026-08-02, which came from four
  no-offload clips.
- **Verified per-episode cost** against the founder's PixVerse pricing (30
  credits/5s, 15,000 credits/$60): ours ~$0.03 electricity, rented RTX 4090
  community ~$0.51, PixVerse $2.11. Rental $/hr figures are from our own
  2026-07-29 ledger rows ($0.19-0.22 community, $0.69 secure), not advertised
  rates.
- **`text=True` without `encoding=` is a Windows landmine.** The farm box decodes
  with cp1252 and our own queue file holds an em dash plus Wan's Chinese negative
  terms. Fixed at 23 call sites; `test_subprocess_reads_are_utf8` guards it. The
  platform that renders is not the platform that runs the tests.
- **Motion directions must be audited against the script's action line.** Four of
  fifteen contradicted their own approved still, including beat 2, whose "no
  typing" note was a direction asking for a glow. `motion.yaml` is now the first
  place to look when a beat does the wrong thing.
- **Sidecars carry `prompt` and `negative`** as of tonight (§7.2 named them all
  along).

**Open, founder-reserved:** D14 (does beat 4 show the fall — no engine ever has),
whether this cut becomes canon, and posting.

## 2026-08-03 — the picture was frozen because we told it to be

Full write-up: `pipeline/loop/cycle-016.md`. Standing facts this adds:

- **MEASURE MOTION AS MEDIAN + FROZEN-FRAME SHARE, never a mean.** A mean is
  dragged up by one jump and cannot tell animation from a still that cuts. The
  steward recommended a variant with 38% barely-moving frames on the strength of
  its mean, and re-rendered fifteen beats before the founder said "literally just
  frozen frames". Reference points: the rejected cut 0.13 median / 70% frozen;
  the approved F recipe 1.30 / 3%; hosted models 1.03-1.13 / 0%.
- **`"camera locked"` protects nothing in image-to-video.** The init frame locks
  the framing. Measured drift 0.00-0.02px without the phrase, against 4.83px on
  the clip the founder called "aggressively moving" — and the phrase costs real
  subject motion. Kept only on beats whose direction IS stillness (4, 6, 8).
- **You cannot pin the body and keep the animation.** none 3% frozen, positive
  wording 25%, negative 43%. Writing stillness into the POSITIVE does almost
  nothing; the negative is the lever, and here it is the wrong lever.
- **Direction register: name the amplitude.** "hammer", "drive hard", "whips
  back", "jolt", "slamming" — not "moves" or "fast". The founder's own call: "do
  this kinda thing. its very good."
- **A term added for picture quality can act on motion.** Three of the four
  suppressors found today were: our shake terms, Wan's inherited 静态/静止
  defaults, and "motion blur" (measured neutral, reverted). Read the whole
  negative before blaming the model.
- **The batch path exists and auto-enables at >=20GB VRAM with >1 beat** — and we
  have never used it, because every queued task names ONE beat. `beats: "1,2,3"`
  is supported. One batched task loads the model once instead of fifteen times:
  ~12 min per episode. Untested WITH offload; batching was unsafe before offload
  fixed the residency.
- **14 steps: 188s render, ~248s per beat end to end, 62 min for 15 beats.**
  20 steps is 240s/300s/75min. Measured, not estimated.
- **`--keep-text-encoder` is gone** — it was declared, plumbed and read nowhere.
- A test may enforce an invariant; it may not outvote a measurement. One asserting
  every direction contains "camera locked" had to be replaced, not satisfied.

**Open, founder-reserved:** D14 (beat 4's fall), D15 (every still is OpenRAIL++,
debt 38), whether 14 steps is the quality bar, and posting.

## 2026-08-04 — clips are watch-only, and the model/speed audit landed

**Posture change, Oleg, and it reframes every licence finding below** (verbatim):
*"when we publish clips they are for people to watch, not use for anything, so dont
create problems for scale."* Published media carries **no reuse grant — watch-only,
not CC BY 4.0**; pass-through objections are moot for media, while everything that
binds **us** (NC, territory, personal-use-only, revocable grants) is untouched. Not
yet in the licence files or `licence_gate.py` — recorded as DECISIONS.md 2026-08-04
item 0, and the D1 amendment it needs is the founder's.

Five briefs under `pipeline/research/`: `models-licence.md` (47KB, every clause
quoted from the primary document), `DECISION.md` (per-card recommendation),
`speed-quant.md`, `benchmarks.md`, `tooling.md`. Licence outcomes are recorded in
`DECISIONS.md` — **D16** (LTX-2.3 moves BLOCKED → **CANDIDATE** under watch-only,
gated on a per-post AI-generated label, a standing rule that LTX never powers a
contributor-facing render service, and one founder-screened sample) and the dated
2026-08-04 entry (Hunyuan territory extended to 1.5 and FramePack; the Turbo chain
closed and **watch-only does not unblock NC**; the output-use rule rescoped; the
OpenRAIL++ stills debt re-opened for review at ratchet 38). `vet_model.py` now
carries every link of that chain plus FramePack and the AniSora 5B line, and no
longer reads a vendored third-party LICENSE three directories down (BERT's, a Ditto
LoRA's) as a repo's own grant. Standing facts that change how we plan:

- **There are no Wan 2.5, 2.6 or 2.7 open weights.** The whole `Wan-AI` org was
  enumerated via the HF API: newest are the Wan 2.2 line plus `Wan-Dancer-14B`,
  `Wan2.2-Animate-14B`, `Wan2.2-S2V-14B`. Wan 2.5 shipped September 2025 as
  **API-only** and remains so; the 2.6/2.7 marketing sites correspond to no
  weights in the official org. Do not plan around a local Wan 2.5+.
- **Frozen frames is partly the model, and ours is mid-pack in the field.**
  TI2V-5B scores Dynamic Degree **52.85%** on VBench-I2V — about half its clips
  classify as not moving at all. Cycle 016's prompt fixes were real; this is the
  floor underneath them, and it is the field's dominant failure mode, not ours.
- **"13.4s per forward pass" was contaminated arithmetic.** It is 188/14, and the
  20-step run gives 240/20 = 12.0 — a per-pass cost cannot depend on how many
  passes you make. Solving the two: **8.67s marginal per step + ~67s fixed per
  clip**, i.e. 36% of wall clock is not denoising, most of it model load.
- **Per-beat: 248s → ~200s batched → ~160s with SageAttention.** The batch path
  is the fix for the fixed 67s and we already have it (`beats: "1,2,3"`,
  auto-enabled ≥20GB and >1 beat) — free, our own code, worth more than the
  wheel, and untested with `--offload`, so start at 2 beats. SageAttention 2.2.0
  sm_120 is ~35% CLAIMED by its author on an RTX 5090 Laptop 24GB, our exact
  card, and it pins torch to a nightly — separate venv only. 15 beats: 62 → ~40 min.
- **Card B (5070 Ti, 12GB) is a proof-pass machine, not a 704x1280 renderer.**
  Seconds-per-clip on it: no data, from anyone. Card A peaks at 22.9GB on this
  shape and activations dominate, so quantised weights do not rescue it. Give it
  T1/T2 stills, VO and 480x832 drafts. (LTX-2.3 fp8 at 12-16GB is the only
  candidate that would change this, and it is gated in D16.)

**Gemma second-licence audit: ship-safe** (LTX-2.3's required text encoder is
Gemma-3-12B, so the Gemma ToU + Google's PUP are in the chain of every LTX clip —
see the D16 addendum); the full model test set (**~115GB**: LTX-2.3 fp8 stack,
anisora V3.2, Wan A14B + Lightning LoRA) is downloading to the rtx5090 box at its
measured **9.8MB/s** ceiling; a **64GB RAM kit** (2x32 DDR5-5600 SODIMM) is ordered
by Oleg to unlock the A14B class.

**Open, founder-reserved:** the watch-only split (what the media licence says, and
the D1 amendment it needs), D15 + D13's re-opened licence debt at ratchet 38,
whether LTX-2.3 gets a sample beat, D14 (beat 4's fall), and posting.

## 2026-08-05 — the box has 68GB, and four records were wrong

Records day, not a render day. Nothing new was generated; five things that were
stale, mislabelled or simply lost got corrected against the sidecars, the jsonl
and the run logs.

- **The rtx5090 laptop's RAM landed.** Oleg's 2x32 DDR5-5600 SODIMM kit went in
  on 2026-08-04, box down ~15:52-16:39 local for the swap: **31.4 GB → 68.1 GB
  measured physical, 130.4 GB commit limit.** Same physical machine that
  bluescreened that morning on the AnimeGen load (bugcheck 0x3B, reboot
  11:30:33) — the crash and the upgrade are the same box, hours apart.
- **The A14B park's requeue condition is met on both limbs, and the task stays
  parked anyway.** Commit c004060 wrote it as "requeue only against a 64 GB
  host, or after someone has instrumented peak working set during load"; the
  upgrade satisfies the first and the 2026-08-04 bench satisfied the second.
  **The 64GB host turned out to be necessary, not sufficient.** On the upgraded
  box attempt 1 still died at step 0 (commit 140.6/140.6GB) and attempt 2
  succeeded *only* by evicting the text encoder into its own process, which
  freed 13.1GB. The queue path does not do that: `video_task.py:994` reads
  `big = gpu_vram_gb() >= 20` and routes a 26GB card straight into the
  single-process, text-encoder-resident branch. **So the parked AnimeGen task
  waits on code that does not exist yet, not on hardware.** Writing that branch
  is a recipe change and wants its own one sample.
- **An AnimeGen PRODUCTION clip existed on the box and we nearly lost it —
  recovered today.** `animegen-production-b1-s20260732.mp4` — 704x1280, 61f, the
  4-step LoRA recipe — finished at **23:30:14** on 2026-08-04: **545.5s sample,
  136.38s/step, 0.0047 s(video)/s(wall) = 214.6s per 1s of video**, 23.2GB peak
  of 25.7GB, 66.7GB host. The `scp` that pulled the night's artifacts ran about
  **four minutes before the run exited**, so neither the clip nor its sidecar
  came back with the rest of the session. Both are now in `SAMPLES/`, the
  MODEL-COMPARISON row is appended from the sidecar, and the clip has taken the
  AnimeGen slot in COMPARISON.html's hero row — **it is unscreened, and the
  verdict is Roman's (R4)**. First production-geometry cost for this model:
  ~3.7x the 5B's settled 57.6s per video-second, which is a taste question
  rather than a throughput one. **The lesson is the copy race, not the clip:** a
  pull scheduled against a wall-clock guess instead of against the producing
  process exiting silently returns a partial night, and looks exactly like a run
  that never happened.
- **The b4 data conflict is resolved: the jsonl was right.**
  `MODEL-COMPARISON.md`'s batch-4 row (99.3s/step, "projected ~0.014", 24.1GB /
  94%) was written at **23:20:37, five minutes before the run finished**, and
  tagged `MEASURED-BY-US` — a mid-run extrapolation promoted in violation of
  that file's own §3 rule 2. The sidecars and `animegen-bench.jsonl` had the
  measurement: **601.3s, 150.32s/step, 0.0091 s(video)/s(wall) = 109.3s per
  video-second, 23.2GB of 25.7GB = 90.3%.** Row corrected, with a dated
  correction note in the doc. The finding did not move — b4 is still a WDDM
  spill and still worse than b1 — the cliff is just steeper than the projection
  said. Also fixed there: b2 is **1.39x** b1's time, not 1.28x (124.6/89.6), and
  §2's claim that no Wan 5B row ever had host RAM measured, which its own T1 row
  and open observation 5 contradict.
- **`COMPARISON.html` provenance, since it is a local file nobody can date from
  the outside:** built 2026-08-05 00:16 local by `pipeline/build_comparison.py`,
  session 29be8750-ae1d-4233-9959-9a2186aa75f6, at Roman's request. Unapproved
  media under §6 — never in `_site/`, never committed, never deployed. It is
  regenerated, not edited: `python3 pipeline/build_comparison.py`.

**Why there was no batch coverage to compare against, and it was nobody's
dropped ball.** Oleg's directive to measure every model batched (17:59Z, restated
18:02Z on 2026-08-04) arrived *after* `ACTION-PLAN.md` was frozen and **13
minutes before** the detached 5B bench exited. It was never folded into the plan
and never re-queued — a directive that lands between a frozen plan and a running
job has no owner unless someone re-queues it by hand. Decision today:
`--batch` support is in the generator, and **three probes are authorised** — 5B
at b2, 5B at b4, LTX at b2 — so the batch-scaling section stops being one model
wide. `build_comparison.py` now reads `SAMPLES/batch-bench.jsonl` alongside the
AnimeGen file and renders one table per model label, so those rows need no code
change to appear; the hand-written reading prose stays attached to AnimeGen only,
because AnimeGen's cliff is the only one anyone has investigated.

**Open, founder-reserved:** everything still open from 2026-08-04, plus the
screening verdict on the recovered AnimeGen production clip (R4), and whether the
text-encoder-eviction branch is worth writing before the three batch probes run.

## 2026-08-05, the small hours — the batch probes: one answer, one bugcheck, one that could not start

The three probes authorised above ran, or tried to. The box is down at the end of
it and needs a human at the keyboard.

- **5B at batch 2: measured, and the answer is that batching this model loses.**
  704x1280, 61f, 14 steps, seeds 20260732-33: **764.7s sample, 54.62s/step,
  0.0066 s(video)/s(wall)** — 150.4s of wall per second of video, 382.3s per
  clip — **23.5GB peak of 25.7GB (91.4%)**, 54.4GB host. Against the b1 point of
  the identical recipe (T1-shift5.0: 12.05s/step, **0.0151**) that is **0.44x the
  throughput**. Not a plateau, a loss. **The fidelity gate passed decisively** —
  slot 0 differs from the b1 reference by less than re-encoding alone, and the
  two slots diverge from each other properly, so this measures batching and not a
  batch that quietly rendered one clip twice. The box's own preview rows say the
  same thing harder: **16.43 → 110.36 s/step** b1 → b2
  (`SAMPLES/ti2v5b-modes.jsonl`). AnimeGen's b2 was the optimum on this same
  card; the 5B's is a regression, and the difference is headroom — AnimeGen's
  second latent cost +1.8GB, the 5B's cost +9.1GB.
- **5B at batch 4: DNF — the run bugchecked the host.** **06:07:05 local**,
  Kernel-Power 41 / EventLog 6008, the box's **second unclean reboot that day**.
  It had done **2 of 14 steps at ~118-122s/step**; at death the GPU held
  **24102 MiB of 24463 (98.5%)** at 100% util while host commit sat pinned at its
  ~69GB ceiling and physical was being reclaimed 33 → 19GB — WDDM sysmem-fallback
  thrash, the same mechanism AnimeGen's b4 showed as a slowdown, escalated here
  into taking the machine. Telemetry: `probe-5b-b4.log`. **No sidecar, no clip,
  no row** — MODEL-COMPARISON rule 1 keeps unfinished runs out of the table, so
  it is recorded there as prose with the log named. **Standing decision: b4 is
  DEAD on this card. Do not re-run it. Reopening is founder-reserved** — the
  series is superlinear the whole way (12.05 → 54.62 → ~118 s/step) and the
  price of asking again is a bugcheck.
- **LTX at batch 2: never started — we had shipped a renderer that could not
  render.** Commit **fab4632** added the `--batch` body to `pipeline/ltx_i2v.py`
  and never declared the flag, so `batch = max(1, int(a.batch))` raised
  `AttributeError` on **every** `--stage render`, at the defaults, before a
  weight was loaded. A day of the LTX path being dead, and nothing here could
  have caught it: `py_compile` passes, `test_no_undefined_locals` passes (`a` is
  defined; the *attribute* is not), and no test had ever touched either
  renderer's CLI — which matters because the box those scripts run on is not this
  machine, so the first thing that executes them is an hour-long render nobody is
  sitting at. Fixed today, to parity with `wan_i2v.py`: the four flags declared,
  per-slot output naming, per-slot sidecars carrying mode/batch/slot/throughput,
  and an optional bench row. The gate is
  **`test_argparse_declares_every_flag_it_reads`** — AST-only, both renderers,
  and it was verified by running it against `git show fab4632:pipeline/ltx_i2v.py`
  first, where it names `a.batch` at line 401 and fails.
- **The farm worker is DOWN and cannot be restarted from here.** It has been down
  since the 06:07 crash. `schtasks /run /tn banyan-worker-start` returns
  **0x800710E0**: the task's LogonType is Interactive, and after an unattended
  reboot there is no interactive session for it to run in. This is pre-existing
  configuration, not damage from the crash — the same failure was already logged
  at 23:59 the night before. **A human has to log in at the box.**
  `banyan-telemetry` recovers by itself at logon; the worker does not.
- **Two smaller records corrected while in there.** `wan_i2v._scheduler_shift`
  read only `cfg.get("shift")`, but TI2V-5B ships `UniPCMultistepScheduler` whose
  key is **`flow_shift`** — measured at 5.0 in `bench-T1T2T3/bench-t0.json` —
  so every 5B bench row has been recording `"shift": null` while running at 5.0.
  It now reads `shift`, then `flow_shift`, else null. And `compute_per_video_s`
  was written by that same bench row as seconds per *clip* while the sidecar of
  the same run wrote seconds per *second of video*: 382.3 against 150.4 for the
  b2 run. The rows already on disk stand — they are measurements — the renderer
  now writes the form its column is named after, and `COMPARISON.html` derives
  that cell from `sample_s / video_s` so old and new rows read alike.
- **`COMPARISON.html` is hardened rather than re-styled.** Null bench fields used
  to render literal `None` and `NoneGB` cells, and the `ok` field was never read
  at all; both are fixed (gap = em-dash, a dead run renders struck-through and
  marked *did not finish*, and is excluded from the winner and the baseline). The
  batch tables grouped on the raw bench `label`, so last night's `ti2v-5b` rows
  never met the `ti2v5b` gallery group and the table titled itself with the raw
  string; a small alias map resolves both. The 5B production batch table now has
  its **b1 comparator**, joined from `bench-T1T2T3/bench-t1t2t3.jsonl`'s
  T1-shift5.0 — same recipe, same seed, run hours earlier — with the source named
  in the cell. **Joined, not synthesised: nothing was written back to any jsonl,
  and no DNF row was hand-written into one.** Cross-check that it is the same run:
  `ti2v5b-production-b1-s20260732.mp4` is byte-identical to `T1-shift5.0.mp4`,
  and its sidecar independently carries the two derived figures (0.0151, 66.3).

**Open, founder-reserved:** everything above, plus — *someone must log in at the
rtx5090 box* before any render is queued, and **b4 stays closed on this card.**

## 2026-08-05 ~03:00Z — the third probe ran: LTX at batch 2 pays, but the slot is not the same clip

The probe that could not start yesterday started. `probe-ltx-b2.log`, rc=0 at
06:51:40 box-local, no crash, no abort. Recipe read off
`SAMPLE-ltx23-b01.mp4.meta.yaml` and changed in exactly one place — `--batch 2`:
two-stage distilled (8 steps at 352x640, 2x latent upsample, 3 steps at
704x1280), distilled sigmas, 704x1280, 65 frames @24fps, guidance 1.0,
`--image-crf 33`, base seed 20260732 with slot *i* at seed+*i*. Same embeds file,
same prompt files, same conditioning still as the b1 sample — and the still is
provably the same input: `cond-crf.png` from last night's run and from this one
are **byte-identical** (sha256 `da388e7b…`), so nothing upstream of the denoiser
moved.

- **The measurement: 190.1s for two clips against 108.1s for one.** 1.76x the
  wall for 2.00x the video, so throughput goes **0.0251 → 0.0285 s(video)/s(wall)**
  and the cost of a second of finished video goes **39.9s → 35.1s, a 12% saving**.
  It is a win — the second batch configuration on this card that pays, after
  AnimeGen's b2 — but it is **1.14x, not the 1.33-1.54x that was predicted**, so
  the prediction was optimistic by better than half the margin. `s/step` is null
  and stays null: 8 half-res calls plus 3 full-res is not a uniform step, and
  throughput is the column that carries the comparison.
- **The GPU is not the constraint here; the host is.** Peak torch **7.2GB of
  25.7 (28%)**, device 2.6GB — where the 5B at b2 sat at 23.5 of 25.7 (91%) and
  the 5B at b4 took the machine. But host physical peaked at **64.2 of 68.1GB
  (94%)**, up from b1's 60.8, and commit at 75.3 of 123.9. b1 → b2 cost +3.4GB of
  physical; the same slope puts b4 past 68.1, which is the wall this box
  bugchecked at twice today. **LTX b3+ is not queued and b4 stays closed here
  too** — for the opposite reason to the 5B's, and the reason is worth keeping
  straight: the 5B dies on the card, LTX would die on the host.
- **THE FIDELITY GATE DID NOT PASS, and the row still stands.** Slot 0 shares the
  b1 sample's seed and recipe, so it should have been the same picture. It is
  not, quite. Against a control of the reference re-encoded one more generation
  (MSE 0.87, **48.7 dB**, rms 0.93/255), slot 0 vs the b1 reference measures MSE
  107.1, **27.8 dB**, rms **10.3/255** — 11x the control, where the gate allowed
  1.5x. What it is *not* is the silent-expansion failure this gate was written to
  catch: slot 1 vs slot 0 is MSE 705.2 (19.7 dB), the two clips are emphatically
  different, and the log shows the expansion happening
  (`embeds expanded to batch 2: (2, 1024, 188160)`). An independent seed against
  the reference sits at 720.4; slot 0 sits at 107.1, **6.7x closer**. So slot 0
  is the same sample drifted, not a different draw. The per-frame profile says
  the same thing twice: slot 0 vs reference starts at MSE 2.12 on frame 0 — the
  conditioning-pinned frame, control 0.54 — and climbs in steps to a 90-130
  plateau by frame 6, the identical shape slot 1 vs slot 0 traces up to 1100+.
  Divergence that starts at zero and grows with denoise depth is rounding
  amplified through eleven steps of bf16, not a changed input.
- **What that costs us, plainly: a batched slot is not a drop-in for the
  un-batched clip.** Batching buys 12% on throughput and gives up bit-identity,
  so it cannot be used to re-render an approved beat "identically, plus a spare".
  The clips are real — consecutive-frame MSE 80.7 for slot 0 and 44.8 for slot 1
  against the reference's 85.7, nothing frozen, and slot 1 is a visibly calmer
  take. **What is NOT established** is whether an *un-batched* re-run would drift
  from the stored reference by the same amount, i.e. whether this pipeline is
  reproducible run-to-run at b1 at all. That needs one more render at b1 and the
  probe was scoped to one run, so it was not taken. **It is the next question,
  and it is cheap** — 108s.
- **`COMPARISON.html` regenerated, and the LTX batch table has a wrong word in
  it.** Exit 0, 91KB, all video srcs resolve, no literal-None cells, five batch
  tables. The LTX table carries the single b2 row correctly, but its
  one-point boilerplate reads *"the cells are this recipe's cost at b1"* when the
  only row is b2. And it has **no b1 comparator**, though a real b1 exists:
  `BATCH_B1_JOIN` joins from a jsonl row, and LTX's b1 predates `--bench-jsonl`
  on that renderer — it survives only as a sidecar and a log. Both are small and
  neither was touched here; this probe's authority was one commit for this file.
- **The worker is UP.** `schtasks /run /tn banyan-worker-start` returned SUCCESS,
  not 0x800710E0 — status Running, last result 0x41301. The blocker was never the
  task, it was the missing interactive session, and there is one now: the
  telemetry daemon respawned at 06:39:09, which is the logon signature this file
  already records. **Someone logged in at the box between the 06:07 crash and
  06:44.** The worker took the one task on `pipeline/farm-queue.yaml` —
  `faceneg-b01-1785819600`, the deliberate one-beat face-negative sample — at
  06:55:29 and is rendering it. One sample, already sanctioned, left alone.

## 2026-08-05 ~04:00Z — the fp8 sample: the transformer sits on the card, and the host pays for it

ONE sample for ONE recipe change (fp8 layerwise cast + `--offload model`), run
host-exclusive with both farm-worker processes stopped. Ran clean at **rc=0 on
the first attempt** — the researched `--offload group` fallback was never needed.
Sources: `SAMPLES/batch-bench.jsonl` row `ltx23fp8`, the clip's sidecar,
`probe-ltx-fp8.log`, `fp8-fidelity-20260805.log`. Full write-up and the table row
in `pipeline/research/MODEL-COMPARISON.md`.

- **Recipe held to the reference byte-for-byte** — same embeds, same still, same
  prompt/negative files, `--image-crf 33`, seed 20260732, two-stage, guidance
  1.0, 65f @24fps. The only variables were the two new flags. Worth stating
  because the implementation report's suggested CLI had `--image-crf 0` (the flag
  default, not the reference's value); passing it would have fed a different
  conditioning still and made every frame differ for a reason unrelated to fp8.
- **Residency: CONFIRMED, and only an external measurement could confirm it.**
  The telemetry daemon's own trace (`C:\banyan-farm\telemetry.csv`, 10s cadence,
  external to the render process) shows **21346 MiB at 97% util** through stage 1
  and **22920 of 24463 MiB at 99% util** through stage 2, against ~2.5GB when the
  model is streamed. The run's own peak line says `device 2.6GB` — a post-run
  reading taken after the card drained, which quoted alone reads as "streamed"
  and is exactly wrong. **1543 MiB spare**, and that thin margin, not the host, is
  what makes b2 a real question.
- **Residency is per-stage, not across the run** — corrected on the verification
  pass. Between stage 1 and stage 2 the same trace drops to **362 MiB**:
  `enable_model_cpu_offload` returns the transformer to host RAM while the latent
  upsampler runs, exactly as the hook is documented to. An earlier draft of this
  entry said the card held "flat" through the whole denoise loop; it does not.
  The eviction is also part of why the host got worse, not better.
- **The cast is real and measured**: transformer storage **35.37 → 17.69 GiB** in
  139s; norms stayed bf16 via the model's own skip patterns.
- **Speed: 73.3s sample vs the bf16 b1's 108.1s = 1.47x**, throughput 0.0369 vs
  0.0251 s(video)/s(wall) — the fastest row on this box. **But the 139s cast is a
  new one-time cost**, so a single clip end-to-end is 224.3s against ~120s.
  **Break-even is exactly 4 clips in one process.** The 1.47x should never be
  quoted without that number beside it.
- **The host prediction was WRONG and is retracted here rather than dropped.**
  The change was expected to need ~34GB of host physical against bf16's 60.8GB.
  Measured **64.6GB phys / 97.0GB commit** — worse on both. The in-process cast
  retains the bf16 storages it replaces, the same mechanism the AnimeGen work
  already recorded. Size future fp8 runs against 97GB of commit, not against the
  17.69GiB the weights settle at.
- **Fidelity: a different clip, by about one batch-change.** Same-seed drift vs
  the bf16 b1 is **rms 11.93/255, PSNR 26.60 dB**, against controls of **0.93**
  (crf23 re-encode) and **1.74** (re-encode at the fp8 clip's own bitrate) — so
  ~13x the encode-noise floor, and slightly *above* what batch 2 cost (10.35).
  Frame 1 matches at the noise floor and divergence builds over ~4 frames then
  plateaus: quantisation accumulating through the denoise, not a different scene.
  **0/64 frozen frames** (consecutive-frame MSE min 5.06 vs the reference's 3.60
  — marginally more motion, not less). Colour cools slightly: R −2.54, G −2.81,
  B +0.12. Unlike the last fidelity check, this one left an artifact on disk.
- **`COMPARISON.html` regenerated**, exit 0, all srcs resolve, no literal-None
  cells. The fp8 clip is in the hero row as its own column and in the gallery
  under its own model card; the coverage matrix cell that read "sample pending"
  now carries the measured state. **The fp8 row now ranks first on throughput,
  which means the page's top row is a clip nobody has screened** — so a third
  correction was added under that table saying the top row is not a verdict.
- **The worker is back up.** Both processes had to be stopped with `taskkill /F`
  (a console worker with no window refuses a graceful kill; it was idle, last
  `DONE` at 06:59:53 local, GPU at 0 MiB, so nothing was lost).
  `schtasks /run /tn banyan-worker-start` returned SUCCESS; it is back in its
  normal parent-blocked-on-child pair and fetched the queue 33s after restart.
  The one-shot probe task was deleted after the run.
- **SCREENING IS OWED TO ROMAN.** Nothing above is a verdict — they are defect
  counts (R4, and §3 rule 5 of the comparison table). **No batch point above b1
  on this build may be scheduled until he has looked at the clip:**
  `SAMPLES/ltx23fp8-production-b1-s20260732.mp4`, best watched against
  `SAMPLES/ltx23-production-b1-s20260732.mp4` at the same seed.

## 2026-08-05 ~15:30Z — two boxes, one bit-identical re-run, and two probes that did not happen

A two-box afternoon. **One measurement landed, two did not**, and the two that
did not are recorded here at the same length as the one that did, because a
probe that never ran and a probe nobody mentions look identical six weeks later.
Evidence: `bench-platform/` (repro log, run-2 sidecar, sha256 proof, fleet
inventory). Table rows and the platform section: `pipeline/research/MODEL-COMPARISON.md`.

**The fleet is two boxes, and one of them was misnamed. There is no 4070**
(founder's correction — nothing in the repo ever claimed one, so this is a
record of the fact, not a fix to a file). The second box is the **MSI Vector 16
HX AI A2XWHG, RTX 5070 Ti Laptop, 12227 MiB**, and it is now **directly
reachable over the LAN** — it was a USB-bundle enrollment back on 2026-07-30 and
had no ssh route until today:

```
Host rtx5070            # added to ~/.ssh/config 2026-08-05, backup at ~/.ssh/config.bak.<epoch>
  HostName 192.168.3.153
  User olegm
  IdentityFile ~/.ssh/banyan-5070
  IdentitiesOnly yes
```

**Both boxes report `hostname` = `MSI`.** Identify them by GPU or by user
(`artvn` = 5090, `olegm` = 5070 Ti), never by hostname. Its checkout was
fast-forwarded 231 commits off the stale `farm-results-msi` branch to `main` @
`ae13cc6`; nothing was started on it.

### The measurement: an un-batched re-run is BIT-IDENTICAL, and its clock is not

Re-ran the LTX-2.3 bf16 b1 reference — same script, same venv, same embeds, same
still, same prompt/negative files, `--image-crf 33`, seed 20260732, the only
diff being `--out` and the provenance label. **sha256
`6226aef5…a880` both times, 352084 bytes both times.** The pipeline is
bit-deterministic through the h264 encode.

- **This closes the open question the batch-2 note left standing.** That note
  said the b2 slot-0 drift (rms 10.35/255) could not be attributed to batching
  because "whether two UN-batched runs reproduce each other has not been
  tested". It has now been tested and **the run-to-run noise floor is exactly
  zero**. So both drift figures on the books — **batch 2 at rms 10.35** and
  **fp8 at rms 11.93** — are attributable to their recipe change in full. No
  part of either is run-to-run wobble. Doctrine unchanged, and now founded:
  a batched or fp8 re-render of an approved beat is a NEW clip and needs
  screening again.
- **The clock did not reproduce, and that is the finding with teeth.**
  `sample_s` went **108.1s → 159.1s (+47%) for byte-identical output.** Where it
  went, per-step: stage 1's **first** step 24.55s → **62.88s** (cold weight
  stream under sequential offload — that step alone is the whole delta), stage 1
  steps 2-8 **5.35 → 5.59 s/it (+4.5%)**, stage 2 **10.54 → 10.32 s/it (−2.1%)**.
  Memory reproduced: 4.1GB torch both, 60.8 → 61.0GB phys, 67.1 → 68.8GB commit.
- **Consequence for how we quote speed: a cross-run `sample_s` delta under
  ~50s on this box is box state, not a recipe.** Steady-state s/step reproduces
  to within 5%; totals carry a fixed cold-start term that varies by 38s in the
  first denoise step alone. Recipe comparisons should be made on **per-step**
  figures, and any total quoted should say which run it came from.
- **The fp8 headline needs that correction applied, and survives it.** "1.47x"
  was 108.1/73.3 — two totals, both carrying the variable term; against
  today's re-run of the *same* bf16 recipe it would have read 2.17x. The gain
  is real on the per-step evidence, which is the part that reproduces:
  stage 2 **6.17 s/it fp8 vs 10.54/10.32 bf16 = 1.67-1.71x**, stage 1 steady
  **1.23 vs 5.35/5.59 s/it**. **The "break-even at exactly 4 clips" figure is
  withdrawn as over-precise**: 139s of cast against a per-clip saving of 34.8s
  (ref totals) → 4.0 clips, against 85.8s (re-run totals) → 1.6, against the
  denoise-only per-step arithmetic (93.0s → 39.5s) → **2.6**. Quote it as
  **~3 clips, range 2-4**.

### Did not happen 1: fp8 at batch 2 — nothing was run, nothing was staged

**SUPERSEDED the same afternoon — it ran at 15:52 and the card spilled. See the
2026-08-05 ~12:00Z entry at the end of this file.** True as written at 15:30.

No clip, no sidecar, no jsonl row, no log, no cmd file. Checked the box directly
rather than taking a report for it: the only files written to `C:\banyan-farm`
after 08:10 today are the repro directory and the telemetry daemon's own three.
GPU 0 MiB / 0% util, no render process, box up since 06:07:05 with no new
bugcheck. **The coverage gap therefore stands unchanged and for its original
reason** — `ltx23fp8` b1 has **not been screened**, and the standing rule is
that no batch point above b1 on a build may be scheduled before its b1 sample is
screened. b1 fits with **1543 of 24463 MiB spare**, and a second latent in the
same resident loop spends that margin on activations. It is a founder-gated
question, not a scheduling oversight.

### Did not happen 2: the 5070 Ti 5B-preview viability sample — battery

Staged and byte-verified in `C:\banyan-farm\probe-5070-ti2v5b\` (the conditioning
still, prompt and negative all sha256-match the 5090's; same model snapshot
`b8fff731`; torch 2.11.0+cu128, diffusers 0.39.0), one command from running. It
did not run and **should not have**: `PowerOnline=False`, charge **9.5% falling
to 8%**, and Windows' own task policy (`Stop On Battery Mode, No Start On
Batteries`) refused it. Three reasons to leave that policy alone — a 5-10 minute
100%-util render at 8% ends in a power-off mid-write, which is the same class of
event as yesterday's two unclean reboots; on battery the SM clock sits at
**442 MHz** with `power.limit` reporting `[N/A]` against a 140W part, so the
number would not be the box's throughput; and an OOM under a throttled clock is
not an OOM answer either. **The box needs a human to plug it in.**

What the afternoon did measure about it, over ssh:

- **31.4GB visible host RAM / 32GB installed** — this **corrects the 16GB**
  assumed in `pipeline/research/misc-candidates-source.md:58`. Commit limit
  **67.4GB** (36GB pagefile), **714.7GB** free on C:.
- **The card was never the only question, and the host is now the sharper
  one.** Derived, not measured: the 5B preview b1 row on the 5090 peaks at
  **80.6GB of commit** — above this box's **67.4GB** ceiling. Windows may grow
  the pagefile into 714GB of free disk or may not. On the card side the fit is
  plausible for a different reason than the raw row suggests: that row's 14.4GB
  torch peak is an **untiled VAE decode** (`bench_5b_modes.py` never calls
  `tile_vae`), while `pipeline/wan_i2v.py` does, which puts the ceiling at the
  largest single resident module (~11.4GB UMT5-XXL) against 11.94GiB of card.
  Sub-gigabyte margin, genuinely uncertain, still worth one sample.
- **Fleet verdict as of tonight: one proven video box, one unproven.** The 5070
  Ti stays a **stills / VO / 480x832-draft box** in every plan until that sample
  runs. It is not "confirmed too small" — nobody has measured it — and that
  distinction is the whole reason this entry exists.

### Housekeeping

Deleted `banyan-repro-ltx-b1` on the 5090: a One Time Only task, already fired
manually at 15:19, but still carrying **Next Run Time 2026-08-05 23:59**. Left
alone it would have re-rendered a clip nobody asked for, overnight, unattended —
a render with no consumer. Thirteen `banyan-*` tasks remain, all Ready, plus
`banyan-telemetry` Running.

## 2026-08-05 ~12:00Z — fp8 at batch 2 ran, and the card spilled instead of raising

The "did not happen 1" above is now closed: founder-sanctioned, the fp8 b2 probe
ran. **It does not fit, and it is not an OOM — the card pinned at 24112 of 24463
MiB (100% util) and spilled to host through the WDDM fallback rather than
raising.** Stage 1 at 352x640 cleared cleanly at two latents (~2.2 s/step against
b1's ~1.3 — 1.7x per step for 2x the output, a real gain); stage 2 at 704x1280
never completed a single one of its three steps, running past ~71s against the b1
reference's 8.37s for the same step. Killed at 15:56:36 rather than allowed to
converge, because that is the signature that bugchecked this host yesterday. The
host was never the wall: 65.4GB of 68.1 at weight load, 44.0GB while the card was
pinned. The one sanctioned fallback, `--offload group`, then died in 129s (rc=1)
for a reason that has nothing to do with memory or batch size — diffusers 0.39.0
onloads group-offloaded weights on `forward`, and the image conditioning goes
through `vae.encode`, so `prepare_latents` hands a CUDA tensor to a CPU VAE.
**`--offload group` is unavailable on this pipeline, not a fallback**;
`ltx_i2v.py`'s comment saying otherwise is corrected. No clip, no sidecar, no
jsonl row — nothing finished, so nothing entered the tables. `ltx23fp8` b1 is
**still unscreened** (R4). Evidence: `probe-ltx-fp8-b2.log`,
`probe-ltx-fp8-b2-group.log`, `probe-ltx-fp8-b2-trace.csv`.

**The farm worker had been down ~42 minutes and nobody had noticed.** It was
stopped for the 15:19 reproducibility render and never restarted — the agent that
ran that render died mid-task. Restarted 16:01:44 via `schtasks /run /tn
banyan-worker-start`; pids 7320 + 13076 are the documented parent+child pair, ONE
worker, and it fetched at 16:01:51. Nothing was lost — the queue had been empty
since the 06:59:53 `DONE`. **A stopped worker leaves no alarm anywhere**, which is
worth a watchdog the next time someone stops one to take the host exclusive.

## 2026-08-05 ~16:15Z — the 5070 Ti is on AC, and it is still clamped to 180 MHz

The founder plugged the box in, which was the one thing "did not happen 2" above
said it needed. **It was not enough, and the sample still has not been spent.**
`PowerOnline` is now True and the pack is charging, but the GPU is held near
idle, so a render would have measured the clamp instead of the card.

Measured over ssh with a 35-second bf16 matmul burn — $0, killed as soon as it
had answered:

| | idle | under 100% util |
|---|---|---|
| `enforced.power.limit` | **25.00 W** | **25.00 W** |
| SM clock | 0 MHz | **180 MHz** of a **3090 MHz** max |
| `power.draw` | 19.2 W | 13.4 W |
| temperature | 35 C | 36 C |

`clocks_event_reasons.sw_power_cap` is **Active** in both states, against a
**65 W default and 140 W maximum** board power. 180 MHz is about **6% of clock**.
Not thermal — the card never passed 36 C. The 5090 denoised this exact recipe in
58s at 9.68 s/step; the same six steps here, once weight load and the VAE decode
are counted, land somewhere around 25-45 minutes, past every abort gate the probe
was given and past the 10-minute ssh cap. **A number taken at 180 MHz is not this
box's throughput**, which is the same reason the 442 MHz reading on battery was
refused this morning. Plugging it in moved 442 MHz to 180 MHz — the wrong
direction, and the clearest evidence that battery *state* was never the whole
story.

The pack is **84 Wh** (`FullChargedCapacity` 84176 mWh), **4% at 16:00Z rising to
13% by 16:16Z**, `Discharging` False. The charge rate is low and falling rather
than rising: **39.8 W → 32.5 W → 20.2 W** (while the GPU burn ran) **→ 17.4 W**
(idle again). A nearly-flat 84 Wh pack on a healthy supply charges harder than
that.

**Two candidate causes, both needing a human at the machine, and they are
distinguishable by waiting.** One: the wrong charger. An MSI Vector 16 HX AI
driving a 140 W-capable 5070 Ti ships with a ~240 W barrel adapter, and every
symptom here — GPU pinned at 25 W, ~20-40 W into a flat pack, charge rate
*dropping* when the GPU draws — fits a ~65 W USB-C PD supply sharing one small
budget. Two: MSI Center's Silent/Eco shift mode, which clamps GPU TGP regardless
of AC and is not the Windows power scheme (that reads Balanced) and cannot be
read over ssh. If it is the charger, waiting will not help: the pack fills and
the GPU stays adapter-limited under load. If it is shift mode or a battery-percent
threshold, it clears on its own.

**Correction — `stage_simple` does NOT tile the VAE, and this inverts the fit
prediction.** Both the "did not happen 2" entry above and
`MODEL-COMPARISON.md` §4 argued the fit was plausible with a sub-gigabyte margin
because the 5090's 14.4GB torch peak is an untiled VAE decode in
`bench_5b_modes.py` "while `pipeline/wan_i2v.py` does" tile, putting the ceiling
at the largest resident module (~11.4GB UMT5-XXL) against 11.94GiB of card. The
file does tile — in the *other* two paths. `tile_vae()` appears exactly three
times in `pipeline/wan_i2v.py`: the definition at :176, the AnimeGen loader at
:328, and `stage_render` at :687. The 5B branch of `stage_simple` runs
`from_pretrained` → VRAM accounting → offload-or-`.to(cuda)` → `_sample`, and
neither `stage_simple` (:357-482) nor `_sample` (:483-657) calls it. **The staged
probe invokes `--stage simple`, so it will do an untiled float32 VAE decode of 61
frames at 704x1280 and should peak near the same 14.4GB — against 12.82GB decimal
of card. The margin is negative, not sub-gigabyte.** That is not "the box is too
small": it is that the staged probe tests the untiled path, and a VAE OOM there
has a one-line fix — call `tile_vae()` in `stage_simple`, which is the
configuration §4's own reasoning already assumed and the one an episode would
use. §4 says its prediction is "stated before the sample so the sample can
falsify it", so the probe stays exactly as staged rather than being quietly
re-cut.

A second recipe difference worth naming before any number is compared: the 5090
baseline ran **without** `--offload` and the probe runs **with** it
(`bench-5b-modes.log` is 31 lines and contains no "offload", "tiling" or
"slicing"; `stage_simple` prints "model cpu offload ON" when the flag is set).
Right call for a 12GB card, but it means the eventual ratio mixes silicon with
PCIe streaming and must not be quoted as a clean throughput factor.
`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` is also in the probe env and
buys nothing — the 5090 log carries "expandable_segments not supported on this
platform".

**Verified ready, so the run is one command once power is real:** staged
`wan_i2v.py` and `video_task.py` are byte-identical to repo HEAD
(`9DFD2B4F…`, `64B2A58E…`); the conditioning still is `004ECF2D…`, matching the
5090's; the model snapshot `b8fff731…` is complete at **31.85GB across 22 files
with zero `.incomplete`**, so nothing downloads mid-probe. Box left exactly as
found: repo clean at `ae13cc6`, no python processes, GPU 0 MiB, **no scheduled
tasks registered** (`register.cmd` was never run), probe directory back to its
nine staged files.

**Fleet verdict is unchanged and stays unchanged:** one proven video box, one
unproven. The 5070 Ti is still a stills / VO / 480x832-draft box in every plan.
It is not "too small" — the card side has still never been measured, and now the
reason is documented as *power delivery*, not memory.

### Correction, ~16:58Z — the clamp is the ON-AC state, and the AC is gone again

Two things in the entry above are wrong, and the Windows event log settles both.
`Get-WinEvent` for Kernel-Power **event 105 (power source change)** returns four
transitions in under two hours: **15:09:57, 15:19:21, 15:58:53 and 16:42:27**.
The 15:58:53 one is the founder plugging it in — it matches `PowerOnline=True` at
16:00Z. **The 16:42:27 one is the AC going away again**, and the box has been on
battery ever since: `PowerOnline=False`, `Charging=False`, `Discharging=True` at
10-23 W, **25% and falling**, 21545 mWh left of 84176.

So the "cap lifted at exactly 30% battery" reading was a coincidence of timing,
not a state-of-charge gate. `enforced.power.limit` went 25.00 W → 45.00 W at
16:42:54, which is **27 seconds after AC was lost**, and the battery's 30% peak
was simply where charging stopped. Corrected causal account, measured both ways:

| power source | `enforced.power.limit` | SM clock at ~99% util | measured throughput |
|---|---|---|---|
| **AC, charging a 4-30% pack** | 25.00 W | **180 MHz** of 3090 | not measured (clock ~6%) |
| **battery, ~28%** | 45.00 W | **802 MHz** of 3090 | **35.4 TFLOPS** bf16, 28.6 W drawn, 33 C |

**On AC the GPU was clamped HARDER than on battery** — the opposite of what the
morning's entry assumed when it treated 442 MHz on battery as the throttled case.
Both are far under the **65 W default / 140 W maximum**. 802 MHz is 26% of clock;
extrapolating the achieved TFLOPS to a normal ~2400 MHz sustained clock puts this
part near ~106 TFLOPS, so even the better of the two states is about a third of
the card. Neither number is this box's throughput and no row goes in §1.

**Retracted: the "wrong charger" and "MSI Eco shift mode" hypotheses above.**
Neither is needed to explain the readings and neither was measured — adapter
wattage is not exposed to software and MSI's shift mode is not readable over ssh.
What IS measured is that AC-while-charging clamps the GPU to 25 W. A modest
adapter sharing one budget with a ~40 W charging load remains the plausible
mechanism, but it stays labelled a guess. **What is not a guess: the mains
connection to this box has changed state four times in two hours and is currently
disconnected**, which is a loose plug, a failing adapter, or someone moving the
machine — and it is the actual blocker.

**Still nothing rendered, and the founder's one sample is still unspent.** The
right call twice over: the second burn measurement showed the battery drop 30% →
29% the moment the GPU was allowed to draw, so a multi-minute render would have
crossed the power-state boundary mid-sample and averaged two different machines
into one s/step — worse than no number, because it would look like a number. And
running a 100%-util render on a box that is now at 25% and discharging is exactly
what this morning's entry refused. The correct next step is unchanged and remains
a human one: **plug it back in and confirm it stays plugged in.** After that the
probe is one command, and the fit question — which does not care about clocks —
gets answered first.

Box left as found again: probe directory back to its nine staged files (both burn
scripts removed), no python processes, GPU 0 MiB at 0% util, no scheduled tasks
registered, repo clean at `ae13cc6`. Nothing is running and nothing is queued.
