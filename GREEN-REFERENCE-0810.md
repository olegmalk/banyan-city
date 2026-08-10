# Is the reference we handed IP-Adapter even green?

2026-08-10. Beat 04 of `002b-first-citizen`. A negative result, recorded
because it closes a question rather than because it is the answer anyone
wanted.

## The question

`406909c` found the identity defect: the same words drew four different
creatures across four seeds. `09a86bf` fixed it with IP-Adapter and charged
for it — the character held and the green went. `bbf1f26` recorded the fork:
one arm holds the character, the other keeps the green. Green is the
founder's ONE named attribute, his words verbatim in `d33fb09` — *"he is just
a simple green goblin, nothing complex."*

The cheap hypothesis, and the reason for this file: **nobody had measured the
reference image itself.** If the picture we handed the adapter were
desaturated, then "the reference drains the green" would be a fact about our
picture rather than about the method, and the fork would dissolve for free —
colour-correct the reference, re-run, done.

It does not dissolve. The reference is the greenest thing in the experiment.

## Method

`pipeline/green_share.py`, documented in its own docstring. sRGB → HSV;
`green_share` = fraction of all pixels with hue in [70,180) and S ≥ 0.15;
`sat_all` = mean saturation over every pixel, kept separate so a *drain*
(chroma leaves the frame) can be told from a *rotation* (chroma stays, hue
moves). No model is involved and neither the flow metric (disqualified — it
peaked on the beat where the plant fell over) nor the pan metric (saturates
at half a block) is used.

Two things were checked before the numbers were trusted:

- **It reproduces the earlier instrument.** The arm-1 report put the wave-1
  baseline at 0.256 in the narrow 140–170° band; this tool gets 0.2465 on the
  same frames. Same ruler, near enough.
- **It discriminates on this footage, and agrees with the eye.** It separates
  the frames that look green from the frames that look grey-teal by a factor
  of thirty to three hundred, and its ordering matches a direct look at the
  contact sheet in every group. On the centre square — mostly the goblin's
  face at this framing — the separation holds, so the number is reading his
  skin and not the background.

## The three numbers

Frames verified against the box's own `.sha256` manifests; the four wave-1
PNGs in `takes/stills/` are byte-identical to the ones the box rendered from.

| what | green_share | narrow 140–170 | sat_green | median hue | sat_all |
|---|---|---|---|---|---|
| **the reference, as the adapter saw it** (wave-1 s0–s3, centre square) | **0.4918** | 0.3341 | 0.283 | 160.1° | 0.254 |
| wave-1 full frame — the frames that read green 4/4 | 0.3627 | 0.2465 | 0.282 | 159.9° | 0.261 |
| **arm 1**, adapter on every block @0.6 (r0/r1/r2/r3) | **0.0012–0.0124** | 0.0006–0.0038 | 0.21–0.32 | 134–170° | 0.112–0.253 |
| arm 1 r0 @0.4 / @0.8 | 0.0129 / 0.0140 | 0.0045 / 0.0033 | 0.28 / 0.28 | 168° / 174° | 0.254 / 0.250 |
| **arm 2**, adapter scoped to down block_2 (r0/r1/r2/r3) | **0.3440–0.3944** | 0.19–0.21 | 0.34–0.39 | 152–161° | 0.311–0.339 |

`ip_adapter_reference_prep` in every render-time sidecar reads *"centre-cropped
to square, then the pipeline's CLIPImageProcessor"*, so the square crop — not
the full portrait frame — is what the image encoder actually received. The
crop **raises** green share from 0.363 to 0.492, because it throws away the
dim window and keeps the face.

## The finding: the hypothesis is dead

**The reference is strongly green.** At 0.4918 it is greener than any output
in the experiment and greener than the full frames that the founder's eye
read as green 4/4. There is no weak reference to fix.

The control that settles it is inside the existing data and needs no new
render: **arm 2 used the byte-identical reference** — same
`ip_adapter_reference_sha256`, same prompt string, same four seeds, same
steps, guidance, size and negative, the only differing field in the sidecars
being `ip_adapter_scale` — and arm 2 came out at green_share 0.34–0.39 with
*higher* saturation than the reference itself (sat_green 0.34–0.39 against
the reference's 0.283). The same bytes produced green in one arm and grey in
the other. A reference cannot be the cause of an effect that changes when the
reference does not.

Because the reference is not the problem, no re-render was run. There was
nothing to confirm.

## A second thing the numbers say, which the fork's wording gets wrong

"Drains the green" is not what happened in arm 1, at least not at r0. Total
chroma barely moved — `sat_all` 0.254 on the reference against 0.253 on arm 1
r0. What moved is the hue: the mass sitting in the 150–180° bin on the
reference (0.418 of all pixels) reappears in the 180–210° bin on the output
(0.494). That is a rotation of roughly twenty degrees, out of green and into
cyan-teal, with the colour still there. It reads as "the green is gone"
because twenty degrees is enough to cross the boundary of the word.

The other three arm-1 references *did* drain — r3 collapses to `sat_all`
0.112, chroma 0.180 — so arm 1 is not one failure mode but two.

## What I think the next lever is, and am not pulling

Not stated as a recommendation to act on; the fork decision is the founder's
and the taste call is R4's.

The arm-1 sidecars show the adapter applied at a flat scale across every
block, and `set_ip_adapter_scale` in diffusers 0.29.2 takes a per-block
config — arm 2 already uses it. So the two arms are not "character" and
"colour", they are two points on a knob that has more than two positions:
arm 1 is every block at 0.6, arm 2 is down block_2 alone. The untested
positions are the ones in between — down block_2 at full strength *plus* a
small weight on the remaining blocks, which is the standard
style/content split the docstring describes. That is a real sweep with a real
cost, and it should be queued only if the fork is judged worth another pass.

The other candidate is upstream of all of it: the arm-1 job's own comment
identifies the beat-04 references as "lit like a dim interior — the wave-1
lighting fault (morning light drew dusk in 4 of 4), now being fed back in and
amplified." The measurement above says the references are green, but it also
says they are only moderately saturated (0.283) while arm 2 clears 0.39 with
the same input. The lighting fault is a separate defect from the colour
fork and is not fixed by anything measured here.

## Provenance

Frames: `origin/farm-results-rtx5090`, `farm-out/ep2-b04-goblin-ipa/` and
`farm-out/ep2-b04-goblin-ipa-content/`, each with its render-time sidecar;
baseline from
`genomes/sapling/nodes/002b-first-citizen/takes/stills/04-the-footnote-wave1-s*.png`
against `04-the-footnote-wave1.sha256`. All frames drawn by
`cagliostrolab/animagine-xl-3.1` (CreativeML Open RAIL++-M; use restrictions
travel — D15 open). Measurement is arithmetic on pixels, ran locally, $0, no
GPU and no render. Nothing here is a taste verdict, nothing is promoted to
canon, and no goblin has been picked.
