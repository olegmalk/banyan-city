# Attribute binding: one attribute, one figure of several — eyewear on guard A only

Lane: `attrbind-eyewear` (0817). Founder ruling 2026-08-15, verbatim:
*"draw the second man without glasses. we need to have control."*

That is not the two options offered (drop the wire-rims, or draw both men in
glasses). It rejects both and asks for a **mechanism**: the attribute lands on
the figure we choose, and the engine does not get a vote on our cast. The cast
stands as drawn (founder, 2026-08-15) — guard A carries wire-rims, guard B must
not, and no cast redraw is available as an escape.

## The defect (established, not re-litigated here)

Naming eyewear inside ONE man's clause puts glasses on BOTH men, **5 of 5**.
The two men are the patrol guards; it surfaces in beats 05, 09, 10. This lane
does NOT spend card re-reproducing that count — it is already measured.

## External research (done before building — Oleg, 2026-08-04)

The published diagnosis of why this happens, and it is not a wording problem:

- **ALE-Edit**, *Addressing Attribute Leakages in Diffusion-based Image Editing
  without Training* (arXiv 2412.04715). Root cause: CLIP's text encoder is
  **causal**, so later tokens absorb the semantics of earlier attribute tokens,
  and the **EOS token carries global prompt semantics**. An attribute named
  anywhere is therefore smeared into the global conditioning that steers the
  whole frame. Their fix, **Object-Restricted Embeddings (ORE)**, is training
  free: encode each entity's clause *separately*, substitute those token
  positions into the base embedding, zero the other entities' positions, and
  **replace the EOS with the object-specific EOS**. Implemented on LCM +
  Grounded-SAM, not SDXL.
- **MaskAttn-SDXL** (arXiv 2509.15357) — region-level gating of SDXL
  cross-attention logits. Names our exact failure ("cross-token interference
  where entities entangle and attributes mix across objects") but **learns** a
  binary mask per layer. Training. Not available to us.
- **Training-free Regional Prompting for Diffusion Transformers**
  (arXiv 2411.02395) — regional attention masks, training free, but **DiT /
  FLUX**, not SDXL U-Net.
- **BindEdit** (arXiv 2606.18906) — same framing: when token-group→mask binding
  fails at attention level, tokens activate beyond their region and produce
  blended/hybrid objects.
- diffusers community pipelines: `regional_prompting_pipeline` (hako-mikan) is
  **SD 1.5 ONLY**. The only SDXL region-aware community pipelines are
  `stable_diffusion_mixture_tiling_pipeline_sdxl` and the tile-SR one — coarse
  panorama tiling, not face-scale control.
- a1111 / ComfyUI community practice on multi-character attribute bleed
  (AUTOMATIC1111 discussion #2757, Civitai multi-subject threads): consensus is
  that two *differently specified* characters in one pass is unreliable, and the
  standard remedy is **"generate twins, then inpaint the area"**, or a regional
  prompter.
- diffusers `padding_mask_crop` (inpaint pipelines, issue #6345; a1111
  "inpaint only masked"): crops the mask bbox + padding, inpaints at **full
  resolution**, scales back. This is the reason face-scale inpainting works at
  all — a small region in a large frame has too few pixels for detail.
- SDXL inpainting does **not** require a separate inpaint checkpoint: the
  9-channel inpaint UNet was initialised from base SDXL with the 5 extra
  channels zero-initialised, so `StableDiffusionXLInpaintPipeline` runs on a
  standard 4-channel SDXL checkpoint (our `animagine-xl-3.1`) via the masked
  latent path. $0, offline, no download.

**Conclusion drawn from the outside work, before any pixels:** there is no
drop-in regional-prompting mechanism for SDXL in our stack. The available
training-free mechanisms are (a) ORE-style per-clause text encoding, and
(b) composite-then-inpaint — which is already **our own proven pattern** (bark
clipboard, beats 06 and 10, low strength 0.30).

## Which class does eyewear belong to — ANSWERED, from measurements already in hand

It is **neither**, and the existing numbers already say so. Three distinct
behaviours are on record from the same 9-render / 3-seed sweep:

| Class | Behaviour | Evidence |
|---|---|---|
| hair, garments | **bind** to their person clause | separate cleanly at the same seed |
| props (the bark board) | go to **ONE WRONG** figure — nearest/first drawn | 3 of 3 wrong |
| eyewear | goes to **BOTH** figures | 5 of 5 |

A prop failure is a *routing* failure: the attribute lands on exactly one
figure, just not the chosen one. Eyewear does something different — it lands on
**every** figure of the class. That is not misrouting, it is **broadcast**, and
it is a third class which this lane names:

> **Broadcast-class attribute.** An attribute whose token is absorbed into the
> *global* conditioning and then applied wherever its host feature (here, a
> face) appears in the frame.

This is exactly what ALE-Edit predicts and it is why the class matters: CLIP is
causal and the **EOS token carries global prompt semantics**, so `glasses` named
in any clause is present in the pooled embedding that steers the whole frame.
Nothing in the prompt says *which* face; every face qualifies.

Corroboration that the wording is not the lever: **`wire-rim glasses` BINDS 7 of
7** on beat 09's ONE-figure close-up — round silver frames every time, never
sunglasses. The tag is not weak and the phrasing is not wrong. It fails only
when there is a second face for it to also land on. **The number of eligible
faces in the frame is the variable, not the wording.**

### The three-cell experiment that settles it, all cells now observed

The guard-cast lane's 2026-08-17 plates completed the table, and it took no
render of mine to read it:

| Faces in frame | Eyewear named? | Result | Evidence |
|---|---|---|---|
| **1** | yes, in the man's clause | lands correctly on him | 7 of 7 on beat 09; confirmed again on `ep2-b09-cast-0817` (round wire-rims, correctly bound) |
| **2** | yes, in ONE man's clause | lands on **BOTH** | 5 of 5 across beats 05/09/10 |
| **2** | omitted entirely | **both bare** | `ep2-b05-cast-0817` — verified by eye on `05-the-patrol-ipa-r0-w015-s0.png` |

**This rules the proximity hypothesis OUT.** It was proposed that eyewear might
bind by adjacency the way a prop does — the bark board goes to whichever figure
is drawn nearest, which is why beat 10's cast draft solved the clipboard by
*using* the prop law and drawing guard B nearest. If eyewear obeyed that law it
would land on **one** man, the nearest, and be fixable by staging. It lands on
**two**. Proximity cannot produce two, so eyewear is not prop-class; and a clause
binding cannot produce two either, so it is not garment-class. It is broadcast,
and the middle row is the whole defect: the attribute is present in conditioning
that has no address.

The third row is also the load-bearing practical fact — **omitting the token
gives two bare faces reliably**, which is what makes the ADD direction possible
at all and is precisely the founder's "draw the second man without glasses".

Noted for the cast lane and not ruled on here: the `ep2-b09-cast-0817` figure has
**light sandy hair**, which is guard B's canon colour, not guard A's dark cropped
hair. Cast is R4 and another lane's call; it does not affect the binding finding,
which is about how many faces exist, not whose they are.

## Arm 1 is RETIRED WITHOUT SPENDING A GPU-SECOND — it is self-defeating in both dialects

Pre-registered as "expected to fail". It is worse than that: it cannot be run as
written, and the reason is mechanical, checkable, and costs nothing to establish.

- **`plate_scratch.py` dialect** (the Mac plate lane) does **no negation
  lifting** at all. `no glasses` in its positive prompt puts the literal token
  **glasses** into the positive — it would *guarantee* the defect it is meant to
  test. The arm is self-defeating here.
- **Box prose dialect** (`sd_prompt._NEGATION`) *does* lift `no X` into the
  negative. But then `glasses` sits in the negative while guard A's clause asks
  for `wire-rim glasses` in the positive — the exact contradiction
  `plate_scratch.py` exits **7** on, and the standing decision already records it
  as such. On a plate that names no eyewear at all, `no glasses` is
  non-contradictory but also **vacuous**: the plate was not asking for glasses.

So there is no wording in either dialect that both asks for eyewear and confines
it. This is the vacancy law and ALE-Edit agreeing: **a negation cannot unbind a
broadcast.** Arm 1 is closed on mechanism, not on pixels, and no card was spent
on it. Recorded so the next lane does not re-file it.

## Pre-registered bar — written BEFORE the pixels exist

Per-sample scoring, three objective booleans read off the rendered frame:

1. `A_glasses` — the figure we designated carries visible eyewear.
2. `B_bare` — the second man carries **no** eyewear.
3. `cast_holds` — no third figure gains eyewear, and both men still read as two
   guards in patrol uniform (identity held 14/14 on a correctly-cast plate;
   that baseline is what must not be broken to buy the fix).

A sample **passes** iff `A_glasses AND B_bare AND cast_holds`. Reported as a
count out of N. An impression is not a score. A metric agreeing with me is not
a sample.

**Adoption threshold: a mechanism is adopted only at ≥4/5 passes across 5
seeds.** 3/5 or worse is not adopted, whatever it looks like. If this bar turns
out loose it is tightened FORWARD and said out loud — never retroactively.
Bending bars after seeing the picture is how 8/12 "passes" became 0/12 usable.

Out of scope for this lane, named and moved past: whether a passing plate is
**shippable** — look, framing, whether the wire-rims are the right wire-rims —
is R4, the founder's alone.

## Arms, cheapest first, ONE SAMPLE per recipe change

- **Arm 1 — positive-clause negation.** `no glasses` inside man B's own clause.
  Cheap, and it is the direct garment-vs-prop probe: if B comes back bare, the
  attribute is reachable by B's clause and eyewear binds garment-class. Prior:
  **expected to fail.** Vacancy law here says the negative does not reach an
  empty region, and ALE-Edit says leakage is a *binding* failure — a negation
  cannot unbind. Note `plate_scratch.py` refuses any tag present in both
  positive and negative (**exit 7**), so the real negative prompt is
  mechanically unavailable for this; this arm is positive-side only.
- **Arm 2 — composite-then-inpaint (the candidate mechanism).** Render the plate
  with **no eyewear token anywhere** — both men bare, which is also the founder's
  literal instruction — then inpaint eyewear onto guard A's face region ONLY,
  low strength, `padding_mask_crop` for face-scale resolution. Control is
  structural: the attribute cannot leak to B because B's pixels are never
  denoised.
- **Arm 3 — ORE-style split encoding.** Only if Arm 2 fails or is too heavy for
  the card. Per-clause text encoding with object-specific EOS.

## Machine discipline

Fixed seed set across arms; one variable at a time. Backend split is real —
bf16/CUDA renders red where fp16/MPS, fp32/MPS and bf16/MPS render purple off
the identical seed (MAE 60-61), so **all arms run on ONE backend** or the
measurement is of the machine, not the wording. A plate is never a prediction
about a prompt; colour does not travel. CLIP 77-token budget is enforced by
`plate_scratch.py` — any token trade is recorded and the traded words are named
as first suspects; the style tail is not cut, it confounds comparisons.
If anything renders on a Mac, `pipeline/mac_preflight.py` gates it first (two
Macs are currently suspect; macbook1/macbook3 rendered SDXL as pure noise for
days behind a UNet of exactly the right length with 88%/93% holes).

## THE MECHANISM, written down for the next lane

**Control over which figure carries an attribute is a MASK problem, not a wording
problem, and the mask is authored by a step with no sampler in it.**

Three parts, and the first two cost nothing:

1. **`pipeline/attribute_mask.py`** — $0, PIL only, no GPU, no diffusers. Builds
   a mask as a union of added shapes minus subtracted ones:
   `ellipse`, **`ring`** (an annulus — the thin-band case), `quad`, `band`
   (a thick line segment), `box`. Writes the mask PNG, a look-at-it preview with
   the region tinted, and a provenance sidecar carrying every number.
2. **`--protect x0,y0,x1,y1`** (repeatable) is the part that makes "control"
   mean something. Each protect box is a region that must not change; **one
   white pixel inside it and the tool refuses (exit 5)** and counts the overlap.
   Spend guards in this tree are code rather than intentions, and so is this:
   a mask that *cannot* reach guard B is checkable, where a wording is not.
3. **`inpaint_fruit.py --mask-png`** consumes it (xor with `--ellipse`/`--quad`).
   Everything outside the mask is restored every step by diffusers' latent-blend
   branch, so the untouched figure is untouched by construction.

**Why the mask had to become arbitrary.** A spectacle frame is neither a blob nor
a convex polygon. `--ellipse` would have masked the whole eye socket and forced
the sampler to *invent an eye*; `--quad` cannot curve. The `ring` shape masks the
**frame path only** and leaves the irises outside the mask, so identity — the
veto axis, held 14 of 14 — is protected geometrically instead of hopefully. The
same flag retires the **board-MINUS-the-hand** limitation recorded against
`inpaint_fruit.py` in `wave-drafts.yaml`, which `--sub` now expresses.

**Which strength, and it is not one number.** Two recipes already exist in this
tree and they are for different jobs:
- **ADD an object that is not there → high strength (0.99).** Measured: img2img
  at 0.35/0.55 could not add a fruit, 0 of 12. The unmasked region is restored
  each step, so high strength costs nothing outside the mask.
- **ADD detail onto structure that must keep its outline → composite first, then
  LOW strength (0.30).** Measured: the bark board split at 0.45 and held at 0.30,
  because crust relief and a straight silhouette live in the same frequency band.
- **REMOVE a thin object → high strength on a band mask.** There is no outline
  *inside* the band to preserve; the band is exactly what should go, and the
  surrounding unmasked skin gives the sampler its context. This is the case filed
  below and the reasoning is pre-registered, not retrofitted.

### Both directions, and which one is blocked

| Direction | Needs | Status |
|---|---|---|
| **REMOVE** eyewear from guard B on an existing plate | a plate that exists today | **FILED** — `pipeline/jobs/ep2-b10-attrbind-eyewear-0817.yaml`, backlogged, in the card's queue |
| **ADD** wire-rims to guard A on a bare plate | a two-guard plate with BOTH men bare | **blocked on a real dependency** — the box-lane beat-05 draft deliberately names no eyewear and is a peer lane's in-flight job. Not a scheduling excuse: it is a physical dependency, and the moment such a plate lands this is one `attribute_mask.py` call plus one low-strength pass |

The ADD direction is the one a production recipe would use, because it also
removes the leak at source: with no eyewear token in the plate prompt there is
nothing to broadcast. Removal is what could be tested today, and it is the
founder's sentence read literally.

## What was filed

- `pipeline/loop/attrbind-eyewear-0817.md` — the bar, committed `f0e65e07`
  **before** any pixels; this file.
- `pipeline/attribute_mask.py` + `inpaint_fruit.py --mask-png` — commit
  `fa03f898`. All refusal paths exercised: protect violation → 5, `--sub`
  cancelling every `--add` → 4, init sha mismatch → 3, two shape flags → 2,
  mask/init size mismatch → 6, all-black mask → 7.
- `pipeline/jobs/ep2-b10-attrbind-eyewear-0817.yaml` — commit `460565ee`, the
  REMOVAL arm. Attempt 1 died **rc=2, "init not found"**: the box's checkout has
  no `farm-out/ep2-b10-mac-plate-0817`, so the plate committed at `0ac649d5` was
  not there. **That is the sha-asserted init gate working** — a loud stop instead
  of a render of the wrong frame. Respun as
  `ep2-b10-attrbind-eyewear-0817b.yaml` (commit `1e2d34e6`) against a copy beside
  the job whose sha256 was verified **on the box**; nothing but the path moved.
  Result above: **0 of 1**.
- `pipeline/attribute_mask.py --composite/--ink` — commit `7fb1dfc7`. Inks the
  same geometry into the plate so a low-strength pass harmonises a frame that
  exists instead of inventing one. Ink follows the **undilated** shapes while the
  mask is dilated, leaving real plate pixels either side for the blend. `--ink
  auto` **samples the plate's own darkest lineart** rather than assuming black
  (measured `(0,0,0)` on the beat-05 cast plate). The composite is asserted
  byte-identical to the plate outside the ink, and refuses (exit 6) if it drifted.
- `pipeline/jobs/ep2-b05-attrbind-addA-0817.yaml` — commit `a5b42b91`, the ADD
  arm and the one the mechanism actually recommends. Init is the composite over
  `ep2-b05-cast-0817`'s bare two-guard plate; geometry read off a **coordinate
  grid** over guard A's face, not eyeballed — lenses `(294,146) r27` and
  `(379,155) r24`, bridge, one temple to the ear; 2800 mask px, 0.277% of frame;
  guard B's whole head protected at `[470,50,720,340]`, 0 violations. Strength
  **0.30**. `glasses` is in the positive prompt **on purpose**: the claim is that
  the mask, not the wording, decides where it lands.

Also run: `lint_genome.py` rc=0, 0 violations (25 pre-existing licence warnings
at the ratchet, none of them mine).

Not mine and left alone: `pipeline/test_pipeline.py` has one pre-existing
failure, `ledger_freshness.py:369` (`subprocess.run(text=...)` with no
`encoding=`). That file is another lane's and off limits to this one; neither
file touched here uses `subprocess`.

## RESULT — the REMOVAL arm: 0 of 1, and it fails on the predicate it was aimed at

`ep2-b10-attrbind-eyewear-0817b`, rendered on the box, scored against the bar as
written above.

| Predicate | Verdict | How it was established |
|---|---|---|
| `B_bare` | **FAIL** | the frames are **thinned, not gone** — both lens rims, the bridge and the temple arm survive as pale continuous arcs. The bar named this exact outcome in advance: *"no ghost of a frame left behind as a smear or a floating arc."* |
| `A_untouched` | **PASS** | measured, not judged: **0 changed pixels** inside guard A's declared protect box `[430,160,590,280]` |
| `cast_holds` | **PASS** | guard B's eyes, brows, hair and skin tone all survive; he reads as the same man |

**Sample passes on all three or not at all, so: 0 of 1.** Not adopted. The bar is
not being bent to call a thinned frame a removed one.

Measured mask behaviour, for the next lane: **1098 of 1098** mask pixels changed
(the pass did act), and **2040 px changed outside the hard mask** — that is the
`--blur 3` soft edge doing what blur is for, not leakage; the protect box inside
that same frame is untouched at 0.

### Why it failed, and this is the part worth keeping

**A thin band along an object's own outline cannot REMOVE that object, because the
unmasked pixels immediately either side of the band still describe it.** The
sampler filled the band with what the surrounding context implied, and either side
of a frame stroke the context implies *frame*. Strength was not the problem —
0.99 renoised the band completely and it came back as a frame anyway.

**This yields an asymmetry that is more useful than the beat-10 fix would have
been:**

- **ADDING** an attribute works with a thin band, because the **ink** supplies the
  structure and the surrounding context is not fighting it.
- **REMOVING** an attribute does *not* work with a thin band. It needs a mask over
  the whole host region — which for eyewear means the eye socket, which forces the
  sampler to invent an eye and gambles identity, the veto axis.

So the direction the founder's sentence points at — **draw the plate bare and add
to one figure** — is not merely the convenient direction, it is the *correct* one,
and this failure is the evidence. Removal is retired as a route for eyewear:
not on taste, on mechanism.

## Why this is worth more than a beat-05 fix

The mechanism is general in a way the beat-05 fix would not have been: **any
attribute, onto any one of several figures, by construction rather than by
wording** — draw the frame without the attribute, ink the attribute's geometry
into the region that should carry it, then denoise only that region.

**What generalises, precisely:**

- **The diagnosis.** "Which figure gets this?" has no answer in a prompt, because
  a broadcast-class attribute lives in conditioning that has no address. Any
  attribute that can plausibly sit on more than one figure will broadcast. The
  three-cell table is the cheap way to test any *new* attribute: render it with
  one eligible figure, with two, and with none. If it lands on both, it is
  broadcast and no wording will fix it.
- **The lever.** `--protect` turns "we need to have control" from an intention
  into an exit code. That applies to any figure and any attribute.
- **The asymmetry.** Add with a thin band; do not try to remove with one. Draw the
  plate *without* the attribute — which is also the cheapest prompt, since
  omitting a token is free — and add it where you want it.
- **The limit, stated honestly.** This only covers attributes expressible as
  **geometry** — eyewear, a sash, an armband, a scar, a headband. An attribute
  that is a *property of the whole figure* (a hair colour, a height, a body type)
  has no thin band to ink and is not reachable this way. For those the lever is
  the cast plate, not the mask.

This lines up with what the ControlNet lane found independently today —
**conditioning biases an attribute, it does not pin it.** Attention-level and
conditioning-level fixes shift probabilities; a mask decides. That is the whole
reason the mask route is the one that answers the founder's word, and it is why
`--protect` refusing is a feature and not an inconvenience.

"We need to have control" applies to every attribute we ever bind to one figure
among several, and the founder asked for the mechanism, not the dodge.
