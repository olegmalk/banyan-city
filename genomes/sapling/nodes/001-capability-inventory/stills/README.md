# Approved stills — the exact pixels the motion stage animates

Each PNG here was **approved by the founder** (2026-07-27, stills review rounds,
kernel v43+) and is canonical: the Kaggle notebook uses a committed still instead
of redrawing the beat, so what was approved is what gets animated (SVD is
image-to-video — the still IS the shot). Kaggle has no persistent disk; the repo
is the resume mechanism, same as clips/.

Provenance: drawn by cagliostrolab/animagine-xl-3.1 from the beat's shots.md
prompt (see git history for the exact prompt at approval time), steps 40, cfg 7.5,
seed 20260719+beat.

To REVOKE an approval: rename the PNG to `NN-<slug>-REVOKED-<why>.png` (git records
it, R6 keeps history). The renderers skip any name containing `REVOKED`
(`video_task.py:1308`, `:1433`, `:1501` — the line numbers this file used to give,
1182/1295/1359, moved when that module grew on 2026-08-08; the three `"REVOKED" not
in` guards are the same three), so a revoked frame stays readable as evidence without
ever being animated again. Deleting works too and is what this file used to say;
renaming is better, and it is what beats 3, 6, 7, 8, 9, 10, 12, 14 and 15 do.

**Revocations STACK, and beat 15 was the first beat here to carry two** — beats 3, 10 and
14 have carried two since 2026-08-09 as well (the section below). A `-REVOKED-`
name is not a slot; it is one refusal with its reason in it. Beat 15 now holds
`15-something-s-coming-REVOKED-abstract.png` (the vertical-streak frame the
"underground side view" prompt produced, retired 2026-08-04 by `049c519`'s reframe to
ground-level macro) and `15-something-s-coming-REVOKED-underground.png` (that reframe
itself — soil, stones and a raking light band, no plant in it — refused by the founder
in v32 on 2026-08-07). Both are skipped by the same guard and neither overwrote the
other.

## 2026-08-09 — beats 3, 6, 10 and 14 have NO approved frame, and their names say why

**This directory no longer holds fifteen approved frames. It holds eleven.** The
founder refused four of them itemised in v32 on 2026-08-07 and each one kept its canon
name anyway, so for two days every renderer in this repo read a refused frame as the
approved one and `/status` published "15 of 15 scene frames approved". The names are
now what the rest of this directory's names are: the refusal with its reason in it.

| beat | now | sha256 | his words, v32, 2026-08-07 |
|---|---|---|---|
| 3 | `03-deploy-succeeded-REVOKED-terminal-lab.png` | `8f5420d8a14897e6cefb9eacd54b04f8547d43434c58234b6035a0e444cf7f2d` | *"Beat 3 looks more like a terminal in some.. lab. not realistic. whatever you intended it to be, you should make a new image for it and make sure it looks like its inside a house."* |
| 6 | `06-too-blue-REVOKED-leaf.png` | `8fdc2f747c965fe7c644952d494e7f681b9924335a5534c7a12f0770db0803ae` | *"for beat 6, there shouldnt be a leaf in the image, doesnt make sense that he can see himself when he is looking at the sky."* |
| 10 | `10-sense-REVOKED-style-change.png` | `3f84af7209d8c474d1f963f9127cabec4ca3fddcd537c78c8aa37bddf687ec27` | *"for beat 10, another major style change and it looks a sapling in the middle of a long body of water, with a blank dark background."* |
| 14 | `14-worth-staying-in-REVOKED-illegible.png` | `3c9b104225081f94549ed3f7adbfe2dd5ad88f88c45f9ecb1de3b1ec422e1b0b` | *"beat 14 is.. i dont know what?? what is it supposed to be? i think you need to regenerate it."* |

All four are 832 × 1216, `cagliostrolab/animagine-xl-3.1`, and unchanged in every byte —
this was `git mv` and nothing else. Beats 3, 10 and 14 each already carried one earlier
revocation (`-magenta`, `-abstract`, `-abstract`); these are their second, and beat 6's
is its first. Nothing overwrote anything, which is the whole reason the reason word is
in the name.

**WHAT THIS CHANGES ON PURPOSE, and none of it is a regression to be undone.**
`hold_still.approved_still()` globs `NN-*.png` and skips any name containing `REVOKED`,
so it now answers None for these four beats: **render_t3 will SLATE beats 3, 6, 10 and
14 in any assembly built from here on**, until replacements land. A slate is the honest
picture of a beat whose frame the author refused; the alternative was to keep quietly
animating frames he had said no to, which is what was happening. `build_status.scenes()`
tests for the exact `NN-<slug>.png` name, so `/status` now reads **11 of 15 approved**
with four scenes "waiting for the author's pick" — the same four the /review checklist
asks about, and the same four `ep1-v33-assemble-1786124760` is gated on.

**`review/provisional-v33/ep1-v33-PROVISIONAL.mp4` is not affected.** It was assembled before this rename, from these
pixels, and it still holds them; a cut is rendered, not resolved at read time. What it
is a cut OF has not changed — it was always a provisional cut built on four frames he
had refused, and that is exactly what its own record and STATE.md say it is.

**Six clip records were given their measured still hash in the commit before this one,
so no poster broke.** `cuts/pairs/beat-03-held-approved`, `beat-10-zoom-18pct`,
`beat-10-zoom-gentle`, `beat-14-zoom-18pct`, `beat-14-zoom-gentle` and
`cuts/checklist/beat-14-HELD-moderate` each named their still by filename with no hash,
and `still_from_record` refuses a name it cannot find rather than guessing — six blank
players on the review page. Each hash was read out of the repository's own history
(`git rev-list -1 --before=<the clip's commit> HEAD -- <the still>`, then sha256 of that
blob), the method `cuts/pairs/beat-07-zoom-gentle.meta.yaml` records for beat 7's
re-promotion, and all six matched the bytes now under the new names. With the hash
recorded, rule 2 of `still_from_record` finds the renamed file and the posters are the
frames the clips actually hold.

**WHAT DOES NOT FOLLOW FROM THIS.** These four beats are not "waiting on a better
prompt" and this rename does not queue anything. Beats 3, 6, 10 and 14 are the four the
redraw wave still owes, `22b4cbe` records that beat 3 in particular is waiting on the
founder to choose which of his own rules gives, and nothing here changes who decides
what replaces them. R4: the pick is his.

## 07 / 08 / 09 — the progression, picked 2026-08-08 (item 03)

The founder answered checklist item 03 with three addresses and nothing else, verbatim:
**"po7-r1-s2, po8-r2-s0, po9-r1-s2"** — his own shorthand for the `p07`/`p08`/`p09`
grammar, normalised and resolved through `REVIEW-KEY-0808.md`, the pixel-matched
address map, not by grid position. That is R4. The reading of each pick, and the
directions they endorse, are in `shots.md` under **Beat 07**, **Beat 08** and
**Beat 09**.

| | beat 07 — WIDE | beat 08 — MEDIUM | beat 09 — CLOSE |
|---|---|---|---|
| label | `p07-r1-s2` | `p08-r2-s0` | `p09-r1-s2` |
| promoted from | `takes/stills/07-zero-0-moving-parts-prog-s2.png` | `takes/stills/08-sev-1-prog2-t0.png` | `takes/stills/09-whoami-prog-s2.png` |
| copied | byte-for-byte | byte-for-byte | byte-for-byte |
| sha256 | `76e4d81fa108654d7575224f6495c8c5932f7e57d49c57d6c458fc3db39e4282` | `e886758c3a344c87450304f50746ce825b38cf1ef9f765fde0db4212855115b2` | `16ec0b49e04e540681b857d75b5db466f15f0cdeb30705707bb1a5afa50f5f66` |
| size | 832 × 1216 | 832 × 1216 | 832 × 1216 |
| model | `cagliostrolab/animagine-xl-3.1` | same | same |
| round | **1** (`candidate_set: prog`) | **2** (`candidate_set: prog2`) | **1** (`candidate_set: prog`) |
| seed | **20262726** | **20260726** | **20262728** |
| task | `ep1-stills-rework-1786124640` | `ep1-stills-round2-1786129764` | `ep1-stills-rework-1786124640` |
| steps / guidance | 40 / 7.5 | 40 / 7.5 | 40 / 7.5 |
| wall | 9s, rtx5090 | 39s, rtx5090 | 9s, rtx5090 |
| prompt | the fenced block under **Beat 07** in `shots.md` | the fenced block under **Beat 08** in `shots.md` — the round-2 text, NOT `shots-alt-789.md`'s | the fenced block under **Beat 09** in `shots.md` |
| cost | $0 — local CUDA, no provider | $0 | $0 |
| replaces | `07-zero-0-moving-parts-REVOKED-grayened.png` | `08-sev-1-REVOKED-same-picture.png` | `09-whoami-REVOKED-same-picture.png` |

**Every seed above is read out of that PNG's own `.meta.yaml` sidecar under `takes/`,
not off a sheet caption.** Round 1's sidecars were reconstructed from `wave.log` on
2026-08-07 and say so in their own header comments; round 2 wrote itself at render
time.

**The three frames they replace are kept, and their names say why he refused them.**
Beat 7's is `-REVOKED-grayened` — his word, from v32: *"beat 7 makes everything look
grayened … the main problem is that it drastically changes the style."* Beats 8 and 9
are `-REVOKED-same-picture`, the other half of the same list: *"beat 7, 8, 9 are
basically the same picture."* Beat 7 was on both halves, and **the wide he picked
answers both** — that dual duty was written into item 03's copy before he read it, so
the palette complaint is closed by this pick rather than left hanging.

**THE ONE CAVEAT ON THE RECORD: THE PICKS MIX ROUNDS.** Wide and close are round 1;
the medium is round 2. Round 1's one documented flaw was **colour drift across the
trio** — that is the entire reason round 2 was rendered, and round 2 removed it by
using a byte-identical palette block, a byte-identical negative and **one shared seed
(20260726) across all three shots**, with the lens as the only variable. Two of the
three canon frames now come from outside that lock: three different seeds, and beat
09's negative is a different string from the other two. **The combination is his call**
— he picked per beat with the three sheets side by side, and mixing rounds was stated
as a legal answer in the copy he answered from. **But the drift risk transfers to the
assembled cut and is judged at the v33 screening, not here.** If 7→8→9 reads as three
colour temperatures rather than one camera moving in, re-rendering a single beat on the
palette-locked block costs 39 seconds at $0 and the round-2 wide and close already
exist. Nothing re-renders before he has seen them cut together.

**No sidecars beside these three either**, for the reason spelled out at the foot of
this file: a `.meta.yaml` naming `cagliostrolab/animagine-xl-3.1` next to a canon still
scores as a new CreativeML Open RAIL++-M finding and would push CI's licence ratchet
past 25. The provenance is this table, the takes' own sidecars, and git.

## 12-undefined.png — picked 2026-08-08, and the only pick of that wave

The founder screened the forty replacement candidates rendered on 2026-08-07 and
picked exactly one: **`b12-r2-s1`** for beat 12. That is R4, it is recorded verbatim
with the reservation he attached to it in `shots.md` under **Beat 12**, and it is the
frame every renderer now reads for this beat.

| | |
|---|---|
| promoted from | `takes/stills/12-undefined-r2-s1.png`, copied byte-for-byte |
| sha256 | `5bf2f645215e4fa10b47eb1e9f189edbf8775d056162791db410556b84913d87` |
| size | 832 × 1216 |
| model | `cagliostrolab/animagine-xl-3.1` — the house still model |
| prompt | round 2, the fenced block under **Beat 12** in `shots.md`, unchanged |
| seed | 20261731 — **recorded, not derived**: round 2 wrote a real sidecar at render time (`takes/stills/12-undefined-r2-s1.png.meta.yaml`, task `ep1-stills-round2-1786129764`), which round 1 did not and had to be reconstructed from `wave.log` |
| steps / guidance | 40 / 7.5, 39s wall on the rtx5090 |
| cost | $0 — local CUDA, no provider |

**It replaces a frame he refused, and that frame is kept.** The 2026-07-27 approval
for this beat is now `12-undefined-REVOKED-cracked-grey.png` — the dark place with
the dry cracked grey floor he named on 2026-08-07. It is the record of what was
refused and the reason the round-2 prompt reads the way it does.

**The reservation he picked it with, and it is not a defect to fix quietly:** *"not
sure what it's supposed to be."* The pick stands and nothing re-renders on it; the
full reading is in `shots.md`, because a note like that belongs beside the direction
it questions and not only beside the pixels.

**No sidecar here, on purpose** — the same reason 002b's `stills/README.md` gives. A
`.meta.yaml` naming `cagliostrolab/animagine-xl-3.1` beside a canon still would be
scored by `licence_gate` as a new CreativeML Open RAIL++-M finding (D15, open, the
founder's to settle) and would fail CI's ratchet. The provenance lives in this file,
in the take's own sidecar under `takes/`, and in git.

## 15-something-s-coming.png — picked 2026-08-08, and it is the ONE SAMPLE, not just a frame

The founder's verdict on the beat-15 round-3 sample was three characters long:
**`b15-r3-s1`**. Resolved through `REVIEW-KEY-0808.md`, the pixel-matched address map,
not by grid position — and `b15-r3-*` is the round-3 row of `LABELED-beat15-r3.png`,
the four seeds redrawn with the sapling tall. That is R4. The reading of the pick and
the direction it endorses are in `shots.md` under **Beat 15**.

| | |
|---|---|
| promoted from | `takes/stills/15-something-s-coming-r3-s1.png`, copied byte-for-byte |
| sha256 | `f60c1404f88d45720ca295dfc753e9eaabb815446710bcfffb3c7a07b7277f54` |
| size | 832 × 1216 |
| model | `cagliostrolab/animagine-xl-3.1` — the house still model |
| round | **3** (`candidate_set: r3`) — there is no r2 for this beat; the round-2 tag belongs to beats 3 and 12, and skipping it keeps a label meaning the same round everywhere |
| seed | **20261734** — read out of that PNG's own `.meta.yaml` sidecar under `takes/`, which round 3 wrote at render time, never off a sheet caption |
| task | `ep1-beat15-r3-1786193372` |
| steps / guidance | 40 / 7.5, 9s wall on the rtx5090 |
| prompt | the fenced block under **Beat 15** in `shots.md` — the round-3 text, with `one slender sapling standing tall` as the subject |
| negative | the recipe's list **minus one term, `tall tree`** — recorded in the take's sidecar as `negative_terms_removed: tall tree`, and the sidecar's header comment carries the un-removed string for comparison |
| cost | $0 — local CUDA, no provider |
| replaces | `15-something-s-coming-REVOKED-underground.png` |

**IT REPLACES A FRAME WITH NO PLANT IN IT, and that frame is kept.** What was canon
here until this pick — `15-something-s-coming-REVOKED-underground.png`, sha256
`aa14d078774b703cecc156f119fc0142e4a73ec350675790b6a094fe0d74d34a` — is soil, stones
and a hard light band raking in from the right, and nothing growing. It is the frame
the founder refused in v32 in his own word: *"for beat 15, why is it showing the
underground? i think it should show the sapling, no?"* — which is where the `-underground`
in the name comes from. Retired in place rather than deleted (R6), because it is the
record of what the closing shot of the episode used to be.

**THIS PICK IS ALSO A RECIPE VERDICT, which no other frame in this directory is.**
Beat 15 was drawn first and alone on purpose (ONE SAMPLE BEFORE ANY BATCH, 2026-08-03),
and passing it settles two things beyond one beat's pixels: that *the sapling reads
tall* looks the way he meant it (his item-07 ruling, and this is the first frame this
tree has rendered under it), and that dropping **one** term — `tall tree` — from
`sd_prompt.SCALE_NEGATIVES` is the right reconciliation rather than deleting the scale
block or keeping it whole. The remaining four beats of the wave (3, 6, 10, 14) and
episode 2's twenty inherit that removal from this frame. Which of them it actually
touches is stated in `shots.md`'s wave note and is not "all of them" — `SCALE_NEGATIVES`
only fires on a prompt whose own text says the subject is small.

**No sidecar beside this one either**, for the reason the section above and the foot of
this file give: a `.meta.yaml` naming `cagliostrolab/animagine-xl-3.1` next to a canon
still scores as a new OpenRAIL++ finding and pushes CI's licence ratchet past 25. The
provenance is this table, `takes/stills/15-something-s-coming-r3-s1.png.meta.yaml`, and
git.

**FOUR OLDER SIDECARS NAME THIS FILENAME FOR CLIPS DRAWN FROM THE OLD PIXELS, and
they are not being edited because they are not wrong.**
`cuts/pairs/beat-15-animated.meta.yaml`,
`review/animated/15-something-s-coming.mp4.meta.yaml` and
`review/animated/15-something-s-coming-v2.mp4.meta.yaml` each carry
`init_still_sha256: aa14d078…` — the bytes now living under the `-REVOKED-underground`
name — so each states exactly which frame it conditioned on and stays true after the
promotion. `cuts/pairs/beat-15-held.meta.yaml` names `source_still:` with no still sha
(its own `sha256:` is the CLIP's, verified against `cuts/pairs/beat-15-held.mp4`), so it
is the one that is merely ambiguous rather than precise. Beat 12's pick left the same
pattern alone for the same reason.

**ONE CONSEQUENCE OF THAT, RECORDED HERE BECAUSE IT IS VISIBLE AND WAS NOT INTENDED.**
`build_site.still_for()` picks a clip's review-page poster by reading `init_still` /
`source_still` **by name**, and `poster()` only reaches that fallback when ffmpeg is
absent — which is exactly the Vercel build image (`build_site.py:574-601`, its own
docstring). So on the deployed `/review/` page the beat-15 comparison pair can show a
poster of the NEW tall-sapling frame over the OLD soil-and-stones footage. Beat 12's
promotion did the same thing on 2026-08-08 and it went unnoticed. Not fixed in this
commit — the fix is in `build_site`, it needs a test, and it is not a stills-promotion
change — but it is queued and named rather than left to be discovered on the page. If any of those clips is re-rendered it gets the new frame
and a sidecar that names its bytes.
