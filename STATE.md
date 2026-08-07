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

## 2026-08-05 evening — the 5070 Ti rendered for 28 minutes, and it was the adapter all along

**The power saga is over and the answer was the cable.** The founder plugged in the
correct barrel adapter; nothing else changed. `enforced.power.limit` went
**25.00 W → 140.00 W**, a bf16 burn held **2385 MHz at 139.93 W**, and through the
render the card sat at **2775 MHz, 100% util, `sw_power_cap` Not Active** while
charging the pack **6% → 32%** — one supply carrying a flat battery and a full-power
GPU at once, which is exactly what the old one could not do. So the "modest adapter
sharing one budget" mechanism that this file retracted a few hours earlier as
unmeasured is **confirmed by intervention**. Two caveats kept on the record: it is a
single intervention, and reseating the plug is confounded with swapping it. The
lesson is about the retraction, not the hypothesis — "unmeasured" was the right
label, "retracted" was not, and downgrading a well-supported inference because ssh
could not prove it cost an afternoon of waiting for the wrong thing.

**The sample finally ran, and the lead stopped it during step 4 of 6.** Fired 19:00:43,
the staged recipe unchanged (TI2V-5B preview, 704x1280, 61f, 6 steps, g5.0, seed
20260732, `--offload`, inputs sha256-identical to Box A's). Loaded in 74s, then:

    step 1  362 s      step 2  601 s      step 3  719 s      (Box A: 16.4 s/step)

Those are differences of tqdm's *cumulative* elapsed; its smoothed rate understates
every step after the first. **Settled steps only — no clip, no completed sample, so
no `s(video)/s(wall)` number exists for this box, and none should be quoted.** Three
rising steps do not extrapolate honestly to six.

Not the clamp this time: full clock throughout, 43-55 W of 140 W, 48-52 C, device
memory pinned flat at **11908/12227 MiB (97.4%)**, commit ~59.5 GB against **31.4 GB
installed**. The structural finding is solid — UMT5-XXL alone is ~11.4 GB bf16
against 11.94 GiB usable, so **this box can never hold Wan 5B resident the way Box A
does**; offload and its PCIe cost are mandatory here. Why each step costs more than
the last is deliberately left unexplained: host physical use fell 27.9 → 13.7 GB and
then flattened with ~17.5 GB free, which fits "the safetensors file cache was
released after load" as well as anything paging, and no page-fault rate was sampled.
A measured curve with no mechanism attached is the honest artifact.

> **Superseded 2026-08-06 — the curve does have a mechanism, and it is on the device,
> not the host.** The caution above is about *host* memory and stays correct; the
> spill is on the *card*. 11908/12227 MiB pinned flat at 100% util and full clock for
> 31 minutes while identical steps cost monotonically more is a working set being
> moved, not computed. So these are **paging figures, not throughput figures**, the
> binding constraint is the **denoise**, and the s/step ratio must never be published
> as this box's speed. Full reasoning and its limits:
> `pipeline/research/MODEL-COMPARISON.md` §4.

**It did not crash, and the missing rc line is what proves it.** `probe-5070.cmd`
runs python and *then* echoes `==== probe-5070 exited rc=%ERRORLEVEL% ====` into the
log. A python-side failure — a CUDA OOM, a host OOM, any exception — leaves the
parent `cmd` alive to write that line. **There is no rc line at all**, so the whole
process tree went down together, which rules out a crash in the renderer and points
squarely at the scheduler stopping the task. The log also ends with no traceback and
no CUDA error, while the trace's next sample shows GPU util and memory at **0** and
commit collapsing **61.0 → 16.16 GB** — alive at 19:34:44, gone by 19:35:24. For 31
minutes GPU, host RAM and commit were all steady, so this is the opposite of the two
bugchecks above.

> **Corrected 2026-08-06 — the lead killed it; the scheduler had nothing to do with
> it.** This entry originally continued "the box was being unplugged to be carried to
> another room, and `schtasks` defaults include stopping a task on the switch to
> battery", flagged unconfirmed. Wrong. **The lead terminated the run at ~19:34
> local**, three settled steps being enough to show the recipe was paging rather than
> rendering. `Stop On Battery Mode` never applied — AC held for the entire 34-minute
> run. The missing rc line still rules out a renderer crash; it just no longer points
> anywhere in particular beyond "killed from outside", which is what it was.
>
> One conflict left open rather than papered over: the lead's account is that **no
> scheduled tasks were registered**, while the housekeeping note further down this
> entry records **two left registered**. Both cannot be true and the box is offline,
> so **verify the registration state before re-firing anything on it** — a stale
> registration would launch the recipe now ruled out.

**Both headline questions are still open, and I am not going to pretend otherwise.**
The run never reached the VAE decode, so §4's "does the untiled decode OOM on 12 GB"
prediction is neither confirmed nor falsified, and with no clip there is no
cross-platform determinism figure. `bench-platform/xplat_fidelity.py` was promoted to
`pipeline/xplat_fidelity.py` ready for it and re-validated (it still reproduces the
recorded CTRL-crf23 0.8714/0.933 and XPLAT 142.3771/11.932 exactly).

Two real fixes came out of the attempt anyway. `tile_vae()` now runs on
`stage_simple`'s 5B path — the divergence §4 found by reading the source, where the
AnimeGen loader and `stage_render` tiled and the untested path did not. **Unverified
on hardware**, and its comment says so. And promoting the fidelity harness into
`pipeline/` put it under `test_subprocess_reads_are_utf8`, which immediately caught a
latent bug the untracked copy had hidden: `sh()` ran `text=True` with no `encoding=`,
which on these Windows boxes decodes as cp1252 and silently sets `.stdout` to `None`.

**Provenance defect found, not fixed (outside that task's scope):**
`video_task.write_sidecar` writes `platform: local-gpu ({worker})` from
`platform.node()`, which is **"MSI" on both boxes** — so a clip from the 5070 cannot
be told from a 5090 clip by its own sidecar, in direct conflict with §4's rule to
identify a box by GPU and never by hostname. Worth fixing before Box B produces any
artifact anyone keeps.

**Box NOT left clean — it went offline mid-cleanup and this is outstanding.** Two
scheduled tasks remain registered (`banyan-probe5070`, `banyan-probe5070-trace`); the
trace loop self-terminates after 90 samples so it is not running, but the
registrations are still there. The re-fire is one command once the box is back
(`cmd /c C:\banyan-farm\probe-5070-ti2v5b\register.cmd`), and the tiled renderer is
already staged beside it as `wan_i2v_tiled.py`, hash-verified — rename it over
`wan_i2v.py` first and the next run tests the tiled path.

**`~/.ssh/config`'s `rtx5070` block is now stale, and not because of the box.** This
Mac re-addressed from **192.168.3.x to 192.168.70.x** during the same window — Oleg's
iPhone shows up on the new subnet under the MAC it had on the old one, so the LAN
itself changed, not just the laptop. `HostName 192.168.3.153` cannot resolve to the
box from here regardless of whether it is awake. To re-find it: sweep the current
subnet and match its Wi-Fi MAC **9C:67:D6:85:0A:B6**
(`arp -a | grep -i 9c:67:d6:85`), then update the `HostName` line. As of this entry
it is not on 192.168.70.x at all — nine real ARP entries, none of them the box —
which is what a laptop closed for a room move looks like. Nothing here is evidence
about the box's health.

## 2026-08-06 — reconciling the 5070 Ti record: a paging measurement, a ruled-out recipe, and an option nobody scheduled

No machine work today — the box is **offline and unavailable again** (stale
`192.168.3.153`, absent from the re-addressed `192.168.70.x` subnet). This entry
closes out records left partly written when yesterday's run ended, and corrects three
claims in the entry above rather than restating what it got right. The corrections are
inline there and the full reasoning is in `pipeline/research/MODEL-COMPARISON.md` §4;
what follows is only the part that changes decisions.

**What the 28-minute 5070 Ti run actually measured.** Not throughput. The card sat at
**11908/12227 MiB (97.4%)** pinned flat, 100% util, 2775 MHz, full clock, for 31
unbroken minutes while identical denoise steps cost **362 → 601 → 719 s** — rising
monotonically. Constant work whose cost grows at constant clock and constant occupancy
is a working set being moved, not computed. The binding constraint is the **denoise**,
which was already full before step 1 finished; the run never reached the VAE decode at
all. Against Box A's 16.43 s/step that is **22x, 37x, 44x and still climbing** — which
is a description of a recipe that does not fit, not a speed. **The s/step ratio from
this run must never be published as this box's speed.**

**Two things this therefore did NOT settle**, both of which the record now says
plainly: §4's untiled-VAE-decode OOM prediction is **UNTESTED, not falsified** (the run
stopped four steps short of the decode), and the `tile_vae()` fix — which **is** landed
at `pipeline/wan_i2v.py:462` in `84f54b9` and is a real bug fix on its own terms — had
its premise untouched. Tiling lowers the *decode* peak; nothing here was decode-bound.
A re-run with tiling would spill in exactly the same place.

**Fleet consequences.**

- **RULED OUT — TI2V-5B at 704x1280 on the 5070 Ti.** Not slow, not unmeasured: not
  viable, with no offload/step/scheduler setting that recovers it. Do not queue or
  re-benchmark it.
- **UNCHANGED — the 5070 Ti's proven role is stills, VO and drafts.** Third
  independent route to the same verdict, now on measured rather than cautious grounds.
- **RECORDED AS AN OPTION, NOT SCHEDULED — a smaller 5B recipe** (480x832, fewer
  frames). It changes the working set that spilled, so this run says nothing about it.
  It is a **new recipe**, therefore a ONE-SAMPLE question for the founder before it is
  anything else, and it has **no named consumer** — two independent reasons it is not
  on any queue. It is written down so it is not lost, not so it gets run.
- **Before anything re-fires on that box**, resolve the scheduled-task registration
  conflict noted in the entry above — a stale registration would launch the recipe
  just ruled out.

**Also corrected today, in `MODEL-COMPARISON.md` §1** (unrelated to the 5070, found
while reconciling): the six Box A rows an interrupted edit had left uncommitted are now
in, having been checked cell-by-cell against `SAMPLES/*.jsonl`. Two defects were caught
in them. The baked-fp8 AnimeGen row compared its 73.3GB commit against **128.7GB**, a
*load*-path peak, where the matched render figure is **119.1GB** — both are now quoted
with their scope. And the LTX-2.3 preview row claimed "the best throughput of any model
measured", which the fp8 resident build (0.0369) beats; worse, that row's `94.3s`,
`1.9/1.5GB` and `60.5/68.9GB` cells have **no archived source anywhere in this repo** —
no sidecar timing, no jsonl row, no log. The clip and its recipe are real and
`ffprobe`-verified (352x640, 65f @24fps, 2.708s), so the row is kept with those four
cells labelled **UNARCHIVED** rather than deleted or quietly trusted. Re-run it to
archive a sourced row before anything downstream cites them.

## 2026-08-06 evening — the founder's eye beat the metric: LTX-2.3 loses 86-89% of its colour, and our own table had the number

**Roman screened the LTX samples today and the verdict is two verdicts.** On the
fp8 cast, **cleared on look**: *"barely a difference"*. On the colour, a defect
report: both LTX clips *"turn black and white ... an unnecessary colour
transition"*. The second one is why everything below happened.

**The diagnosis, measured, $0, read-only on this Mac** — 38 clips through one code
path; full artefacts in `bench-platform/colour-drift-20260806.log` and
`bench-platform/colour-postfix-mkl-20260806.log`, written up per that file's own
rules in `pipeline/research/MODEL-COMPARISON.md` (new dated 2026-08-06 section):

- **LTX-2.3-Distilled loses 86-89% of its chroma over each clip.** bf16 b1: mean
  CIELAB chroma **Cab 28.07 at frame 0 → 3.78 at frame 64, −86.5%**. **58% gone by
  frame 6** (0.25 s), **90% by frame 18** (0.75 s), then a flat plateau for the
  remaining ~2 s. It is not only desaturation: **a\* +17.46 → −2.17** and **b\*
  −20.18 → +1.95** cross zero, so blue-violet inverts to faint green, **L\* rises
  +36%**, and the channels converge on R (**G +108%, B −32.5%**). By the last frame
  **79% of pixels are visually neutral** — that is exactly the black-and-white
  Roman saw.
- **LTX-2.3 ONLY. Our pipeline is exonerated.** Same beat, same still, same writer,
  same export path: Wan-5B **+1.8 to +4.3%**, AnimeGen flat, AnimateDiff flat, and
  the **July LTX-Video 0.9 renders of this same still flat too**. Frame 0 of every
  clip is within **±3.2%** of the conditioning still, so nothing is lost at
  VAE round-trip, encode or mux. **The defect arrived with the 2.3 distilled
  checkpoint**, not with "LTX" and not with us.
- **Four causes eliminated, three without spending a sample.** fp8 is not it —
  bf16 −86.5% vs fp8 −89.4%, **under 0.5 JND apart**, so *the founder's "barely a
  difference" is numerically exact* (and the reason they agree is that both are
  dead). Batching is not it. Container tagging is not it — all 38 clips are
  identically h264/yuv420p with every colour tag `unknown`. And **stage 2 plus the
  latent upsampler are exonerated** by the stage-1-only clip collapsing
  identically, which **refutes `adain_factor`** — the one lever we had been holding
  a sample for — **without rendering anything**. `conditioning_mask` is already
  hardcoded at 1.0.
- **Upstream had it first:** Lightricks/LTX-2 issue **#37**, *"green artifacts +
  near-total grayscale output"* on RTX 5090 — **open, no fix** — plus issue #148,
  and Lightricks' guidance that 2.3 washes out far from its **960x544x121**
  training bucket. We render 704x1280x65 and 352x640.
- **SECOND DEFECT, de-confounded.** LTX-2.3 motion is **quantised to 3-frame
  steps**: lag-3 autocorrelation **0.79 / 0.77 / 0.82** for the three LTX clips
  against **1.02 / 1.05 / 0.95-1.29** for 5B, AnimeGen and AnimateDiff **through
  the identical writer**. So the 65-frame 24 fps clip carries **~22 distinct motion
  states — an effective 8 fps**. `MODEL-COMPARISON.md` had blamed the encode; that
  is now **refuted** (an encoder cannot do this to one model's clips and not
  another's). **The mechanism is OPEN and is not being guessed at** — LTX-2's
  documented 8x temporal VAE predicts period-8, not period-3.

**The one sample: it did not complete, so there is no colour verdict.** Launched
18:42:47 as scheduled task `banyan-colour-bucket`, one variable moved — geometry
**352x640x65 → 544x960x121**, LTX-2.3's own bucket transposed to 9:16 — with the
script hash matched both sides and the conditioning round-trip bit-identical to
the 2026-08-04 controls. The **rtx5090 left the LAN at ~18:56, mid-denoise at step
4 of 8**: ICMP silent, an ARP sweep of the /24 found its MAC nowhere, WoL to three
addresses did nothing, our gateway answered throughout. **Not a gate trip** — at
last contact host phys was 44.90 of 63.42 GiB and *falling*, VRAM 12.4%, s/step
*improving*. **No clip, so no R and no colour verdict.** The task has no time
trigger, so a reboot does not re-fire it; the re-run is one command,
`Start-ScheduledTask -TaskName 'banyan-colour-bucket'`.

**What the dead run did give us is a real and expensive number: the first
on-bucket throughput datapoint.** Four steps timed — 196 / 138 / 136 / 138 s —
so **137.3 s/step at 544x960x121** against the control's **7.75 s/step at
352x640x65**. Latent tokens ratio 4.12x, measured time ratio **17.7x** (tokens² =
17.0x). **LTX-2.3 stage 1 is attention-bound at this size: going on-bucket is an
~18x per-step cost, not 4x.** Projected ~22 min/clip, so a 15-beat episode is
**≈5.5 GPU-hours** under sequential offload. That is a planning fact whichever way
the colour verdict lands.

**Candidacy: SUSPENDED.** `DECISIONS.md` D16 gate (c) was *"one sample beat,
founder-screened"* — it fired, and it fired negative. LTX-2.3 moves **CANDIDATE →
CANDIDACY SUSPENDED**, pending Roman's screening of the on-bucket sample, recorded
in a D16 addendum and on all five LTX rows in `MODEL-COMPARISON.md` §1. **The
licence analysis is untouched and is not the reason.** Those five rows' time,
s/step, throughput and VRAM cells are now also marked **OFF-BUCKET —
PROVISIONALLY NON-COMPARABLE**, because every one was measured at a geometry we
will not ship if the on-bucket recipe passes.

**A free fallback exists and is NOT the fix.** MKL colour transport of every frame
onto frame 0 holds **Cab 27.94-28.20 across all 65 frames** (against 28.07 → 3.78
untreated) and undoes the hue inversion, at $0 and no GPU. It is cosmetic: it
forces one palette on the whole clip, **cannot invent chroma detail the model did
not generate**, and amplifies chroma noise. Recorded as an available fallback
only — **shipping it is a look change, therefore R4**, and it is not scheduled.

**The process lesson, and it is not a near-miss.** **Saturation 0.264 was already
in our own table**, in an LTX row whose same cell said **"Clip clean: no issue-#37
corruption"**, sitting one row away from AnimeGen's **0.636** on the same beat and
the same still. A **2.4x deficit** was measured, written down, published to
`COMPARISON.html`, and read past for two days — through two separate correction
passes on neighbouring cells. **Nobody escalated it. The founder watching the clip
did.** The standing rule is *"a metric agreeing with me is not a sample"*; today
supplies its converse, which is the more expensive half: **a metric disagreeing
with its own label is not noise.** The row now states the measured collapse
instead of "clean", the fp8 row's `R −2.54, G −2.81, B +0.12` is labelled
**BETWEEN-clip** so it stops reading as within-clip reassurance next to an 86%
collapse, and the screening page shows the retention figure on the LTX cards
rather than leaving it in a research file.

**Also withdrawn today:** the standing recommendation to put the **LTX single-stage
352x640 preview recipe on the 5070 Ti**. It is the **hardest-collapsing recipe we
have measured** (**R = 0.1369**) at the geometry furthest from LTX-2.3's bucket —
it would have spent the fleet's only unproven box proving a broken recipe is also
small. The 5070 Ti's role is unchanged: stills, VO, drafts.

**Still open.** (1) The on-bucket sample — one command, blocked only on the box
being reachable. (2) The period-3 mechanism. (3) `pipeline/ltx_i2v.py`'s module
docstring still calls LTX a D16 CANDIDATE; that file is carrying unrelated
uncommitted work, so the line is left for whoever lands that change. (4) Nothing in
this repo writes colr/bt709 tags on any clip — real hygiene, not this defect,
worth zero chroma.

## 2026-08-06, later — the founder cleared what he flagged: LTX's suspension is LIFTED, the blocker is INTEGRATION, and node 002b's one sample did not render

**This block supersedes the "Candidacy: SUSPENDED" paragraph of the block above.**
That paragraph was true when written and is not true now — same day, same founder,
a second screening with the measurements in hand. Nothing in it is deleted; it is
the first half of the story and this is the second.

**The three verdicts, R4, 2026-08-06.** Shown the LTX clips again alongside the
colour numbers, Roman cleared all three of the things the block above had recorded
as defects:

- **fp8 vs bf16 — "barely a difference".** (This one was already recorded above;
  it is repeated here because it is now one of three, not a lone exception.)
- **The within-clip chroma collapse — "fine".** The measurement is unchanged and
  stays on every page it is on: **86%, Cab 28.07 → 3.78** on the bf16 b1, 89.4% on
  the fp8. He was shown that figure and accepted it.
- **The 3-frame motion cadence / effective 8 fps — "fine".** Also unchanged as a
  measurement: lag-3 autocorrelation 0.79/0.77/0.82, ~22 distinct motion states in
  a 65-frame 24 fps clip.

**A verdict does not move a measurement.** Every number above stays exactly where
it is written, in `MODEL-COMPARISON.md` §1, in the colour section, and on the
comparison page's clip cards. What changed is their *status*: they are now
described properties of a renderer the founder has cleared **on look**, not open
objections. And "cleared on look" is the whole of it — he has approved how it
looks, not decided we ship it.

**Consequence: LTX-2.3 is a CANDIDATE again.** `DECISIONS.md` D16 gate (c) —
*"one sample beat, founder-screened"* — has now been through both halves of a
screening and comes out **cleared**. The suspension recorded earlier today in D16's
addendum, on all five LTX rows in `MODEL-COMPARISON.md` §1, and on `COMPARISON.html`
is **LIFTED**, superseded in place in each of those files rather than edited away.
The licence analysis was never the reason and is still untouched. The **OFF-BUCKET
— PROVISIONALLY NON-COMPARABLE** markers are a separate matter and **stay**: they
are about geometry, not taste, and only an on-bucket measurement removes them.

**What actually blocks LTX now is integration, and it is measured, not estimated
(2026-08-06).** This is the finding most likely to be re-litigated, so it is stated
with its numbers:

- **Nothing wires LTX into the render queue.** `pipeline/video_task.py` hardcodes
  the Wan path in both places it launches a renderer — **`:1015`** (the batch
  branch) and **`:1082`** (the per-beat branch), both `REPO / "pipeline" /
  "wan_i2v.py"`. LTX has no queue path at all; it is hand-run via
  `pipeline/ltx_i2v.py` with a separate `--stage encode` pass.
- **Wired in naively, LTX is SLOWER per episode than the incumbent it beats per
  clip.** One process per beat — the shape the queue would actually give it —
  costs **≈78 min for a 15-beat episode against the 5B's ≈42**. The per-clip win
  is real and it does not survive contact with the queue, because every beat
  re-pays a **88s Gemma load**, the transformer load, and a **139s fp8 cast**.
- **A jobs-loop fixes it: ≈25 min.** Load once, render all fifteen — the same
  structure `wan_i2v.py` already has and `ltx_i2v.py` does not. **That work is not
  done and nobody is doing it.**

So the honest state is: **screened and cleared on look; adoption still needs the
jobs-loop.** Anyone proposing to switch renderers should cost the integration
first, and anyone proposing to re-open the colour question should read the
clearance above before spending a sample on it.

**Node 002b, "The First Citizen" — the one sample DID NOT RUN today.** Recording
this plainly because a comparison page full of LTX and 5B clips reads as though it
had:

- **No beat-01 clip for node 002b exists anywhere in this repo.** The render agent
  failed before producing either the Wan2.2-TI2V-5B or the LTX-2.3+fp8 version.
  Disk check 2026-08-06: the newest file in `SAMPLES/` is from 2026-08-05 18:15,
  and **every LTX and 5B clip on `COMPARISON.html` is the 2026-08-04/05 bench beat,
  not node 002b.** The staging got as far as the conditioning still, the prompt and
  negative files and a jobs JSON; the rtx5090 was unreachable for the whole window
  (44 poll iterations, all `down`).
- **The permission side is clear — what is missing is the render, not the
  approval.** 002b's **t0-c** cut is founder-approved:
  `genomes/sapling/nodes/002b-first-citizen/leaves/002b-t0-c.yaml:17-18`,
  `approved_by: founder`, `approved_on: 2026-08-03`. STEWARDSHIP §6 permits the
  footage. 002b is the only node in the tree with an approved script and zero
  media.
- **When it runs it is ONE beat and only one.** Beat 01 is the beat both of the
  founder's approval conditions were spent on — *the fig must GROW on screen, not
  already hang* — so it is the beat that proves the fix. **The other 20 beats of
  `shots.md` (21 total, Beat 01 → Beat 21) wait on the founder's look at beat 01**,
  per the one-sample rule. Not fifteen, not twenty-one.
- **002b's existing media is DEAD and must not be reused or cited.** The two T3
  leaves (`002b-t3-a.mp4` 2026-07-22, `002b-t3-b.mp4` 2026-07-24) and the **18 VO
  takes** in `clips/*-vo.mp3` all predate t0-c and come from the **superseded t0-b
  cut**. They are not footage for this node's approved script. Re-voice from t0-c
  when the time comes.
- **Where the clips will land.** Drop the two mp4s and their `*.mp4.meta.yaml`
  sidecars into `SAMPLES/` and `COMPARISON.html` picks them up with **no code
  change** — `build_comparison.py`'s `CLIP_GLOBS` already globs `SAMPLES/*.mp4`.
  Until then the page carries the absence explicitly, as the first entry of
  §4 "Still no sample, and why", rather than letting the bench clips imply it.

## 2026-08-06, night — 002b beat 01 is THE job: eight candidate stills exist, the fig is in none of them, and one founder pick is the gate

The entry above says the one sample "did not run" — that was true of the *clip*.
Since then the box came back and the sample ran one tier lower, as **stills**, per
STILLS BEFORE MOTION (dad, 2026-07-27). Eight of them exist. **None is approved and
none is fit to condition a video on yet**; the founder's look at them is now the
single thing gating episode 2.

**The active production job is node 002b beat 01 — one frame, not twenty-one.**

- **Permission is settled, only the picture is missing.** The t0-c cut is
  founder-approved:
  `genomes/sapling/nodes/002b-first-citizen/leaves/002b-t0-c.yaml:17-18` —
  `approved_by: founder`, `approved_on: 2026-08-03`. STEWARDSHIP §6 is satisfied for
  media on this node. The approval's own `approval_scope` says it covers the STORY,
  not the shot prompts, and that beat 01 is converted to the current native-tag
  dialect as **the one sample** — beats 02-21 stay unconverted and unrendered until
  he has looked at this frame. That is where they still are.
- **002b's existing media is DEAD.** Restating it because it is the most re-usable
  looking thing in the node: the two T3 leaves (`002b-t3-a.mp4` 2026-07-22,
  `002b-t3-b.mp4` 2026-07-24) and the **18 `*-vo.mp3` takes in `clips/`** (counted,
  18) are all from the superseded **t0-b** cut. They are not footage or voice for the
  approved script. Do not reuse them, do not cite them as progress; re-voice from
  t0-c when the time comes.

**What was rendered, and on what.** All eight on the **rtx5090** (`artvn@.157`) with
**animagine-xl-3.1** — not cached there, 9m39s to pull, 18 files — at 832x1216, 40
steps, cfg 7.5, bf16, matching `farm_worker.render_task`. Seeds
20260720 / 20261720 / 20262720 / 20263720 (`20260719 + beat + k*1000`), the same
four in both rounds, so the only variable between rounds is the prompt. ~9-11s per
image, rc=0 both rounds. The farm worker was **not** touched: it was down before and
after, no queue, no lock, no courier branch; GPU back to 0 MiB / 0%. The Mac rendered
nothing. The eight PNGs are **untracked** in
`genomes/sapling/nodes/002b-first-citizen/takes/stills/01-cold-open-r{1,2}-s{0..3}.png`
— `takes/stills/` is the candidate bin; `stills/` is founder-approved canon and
nothing was put there, because putting it there would assert an R4 verdict.

**The failure that started this, and the fix.** The first still came back as a thick
woody **mature branch** carrying ~8 leaves and a **ripe pink peach** — a grown tree
with the wrong fruit, when the entire premise is that he is 40cm tall. The scale
negatives were firing and losing, so the fix went into the positive prompt
(`shots.md` beat 01 only, two commits, text-only):

- **bc1b1a3** — the sapling leads instead of the scene; "40cm" and "whole plant in
  frame" state the scale out loud; the fig is small, green and *unripe* (it still
  swells — the founder's condition — but "ripening" is what coloured it peach);
  `macro shot` removed, it invited the branch-scale crop. **Result: mature tree gone,
  0 of 8 recurrences.** But two words of mine broke it: `mascot-simple`, copied from
  beats 02-03 where it modifies the sapling a goblin hides behind, became the SUBJECT
  here and **three of four candidates drew a chibi mascot creature with a face, arms
  and legs**; and `no ripe fruit` / `no large fruit` sat in the negative prompt
  suppressing the one piece of fruit the beat exists to show.
- **cce81ae** — no `mascot-simple`, no fruit negatives, `no chibi` / `no mascot` /
  `no creature` / `no face` written comma-terminated so `sd_prompt` lifts them into
  the negative. Measured with the repo's own `sd_prompt.compress`: old prompt = 67
  tokens and literally began with a comma; new = 72 tokens with **nothing dropped**.

**Honest read of the eight, against the beat's own five points** (tiny two-leaf
sapling / one small fig / empty green field / morning peach-gold sky / no humans-no
text): **no candidate passes.** Round 1 is rejected outright (3 of 4 are a creature).
In round 2: r2-s0 best composition, ~6 leaves, dry amber field, no fig; r2-s1 pretty
and violet (hue 320°, reads dusk not sunrise), no fig; r2-s2 giant foreground leaves
own the frame, scale reads backwards; r2-s3 best scale and the only truly green field
(38%), and the only stem carrying anything — a small **magenta flower bud**, not a
fig. **Two structural blockers, not seed luck: the fig is in 0 of 8, and the leaf
count is wrong in 8 of 8 (4-6 leaves, never two).** Conditioning i2v on a figless
plate means the fig can only "just.. appear" again — precisely the defect the
founder's approval condition exists to prevent. Untried and cheap, for whoever picks
this up: `still_local.py --init` img2img to paint the fig onto a chosen plate at low
strength; and replacing "fig" (which likely maps to *fig leaf* in the Danbooru
vocabulary) with "one small round green fruit hanging from the stem", plus "two
cotyledons" for the leaf count. Both are new recipes, so both wait for the founder.

**Screening page: `SCREENING.html` (local, untracked, nothing published, nothing in
`_site/`).** It now carries two sections — episode 1 `ep1-v30-fixed.mp4` yes/no at the
top, unchanged, and below it episode 2 beat 01: all eight stills at judgeable size,
each labelled with its seed and its five-point result, the beat's script text beside
them for comparison, the wrong ones shown *with the reason under them* rather than
hidden, and the question stated plainly — which one is the sapling as he pictures
him, or none — with the point that the pick becomes the frame the video is grown from,
so scale and the fig outrank prettiness. Contact sheet: `CONTACT-002b-b01.png`.

**Side finding worth keeping (it silently degraded every farm still ever rendered on
that box).** The rtx5090 had no `openai/clip-vit-large-patch14` tokenizer cached, so
`sd_prompt` fell back to its word-count estimate and trimmed trailing booster tags —
round 1 lost `very aesthetic`, an untrimmed variant lost the whole
`detailed, newest, masterpiece, best quality, very aesthetic` tail. Tokenizer is now
cached there and round 2 dropped nothing. **Assume prior farm-rendered stills were
missing part of their Animagine booster tail.**

### Still open tonight — recorded so the next session does not re-litigate them

- **`ep1-v30-fixed.mp4` is still unscreened.** 15 beats, 89s, rendered 2026-08-04,
  never watched. It is what blocks posting — and posting is what the founder himself
  ordered on 2026-08-02. It is the top section of `SCREENING.html`; it costs 89
  seconds.
- **Five trunk scripts are written and unread: 003b, 004, 005, 006a, 007a.** Only two
  leaves in the entire tree carry `approved_by: founder` (`001-t0-d.yaml` and
  `002b-t0-c.yaml`); everything downstream of 002b is script-blocked, not
  machine-blocked. **One reading pass is the cheapest unblock available in the tree.**
- **The rtx5090 has had three unclean shutdowns in three days, and today's was NOT
  under memory stress** — VRAM at 12%, host memory *falling*, step times *improving*
  when it went. That rules out the paging explanation we have leaned on and leaves the
  cause unknown. **Treat it as a reliability risk for any 15- or 21-beat run:** a crash
  at beat 12 loses the whole run unless clips are written and fsynced **as each one
  lands**, with the job resumable from the clips already on disk. Do not queue a long
  batch on that box until the per-beat save path is the default.

## 2026-08-07 — the four held beats were re-examined: three had been held on a broken measurement, one because a machine was off

**The founder's question, verbatim in effect:** should the whole episode be
animated? Episode 1's current cut `ep1-v30-fixed.mp4` has four beats that are
held stills with a slow push-in rather than animation — **3, 12, 13 and 15**.
Answering it needed the reasons those four were held, and the reasons did not
survive being checked.

**Beat 3 — measured on a picture that no longer exists.** The hold was decided
on a render of `03-deploy-succeeded-REVOKED-magenta.png`, the still the founder
rejected and which was revoked on 2026-08-04 (`049c519`, which renamed it and
replaced the shipping frame in the same commit). The frame the episode
ships had **never been animated at all**, and the old shot direction named
objects (text, a cursor) that are not in it. Animated tonight for the first
time: **0.20 median, 50% frozen**, against the revoked-still take's 0.13/72%.
Genuinely flat — a cel-shaded panel has almost nothing to modulate but the two
screens. Do not spend more renders here without the founder asking.

**Beat 12 — not static, measured wrong.** Whole-frame 0.19 median with 58%
frozen; measured **inside the sprout's own box** (0.38,0.42,0.64,0.60) the same
clip is **0.46 with 8% frozen**, against 0.14/67% for the cracked ground below
it and 0.08/77% for the sky. The frame is mostly rigid plain, and that averaged
plant away. **Same class of instrument error as cycle-016's mean-vs-median, one
level down: the right statistic over the wrong support.** A rewritten direction
was rendered tonight and **lost to the take it replaced** — 0.27/25% in the
sprout box against 0.46/8% — because it asked the stem to shudder "without
moving anywhere", and positive prose about stillness suppresses motion. v31
therefore carries the *older* clip; the rewrite is kept as evidence.

**Beat 13 — half the frame works, half cannot.** Grass and road 0.30/8%,
cloudbank 0.11/80%, because a 2.5s clip cannot show clouds travelling; the dead
half halved the whole-frame average. Re-rendered: **grass and road 0.28/15% →
0.50/0%, whole frame 0.19/53% → 0.30/3%**, cloud half unchanged (0.11/80% →
0.10/82%) — the cloud-shadow band the new direction asked for did not land.

**Beat 15 — never a judgement.** Nothing was wrong with its direction; **the
render box was switched off**, so no animation existed and a held still went in.
Two takes tonight. Take 1 scores **4.63/0%, the highest number in the episode,
and is rejected**: a bright red-orange cone stabs into frame twice, an object in
no still and no script — *the invented object is what produced the score.* Take
2, same seed and recipe with the wording moved to "in place" and a negative
naming the cone, measures **2.72/0%** with the object gone. Take 2 is in v31.

**Controls for reading any of these, same night, same model and recipe:** beat
11 = 2.36/0%, beat 1 = 1.75/3%, beat 7 = 0.78/0%, beat 9 = 0.36/2%.

**The held clips score HIGHER than the animated ones, and that is the trap.** A
held still with `hold_still.py`'s centred push-in moves every pixel: beat 3 held
= 2.13, beat 13 held = 2.90, beat 15 held = 1.67. **The frame-difference
statistic cannot compare a held beat against a moving one at all** — only one
animated take against another. Any future held-vs-moving call is the author's
eye or nothing.

**`ep1-v31-animated.mp4` exists — an unapproved working cut, no leaf written.**
15 beats, 15 footage, 0 slate, 89.96s, 720×1280, 8.9 MB, $0. `qa_episode` 13
checks pass with the same single luma warning v30 has; `check_sync` clean on all
of node 001; **`check_invention` flags nothing** on any of the ten animated
clips. Assembled with the recovered v30 recipe (`collect_farm.py f15` off
`0e8c298` — the f15 blobs are gone from the branch tip — plus the face-B beat 02
from `3629e58`, `hold_still` for 4/5/7/10/14, then the four swaps), verified by
rebuilding v30 itself first and diffing: **ten of the eleven unswapped beats are
pixel-identical**, and the eleventh (beat 14) is the same footage sampled 0.04s
later, because each animated clip is one frame longer than the held clip it
replaces. Five beats stay held on purpose (4, 5, 7, 10, 14), down from nine.

**A defect in v30 found by that rebuild, worth keeping:** v30's clip directory
was populated at 2026-08-03 16:26Z and its VO manifests were **never refreshed**
after `4611efc` (20:58Z the same evening) re-measured beats 6 and 7 —
`06-vo.json` 3.977 → 4.473s, `07-vo.json` 5.734 → 6.237s. v30 therefore sizes
those two slots to pre-sync-fix voice lengths and clips ~0.1s off the end of
beat 6's line. **The whole 0.88s by which v31 is longer than v30 is this
correction, not footage.** The lesson is narrow and concrete: a clip staging
directory outside the repo goes stale silently, and nothing compares it against
the tree it was copied from.

**Model choice was deliberate: Wan2.2-TI2V-5B, not LTX.** LTX is faster and its
suspension was lifted on 2026-08-06, but every beat already in the episode was
rendered on the 5B, and LTX's measured colour loss would change the look partway
through a 90-second cut. Consistency inside one episode outranks throughput.

**Screening page:** `SCREENING.html` (local, untracked, nothing published,
nothing in `_site/`) now carries three sections — episode 1 `ep1-v30-fixed.mp4`
yes/no at the top unchanged, then the new v31 section with the whole cut plus
per-beat held-vs-animated pairs for 3, 12, 13 and 15, each labelled with its
measured motion, a one-line plain reason it had been held, and its own explicit
question; then episode 2 beat 01. It states plainly that three of the four were
held on a measurement rather than on the founder's verdict, and it says in the
page why the number cannot decide held-vs-moving.

### Carried forward for a fresh session

- **Episode 1 is still unscreened, and that is what blocks posting** — which the
  founder himself ordered on 2026-08-02. Two cuts are now waiting, v30 and v31;
  the decision is one 90-second watch.
- **Five trunk scripts written and unread: 003b, 004, 005, 006a, 007a.** One
  reading pass remains the cheapest unblock in the tree.
- **Node 002b beat 01 has a fig at last, and four leaves after four wordings.**
  The fig is in 2 of 4 round-3 candidates after 0 of the previous 8; the leaf
  count is wrong in every picture ever rendered and **four wordings in, this
  model will not draw a two-leaf plant on request** — a model limitation, and
  the founder's call whether to accept it or change tools. Recommended
  conditioning frame: `takes/stills/01-cold-open-r3-s3.png`, **untouched** — both
  repaints made the fruit bigger when asked for smaller, so the untouched plate
  is the nub and the repaints are what the end of the shot looks like.
- ~~**Negative prompts silently truncate at 77 tokens on every render.**~~
  **FIXED 2026-08-07** (`sd_prompt.fit_negative`, commit d63271c). Measured with
  the real CLIP tokenizer, 7 of the genome's 177 beats were over: 001 beats 5, 6,
  7, 10, 14, 15 and 002b beat 1. 001 beat 7 was the worst at 115 tokens — 16 of
  the terms its author wrote were never sent. The fitter deduplicates, then drops
  whole terms from the least important end (house boilerplate before a
  beat-specific instruction, video_task's rule), and names what it dropped. It is
  a no-op for the 170 beats that already fitted — byte-identical, and a test
  holds that line. **Two consequences worth knowing:** re-rendering 001 beats 5,
  6, 7, 10, 14 or 15 will no longer reproduce the archived frames exactly, and
  the shot board still prints the *unfitted* negative under "as sent", so for
  those 7 beats the published board overstates what reaches the model (it was
  already wrong there — CLIP was cutting it — just differently wrong now).
- ~~**`002b-first-citizen/takes/` is untracked but NOT gitignored**~~ **FIXED
  2026-08-07** (same commit). Candidate media under any node's `takes/` is now
  ignored **by extension** — png/jpg/mp4/mp3/wav — so the yaml provenance
  sidecars beside the pixels stay in the tree. 001's `takes/` is exempted: it is
  a deliberately committed v1 archive, all 183 files still tracked, and new files
  there behave as they always have. Verified: tracked count unchanged at 1668,
  002b's 21 candidates gone from the untracked list.

## 2026-08-07 — the mitosis was never fixed because it was never attempted, and the metric scored it as the episode's best beat

**The founder:** *"why did we never fix the mitosis? you can remake that beat
with the new render method."* The beat is node 001 **beat 11, "grow"** —
*"Latency: three days. Throughput: one leaf."* Its clip is in
`ep1-v30-fixed.mp4` and in `ep1-v31-animated.mp4` right now.

**The answer is that nothing was ever tried.** No prompt, no negative, no seed
and no direction was ever changed to fight it. Beat 11 was never held, never
re-rendered and never flagged, because it measured **2.36 median with 0% frozen
frames — the highest motion of the fifteen**, and the steward called it the best
beat in the episode. The duplication *was* the score: a leaf dividing moves a
great many pixels. `check_invention.py` was written on exactly that observation
and nobody then went back and re-rendered the beat that prompted it.

**Three explanations checked and killed before touching anything.**

- **The 77-token truncation is not this one.** Measured with the real CLIP
  tokenizer: beat 11's still negative is **75 of 77 tokens**, `fit_negative`
  returns it byte-identical and drops nothing. The video path builds its
  negative against `NEG_MAX` 900 **characters** on UMT5 and was using **390**.
  Nothing was ever silently discarded here — unlike 001 beats 5, 6, 7, 10, 14
  and 15, which is a different defect that happens to share a date.
- **The suppressors are not this.** `antistatic_for()` correctly reads the
  movement words and applies Wan's anti-static terms; no shake terms, no
  "camera locked".
- **The negative had nothing whatever to say about leaves.** No
  anti-duplication, anti-splitting, anti-extra-leaf or anti-second-sprout term
  had ever existed for this beat. **They were never authored.** Meanwhile the
  direction asks the leaf to *unfurl* and *spring upright* — a shape
  transformation — while anti-static forbids the beat from holding still. Told
  to change shape and denied the option of not moving, the cheapest thing a leaf
  can do is become two leaves.

**The seed turned out to be recoverable, so this is an A/B and not another
take.** The f15 sidecars are gone from the branch tip but survive at `0e8c298`:
`f15-b11-1785804000-11-grow.mp4.meta.yaml` records **seed 20260816**, 704x1280,
14 steps, guidance 5.0, and both prompt strings. Re-deriving the pair from the
genome reproduces that sidecar's positive and negative **byte-identically**, so
the re-render holds still, recipe and seed constant and changes **one input**.
Same shape as the beat 15 fix on 2026-08-06, where naming the invented cone took
4.63 to 2.72 at a fixed seed.

**What was authored** (`motion.yaml`, beat 11, in beat 10's existing "no god
rays" convention — `video_prompt()` splits these into the real negative field, so
they never reach the positive): *no splitting leaf, no dividing leaf, no
duplicate leaves, no extra leaves appearing, no second sprout, no leaf
multiplying, no changing leaf count, no morphing silhouette.* They land at the
**front** of the negative, which is the position the cap cannot reach.

- **Video path: 390 → 552 characters of 900.** Nothing truncated, anti-static
  still applied.
- **Still path: untouched, still 75/77 tokens, byte-identical.** `motion.yaml`
  is read only by the video renderer. Adding the same terms to `shots.md` would
  put the still at **103 tokens unfitted**, and `fit_negative` would buy the room
  by dropping eight house terms in the documented order — *realistic skin
  texture, jpeg artifacts, deformed, extra limbs, blurry, low quality, signature,
  watermark*. That is a change to an approved still's recipe and is **not** made
  here.

**IT RAN, and the leaf no longer divides.** The 5090 was unreachable at the start
of the session and answered mid-session; the job fired the minute it did (see the
correction below — the box had been up the whole time).
`review/11-grow-antisplit.mp4`, seed 20260816, 704x1280, 14 steps, guidance 5.0,
UniPC shift 5.0, `model_cpu_offload`, 279s wall, $0, provenance sidecar beside
it. Frame counts at the apex, where the script has exactly two blades (the one
already there and the one unfurling):

| frame | old (`review/beat-11-grow.mp4`) | new |
|---|---|---|
| 0 | 2 — identical, it is the still | 2 |
| 20 | **3** — the hooked tip has its own closed outline, separated from the pale blade | 2 — hook and blade share one unbroken contour |
| 35-40 | **3, and the hook is DETACHED** — clear background between it and the leaf, no stem anchor | 2 — the curl stays attached to its blade |
| 58-60 | 3 overlapping shapes resolving to 2 | 2 |

The old clip's extra shape appears around frame 20, floats free by frame 35 and
is the thing the founder's eye caught. In the new clip the same apex leaf curls
its tip over and unfurls as **one** leaf for all 61 frames.

**The numbers, and why the good one went down.** Motion **2.36 → 2.07 median,
0% frozen in both**. A *lower* number is the better clip here, exactly as
predicted: part of the 2.36 was the duplication itself. `check_invention` flags
neither (old ret 0.85 / mono 0.58, new **0.90** / 0.58, against a 0.88 gate) —
and note the new clip scores marginally *worse* on the tool's own axis while
being visibly correct. That is the documented structural blind spot
(`check_invention.py:45`), not a drifted threshold: a beat that is *supposed* to
transform reads like an invention. **The frame count is the evidence; the tool is
not.**

**Not swapped into any cut, and nothing published.** The clip is a candidate for
the founder's eye against the one in v30/v31 — a taste verdict, R4.

**If he wants it cleaner, the next lever is the STILL, and that is his call.**
`stills/11-grow.png` contains **five leaf shapes** where the prompt asked for one
new leaf, a **Y-fork at the stem apex that already reads as one leaf mid-division**,
three free-floating detached leaf shapes with no stem anchor, and heavy shallow-DOF
blur leaving no crisp silhouette for the model to preserve. The negative can only
stop the model *adding*; it cannot remove what the approved frame already shows.
Replacing that still is a change to approved canon and is not steward work.

**New in the pipeline:** `pipeline/probe_beat.py` renders one beat with its
prompt and negative read from **files** — the negative carries Wan's Chinese
anti-static terms and a cp1252 console mangles them silently, which would have
produced a clip that renders and quietly proves nothing (both sha256 were
compared on each machine; they matched). It also writes the §7.2 sidecar that
`--stage simple` never wrote, which is the whole reason this beat's seed had to
be excavated from a dead commit. `pipeline/probe-b11-mitosis.sh` is the one
command that stages and fires it.

**Machine state, and a correction worth more than the render: THE 5090 WAS NEVER
DOWN TODAY.** It was reported off, it failed ping, ssh and ARP at 12:50 local, and
it answered at 13:20 — and its own clock says otherwise. `LastBootUpTime` is
**2026-08-06 20:13:54**, i.e. **17.4 hours of unbroken uptime** across the whole
window in which we called it powered off, and there is **no Kernel-Power 41 dated
2026-08-07 at all**. The unclean-shutdown record is six events, none today:

    2026-08-06 20:13:57   <- the mains failure, yesterday evening
    2026-08-05 06:07:09       2026-08-05 00:11:46
    2026-08-04 16:38:32       2026-08-04 11:30:38
    2026-08-03 11:33:23

**So today's outage was the LAN, not the power** — the same failure mode as
2026-08-06 (`2c02c3e`, "the LAN moved too"), and the second time in two days that
a network fault has been read as a dead box. The cost is not small: "the box is
off" ends work and waits for a human to walk to it, while "the box is unreachable"
is a thing to retry. **Ping is not a power state.** Before recording a machine as
down, check the other one's reachability and re-probe; after it answers, read
`LastBootUpTime` and settle which it was, because that answer decides whether
anyone has to get up.

The card was idle before and after (0 MiB / 0%), the one-shot task was deleted,
and the only python on the box is `telemetry.py --daemon`, which was already
running — **the farm worker was not started and nothing else was touched.**

MSI 5070 Ti (192.168.3.153) is **unreachable** — no ping, no ssh, ARP incomplete.
On today's evidence that word is doing real work: unreachable is what we know, and
whether it is switched off is exactly what we cannot tell from here.

## 2026-08-07 — the founder meant BEAT 9, and beat 9 is the worse one: 3 leaves become 7, and the metric scored it 1.00

**The founder corrected himself mid-sentence:** after *"why did we never fix the
mitosis?"* he added *"that's not the beat i was talking about. i was talking
about BEAT 9."* He is right, and the records pointed the other way:
`hold_still.py` attributes *"the sapling doing mitosis"* to beat 11, quoting him
directly, and beat 11 had just been re-rendered against it. Both are true. Beat
11 does divide a leaf. **Beat 9 does it worse, and nobody had ever written it
down.**

**Beat 9 is "WHOAMI" (0:48–0:53)**, no dialogue — the script is a terminal
panel, `$ whoami` / `sapling (ficus. probably.)`, typed in post over the plate.
Still `stills/09-whoami.png`; clip `review/beat-09-whoami.mp4`, the f15 take
that is in every cut of episode 1. Direction, before today: *"the sprout's two
leaves swing up on a gust and drop back, one leaf spinning as it falls, the
grass thrashes behind, dust motes streaming across the light."*

**Counted off the pixels, at 4x zoom on the subject, all 61 frames extracted:**

| frame | distinct leaf blades | what changed |
|---|---|---|
| 0 | **3** | one yellow top leaf, two white wing blades, one node |
| 5 | **4** | the top leaf has DIVIDED — a narrow blade peels left off the broad one |
| 10 | **5** | a third yellow leaf is out |
| 20 | **6** | a second node has appeared lower on the stem |
| 25–60 | **7** | two full tiers on an elongated stem; the plant also drifts right |

So it is the same defect class as beat 11 and a **distinct, worse instance**.
Beat 11's tip leaf divides and re-fuses inside the clip; beat 9's plant simply
**keeps growing**, which is beat 11's job in the script, not beat 9's — "$
whoami" is the identity beat, where the sapling is supposed to be *one thing*
for two and a half seconds.

**The metric is not just blind to this, it prefers it.**
`check_invention.py` scores beat 9 **ret 1.00** — the highest of every clip
measured, i.e. "returns perfectly to its opening composition" — while the
subject triples its leaf count. The reason is the same one the tool's own
docstring warns about: the sprout is a small share of a frame that is mostly
stable grass and sky, and the score is a whole-frame number. For scale, the same
run gives beat 8 **0.86** and beat 11 **0.85**. Nothing was flagged. This is the
second time in two days that a number has rated a duplication artifact as the
cleanest thing in the episode.

**The negative-prompt audit, with the real CLIP tokenizer and the real builder.**

- **Still path** (`sd_prompt.beat_negative`): **64 of 77 tokens**, nothing
  dropped, no warning. Not truncation.
- **Video path** (`video_task.video_prompt`): **363 of 900 characters.** It
  regenerates byte-identical to the f15 sidecar at `7f6c538`, so the genome
  still reproduces the take exactly. **It was using 40% of its budget and held
  not one word about leaf count.** The terms were never authored — the same
  finding as beat 11, arrived at independently.
- `antistatic_for()` fires correctly on the amplitude words, so the beat is
  forbidden to hold still.

**And a second cause that is ours alone, which beat 11 did not have.** The
direction *asked for the leaf count to change*. **"one leaf spinning as it
falls"** instructs a leaf to detach; **"the sprout's two leaves"** asserts a
count the approved still contradicts — `09-whoami.png` draws three blades plus a
bud. Adding "no extra leaves" to the negative while still asking for a leaf to
come off is precisely the mistake `video_prompt`'s own docstring records: *"It
was told to."*

**The still is not innocent either, and it was not changed.** At zoom,
`09-whoami.png` already contains the ambiguity the model resolved: the top
yellow leaf is drawn as a broad blade with a **second thin sickle blade peeling
off it from a shared base** — beat 11's Y-fork again — the two white wings have
hollow interiors, red rim outlines and no visible attachment on the right, a
pale teardrop hangs unattached under the node, and a straight dark grass blade
crosses the node diagonally, reading as a second stem. It stays as it is:
`motion.yaml` is read only by the video path and the still is the founder's
canon (R4).

**The logged "beats 08+09 near-identical" complaint is real and measured.** SSIM
between the two clips is **0.893 All / 0.869 Y**. Against every other beat in the
episode, beat 9 scores 0.755 (b12), 0.748 (b6), 0.726 (b7), 0.511 (b10); the two
*stills* are 0.807. Same low shot through grass, same sun on the horizon, same
three-blade sprout design. But it is **not** what the founder is reacting to
here: beat 8 holds its three blades rock-steady across all 61 frames, so the
thing that moves in beat 9 and not in beat 8 is the duplication.

**The fix, in `motion.yaml` beat 9.** Two inputs change, unlike the beat 11
probe, and deliberately: thirteen leaf-count terms lead the negative (`no
splitting leaf … no leaf detaching, no falling leaf`), **and** the direction
loses the detachment clause and the wrong count, the way beat 12's rewrite
dropped its count on 2026-08-06. Amplitude register kept — the stem now carries
the swing instead of a departing leaf. Measured after: positive **256 chars**,
negative **627 of 900**, fifteen terms leading it.

**Anti-static stays on, and that is a decision rather than an oversight.** Beat 9
does carry Wan's 静态 / 静止 / frozen frame / no motion block, and the question of
whether it is *pushing* the model to invent was asked and answered no: the
founder's standing complaint on this exact beat is the opposite one — *"the beat
9 generations i've literally make it not move at all. not one pixel"*
(2026-08-02) — and the frame has legitimate work to give it: thrashing grass,
streaming dust motes, a stem that can sway without gaining parts. Anti-static did
not invent the leaves. The absent leaf-count terms and the direction's own
detachment clause did, and both are now closed.

**The method is proven, on beat 11, before beat 9 ever renders.** That job
finished today as a controlled A/B — same still, same recipe, same seed 20260816,
only the negative changed — and the apex count settled it: the old clip holds 2
silhouettes at frame 0, 3 from frame 20, with the extra shape **detached and
unanchored** by frame 35; the new clip holds **2 for all 61 frames**. Motion fell
2.36 → 2.07 at 0% frozen in both, and **the drop is the artifact leaving.** So
the eight-term convention works and beat 9 is the same convention applied to a
worse case; what is missing here is only the render.

**THE RENDER DID NOT HAPPEN, and the reason is a Windows security policy, not a
schedule.** `pipeline/probe-b9-mitosis.sh` is written and was fired at the
5090 — same still, same recipe (704x1280, 14 steps, guidance 5.0, UniPC shift
5.0, `model_cpu_offload`), **same seed 20260814**, recovered from the f15 sidecar
at `7f6c538`. Both prompt files hashed identical on both machines. It died in
three seconds:

```
OSError: [WinError 4551] An Application Control policy has blocked this file.
Error loading "...\torch\lib\c10.dll" or one of its dependencies.
```

**Smart App Control turned itself on.**
`HKLM\SYSTEM\CurrentControlSet\Control\CI\Policy\VerifiedAndReputablePolicyState`
now reads **1 (enforcement)**, and the CodeIntegrity log dates the change. At
**13:25:22** today: *"Refreshed and activated Code Integrity policy
{0283ac0f-fff1-49ae-ada1-8a933130cad6} VerifiedAndReputableDesktop"* — the same
policy GUID the block event names, activated about a minute before beat 11's clip
finished rendering on that same torch. The log holds **1341 events going back to
2026-07-31**, and **exactly three of them are blocks (Id 3077), all today at
13:51** — this probe and the interactive check that confirmed it. So beat 11 was
the last render to get through, and this is not an artifact of the scheduled
task: a plain interactive ssh `import torch` is blocked identically.

**This one needs a human at the keyboard, and the switch is one-way.** Smart App
Control has no allowlist and no per-file exclusion; Microsoft's documented
remedies are signed binaries or turning it off, and **once off it cannot be
turned back on without resetting or reinstalling Windows.** PyTorch's wheels ship
unsigned DLLs, so there is no user-space route. The unblock is *Windows Security
→ App & browser control → Smart App Control settings → Off*, on the box, by
someone who accepts that it is permanent — **that is Oleg's or Roman's call, not
the steward's.** The probe dir `C:\banyan-farm\probe-b9-20260807` is staged and
hashed, so after the toggle the render is one command:
`bash pipeline/probe-b9-mitosis.sh`.

The card was idle before and after (0 MiB / 0%), the one-shot task was deleted,
and the only python on the box is the telemetry daemon that was already running —
**the farm worker was not started and nothing else was touched.** MSI 5070 Ti
(192.168.3.153) is still unreachable: no ping, ssh times out.

**The defect measured, before anything is rendered against it.** The lead's read
and the probe script's header were both counted again off `review/beat-09-whoami.mp4`
— 61 frames, 704x1280, 24fps — at frames 0/12/24/36/48/60, on 2x crops of the
sprout column rather than the whole frame, because at full width the plant is
forty pixels of a vertical still. Leaf shapes counted by eye; apex read off the
crop and converted back to source pixels, so the heights are approximate and the
*direction* is the finding:

| frame | leaf shapes | node tiers | apex y (of 1280, lower = taller) |
|---|---|---|---|
| 0  | 4 | 1 | ≈558 |
| 12 | 5 | 1 | ≈540 |
| 24 | 6 | 1→2 | ≈518 |
| 36 | 7 | 2 | ≈472 |
| 48 | 7 | 2 | ≈450 |
| 60 | 7 | 2 | ≈448 |

Four shapes become seven, one node tier becomes two, and the apex climbs about
110px — a tenth of the frame — over two and a half seconds. The cleanest
in-frame landmark: **at frame 0 the sprout's tip sits below the horizon grass
line; from frame 24 it stands above it.** This is not beat 11's defect at a
different size. Beat 11's leaf divides and re-fuses in place; beat 9's plant
*grows*, and growth is beat 11's only event, two beats early.

**So the terms are right and they stay.** Fifteen, not beat 11's eight, and the
two that beat 11 never needed — `no extra stem nodes`, `no branching stem` — are
the second tier the table names. Re-measured on the real genome today: video
positive **256 chars**, video negative **627 of 900**, 43 terms after dedupe,
**nothing truncated**, the growth terms leading and `frozen frame` still present,
and **nothing leaked into the positive**. The still path is untouched and
provably so — `shots.md` is not edited, and `beat_negative()` reads only
`shots.md` and `still_local.NEG`. For the record its negative fits at **67 of 77
CLIP tokens**, though that is the deliberately pessimistic tag estimate: no CLIP
tokenizer is installed on this Mac, and the box cannot supply one either (below).
`fit_negative` drops one house term there, `realistic skin texture` — pre-existing,
not ours, and the reason motion.yaml's terms were kept off the still path.

**`test_beat09_negatives_forbid_the_growth` now holds all of it** next to beat
11's, so deleting the terms is a red build rather than a quiet regression: the
fifteen terms present, none in the positive, leading the negative, under NEG_MAX,
anti-static alive, and — the half no negative can do — the direction no longer
saying `one leaf spinning as it falls`. Tests exit 0, lint exit 0, ratchet 38.

**The block is wider than torch, which rules out the workarounds.** It is not the
`c10.dll` load specifically: `from transformers import CLIPTokenizer` on the box
dies the same way on `regex/_regex`, *"An Application Control policy has blocked
this file"*. Every unsigned compiled extension in `C:\banyan-video\venv` is
blocked, so there is no import-order trick and no lighter path through that venv.
Checked and closed today: **WSL is not installed** on the 5090 (`wsl --status`:
"not installed"), so there is no Linux side to run under a policy that does not
apply; the **MSI 5070 Ti is still unreachable** (ssh timeout), so there is no
second card; and a fresh mainstream torch wheel would be a *second changed input*
against a seed-matched A/B even if its DLLs happened to pass reputation. The
render waits on the toggle, not on an idea.

**Nothing was touched on the box and nothing was rendered.** Card idle at 0 MiB /
0% / 42C, farm worker left down, probe dir `C:\banyan-farm\probe-b9-20260807`
still staged with the founder's still (`b0dabdfd…`, hash-matched to
`_site/.../09-whoami.png`). Its `b9-negative.txt` is one revision stale at 593
chars — harmless, because `probe-b9-mitosis.sh` regenerates both prompt files
from the genome and asserts the terms before it fires, so after the toggle the
render really is one command: `bash pipeline/probe-b9-mitosis.sh`. Seed
**20260814**, off the f15 sidecar.

## 2026-08-07 — the queue had nowhere to put a plan, so the plan lived in comments: `backlog:` and a promoter

**The approved plan (founder Roman, today).** The `/status` page must stop lying,
become genuinely live client-side, and answer at a glance NOW / QUEUE+BACKLOG /
DONE TODAY / WAITING ON ROMAN; the queue file gains a `backlog:` section with
dependencies, gates, day/night windows and estimates; a promoter moves work to
runnable when it unblocks; and the backlog gets stocked days deep. Every number
on the public page must be TRUE and sourced, staleness visible. This entry covers
the queue half of that; the page half is a parallel lane.

**What the file was.** 180 lines, **130 of them commentary**, holding one live
task that had finished four days earlier and one blocked entirely in prose. The
schema had no field for a dependency, a gate, a window or an estimate, so every
one of those went into a comment — unreadable by the status page, unqueryable by
anything, and impossible to keep honest.

**The schema, as landed.** `tasks:` keeps its exact meaning: runnable now, and
the only key any worker has ever read — `farm_worker.py:115` is
`.get("tasks", [])` against `origin/main`, which is also why a new top-level key
is invisible to every worker ever shipped, including stale checkouts. `backlog:`
is that new key. An entry is a tasks entry plus planning fields: `after` (ids that
must all show DONE on some heartbeat), `gate` (founder | code | hardware),
`gate_ref` (the specific thing — a `pending-founder.yaml` id, a code gap with
file:line, a machine and its fault), `needs` (cuda | vram20 | mps | video-venv),
`window`, `est_minutes`, `why`, and `runner` (farm | manual) for the difference
between a worker's inbox and a command a person runs. Unknown fields on a task
are inert — dead keys already exist in this file's history — so a promoted entry
keeps its planning fields and no worker cares.

**Two schema decisions worth defending.** `runner: manual` exists because most of
the real work right now is not farm-shaped — a probe script, a licence check, a
code change — and putting any of it in `tasks:` would hand a worker something it
would choke on. The promoter reports manual entries as runnable and never moves
them. And **`window:` is advisory and delays nothing**: it records that a
host-exclusive job will evict the farm worker, not that anyone should wait for
dark. Machine work is scheduled by dependencies, not human hours (Oleg,
2026-08-05), and a promoter that slept until night would be re-introducing the
thing that directive killed.

**`pipeline/queue_promoter.py`.** Idempotent, safe by hand and on a timer. It
fetches every `farm-results-*` heartbeat, then in ONE write: **retires** any task
with a `DONE task=<id>` line; **promotes** any backlog entry that is `runner:
farm`, carries no `gate`, and whose every `after` id is DONE somewhere, filling
`worker` from `needs` when unset; and **prints** what is unblocked but manual plus
every blocked entry with its blocker by name. It cannot clear a gate — that would
be deciding the founder has looked, or that Smart App Control is off, on its own
evidence — so clearing one is a human deleting the key in a commit. It invents no
work.

It edits the file as **text**, not by re-dumping it, because `safe_dump` cannot
carry a comment and this file's comments are what keeps a host-bluescreening job
parked. An entry's own comment run travels with it; a comment run that touches the
top of a region is preamble and stays put, so a move can never delete reasoning
that was not the entry's. Every write is verified by parsing both versions and
comparing id sets before it lands, which is what makes the move atomic in
substance rather than only in commit count.

**`queue_keeper.py` now refuses to run while a backlog exists.** It rewrites the
whole queue with `safe_dump`; that was tolerable for a bare task list and would
now erase about two hundred lines of blockers. Reviving refills needs a
comment-safe writer first — and an answer to who consumes a rotating
world-reference bank, which is the standing no-work-without-a-consumer question.

**Hygiene.** `faceneg-b01-1785819600` is **retired**: it finished 2026-08-03 at
02:59:53Z (`DONE task=faceneg-b01-1785819600` on `farm-results-rtx5090`) and sat
live for four days. A worker skips what it can see DONE in its own heartbeat, so
nothing re-rendered it — but a re-imaged box, or one whose `heartbeat.txt` was
reset, sees a fresh queue and a task it has never run. The heartbeat line is the
record; the queue entry was a loaded gun, and the promoter now removes these
automatically. The 5070 Ti row became a backlog entry with `gate: hardware` and
its real blocker (unreachable since 2026-08-06; find it by Wi-Fi MAC
9C:67:D6:85:0A:B6, the LAN having re-addressed to 192.168.70.x). **The AnimeGen
park is untouched**, reasoning and all.

**Stocked: fifteen entries, 7.6 hours, every one with a named consumer.** Mined
from STATE.md's recent sections, `002b-t0-c.yaml`'s `approval_scope`,
`ACTION-PLAN.md` §1 and `MODEL-COMPARISON.md` §1's SCHEDULED rows.

| gate | entries | est | what |
|---|---|---|---|
| **none** | 5 | **2.8 h** | beat 7's still with the sixteen negatives that never used to arrive (promoted to `tasks:` on the first run); find the msi by MAC; **the LTX jobs-loop, 2 h, the biggest unblocked job in the tree**; the FastWan licence check; the AniSora conversion check |
| **hardware** | 4 | 1.7 h | beat 9's anti-growth render; the 5070 Ti 480x832 row; T5's sample; T4 SageAttention |
| **code** | 1 | 0.5 h | the LTX episode batch, behind the jobs-loop |
| **founder** | 5 | 2.6 h | ep1 v30/v31 verdict → canon leaf + posting; 002b beat-01 video on the 5B and on LTX; 002b beats 02-21 stills; 002b's 21-beat re-voice |

**4.5 hours of that needs no human decision at all** — the gate-free work plus
everything held only by hardware, which is one one-way Smart App Control toggle
and one LAN scan away. By window: 6.1 h `any`, 1.5 h `overnight`, **0 h `day`** —
nothing in the backlog waits on office hours by construction.

**Three gates hold almost everything, and two of them are one action each.**
Smart App Control on the 5090 blocks four entries; the founder's unwatched
90-second cut and his unmade 002b frame pick block five; the unwritten LTX
jobs-loop blocks one. The most valuable single thing on this list is still the
90-second watch.

**Two honest gaps, recorded rather than papered over.** `pipeline/pending-founder.yaml`
has an id for the episode-1 verdict (`v6-verdict`) and **none for the 002b
beat-01 frame pick**, so two founder gates point at a decision the public inbox
does not list; adding it belongs to whoever owns that file. And `build_sim.py`
reads the queue's `tasks:` from raw GitHub — it will now see an accurate,
usually-short list, and it should learn to read `backlog:` for the page to answer
QUEUE+BACKLOG at all.

**Verification, each as its own step:** `lint_genome.py` exit 0, ratchet 38;
`test_pipeline.py` exit 0 (three new test groups — an old-style task still parses
and `backlog:` never reaches the worker's list; a gate blocks regardless of
`after`, `window` blocks nothing, manual is never queued, a farm entry missing a
node or a resolvable worker is refused; and the move itself is one write, both
lists, comments intact, idempotent on a second run); `yaml.safe_load` on the queue
exit 0, before and after the promoter's own commit.
