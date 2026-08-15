# Loop cycle 017 — the wording was never the lever; the camera negative was

**Opened:** 2026-08-16 · **Closed:** pending the seed wave filed at the foot of this
file · **Source:** the bark-board motion wave of 2026-08-15/16 — ten clips across
beats 06 and 10, of which eight had landed unread when this cycle opened.

## The finding

Two wordings were carried into this wave as established levers, on the theory that
naming the **path** ("rotating it edge over edge through every angle") rather than
the **destination** ("turns the board around to face the camera") is what makes the
board turn. Seeded out, neither survives:

| arm | seeds run | turned |
|---|---|---|
| beat 10 `slow` — "rotating it edge over edge through every angle" | 3 | **1** |
| beat 06 `f1` — "the face that was toward the camera swings away…" | 4 | **1** |

**1 of 3 and 1 of 4 is the engine's base rate** — the same number that retired
"turns the board around to face the camera" at 5d9a94e8. A wording that performs at
base rate is not a lever, it is a seed that happened to land. Both wordings were
promoted on a single sample each, and a single sample cannot tell a lever from luck
at a 25% base rate. That is the mistake this cycle exists to record.

**What actually separates every pass from every fail is the expanded camera
negative.** Three clips in this wave carry it — `ep2-b10-bark-pathneg-0815`,
`ep2-b06-bark-f1neg-0815`, and `ep2-b10-bark-camB-0815` from the round before — and
all three kept both guards in frame for all 97 frames and turned the board. It is
the only variable that does that, and it does it across BOTH beats and BOTH wordings.

    baseline negative (all arms):
      camera pan, camera tilt, zoom, dolly, push in, pull back, tripod,
      cut to another shot, scene change, different location, split screen,
      still image, freeze frame
    the expanded arm appends:
      , zoom in, dolly in, crane, handheld, the camera moves closer,
      framing change, scale change, cropping in

**The dominant failure mode is an uncommanded push-in, and it takes guard 2 out of
frame with it.** Beats 06 and 10 are both two-guard beats — beat 10 is *"Guard 2
flips the clipboard around"*, beat 06 is *"GUARD 2 turns over a clipboard made of
bark and reads"*. Every failing clip in this wave failed the same way: the camera
closes in over the first third, the second guard leaves the frame, and the board
never turns because the shot has become a chest crop with nothing else in it. The
board's behaviour was never the primary defect. The framing was.

This is the same law cycle 016 wrote down — *you stop motion by NAMING it in the
negative; positive prose does nothing* — applied one level out, to the camera rather
than the subject. It is **not** the retired "negative against prop deformation"
lever: nothing here asks the negative to hold the board's shape, and `f1s2` below
shows the negative would not have helped if it had.

## The clips, judged

Metrics are `hold_period.py` (period, autocorrelation strength) and `depth()` from
`vae_roundtrip.py`, with the terminal-freeze index reported **separately** because a
clip that dies at f70 and a clip that holds every 2 frames are different failures.
Reference depths: b13-AFTER 0.029 (real hold) · b06-DONE 0.215 · b02-FIXED 0.397.
Every verdict below is a cold read of the frames; the numbers only chose what to open.

### Beat 10 — plate `b10-barkboard-pass-s13.png`

| clip | seed | period | depth | terminal freeze | verdict |
|---|---|---|---|---|---|
| `slow` | 20260815 | 2 | 0.448 | none | **PASS** (baseline) — turns, no wall |
| `slows3` | 20260817 | 1 | — | none | **FAIL** — hard push-in, guard 2 gone by f35, board raised and held but never turns |
| `slows4` | 20260818 | 2 | 0.154 | none | **FAIL** — guard 2 gone by f26; board lifts and tucks into the arm crook at f70-96, which is not an edge-over-edge turn |
| `pathneg` | 20260815 | 2 | 0.425 | 1 frame | **PASS — best of the wave.** Both guards held to f96, framing stable from f9 on, board rotates through profile (a bark sliver at f44) and back to face |
| `barkface` | 20260815 | 1 | — | 1 frame | **CATASTROPHIC FAIL** — leading state tag "both faces of the board rough fissured bark," slams to an extreme close-up at f17, rockets out to a wide two-shot by f35, character designs change and the board becomes a scroll. min ncc 0.197 |

### Beat 06 — plate `b06-barkboard-pass-s10.png`

| clip | seed | period | depth | terminal freeze | verdict |
|---|---|---|---|---|---|
| `f1` | 20260815 | 2 | 0.535 | 1 frame | **PASS** (baseline) |
| `f1s2` | 20260816 | 4 | 0.331 | none | **FAIL** — both guards held and framing stable, but the board **dissolves to a shapeless blob at f26-35** and reforms smaller against the chest without ever turning |
| `f1s3` | 20260817 | 2 | **0.606** | **27 frames — dead from f70** | **FAIL** — heavy push-in, guard 2 lost, board never turns, clip stops moving at f70 of 97 |
| `f1s4` | 20260818 | 2 | 0.393 | 6 frames | **FAIL** |
| `f1neg` | 20260815 | 2 | 0.511 | 3 frames | **PASS** — both guards to f96, real rotation, and he reads it at the end, which is what the beat asks for |

### Two things the numbers got wrong on their own

**`f1s3` has the highest depth in the wave (0.606) and is a total failure.** The
depth was manufactured by the push-in — a camera closing steadily on a static subject
produces large, evenly-spaced pair differences and reads as healthy motion. Depth
answers "is the hold deep", not "is the right thing moving". The cold read is what
caught it, and the same clip is frozen solid for its last 27 frames.

**Terminal freeze is orthogonal to hold and invisible to both metrics.** It appears
at 27, 6, 3 and 1 frames across the beat-06 arms while their periods and strengths
sit in the same band. It has to be measured directly — the trailing run of
consecutive-frame ncc == 1.0000 — or it is simply not seen. It is worst exactly where
the push-in is worst, which is one more count against the camera.

## What this retires

- **The leading state tag on beat 10** (`barkface`). It destabilised scale violently,
  which is the beat-13 finding at f4dd75d8 reproduced on another beat. Do not refile.
- **More plain-wording seeds on either beat.** `slow` and `f1` have had 3 and 4 seeds;
  the answer is in and it is "base rate". Any further beat-06/beat-10 motion job
  carries the expanded camera negative or it is not asking a question.

## What this promotes, and the bar it has to clear

`pathneg` and `f1neg` are each **one watched sample**. That is exactly the evidence
`slow` and `f1` had when they were wrongly promoted, so they get seeds and not a
conclusion. Four fresh seeds each (20260819-20260822 — 20260815-18 are spent on both
beats), filed to `backlog/`:

**The bar, written before the renders, so it cannot be softened afterwards.** For the
arm to be a lever rather than another lucky seed, of 5 total samples (the watched one
plus four seeds) at least **4 must** hold all of:

1. both guards in frame at f0 **and** f96 — this is the one the wave actually failed;
2. the board passes through profile (a visibly narrow edge) and returns to a face —
   a lift, a tuck or a slide is not a turn;
3. terminal freeze under 4 frames;
4. no scale change large enough to crop a guard out.

3 of 5 or fewer and the expanded negative joins the wordings as base-rate noise, and
the lane stops rather than seeding a sixth thing.

Two further single samples ask whether the negative rescues the beat-06 wordings that
died on staging (`c1`, `d1`) — same seed and same prompt as their originals, the
negative the **only** variable — and two cross-beat samples move each beat's action
clause onto the other beat, both carrying the negative. One sample each, no seeds,
because nobody has watched them perform.
