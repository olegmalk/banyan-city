# v34 clip set — episode 1 — STAGING. NOT screened, NOT published

Staged 2026-08-09. **ASSEMBLED 2026-08-09 21:03 local** into
`../ep1-v34-PROVISIONAL.mp4` — all fifteen beats, no slate. Nothing here is
promoted to a canon filename or published, no file in `review/` is tracked by
git, and nothing has been opened on the founder's screen.

## What changed from v33, and why v33 could not just be re-cut

v33's checklist item 12 says it plainly: **v33 needs a rebuild, not a redraw** —
four of its fifteen beats were wrong. **All four are now closed.**

| beat | v33 | v34 | why |
|---|---|---|---|
| 03 | **footage**, 2.54s | **held**, 3.54s | v33's clip was animated on `init_still_sha256 8f5420d8…`, which is now `03-deploy-succeeded-REVOKED-terminal-lab.png`. It is footage of a refused drawing. Re-filmed on the frame he picked, `b03-r4-s3` (a0a5170). |
| 06 | held on `06-too-blue-r3-s2.png` | **held**, 4.87s — **PROVISIONAL** | he rejected r3 (*"women, too many clouds/weird cloud formations"*) and then r4 (*"its getting worse"*). Round 5 (82fd4ff) put `no humans` in the POSITIVE and drew **zero people in 4 of 4**. Held on the steward's pick `b06-r5-s2` — see **Beat 06** below. |
| 10 | held on the pre-promotion frame | **held**, re-filmed | v33's sidecar recorded `source_still_sha256 3f84af72…`; canon is now `f05fe426…` (`b10-r1-s3`, a0a5170). |
| 14 | held on `14-worth-staying-in-r3-s3.png` | **held**, 12.99s | he rejected r3 — *"all too short"* (HEIGHT, not area) — and picked `b14-r4-s3` at ~14:40Z. Re-filmed on that frame. |

**Beat 14 arrived after the re-film lane closed, and the frame was verified
rather than assumed.** That lane budgeted 30 minutes against `origin/main` and
gave up at 16:30Z with the promotion still uncommitted; it was right to. The
promotion has since been checked directly instead of waited for:
`stills/14-worth-staying-in.png` is **byte-identical (`cmp` clean) to
`takes/stills/14-worth-staying-in-r4-s3.png`**, the take he named, at sha256
`ab1ecdc9…` — the same hash `stills/README.md` records for his pick. It is his
frame, so this beat is **not** provisional. The file is still untracked: the
promotion COMMIT belongs to the verdicts lane, which holds the `stills/README.md`
table for it, and this lane deliberately did not race them for it.

**Beat 06 is the one beat here the founder has never seen, and it is labelled
everywhere.** Round 5 cleared on the axis he named twice, but *clearing* is a
measurement and *choosing* is R4's. `b06-r5-s2` is the steward's pick at
confidence 0.55 (taste ledger `ep1-b06-r5-provisional`, written before the sheet
existed), held so that he screens a beat 6 instead of a slate. The clip's sidecar
opens with a PROVISIONAL banner and carries `provisional: true`; the cut's own
manifest carries it too. **The cost is pre-registered:** none of the r5 four
looks straight *up*, and s2 has mountains the script never mentions — if he
rejects it, that is the most likely reason, and the answer is a scenery-safe
camera tag, not a return to person negatives.

**Beat 03 changes in KIND, and that is the one thing here a screening should
look at.** He has seen this beat *moving* in v31, v32 and v33. It is a held still
now because the frame it moved on was thrown out and the Mac-side $0 route is the
one that was authorised tonight; a GPU re-render on the new frame is the
alternative and nobody has ruled between them. Flagged, not decided.

## The set

Eleven held beats, four filmed, **none absent**. Held beats use
`pipeline/hold_still.py` — the fixed 12% linear centred push-in, cut from the
native still on `plate_prep`'s cover-centre policy. No video model ran on them
and none is claimed. Filmed beats are **byte-for-byte copies** of the v33 files,
carrying the render record their original sidecars carried, unedited — so their
headers still name the v33 set, which is where those pixels were staged. Nothing
about them changed but the directory.

- beat 01 footage `01-the-keyboard.mp4` 2.54s — copied from v33
- beat 02 footage `02-three-oh-seven.mp4` 2.54s — copied from v33
- beat 03 **held** `03-deploy-succeeded.mp4` 3.54s ← `03-deploy-succeeded.png` **(canon, a0a5170)**
- beat 04 held `04-the-fall.mp4` 3.50s — copied from v33
- beat 05 held `05-fan-spinning-down.mp4` 2.58s — copied from v33
- beat 06 **held, PROVISIONAL** `06-too-blue.mp4` 4.87s ← `takes/stills/06-too-blue-r5-s2.png` **(steward pick, NOT canon)**
- beat 07 held `07-zero-0-moving-parts.mp4` 6.67s — copied from v33
- beat 08 held `08-sev-1.mp4` 12.92s — copied from v33
- beat 09 held `09-whoami.mp4` 2.58s — copied from v33
- beat 10 **held** `10-sense.mp4` 10.54s ← `10-sense.png` **(canon, a0a5170)**
- beat 11 footage `11-grow.mp4` 2.54s — copied from v33
- beat 12 held `12-undefined.mp4` 2.58s — copied from v33
- beat 13 footage `13-i-always-left.mp4` 2.54s — copied from v33
- beat 14 **held** `14-worth-staying-in.mp4` 12.99s ← `14-worth-staying-in.png` **(canon `b14-r4-s3`, his 14:40Z pick)**
- beat 15 held `15-something-s-coming.mp4` 2.58s — copied from v33

## Durations

Held beats are cut to their slot: VO `total_s + 0.4`, the floor of
`render_t3.fit_duration` and a fixed point of it, so the assembler neither loops
nor lengthens them. Beat 03 gains a second by this rule (VO 3.13s → 3.53s slot):
its v33 footage was **2.54s against a 3.53s slot**, which is exactly the shortfall
that hands `render_t3` a clip to loop. Beat 06's slot is 4.87s (VO 4.473 + 0.4)
and beat 14's is 12.99s (VO 12.592 + 0.4); the assembler looped neither.

## Verification run on the re-filmed beats

Frame 0 of each new clip was decoded and compared against
`plate_prep.fit_cover(still)` — the composition the recipe claims to cut from —
and against `hold_still`'s own recomputed frames at the start, midpoint and end,
so a reversed or truncated move cannot pass on its first frame alone.

| beat | frame0 IS the plate | PSNR f0 / mid / last | window | monotonic |
|---|---|---|---|---|
| 03 | yes, byte for byte | 42.85 / 42.35 / 41.70 dB | 669→597 px | non-increasing, one-way |
| 10 | yes, byte for byte | 43.99 / 44.12 / 44.08 dB | 669→597 px | non-increasing, one-way |
| 06 | yes, byte for byte | 40.83 / 41.10 / 40.19 dB | 669→597 px | non-increasing, one-way |
| 14 | yes, byte for byte | 43.89 / 44.00 / 43.57 dB | 669→597 px | non-increasing, one-way |

The residual is h264 quantisation and nothing else — the pre-encode frame is the
plate byte for byte. Frame counts were probed rather than trusted: 117 frames at
704x1280 for beat 06 (4.87s × 24) and 312 for beat 14 (12.99s × 24), both exactly
what `hold_still` computed. `source_still_sha256` in each new sidecar was
re-measured against the file on disk.

## The assembled cut

`../ep1-v34-PROVISIONAL.mp4` — 90.1s, 720x1280, **15 beats, 0 slate**, $0, no
model ran in this step. `leaf: bench (--out) — no leaf, not canon`.

- `qa_episode`: 13 checks pass, 2 warnings, both pre-existing and both structural
  — a 5.5s dialogue hole from 12s (beats 04/05 have no VO) and an opening mean
  luma of 45/255 (beat 01 is a dark room by design).
- `check_sync sapling 001`: picture, script and voice agree on every beat.

## Standing

Taste is the founder's (R4). Nothing here has been screened by him and no frame
here is promoted. The canon frames under beats 03, 10 and 14 are **his own
picks**; beat 06 is the only **steward** pick in the set, and it says so in its
own sidecar and in the cut's manifest.

**A note on the word `provisional`, because the manifest will look alarming.**
The cut's head lists twelve flagged beats, not one. Twelve of these clips are
byte-for-byte v33 copies and inherit v33's hand-written `provisional: true`,
which that lane applied to a whole review set for four different reasons —
*"canon, unchanged"*, *"the founder's face-B pick"*, *"old footage is the
superseded picture"*, and an actual unratified guess. Beat 15's record contains
both readings at once: reason *"canon b15-r3-s1, approved 2026-08-08"* under an
authority line reading *"the founder has ratified nothing here"*. So the flag is
**copied, never interpreted** — a row means "this ingredient's own record marks
itself provisional, read its reason", and only beat 06's reason is the strict
one. Settling that vocabulary is a separate job and it is the author's.
