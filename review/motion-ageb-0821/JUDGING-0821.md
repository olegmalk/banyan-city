# The age-B expressive wave, judged — 14 clips, 7 beats, 2026-08-21

All fourteen `ep2-b*-tilemotion-s{1,2}-0821` clips landed on the rtx5090 box, were
pulled to this directory and **verified against the box's own `.sha256` manifest
before a frame was opened** — 28 of 28 files OK (mp4 + sidecar for each).

Every clip is 121 frames at 24 fps = **5.04 s**, 704x1280, LTX-2.3-Distilled, two-stage,
image-crf 10, guidance 2.0, $0 (local GPU).

## The bar these were judged against

Not a metric. `pipeline/canon.yaml` → `ep2-goblin-design-adult` →
`correction_2026_08_20`, which is the founder's own correction and reads the B tile's
pixels as the authority:

* **EYES** — blank white, no iris, no pupil; two narrow upward-slanting slits under one
  heavy dark brow bar. "The single loudest creature cue and the first thing a close-up
  destroys."
* **NOSE** — no human nose, a blunt forward muzzle.
* **MOUTH** — one wide thin lipless line.
* **EARS** — short, broad, low-set flanges swept back, almost flush at the jawline.
  **NOT long tapering elf spikes.**
* **SKULL** — large smooth dome, ~1/5 of the seated figure's height.

Plus, per beat: does the beat's action read, and is the **usable window** at least as
long as the slot `render_t3.fit_duration` will give it —
`max(min(clip, vo+2.0), vo+0.4)` with voice, `min(clip, script_s)` without.

| beat | VO | slot | must be clean through |
|---|---|---|---|
| 02 | silent | 4.04 s | f096 |
| 03 | 3.98 s | 5.04 s | f120 |
| 04 | 5.76 s | 6.16 s | f120 **+ the last frame holds 1.12 s** |
| 07 | 2.93 s | 4.04 s | f096 |
| 08 | 2.12 s | 4.12 s | f099 |
| 13 | 1.56 s | 3.56 s | f085 |
| 20 | 1.74 s | 3.74 s | f089 |

## The one failure mode this wave has, named once

**THE FACE DISSOLVES INTO A GREEN EGG.** It is not drift and it is not a freeze: the
head keeps its silhouette and its colour, and the eyes, brow bar and mouth line simply
stop being drawn, leaving a featureless ovoid. It arrives suddenly, always in the second
half, and it never recovers. Six of the fourteen clips have it. **It is the whole
judging axis** — every pick below is the seed whose face survives its own slot.

## Per beat

### BEAT 02 THE SPRINT — SWAP, seed 2, trimmed to 4.04 s
* **s1** — face intact to **f048 (2.0 s)**, green egg from f055 onward. This is the
  clip the wave lane flagged PARTIAL. Slot needs f096. **FAIL.**
* **s2** — face, slit eyes and open mouth intact to **f101 (4.21 s)**; the run, the
  push off and the dive into the grass all happen inside that. Egg only from f106.
  **PASS with 0.17 s of margin over a 4.04 s slot.**
* Trimmed to 97 frames so the slot can never reach past the window regardless of the
  script's paper timing. **PICK: s2-trim.**

### BEAT 03 BAD COVER — SWAP, seed 2
* **s1** — face holds all 121 f, and it has the most real body motion in the wave (he
  shifts, comes up onto a knee, turns). But **the costume morphs on screen**: a dark
  cloak becomes a brown plaid blanket between f065 and f076, i.e. at 3.0 s, well inside
  a 5.04 s slot. That is a continuity break the viewer sees. **FAIL.**
* **s2** — face holds all 121 f, no morph, no freeze. Motion is small: seated, hands on
  knees, a lean at the end. For a beat whose content is *hiding badly and not moving*,
  small is defensible. **PICK: s2.**
* Replaces a take whose recorded fault is a **0.79 s dead freeze at the end of the slot,
  15 frames byte-identical**. s2 has no dead frames.

### BEAT 04 THE FOOTNOTE — SWAP, seed 1
* **s1** — face holds all 121 f and stays large in frame; the head tilts and turns down
  through the clip. **The last frame is clean, which this beat specifically needs** —
  its 6.16 s slot is longer than the 5.04 s clip, so `render_t3` plays it once and holds
  frame 120 for 1.12 s. **PICK: s1.**
* **s2** — also holds, but the camera drifts back and the head is meaningfully smaller
  by f120; the frame that would be held for 1.12 s is the weaker of the two.

### BEAT 07 CONFISCATE — **KEPT**, both seeds fail the action
* **s1** — identity holds to ~f095, then the slit structure smears; the only gesture is
  hands clasping at f098.
* **s2** — identity holds, motion is very close to zero.
* **Neither clip contains a guard.** Beat 07 is an authority taking something off the
  scavenger; both age-B seeds are a solo standing portrait, so the beat's action is not
  merely weak, it is **absent**. The take in the cut earns its place on exactly this
  axis: "the guard raises his OWN arm at f045 and the point holds to f096."
* **Beat 07 keeps `07-confiscate-b07-point-crf10-0819.mp4`, and keeps its named fault:**
  the plate dresses the scavenger in the guard's pale wrap tunic and white sash, so the
  shot reads as two officials in matching kit. **Age-B did not fix it and this round did
  not try** — the age-B plate never staged a second figure.

### BEAT 08 INSIDE HIM — **KEPT**, both seeds fail identity
* **s1** — green egg from **f055 (2.29 s)**. Slot needs f099. **FAIL.**
* **s2** — green egg from **f055** too, with a detached brow bar floating below it from
  f065. **FAIL.**
* Same beat, both seeds, same frame. **Beat 08 keeps `08-inside-him-b08-twohander.mp4`
  and keeps its fault:** unjudged, and its identity is open — every geometric-conditioning
  rung returns two green figures, because `green skin` enters the pooled embedding and
  lands on both bodies.

### BEAT 13 THE SHADE — SWAP, seed 2
* **s1** — carries the win the wave was chasing: **a real smile, f000–f044**. Then the
  face is an egg from **f065 (2.71 s)** — inside a 3.56 s slot. The expression this wave
  exists to get is in a clip that cannot hold it. **FAIL.**
* **s2** — face holds all 121 f. Through the slot (f000–f085) he is seated, head down,
  eyes closed, settling. **PICK: s2.**
* **Named honestly:** s2's own expressive lift — head up, blank slit eyes, mouth open —
  begins at **f087 / 3.62 s**, which is **0.06 s past the end of its slot**. The cut
  will not show it. That is the beat's fault going out, and the cheap next rung is
  staging the lift earlier, not another seed.
* Replaces the frame the founder was literally shown when he said *"this is one of the
  images where the goblin looks like an adult, which is wrong."*

### BEAT 20 EVIDENCE — SWAP, seed 2
* **s1** — face holds all 121 f, cleanest identity in the wave, but he never lifts his
  head, which is the outgoing take's own unmet clause.
* **s2** — face holds all 121 f **and he looks up**: the head rises from f055 and is up,
  slit eyes open and mouth parted, by f076 — completed at 3.17 s, inside a 3.74 s slot.
  **PICK: s2**, because it is the only clip in the wave that closes a `done_when` clause
  the cut has been failing.
* Outgoing verdict for the record: "STILL NOT A PASS ON THE BEAT ... HE NEVER LOOKS UP,
  and the tree is still the wrong tree."

## Faults that travel with the five swapped beats

1. **THE EARS ARE WRONG, IN ALL FIVE.** Canon's B tile says short, broad, low-set flanges
   almost flush at the jawline. Every age-B clip draws **long tapering pointed ears**.
   This is the wrong-ears defect already named in `bfcc7c99` and it is now shipping on
   five beats instead of being confined to plates.
2. **C1 — the magenta/pink collar** is present on beats 02, 03, 04 and 13.
3. **T4 — the magenta ear-stud** is present on beats 03, 04 and 13.
4. **BEAT 20's FRUIT IS RED.** Canon has the fig purple (the 08-13/14 ruling). The
   outgoing take carried the same fault, so this is a carry-across, not a regression.
5. **THE CUT IS STILL MIXED.** `canon.yaml` counts the goblin in TWELVE of the twenty-one
   beats (2, 3, 4, 7, 8, 13, 14, 15, 16, 17, 19, 20). This wave covered seven and five
   of them pass, so the shipped cut has **five beats on one face and seven on the old
   assorted ones**. It is more consistent than it was — five beats now share one exact
   design, where before no two goblin beats matched — and it is not consistent. Beats 07,
   08, 14, 15, 16, 17 and 19 are the remaining work, and it is post-ship work.

## Ledger

| beat | s1 | s2 | pick | why |
|---|---|---|---|---|
| 02 | FAIL egg f055 | PASS to f101 | **s2, trimmed 97f** | window |
| 03 | FAIL costume morph f076 | PASS 121f | **s2** | continuity |
| 04 | PASS 121f, face large | PASS 121f, face recedes | **s1** | the held last frame |
| 07 | FAIL no action | FAIL no action | *keep current* | no guard in either |
| 08 | FAIL egg f055 | FAIL egg f055 | *keep current* | identity |
| 13 | FAIL egg f065 | PASS 121f | **s2** | window |
| 20 | PASS 121f, no lift | PASS 121f, lifts | **s2** | closes a done_when |

**5 swapped, 2 kept.** Every swap is a **STEWARD PICK on the design axis and is
R4-veto-able in one line** — the founder has screened none of these fourteen clips.

Evidence: `STRIP-b02.png`, `STRIP-b02-s2-tail.png`, `STRIP-b03.png`, `STRIP-b04.png`,
`STRIP-b07.png`, `STRIP-b08.png`, `STRIP-b13.png`, `STRIP-b20.png`, and
`STRIP-CURRENT-shipping.png` (the seven outgoing takes side by side, which is the
picture that makes the design argument on its own).
