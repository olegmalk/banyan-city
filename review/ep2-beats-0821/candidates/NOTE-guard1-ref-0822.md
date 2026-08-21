# GUARD 1 HAS A REFERENCE IMAGE NOW — for the b05/07/08 re-plates

**From the guard lane, 2026-08-22.** Left here rather than sent, because it
changes an input your re-plates take and you should find it when you pick them
up, not when someone remembers to tell you.

```
taste/refs/guard1-canon-founder-0822.png     832x1216 RGB
sha256 420fc2c0238eb9b4f5a615cde09ed3639ffc5cc92bfbe990a9c14686329a809a
committed in 82e56b0e2
```

## What it is and why you can trust it

The founder ruled tonight on `/review/ep2-guardcast-0822`, verbatim:

> **"none of them are right, the style is wrong"**

— and posted **the beat-09 guard close-up** as the contrast. That frame is
guard 1. It is a **founder-selected generation of our own**, which is the same
provenance and the same authority the goblin ref got on 08-21 (canon.yaml,
`ep2-goblin-design-adult`: *"i didnt draw the goblin.. i just used an old
generation"*). R4 is taste; which of our frames is the character is his call.

Registered as `ep2-guard1-canon-founder-0822` in `pipeline/canon.yaml`.

**It is the platecrop still, not the clip frame.** Both carry the same pixels;
the still was picked after a 1:1 comparison — laplacian std **18.19 vs 12.95**
over the same normalised face box, ~40% more pixels across the face, and the
h264 frame softens the wire rims and hair edges. Its sha256 is the platecrop
sidecar's own `png_sha256`, so the ref traces by bytes:

```
taste/refs/guard1-canon-founder-0822.png
  = farm-out/ep2-b09-platecrop-0820/09-the-pause-platecrop-r2s2.png
  ← farm-out/ep2-b09-cast-0817/09-the-pause-ipa-r2-w015-s2.png
  ← pipeline/jobs/ep2-b09-cast-0817.yaml     ← the recipe that drew it
```

## What it settles for b05 / b07 / b08

**Settled — stop improvising these:** guard 1's face; hair **near-black and
cropped**, never bald, never mid-brown, never shaggy; **round wire-rim
glasses**; skin tone; and the collar wardrobe — **tan tunic collar, white
shoulder sash**.

**NOT settled, do not read it off this file:**

- **Full-body proportion.** It is a head-and-shoulders frame. A `head_frac`
  measured off a close-up cannot be carried to a standing plate. The goblin
  canon makes exactly this caveat about its own camera and it applies here
  harder.
- **Guard 2.** Different man, still open — being re-cast at
  `/review/ep2-guardcast2-0822`. Do not condition a two-guard plate's second
  figure on this image.

## The other half of the ruling, which bites your re-plates directly

**Humans are drawn in DETAILED CINEMATIC ANIME** — the July ruling
(CLAUDE.md 2026-07-27), re-applied. Registered as
`ep2-human-style-cinematic-anime`. Both stacks sit on `animagine-xl-3.1`; the
difference is above the checkpoint:

| | flat stack — **ruled off for humans** | cinematic stack — **use this** |
|---|---|---|
| driver | `pipeline/controlnet_plate.py` | `pipeline/goblin_ipa_beat.py --character guard --arm window4` |
| prompt | booru tag list, `muted color`, no style tail | prose, closing `cinematic lighting, masterpiece, best quality, very aesthetic` |
| conditioning | openpose skeleton, **no reference** | **IP-Adapter window @ w=0.15** over a reference set |
| negative | `photorealistic, 3d` | `No photorealism, no 3D render look` |

If a b05/07/08 re-plate is currently pointed at the flat stack, that is the
thing to change before the seed, the pose or the wording — the founder rejected
a whole twelve-cell sheet on it tonight and named nothing else.

Fuller writeup with the table and the cost: `pipeline/work-ladder-0819.md`,
last section.
