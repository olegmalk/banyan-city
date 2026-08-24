# Loop cycle 019 — the founder rejected pixels the record had already rejected

**Opened:** 2026-08-24 · **Closed:** pending founder screen of the ONE sample below
**Source:** founder (Roman) on the queue2 beat-02 sample, verbatim — *"barely looks
like the goblin"* and *"the animation is trash."* Recorded in
`ledger/sample-verdicts.yaml` (fingerprint `8546220224…8927`, job
`queue2-sample-b02-0824-1787566150`); queue2 now refuses that fingerprint on every
host ("a rejected recipe does not run again", `pipeline/queue2/queue2.py` ~381–392,
matched against the committed ledger).

Evidence base: four grounding/research lanes (journal `wf_dff134f3-16f`) plus the
files named inline. The adversarial checker's findings on the earlier draft bind
this document; where a gap it named has since been closed on disk, that is stated
with the file that closes it.

## The finding

**Nothing regressed and no bar moved. The sample was byte-identical to footage this
repo had already rejected, trimmed, and reverted — the founder was simply the first
person to apply his bar to it.**

sha256 of `_sample/02-the-sprint-LTX-queue2-sample-0824.mp4` =
`8e86a1f5f78263526137f676baf5ba9db2712f9a5d4739f67f2f583957877f19` — exactly the
`source_sha256` of the 08-21 age-B seed-2 take's sidecar
(`review/motion-ageb-0821/02-the-sprint-LTX-b02-ageb-s2-trim97-0821.mp4.meta.yaml`).
The founder screened the UNTRIMMED 121 frames of a clip whose own lane had cut it
to 97 because *"THE FACE STOPS BEING DRAWN AT f106 … a featureless ovoid"* — he was
shown 24 frames of face collapse the pipeline had already condemned. (ground:recipe,
ground:likeness)

## What the 08-21 "acceptance" actually was — the honest bar statement

The mirrored recipe was **never accepted as show quality, and never accepted by the
founder at all**. The record, verbatim:

- Ship manifest (`review/ep2-ship-0821/sources/ship-manifest.yaml`, beat 2):
  *"STEWARD PICK … R4-VETO-ABLE IN ONE LINE. The founder has screened neither this
  clip nor the one it replaces."*
- Its verdict was a mechanics-and-relative bar: *"PASS ON THE WINDOW AND
  CUT-PREFERRED … IT DOES NOT PASS DESIGN: the ears are long tapering spikes …
  C1's magenta collar is present"*
  (`pipeline/jobs/ep2-b02-tilemotion-s2-0821.yaml`, scored under a bar whose
  preamble reads *"SCORED AS A CANDIDATE FOR A POST-SHIP SWAP, not as a shipped
  clip"*).
- It sat in the ship cut ~5 hours. The founder watched that cut the same evening —
  *"worse than the last one"* — and commit `5412a4522` reverted all five age-B
  swaps as takes he never approved; `de1666f86` deleted them from the tree.
  (ground:recipe)

So this is not "the bar moved" and not a regression: **both 08-24 verdicts restate
faults already written into the acceptance record itself** — `fault_shipping`
named the wrong ears and collar ("barely looks like the goblin"), `why_trimmed`
named the face melt, and the freeze was measurable in the bytes ("the animation is
trash"). The 08-24 rejection is this recipe's first founder screening, and it is
consistent with every prior founder note, not a reversal of any. (ground:bar)

## Fault 1 — "barely looks like the goblin"

**In this LTX recipe the init frame is the ONLY carrier of likeness, the init
chain worked perfectly, and it delivered the wrong goblin.** (ground:likeness)

- `pipeline/ltx_i2v.py`'s render stage takes exactly (`embeds`, `init`, `out`) —
  no IP-Adapter, no LoRA, no ControlNet exists in the motion stage, and the job
  spec itself recorded that 13 prompt-ladder rungs proved wording alone returns a
  human male. The face reaches LTX as pixels in frame 0 or not at all.
- The chain was intact: the crop was reproduced locally from the sha-asserted
  plate (`farm-out/ep2-b02-ageb-r2-0821/ep2-b02-ageb-r2-0821-ipahead.png`,
  832x1216 → 704x1280) and sample frame 0 matches it at codec-noise level
  (mean |Δ| 3.46). The machinery is not the defect.
- The goblin IN the plate is the defect, twice over. (1) It was drawn 08-21
  10:12Z under the k6a steward standard (`pipeline/jerry_standard_0821.py`,
  IP-Adapter route) — six hours before the founder's 16:54 canon ruling, *"dude,
  this is how the goblin should look"*, which installed
  `taste/refs/goblin-canon-founder-0821.png` and *"SUPERSEDES TILE B AND THE
  08-21 AGE-B RECIPE ON EVERY AXIS THE IMAGE SHOWS"*
  (`pipeline/canon.yaml`, `founder_ruling_2026_08_21`). (2) Even inside its own
  superseded canon it carried the recorded elf-spike ears and magenta collar —
  with "pointy ears, long pointy ears, elf" sitting in its own negative prompt,
  which is the standing evidence that words cannot fence what the checkpoint
  wants to draw.
- The route that drew it is CLOSED BY RULE, not by preference: after four vetoes
  verbatim *"these are not my goblin"* on ~sixteen rounds of prompt/IP-Adapter
  face work, `canon.yaml route_closure_2026_08_22` forbids any further
  prompt-side face rung. *"His pixels have to enter as PIXELS."*

**Where the pixels-as-pixels route actually stands on disk** (all 08-22, verified
in `pipeline/lora/registry.yaml`, `pipeline/goblin-twopass-route-0822.md` incl.
its evening CORRECTION, and the `farm-out/lora-jerry-v3-*` grids):

| mechanism | status |
|---|---|
| img2img from canon at 0.30–0.45 | re-lighting only — cannot change pose or ground; eye survives only at face fraction ~22–29%. Dead for a full-body sprint. |
| v2 LoRA (`bnyjerry-sdxl-v2`, founder-ratified 21-frame set, "all ok") | identity passes; insists he is STANDING (21/21 training frames stand). One pass cannot carry pose + face. |
| two-pass (net poses a stranger, LoRA repaints at 0.75) | RETIRED — the correction measured that weight reaches structure too; the seat survives only where he is somebody else. |
| pose hint, wording A | **four of four postures drive**, including the sprint: `tp5-p1-stride-wA` adopted `jerry-skel-h240stride-0821`. Any addition to the wording costs the pose (measured, three controls). |
| **v3 LoRA** (`bnyjerry-sdxl-v3`, trained on his pixels + posed frames) | **poses AND keeps his face in ONE pass** (`loraweight-jerry-v3-0822.yaml`: "v3 poses and keeps his face; the single clause between it and a shippable recipe is his skin under a pose net" — sage 15/15 without a skeleton, tan 6/6 with one; wording and hint-volume ruled out as the cause). |
| the four v3 knob probes (loraweight 1.0/1.2, cnetscale, capshape, blockweight) | RENDERED on the box, **never graded** — the pixels sit ungraded in `farm-out/lora-jerry-v3-{loraweight,cnetscale,capshape,blockweight}-0822/`. |

**Concrete pipeline change (resemblance):** goblin init plates stop being drawn by
the closed IP-Adapter standard and are drawn by the v3-LoRA-plus-skeleton one-pass
through `pipeline/inpaint_fruit.py` — the one driver where the pose net is proven
to act and which already has the sha-pinned `--lora` arm. The rejected plate
family (`ageb`) is retired with its fingerprint. The first artifact of that change
is the ONE sample below, and step zero of it costs no GPU: **open the four
ungraded probe grids** and read the skin cross before choosing the LoRA weight —
the route doc's own closing lesson ("Open the PNG").

## Fault 2 — "the animation is trash"

Measured from the rejected bytes (ground:likeness, grayscale inter-frame mean |Δ|,
10-frame stride): **frozen for ~2.1 s** (f010–f060 at 0.16–0.32 — a still with a
runtime, the M5 failure the job's own bar names), then the sprint, plant and dive
**compressed into ~1.2 s** (18.4 → 69.7 → 56.6), then the face-melt tail the trim
existed to remove. The 08-21 PASS was judged off contact strips, and a strip
cannot show a freeze.

The outside research (research:outside lane; sources at the end) ties both
verdicts to known LTX-family mechanisms and ranks the $0 levers:

1. **Guidance 2.0 is off-recipe.** The shipped `ltxv-13b-0.9.8-distilled` config
   runs `guidance_scale 1`, `stg_scale 0` in both passes; distilled checkpoints
   are trained CFG-free, and CFG>1 against distilled sigmas is a known artifact
   source. Our 2.0 is a documented divergence. Cheapest experiment on the motion
   axis, zero downloads.
2. **The image-compression knob couples the two verdicts and cannot fix both.**
   LTX 0.9.x learned to associate MPEG compression artifacts with motion
   (ComfyUI `LTXVPreprocess` docs): low compression = crisp identity + frozen
   frames, high = motion + a degraded init face. The rejected recipe ran
   `--image-crf 10` — the frozen end — and froze for two seconds. The
   founder-side anchor take ran 33. Stop sweeping this knob; it trades one
   verdict for the other.
3. **Prompt register is the biggest free motion lever.** The model card demands
   chronological action narration under 200 words — what happens NEXT, not what
   the scene is. The rejected clip ran the long descriptive age-B block.
4. **Identity drift in LTX i2v is an open upstream defect with no parameter
   answer** (Lightricks/LTX-2 issue #255, conditioning tried to 0.8, zero
   workarounds) — which is why fault 1 is fixed in the init, not with LTX knobs.
5. **The recipe is beat-sensitive.** "The sprint" is fast full-body motion,
   LTX's documented worst case; frame-0 conditioning propagates only while
   motion is modest. An accepted low-motion recipe is not accepted globally.

**Concrete pipeline change (motion):** the beat-02 motion job spec is corrected
before any next video render — `guidance 1.0` (the shipped distilled config),
prompt rewritten as a <200-word chronological sprint narration, `--image-crf 33`,
**97 frames** so the founder is never again screened on frames the pipeline
already condemned — and job specs gain a `motion_magnitude` tag so high-motion
beats stop inheriting low-motion acceptances silently (lessons-become-code).
These four deltas are sample 2 of the ladder, one recipe change, one render,
founder-screened; they never batch on their own.

## The prescription — ONE sample, and it is a STILL

The right fix starts with a better init still, so the still IS the sample: the
init frame is the only likeness carrier, "barely looks like the goblin" is
decided at frame 0, and no motion lever can answer it. Stills before motion is
also the founder's own standing directive (2026-07-27). ONE render, $0, local
hardware, new recipe = new fingerprint = its own clean sample-before-batch gate.

**The beat-02 init plate, drawn by the v3 one-pass:**

| field | value | why this value |
|---|---|---|
| driver | `pipeline/inpaint_fruit.py` | the one code path where the pose net is proven to act; sha-pinned `--lora` arm; selftest reproduces a filed sidecar byte-for-byte |
| base checkpoint | `cagliostrolab/animagine-xl-3.1` | the driver's `BASE`; the standing detailed-cinematic-anime look |
| LoRA | `bnyjerry-sdxl-v3.safetensors`, sha256 `d2062ac060a4ac44e217815464de143897550f078294eb59b3f303cc5f8a0cdd` (box: `C:\banyan-farm\lora-jerry-v3-0822\out`) | trained on the founder's own pixels + posed frames; the only mechanism on disk that poses AND keeps his face |
| `--lora-weight` | 0.8, **revised by step zero** — read the ungraded `lora-jerry-v3-loraweight-0822` grid (1.0 / 1.2 cells) first; if a cell shows sage skin with the pose held, use that weight | the skin-under-a-pose-net clause is the one open defect; its answer is already rendered, just never looked at |
| ControlNet | `C:\banyan-farm\cnet-openpose-twins` (allowlisted), `--scale 1.0` | the blob the probes ran; licence pinned by name |
| hint | `farm-out/jerry-skel-assets-0820/jerry-skel-h240stride-0821.png`, sha256 `f6150add3a2c603b2681d5e2f5c76e252ccb2442c43d15d285e7b15141eb67a2` | the sprint stance; proven to drive under wording A (`tp5-p1-stride-wA`) |
| init + mask | flat grey 832x1216 + all-white 832x1216 mask, `--strength 1.0`, `--pad-crop 0`, `--blur 0` | all-white at strength 1.0 IS txt2img-with-ControlNet; pad-crop 0 keeps hint magnification at exactly 1.000x |
| size | 832x1216 | the plate geometry the crop chain (`cover_crop.py` → 704x1280) already handles, sha-asserted end to end |
| steps / cfg / seed | 40 / 7.5 / 20260822 | the b2 grid's fixed values — one variable moves in this sample (the plate recipe as a whole vs the retired ageb one), not five |
| prompt | wording A, exactly: `bnyjerry, 1boy, solo, in tall grass, detailed cinematic anime, masterpiece, best quality, very aesthetic` | the knife edge: any addition to this wording cost the pose in three controls; the character enters as trained weights, not words — no face vocabulary, per the route closure |
| prompt deltas vs the rejected recipe | the entire age-B descriptive block is GONE; no ear/eye/collar words in either direction | prompt-side face work is closed by rule, and its negatives were proven porous (the elf ears came through their own negative) |
| negative | the b2 grid's `negative.txt`, unchanged bytes | same reason as steps/cfg/seed |
| host / cost | rtx5090 via a queue2 spec with `sample: true`, fanout 1 | weights are box-side; $0; the fixed recipe hashes to a NEW fingerprint and starts clean under the gate |

**Pre-checks, stated honestly:**

- Step zero, $0, no GPU: grade the four ungraded v3 probe grids by eye before
  firing — the loraweight answer may change one field above and costs nothing.
- The steward's motion metric is FALSIFIED-BUT-LIMITED (the K-recipe episode:
  the metric said good, the founder said *"literally just frozen frames"*). It
  may be used as a floor check only — against the known-frozen calibration
  (mean 0.00) — and only when the ladder reaches a video. It clears nothing.
  **Approval is founder eyes only**, on the still at 1:1 beside
  `taste/refs/goblin-canon-founder-0821.png`, one question: *is this your
  goblin, mid-sprint?*
- Steward pre-read before it reaches him (bars, not taste): stride adopted, face
  reads as the canon head, skin sage not tan. A frame failing the pre-read goes
  to the ladder, not to the founder — he gets ~one open question, with pixels.

## The ladder — what sample 2 changes on each verdict

- **Still rejected on skin** (tan/washed): the block-weight sweep the loraweight
  probe yaml ranks next — an eight-line `set_adapters`-instead-of-`fuse_lora`
  arm on `inpaint_fruit.py` plus a selftest clause; the blockweight grid is
  already rendered and gets graded first.
- **Still rejected on the face itself** ("not my goblin", a fifth time): no more
  inference knobs — the v3 DATASET goes back to his pixels
  (`pipeline/lora/manifest-jerry-v3-0822.yaml` builds from the canon image and
  masked-pass posed frames; a rejected face means a dataset frame he would not
  ratify, so the fix is curation at 1:1, then retrain — overnight-class, $0).
- **Still rejected on the pose** (stride not a sprint): the hint is re-authored
  the way `h240hunchdeep` fixed `h240hunch` — as a re-proportioned skeleton,
  one stance, one render — never by adding pose words (measured to cost the
  pose every time).
- **Still passes → sample 2 is the VIDEO** on the corrected motion recipe
  (fault-2 deltas: guidance 1.0, chronological <200-word narration, crf 33,
  97 frames), init = the passed still through the sha-asserted crop chain. One
  render, founder eyes, floor-check only from the metric.
- **Video rejected on motion again**: Tier 2 — `ltxv-13b-0.9.8-dev` in the
  first (motion-deciding) pass with its scheduled STG≈4 / guidance 3–3.5 /
  30–40 steps, distilled second pass (~2–3x slower, $0). Then Tier 3 — ONE
  Wan 2.2 I2V-A14B sample via the lightx2v 4-step Lightning distill on the
  identical init, head-to-head (one weights download, $0 cash; the community
  consensus for character motion coherence). If Tier 3 lands, high-motion beats
  route to Wan, low-motion beats keep the LTX recipe with the `motion_magnitude`
  tag deciding.

Each rung is one recipe change = one new fingerprint = one sample = one founder
look. Nothing batches off this document.

## Gate status — what the adversarial checker found, and what is closed

The checker ran before this file existed and failed closed; its findings bind
here. Since its run, on disk: the ledger row is keyed `fingerprint:` with the
real recipe fingerprint (`8546220224…8927`) — the key `sample_verdict_for()`
matches — and `queue2.py` refuses a rejected fingerprint outright at enqueue,
reading the committed ledger, so the block holds on every host including a
fanout-1 respin. Still open from its findings and honored above: the falsified
motion metric is demoted to a floor check (finding 6), both fault threads end in
a concrete pipeline change each (finding 5), and the outside-research
requirement (finding 7) is met by the research lane cited below.

## Outside research cited (research:outside lane)

github.com/Lightricks/LTX-Video (model card: distilled = CFG-free, prompt
engineering) · huggingface.co/Lightricks/LTX-Video ·
github.com/Lightricks/LTX-2 issue #255 (i2v identity drift, open, no workaround) ·
docs.comfy.org LTXVAddGuide + LTXVPreprocess / Comfy-Org embedded-docs (the
compression-artifact motion mechanism) · ltx.io prompt + character-consistency
guides · github.com/Lightricks/LTX-Video-Trainer (13B LoRA) ·
github.com/ModelTC/LightX2V + huggingface.co/lightx2v/Wan2.2-Distill-Models
(4-step Wan 2.2 on a 5090) · 500images.com LTX half-resolution first-pass
analysis · nvidia.com RTX AI video generation guide.

## Lesson

A steward-internal "pass" aged into a phantom acceptance in three days: a
timing-window pick, explicitly scored as failing design, was mirrored
byte-for-byte as if it were an approved recipe — and the founder was handed the
untrimmed version of a clip whose trim existed to hide its worst second. Every
verdict he gave was already written in our own records; the miss was treating a
relative, mechanics-scoped verdict as transferable approval. The fingerprint
gate now makes that structural: a recipe with no founder verdict renders ONE and
waits, a rejected fingerprint never runs again, and an "accepted" recipe is
accepted only for the bar its verdict actually names — which, for the 08-21
beat-02 take, was never the show.
