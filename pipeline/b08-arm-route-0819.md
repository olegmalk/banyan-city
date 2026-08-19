# Beat 08's pointing arm — the route, decided 2026-08-19

**Decision: no job filed. Not for want of a tool — the tool question got answered
tonight, and favourably — but because beat 08 does not have an arm-shaped hole to
fill. The init that survived 0.30 has both of the guard's hands committed to the
clipboard, so any arm added to it is a *third* arm.**

This closes the "source an arm for this init" framing that the boardcomp verdict
opened, and reopens the beat one level up, at staging. $0 spent. Nothing queued.

---

## 1. Where this started

`ep2-b08-boardcomp-0818` returned `PASS-ON-PURPOSE` on 2026-08-18, exactly as its
own verdict rule defined it:

> `B4a` PASSES and `B4b` FAILS as pre-registered. THE COMPOSITE/INIT ROUTE IS
> PROVEN FOR BEAT 08.

- **B4a — board down, grips survive** — PASS, and better than survive: the cloak
  came back as continuous brown cloth with plausible folds and the fist as a drawn
  fist with knuckles.
- **B4b — point gesture** — FAIL, pre-registered as an expected FAIL. `0.30`
  finishes what the init contains and does not originate a limb.
- B1, B2, B3, B5 — all PASS, measured: mean |diff| **10.61 inside** the mask,
  **0.04 outside**, only **231 px** of the untouched 80% of the frame differing by
  more than 8 levels.

Its `what_this_settles` named the remaining gap in one line — *"SOURCING AN ARM.
Not the plate, not the compositor, not the denoise strength"* — and
`composite-init-pattern.md` §9b named two candidate levers:

> Beat 08's staging needs a redrawn arm — **pose-conditioned generation, or a
> plate campaign that stages the point** — and no further composite of this plate.

Tonight's job was to read the ControlNet probe, decide between those two, and fire
at most one sample.

## 2. The probe: it ran, it was stranded for two days, and it PASSES

**The repo's record was wrong.** `pipeline/jobs/ep2-cnet-probe-0817.yaml` carried no
outcome block, two commits said it was deliberately held back
(`4d41a7f6`, `88f9a743`), the driver commit said *"Not run yet"*, all five
`C:\banyan-queue\*` directories are empty, `autofill.json` reads `backlog_empty`,
and a repo-wide `find` for `*cnet*` returned exactly two files — the spec and a
research note. Every repo-side signal says it never fired.

**The box says otherwise.** `C:\banyan-farm\cnet-probe-0817\out\` holds all four
arms and all four sidecars, written **2026-08-17 12:39–12:41Z**. They are now
pulled and published to `farm-out/ep2-cnet-probe-0817/` with a sha256 manifest
computed on the pulled bytes.

**Why nobody knew, and it is a process defect worth fixing:** *this spec has no
publish step.* It declares `artifacts:` under `C:\banyan-farm\cnet-probe-0817\out\`
and nothing ever copies them to `C:\banyan-farm\courier-box\farm-out\`, which is the
only path by which a box result reaches this tree. `box_enqueue.output_path_problems`
checks that declared artifacts are *named* by some step; it does not check that any
step *couriers* them off the box. **Named, not built:** a queue-time warning for a
GPU job with no courier destination would have saved two days here.

**Scored against its own bar, which was written in code before any pixels existed**
(`A_LO, A_HI = 0.85, 1.15`; `BIND_MIN = 1.25`), by running the probe's own
`--measure` on CPU at $0:

| arm | `bind_ratio` | bar | |
|---|---|---|---|
| `nocontrol` | **1.012** | must be in [0.85, 1.15] | metric sane, not void |
| `left` | **35.363** | > 1.25 | PASS, 28× the bar |
| `right` | **21.530** | > 1.25 | PASS, 17× the bar |
| `polarity` | 0.999 | — | white-on-black confirmed |

**And the pixels were opened, because a metric agreeing with me is not a sample**
(`farm-out/ep2-cnet-probe-0817/EVIDENCE-cnet-binds-0819.png`). Both control arms
draw a green two-leaf seedling whose stem line, leaf splay and horizontal position
trace the authored stroke. Mirroring the hint moves the plant with it. The
uncontrolled arm, at the same seed and the same prompt, puts a seedling somewhere
else entirely inside a full illustrated scene. **The hint decides the drawing.**

So the crosswalk's own closing caveat — *"What is NOT established by any of the
above: that the condition BINDS"* — is now settled affirmatively, and the licence
position is clean: base is OpenRAIL++-M, the scribble net is Apache-2.0 with no
attribution condition, and the hints are drawn by `author_scribble.py` with PIL, so
the `lllyasviel/Annotators` landmine is never touched.

**One thing observed and deliberately not scored:** at `conditioning_scale 0.8` with
a sparse hint, the condition does not merely place the subject — **it flattens the
whole frame.** Both control arms lost the environment the uncontrolled arm invented.
That is a feature when the goal is to pin a composition, and a defect when the goal
is to change one region of an existing picture.

## 3. Why no b08 arm sample was filed anyway

The ruled sample was: take the signed board-lowered composite as init, condition a
pointing arm onto it, carry B1–B5 with B4b now expected to PASS.

**I opened the init at full size before designing anything, as
`composite-init-pattern.md` §10 step 4 requires. It cannot host that gesture.**

`farm-out/ep2-b08-boardcomp-0818/08-boardlowered-comp-0818.png`, 832×1216,
sha256 `487ef4e8…`:

1. **Both of the guard's hands are on the board.** `HAND_L` (545,505)-(645,618) and
   `HAND_R` (693,505)-(793,618), one at each lower corner of the clipboard, fingers
   curled over its front face. Visible, not inferred.
2. **A pointing finger requires a hand that is not holding something.** Adding an
   extended arm while both hands stay gripped draws a **third arm** — and
   `extra arms` is in this beat's own negative prompt.
3. **So B4a's success is what forecloses B4b on this init.** The clause the sample
   existed to protect — *"both hands still grip its edges"* — is the same fact that
   makes the gesture unreachable. That is not a defect in the sample; it is the
   sample telling us the ask was mis-shaped.

This sits *on top of* §9b's three already-published blockers, each fatal alone and
all three re-confirmed by eye tonight: no pointing hand exists in the plate (the
near hand is a four-finger back-of-hand grip, and no rotation of a curled fist is a
point); no forearm exists to move (the near arm is under the cloak and the cream
under-robe, ~230 px of reach required between `HAND_L`'s edge and the goblin's belly
at (315, 588)); and the path is occupied (the goblin's own green fist,
x 355–475 / y 585–700, sits dead centre of the gap — I cropped it and it fills
almost the entire span between his belt and the guard's robe).

**Conditioning does not solve any of those.** The probe proves a hint controls what
the model *draws*; it says nothing about a hint persuading a checkpoint to give an
existing figure a limb it does not have, inside a mask, at low strength, matching
that figure's cloak and lineart. Filing that as "one sample" would have meant
shipping two pieces of code nobody has run — there is **no driver in this tree that
pairs a ControlNet with a mask** (every driver is inpaint-without-control or
control-without-inpaint), and **no hint tool that can draw an arm**
(`author_scribble.py` draws exactly two hardcoded shapes, a stem and lens leaves).
Two unproven mechanisms plus a fourth structural blocker is not a sample, it is a
guess with a GPU attached.

**An empty queue on an honest "no ruled route yet" is the correct outcome here, and
this is the reasoning that makes it honest rather than tired.**

## 4. What remains, with what is now known about each

### Route A — a plate campaign that stages the point *(the live one)*

Generate a **new two-figure plate in which the guard is already pointing** — one
hand on the board at his waist, the other extended toward the goblin's belly. This
is the only route that resolves the two-hands problem, because the pointing hand has
to be drawn by something that knows it is a hand, not inked in as geometry.

Now cheaper than it was yesterday, because of §2: a hand-authored hint can pin the
composition that free-running text2img has never produced, and **it needs no new
driver at all** — `controlnet_probe.py` already runs text2img + control, and the
frame-flattening observed there is a *feature* for this use. What it still needs:

- **A hint that can draw two standing figures**, a board at waist height, and one
  extended arm. `author_scribble.py` cannot; its two shapes are hardcoded.
  `pipeline/attribute_mask.py` already has the right primitive grammar
  (`band:` is documented as *"a thick line segment — a bridge, a temple arm"*, plus
  `ellipse:`, `quad:`, `ring:`, `box:`) and would need a way to emit a hint PNG
  rather than a mask. That is the smallest piece of new code on the table.
- **Re-clearing B1, B2, B3 and B5**, which the current init already passes. A new
  plate puts the ground plane, the guard's adulthood, the goblin's identity and the
  scale relationship back in play. That is the real cost of this route and it should
  be stated before it is started, not after.
- The standing constraint that beat 08's `done_when` wants **three figures** and the
  only passing plate we have holds **two** is untouched by any of this.

### Route B — ControlNet + masked inpaint *(needs its own probe first)*

Only worth opening if Route A's plate campaign stalls. It would need a driver that
does not exist, and the frame-flattening in §2 is precisely the failure that would
show up outside the mask. **It is a separate one-sample question with its own bar**,
and it must not be smuggled in as an implementation detail of a beat-08 job.

### Route C — further compositing of this plate *(closed)*

`composite-init-pattern.md` §9b already ran the cut-and-rotate attempt and rejected
it on pixels (`EVIDENCE-arm-attempt-rejected.png`: it pasted a rotated crop
containing a *second clipboard* onto the goblin's chest). Inking a `band:` from the
guard's shoulder to the belly fails the same way for a new reason — it would cross
the lowered board, emerge from no shoulder, and still leave both hands gripped.
**A compositor cannot manufacture a limb the plate never drew, and it certainly
cannot free a hand that is drawn holding something.**

## 5. What was actually done tonight

- Read the probe's spec, driver, queue state and box working directory. **Found the
  outputs stranded on the box** and pulled them.
- Scored them with the probe's own pre-registered metric ($0, CPU) — **PASS**, and
  opened the four renders side by side.
- Published them to `farm-out/ep2-cnet-probe-0817/` with a sha manifest, built
  `EVIDENCE-cnet-binds-0819.png`, and appended a verdict to the spec **without
  editing its bar**.
- Opened the beat-08 composite at full size and **rejected the ruled sample on the
  init rather than on a metric.**
- **Filed nothing. Queued nothing. Spent nothing.**

Two things for whoever picks this up: the courier-step gap in §2 is a real
`box_enqueue` warning waiting to be written, and Route A's hint tool is the smallest
piece of new code that would move beat 08 at all.

---

## 6. Addendum, same night — a sibling lane is already asking the harder half

Written after the fact: while this was being drafted, another lane filed
`pipeline/jobs/ep2-b07-point-motion-0819.yaml` (`bdee2b70`) against **beat 07**, and
it bears directly on everything above.

- It found beat 07 a two-figure plate that clears both the count and the cast clause
  (`ep2-b07-twofig-0817` r1-s3, 1 frame of 24) — **a guard and a goblin, and no board
  anywhere**, so neither of the guard's hands is committed. That is precisely the
  property §3 above finds missing from beat 08's init.
- It asks the question this document could not: **does a pointing gesture bind to the
  GUARD once both figures are fixed by an init?** — in **i2v**, on the engine that
  renders whole-body motion, rather than in a still generator.
- And it reports the result that most constrains Route A: **in text-to-image the point
  attached to the goblin 3 of 3.** Twelve tries could not aim it.

**Three consequences for the routes above, and none of them is a retraction.**

1. **There is a fourth route, and it is already running:** let the motion engine stage
   the point from a board-free two-figure init. Beat 08 would then need a plate without
   the board in the guard's hands — which is the same staging campaign Route A names,
   arrived at from the other side.
2. **Route A's risk is now quantified.** The 3-of-3 misattachment is the BROADCAST class
   `attribute_mask.py`'s own header documents: CLIP's causal encoder puts an attribute
   named anywhere into the pooled embedding, so "pointing" lands on whichever figure the
   sampler likes. **A wording cannot aim it.** This is an argument *for* the ControlNet
   version of Route A rather than against it — geometry is per-location, so a hint is one
   of the few levers that can say *which* figure grows the arm. It is the strongest
   reason yet to build the two-figure hint tool named above.
3. **Do not duplicate the beat-07 sample.** If the point binds to the guard in i2v there,
   beat 08's answer is a plate change and not a conditioning problem at all, and this
   document's Route A should be re-scoped before anything is filed against it. **Read
   that job's verdict before opening beat 08 again.**

---

## 7. Route A was built and fired the next morning — and it aims the gesture

Appended 2026-08-19 by the lane that picked this up. Both loose ends §5 left are
now closed, and Route A has its first sample: `ep2-b08-cnetplate-0819`
(evidence: `farm-out/ep2-b08-cnetplate-0819/EVIDENCE-b08-cnetplate-0819.png`).

**The courier gap in §2 is now a refusal, not a warning.** `box_enqueue.
courier_problems` blocks any spec whose declared artifacts live outside
`courier-box\farm-out` unless some step actually writes into it — a copy verb
beside the path, or an `--out` that lands there. *Mentioning* the path does not
count, and that is asserted. Blast radius measured across all 962 specs that
declare artifacts: 100 refusals, 97 of them from the pre-courier era
(ep1, and ep2 dated 0811–0812) — from the whole current era it fires on exactly
one spec, `ep2-cnet-probe-0817`, which is the incident.

**The hint tool exists and it draws people.** `author_b08_pose_hint.py`, PIL
only, contours rather than a stick figure, with the arm solved by the two-link
triangle from a fixed fingertip clearance so both failure modes refuse — too far
apart raises on a stretched limb, too close on a folded elbow. Every clause of
the bar a picture can carry is asserted in its `--selftest` before any pixels.

**The result, in one line: THE HINT AIMS THE GESTURE, AND DOES NOTHING FOR
IDENTITY.** Scored against a bar pre-registered in the spec:

- **B4c — the pointing arm grew from the GUARD.** First time on this beat. Not
  luck: the nocontrol arm at the *same seed and the same words* put it on the
  goblin, making the uncontrolled tally 4 of 4.
- **B5 — the colossus was removed by geometry in one shot.** The control frame
  is the most extreme colossus this beat has produced (one goblin filling the
  frame, the other at about an eighth his height) and it also bound the guard's
  *frozen wardrobe* — cream shirt, white sash, brown wrap skirt — onto the
  goblin. §6.2's BROADCAST class, caught in the open.
- **B1, B3, B4a — pass.** Two whole figures, one ground plane, and a clipboard
  legibly lowered at the guard's hip in one hand, reached in a single generation
  rather than by compositing.
- **B2 — FAIL, and it was named in advance as the clause geometry cannot carry.**
  Both figures came back green with pointed ears; the two heads measure (33,78,49)
  and (31,72,49), indistinguishable. **A contour cannot say which body an
  attribute belongs to**, so `green skin` went to both. Anyone building on this
  takes the composition from the hint and must still solve identity elsewhere.
- **B4b — FAIL.** The arm is aimed but ends in nothing: the fingertip region
  samples background. A gesture with no hand on the end of it is not a point.

**Two things the next lane should not have to rediscover.** First, at
conditioning scale 0.8 a dense full-body contour is **traced, not interpreted** —
both figures returned as flat mannequins with the authored polygon silhouettes,
while the grass and sky around them are detailed and fine. That inverts §2's
observation rather than repeating it: with a sparse hint the *environment*
flattened; with a dense one the flattening lands on the *conditioned regions*.
Second, the frame is NIGHT (mean luma 22.9 against the control's 95.1) because
the negative was assembled from `ep2-b08-boardcomp-0818` — written for an inpaint
over an already-daylit init, so it never needed `no dark, no night`, which beat
08's own cast draft does carry. That is an authoring error, not a ControlNet
behaviour, and the negative measured 76 of 77 tokens so there was no room to
notice.

**The next rung is named and deliberately not taken:** same hint, same seed,
`dark, night` restored to the negative, at a LOWER conditioning scale (0.4–0.5)
and/or a thinner stroke — does the hint keep B3, B4a, B4c and B5 while giving the
checkpoint back enough freedom to draw people instead of polygons? One sample,
its own bar. **Route B (ControlNet + mask) is if anything less attractive now**:
the tracing above is exactly what would appear inside a mask.

---

## 8. The conditioning-scale axis is closed — bracketed on both sides (2026-08-19)

Three rungs, one hint file, one seed, one prompt; only the scale moved.

| scale | staging (B1/B3/B4a/B4c/B5) | the figures themselves |
|---|---|---|
| **0.80** | HELD | **traced** — flat mannequins in the authored polygons, no hand, no face, no cloth |
| **0.45** | HELD | **surface returned, outline not** — a hand with an index finger, two faces, cloth with folds, shading; silhouettes still the polygons |
| **0.28** | **LOST** — colossus, point on the goblin, guard wardrobe on the goblin, board on a background figure | drawn beautifully, because the condition is no longer shaping anything |

**There is no value that yields both, and the failure between 0.45 and 0.28 is
not a gradual softening — it is a collapse back to the uncontrolled
composition.** 0.45 is the best point on the axis and interpolating is not worth
a rung.

**What that means for the tool I wrote at the top of this document:** a DENSE
FULL-BODY CONTOUR cannot be tuned into a composition guide on this checkpoint,
because its ink *is* the drawing — any strength that lets the model redraw the
outline also lets it redraw the staging. **The next instrument is a change of
hint SHAPE, not of strength**: a sparse skeleton marking joints and the board
rather than enclosing bodies, a much thinner stroke (this hint is 7px; the
xinsir card calls stroke weight the second dial), or an early
`control_guidance_end` that pins composition in the first denoising steps and
releases before the detail passes. One sample each, same bar. None filed.

**Do not quote `controlnet_probe.py --measure` on this hint.** Its `bind_ratio`
is VOID here by the probe's own pre-registered rule: the *nocontrol* frame
scores 1.498, outside the [0.85, 1.15] kill-switch band for an unconditioned
arm. The metric assumes a sparse off-centre hint whose strokes sit where the
model would not otherwise put structure; this hint's strokes enclose two
standing figures in the middle of the frame, which is exactly where any
two-figure image has its edges. Every verdict in §7 and §8 rests on pixels.

**Rung 1's finding is untouched and still the reason to keep going:** a
hand-authored hint DOES aim the gesture, and it remains the only mechanism that
has ever put this beat's pointing arm on the guard.

**And identity is now the beat's other blocker, untouched by any of the above.**
Three rungs at three scales all returned two green figures — at 0.28 the guard's
frozen wardrobe came back complete and well drawn *on the goblin*. A contour
cannot say which body an attribute belongs to. Per-figure IPAdapter is the
candidate and it is its own probe. **Take the hint shape first**: an identity
lever has nothing to attach to on a figure whose outline is not the model's own.

---

## 9. Stroke weight was the wrong dial, and it points the wrong way (2026-08-19)

§8 named three instruments and called stroke weight one of them, on the xinsir
card's authority. `ep2-b08-cnetplate-r4-0819` took it: the same hint re-drawn at
`--stroke 3`, at the bracketed-best scale **0.45**, same seed, same fixed
negative, driver byte-identical. Zero new code — the flag existed and its
`--selftest` already asserted it as a dial.

**The hint was one variable, and that is measured rather than intended:** every
landmark unmoved (both cx, both statures, the shared foot line y=1149.1, the
shoulder→elbow→wrist→fingertip chain, the 26.8px torso clearance, the board), and
**24684 of 24685 lit pixels in the 3px hint lie inside the 7px hint's ink** — the
same centrelines, 42% of the pixels. It was opened at full size and at 1:1 before
filing (`EVIDENCE-b08-thinhint-0819.png`).

| dial | value | staging | the figures |
|---|---|---|---|
| scale | 0.80 / 0.45 / 0.28 | HELD / HELD / **LOST** | traced / surface-only / drawn-but-uncontrolled |
| **stroke** | **7px → 3px @ 0.45** | **HELD** | **still the authored polygons, and the hand got worse** |

**THE THIN HINT IS TRACED MORE TIGHTLY THAN THE THICK ONE.** Share of authored
ink with a strong render gradient within 3px, identical instrument on all four
frames, nocontrol as the coincidence floor:

| frame | ink traced | strongest gradients on ink |
|---|---|---|
| nocontrol | 26.1% | 7.8% |
| rung1 0.80 / 7px | 97.7% | 22.7% |
| rung2 0.45 / 7px | 94.4% | 35.1% |
| **rung4 0.45 / 3px** | **98.3%** | **83.4%** |

**So stroke weight is not a strength dial, it is a PRECISION dial, and its sign
is the opposite of the assumption that listed it.** A 7px bar is an ambiguous
ribbon — the model may put the edge anywhere inside the band, and rung 1 filling
that band is exactly what "flat mannequin" meant. A 3px line is a single
unambiguous edge locus, so the outline snaps onto it. Thinning does not hand
authority back; **it sharpens the instruction.**

Scored against the carried bar: **B1, B3, B4a, B4c, B5 PASS** — the pose and the
guard's arm survive a 58% ink cut, which is the fourth confirmation of rung 1's
one durable finding. **B2 FAILS a fourth time** as pre-registered. **B6 fails its
negative test again with no movement at all.** And **B4b REGRESSES against its
own parent rung**: at 1:1 the arm ends in a fingerless wedge where rung 2 drew a
hand with an extended index finger — the 1px finger stroke was named as the
faintest mark in the drawing before the render, and it did not carry.

**What is now settled, by two bracketed dials rather than by argument: the
TRACING IS CAUSED BY THE ENCLOSURE.** A closed contour around a body is an
instruction about where that body's edge goes, and there is no strength or weight
at which it stops being one. **Two of §8's three candidates are therefore no
longer equals.** A **sparse skeleton** — joint dots and single-line limbs plus
the board, no closed contour anywhere — is the ruled next instrument, because it
is the only candidate that attacks the property just shown to be causal, and
because `author_b08_pose_hint.py` already solves the pose geometry and would need
a draw mode rather than new maths. An **early `control_guidance_end`** is the
fallback and needs code first: `controlnet_plate.py` hardcodes it to 1.0 at lines
167 and 277 and exposes no flag. One sample, same bar, and **whatever the class,
B4b needs a hand-sized mark at the end of the arm** — a 1px finger has now failed
once. **No fifth stroke value**; the dial is measured and points the wrong way.

Identity is unchanged: four rungs, two dials, four pairs of green figures. Take
the hint shape first.

---

## 10. The net was a scribble net all along — the hint-authoring line is closed (2026-08-19)

§9 ruled the sparse skeleton the next instrument. `ep2-b08-cnetplate-r5-0819`
took it: `--skeleton`, joint dots and single-line bones, **no closed contour on
either body**, at rung 2's own scale and stroke (0.45 / 7px) so the hint's
**class is the only variable in the job.**

The claim was asserted in code before any pixels: geometry compares equal key for
key against the contour hint, and non-enclosure is proved by flood fill from a
mid-torso seed checked off-ink in both classes — the contour traps it (guard
18007 px, goblin 11247 px, single closed cells), the skeleton lets it reach the
frame border on both figures. The board stays a closed rectangle on purpose.

**Every composition clause failed.** B1, B3, B4a, B4b, **B4c**, B5 — an extreme
colossus, no guard, no board, no point, and a thumbs-up where the gesture should
be. B2 failed a fifth time. B6 "passes" and the pass is worthless, exactly as at
0.28.

**But the frame did something branch 2 did not predict: it DREW THE CONDITION.**
Cropping render and hint at identical pixel columns puts the authored strokes on
top of glowing scene objects — the shoulder bar and its two joint dots became a
luminous cross with two orbs on each figure's chest, and the leg bones became a
glowing slab. Guard spine column: luma **212.3 against a 165.4 surround (+47.0)**;
goblin spine column **218.2 against 186.0 (+32.2)**.

*Reported against myself:* averaged over **all** the ink, brightness enrichment is
1.4–1.7x — indistinguishable from the nocontrol floor — so the blanket claim "the
skeleton was rendered as light" is not supported and is not made. The effect is
localised to the strokes that landed inside a figure; the rest were ignored.

**Why, and it reframes all five rungs: `xinsir/controlnet-scribble-sdxl-1.0` is a
SCRIBBLE net.** Scribble conditioning means one thing — *these lines are lines in
the picture*. A closed contour is interpretable that way, because it is an object
boundary; that is why rungs 1, 2 and 4 held the staging and traced the silhouette,
and why a **thinner** stroke bound **tighter**. A medial-axis skeleton is not a
boundary and means nothing to this net, so it did the only thing a scribble net
can do with ink: it drew it. **The enclosure was never a quirk to tune away — it
was the only thing this net could read.** Four rungs of scale and stroke were
asking a scribble net to do pose conditioning.

| axis | values bracketed | result |
|---|---|---|
| conditioning scale | 0.80 / 0.45 / 0.28 | staging HELD / HELD / LOST |
| stroke weight | 7px / 3px @ 0.45 | staging HELD both; thin traced **tighter** |
| **hint class** | **contour / skeleton** | **contour traces, skeleton is drawn** |

**Three axes, fully characterised: any hint this net can read is a hint it traces,
and any hint it cannot read it ignores or draws. There is no setting that yields a
model-drawn figure inside an authored composition.** Hand-authored geometry is
closed as a composition lever for beat 08 **on this net**.

**What survives, and it is not retracted:** a hand-authored *contour* aims the
gesture, and **rung 2 (0.45, 7px) remains the best frame this beat has produced.**

**The next instrument is a different NET, and it is a research question first.** A
pose skeleton is the right *instruction* and the wrong *net*; what reads one is an
OpenPose/DWPose ControlNet. Before any spec, and per the research-before-solving
directive, that needs answering **outside this repo**: does an SDXL-compatible
openpose controlnet exist, can its weights reach a box running `HF_HUB_OFFLINE`,
what is its licence, and — critically — **is its preprocessor the
`lllyasviel/Annotators` landmine this route has avoided by drawing hints with
PIL?** A hand-authored skeleton needs no annotator, which is the one genuinely
valuable thing rung 5 leaves behind. Nothing is filed until that research is in.

**Identity stays parked, but its reason has changed.** The order was "hint shape
first, because an identity lever has nothing to attach to on a figure whose
outline is not the model's own." That reason is now spent — the axis is closed and
no outline was freed. Identity is no longer *blocked*; it is simply the next open
question, beside Route A's plate campaign, and whoever takes it should know that
geometric conditioning on this net will not help.

---

## 11. Identity binds — the blocker five rungs could not reach fell to a mask (2026-08-19)

§10 left identity as "no longer *blocked*; simply the next open question", and
warned that geometric conditioning on this net would not help it. Both halves of
that turned out to be right. `ep2-b08-ipamask-0819` took the question with the
mechanism the external research had already verified, and it worked on the first
sample (evidence:
`farm-out/ep2-b08-ipamask-0819/EVIDENCE-b08-ipamask-0819.png`).

**One variable.** Rung 2 — this beat's best frame — plus two masked identity
references. Same hint bytes (`19cfad48…`), same seed 20260819, same conditioning
scale 0.45, same prompt and negative *word for word* including the broadcasting
`green skin`, same base, same net, same driver. Added: `--ip-ref` ×2,
`--ip-mask` ×2, `--ip-scale 0.7`. Keeping the wording was the point — the claim
was that a **mask can aim an attribute a wording cannot**, and rewriting the
words would have made the result unattributable.

**B2 was stated as a number before the pixels, and the band was measured rather
than chosen.** Instrument: mean RGB over the central-50% box of each head as the
hint places it, statistic `G − R`. Every head this beat ever judged green scored
≥ +20.1 across six rungs; every head judged human-skinned scored ≤ −21.1; 41
empty levels between the classes. So the bar was guard ≤ 0.0 and separation
≥ +20.0.

| | guard head `G−R` | goblin head `G−R` | separation |
|---|---|---|---|
| rung 2 (no adapter) | **+34.0** | +29.4 | **−4.6** |
| **rung A (masked refs)** | **−14.5** | +28.5 | **+43.0** |

**And the pixels agree, which is the actual verdict.** At 1:1 rung 2's guard is a
green featureless egg with pointed ears, closed eyes and no nose. Rung A's guard
is a bald **human** man — pale skin, brows, open eyes, nose, mouth — in his own
brown cloak with his own gold clasp and **a white sash at his waist**, holding
the board at his hip, beside a green goblin whose pointed ears got *longer*. The
mask held each identity in place instead of averaging the two, which is the thing
an unmasked adapter would have got wrong.

**Every staging clause the hint bought survived.** B1, B3 (foot lines y=1151 and
y=1152, one pixel apart, against the authored 1149.1), B4a (the board survived a
mask whose bottom edge stops one pixel above it), B4c (the arm still grows from
the guard, and is now visibly a human arm in a sleeve), B5 (statures 816/729,
ratio 1.119 against 1.100 asked). **The two mechanisms compose; they do not
compete** — that was the pre-registered risk and it did not fire.

**What this reframes about rungs 1–5.** Identity was never a conditioning
problem, so no value of scale or stroke could ever have reached it. Four rungs
spent bracketing dials were asking geometry to carry a clause geometry cannot
express, and the axes they closed are still closed — they were just not the axis
B2 lived on.

### The one clause that regressed, and it hands the next rung its reason

**B4b — the aim — got worse, and the cause is the hint, measured.** The
legibility half improved: the arm now ends in a properly modelled human hand with
a distinct index finger where rung 2 drew a green one. The aim half failed: that
finger hangs almost straight **down**, so the gesture reads as an arm held out
with the hand drooping.

That is not the adapter. **This contour aims with a separate 1 px finger stroke,
which leaves its forearm free to bend — extend its own elbow→wrist segment and it
passes 29.1 px wide of the navel.** The arm the hint actually asks for *is*
"horizontal upper arm, forearm down". Rung A simply drew what was asked for,
well.

### Three costs to price in, observed and not scored

1. **The guard's ears are still pointed.** Skin, face and wardrobe are human; the
   ears are not, and `pointed ears` is nowhere in the prompt. A residual broadcast
   from the checkpoint's own goblin association, and now the sharpest identity
   defect left.
2. **A green halo around the goblin**, inside his own mask, and his eyes came back
   as blank white slits where the reference has pupils. Mask-region artifacts; the
   first things a lower `--ip-scale` would be expected to reduce.
3. **The frame darkened 36 levels** — mean luma 115.7 against rung 2's 151.6 at
   the same seed and the same negative (which carries `dark, night`). Per-region
   image conditioning costs some exposure. Dusk-hazy, not night, and it failed no
   clause — but unlike rung 1's darkness this is a *cost*, not an authoring error.

*Reported against myself:* B6 (drawn, not traced) looks **better** than rung 2's
PARTIAL — the guard's cloak drapes and his outline is a cloaked man rather than
the authored polygon. I did **not** run rung 4's ink-on-edge instrument on it, so
that is an eye call and is **not** a claim that the adapter beat the enclosure.
The plausible mechanism is that `plus` carries structure from a standing, cloaked
reference; that is a hypothesis for a later rung.

## 12. The pose net is on the box, and two independent findings now license its sample

`ep2-b08-posenet-fetch-0819` **PASSED** at 08:00Z: `xinsir/controlnet-openpose-sdxl-1.0`,
`config.json` 1,235 bytes and `diffusion_pytorch_model.safetensors`
2,502,139,104 bytes, both exact, zero `.incomplete`, 3 m 25 s, apache-2.0, $0.
`allow_patterns` kept it to 2,386 MiB where a naive pull is ~5,014 MB. It fired
the moment the card was free rather than waiting on rung A, because it was the
only physical dependency on the route.

`pipeline/author_b08_openpose_hint.py` is written and its `--selftest` passes.
It transcribes §2's COCO-18 spec — the 18-colour ramp, the 17-entry `limbSeq`,
limbs at 60 % under full-intensity dots, ratio 3.0 (**24 px limbs, r=12 dots**,
because a 4 px skeleton is a documented ignored-hint trap), missing keypoints
dropping their limbs — and it asserts the trap that limb colours and dot colours
index the **same** ramp **differently**. It draws **no board rectangle and no
ground ticks**, asserted on purpose: a pose net's whole vocabulary is 18
keypoints, and rung 5 already proved that unreadable ink gets *drawn*. **B4a
therefore becomes a prompt-only clause in that sample and must be pre-registered
as at risk.**

The one thing it could not inherit is the arm, and §11's B4b regression is why:
the elbow is solved against a target one **hand** short of the belly and the
wrist placed one forearm along elbow→belly, so **the forearm ray passes 0.1 px
from the navel with no finger keypoint anywhere.** Shoulder, target, total reach
and extension stay identical to the contour hint's, so the sample remains a *net*
comparison.

**The next rung, named and its one design question answered rather than left
open:** run the pose net **BARE** — no IP-Adapter in the same job. Two reasons.
The pose question is "does a skeleton bind at all on animagine", and identity is
now a **solved bolt-on** whose own bar has been met once, so carrying it in would
make a two-variable job out of a one-variable question. If the skeleton binds,
the recipe is skeleton + the two masked references and both halves have already
been proven separately. **What this route no longer needs:** another conditioning
scale, another stroke weight, another contour hint, or any further argument about
identity.

---

## 13. Pose binds — the research's three questions all answered yes, and the aim still fails (2026-08-19)

`ep2-b08-posenet-sample-0819` ran bare on `xinsir/controlnet-openpose-sdxl-1.0` at
scale 1.0 with the COCO-18 skeleton. One variable: **the net.** Same base, seed
20260819, size, steps, guidance, prompt and negative word for word; staging
asserted key for key against the contour hint's own metadata. Evidence:
`farm-out/ep2-b08-posenet-sample-0819/EVIDENCE-b08-posenet-0819.png`.

**B0 read first, because "did nothing" and "never loaded" are different findings:**
the sidecar records the openpose net, `variant: None`, scale 1.0, and no
`ip_adapter` lines. Not void.

### All three of §10's research questions are now DEMONSTRATED

| question | upstream grade before | now |
|---|---|---|
| does pose bind on animagine-xl-3.1? | MAINTAINER (xinsir's anime masonry names no checkpoint) | **PASS** — composition follows the skeleton; shoulder and elbow bind to the pixel |
| do two skeletons give two figures? | **absence** — every xinsir strip is one figure; `#1791` documents limbs connecting between characters | **PASS** — two whole separate figures, no fusion |
| does the stated scale ratio survive? | mechanism argument only | **PASS** — 830/715 px, ratio **1.161** against 1.100 authored, both statures within 4% |

And **B6 passes emphatically for the first time in six rungs** — cloth with real
folds, hair, faces, modelled hands, silhouettes that are the checkpoint's own.
That is precisely what §9's *tracing is caused by the enclosure* finding
predicted, and what no scale or stroke on the scribble net could deliver.
**§10's branch-(3) risk — that hand-authored geometry was closed on this
checkpoint entirely — did not fire.**

### The failure, and it is specific enough to act on

**B4b fails a third time, on a third mechanism — the forearm flipped.** The hint
authored Rsho (512,491) → Relb (360,485) → Rwri (257,657): out horizontally, then
steeply **down** toward the belly at (225,711). The render bound the first limb
exactly and **mirrored the second about the elbow**, putting a hand with a raised
index finger at roughly (320,420) — about 230 px *above* the authored wrist.
Nothing is drawn at the authored wrist at all. **The forearm's length and
attachment bound; its direction did not.**

Two candidate causes, and the cheap one is testable first:

- **(a) our anatomy.** The authored elbow sits at *shoulder height and laterally
  out* — a chicken-wing — and the forearm then has to drop steeply. That is not
  what a person does to point at someone's belly, which is elbow **low and near
  the ribs** with the forearm reaching forward and down.
- **(b) the net's prior** for "pointing = index up" overriding the geometry.

(a) is a change to our own staging and costs one render. **Test (a) first.**

**B4a fails as pre-registered, and the diagnosis is the useful part.** The
board-holding *hand* bound — the authored L-wrist (622,668) lands on the rendered
hand — but what he holds is a small book at his **chest**, not a clipboard at his
hip. **The pose of holding bound; the object did not**, which is exactly what a
hint containing no object should do, and it confirms the pre-registered remedy:
multi-ControlNet, pose for bodies + scribble for the board, both nets local, $0.

**B3 is marginal.** One plane by eye, but the guard's feet sit 35 px below the
goblin's where the hint pins both ankles at ~1122 — rung A held this to *one*
pixel. With no ground ticks (a pose net cannot read them), the clause rests
entirely on two ankle keypoints, and 35 px is what that costs.

### The surprise: B2 passed with no adapter at all

Pre-registered to **fail**. It passed, and by more than rung A managed *with* two
masked references and a ViT-H encoder:

| frame | guard `G−R` | goblin `G−R` | separation | luma |
|---|---|---|---|---|
| rung 2 — contour, scribble 0.45 | +34.0 | +29.4 | −4.6 | 149.5 |
| rung A — contour + 2 masked refs | −14.5 | +28.5 | +43.0 | 115.7 |
| **rung B — skeleton, openpose 1.0, BARE** | **−27.5** | +28.0 | **+55.5** | **32.5** |

**The hypothesis this raises, and it is a hypothesis:** the contour hint may not
only have traced the silhouette — it may have *destroyed the model's ability to
differentiate the two figures*. Two enclosed polygons of near-identical shape got
near-identical fills, five times running. A skeleton leaves each body's surface to
the checkpoint, which then drew the two *different* characters the prompt
describes. If that is right, four rungs of green pairs were an artifact of the
enclosure rather than of CLIP's pooled embedding. **One sample does not promote
that past a hypothesis**, and rung A's mechanism stays measured and available:
the honest reading is that the masked references are now *possibly redundant*,
not proven so.

### Four costs, and the first is severe

1. **THE FRAME IS NIGHT.** Mean luma **32.5**, with `dark, night` *in* the
   negative — the same words that measured 149.5 on the scribble net at 0.45.
   Rung 1's darkness was an authoring error (the clause was missing); this one was
   *overridden*. A dark palm-frond silhouette dominates the left third where the
   prompt asks for tall grass and pale sky. Scale 1.0 is the obvious suspect and
   it is the card's recommended value, so this is a real tension, not a mistake.
2. **The guard reads as a woman** — blonde chin-length hair, soft features — against
   a prompt opening "Two men" and a negative carrying `girl`.
3. **`plump` broadcast onto the GUARD while `green skin` did not.** The guard is
   heavy-set and the goblin slight, the reverse of the wording. So the pooled-embedding
   broadcast is **reduced, not eliminated**, and which attributes escape it is not
   yet predictable.
4. **Both figures are in modern plainclothes.** The brown wrap skirt is the one
   wardrobe clause that landed.

### Where beat 08 actually stands, and the ruled order

**Two mechanisms are proven and the beat's only remaining blocker is the aim** —
which has now failed on three separate mechanisms, each time for a different and
progressively better-understood reason.

**Ruled next, one sample, nothing else changed: RE-STAGE THE ARM.** Elbow low and
near the ribs, forearm reaching forward and down to the belly. Its question is
whether the flip was our anatomy or the net's prior; it needs no new weights, it
is a change to `author_b08_openpose_hint.py`'s staging with its `--selftest`
carried, and it is the cheaper of the two hypotheses.

Then, in this order, each as one sample: **the night** (same hint at scale
0.6–0.7 — does the dark relax while the pose holds); **B4a** via multi-ControlNet
pose+scribble for the board; **whether rung A's masked references are still needed
at all** given B2's surprise here.

**What this route no longer needs:** another scribble-net rung, another stroke
weight, another contour hint, the `_twins` variant (pose *adherence* was never the
failure — forearm *direction* was), or any further argument about whether pose
conditioning works on this checkpoint.

---

## 14. The flip was ours, and the arms now reach for each other (2026-08-19)

§13 ruled one hypothesis testable first. `ep2-b08-posenat-0819` took it with one
variable — the guard's elbow, `solved` → `natural` — and everything else held,
including the **driver byte-identical** to the parent's, so the net, the scale
and the pipeline are provably the same. Evidence:
`farm-out/ep2-b08-posenat-0819/EVIDENCE-b08-posenat-0819.png`.

**THE MIRROR IS GONE, AND BRANCH (2) IS EXCLUDED BY 229 PX.** The predicted
mirror point (665, 581) is empty background. The guard's pale hand measures a
centroid of **(436, 656)** — on the correct side of the elbow, with the forearm
running down-and-left in the authored direction. At 2× the parent's authored-wrist
neighbourhood is empty sky; this frame's has two hands in it. **The forearm flip
was our anatomy, not the net's prior.**

The reason it worked was asserted in code before the render, and it is the
cheapest useful assertion on this route: reflect each forearm about its own elbow
and ask where the hand lands. `solved` mirrored puts it at y=312, **above** the
shoulder — a plausible raised-finger point, which is what the net drew. `natural`
mirrored puts it at y=581, **below** the shoulder, where it reads as nothing. The
fix was not asking harder for the right pose; it was **removing the attractive
wrong answer.**

### And it is still not a point — the obstruction changed identity

The guard's hand reaches only ~60% of the way to the authored wrist, and **the
goblin lifts his own left arm 186 px up and 129 px across, out of its authored
hanging pose** (wrist authored at (221, 857), green fist rendered at (350, 671)),
to meet it. **The two hands clasp in the middle of the gap. Both figures' arms
deviated toward each other.**

This is §9b's *"the path is occupied"* blocker returning at the skeleton level. It
killed the composite route because "the goblin's own green fist sat dead centre of
the gap"; here the net *put it there*, against its own conditioning.

**So the pose net's binding is not rigid.** An authored limb can be overridden when
the checkpoint prefers a different reading of the scene. Nothing before this frame
had shown that, and it is the finding that licenses what comes next.

### B4b's four causes, all distinct

| rung | mechanism | why the point failed |
|---|---|---|
| 1 | contour @ 0.80 | the arm ended in nothing — fingertip sampled background |
| 2 / A | contour @ 0.45 | a good hand, aimed wide **by construction** (forearm ray 29.1 px off the navel) |
| B | skeleton, solved elbow | the forearm **mirrored** — hand 230 px above the authored wrist |
| **B2** | skeleton, natural elbow | **both figures reached for each other and clasped** |

### The enclosure hypothesis survived its first chance to die

| frame | hint class | guard `G−R` | separation | adapter |
|---|---|---|---|---|
| rungs 1, 2, 3, 4, 5 | contour | +34.0 … +44.3 | −4.6 … +5.5 | none |
| rung A | contour | −14.5 | +43.0 | **two masked refs** |
| rung B | skeleton | −27.5 | +55.5 | none |
| **rung B2** | skeleton | **−32.6** | **+83.0** | none |

Two skeleton frames, two passes; five contour frames, five failures — and the
best separation on this beat now belongs to a frame with **no identity mechanism
at all.** That is a pattern rather than a single observation. It is still **not a
controlled test**, and the honest statement is only that the hypothesis has not
died yet.

*And a caution against over-reading any single frame:* **`plump` landed on the
GOBLIN here and on the GUARD in the parent** — two frames differing only in the
guard's elbow, no wording change at all. The residual pooled-embedding broadcast
is not merely reduced, it is **unstable**. Nobody should read one frame's
attribute assignment as evidence about wording.

## 15. `twins` is licensed for the first time, and the order after it is unchanged

Every rung so far declined `diffusion_pytorch_model_twins.safetensors` on one
consistent ground: xinsir describes it as *"similar performance and different
style"* — **more precise pose adherence, lower aesthetic score** — and pose
adherence was never what was failing.

**It is now.** The goblin's arm left its own skeleton by 186 px and the guard's
forearm reached 60% of its authored length. That is precisely and only what twins
claims to fix. One 2,386 MiB download from a repo already cached, an explicit
filename load, apache-2.0, $0.

**One sample**, this exact hint, this exact seed, and its bar is B4b's two halves
as measured here: does the guard's hand reach **(280.5, 695.1)**, and does the
goblin's arm **stay** at (221, 857).

Then, unchanged: **the night** (luma 40.4 with `dark, night` in the negative —
same hint at scale 0.6–0.7), **the board** (multi-ControlNet pose+scribble; the
holding *hand* already binds, only the object is missing), and **whether rung A's
masked references are needed at all** given two adapter-free B2 passes.

**What this route no longer needs:** a scribble-net rung, a stroke weight, a
contour hint, a conditioning-scale bracket on the scribble net, a `hang_deg`
sweep, wider figure separation (the staging is already at 0.847 extension against
a 0.99 ceiling, and buying room re-opens B1 and B5), or any further argument about
whether pose conditioning works on this checkpoint.
