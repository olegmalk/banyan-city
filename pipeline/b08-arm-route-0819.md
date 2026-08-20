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

## 16. The board arrives and takes the drawing with it (2026-08-20)

**Two rungs happened between §15 and this one and are filed in their own specs,
not transcribed here.** `ep2-b08-twins-sample-0819` fired the twins net on the
hint §15 licensed: B4b bound, and identity stopped smearing *between* the
figures and started fragmenting *within* them — the guard's forearms green, the
goblin's legs pale. `ep2-b08-twinsipa-0819` fixed that with per-limb capsule
masks and **passed nine of ten pre-registered clauses**: within-figure spread
10.6 (guard) and 0.7 (goblin) against a bar of 25.0, the hand 40.3 px from its
authored wrist, one ground plane at 4 px, and a better drawing than its parent.
The single failing clause was **B4a, the board**, pre-registered to fail because
no object can be expressed in a pose hint. Its verdict named this rung.

**What was asked.** Multi-ControlNet: the twins openpose net at 1.0 on the
byte-identical hint (`562911c8`) that passed, **plus** `xinsir/controlnet-
scribble-sdxl-1.0` at 0.8 on a hint carrying the clipboard and nothing else.
Same capsule masks, same references, same ip-scale, same seed, same words. The
new hint is `pipeline/author_b08_board_hint.py`, whose `--selftest` asserts as
*pixels* that no figure is in it: every lit pixel inside the quad dilated by the
stroke, zero pixels anywhere on the goblin, and the set of guard limbs the ink
meets pinned to exactly `{gripping forearm, torso, left thigh}` — the three a
clipboard at the hip occludes — with his face and pointing arm untouched by
name. Its grip point equals `stage()`'s guard L-wrist **to the float**,
`(621.6704, 668.4352)`.

**The composition worked on the first try.** `multi-controlnet: 2 nets, scales
[1.0, 0.8]`, no crash, no driver bug. Verified read-only against the box's
installed diffusers 0.29.2 *before* the spec was written: `from_pipe` passes a
list through unfiltered (`auto_pipeline.py:401`), `__init__` wraps it into a
`MultiControlNetModel` (`pipeline_controlnet_sd_xl.py:266-267`), scalar guidance
broadcasts across nets (`1222-1232`), and — the one question that could have
crashed it — the ControlNet forward receives `added_cond_kwargs` but **not**
`cross_attention_kwargs` (`1488-1495`), so the masked IP-Adapter reaches only
the UNet and the two nets never see `ip_adapter_masks`.

**Result: FAIL, and the board is the only thing that went right.**

| clause | parent | this rung |
|---|---|---|
| B4a board | absent | **drawn**, authored place and 9° tilt — but **no hand holds it** |
| B6 drawn | improved | **FAIL** — two garments became one flat robe, linework gone |
| B8 hair (canon) | sandy | **FAIL — bald**, matching the bald *reference* |
| B4b-i hand→wrist | 40.3 px | **10.2 px** (better) |
| B4b-ii far arm | on sash | **absent** — swallowed by the robe |
| B7 spread | 10.6 / 0.7 | **UNMEASURABLE** — no luma-matched probe set exists |
| frame mean luma | 141.6 | 86.9, flat ambient → hard directional key |

**The finding, and it is worth the render: a sparse hint is not a weak hint.**
The board hint is 99.7 % black. The intuition that it therefore acts only where
its ink is, is *wrong*. For a scribble net a black pixel is not an absence of
instruction — it is the instruction *"no edge here"* — so a nearly-black hint
asserts **"no edges anywhere"** across the whole frame, at 0.8, for the full
denoise, and its residuals are **added** to the pose net's at 1.0. Everything
observed follows from that one mechanism: detail flattened everywhere, garments
simplified, an arm dropped, the light hardened, and the one place the hint said
*"edge here"* is the one place an object appeared.

**Two instrument notes, both reported rather than buried.** The pre-registered
edge metric for B4a *did not work*: mean gradient in the board region **fell**
(13.36 → 3.68) because the parent's region was full of fine linework and the
child's is a flat board on a flat robe — it measures busyness, and the child is
less busy everywhere. And B7 is UNMEASURABLE by the bar's own admissibility
rule: sweeping for the brightest patch on each region still spans 120.2 luma
levels on the guard, so reporting its raw spread as a fail would repeat exactly
the error `twinsipa`'s verdict documented.

**B8 inverts a parent finding.** `twinsipa` observed that a capsule mask "leaves
attributes the reference does not assert to the prompt" — the wording won and
the guard kept his canon hair. Adding a second net flipped it toward the bald
reference. So that balance is **not** a stable property of capsule masks; it is
a property of the conditioning load, and it moves.

**Next: ONE sample, `--scale2` 0.8 → ~0.3, nothing else changed.** Its bar is
B4a *plus* B6 and B8 restored to parent quality. If 0.3 still damages the frame,
the second lever is a per-net guidance window — an object only needs
establishing early, so net 2 runs `control_guidance` 0.0→~0.3 and stops;
diffusers takes lists there, so it is the same small driver change `--scale2`
was. **The parent remains the best frame on this beat**, and this one is not a
plate candidate: off-canon hair, lost wardrobe, worse drawing.

## 17. Scale was the lever: the board survives at 0.3 and the frame comes back (2026-08-20)

One number, `--scale2` 0.8 → 0.3, everything else byte-identical to §16 — same
two nets, same two hints, same masks, same references, same seed, same words.

**Everything §16 broke came back, and the board stayed.**

| clause | twinsipa (no board) | §16 at 0.8 | §17 at 0.3 |
|---|---|---|---|
| B4a board | absent | drawn, **no arm** | **drawn, arm reaches it** |
| B6 drawing | good | flat robe, **FAIL** | **PASS**, at twinsipa's level |
| B8 hair (canon) | sandy | **bald, FAIL** | **sandy, PASS** |
| B7 guard / goblin | 10.6 / 0.7 | UNMEASURABLE | **21.7 / 8.1, PASS** |
| B2 separation | +42.0 | +77.7 (unscorable) | **+60.6** |
| B4b hand→wrist | 41.5 px | 10.2 px | **48.5 px** |
| B4b far arm | on sash | **absent** | **present, reaches board** |
| frame mean luma | 141.6 | 86.9 | **135.4** |

**What this settles.** The damage at 0.8 was *proportional to strength*, not
intrinsic to composing two nets. The per-net guidance window — the second lever
§16 named — is **not needed**; scale was the lever. And **B8 is now an
instrument**: with the wording byte-identical across all three frames, the
guard's hair goes bald at 1.0+0.8 and returns at 1.0+0.3, so it reads
conditioning load for free.

**The one clause still short is the HAND.** At 5x the sleeve ends in a rounded
mitten-like form and the board's top edge tucks under it — no fingers, no thumb,
no grip. The beat asks for a clipboard *lowered in one hand*; what is drawn is a
board carried at the end of a sleeve. Much better than §16's satchel hanging off
a vanished arm, and **not yet the picture** — so this frame is deliberately
**not** called a complete plate candidate.

**A second instrument finding, and it nearly produced a false FAIL: published
probe boxes do not transfer between frames on this beat.** Scored at twinsipa's
six coordinates this frame reads goblin spread 41.5 — a fail. Drawing the boxes
onto the image shows why: **the goblin is wearing trousers in this frame**, so
his "shin" and "forearm" boxes are on *cloth*, and the guard's "forearm" box is
on his *sleeve*. Luma-matching those boxes to 0.3 levels still gave 50.6 —
**luma-matching does not rescue a probe on the wrong material.** The bar's
"placed ON THE DRAWN LIMB" requirement does separate work from its luma
requirement, and this frame is the proof. Re-placed on pure skin (≥97 %
skin-coloured windows, coordinates published in the verdict) both figures pass
comfortably. Every future B7 must publish the **material** as well as the luma.

**Next: ONE sample, the grip, by wording first.** `--scale2` stays at 0.3 and
both hints stay byte-identical; the prompt already says `clipboard lowered in
one hand`, so the change is to make the grip explicit and nothing else — a
wording rung whose risk is the token budget (64 of 77 used). Only if that fails
does the board hint get a stroke for the gripping hand, and that would be the
first figure ink ever placed in it and must be argued against the five tracing
losses rather than slipped in.

## 18. Nine words bought a grip and paid for it with the clipboard (2026-08-20)

One variable, the positive prompt, +9 words: `clipboard lowered in one hand,`
gained `fingers and thumb gripping the clipboard edge,`. Every conditioning
input byte-identical and verified in the sidecar — both nets, both hints, both
capsule masks, both references, `--scale` 1.0, `--scale2` 0.3, seed 20260819,
negative unchanged. Budget measured on animagine's own vocab: 64 → **73 of 77**.

| clause | twinsipa | §16 at 0.8 | §17 at 0.3 | §18 at 0.3 + 9 words |
|---|---|---|---|---|
| B4a board | absent | drawn, no arm | **drawn, arm reaches it** | **ABSENT** |
| quad px < luma 80 | — | — | 0.758 | **0.235** |
| B4b grip | — | — | mitten, no digits | **fingers + thumb, on the SASH** |
| B8 hair (canon) | sandy | bald | sandy | **BALD** |
| B7 guard / goblin | 10.6 / 0.7 | unmeasurable | 21.7 / 8.1 | **3.8 / 11.1 spread, PASS** |
| B2 separation | +42.0 | +77.7 | +60.6 | **+54.4** |
| B4b hand→wrist | 41.5 px | 10.2 px | 48.5 px | **41.2 px** |
| frame mean luma | 141.6 | 86.9 | 135.4 | **127.3** |

**Two pre-registered branches fired at once, and one fired harder than it was
written.** Branch (5) was written for a board that *degrades*; what arrived is a
board that is *gone* — the authored quad holds the wrap skirt, the grass and the
gold belt clasp, and no board appears anywhere else in the frame. Branch (4) —
prompt crowding — is confirmed by the hair: at identical conditioning, with
`light sandy hair` in both prompts, the parent came back sandy and this frame
came back bald.

**The diagnostic half, and it is why the frame was worth rendering: the grip
clause worked as a SUMMONS and failed as a BINDING.** Fingers and a thumb are
drawn, separated and articulated at 4x, on the correct far hand — and closed
around the diagonal **sash strap** at his chest, which is where that hand
already was in §17. The words reached the right hand and the wrong object.
Repeating the noun `clipboard` was chosen to bind the digits to the object and
instead the render resolved the ambiguity toward the object already under the
hand. The pre-registered duplication risk did not fire: boards in frame, zero.

**§17's headline needs one word changed.** `--scale2` 0.3 is not *robust*, it is
**prompt-coupled**: it carried the board for exactly the 64-token text it was
measured against and did not carry it for nine more words at the same strength.
Every future beat-08 prompt edit re-verifies the board rather than assuming it.

**The B8 instrument has two inputs, not one.** It was calibrated on conditioning
load (bald at 1.0+0.8, sandy at 1.0+0.3). It moved here with conditioning fixed
and only the token count changed. A bald guard on this beat now reads
"over-conditioned **or** over-crowded", told apart by which one moved.

**An admissibility extension §17's rule does not cover.** §17 established that a
probe box must publish its *material*. This frame establishes that **on the
guard, colour alone cannot decide that material**: his cream shirt measures
R−B 34.7 against his skin's 42.6–49.7, and the first probe placed here by a
colour predicate landed on a **sleeve** at 100 % "pale". Guard probes are placed
by eye at 5x and published with their R−B; the goblin's green needs no such care
(100 % on all three boxes).

**Next: ONE sample, and the variable is `--scale2`, with this frame's wording
held byte-identical.** The open question is whether the board and the grip
compete for one conditioning budget — they have never been asked for together at
a strength that could carry both. 0.3 → ~0.5: board back **and** fingers kept
means beat 08 has its recipe; board back and hair still bald means the two
failures are independent and the wording comes out; neither back means the
second net cannot hold an object against a crowded prompt at any strength that
leaves the drawing alone, and figure ink in the board hint becomes the argued
lever instead of the speculative one. **§17's frame remains the best on this
beat** and this one does not displace it.

## 19. The board and the wardrobe are bought with the same knob (2026-08-20)

One number, `--scale2` 0.3 → 0.5, the 73-token prompt held byte-identical (the
deriver asserts the payload matches the parent's; diffed again at pull).

| clause | scale30 (0.3, 64 tok) | grip (0.3, 73 tok) | scale50 (0.5, 73 tok) | boardnet (0.8) |
|---|---|---|---|---|
| board: quad px < luma 80 | 0.758 | **0.235** | **0.757** | present |
| grip on the board | mitten | fingers, **on the sash** | **none, board untouched** | absent |
| B6 wardrobe | shirt + sash + wrap | shirt + sash + wrap | **ONE BROWN ROBE** | one flat robe |
| sleeve RGB | (217.9,193.4,165.0) | — | **(161.6,115.4,80.3)** | — |
| B8 hair (canon) | sandy | **bald** | **bald** | bald |
| B4b hand→wrist | 48.5 px | 41.2 px | **4.0 px** | 10.2 px |
| both arms | yes | yes | **yes** | far arm gone |
| frame mean luma | 134.2 | 127.3 | **114.4** | 86.9 |

**The window is narrower than 0.3–0.5, not 0.3–0.8.** At 0.3 the drawing is
intact and the object is so marginal that nine words remove it. At 0.5 the
object is as solid as it has ever been and the cream shirt and white sash have
already merged into the brown wrap — the same collapse 0.8 produced, measured on
three patches rather than judged by eye. **So the route stops tuning this
number:** one knob buys the object and the garments, and they move in opposite
directions.

**Two separations this frame bought that no other frame could.** (1) **The hair
is not a conditioning problem.** Conditioning rose by two thirds and the hair did
not move — at 73 tokens the crowding alone is sufficient to lose `light sandy
hair`, so §18's failure and the object failure are independent and the hair is a
prompt-budget item. (2) **Where a hand GOES is not the object net's to decide.**
Strengthening the board moved the far hand by nothing: it sat at the chest on
the strap at 0.3 and sits there at 0.5.

**Next, and it is now ARGUED rather than speculative: figure ink in the board
hint.** Three rungs have spent every free lever — wording summons a grip and
binds it to the wrong object while costing the board (§18), strength restores
the board and moves no hand while costing the wardrobe (§19), and the guidance
window was excluded at §17. A short stroke for the gripping hand at the authored
L-wrist, with `--scale2` back at 0.3 where the drawing survives and the prompt
back to §17's 64 tokens so the crowding that costs the hair goes with it, is the
only remaining input that addresses **position**. It would be the first figure
ink ever placed in that hint and it is still owed the five tracing losses in
writing before it is authored — but §19 is the evidence those losses were
waiting for. **§17's frame remains the best on this beat.**

## 20. The loop bound, was traced perfectly, and came back a belt buckle (2026-08-20)

Section 19 named figure ink in the board hint as the last free lever and said it
was owed the five tracing losses in writing. That argument was filed first
(`pipeline/work-ladder-0819.md`, "the grip mark, argued against the five tracing
losses"), and it **rejected the lever as three rungs had named it**: "a short
stroke" is loss 4 exactly, and section 9 had already ruled that B4b needs a
hand-sized mark. What it authorised instead was a **closed, hand-sized loop at 7
px**, centred on the authored L-wrist and straddling the board's top edge.
`ep2-b08-gripmark-0820` fired it: one variable, `--control2`
`b08-board-0820.png` -> `b08-board-grip-0820.png`, the prompt back to the
parent's byte-identical 64 tokens, `--scale2` 0.3, seed 20260819, everything
else held and verified in the sidecar.

**FAIL. And the mode that fired was not one of the five.**

| clause | parent scale30 | gripmark |
|---|---|---|
| board: quad px < luma 80 (bbox x583-723 y657-820) | **0.754** | **0.234** |
| the mark at the authored L-wrist | nothing | **a gold belt clasp**, 511 px, centroid 14.2 px off |
| B8 hair (canon) | sandy | **BALD** |
| near hand vs authored ELBOW / WRIST | 8.0 / 96.1 px | 2.7 / 90.0 px |
| B4b-i pointing hand -> authored wrist | 48.5 px | **39.8 px** |
| B2 separation | +60.6 | +55.5 |
| B7 guard / goblin spread | 21.7 / 8.1 | 22.9 / 18.7 |
| frame mean luma | 135.4 | 130.2 |

### The mark bound. That question is answered and it is not the failure.

The pre-registered most-likely mode was **L1 IGNORED** (loss-3 class: figure ink
lost its grip at 0.28, and 0.3 is 0.02 above it with a tenth of the board's ink).
It did not fire. The loop was traced at full fidelity, in place: 511 pixels
satisfying (R>170, G>140, B<130) in the wrist window, centroid **(615.7, 681.2)**,
**14.2 px** from the authored **(621.6704, 668.4352)**. **Figure ink at 0.3 in
this two-net rig is above threshold** — loss 3's number came from a single-net
frame and does not transfer.

### THE FINDING: YOU CHOOSE THE SHAPE AND THE PLACE. YOU DO NOT CHOOSE THE NOUN.

The traced form came back as a **second gold belt clasp**, drawn beside the one
already there, with a rim, a dark inset and a highlight — a fully drawn object,
so **L2 (flat-trace) did not fire either**. The openpose net asserts a guard
L-wrist at exactly that pixel at scale 1.0. The prompt says `clipboard lowered in
one hand`. Neither disambiguated it. A rounded closed form sitting on a belt line
beside a leather strap is, to this checkpoint, **hardware**.

**The argument this rung was built on is falsified in its load-bearing step.** It
claimed the loop was different in kind from the five losses because "the two nets
agree at one pixel, and agreement between nets is not a new class of
instruction." As measured, the pose keypoint contributed nothing to the mark's
identity.

**And section 10's synthesis gains a corollary.** *"Any hint this net can read is
a hint it traces"* — true, and now: **what it traces is named by the surrounding
pixels.** Every one of the five losses drew ink ON a figure, so the ink WAS the
silhouette that named itself and the question could not arise. This is the first
mark on this route whose intended noun differed from what its neighbourhood
implies, and the neighbourhood won. The practical rule for any lane: **place an
authored enclosure only where the scene already implies the object you want** —
which is exactly why the board hint has worked four times. A rectangle at a hip,
beside a hand, is a board.

### Second finding: the effective load is (strength x INK), not strength

Section 19 calibrated the B8 hair instrument on two inputs — conditioning load
(bald at 1.0+0.8 and 1.0+0.5, sandy at 1.0+0.3) and prompt crowding (bald at 73
tokens, sandy at 64). **This frame holds both at the values that passed and comes
back bald anyway.** The only thing that moved is the hint's ink fraction,
0.00324 -> **0.00418**, +29% at unchanged strength — and it cost the same two
clauses that +0.2 of strength and +9 prompt tokens each cost: the canon hair and
the object. The board fell to **0.234**, against the wording rung's 0.229.

**So B8 now reads three inputs, and "0.3 is the scale that works" is not a safe
thing to inherit across a HINT edit any more than across a prompt edit.** Section
18's rule generalises: a conditioning strength is a property of the whole
triple (strength, prompt, ink).

### What held, and it matters for reading the failure

B0 all four preflight lines with the new sha in the sidecar and 64 tokens in the
log; B1 two figures, exactly two hands (**L5 third-hand did not fire**) and zero
boards so no duplication; B2 +55.5; B7 22.9 / 18.7 on boxes **re-placed by eye at
5x** and published with luma AND material — the parent's guard forearm box landed
on a **sleeve** here, the third frame running that rule has earned itself; B4b-i
**better** than the parent at 39.8 px; B4c; B6 intact. **The loop did not act
globally.** The pointing arm the hint's selftest promised not to touch was not
touched.

### Route status

**Every lever on this net is spent, including the one three rungs deferred.** The
argument was written honestly before the pixels, the sample was cheap and every
outcome was informative, and the answer is no — not because the mark was too
weak, but because the instrument cannot be told what a mark means. The fallback
the spec named in advance is now the route: **composite-then-inpaint** on the
parent plate (4 for 4 on 2026-08-20 across beats 15, 19, 03, 13), which is the
one instrument that never has to ask this net for a noun, because the compositor
draws the noun and the sampler only re-renders it.

**`ep2-b08-scale30-0820` remains the best frame on beat 08. No pick, no
plate_ack, no cut, and beat 08 does NOT have a complete plate candidate.**

## 21. The composite's hand moved and the strap did not survive it — and the bar certified the wreckage (2026-08-20)

Section 20 ruled the fallback: composite-then-inpaint on the parent plate, the
one instrument that never has to ask the scribble net for a noun. A lane took
it, wrote `pipeline/beat08_grip_composite.py`, rendered composite rounds, and
died mid-judging with its last state "Round 3 reads correctly" and a self-caught
doubt about its own detail bar. This section is that judging finished.

**`ep2-b08-gripcomp-0820`, FAIL.** Evidence
`farm-out/ep2-b08-gripcomp-0820/EVIDENCE-b08-gripcomp-verdict-0820.png`, 5x,
plate | round 3 on disk | what the source now builds.

### Where judging actually stopped, which is not where the note said

Nothing was committed: the compositor and the whole output directory were
untracked, no verdict was appended anywhere, and **no inpaint job was ever
filed.** `ep2-b08-gripcomp-0820` is an INIT plus a MASK. It has never been near
the card. It is the first half of a two-half route.

And the round that "reads correctly" is not the round in the tree. **The on-disk
init differs from what the source's `build()` now produces in 4488 of the hole's
4489 px and in zero px anywhere else** — same hand, same translation, same mask,
a different vacancy fill. `--write` refuses to run when the selftest fails, so
the artifact was written while C4 passed and the fill was swapped afterwards.
The artifact is an axial continuation; the source is an isotropic Jacobi
diffusion whose docstring still describes the axial one. `STRAP_AXIS` is defined
and never read.

### The re-base the lane asked for: its own self-catch was wrong, and by 0.4%

The doubt was that C4's baseline ring included the removed object's own outline
and was therefore inflated. It does, and it is worth **0.08 of 17.94**. Same
ring pixels, gradient computed with the fist still there **17.94**, with the
fist gone and the fill in **17.86**.

| annulus outside the hole | 1 px | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 | 16 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| grad on the plate | 12.53 | 13.78 | 14.18 | 14.73 | 18.18 | 19.19 | 21.19 | 21.37 | 18.62 | 12.86 | 12.16 |

**The innermost ring is the coolest.** The baseline is high because the gold
clasp, the sash edge and the shirt folds are 8–10 px away, not because of the
rim. Re-based honestly — rings 3–12, 4–14, 5–14, 6–16, 8–20 px, every one of
them excluding the object entirely — the current fill reads **17%, 18%, 18%,
19%, 22%** against a 45% bar. The correction was worth making and it moves
nothing.

### THE FINDING: C4 IS A SMEAR DETECTOR, AND IT CERTIFIED A STREAK ARTIFACT

The two fills fail in opposite directions and only one of them was caught.

| | fill grad | share of ring | C4 | what it is at 5x |
|---|---|---|---|---|
| round 3, on disk | **16.04** | **89%** | **PASS** | a ribbed corduroy comb down the strap |
| current source | 3.29 | 18% | FAIL | a smooth pale blob, the strap gone, the clasp dangling |

A mean-|gradient| bar asks one question — *is this flat?* — and a ladder of
streaks is not flat. **The bar passed the artifact at twice its threshold and an
eye rejects it in a second.** The obvious extension does not rescue it either:
`|gy|/|gx|` reads **0.64 in the fill and 0.64 in the untouched ring**, because
the streaks run along the strap's own dominant axis, which is exactly the axis
the fill was designed to continue along. Measured, not assumed. **No cheap pixel
statistic tried here separates the fill an eye rejects from the material it
replaces**, so no further round on this vacancy may be judged by C4.

### What the composite DID hold, measured, because it is real and it is the ceiling

Every parent clause outside the mask survives **by construction and it is
proved, not asserted**: maxdiff outside the mask **0** over the whole frame,
zero stray pixels, and all six of the parent's published pure-skin probes
untouched by the mask. Coordinates, luma AND material published, per the
admissibility rule three frames have now earned:

GUARD face (541,363,565,387) G−R **−18.9** / R−B +49.7 / luma 228.4; forearm
(387,668,411,692) **−10.6** / +39.5 / 227.3; shin (535,1096,559,1120) **−32.3**
/ +48.6 / 189.4 — **spread 21.7** against 25.0, every region ≤ 0.0.
GOBLIN face (150,480,174,504) **+41.7** / +75.3 / 222.0; forearm
(231,764,255,788) **+41.6** / +73.9 / 222.1; shin (106,880,130,904) **+49.7** /
+63.7 / 221.9 — **spread 8.1**, every region ≥ +20.0. **B2 +60.6.** These
reproduce the parent's published 21.7 / 8.1 / +60.6 exactly, so the instrument
is the same one. B4a: authored-quad fraction below luma 80 **0.754 → 0.664**,
the drop being the hand's intended occlusion of the board's top-left corner and
not a board regression. B1, B3, B5, B6, B8, B4c: byte-identical pixels.

**The grip clause is half-bought.** Fingers and a thumb ARE visible at the
board's top edge at 5x — they are the plate's own articulated fist, translated,
so the digits are drawn rather than invented — and the hand straddles the edge,
1540 px above and 1439 below. Centroid 4.9 px from the authored L-wrist against
the parent's 90.5, and closer to the wrist than to the elbow: **the parent's
defect is inverted.** What fails is `held, not tucked`: at 5x the moved unit
carries a visible stair-stepped octagonal rim against the wrap skirt and the
sash, it sits ON the board's undisturbed outline rather than closing around it,
and there is no contact shading. It reads as a sticker of a hand.

### THE OPERATION IS WRONG, NOT THE FILL

The compositor's own docstring rejected MOVE-THE-BOARD because "a translation of
a mis-cut object is a decal." MOVE-THE-HAND fails the mirror of that test: the
cut is clean and **the hole is not fillable.** Moving the fist 91 px opens
4489 px in a harness-strap / cuff / shirt junction with a gold clasp on its top
edge, and the plate contains no clean source for that junction — not a patch to
copy, not an axis to continue, not a boundary to interpolate. Three fill
families have now been tried on it (per-row ramp, axial continuation, isotropic
diffusion) and all three left an artifact an eye names instantly.

**And this is why the four wins do not transfer.** Beats 15, 19, 03 and 13 all
either removed an object from a homogeneous field or dropped a sprite onto one.
**Not one of them had to reconstruct a garment junction.** The generalisable
rule: *composite-then-inpaint is licensed where the vacancy's material is
continuous and unstructured; it is not a licence to relocate a part of a figure
across its own clothing.*

### The rung that follows, named and NOT filed, with the reason

Not a fourth fill. The vacancy should not exist: the honest version is to
**COPY** the fist to the board edge and leave the original in the init, inside
the mask, so the sampler removes it from real strap pixels instead of being
handed a fabricated fill to rationalise. **That rung is not zero-dependency and
not mechanical, and it is not filed for two reasons.** First, a 0.30 pass does
not delete a hand — 0.30 is the strength that exists to preserve structure — so
the rung has to choose a higher strength inside the mask and that re-opens the
exact clauses (B6, B8, the wardrobe) the 0.30 number was bought with, at
`(strength × ink)` prices §20 already measured. That is an argued tradeoff, not
a knob turn. Second and decisive: **the instrument that would score its vacancy
has just been shown to certify artifacts at twice its bar.** Filing a render
whose verdict cannot be trusted is filing work with no consumer. A replacement
for C4 has to come first, and nothing tried in this section is it.

**`ep2-b08-scale30-0820` remains the best frame on beat 08. NO pick, NO
plate_ack, NO cut, and beat 08 does NOT have a complete plate candidate.**

## 22. The copy worked, the mask did not: 0.99 drew a second goblin into it (2026-08-20)

§21 named the copy-the-fist rung and refused to file it for two reasons — no
trustworthy instrument, and an unargued strength. Both were discharged (C4' in
`pipeline/fill_quality.py`; the argument in `beat08_grip_copy.py`), the rung was
filed, and it ran. **`ep2-b08-fistcopy-0820`, FAIL.** Evidence
`farm-out/ep2-b08-fistcopy-0820/EVIDENCE-b08-fistcopy-verdict-0820.png`, 3x,
plate | init | landed.

### WHAT THE PASS DID

At strength 0.99 into an 18408 px mask it **drew a whole second goblin** — green
skull, blond hair, pointed ears, an angry face — with a buttoned shirt placket
where the harness strap had been. At 1x. The two predictions that held:

* **THE FIST WAS DELETED**, completely, from real strap pixels. The thing §21
  said 0.30 could not do, 0.99 did.
* **THE COPIED DIGITS SURVIVED BYTE-INTACT.** The latent-blend argument was
  right and it is now demonstrated rather than sourced: an unmasked region is
  restored every step, so protected drawn content is safe **at any strength**.

### THE OBVIOUS CORRECTIVE WAS WRONG, AND MEASURING IT FIRST IS THE POINT

The corridor was the part of the mask I had argued hardest for, so it looked
like the culprit. **Dropping it saves 434 px of 18408** — it was already covered
by the fist's own margin and the copy's rim. A rung filed on that theory would
have changed 2% of the mask and learned nothing.

**The cause is geometry.** The two work sites — the fist at y 542-620 and the
copy at y 633-711 — are **13 px apart**, so any mask covering both is ONE
~200 px tall region. Swept: it does not split at `OLD_GROW` 4 any more than at
14.

| OLD_GROW / rim | mask px | components | largest box |
|---|---|---|---|
| 14 / 8,4 | 17974 | 2 | 142x211 |
| 10 / 6,3 | 15964 | 2 | 138x205 |
| 6 / 5,2 | 14222 | **1** | 134x200 |
| 4 / 4,2 | 13392 | **1** | 132x197 |

A region that size, at 0.99, under a prompt naming *"the small goblin man"*,
with **no spatial conditioning anywhere in this pipeline** — `inpaint_fruit.py`
has no controlnet at all — gets filled with the largest available noun.
`composite-init-pattern.md` names that failure in exactly those words. This rung
walked into it while quoting the same document about strength.

### THE SECOND FINDING, AND IT HAS THE WIDER BLAST RADIUS

**`--pad-crop 64` BREAKS THE "NOTHING OUTSIDE THE MASK CHANGES" GUARANTEE.** The
landed frame differs from its init in **15355 px OUTSIDE the mask, maxdiff 160.**
`padding_mask_crop` crops the masked region with padding, upscales it, inpaints,
and pastes back — and the resample on the way back rewrites unmasked pixels
inside the crop box. The latent blend protects the *latent*; the crop-and-paste
happens around it.

Every composite in this tree asserted *"nothing changed outside the mask"* about
the **composite init**, never about the **landed result**, and b03/b13/b15/b19
all ran through this same script with `--pad-crop 64`. On this frame the guard's
head fell outside the crop box and read maxdiff 0, so **B8 survived by luck of
geometry rather than by the guarantee.** Any beat clause claimed to be safe
"because it is outside the mask" is only safe if it is also outside the crop box,
and that has never been checked anywhere.

### C4' RETURNED **VOID**, AND THAT IS THE INSTRUMENT WORKING

Its first live use. The 18408 px mask left only **120 real px** in the erase
region's 3-12 px ring, against a 200 px floor, so `fill_quality.py` refused to
score rather than guess — published dead zone 5, behaving as documented. **The
retired C4 would have returned a confident number here.** A bar that declines is
worth more than a bar that answers.

### THE RUNG THAT FOLLOWS, AND IT IS FILED

**`ep2-b08-eraseonly-0820`, backlogged**, derived from the failed parent.
**ONE SITE, ONE QUESTION:** mask the original fist alone at grow 10 — 10020 px,
largest component 9956 px in a **102x118** box, 1.8x smaller by area than the
region that hosted a face — and ask only whether the sampler can delete the hand
from real strap pixels. The copy stays in, wholly outside the mask, and **will
still read as a decal**; that is pre-registered as expected, not as a fail,
because drawing its contact edge is a SECOND pass on this pass's output. **Two
small masks in series, never one big one.**

One variable: the mask. Strength stays 0.99, the prompt stays byte-identical,
and the pre-committed next step if a noun still arrives is strength 0.99 → 0.70.

**The forearm is out of scope and stays out.** Re-routing a limb needs spatial
conditioning and this tool has none; that is a txt2img-route question.

**`ep2-b08-scale30-0820` remains the best frame on beat 08. NO pick, NO
plate_ack, and beat 08 still does NOT have a complete plate candidate.**

## 23. Halving the mask changed the SIZE of the noun, not the noun (2026-08-20)

**`ep2-b08-eraseonly-0820`, FAIL.** Evidence
`farm-out/ep2-b08-eraseonly-0820/EVIDENCE-b08-eraseonly-verdict-0820.png`, 3x,
init | fistcopy's goblin head | eraseonly's green fist.

§22's corrective ran: one site, the guard's fist alone at grow 10, **10020 px in
a 102x118 box — 1.8x smaller by area** than the region that hosted a face. The
pass **drew a green goblin FIST** where the guard's hand was. It did not delete
the hand; it recoloured and redrew it as the other character's.

| | fistcopy | eraseonly |
|---|---|---|
| mask | 18408 px, 142x211 | **10020 px, 102x118** |
| what arrived | a goblin head, ears, hair, a shirt placket | **a green goblin fist** |
| H1 fist gone | PASS | **FAIL** |
| H3 copied digits | PASS | **PASS** |
| out-of-mask drift | 15355 px, maxdiff 160 | **8574 px, maxdiff 132** |
| B8 head box | maxdiff 0 | **maxdiff 0** |
| C4' | VOID (ring 120) | **VOID (ring 148)** |

Two things the second run confirmed cleanly. **The out-of-mask drift scales with
the crop box**, 15355 → 8574 px, which is the `--pad-crop` mechanism §22 named
behaving exactly as described — it is the crop, not the mask. And **the copied
digits survived a second 0.99 pass**, this time wholly outside the mask rather
than interior-protected.

### THE PRE-COMMITTED NEXT STEP WAS STRENGTH, AND IT IS NOT BEING TAKEN

§22 registered *"if a face, a hand or a bunched garment object appears … STRENGTH
is the next rung: 0.99 → 0.70"*. **The second sample distinguished something the
first could not, so that pre-commitment is superseded and the reason is written
rather than skipped.** What arrives is not *any* noun. Both times it is
**specifically the goblin**, and beat 08's prompt names one twice:

> "...other arm pointing at the small **goblin** man's belly, **green skin**,
> plump, adult..."

That is the whole-frame txt2img prompt, carried byte-identical through two
derivations on the deliberate ground that unchanged wording keeps the mask the
only variable. **That was the right discipline for testing the mask and it is the
wrong prompt for this pass.** The mask lies entirely on the GUARD — his harness
strap, his cream sleeve, his brown cuff. There is no goblin in it and no hand in
it. Handing that region a prompt naming a green-skinned goblin at strength 0.99,
and then being surprised by a green fist, is the error.

### C4' HAS NOW RETURNED VOID TWICE, AND THE SECOND ONE IS ON ME

Ring 120 px, then 148 px, against a 200 px floor. The instrument is right both
times — it refuses to score a region whose neighbourhood was repainted — but the
repeat is a **usage** defect, not an instrument defect: **the erase region I
publish IS the mask**, so its ring can never land on real pixels. The fix is to
set the scored region IN from the mask boundary by more than the ring's outer
radius, so the ring falls on untouched plate. Not applied yet, and named here so
the next rung does not spend a third render discovering it.

### THE RUNG THAT FOLLOWS, AND IT IS FILED

**`ep2-b08-nogoblin-0820`, backlogged.** ONE VARIABLE: the prompt. The init, the
mask, the strength, the steps, the cfg and the seed-bearing structure are all
inherited byte-identical — `derive_spec` refused the init and fetch overrides as
no-ops, which is the guarantee working.

* **POSITIVE** describes only what the mask covers: *"brown leather harness strap
  crossing a cream linen shirt, brown cuff, white sash"* + this plate's cel
  dialect. **No figure noun at all** — there is no person in that region, only
  clothing on one.
* **NEGATIVE** keeps beat 08's whole negative and adds the nouns both samples
  actually drew: `goblin, green skin, pointed ears, second figure, face, head,
  hand, fist, fingers, knuckles, arm, buttons, placket`.

**If that fails, strength 0.70 is next, and after that the route closes.** The
honest conclusion waiting behind it: a tool with **no spatial conditioning of any
kind** — `inpaint_fruit.py` has no controlnet — cannot be asked to erase a limb
from a figure, and beat 08's grip goes back to the txt2img route with three
measured samples saying why.

**`ep2-b08-scale30-0820` remains the best frame on beat 08.**

## 24. The prompt WAS the lever — the goblin is gone, and the plate still fails (2026-08-20)

`ep2-b08-nogoblin-0820`, rc=0, **9.7 s of render**, $0. One variable against
`ep2-b08-eraseonly-0820`: the prompt. Same init sha `7cc1a4cb…`, same mask sha
`8c94f140…`, same strength 0.99, same 40 steps, same cfg 7.5.

### IT DID NOT GET THERE ON THE FIRST TRY, AND THE REASON IS WORTH MORE THAN THE RUNG

The job was filed at 17:45 and was **dead at 17:48, rc=1, in its FIRST step,
three seconds in: HTTP 404**. Not the recipe — the address.

`derive_spec`'s retoken pass rewrites *every* string in a child, and this
deriver asked for `("b08-eraseonly" → "b08-nogoblin")` to move the working
directory and the User-Agent. It also hit the one string that had to keep
naming the **parent**:

```
https://raw.githubusercontent.com/.../farm-out/ep2-b08-eraseonly-0820/
                                  → .../farm-out/ep2-b08-nogoblin-0820/
```

— a directory nobody had published, because the init and the mask live under the
run that produced them. The sha256 assertions were right, the filenames were
right, the bytes were on `main`; the child was reading them from an address
invented by a search-and-replace.

**And §23 recorded the near-miss as a success.** It says *"`derive_spec` refused
the init and fetch overrides as no-ops, which is the guarantee working."* That
refusal was correct — the text offered was the parent's, byte for byte — but it
was read as *"the fetch inherits fine"* when retoken had **already changed it**.
A refusal that fires because your replacement equals the parent's original tells
you nothing about what the child ended up carrying. **Generalisable: after a
retoken, re-read the child's payload for strings that must still point at the
PARENT. Published-artifact URLs are the whole class.**

Fixed at the address, not the string: the same two files are now published under
the child's own name too. Git stores one blob for identical content, so it costs
two tree entries and makes every guard, the retoken and the sha assertion line
up. Re-filed with `--backlog --again`, autofilled, ran clean.

### THE ANSWER: YES, AND IT IS UNAMBIGUOUS

Two samples put a goblin in this mask. Removing the goblin from the prompt
removed it from the picture, completely, first try. Measured on the green
channel, in-mask `G−R`:

| | in-mask G−R mean | px > +20 | px > +40 |
|---|---|---|---|
| init (guard's own fist) | −28.59 | 0 | 0 |
| **parent** eraseonly | **−2.83** | **1934** | 0 |
| **this frame** | **−16.06** | **166** | 46 |
| the real material around it (ring 35–45 px, 6840 px, 100 % untouched) | **−19.90** | **0** | 0 |

The parent sat 17.1 levels off its own neighbourhood; this fill sits 3.8 off.
The 46 strongly-green px are a single desaturated teal fringe (mean RGB
112,159,143) along one shard edge at x603-638 y556-627 — a chromatic artifact on
a hard edge, not skin.

### AND THE PLATE STILL FAILS, ON THE OTHER HALF OF THE SAME CLAUSE

H1 says the fist must be *deleted* **and** *replaced by plausible harness strap,
cuff and shirt*. The first half passes: no skin-toned fist survives anywhere,
by eye at 9x. The second half fails. The plate's own diagonal strap is **severed
at the mask's top edge**, a **new brown strap segment carrying a NEW GOLD CLASP**
is drawn across it, and the rest of the region is a radiating fan of hard white
and black wedges. The prompt asked for "brown leather harness strap … brown
cuff" and at 0.99 the sampler drew *another one of those*, with hardware.

At 1x the frame reads fine — a strap-and-clasp cluster at the chest, the copied
fist reading correctly at the board, the goblin untouched. At 4x it is an
artifact. **That is worse than it sounds and better than the parent**: the
failure has stopped being a *character* and become *over-drawing*.

`EVIDENCE-b08-nogoblin-verdict-0820.png` — init / parent / child at 9x, and the
copy at 7x.

### C4' VOIDED A THIRD TIME, AND §23's PROPOSED FIX WAS BACKWARDS

The prescribed call returned **`ring 120 real px, need 200`**; the parent's
control run of the same call returns 148. §23 said the fix was to set the scored
region **IN** from the mask boundary by more than the ring radius. **That is
backwards and is withdrawn here** — moving the region inward moves its ring
*deeper into repainted pixels*. The bar's own prediction ("4673 real px") was
measured on the **init**, where nothing has changed yet, so it could never have
been the number that matters.

What works is to leave the region on the actual fill and push the **RING**
outward past the pad-crop drift band; `assess(ring=…)` already takes it.
Real-pixel density of the annulus, identical on both frames:

| ring, px from the erase region | 3–12 | 13–22 | 20–30 | 30–40 | 35–45 |
|---|---|---|---|---|---|
| real (untouched) | 3.1 % | 7.9 % | 41.4 % | 99.1 % | **100.0 %** |

At **35–45** — 6840 px, all real, so no survivor-biased subsample — this frame
**PASSES: D 3.479, N 2.510, F 1.24** against D ≥ 0.45, N ≥ 0.25, F ≤ 2.60.
Empirical null on 200 real windows of the same footprint at that ring: false-FAIL
**13.0 %**, the fill at D pct 92.5, N pct 90.5, F pct 81.0.

### THE INSTRUMENT FINDING: C4' HAS NOW CERTIFIED THREE STREAK ARTIFACTS

The parent control passes the same re-based call at D 1.751, N 1.484, F 0.77 —
**and it is a green goblin fist.** This frame passes at D 3.479 — and it is a
wedge fan. C4' bars D from **below** and leaves it unbounded **above**, so a fill
made of shards scores as "detailed".

Shard rate — the fraction of fill px whose |grad| exceeds the 99th percentile of
its own real ring:

| | shard rate | near-black L<40 | near-white L>240 |
|---|---|---|---|
| the material this fill replaced | **1.82 %** | 242 | 535 |
| parent's goblin fist | 2.79 % | 114 | 663 |
| **this fill** | **9.27 %** | **925** | **1542** |

**Five times the shard density of the plate it replaced, and D reads it as a
pass.** F misses it too, because the wedges fan out in several directions at
once and F only asks whether the fill is *more* directional than its material
(1.24 — it is barely). §21 said "C4 is a smear detector"; the sharper statement
is **C4' is a one-sided detector and its blind side is over-drawing.**

### WHAT ELSE HELD, MEASURED

* **H3 the digits SURVIVED** — three creases and the thumb legible at 9x. Not
  free: the copy sits **inside** the pad-crop box (box y ends 705, copy spans
  y 640-705) and read maxdiff 121 over 1598 px, against the parent's 55.
  Legible is not untouched.
* **B8 hair** maxdiff **0** over (500..640, 300..430); head outside the crop box.
* **B6 wardrobe** — three garments; the mask never reached sash or belt.
* **Out-of-mask drift** 8598 px, maxdiff 151 (parent 8574 / 132 — same geometry,
  so run-to-run noise). **Mechanism confirmed exactly: the crop box is
  x488-719 y458-705 and 8598 of 8598 out-of-mask changed px fall INSIDE it, 0
  outside.** Dense within ~20 px of the mask boundary, gone by 30 — which is
  precisely why the prescribed C4' ring is structurally starved.
* **scale30 clauses** — goblin box maxdiff 0, board box maxdiff 1 over 23 px.

### THE RUNG THAT FOLLOWS, AND WHY IT IS NOW EARNED

**Strength 0.99 → 0.70.** §23 pre-committed it and §23 was right not to take it
then: the fault was a **noun**, and strength does not choose nouns. That
objection is now discharged by measurement. The noun is gone at 0.99, so what is
left is **over-drawing** — and strength is exactly the knob that governs how far
the sampler may invent over its conditioning. One variable, everything else
byte-identical.

**If 0.70 still draws a second clasp, the route closes** on the conclusion
already written in §23: a tool with no spatial conditioning of any kind cannot be
asked to erase a limb from a figure, and beat 08's grip goes back to txt2img with
four measured samples saying why.

**Two instrument debts, both cheap, neither of them GPU work:** (1) C4' needs a
**ceiling** on D, or a shard-rate clause beside it; (2) every C4' call on a
`--pad-crop` composite must re-base its ring past the drift band and **publish
the annulus's real-pixel fraction**, because the prescribed 3-12 px ring is
structurally starved on this pipeline and will VOID every time.

**`ep2-b08-scale30-0820` remains the best frame on beat 08. No cut change, and
nothing staged.**

## 25. Strength was the knob after all, and the strap survives — one crossing band short (2026-08-20)

`ep2-b08-str70-0820`, rc=0, **7.3 s of render**, $0. One variable against §24:
strength 0.99 → 0.70. Same init sha, same mask sha, **same seed 20260822**, same
40 steps, same cfg 7.5, prompt and negative byte-identical.

**Neither pre-registered fail mode fired.** The most likely one said the fist
would only *dent* at a lower strength. It did not dent — it is gone completely,
by eye at 14x. **Deletion does not need 0.99.** The second said a clasp would be
drawn anyway, proving the invention was not a function of strength. No clasp was
drawn. **Strength was the knob.**

### THE FOUR-FRAME LADDER, ONE FOOTPRINT, BOTH KNOBS

C4' at the re-based 35–45 px ring (6840 px, **100 % real on every frame**);
shard rate = fill px whose |grad| beats that ring's 99th percentile.

| | C4' D | N | F | shard | ink L<90 | in-mask G−R | px > +20 | what it drew |
|---|---|---|---|---|---|---|---|---|
| init (the plate) | 2.169 | 1.752 | 0.93 | **1.82 %** | **13.3 %** | −28.59 | 0 | the guard's own fist |
| 0.99 `eraseonly` | 1.751 | 1.484 | 0.77 | 2.79 % | 10.6 % | −2.83 | **1934** | green goblin fist |
| 0.99 `nogoblin` | 3.479 | 2.510 | 1.24 | **9.27 %** | **24.6 %** | −16.06 | 166 | 2nd clasp + wedge fan |
| **0.70 `str70`** | 1.548 | 1.157 | 1.12 | **0.38 %** | 10.5 % | **−23.11** | **0** | **the strap, plus one crossing band** |

**The symmetry is the finding.** At 0.99 the fill is **5.1× more** shard-dense
than the material it replaced and 1.85× more inked; at 0.70 it is **4.8× less**
shard-dense and slightly under-inked. **The plate's own line quality sits between
the two ends of the knob and neither end lands on it** — 0.70 much the closer
(10.5 % ink against 13.3 %), and the only one of the three that keeps the strap.

### WHAT IT COSTS TO KEEP THE BAR I WROTE

H1(b) says *"the guard's own strap RUNS continuously through the mask … and no
second strap, second buckle or second clasp appears."* The strap **runs** — the
parent's was severed. No buckle, no clasp; a few-px orange speck at x≈600 y≈575
is the only hardware hint. But a **second brown band crosses the strap below the
buckle**, forming a small X that is not in the init, with two short stubs at its
top. **That is a second strap and the clause says no second strap.**

The bar was written forty minutes before the pixels landed. It is not being
relaxed now that a second strap is what arrived. Recorded honestly in both
directions: a strap crossing a strap is **in vocabulary** for a harness in a way
that a floating gold clasp and a fan of white wedges are not, and at 3x — the
screening scale — the frame reads as a plausible harness. **That is a reason to
take one more rung, not a reason to rewrite the clause after the fact.**

Everything else passes, several by the widest margin the route has seen: **G−R
−23.11 with ZERO px above +20** (closest of the four to its own neighbourhood,
and the only frame with no green at all); **shard rate 0.38 % against a 3.00 %
bar**; the copy took **less** damage than at 0.99 (maxdiff 78 against 121);
B8 hair maxdiff 0 for the third run; out-of-mask drift **8600 px, and 8600 of
8600 inside the crop box** — 8574 / 8598 / 8600 across three renders of identical
geometry, which is the tightest evidence yet that the drift is a deterministic
property of the crop and not of what the sampler drew.

`EVIDENCE-b08-str70-verdict-0820.png` — init, 0.99, 0.99, 0.70 at 9x.

### THE SHARD CLAUSE IS NOW CALIBRATED, AND IT KILLS THE DEBT §24 FILED

An empirical null of **200 real windows of this exact footprint**: shard rate
median **0.35 %**, p95 4.11 %, p99 6.74 %, max 16.43 %. The parent's 9.27 % sits
at the **99.5th percentile of real material**; the 3.00 % bar sits near p90.

The same null puts **D at median 1.077 and p95 4.658** — so **the "ceiling on D"
filed in §24 is wrong and is withdrawn**: a ceiling that keeps false FAILs at
5 % would have to sit near 4.7 and **would not have caught the parent's 3.479**.
The shard rate is the right clause and the D ceiling is not.

**And the shard clause needs a FLOOR as well as a ceiling.** This frame is 4.8×
*smoother* than the material it replaced and nothing in C4' — which passed all
four frames, including a green goblin fist — can say so.

### THE RUNG THAT FOLLOWS, WITH ITS STOPPING RULE WRITTEN BEFORE IT RUNS

What is left is a **noun**, and this route has now *measured* that **the prompt
chooses nouns** (§24: removing the goblin removed it outright at unchanged
strength). So: keep 0.70, keep the positive, and add to the **negative** the noun
that actually arrived — `double strap, crossed straps, second strap, extra strap,
strap end, buckle, clasp`. One variable, ~20 s of card, $0.

**STOPPING RULE, pre-committed: if that pass draws a THIRD unwanted noun, the
route closes** on §23's conclusion and beat 08's grip goes back to txt2img. The
lesson would be that a tool with no spatial conditioning trades one invention for
another indefinitely, and five samples is enough to say so.

**DO NOT PROPOSE AN INTERMEDIATE STRENGTH.** 0.99 over-draws, 0.70 under-inks,
and the fault at 0.70 is a *noun* rather than a quantity — a midpoint searches for
a value satisfying a conjunction the knob does not express, which is the same
refusal beat 01's crf ladder reached this morning.

**`ep2-b08-scale30-0820` remains beat 08's frame. No cut change, nothing staged.**
