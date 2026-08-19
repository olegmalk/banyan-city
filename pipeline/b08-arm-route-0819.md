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
