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
`pipeline/kaggle/wan-t2v-kaggle.ipynb` (open Wan 1.3B on free Kaggle GPU).

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
